import streamlit as st

from core import config, stats
from core.recommendations import recommend
from ui import components as c
from ui import context as ctx
from ui.nav import PAGES


def render() -> None:
    user = ctx.current_user()
    today = ctx.today_local()
    frame = ctx.actions_frame()
    points = ctx.total_points()
    summary = stats.summarise(frame, today)
    level, floor, nxt = config.level_for(points)
    rank = ctx.repo().rank(user.uid, points)
    done = ctx.repo().completed_challenge_ids(user.uid, today)

    c.hero(user.name, points, level, floor, nxt, summary.streak, rank)
    st.write("")

    # ---- KPI row
    if summary.week_change_pct is None:
        delta, trend = ("First week of activity" if summary.points_this_week else "Log an action to start"), "flat"
    else:
        arrow = "▲" if summary.week_change_pct >= 0 else "▼"
        delta = f"{arrow} {abs(summary.week_change_pct)}% vs last week"
        trend = "up" if summary.week_change_pct >= 0 else "down"

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        c.kpi("Points today", f"{summary.points_today:,}", "today",
              f"{config.DAILY_ACTION_POINT_CAP} action pts/day max")
    with k2:
        c.kpi("This week", f"{summary.points_this_week:,}", "calendar_month", delta, trend, "#3B8EA5")
    with k3:
        c.kpi("Day streak", f"{summary.streak}", "local_fire_department",
              f"{summary.active_days} active days in total", tint="#D9A441")
    with k4:
        c.kpi("Challenges", f"{len(done)}/{len(config.CHALLENGES)}", "flag",
              "Completed this day / week", tint="#7A8F3B")

    # ---- charts
    left, right = st.columns([1.55, 1], gap="medium")
    with left:
        daily = stats.daily_series(frame, today, days=14)
        st.plotly_chart(c.area_chart(daily["date"], daily["points"], "Points, last 14 days"),
                        config={"displayModeBar": False})
    with right:
        breakdown = stats.category_breakdown(frame)
        if breakdown["points"].sum() > 0:
            nonzero = breakdown[breakdown["points"] > 0]
            st.plotly_chart(c.donut(nonzero["category"], nonzero["points"], nonzero["color"].tolist(),
                                    "Where your points come from"),
                            config={"displayModeBar": False})
        else:
            c.growth_tree(points)

    # ---- recommendations
    c.section("Recommended next steps", "Based on the categories you've explored least")
    cols = st.columns(3, gap="medium")
    for col, rec in zip(cols, recommend(frame)):
        with col:
            cat = config.CATEGORIES[rec["category"]]
            c.tip_card(rec["label"], rec["icon"], cat.color, rec["tip"])

    # ---- impact + tree + quick links
    c.section("Your impact so far", "Totals of what you've logged")
    a, b = st.columns([1.55, 1], gap="medium")
    with a:
        c.impact_list(stats.impact_summary(frame))
    with b:
        if breakdown["points"].sum() > 0:
            c.growth_tree(points)
        st.write("")
        st.page_link(PAGES["log"], label="Log a new action", icon=":material/add_circle:")
        st.page_link(PAGES["challenges"], label="Open today's challenges", icon=":material/flag:")
