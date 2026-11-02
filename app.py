"""EcoBin: Mission LiFE citizen engagement app (HackCult '26, HC26-GEDA01).

Run with:  python -m streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="EcoBin · Sustainable living",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

from core.config import BASE_DIR, level_for  # noqa: E402
from core.firebase import FirebaseSetupError  # noqa: E402
from ui import components as c  # noqa: E402
from ui import context as ctx  # noqa: E402
from ui.nav import PAGES  # noqa: E402
from ui.theme import apply_theme  # noqa: E402
from views import challenges, history, leaderboard, log_action, overview  # noqa: E402

REQUIRED_AUTH_KEYS = ["redirect_uri", "cookie_secret", "client_id", "client_secret", "server_metadata_url"]

apply_theme()


# ------------------------------------------------------------------ setup checks
def missing_auth_keys() -> list[str]:
    """Names (never values) of required [auth] settings that are missing."""
    try:
        auth = st.secrets.get("auth", {})
    except Exception:
        return REQUIRED_AUTH_KEYS
    return [k for k in REQUIRED_AUTH_KEYS if not auth.get(k)]


def setup_screen(title: str, body: str, items: list[str] | None = None) -> None:
    bullets = "".join(f"<li><code>{c.escape(i)}</code></li>" for i in (items or []))
    c.html(f"""
    <div class="landing"><div class="eco-card" style="padding:2rem">
      <div class="eco-eyebrow">Setup needed</div>
      <div class="eco-title" style="font-size:1.8rem">{c.escape(title)}</div>
      <p style="color:var(--eco-muted)">{c.escape(body)}</p>
      {f'<ul>{bullets}</ul>' if bullets else ''}
      <p style="color:var(--eco-muted);font-size:.85rem">See README.md → "Setup" for step-by-step instructions.</p>
    </div></div>
    """)
    st.stop()


def landing() -> None:
    c.html(f"""
    <div class="landing">
      <div class="eco-hero"><div class="inner"><div style="max-width:620px">
        <span class="pill">{c.icon("eco", 16)} Mission LiFE · HackCult '26</span>
        <div class="big" style="font-size:clamp(2.2rem,5vw,3.4rem);margin-top:1rem">Turn everyday habits into climate action.</div>
        <p style="color:#D4EEDC;font-size:1.05rem;line-height:1.6;margin:0">
          Log sustainable actions, take on daily and weekly challenges, watch your eco tree grow
          and climb a real global leaderboard.</p>
      </div></div></div>
      <div class="feat">
        <div class="eco-card"><div class="kpi"><div class="ic">{c.icon("task_alt")}</div></div><h4>Track 14 actions</h4><p>Across waste, plastic, water, energy, transport and green activities.</p></div>
        <div class="eco-card"><div class="kpi"><div class="ic">{c.icon("flag")}</div></div><h4>Daily & weekly challenges</h4><p>Build habits with missions that reset every day and every week.</p></div>
        <div class="eco-card"><div class="kpi"><div class="ic">{c.icon("insights")}</div></div><h4>See your progress</h4><p>Weekly trends, streaks, impact totals and personalised tips.</p></div>
        <div class="eco-card"><div class="kpi"><div class="ic">{c.icon("leaderboard")}</div></div><h4>Global leaderboard</h4><p>Fair, capped points ranked live across every member.</p></div>
      </div>
    </div>
    """)
    st.write("")
    _, mid, _ = st.columns([1, 1, 1])
    with mid:
        st.button("Continue with Google", type="primary", icon=":material/login:",
                  on_click=st.login)
        st.caption("We only use your Google name to show your progress. Your email is never displayed.")
    c.footer()
    st.stop()


# ------------------------------------------------------------------ auth gate
missing = missing_auth_keys()
if missing:
    setup_screen("Google sign-in isn't configured yet",
                 "Add these settings to the [auth] section of .streamlit/secrets.toml "
                 "(in the same folder as app.py), then restart the app:", missing)

if not st.user.get("is_logged_in", False):
    landing()

uid = st.user.get("sub")
if not uid:
    setup_screen("Your Google account didn't return an ID",
                 "Sign out and sign in again. If it keeps happening, check that "
                 "server_metadata_url points to Google's OpenID configuration.")

name = st.user.get("name") or st.user.get("given_name") or "EcoBin Member"
ctx.set_user(ctx.User(uid=uid, name=name, picture=st.user.get("picture")))

# Create or refresh the Firestore profile once per browser session.
if st.session_state.get("_eco_profile_uid") != uid:
    try:
        ctx.repo().ensure_profile(uid, name)
    except FirebaseSetupError as err:
        setup_screen("Firebase isn't connected yet", str(err))
    except Exception:
        setup_screen("Couldn't reach Firebase",
                     "The app could not connect to Firestore. Check your internet connection, that "
                     "Firestore is enabled for project ecobin-66e68, and that serviceAccountKey.json "
                     "belongs to that project.")
    st.session_state["_eco_profile_uid"] = uid
    ctx.invalidate()


# ------------------------------------------------------------------ navigation
def page_overview():
    overview.render()


def page_log():
    log_action.render()


def page_challenges():
    challenges.render()


def page_history():
    history.render()


def page_leaderboard():
    leaderboard.render()


PAGES.update({
    "overview": st.Page(page_overview, title="Overview", icon=":material/space_dashboard:",
                        url_path="overview", default=True),
    "log": st.Page(page_log, title="Log an action", icon=":material/add_circle:", url_path="log"),
    "challenges": st.Page(page_challenges, title="Challenges", icon=":material/flag:", url_path="challenges"),
    "history": st.Page(page_history, title="Insights", icon=":material/insights:", url_path="insights"),
    "leaderboard": st.Page(page_leaderboard, title="Leaderboard", icon=":material/leaderboard:",
                           url_path="leaderboard"),
})

navigation = st.navigation(list(PAGES.values()), position="sidebar")

st.logo(str(BASE_DIR / "assets" / "logo.svg"), icon_image=str(BASE_DIR / "assets" / "icon.svg"), size="large")

navigation.run()

with st.sidebar:
    user = ctx.current_user()
    try:
        level = level_for(ctx.total_points())[0]
    except Exception:
        level = "EcoBin member"
    avatar = (f'<img src="{c.escape(user.picture)}" alt="" referrerpolicy="no-referrer">' if user.picture
              else f'<div class="initials">{c.initials(user.name)}</div>')
    st.write("")
    c.html(f"""
    <div class="side-user">{avatar}
      <div><div class="who">{c.escape(user.name)}</div><div class="lvl">{c.escape(level)}</div></div>
    </div>
    """)
    st.write("")
    if st.button("Sign out", icon=":material/logout:"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.logout()
    c.html('<div class="side-foot">Mission LiFE · Citizen engagement</div>')

c.footer()
