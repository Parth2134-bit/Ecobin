from datetime import timedelta

import streamlit as st

from core import config
from core.repository import ValidationError
from ui import components as c
from ui import context as ctx


def _used_today(frame, day) -> int:
    if frame.empty:
        return 0
    mask = (frame["date"] == day) & (frame["kind"] == "action")
    return int(frame.loc[mask, "points"].sum())


def render() -> None:
    user = ctx.current_user()
    today = ctx.today_local()

    c.page_header("Action tracker", "Log a sustainable action",
                  "Pick a category, choose what you did and earn Eco Points. "
                  f"You can log actions from the last {config.BACKDATE_LIMIT_DAYS} days.")

    for f in ctx.pop_flashes():
        if f["kind"] == "success":
            st.success(f["message"], icon=":material/eco:")
            if f.get("category"):
                c.fact_card(f["category"])
                st.write("")

    left, right = st.columns([1.6, 1], gap="large")

    with left:
        cat_keys = list(config.CATEGORIES)
        chosen = st.pills(
            "Category",
            cat_keys,
            format_func=lambda k: config.CATEGORIES[k].label,
            default=cat_keys[0],
            key="log_category",
        ) or cat_keys[0]
        options = [a.key for a in config.ACTIONS.values() if a.category == chosen]

        with st.form("log_action", clear_on_submit=True, border=False):
            action_key = st.selectbox(
                "What did you do?",
                options,
                format_func=lambda k: f"{config.ACTIONS[k].label}  ·  {config.ACTIONS[k].points} pts each",
            )
            d1, d2 = st.columns(2)
            with d1:
                action_date = st.date_input(
                    "When?", value=today, min_value=today - timedelta(days=config.BACKDATE_LIMIT_DAYS),
                    max_value=today, format="DD/MM/YYYY",
                )
            with d2:
                quantity = st.number_input("How many times?", min_value=1,
                                           max_value=config.MAX_QUANTITY_PER_ENTRY, value=1, step=1)
            notes = st.text_area("Notes (optional)", max_chars=config.NOTES_MAX_LENGTH,
                                 placeholder="e.g. Took the metro to college instead of an auto")
            submitted = st.form_submit_button("Save action", type="primary", icon=":material/check:")

        if submitted:
            try:
                points = ctx.repo().log_action(user.uid, action_key, quantity, action_date, today, notes)
            except ValidationError as err:
                st.warning(str(err), icon=":material/info:")
            except Exception:
                st.error("Couldn't reach the cloud database, so nothing was saved. "
                         "Check your internet connection and try again.", icon=":material/cloud_off:")
            else:
                ctx.invalidate()
                ctx.flash("success", f"Saved! You earned {points} Eco Points.",
                          category=config.ACTIONS[action_key].category)
                st.rerun()

    with right:
        frame = ctx.actions_frame()
        used = _used_today(frame, today)
        cap = config.DAILY_ACTION_POINT_CAP
        pct = min(100, round(100 * used / cap))
        c.html(f"""
        <div class="eco-card">
          <div class="eco-eyebrow">Today's allowance</div>
          <div style="font-size:1.6rem;font-weight:800;margin-top:.3rem">{used} <span style="font-size:1rem;color:var(--eco-muted)">/ {cap} pts</span></div>
          <div class="meter"><div style="width:{pct}%"></div></div>
          <div style="color:var(--eco-muted);font-size:.82rem">A daily cap keeps the leaderboard fair. Challenges don't count toward it.</div>
        </div>
        """)
        st.write("")
        c.section("Recent entries")
        if frame.empty:
            st.caption("Nothing logged yet. Your first action is one click away.")
        else:
            rows = []
            for _, r in frame.head(5).iterrows():
                cat = config.CATEGORIES.get(r["category"])
                color = cat.color if cat else "#3FA36B"
                ic = cat.icon if cat else "eco"
                rows.append(f"""
                <div class="impact">
                  <div class="ic" style="background:{color}">{c.icon(ic)}</div>
                  <div style="flex:1"><div style="font-weight:700">{c.escape(str(r['label']))}</div>
                  <div class="u">{r['date'].strftime('%d %b')} · ×{int(r['quantity'])}</div></div>
                  <span class="badge-pts">+{int(r['points'])}</span>
                </div>""")
            c.html(f'<div class="eco-card">{"".join(rows)}</div>')
