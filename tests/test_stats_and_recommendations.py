from datetime import date, timedelta

from core import config
from core.dates import period_key, week_key, week_start
from core.recommendations import recommend
from core.stats import (category_breakdown, daily_series, impact_summary, streak,
                        summarise, to_frame, weekly_series)

TODAY = date(2026, 11, 3)  # Tuesday, week starts Mon 2 Nov


def row(days_ago, key="recycle", qty=1, kind="action"):
    a = config.ACTIONS.get(key)
    cat = a.category if a else "green"
    pts = (a.points if a else 20) * qty
    return {"date": (TODAY - timedelta(days=days_ago)).isoformat(), "kind": kind, "key": key,
            "label": key, "category": cat, "quantity": qty, "points": pts, "notes": ""}


def test_config_is_consistent():
    for a in config.ACTIONS.values():
        assert a.category in config.CATEGORIES
    for c in config.CHALLENGES.values():
        assert c.category in config.CATEGORIES and c.period in ("daily", "weekly")
    assert len(config.CATEGORIES) == 6
    assert [t for t, _ in config.LEVELS] == sorted(t for t, _ in config.LEVELS)
    assert set(config.FACTS) == set(config.CATEGORIES)
    # the daily cap must allow at least one entry of every action at max quantity... or one of the biggest
    assert max(a.points for a in config.ACTIONS.values()) <= config.DAILY_ACTION_POINT_CAP


def test_levels():
    assert config.level_for(0) == ("Eco Starter", 0, 100)
    assert config.level_for(150) == ("Eco Explorer", 100, 300)
    assert config.level_for(5000)[0] == "Eco Legend" and config.level_for(5000)[2] is None


def test_dates():
    assert week_start(TODAY) == date(2026, 11, 2)
    assert week_key(TODAY) == "2026-W45"
    assert period_key("daily", TODAY) == "2026-11-03"
    assert week_key(date(2027, 1, 1)) == "2026-W53"


def test_empty_frame_everywhere():
    f = to_frame([])
    assert f.empty
    s = summarise(f, TODAY)
    assert s.points_today == 0 and s.streak == 0 and s.week_change_pct is None
    assert daily_series(f, TODAY)["points"].sum() == 0
    assert len(weekly_series(f, TODAY)) == 8
    assert len(category_breakdown(f)) == 6
    assert impact_summary(f) == []
    assert len(recommend(f)) == 3


def test_summary_numbers():
    f = to_frame([row(0), row(0, "plant_tree"), row(1), row(3), row(8, "walk_cycle", 2)])
    s = summarise(f, TODAY)
    assert s.points_today == 40
    assert s.points_this_week == 55          # Mon + Tue
    assert s.points_last_week == 45          # 31 Oct (Sat) + 26 Oct (Mon)
    assert s.week_change_pct == round(100 * 10 / 45, 1)
    assert s.streak == 2
    assert s.total_entries == 5 and s.active_days == 4
    assert s.top_category == "waste"


def test_streak_counts_from_yesterday_if_nothing_today():
    f = to_frame([row(1), row(2), row(4)])
    assert streak(f, TODAY) == 2


def test_series_and_breakdown():
    f = to_frame([row(0, qty=2), row(13), row(20)])
    d = daily_series(f, TODAY, days=14)
    assert len(d) == 14 and d["points"].iloc[-1] == 30 and d["points"].iloc[0] == 15
    w = weekly_series(f, TODAY, weeks=8)
    assert w["points"].sum() == 60
    b = category_breakdown(f).set_index("key")
    assert b.loc["waste", "points"] == 60 and b.loc["water", "points"] == 0


def test_impact_summary_excludes_challenges():
    f = to_frame([row(0, "public_transport", 3), row(1, "public_transport", 2),
                  row(0, "green_commute", kind="challenge")])
    imp = impact_summary(f)
    assert imp == [{"key": "public_transport", "label": "Used public transport",
                    "category": "transport", "quantity": 5, "unit": "trips"}]


def test_recommendations_target_least_active():
    f = to_frame([row(0, "recycle"), row(0, "save_water"), row(0, "switch_off"),
                  row(0, "walk_cycle")])
    cats = [r["category"] for r in recommend(f)]
    assert cats == ["plastic", "green", "waste"]


def test_frame_tolerates_bad_rows():
    f = to_frame([{"date": "not-a-date", "points": 5}, row(0)])
    assert len(f) == 1
