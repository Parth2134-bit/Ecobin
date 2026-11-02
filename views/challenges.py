import streamlit as st

from core import config
from core.dates import week_start
from core.repository import ValidationError
from ui import components as c
from ui import context as ctx


def _card(ch: config.Challenge, done: bool) -> None:
    badge = (f'<span class="badge-pts badge-done">{c.icon("check_circle", 16)} Completed</span>' if done
             else f'<span class="badge-pts">{c.icon("stars", 16)} +{ch.points} pts</span>')
    c.html(f"""
    <div class="eco-card ch-card{' done' if done else ''}">
      <div class="top">{c.category_chip(ch.category)}{badge}</div>
      <h4>{c.escape(ch.title)}</h4>
      <p>{c.escape(ch.description)}</p>
    </div>
    """)


def _grid(challenges: list[config.Challenge], done: set[str]) -> None:
    user = ctx.current_user()
    today = ctx.today_local()
    for i in range(0, len(challenges), 2):
        cols = st.columns(2, gap="medium")
        for col, ch in zip(cols, challenges[i:i + 2]):
            with col:
                is_done = ch.key in done
                _card(ch, is_done)
                if not is_done and st.button("Mark as completed", key=f"ch_{ch.key}",
                                             icon=":material/task_alt:"):
                    try:
                        saved = ctx.repo().complete_challenge(user.uid, ch.key, today)
                    except ValidationError as err:
                        st.warning(str(err))
                    except Exception:
                        st.error("Couldn't reach the cloud database, so nothing was saved. Try again.",
                                 icon=":material/cloud_off:")
                    else:
                        ctx.invalidate()
                        if saved:
                            ctx.flash("success", f"Challenge complete: {ch.title}. +{ch.points} Eco Points!")
                        else:
                            ctx.flash("info", f"{ch.title} was already completed for this period.")
                        st.rerun()
                st.write("")


def render() -> None:
    user = ctx.current_user()
    today = ctx.today_local()
    done = ctx.repo().completed_challenge_ids(user.uid, today)

    c.page_header("Missions", "Daily & weekly challenges",
                  "Commit to a habit, complete it, then mark it done. Each challenge can be "
                  "completed once per day or once per week.")

    for f in ctx.pop_flashes():
        (st.success if f["kind"] == "success" else st.info)(f["message"], icon=":material/flag:")

    daily = [ch for ch in config.CHALLENGES.values() if ch.period == "daily"]
    weekly = [ch for ch in config.CHALLENGES.values() if ch.period == "weekly"]
    d_done = sum(ch.key in done for ch in daily)
    w_done = sum(ch.key in done for ch in weekly)

    c.section(f"Today · {d_done}/{len(daily)} done", f"Resets at midnight · {today.strftime('%A %d %b')}")
    _grid(daily, done)

    c.section(f"This week · {w_done}/{len(weekly)} done",
              f"Week of {week_start(today).strftime('%d %b')} · resets Monday")
    _grid(weekly, done)
