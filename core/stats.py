"""Turns a user's action records into the numbers and series the dashboard shows.

Pure pandas, no Firestore and no Streamlit, so every function is unit-tested.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

import pandas as pd

from core import config
from core.dates import week_start

COLUMNS = ["date", "kind", "key", "label", "category", "quantity", "points", "notes"]


def to_frame(rows: list[dict]) -> pd.DataFrame:
    """Normalise raw Firestore rows into a typed DataFrame (newest first)."""
    if not rows:
        frame = pd.DataFrame(columns=COLUMNS)
        frame["date"] = pd.Series(dtype="object")
        return frame
    frame = pd.DataFrame(rows)
    for col in COLUMNS:
        if col not in frame.columns:
            frame[col] = None
    frame = frame[COLUMNS + ([c for c in ["created_at"] if c in frame.columns])].copy()
    frame["date"] = pd.to_datetime(frame["date"], format="%Y-%m-%d", errors="coerce").dt.date
    frame = frame.dropna(subset=["date"])
    frame["quantity"] = pd.to_numeric(frame["quantity"], errors="coerce").fillna(0).astype(int)
    frame["points"] = pd.to_numeric(frame["points"], errors="coerce").fillna(0).astype(int)
    frame["kind"] = frame["kind"].fillna("action")
    frame["notes"] = frame["notes"].fillna("")
    sort_cols = ["date"] + (["created_at"] if "created_at" in frame.columns else [])
    try:
        frame = frame.sort_values(sort_cols, ascending=False)
    except TypeError:
        frame = frame.sort_values("date", ascending=False)
    return frame.drop(columns=[c for c in ["created_at"] if c in frame.columns]).reset_index(drop=True)


def _points_between(frame: pd.DataFrame, start: date, end: date) -> int:
    if frame.empty:
        return 0
    mask = (frame["date"] >= start) & (frame["date"] <= end)
    return int(frame.loc[mask, "points"].sum())


def streak(frame: pd.DataFrame, today: date) -> int:
    """Consecutive days with at least one entry, ending today (or yesterday)."""
    if frame.empty:
        return 0
    days = set(frame["date"])
    cursor = today if today in days else today - timedelta(days=1)
    count = 0
    while cursor in days:
        count += 1
        cursor -= timedelta(days=1)
    return count


@dataclass
class Summary:
    points_today: int = 0
    points_this_week: int = 0
    points_last_week: int = 0
    entries_this_week: int = 0
    total_entries: int = 0
    active_days: int = 0
    streak: int = 0
    week_change_pct: float | None = None
    top_category: str | None = None
    category_points: dict[str, int] = field(default_factory=dict)


def summarise(frame: pd.DataFrame, today: date) -> Summary:
    s = Summary()
    if frame.empty:
        return s
    this_week = week_start(today)
    last_week = this_week - timedelta(days=7)
    s.points_today = _points_between(frame, today, today)
    s.points_this_week = _points_between(frame, this_week, today)
    s.points_last_week = _points_between(frame, last_week, this_week - timedelta(days=1))
    s.entries_this_week = int(((frame["date"] >= this_week) & (frame["date"] <= today)).sum())
    s.total_entries = len(frame)
    s.active_days = frame["date"].nunique()
    s.streak = streak(frame, today)
    if s.points_last_week:
        s.week_change_pct = round(100 * (s.points_this_week - s.points_last_week) / s.points_last_week, 1)
    by_cat = frame.groupby("category")["points"].sum().sort_values(ascending=False)
    s.category_points = {k: int(v) for k, v in by_cat.items()}
    s.top_category = by_cat.index[0] if len(by_cat) else None
    return s


def daily_series(frame: pd.DataFrame, today: date, days: int = 14) -> pd.DataFrame:
    """Points per day for the last `days` days, zero-filled."""
    dates = [today - timedelta(days=i) for i in range(days - 1, -1, -1)]
    totals = frame.groupby("date")["points"].sum().to_dict() if not frame.empty else {}
    return pd.DataFrame({
        "date": [pd.Timestamp(d) for d in dates],
        "points": [int(totals.get(d, 0)) for d in dates],
    })


def weekly_series(frame: pd.DataFrame, today: date, weeks: int = 8) -> pd.DataFrame:
    """Points per ISO week for the last `weeks` weeks, zero-filled."""
    starts = [week_start(today) - timedelta(weeks=i) for i in range(weeks - 1, -1, -1)]
    if frame.empty:
        totals = {}
    else:
        week_of = frame["date"].map(week_start)
        totals = frame.groupby(week_of)["points"].sum().to_dict()
    return pd.DataFrame({
        "week": [d.strftime("%d %b") for d in starts],
        "points": [int(totals.get(d, 0)) for d in starts],
    })


def category_breakdown(frame: pd.DataFrame) -> pd.DataFrame:
    """Points and entries for every category (including empty ones)."""
    rows = []
    for key, cat in config.CATEGORIES.items():
        sub = frame[frame["category"] == key] if not frame.empty else frame
        rows.append({
            "key": key,
            "category": cat.label,
            "color": cat.color,
            "points": int(sub["points"].sum()) if not sub.empty else 0,
            "entries": int(len(sub)),
        })
    return pd.DataFrame(rows)


def impact_summary(frame: pd.DataFrame) -> list[dict]:
    """Totals per logged action, e.g. '12 trips' for public transport. Biggest first."""
    if frame.empty:
        return []
    acts = frame[frame["kind"] == "action"]
    out = []
    for key, qty in acts.groupby("key")["quantity"].sum().sort_values(ascending=False).items():
        action = config.ACTIONS.get(key)
        if action is None:
            continue
        out.append({
            "key": key,
            "label": action.label,
            "category": action.category,
            "quantity": int(qty),
            "unit": action.unit,
        })
    return out
