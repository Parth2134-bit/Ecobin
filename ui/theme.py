"""Global styles. Colours are defined once as CSS variables in :root."""

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,400,1,0&display=block');

:root {
  --eco-forest: #0F3D2E;
  --eco-deep: #14532D;
  --eco-green: #1F7A4D;
  --eco-leaf: #3FA36B;
  --eco-mint: #DDF0E3;
  --eco-sage: #EEF4EC;
  --eco-bg: #F4F7F2;
  --eco-card: #FFFFFF;
  --eco-line: #E2EAE0;
  --eco-ink: #13261D;
  --eco-muted: #5D6F64;
  --eco-amber: #D9A441;
  --eco-shadow: 0 1px 2px rgba(16, 48, 32, .05), 0 8px 24px rgba(16, 48, 32, .06);
  --eco-radius: 18px;
}

html, body, [class*="css"], .stApp, button, input, textarea, select {
  font-family: "Plus Jakarta Sans", "Segoe UI", system-ui, sans-serif !important;
}
.material-symbols-rounded {
  font-family: "Material Symbols Rounded" !important;
  font-weight: normal; font-style: normal; line-height: 1;
  letter-spacing: normal; text-transform: none; display: inline-block;
  white-space: nowrap; direction: ltr; -webkit-font-smoothing: antialiased;
  width: 1em; height: 1em; overflow: hidden; vertical-align: -0.15em;
  font-variation-settings: 'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24;
}

.stApp {
  background:
    radial-gradient(1200px 500px at 100% -10%, rgba(63,163,107,.10), transparent 60%),
    radial-gradient(900px 400px at -10% 0%, rgba(217,164,65,.07), transparent 60%),
    var(--eco-bg);
  color: var(--eco-ink);
}
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1280px; padding-top: 2rem; padding-bottom: 4rem; }

