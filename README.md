# 🌱 EcoBin: Sustainable living, made measurable

**HackCult '26 · Problem statement HC26-GEDA01: Mission LiFE citizen engagement application**
Theme: Green Energy and Sustainability

EcoBin helps citizens build sustainable daily habits. Members sign in with Google, log eco-friendly actions across six categories, complete daily and weekly challenges, follow their weekly progress, get personalised suggestions, and compete on a live global leaderboard.

---

## Features

| Area | What it does |
|---|---|
| **Google sign-in** | Secure OpenID Connect login via Streamlit's native auth. Each Google account is a separate EcoBin profile. |
| **Action tracking** | 14 actions in 6 categories: Waste Management, Plastic Reduction, Water Conservation, Energy Conservation, Sustainable Transport, Green Activities. |
| **Fair points** | Points per action, max 10 per entry, a **200-point daily cap** on actions, and logging allowed only for the last 7 days. All rules are enforced server-side in Firestore transactions. |
| **Challenges** | 4 daily challenges (reset at midnight IST) and 3 weekly challenges (reset Monday). Each can be completed once per period, with no double points. |
| **Dashboard** | Level and progress, day streak, today/this-week points with week-over-week change, 14-day trend, category donut, growing eco tree. |
| **Insights** | Weekly (8 weeks) and daily (30 days) charts, category balance, impact summary, filterable history, CSV export. |
| **Recommendations** | Tips drawn from the categories you've used least, rotating as you progress. |
| **Environmental context** | After each action, a short fact with its public source. No invented "CO₂ saved" numbers. |
| **Global leaderboard** | Real users from Firestore, ranked live, with your global rank. Shows first name + last initial only. |

## Tech stack

Python · Streamlit (with `[auth]`) · Firebase Admin SDK · Cloud Firestore · Pandas · Plotly · Google OAuth (OIDC)

## Project structure

```
EcoBin/
├── app.py                      # Entry point: page config, sign-in gate, navigation
├── core/                       # Logic only (no Streamlit), fully unit-tested
│   ├── config.py               # Categories, actions, challenges, points, caps, levels, facts
│   ├── dates.py                # "Today" / ISO-week helpers (Asia/Kolkata)
│   ├── firebase.py             # Firestore connection (key file or secrets)
│   ├── repository.py           # All Firestore reads/writes, transactional
│   ├── stats.py                # Daily/weekly statistics, streaks, impact summary
│   └── recommendations.py      # Personalised tips
├── ui/
│   ├── theme.py                # All CSS (modern green theme)
│   ├── components.py           # Hero, KPI cards, charts, cards (HTML-escaped)
│   ├── context.py              # Session user, cached data, flash messages
│   └── nav.py                  # Page registry
├── views/                      # One file per page
│   ├── overview.py  log_action.py  challenges.py  history.py  leaderboard.py
├── assets/                     # logo.svg, icon.svg
├── scripts/
│   ├── check_setup.py          # Verifies installation + credentials (prints no secrets)
│   └── import_legacy_sqlite.py # Optional: import old ecobin.db into one account
├── tests/                      # pytest suite with an in-memory Firestore fake
├── .streamlit/
│   ├── config.toml             # Theme
│   └── secrets.example.toml    # Template → copy to secrets.toml (git-ignored)
├── docs/                       # Architecture notes + demo/testing checklist
├── firestore.rules             # Deny all client access (server-only database)
├── requirements.txt            # Runtime dependencies (pinned)
└── requirements-dev.txt        # + pytest
```

---

## Setup (Windows + VS Code)

> Use **Python 3.11, 3.12 or 3.13**. Check with `python --version`.

### 1. Put the project in a short, non-synced folder

OneDrive can lock or half-sync files while Python reads them, which caused some of the earlier import errors. Use a plain folder such as:

```
C:\Projects\EcoBin
```

Open that folder in VS Code (**File → Open Folder**). Then open a terminal (**Terminal → New Terminal**). It must show `C:\Projects\EcoBin>`.

### 2. Create a virtual environment and install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

If PowerShell blocks `Activate.ps1`, run this once, then activate again:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

In VS Code press `Ctrl+Shift+P` → **Python: Select Interpreter** → choose the one inside `.venv`.

### 3. Add your private files (never commit these)

| File | Where it comes from |
|---|---|
| `serviceAccountKey.json` (next to `app.py`) | Firebase Console → ⚙ Project settings → **Service accounts** → *Generate new private key*. Rename the download to `serviceAccountKey.json`. |
| `.streamlit/secrets.toml` | Copy `.streamlit/secrets.example.toml` and fill in the `[auth]` values (step 4). |

Generate a strong `cookie_secret`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 4. Google Cloud OAuth settings (project `ecobin-66e68`)

Google Cloud Console → **APIs & Services** (or **Google Auth Platform**):

1. **Clients → your OAuth client (type: Web application)**
   - *Authorised redirect URIs* must include exactly: `http://localhost:8501/oauth2callback`
   - Copy the **Client ID** (ends with `.apps.googleusercontent.com`) and **Client secret** into `secrets.toml`.
2. **Audience / OAuth consent screen**
   - If *Publishing status* is **Testing**, only the Google accounts listed under **Test users** can sign in. Add your second test account and any judge/demo accounts, or click **Publish app**. EcoBin only requests `openid`, `email` and `profile`, which don't need Google verification.

