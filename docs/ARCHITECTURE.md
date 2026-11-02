# EcoBin architecture

## Request flow

```
Browser ──► Streamlit (app.py)
              │  1. Google OIDC sign-in (st.login) → st.user.sub = permanent Google user ID
              │  2. ensure_profile(uid)  (once per session, transactional)
              │  3. st.navigation → views/*.render()
              ▼
         ui/context.py  (session cache, flash messages)
              ▼
         core/repository.py ──► Cloud Firestore (Firebase Admin SDK, server-side only)
         core/stats.py, core/recommendations.py  (pure pandas, no I/O)
```

## Firestore data model

```
users/{uid}                      display_name, public_name, total_points, created_at, last_active
users/{uid}/actions/{id}         kind (action|challenge), key, label, category, quantity,
                                 points, date, week, notes, created_at
users/{uid}/days/{YYYY-MM-DD}    action_points           ← daily cap counter
users/{uid}/challenges/{period}__{key}                   ← one doc per completion period
```

* **Isolation:** every record lives under the user's own document, keyed by Google's `sub` claim. Different Google accounts cannot read or change each other's data.
* **Leaderboard:** `users` ordered by `total_points` (single-field index, created automatically). Rank = 1 + count of users with more points (Firestore `count()` aggregation).
* **Atomicity:** each write that awards points (action record + daily counter + user total) is one transaction. Challenge documents have deterministic IDs, so a second completion in the same day/week is rejected inside the transaction.
* **Security:** `firestore.rules` denies all client access. Only the server (Admin SDK) reads and writes.

## Design decisions

| Decision | Why |
|---|---|
| Firestore only (SQLite removed) | The old app wrote to both stores. SQLite had no user column and a global unique constraint, so multi-user data could never be consistent. One source of truth removes that class of bugs. |
| Streamlit native auth instead of Firebase Auth | Works server-side with no JavaScript bridge. `sub` is a stable, unique Google account ID. |
| Points rules in `core/config.py` | The UI and database read the same values, so they can't drift apart. |
| Daily cap + 7-day backdate limit + qty ≤ 10 | Self-reported actions can't be verified, so caps keep the global leaderboard credible. |
| Public name = first name + last initial | The leaderboard is visible to all members, so less personal data is shown. |
| Facts with sources, no CO₂ numbers | Impact numbers for self-reported actions would be guesses; cited general facts are honest. |
| `core/` has no Streamlit import | All business logic is unit-testable with an in-memory Firestore fake. |