h1, h2, h3, h4 { color: var(--eco-ink) !important; letter-spacing: -.02em; }

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0F3D2E 0%, #0B2F23 100%);
  border-right: none;
}
[data-testid="stSidebar"] * { color: #E7F2EA; }
[data-testid="stSidebarNavLink"] {
  border-radius: 12px; padding: .45rem .75rem; margin: 2px 0;
  transition: background .15s ease;
}
[data-testid="stSidebarNavLink"]:hover { background: rgba(255,255,255,.08); }
[data-testid="stSidebarNavLink"][aria-current="page"] { background: rgba(63,163,107,.28); }
[data-testid="stSidebarNavLink"] span { color: #E7F2EA !important; font-weight: 600; }
[data-testid="stSidebar"] .stButton button {
  background: rgba(255,255,255,.08) !important; color: #E7F2EA !important;
  border: 1px solid rgba(255,255,255,.15) !important;
}
[data-testid="stSidebar"] .stButton button:hover { background: rgba(255,255,255,.16) !important; }

.side-brand { display:flex; align-items:center; gap:.6rem; padding:.25rem 0 1rem; }
.side-brand .logo {
  width:38px; height:38px; border-radius:12px; display:grid; place-items:center;
  background: linear-gradient(135deg, #3FA36B, #1F7A4D); color:#fff;
  box-shadow: 0 6px 16px rgba(63,163,107,.35);
}
.side-brand .name { font-size:1.35rem; font-weight:800; letter-spacing:-.03em; color:#fff; }
.side-brand .tag { font-size:.72rem; color:#9FC7AE; margin-top:-2px; }
.side-user {
  display:flex; align-items:center; gap:.7rem; padding:.75rem; border-radius:14px;
  background: rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.08);
}
.side-user img, .side-user .initials {
  width:38px; height:38px; border-radius:50%; object-fit:cover; flex-shrink:0;
}
.side-user .initials { display:grid; place-items:center; background:#3FA36B; color:#fff; font-weight:700; }
.side-user .who { font-weight:700; font-size:.92rem; color:#fff; line-height:1.2; }
.side-user .lvl { font-size:.75rem; color:#9FC7AE; }
.side-foot { font-size:.7rem; letter-spacing:.12em; color:#7FA892; text-transform:uppercase; margin-top:.5rem; }

/* ---------- Buttons & inputs ---------- */
.stButton button, .stFormSubmitButton button, .stDownloadButton button {
  border-radius: 12px !important; font-weight: 700 !important; padding: .55rem 1.1rem !important;
  transition: transform .12s ease, box-shadow .12s ease, background .12s ease;
}
.stButton button[kind="primary"], .stFormSubmitButton button[kind="primaryFormSubmit"] {
  background: linear-gradient(135deg, #1F7A4D, #14532D) !important; border: none !important;
  box-shadow: 0 6px 16px rgba(31,122,77,.25);
}
.stButton button[kind="primary"]:hover, .stFormSubmitButton button[kind="primaryFormSubmit"]:hover {
  transform: translateY(-1px); box-shadow: 0 10px 22px rgba(31,122,77,.32);
}
[data-testid="stColumn"] .stButton button { width: 100%; }
.stTextInput input, .stTextArea textarea, .stNumberInput input, .stDateInput input,
.stSelectbox div[data-baseweb="select"] > div {
  border-radius: 12px !important; background: #fff !important;
}
[data-testid="stForm"] {
  background: var(--eco-card); border: 1px solid var(--eco-line); border-radius: var(--eco-radius);
  padding: 1.4rem 1.4rem .8rem; box-shadow: var(--eco-shadow);
}
[data-testid="stPageLink"] a {
  background: var(--eco-card); border:1px solid var(--eco-line); border-radius: 14px;
  padding: .7rem 1rem; box-shadow: var(--eco-shadow); transition: transform .12s ease;
}
[data-testid="stPageLink"] a:hover { transform: translateY(-2px); border-color: #A9D3B8; }
[data-testid="stPageLink"] a span { font-weight: 700; color: var(--eco-deep) !important; }
[data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border:1px solid var(--eco-line); }
[data-testid="stPlotlyChart"] {
  background: var(--eco-card); border:1px solid var(--eco-line); border-radius: var(--eco-radius);
  padding: .6rem; box-shadow: var(--eco-shadow);
}

/* ---------- Page header ---------- */
.eco-eyebrow { font-size:.75rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; color: var(--eco-green); }
.eco-title { font-size: clamp(1.8rem, 3vw, 2.5rem); font-weight:800; letter-spacing:-.035em; color: var(--eco-ink); margin:.2rem 0 .3rem; line-height:1.1; }
.eco-sub { color: var(--eco-muted); font-size: 1rem; margin-bottom: 1.2rem; max-width: 720px; }
.eco-section { display:flex; align-items:baseline; justify-content:space-between; margin: 1.6rem 0 .7rem; }
.eco-section h3 { font-size:1.15rem; font-weight:800; margin:0; }
.eco-section span { color: var(--eco-muted); font-size:.85rem; }

/* ---------- Hero ---------- */
.eco-hero {
  position:relative; overflow:hidden; border-radius: 26px; padding: 2rem 2.2rem;
  background: linear-gradient(125deg, #0F3D2E 0%, #14532D 40%, #1F7A4D 75%, #3FA36B 100%);
  color:#fff; box-shadow: 0 18px 40px rgba(20,83,45,.28);
}
.eco-hero::before, .eco-hero::after {
  content:""; position:absolute; border-radius:50%; background: rgba(255,255,255,.07);
}
.eco-hero::before { width:340px; height:340px; right:-90px; top:-140px; }
.eco-hero::after { width:220px; height:220px; right:120px; bottom:-150px; background: rgba(217,164,65,.14); }
.eco-hero .inner { position:relative; z-index:1; display:flex; gap:2rem; justify-content:space-between; flex-wrap:wrap; align-items:flex-end; }
.eco-hero .hello { font-size:.95rem; color:#BFE3CB; font-weight:600; }
.eco-hero .big { font-size: clamp(1.7rem, 3.2vw, 2.4rem); font-weight:800; letter-spacing:-.03em; margin:.2rem 0 .6rem; line-height:1.15; color:#fff; }
.eco-hero .pill {
  display:inline-flex; align-items:center; gap:.35rem; padding:.3rem .75rem; border-radius:999px;
  background: rgba(255,255,255,.14); border:1px solid rgba(255,255,255,.18);
  font-size:.82rem; font-weight:700; color:#fff; margin-right:.4rem;
}
.eco-hero .points { text-align:right; min-width: 240px; }
.eco-hero .points .n { font-size: clamp(2.4rem, 5vw, 3.4rem); font-weight:800; letter-spacing:-.04em; line-height:1; color:#fff; }
.eco-hero .points .l { color:#BFE3CB; font-size:.85rem; font-weight:600; }
.eco-bar { height:10px; border-radius:999px; background: rgba(255,255,255,.18); overflow:hidden; margin-top:.8rem; }
.eco-bar > div { height:100%; border-radius:999px; background: linear-gradient(90deg, #A7E8BF, #F2D27A); }
.eco-hero .next { font-size:.8rem; color:#BFE3CB; margin-top:.4rem; }

/* ---------- Cards ---------- */
.eco-card {
  background: var(--eco-card); border:1px solid var(--eco-line); border-radius: var(--eco-radius);
  padding: 1.15rem 1.2rem; box-shadow: var(--eco-shadow); margin-bottom: .25rem;
  transition: transform .15s ease, border-color .15s ease;
}
.eco-card:hover { transform: translateY(-2px); border-color:#C9E2D1; }
.kpi { display:flex; gap:.9rem; align-items:center; }
.kpi .ic {
  width:46px; height:46px; border-radius:14px; display:grid; place-items:center; flex-shrink:0;
  background: var(--eco-mint); color: var(--eco-green); font-size: 24px;
}
.kpi .lab { color: var(--eco-muted); font-size:.82rem; font-weight:600; }
.kpi .val { font-size:1.65rem; font-weight:800; letter-spacing:-.03em; color: var(--eco-ink); line-height:1.15; }
.kpi .delta { font-size:.76rem; font-weight:700; }
.delta.up { color:#1F7A4D; } .delta.down { color:#B5523B; } .delta.flat { color: var(--eco-muted); }

.chip {
  display:inline-flex; align-items:center; gap:.3rem; padding:.22rem .6rem; border-radius:999px;
  font-size:.72rem; font-weight:800; letter-spacing:.04em; text-transform:uppercase;
}
.badge-pts {
  display:inline-flex; align-items:center; gap:.25rem; padding:.28rem .7rem; border-radius:999px;
  background:#FFF6E3; color:#8A6214; font-weight:800; font-size:.8rem;
}
.badge-done { background: var(--eco-mint); color: var(--eco-deep); }

.tip-card .cat { display:flex; align-items:center; gap:.5rem; margin-bottom:.6rem; }
.tip-card .cat .ic { width:34px; height:34px; border-radius:10px; display:grid; place-items:center; color:#fff; font-size:19px; }
.tip-card .cat b { font-size:.85rem; color: var(--eco-ink); }
.tip-card p { margin:0; color:#33463B; font-size:.93rem; line-height:1.55; }

.ch-card { position:relative; min-height: 150px; }
.tip-card { min-height: 140px; }
.ch-card .top { display:flex; justify-content:space-between; align-items:center; margin-bottom:.7rem; gap:.5rem; }
.ch-card h4 { margin:.1rem 0 .35rem; font-size:1.08rem; font-weight:800; }
.ch-card p { margin:0; color: var(--eco-muted); font-size:.9rem; line-height:1.5; }
.ch-card.done { background: linear-gradient(135deg, #F3FAF5, #E6F4EA); border-color:#BFE0CA; }

.impact { display:flex; align-items:center; gap:.8rem; padding:.7rem 0; border-bottom:1px dashed var(--eco-line); }
.impact:last-child { border-bottom:none; }
.impact .ic { width:38px; height:38px; border-radius:12px; display:grid; place-items:center; color:#fff; font-size:20px; flex-shrink:0; }
.impact .q { font-size:1.15rem; font-weight:800; color: var(--eco-ink); }
.impact .u { color: var(--eco-muted); font-size:.85rem; }

.fact { border-left: 4px solid var(--eco-leaf); }
.fact .k { font-size:.72rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color: var(--eco-green); }
.fact p { margin:.4rem 0 .3rem; color:#33463B; line-height:1.55; }
.fact small { color:#7A8B80; }

.meter { height:10px; border-radius:999px; background: var(--eco-sage); overflow:hidden; margin:.5rem 0 .3rem; }
.meter > div { height:100%; border-radius:999px; background: linear-gradient(90deg, #3FA36B, #1F7A4D); }

/* ---------- Leaderboard ---------- */
.podium { display:grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; align-items:end; }
.pod { text-align:center; border-radius: 20px; padding: 1.1rem .8rem; color:#fff; box-shadow: var(--eco-shadow); }
.pod .av { width:56px; height:56px; border-radius:50%; margin: 0 auto .5rem; display:grid; place-items:center;
  background: rgba(255,255,255,.2); font-weight:800; font-size:1.2rem; border:2px solid rgba(255,255,255,.5); }
.pod .nm { font-weight:800; font-size:1rem; }
.pod .pt { font-size:.85rem; opacity:.9; }
.pod .rk { font-size:.7rem; font-weight:800; letter-spacing:.15em; opacity:.8; }
.pod.r1 { background: linear-gradient(160deg, #1F7A4D, #0F3D2E); padding-top:1.8rem; }
.pod.r2 { background: linear-gradient(160deg, #5E9C76, #2F6B4F); }
.pod.r3 { background: linear-gradient(160deg, #C79A3E, #8A6214); }
.lb-row { display:flex; align-items:center; gap:.9rem; padding:.7rem 1rem; border-radius:14px; background: var(--eco-card);
  border:1px solid var(--eco-line); margin-bottom:.5rem; }
.lb-row .rk { width:2.2rem; font-weight:800; color: var(--eco-muted); }
.lb-row .av { width:34px; height:34px; border-radius:50%; display:grid; place-items:center; background: var(--eco-mint); color: var(--eco-deep); font-weight:800; font-size:.85rem; }
.lb-row .nm { flex:1; font-weight:700; }
.lb-row .pt { font-weight:800; color: var(--eco-deep); }
.lb-row.me { background: linear-gradient(135deg, #EAF6EE, #DDF0E3); border-color:#A9D3B8; }

/* ---------- Landing ---------- */
.landing { max-width: 980px; margin: 4vh auto 0; }
.landing .eco-hero { padding: 3rem 2.6rem; }
.landing .feat { display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1.2rem; }
.landing .feat .eco-card h4 { margin:.6rem 0 .25rem; font-size:1rem; font-weight:800; }
.landing .feat .eco-card p { margin:0; color: var(--eco-muted); font-size:.88rem; }

.eco-footer { text-align:center; color: var(--eco-muted); font-size:.78rem; margin-top: 3rem; padding-top: 1.2rem; border-top: 1px solid var(--eco-line); }

@media (max-width: 720px) {
  .eco-hero { padding: 1.5rem; }
  .eco-hero .points { text-align:left; }
  .podium { grid-template-columns: 1fr; }
}
</style>
"""


def apply_theme() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
