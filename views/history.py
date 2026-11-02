import streamlit as st

from core import config, stats
from ui import components as c
from ui import context as ctx


def render() -> None:
    today = ctx.today_local()
    frame = ctx.actions_frame()

    c.page_header("Insights", "Your progress over time",
                  "Weekly trends, category balance and every action you've logged.")

    if frame.empty:
        st.info("No activity yet. Log your first action and your insights will appear here.",
                icon=":material/insights:")
        return

    s = stats.summarise(frame, today)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        c.kpi("This week", f"{s.points_this_week:,} pts", "calendar_month")
    with k2:
        c.kpi("Last week", f"{s.points_last_week:,} pts", "history", tint="#3B8EA5")
    with k3:
        c.kpi("Entries logged", f"{s.total_entries:,}", "checklist", tint="#7A8F3B")
    with k4:
        top = config.CATEGORIES[s.top_category].label if s.top_category in config.CATEGORIES else "-"
        c.kpi("Top category", top, "military_tech", tint="#D9A441")

    a, b = st.columns(2, gap="medium")
    with a:
        weekly = stats.weekly_series(frame, today, weeks=8)
        st.plotly_chart(c.bar_chart(weekly["week"], weekly["points"], "Weekly points (last 8 weeks)"),
                        config={"displayModeBar": False})
    with b:
        daily = stats.daily_series(frame, today, days=30)
        st.plotly_chart(c.area_chart(daily["date"], daily["points"], "Daily points (last 30 days)"),
                        config={"displayModeBar": False})

    a, b = st.columns([1, 1.3], gap="medium")
    with a:
        breakdown = stats.category_breakdown(frame)
        nonzero = breakdown[breakdown["points"] > 0]
        st.plotly_chart(c.donut(nonzero["category"], nonzero["points"], nonzero["color"].tolist(),
                                "Points by category"), config={"displayModeBar": False})
    with b:
        c.section("Impact summary", "What your logged actions add up to")
        c.impact_list(stats.impact_summary(frame), limit=5)

    c.section("All entries")
    cat_filter = st.pills("Filter by category", list(config.CATEGORIES), selection_mode="multi",
                          format_func=lambda k: config.CATEGORIES[k].label, key="hist_filter")
    view = frame if not cat_filter else frame[frame["category"].isin(cat_filter)]
    table = view.assign(
        category=view["category"].map(lambda k: config.CATEGORIES[k].label if k in config.CATEGORIES else k),
        type=view["kind"].map({"action": "Action", "challenge": "Challenge"}).fillna("Action"),
    )[["date", "label", "category", "type", "quantity", "points", "notes"]]

    st.dataframe(
        table, hide_index=True,
        column_config={
            "date": st.column_config.DateColumn("Date", format="DD MMM YYYY"),
            "label": "Activity",
            "category": "Category",
            "type": "Type",
            "quantity": st.column_config.NumberColumn("Qty", format="%d"),
            "points": st.column_config.NumberColumn("Points", format="%d"),
            "notes": "Notes",
        },
    )
    st.download_button("Download CSV", table.to_csv(index=False).encode("utf-8"),
                       file_name=f"ecobin-activity-{today.isoformat()}.csv", mime="text/csv",
                       icon=":material/download:")
