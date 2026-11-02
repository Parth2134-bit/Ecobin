"""All Firestore reads and writes for EcoBin.

Data model (every user's data lives under their own document):

    users/{uid}
        display_name, public_name, total_points, created_at, last_active
    users/{uid}/actions/{auto-id}
        kind ("action" | "challenge"), key, label, category, quantity,
        points, date (YYYY-MM-DD), week (YYYY-Www), notes, created_at
    users/{uid}/days/{YYYY-MM-DD}
        action_points            (used to enforce the daily points cap)
    users/{uid}/challenges/{period_key}__{challenge_key}
        challenge_key, period, period_key, points, created_at

`uid` is the Google account's permanent subject ID (st.user.sub), so two
Google accounts can never share data or points.

Every write that changes points runs inside a Firestore transaction, so
points can't be double-counted and the daily cap can't be bypassed by
clicking twice.

The class receives the Firestore client and the `google.cloud.firestore`
module as arguments. That lets the tests swap in an in-memory fake.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

from core import config
from core.dates import period_key, week_key


class ValidationError(ValueError):
    """Raised when a request is rejected. The message is safe to show users."""


class DailyCapReached(ValidationError):
    def __init__(self, remaining: int):
        self.remaining = remaining
        if remaining <= 0:
            msg = (f"You've reached today's limit of {config.DAILY_ACTION_POINT_CAP} "
                   "action points. Daily and weekly challenges still count!")
        else:
            msg = (f"That would go over the daily limit. You can earn {remaining} "
                   "more action points for that day.")
        super().__init__(msg)


@dataclass
class Profile:
    uid: str
    display_name: str
    public_name: str
    total_points: int


def public_name_from(full_name: str | None) -> str:
    """'Parth Khatri' -> 'Parth K.' so the public leaderboard shows less personal data."""
    parts = (full_name or "").split()
    if not parts:
        return "EcoBin Member"
    if len(parts) == 1:
        return parts[0][:24]
    return f"{parts[0][:24]} {parts[-1][0].upper()}."


class EcoRepository:
    def __init__(self, client: Any, fs: Any):
        self.db = client
        self.fs = fs

    # ------------------------------------------------------------------ refs
    def _user(self, uid: str):
        if not uid:
            raise ValidationError("You must be signed in.")
        return self.db.collection("users").document(uid)

    # --------------------------------------------------------------- profile
    def ensure_profile(self, uid: str, full_name: str | None) -> Profile:
        """Create the user document on first sign-in; refresh the name afterwards.

        Runs in a transaction so it can never reset an existing points total.
        """
        user_ref = self._user(uid)
        display_name = (full_name or "EcoBin Member").strip()[:60]
        public_name = public_name_from(display_name)
        fs = self.fs

        @fs.transactional
        def run(txn):
            snap = user_ref.get(transaction=txn)
            if snap.exists:
                data = snap.to_dict() or {}
                if data.get("display_name") != display_name or data.get("public_name") != public_name:
                    txn.update(user_ref, {"display_name": display_name, "public_name": public_name})
                return int(data.get("total_points", 0))
            txn.create(user_ref, {
                "display_name": display_name,
                "public_name": public_name,
                "total_points": 0,
                "created_at": fs.SERVER_TIMESTAMP,
                "last_active": fs.SERVER_TIMESTAMP,
            })
            return 0

        points = run(self.db.transaction())
        return Profile(uid, display_name, public_name, points)

    def get_points(self, uid: str) -> int:
        snap = self._user(uid).get()
        return int((snap.to_dict() or {}).get("total_points", 0)) if snap.exists else 0

    # --------------------------------------------------------------- actions
    def validate_action(self, action_key: str, quantity: Any, action_date: date,
                        today: date) -> tuple[config.Action, int, int]:
        if action_key not in config.ACTIONS:
            raise ValidationError("Please choose a valid action.")
        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            raise ValidationError("Quantity must be a whole number.") from None
        if not 1 <= qty <= config.MAX_QUANTITY_PER_ENTRY:
            raise ValidationError(f"Quantity must be between 1 and {config.MAX_QUANTITY_PER_ENTRY}.")
        if action_date > today:
            raise ValidationError("You can't log an action in the future.")
        if action_date < today - timedelta(days=config.BACKDATE_LIMIT_DAYS):
            raise ValidationError(f"Actions can only be logged for the last {config.BACKDATE_LIMIT_DAYS} days.")
        action = config.ACTIONS[action_key]
        return action, qty, action.points * qty

    def log_action(self, uid: str, action_key: str, quantity: Any, action_date: date,
                   today: date, notes: str = "") -> int:
        """Record an action and award points. Returns the points awarded."""
        action, qty, points = self.validate_action(action_key, quantity, action_date, today)
        user_ref = self._user(uid)
        day_ref = user_ref.collection("days").document(action_date.isoformat())
        action_ref = user_ref.collection("actions").document()
        clean_notes = " ".join(str(notes or "").split())[: config.NOTES_MAX_LENGTH]
        fs = self.fs

        @fs.transactional
        def run(txn):
            day = day_ref.get(transaction=txn)  # all reads before any write
            used = int((day.to_dict() or {}).get("action_points", 0)) if day.exists else 0
            if used + points > config.DAILY_ACTION_POINT_CAP:
                raise DailyCapReached(config.DAILY_ACTION_POINT_CAP - used)
            txn.create(action_ref, {
                "kind": "action",
                "key": action.key,
                "label": action.label,
                "category": action.category,
                "quantity": qty,
                "points": points,
                "date": action_date.isoformat(),
                "week": week_key(action_date),
                "notes": clean_notes,
                "created_at": fs.SERVER_TIMESTAMP,
            })
            txn.set(day_ref, {"action_points": fs.Increment(points)}, merge=True)
            txn.set(user_ref, {
                "total_points": fs.Increment(points),
                "last_active": fs.SERVER_TIMESTAMP,
            }, merge=True)

        run(self.db.transaction())
        return points

    # ------------------------------------------------------------ challenges
    def complete_challenge(self, uid: str, challenge_key: str, today: date) -> bool:
        """Complete a challenge for the current day/week.

        Returns False (and awards nothing) if it was already completed in this period.
        """
        if challenge_key not in config.CHALLENGES:
            raise ValidationError("Unknown challenge.")
        ch = config.CHALLENGES[challenge_key]
        pkey = period_key(ch.period, today)
        user_ref = self._user(uid)
        done_ref = user_ref.collection("challenges").document(f"{pkey}__{ch.key}")
        action_ref = user_ref.collection("actions").document()
        fs = self.fs

        @fs.transactional
        def run(txn):
            if done_ref.get(transaction=txn).exists:
                return False
            txn.create(done_ref, {
                "challenge_key": ch.key,
                "period": ch.period,
                "period_key": pkey,
                "points": ch.points,
                "created_at": fs.SERVER_TIMESTAMP,
            })
            txn.create(action_ref, {
                "kind": "challenge",
                "key": ch.key,
                "label": f"Challenge: {ch.title}",
                "category": ch.category,
                "quantity": 1,
                "points": ch.points,
                "date": today.isoformat(),
                "week": week_key(today),
                "notes": "",
                "created_at": fs.SERVER_TIMESTAMP,
            })
            txn.set(user_ref, {
                "total_points": fs.Increment(ch.points),
                "last_active": fs.SERVER_TIMESTAMP,
            }, merge=True)
            return True

        return bool(run(self.db.transaction()))

    def completed_challenge_ids(self, uid: str, today: date) -> set[str]:
        """Keys of challenges already completed in the current day/week."""
        current = {
            f"{period_key(c.period, today)}__{c.key}" for c in config.CHALLENGES.values()
        }
        docs = self._user(uid).collection("challenges").stream()
        return {d.id.split("__", 1)[1] for d in docs if d.id in current}

    def challenge_history_count(self, uid: str) -> int:
        return sum(1 for _ in self._user(uid).collection("challenges").stream())

    # --------------------------------------------------------------- reading
    def get_actions(self, uid: str) -> list[dict]:
        rows = []
        for d in self._user(uid).collection("actions").stream():
            row = d.to_dict() or {}
            row["id"] = d.id
            rows.append(row)
        return rows

    # ----------------------------------------------------------- leaderboard
    def leaderboard(self, limit: int = config.LEADERBOARD_SIZE) -> list[dict]:
        query = (
            self.db.collection("users")
            .order_by("total_points", direction=self.fs.Query.DESCENDING)
            .limit(int(limit))
        )
        board = []
        for d in query.stream():
            data = d.to_dict() or {}
            board.append({
                "uid": d.id,
                "name": data.get("public_name") or public_name_from(data.get("display_name")),
                "points": int(data.get("total_points", 0)),
            })
        return board

    def rank(self, uid: str, points: int) -> int:
        """1 + number of users with strictly more points (ties share a rank)."""
        users = self.db.collection("users")
        try:
            query = users.where(filter=self.fs.FieldFilter("total_points", ">", int(points)))
            result = query.count(alias="n").get()
            return int(result[0][0].value) + 1
        except Exception:  # aggregation unavailable: fall back to a scan
            higher = sum(
                1 for d in users.stream()
                if int((d.to_dict() or {}).get("total_points", 0)) > points
            )
            return higher + 1

    def member_count(self) -> int:
        users = self.db.collection("users")
        try:
            return int(users.count(alias="n").get()[0][0].value)
        except Exception:
            return sum(1 for _ in users.stream())
