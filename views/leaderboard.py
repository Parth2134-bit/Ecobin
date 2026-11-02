import streamlit as st

from core import config
from ui import components as c
from ui import context as ctx


def render() -> None:
    user = ctx.current_user()
    c.page_header("Community", "Global leaderboard",
                  "Every EcoBin member, ranked by Eco Points. Only first names and last initials are shown.")

    try:
        board = ctx.cached_leaderboard(config.LEADERBOARD_SIZE)
        points = ctx.total_points()
        rank = ctx.repo().rank(user.uid, points)
        members = ctx.repo().member_count()
    except Exception:
        st.error("Couldn't load the live leaderboard. Check your connection and refresh.",
                 icon=":material/cloud_off:")
        return

    k1, k2, k3 = st.columns(3)
    with k1:
        c.kpi("Your rank", f"#{rank}", "leaderboard")
    with k2:
        c.kpi("Your points", f"{points:,}", "stars", tint="#D9A441")
    with k3:
        c.kpi("Members", f"{members:,}", "groups", tint="#3B8EA5")
    st.write("")

    if not board:
        st.info("Be the first on the board: log an action!", icon=":material/emoji_events:")
        return

    # Podium (2nd, 1st, 3rd) for the top three
    top = board[:3]
    order = [(1, "r2"), (0, "r1"), (2, "r3")]
    pods = []
    for idx, cls in order:
        if idx < len(top):
            r = top[idx]
            pods.append(f"""
            <div class="pod {cls}">
              <div class="rk">#{idx + 1}</div>
              <div class="av">{c.initials(r['name'])}</div>
              <div class="nm">{c.escape(r['name'])}{' (you)' if r['uid'] == user.uid else ''}</div>
              <div class="pt">{r['points']:,} pts</div>
            </div>""")
        else:
            pods.append("<div></div>")
    c.html(f'<div class="podium">{"".join(pods)}</div>')
    st.write("")

    rows = []
    for i, r in enumerate(board[3:], start=4):
        me = r["uid"] == user.uid
        rows.append(f"""
        <div class="lb-row{' me' if me else ''}">
          <div class="rk">#{i}</div>
          <div class="av">{c.initials(r['name'])}</div>
          <div class="nm">{c.escape(r['name'])}{' · you' if me else ''}</div>
          <div class="pt">{r['points']:,} pts</div>
        </div>""")
    if rows:
        c.html("".join(rows))

    if all(r["uid"] != user.uid for r in board):
        st.caption(f"You're ranked #{rank}. Keep logging actions to break into the top {config.LEADERBOARD_SIZE}!")

    if st.button("Refresh", icon=":material/refresh:"):
        ctx.cached_leaderboard.clear()
        st.rerun()
