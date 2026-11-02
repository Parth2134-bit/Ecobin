"""Single source of truth for EcoBin's categories, actions, challenges and rules.

Change point values or add actions here only. The UI and the database layer
both read from this file, so they can never disagree.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Time zone used to decide what "today" and "this week" mean.
APP_TIMEZONE = "Asia/Kolkata"

# Anti-gaming rules (enforced on the server side, inside Firestore transactions).
MAX_QUANTITY_PER_ENTRY = 10        # one log entry can count an action at most 10 times
DAILY_ACTION_POINT_CAP = 200       # max points from logged actions per user per day
BACKDATE_LIMIT_DAYS = 7            # actions may be logged for today or the previous 7 days
NOTES_MAX_LENGTH = 300

LEADERBOARD_SIZE = 50


@dataclass(frozen=True)
class Category:
    key: str
    label: str
    icon: str      # Material Symbols name, used as :material/<icon>:
    color: str     # chart / accent colour


@dataclass(frozen=True)
class Action:
    key: str
    label: str
    category: str  # Category.key
    points: int
    unit: str      # how one "quantity" reads in impact summaries, e.g. "trips"


@dataclass(frozen=True)
class Challenge:
    key: str
    title: str
    description: str
    category: str  # Category.key
    points: int
    period: str    # "daily" or "weekly"


CATEGORIES: dict[str, Category] = {
    c.key: c
    for c in [
        Category("waste", "Waste Management", "delete", "#2F6B4F"),
        Category("plastic", "Plastic Reduction", "water_bottle", "#5E9C76"),
        Category("water", "Water Conservation", "water_drop", "#3B8EA5"),
        Category("energy", "Energy Conservation", "bolt", "#D9A441"),
        Category("transport", "Sustainable Transport", "directions_bus", "#7A8F3B"),
        Category("green", "Green Activities", "park", "#1F4D3A"),
    ]
}

ACTIONS: dict[str, Action] = {
    a.key: a
    for a in [
        Action("segregate_waste", "Segregated wet and dry waste", "waste", 10, "times"),
        Action("recycle", "Recycled items", "waste", 15, "batches recycled"),
        Action("compost", "Composted kitchen waste", "waste", 15, "times"),
        Action("refuse_plastic", "Refused single-use plastic", "plastic", 10, "plastic items avoided"),
        Action("reusable_bag_bottle", "Used a reusable bag or bottle", "plastic", 10, "times"),
        Action("save_water", "Reduced water use", "water", 10, "times"),
        Action("fix_leak", "Fixed or reported a leak", "water", 20, "leaks fixed"),
        Action("switch_off", "Switched off unused appliances", "energy", 10, "times"),
        Action("natural_light", "Used daylight or air-dried clothes", "energy", 10, "times"),
        Action("public_transport", "Used public transport", "transport", 15, "trips"),
        Action("walk_cycle", "Walked or cycled", "transport", 15, "trips"),
        Action("carpool", "Carpooled", "transport", 10, "shared trips"),
        Action("plant_tree", "Planted a tree", "green", 25, "trees planted"),
        Action("cleanup_drive", "Joined a clean-up drive", "green", 25, "clean-ups"),
    ]
}

CHALLENGES: dict[str, Challenge] = {
    c.key: c
    for c in [
        Challenge("plastic_free_day", "Plastic-Free Day",
                  "Get through the whole day without using single-use plastic.",
                  "plastic", 20, "daily"),
        Challenge("save_water_day", "Save Water",
                  "Take a shorter shower and keep taps closed when not in use.",
                  "water", 15, "daily"),
        Challenge("green_commute", "Green Commute",
                  "Walk, cycle or take public transport for at least one journey.",
                  "transport", 20, "daily"),
        Challenge("switch_it_off", "Switch It Off",
                  "Switch off every light, fan and charger you are not using.",
                  "energy", 15, "daily"),
        Challenge("byo_week", "Bring-Your-Own Week",
                  "Carry your own bag, bottle and cup every day this week.",
                  "plastic", 50, "weekly"),
        Challenge("zero_waste_week", "Segregation Streak",
                  "Segregate wet and dry waste at home on every day this week.",
                  "waste", 50, "weekly"),
        Challenge("plant_and_care", "Plant & Care",
                  "Plant a sapling or adopt one nearby and water it this week.",
                  "green", 60, "weekly"),
    ]
}

# Levels: (minimum points, name). Must be sorted ascending.
LEVELS: list[tuple[int, str]] = [
    (0, "Eco Starter"),
    (100, "Eco Explorer"),
    (300, "Eco Champion"),
    (700, "Eco Guardian"),
    (1500, "Eco Legend"),
]

# Short, sourced facts shown after logging an action (by category).
# They describe general benefits and never claim a measured impact.
FACTS: dict[str, tuple[str, str]] = {
    "waste": ("Separating wet and dry waste makes recycling and composting easier "
              "and keeps recyclable material clean.",
              "Central Pollution Control Board, Solid Waste Management guidance"),
    "plastic": ("Plastic can persist in the environment for a very long time and harms "
                "wildlife when it reaches rivers and oceans.",
                "UN Environment Programme, Plastic Pollution"),
    "water": ("Freshwater is shared by people, farms and ecosystems; cutting waste "
              "at home eases pressure on local supply.",
              "US Geological Survey, Water Science School"),
    "energy": ("Using less electricity lowers demand on power generation and the "
               "emissions from fossil-fuel plants.",
               "International Energy Agency, Energy Efficiency"),
    "transport": ("Buses and trains move more people with less energy per passenger "
                  "than most single-occupant car trips.",
                  "International Energy Agency, The Future of Rail"),
    "green": ("Trees provide habitat, store carbon and support soil and water health "
              "when suitable native species are planted.",
              "FAO, The State of the World's Forests"),
}


def action_points(action_key: str, quantity: int) -> int:
    return ACTIONS[action_key].points * int(quantity)


def level_for(points: int) -> tuple[str, int, int | None]:
    """Return (level name, level floor, next level threshold or None if max)."""
    name, floor, nxt = LEVELS[0][1], LEVELS[0][0], None
    for i, (threshold, level_name) in enumerate(LEVELS):
        if points >= threshold:
            name, floor = level_name, threshold
            nxt = LEVELS[i + 1][0] if i + 1 < len(LEVELS) else None
    return name, floor, nxt