> The "Google" provider under Firebase Authentication is not used. EcoBin signs in through Streamlit directly with Google. Firestore is used for data only.

### 5. Firestore

1. Firebase Console → **Firestore Database**. It should already exist (Native mode).
2. **Rules** tab → paste the contents of `firestore.rules` → **Publish**. The app uses the Admin SDK on the server, so this blocks only direct browser access.
3. No indexes need to be created manually.

### 6. Check everything

```powershell
python scripts\check_setup.py
```

Every line should say `[ OK ]`. The script never prints secret values.

### 7. Run

```powershell
python -m streamlit run app.py
```

Open http://localhost:8501 → **Continue with Google**.
Always run this command **from the project folder** (the terminal shows `...\EcoBin>`).

### 8. Run the tests

```powershell
python -m pytest -q
```

The tests cover points, daily caps, challenge duplicates, weekly resets, user isolation, ranking and statistics. They use an in-memory Firestore fake, so they don't need credentials and never touch your real data.

---

## Your old data (`ecobin.db`)

The previous version stored 32 actions and 4 challenges in a local SQLite file **without user accounts**. The new version doesn't use SQLite, so:

- Keep your old `ecobin.db` where it is, or copy it into a `backups\` folder (git-ignored). Nothing in this project modifies it.
- **Optional:** import it into your Google account:
  ```powershell
  # sign in to the app once first, then:
  python scripts\import_legacy_sqlite.py --list-users
  python scripts\import_legacy_sqlite.py --db "C:\path\to\old\ecobin.db" --uid YOUR_UID           # preview
  python scripts\import_legacy_sqlite.py --db "C:\path\to\old\ecobin.db" --uid YOUR_UID --commit  # import
  ```
  The file is opened read-only. Running it twice won't duplicate anything.
  Note: those records add 1,640 points to your account on the leaderboard.

---

## Troubleshooting

| Message | Cause → fix |
|---|---|
| `StreamlitMissingAuthlibError` | Installed `streamlit` without `[auth]` → `python -m pip install -r requirements.txt` inside the activated `.venv`. |
| `Error 401: invalid_client` | `client_id` isn't the Web client ID → copy it from *Clients*; it ends with `.apps.googleusercontent.com`. |
| `Error 400: redirect_uri_mismatch` | Redirect URI in Google Cloud ≠ `redirect_uri` in secrets → make both exactly `http://localhost:8501/oauth2callback`. |
| `Error 403: access_denied` (second account) | Consent screen is in *Testing* → add the account as a test user or publish the app. |
| "Google sign-in isn't configured yet" | `secrets.toml` missing or in the wrong place → it must be `.streamlit\secrets.toml` inside the project folder. |
| "Firebase isn't connected yet" | `serviceAccountKey.json` missing or from another project → re-download, run `check_setup.py`. |
| `ModuleNotFoundError: core` / odd import errors | Started from the wrong folder or wrong Python → `cd` to the project, activate `.venv`, use `python -m streamlit run app.py`. Delete stray `__pycache__` folders if you copied files around. |
| Port 8501 busy | Another Streamlit is running → close it (`Ctrl+C` in its terminal). The redirect URI depends on port 8501. |

---

## Git: safely updating the existing repository

Repository: `https://github.com/Parth2134-bit/Ecobin.git` (private). Nothing is pushed automatically.

```powershell
# 1. Clone into a fresh folder (or cd into your existing clone)
cd C:\Projects
git clone https://github.com/Parth2134-bit/Ecobin.git EcoBin-repo
cd EcoBin-repo

# 2. Work on a new branch so main stays untouched until you're happy
git checkout -b rebuild-v2

# 3. CHECK FIRST: were secrets or the database ever committed?
git ls-files | findstr /i "secrets.toml serviceAccountKey ecobin.db firebase-adminsdk"
#    No output = good. If anything is listed, see "If a secret was committed" below.

# 4. Remove the old app files from the branch (they stay in git history)
git rm --quiet app.py database.py firebase_cloud.py firebase_config.py recommendations.py requirements.txt .gitignore
#    (ignore "did not match any files" for files that were never committed)

# 5. Copy ALL files from this new EcoBin folder into EcoBin-repo
#    (use File Explorer; do NOT copy .venv, secrets.toml, serviceAccountKey.json or *.db)

# 6. Review what will be committed. Secrets must NOT appear in the list.
git add .
git status

# 7. Commit and push the branch
git commit -m "Rebuild EcoBin: Firestore-only data, Google auth, challenges, insights, new UI"
git push -u origin rebuild-v2
```

Then on GitHub open a Pull Request from `rebuild-v2` into `main`, review it and merge.

**If a secret was committed:** deleting the file isn't enough, because it remains in history. Rotate the secret instead:
- Firebase Console → Service accounts → delete that key, then generate a new one.
- Google Cloud → your OAuth client → **Reset secret** → update `secrets.toml`.
- Generate a new `cookie_secret`.

---

## Deploying for judges (optional)

On Streamlit Community Cloud: deploy the repo, then paste your `secrets.toml` contents into **App settings → Secrets**. Include a `[firebase_service_account]` table (see the example file) instead of uploading the JSON key. Set `redirect_uri = "https://<your-app>.streamlit.app/oauth2callback"`, and add that same URI in Google Cloud → Clients → Authorised redirect URIs.
