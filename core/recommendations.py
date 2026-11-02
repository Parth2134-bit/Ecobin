"""Personalised next steps: nudge users toward the categories they use least."""

from __future__ import annotations

import pandas as pd

from core import config

TIPS: dict[str, list[str]] = {
    "waste": [
        "Keep two bins in your kitchen, one for wet waste and one for dry, so segregating becomes automatic.",
        "Rinse and flatten recyclables before handing them over; clean material is far more likely to be recycled.",
        "Start a small compost pot for vegetable peels and tea leaves.",
    ],
    "plastic": [
        "Keep a cloth bag in your backpack so you never need a plastic carry bag.",
        "Carry a steel or glass bottle and refill it instead of buying bottled water.",
        "Say no to plastic straws and cutlery when ordering food.",
    ],
    "water": [
        "Turn the tap off while brushing your teeth or washing dishes.",
        "Collect the water used to wash vegetables and use it for plants.",
        "Report or fix a dripping tap: a slow leak wastes water all day.",
    ],
    "energy": [
        "Switch off lights, fans and chargers when you leave a room.",
        "Dry clothes in the sun instead of using a dryer.",
        "Switch to LED bulbs as old ones burn out.",
    ],
    "transport": [
        "Walk or cycle for trips under 2 km.",
        "Take the metro or bus for your next commute.",
        "Share a ride with classmates or colleagues heading the same way.",
    ],
    "green": [
        "Plant a native sapling and log it. Then water it every week.",
        "Join or organise a clean-up drive in your neighbourhood.",
        "Invite a friend to EcoBin and compare progress on the leaderboard.",
    ],
}

STARTER = ["waste", "plastic", "energy"]


def recommend(frame: pd.DataFrame, count: int = 3) -> list[dict]:
    """Return `count` tips from the user's least-active categories.

    The tip within a category rotates as the user logs more entries there, so
    suggestions change over time instead of repeating.
    """
    if frame is None or frame.empty:
        picks = STARTER[:count]
        entries = {k: 0 for k in config.CATEGORIES}
    else:
        entries = frame.groupby("category").size().to_dict()
        order = list(config.CATEGORIES)  # stable tie-break
        picks = sorted(config.CATEGORIES, key=lambda k: (entries.get(k, 0), order.index(k)))[:count]

    out = []
    for key in picks:
        tips = TIPS[key]
        cat = config.CATEGORIES[key]
        out.append({
            "category": key,
            "label": cat.label,
            "icon": cat.icon,
            "tip": tips[int(entries.get(key, 0)) % len(tips)],
            "entries": int(entries.get(key, 0)),
        })
    return out
