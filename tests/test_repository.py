"""Firestore data-layer tests (run against the in-memory fake, no credentials needed)."""

from datetime import date, timedelta

import pytest

from core import config
from core.repository import DailyCapReached, ValidationError, public_name_from

TODAY = date(2026, 11, 3)  # a Tuesday


def test_profile_created_once_and_points_never_reset(repo):
    p = repo.ensure_profile("alice", "Alice Sharma")
    assert p.total_points == 0 and p.public_name == "Alice S."
    repo.log_action("alice", "plant_tree", 1, TODAY, TODAY)
    again = repo.ensure_profile("alice", "Alice Sharma")
    assert again.total_points == 25
    assert repo.get_points("alice") == 25


def test_profile_name_refreshes(repo, client):
    repo.ensure_profile("alice", "Alice")
    repo.ensure_profile("alice", "Alice Sharma")
    assert client.store["users/alice"]["public_name"] == "Alice S."


def test_log_action_awards_points_and_stores_record(repo, client):
    repo.ensure_profile("u1", "U One")
    pts = repo.log_action("u1", "public_transport", 2, TODAY, TODAY, notes="  metro \n to class ")
    assert pts == 30
    assert repo.get_points("u1") == 30
    rows = repo.get_actions("u1")
    assert len(rows) == 1
    assert rows[0]["notes"] == "metro to class"
    assert rows[0]["category"] == "transport"
    assert rows[0]["week"] == "2026-W45"
    assert client.store["users/u1/days/2026-11-03"]["action_points"] == 30


@pytest.mark.parametrize("kwargs, message", [
    (dict(action_key="nope", quantity=1), "valid action"),
    (dict(action_key="recycle", quantity=0), "between 1 and"),
    (dict(action_key="recycle", quantity=config.MAX_QUANTITY_PER_ENTRY + 1), "between 1 and"),
    (dict(action_key="recycle", quantity="abc"), "whole number"),
    (dict(action_key="recycle", quantity=1, action_date=TODAY + timedelta(days=1)), "future"),
    (dict(action_key="recycle", quantity=1,
          action_date=TODAY - timedelta(days=config.BACKDATE_LIMIT_DAYS + 1)), "last"),
])
def test_invalid_actions_rejected_and_nothing_written(repo, client, kwargs, message):
    repo.ensure_profile("u1", "U")
    before = dict(client.store)
    kwargs.setdefault("action_date", TODAY)
    with pytest.raises(ValidationError, match=message):
        repo.log_action("u1", today=TODAY, **kwargs)
    assert client.store == before


def test_signed_out_user_rejected(repo):
    with pytest.raises(ValidationError):
        repo.log_action("", "recycle", 1, TODAY, TODAY)


def test_daily_cap_enforced_atomically(repo, client):
    repo.ensure_profile("u1", "U")
    # 25 * 8 = 200 = cap exactly
    assert repo.log_action("u1", "plant_tree", 8, TODAY, TODAY) == 200
    with pytest.raises(DailyCapReached) as exc:
        repo.log_action("u1", "recycle", 1, TODAY, TODAY)
    assert exc.value.remaining == 0
    assert repo.get_points("u1") == 200
    assert len(repo.get_actions("u1")) == 1
    # a different day has its own allowance
    assert repo.log_action("u1", "recycle", 1, TODAY - timedelta(days=1), TODAY) == 15


def test_daily_cap_reports_remaining(repo):
    repo.ensure_profile("u1", "U")
    repo.log_action("u1", "plant_tree", 7, TODAY, TODAY)  # 175
    with pytest.raises(DailyCapReached) as exc:
        repo.log_action("u1", "plant_tree", 2, TODAY, TODAY)
    assert exc.value.remaining == 25


def test_challenges_do_not_count_toward_action_cap(repo):
    repo.ensure_profile("u1", "U")
    repo.log_action("u1", "plant_tree", 8, TODAY, TODAY)
    assert repo.complete_challenge("u1", "green_commute", TODAY) is True
    assert repo.get_points("u1") == 220


def test_daily_challenge_once_per_day(repo):
    repo.ensure_profile("u1", "U")
    assert repo.complete_challenge("u1", "save_water_day", TODAY) is True
    assert repo.complete_challenge("u1", "save_water_day", TODAY) is False
    assert repo.get_points("u1") == 15
    assert repo.complete_challenge("u1", "save_water_day", TODAY + timedelta(days=1)) is True
    assert repo.get_points("u1") == 30


def test_weekly_challenge_once_per_week(repo):
    repo.ensure_profile("u1", "U")
    monday = date(2026, 11, 2)
    assert repo.complete_challenge("u1", "byo_week", monday) is True
    assert repo.complete_challenge("u1", "byo_week", monday + timedelta(days=6)) is False  # Sunday
    assert repo.complete_challenge("u1", "byo_week", monday + timedelta(days=7)) is True
    assert repo.get_points("u1") == 100


def test_completed_challenge_ids_only_current_period(repo):
    repo.ensure_profile("u1", "U")
    repo.complete_challenge("u1", "switch_it_off", TODAY - timedelta(days=1))
    repo.complete_challenge("u1", "plant_and_care", TODAY - timedelta(days=1))  # same week
    repo.complete_challenge("u1", "green_commute", TODAY)
    assert repo.completed_challenge_ids("u1", TODAY) == {"plant_and_care", "green_commute"}


def test_challenge_creates_history_entry(repo):
    repo.ensure_profile("u1", "U")
    repo.complete_challenge("u1", "plastic_free_day", TODAY)
    rows = repo.get_actions("u1")
    assert rows[0]["kind"] == "challenge" and rows[0]["points"] == 20


def test_users_are_isolated_and_leaderboard_is_real(repo):
    repo.ensure_profile("a", "Asha Rao")
    repo.ensure_profile("b", "Bilal Khan")
    repo.ensure_profile("c", "Chen")
    repo.log_action("a", "recycle", 2, TODAY, TODAY)       # 30
    repo.log_action("b", "plant_tree", 4, TODAY, TODAY)    # 100
    assert len(repo.get_actions("a")) == 1
    assert len(repo.get_actions("b")) == 1
    assert repo.get_actions("c") == []

    board = repo.leaderboard()
    assert [(r["name"], r["points"]) for r in board] == [("Bilal K.", 100), ("Asha R.", 30), ("Chen", 0)]
    assert repo.rank("b", 100) == 1
    assert repo.rank("a", 30) == 2
    assert repo.rank("c", 0) == 3
    assert repo.member_count() == 3


def test_ties_share_rank(repo):
    for uid in ["x", "y"]:
        repo.ensure_profile(uid, uid)
        repo.log_action(uid, "recycle", 1, TODAY, TODAY)
    assert repo.rank("x", 15) == repo.rank("y", 15) == 1


def test_leaderboard_limit(repo):
    for i in range(5):
        repo.ensure_profile(f"u{i}", f"User {i}")
    assert len(repo.leaderboard(limit=3)) == 3


def test_public_name():
    assert public_name_from("Parth Khatri") == "Parth K."
    assert public_name_from("Madonna") == "Madonna"
    assert public_name_from("") == "EcoBin Member"
    assert public_name_from(None) == "EcoBin Member"
