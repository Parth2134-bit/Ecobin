# EcoBin testing & demo checklist

Tick each item on your own machine before the demo. Items marked 🔑 need live Google/Firebase credentials.

## A. Automated (no credentials)
- [ ] `python -m pytest -q` → all tests pass
- [ ] `python scripts\check_setup.py` → all `[ OK ]` 🔑

## B. Sign-in 🔑
- [ ] Logged-out visit shows the EcoBin landing page with **Continue with Google**
- [ ] Sign in with **Account A** → lands on Overview, sidebar shows A's name/photo
- [ ] Refresh the browser (F5) → still signed in (session persists)
- [ ] **Sign out** → back to landing page; refresh → still signed out
- [ ] Firestore Console → `users/<A's uid>` exists with `total_points: 0`, `public_name`

## C. Actions & points 🔑
- [ ] Log "Planted a tree" ×1 → success message + "Why it matters" fact appear; Overview shows +25
- [ ] Try quantity 8 of "Planted a tree" again → rejected by daily cap (200), nothing saved
- [ ] Log an action dated 3 days ago → appears in Insights at that date
- [ ] Today's allowance meter updates after each save

## D. Challenges 🔑
- [ ] Complete "Green Commute" → +20, card shows **Completed**
- [ ] Refresh → still completed, button gone (no double points)
- [ ] Complete a weekly challenge → counted in "This week x/3 done"

## E. Two accounts and the leaderboard 🔑 (required before claiming "global")
- [ ] Open a **private/incognito window**, sign in with **Account B** (add B as a test user first if the consent screen is in Testing)
- [ ] B's Overview shows 0 points and none of A's actions
- [ ] B logs an action worth more than A's total
- [ ] Leaderboard (either account, press **Refresh**) shows both A and B in the correct order, names as "First L."
- [ ] Each account's "Your rank" matches its position
- [ ] Firestore Console: A's and B's actions are under their own `users/{uid}/actions`

## F. Insights & recommendations 🔑
- [ ] Insights shows weekly bars, daily trend, category donut, impact summary, table
- [ ] Category filter narrows the table; **Download CSV** works
- [ ] Recommended next steps point at categories you haven't used

## G. Before pushing to GitHub
- [ ] `git status` does **not** list `secrets.toml`, `serviceAccountKey.json`, `*.db`, `.venv`

## Demo script (3 minutes)
1. Landing page → Google sign-in (10 s)
2. Overview: hero, level, streak, charts, eco tree, recommendations (40 s)
3. Log an action → fact card → points update (30 s)
4. Challenges: complete one daily, show once-per-day protection (30 s)
5. Insights: weekly trend + impact summary (30 s)
6. Leaderboard with two real accounts; mention caps keep it fair (30 s)
