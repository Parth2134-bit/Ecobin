"""Checks that everything EcoBin needs is in place, without printing any secret.

Usage (from the project folder):
    python scripts/check_setup.py
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

OK, WARN, FAIL = "[ OK ]", "[WARN]", "[FAIL]"
problems = 0


def report(status: str, message: str) -> None:
    global problems
    if status == FAIL:
        problems += 1
    print(f"{status} {message}")


def main() -> int:
    print(f"EcoBin setup check, project folder: {ROOT}\n")

    v = sys.version_info
    report(OK if (3, 10) <= (v.major, v.minor) <= (3, 13) else WARN,
           f"Python {v.major}.{v.minor}.{v.micro} (3.11-3.13 recommended)")

    for module, label in [("streamlit", "streamlit"), ("authlib", "Authlib (streamlit[auth])"),
                          ("firebase_admin", "firebase-admin"), ("pandas", "pandas"),
                          ("plotly", "plotly"), ("tzdata", "tzdata")]:
        try:
            mod = importlib.import_module(module)
            report(OK, f"{label} {getattr(mod, '__version__', '')}".rstrip())
        except ImportError:
            report(FAIL, f"{label} is not installed. Run: python -m pip install -r requirements.txt")

    secrets = ROOT / ".streamlit" / "secrets.toml"
    if not secrets.is_file():
        report(FAIL, ".streamlit/secrets.toml not found (copy .streamlit/secrets.example.toml)")
    else:
        try:
            import tomllib
            data = tomllib.loads(secrets.read_text(encoding="utf-8"))
            auth = data.get("auth", {})
            needed = ["redirect_uri", "cookie_secret", "client_id", "client_secret", "server_metadata_url"]
            missing = [k for k in needed if not str(auth.get(k, "")).strip() or "PASTE" in str(auth.get(k))]
            report(FAIL if missing else OK,
                   f"[auth] missing/placeholder: {', '.join(missing)}" if missing else "[auth] has all 5 settings")
            cid = str(auth.get("client_id", ""))
            if cid and not cid.endswith(".apps.googleusercontent.com"):
                report(FAIL, "client_id should end with .apps.googleusercontent.com "
                             "(copy the Web client ID, not a URL)")
            if len(str(auth.get("cookie_secret", ""))) < 32:
                report(WARN, "cookie_secret is short; use the generator command in README")
            print(f"       redirect_uri = {auth.get('redirect_uri')}")
        except Exception as exc:
            report(FAIL, f"secrets.toml could not be parsed: {type(exc).__name__}")

    key = ROOT / "serviceAccountKey.json"
    if key.is_file():
        try:
            info = json.loads(key.read_text(encoding="utf-8"))
            pid = info.get("project_id")
            report(OK if pid == "ecobin-66e68" else WARN, f"serviceAccountKey.json found (project_id: {pid})")
        except Exception:
            report(FAIL, "serviceAccountKey.json is not valid JSON; download a fresh key")
    else:
        report(WARN, "serviceAccountKey.json not found (fine only if [firebase_service_account] is in secrets.toml)")

    try:
        from core.firebase import create_repository
        repo = create_repository()
        n = repo.member_count()
        report(OK, f"Connected to Firestore: {n} member(s) in users collection")
    except Exception as exc:
        report(FAIL, f"Firestore connection failed: {type(exc).__name__}: {str(exc)[:160]}")

    print("\nAll checks passed. Start the app with:  python -m streamlit run app.py"
          if not problems else f"\n{problems} problem(s) to fix (see README > Troubleshooting).")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
