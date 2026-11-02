"""Per-session state: the signed-in user, the Firestore repository and cached data.

Data is fetched at most once per page view and refreshed after every write, so
pages stay fast without showing stale numbers.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import streamlit as st

from core import stats
from core.dates import today
from core.firebase import create_repository
from core.repository import EcoRepository

_ACTIONS_KEY = "_eco_actions"
_POINTS_KEY = "_eco_points"
_FLASH_KEY = "_eco_flash"


@st.cache_resource(show_spinner=False)
def get_repository() -> EcoRepository:
    service_account = None
    try:
        if "firebase_service_account" in st.secrets:
            service_account = dict(st.secrets["firebase_service_account"])
    except Exception:
        service_account = None  # no secrets file: fall back to serviceAccountKey.json
    return create_repository(service_account)


@dataclass
class User:
    uid: str
    name: str
    picture: str | None


def current_user() -> User:
    return st.session_state["_eco_user"]


def set_user(user: User) -> None:
    st.session_state["_eco_user"] = user


def repo() -> EcoRepository:
    return get_repository()


def actions_frame() -> pd.DataFrame:
    if _ACTIONS_KEY not in st.session_state:
        st.session_state[_ACTIONS_KEY] = stats.to_frame(repo().get_actions(current_user().uid))
    return st.session_state[_ACTIONS_KEY]


def total_points() -> int:
    if _POINTS_KEY not in st.session_state:
        st.session_state[_POINTS_KEY] = repo().get_points(current_user().uid)
    return st.session_state[_POINTS_KEY]


def invalidate() -> None:
    """Call after any write so the next render reloads fresh data."""
    for key in (_ACTIONS_KEY, _POINTS_KEY):
        st.session_state.pop(key, None)
    cached_leaderboard.clear()


@st.cache_data(ttl=30, show_spinner=False)
def cached_leaderboard(limit: int) -> list[dict]:
    return get_repository().leaderboard(limit)


def flash(kind: str, message: str, **extra) -> None:
    """Queue a message to show after the next rerun (st.rerun clears the page)."""
    st.session_state.setdefault(_FLASH_KEY, []).append({"kind": kind, "message": message, **extra})


def pop_flashes() -> list[dict]:
    return st.session_state.pop(_FLASH_KEY, [])


def today_local():
    return today()
