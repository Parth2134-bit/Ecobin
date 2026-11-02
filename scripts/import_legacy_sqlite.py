"""OPTIONAL one-time import of the old ecobin.db (SQLite) into one Firestore account.

The old database had no user accounts, so you choose which EcoBin user receives
the records. The SQLite file is opened READ-ONLY and is never modified.
Running the import twice is safe: already-imported records are skipped.

Steps (from the project folder):
  1. Sign in to the app once with the Google account that should own the data.
  2. python scripts/import_legacy_sqlite.py --list-users
  3. python scripts/import_legacy_sqlite.py --db "C:\\path\\to\\old\\ecobin.db" --uid <UID>          (preview)
  4. python scripts/import_legacy_sqlite.py --db "C:\\path\\to\\old\\ecobin.db" --uid <UID> --commit (write)
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core import config  # noqa: E402
from core.dates import week_key  # noqa: E402

OLD_TO_NEW = {
    "Waste segregation": "segregate_waste",
    "Recycling": "recycle",
    "Avoided single-use plastic": "refuse_plastic",
    "Saved electricity": "switch_off",
    "Saved water": "save_water",
    "Used public transport": "public_transport",
    "Walked or cycled": "walk_cycle",
    "Planted a tree": "plant_tree",
    "Challenge: Plastic-Free Day": "plastic_free_day",
    "Challenge: Save Water": "save_water_day",
    "Challenge: Green Commute": "green_commute",
    "Challenge: Switch It Off": "switch_it_off",
}


def read_legacy(db_path: Path) -> list[dict]:
    uri = f"file:{db_path.resolve().as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        cur = conn.execute("SELECT id, action, category, action_date, quantity, points, notes FROM actions")
        rows = []
        for rid, action, _cat, action_date, qty, points, notes in cur.fetchall():
            key = OLD_TO_NEW.get(action)
            if key is None:
                print(f"  skip id={rid}: unknown action '{action}'")
                continue
            is_challenge = key in config.CHALLENGES
            meta = config.CHALLENGES[key] if is_challenge else config.ACTIONS[key]
            d = date.fromisoformat(str(action_date)[:10])
            rows.append({
                "doc_id": f"legacy_{rid}",
                "data": {
                    "kind": "challenge" if is_challenge else "action",
                    "key": key,
                    "label": f"Challenge: {meta.title}" if is_challenge else meta.label,
                    "category": meta.category,
                    "quantity": int(qty),
                    "points": int(points),
                    "date": d.isoformat(),
                    "week": week_key(d),
                    "notes": (notes or "")[: config.NOTES_MAX_LENGTH],
                    "legacy": True,
                },
            })
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--db", type=Path, help="Path to the old ecobin.db")
    p.add_argument("--uid", help="Firestore user ID that will own the records")
    p.add_argument("--list-users", action="store_true", help="List EcoBin users and their IDs")
    p.add_argument("--commit", action="store_true", help="Actually write (default is a dry run)")
    args = p.parse_args()

    from core.firebase import create_repository
    repo = create_repository()
    fs = repo.fs

    if args.list_users:
        for d in repo.db.collection("users").stream():
            data = d.to_dict() or {}
            print(f"{d.id}  {data.get('display_name', '?'):<30} {data.get('total_points', 0)} pts")
        return 0

    if not args.db or not args.uid:
        p.error("--db and --uid are required (or use --list-users)")
    if not args.db.is_file():
        p.error(f"Database not found: {args.db}")

    user_ref = repo.db.collection("users").document(args.uid)
    if not user_ref.get().exists:
        p.error("That user ID doesn't exist. Sign in to the app first, then use --list-users.")

    rows = read_legacy(args.db)
    total = sum(r["data"]["points"] for r in rows)
    print(f"Found {len(rows)} legacy records worth {total} points.")
    if not args.commit:
        print("Dry run only. Add --commit to import.")
        return 0

    imported = skipped = points = 0
    for r in rows:
        ref = user_ref.collection("actions").document(r["doc_id"])

        @fs.transactional
        def run(txn, ref=ref, r=r):
            if ref.get(transaction=txn).exists:
                return False
            txn.create(ref, {**r["data"], "created_at": fs.SERVER_TIMESTAMP})
            txn.set(user_ref, {"total_points": fs.Increment(r["data"]["points"])}, merge=True)
            return True

        if run(repo.db.transaction()):
            imported += 1
            points += r["data"]["points"]
        else:
            skipped += 1
    print(f"Imported {imported} records (+{points} pts); skipped {skipped} already imported.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
