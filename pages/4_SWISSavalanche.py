import streamlit as st

st.set_page_config(
    page_title="SWISSavalanche",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --bg: #f1f3f6;
    --surface: #ffffff;
    --border: #e4e7ec;
    --text: #1a2030;
    --text-dim: #5b6577;
    --text-faint: #97a0af;
    --accent: #7c9cc4;
}

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"] { background-color: var(--bg) !important; }
.block-container { padding: 0.6rem 3rem 2rem 3rem !important; max-width: 1000px !important; margin: 0 auto !important; }
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="collapsedControl"], section[data-testid="stSidebar"] { display: none !important; }
#MainMenu, footer { visibility: hidden; }
[data-testid="stPageLink"] { margin: 0 !important; }
[data-testid="stPageLink-NavLink"] {
    display: inline-flex; background: #111827; border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px; padding: 0.35rem 0.9rem; transition: background 0.2s; }
[data-testid="stPageLink-NavLink"]:hover { background: #1a2235; }
[data-testid="stPageLink-NavLink"] p, [data-testid="stPageLink-NavLink"] span {
    color: #e8edf5 !important; font-size: 0.8rem !important; font-weight: 600 !important; margin: 0 !important; }
</style>
""", unsafe_allow_html=True)

st.page_link("app.py", label="← Home")

st.markdown("""
<style>
.hero { padding: 1.6rem 0 1.4rem 0; }
.hero-eyebrow { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; letter-spacing: 0.18em;
                text-transform: uppercase; color: var(--accent); margin-bottom: 0.6rem; }
.hero-name { font-size: 2.6rem; font-weight: 700; color: var(--text); line-height: 1.05;
             letter-spacing: -0.02em; margin-bottom: 0.8rem; }
.hero-bio { font-size: 1rem; color: var(--text-dim); line-height: 1.7; max-width: 660px; margin-bottom: 1.2rem; }
.hero-bio b { color: var(--text); font-weight: 600; }
.hero-tags { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.4rem; }
.tag { background: var(--surface); border: 1px solid var(--border); border-radius: 30px;
       padding: 0.25rem 0.8rem; font-family: 'IBM Plex Mono', monospace;
       font-size: 0.65rem; color: var(--text-dim); letter-spacing: 0.04em; }
.btn-row { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.gh-btn { display: inline-block; background: var(--text); color: #fff !important; border-radius: 8px;
          padding: 0.5rem 1.1rem; font-size: 0.8rem; font-weight: 600;
          text-decoration: none; transition: background 0.2s; }
.gh-btn:hover { background: var(--accent); }
.gh-btn.ghost { background: var(--surface); color: var(--text) !important; border: 1px solid var(--border); }
.gh-btn.ghost:hover { border-color: var(--accent); color: var(--accent) !important; background: var(--surface); }

.section-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; letter-spacing: 0.15em;
                 text-transform: uppercase; color: var(--text-faint); margin: 2.2rem 0 1rem 0; }

.feat-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; }
.feat-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
             padding: 1.1rem 1.2rem; position: relative; overflow: hidden; }
.feat-card::before { content: ''; position: absolute; top: 0; left: 0;
                     width: 100%; height: 3px; background: var(--accent); }
.feat-title { font-size: 0.95rem; font-weight: 700; color: var(--text); margin-bottom: 0.4rem; }
.feat-desc { font-size: 0.8rem; color: var(--text-dim); line-height: 1.6; }

.steps { background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
         padding: 0.6rem 1.4rem; }
.steps ol { margin: 0.6rem 0; padding-left: 1.2rem; }
.steps li { font-size: 0.85rem; color: var(--text-dim); line-height: 1.9; }
.steps code { font-family: 'IBM Plex Mono', monospace; font-size: 0.78rem; background: var(--bg);
              border: 1px solid var(--border); border-radius: 5px; padding: 0.05rem 0.35rem; color: var(--text); }

.disclaimer { background: #fff4ed; border: 1px solid #f3c9b3; color: #a3491f; border-radius: 12px;
              padding: 0.9rem 1.1rem; font-size: 0.82rem; line-height: 1.6; }
.src-list { font-size: 0.85rem; color: var(--text-dim); line-height: 2; }
.src-list b { color: var(--text); font-weight: 600; }

.footer { margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--border);
          font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem;
          color: var(--text-faint); text-align: center; }
</style>

<div class="hero">
  <div class="hero-eyebrow">QGIS Processing plugin</div>
  <div class="hero-name">SWISSavalanche</div>
  <div class="hero-bio">
    A QGIS Processing plugin for mapping <b>seasonal avalanche susceptibility</b> in the Swiss Alps.
    It combines terrain morphology from the <b>swissALTI3D</b> digital terrain model with snow-load data
    from <b>Open-Meteo</b> archives, including optional elevation and wind-loading adjustments. Select a
    study area and obtain a classified susceptibility raster, a continuous-score raster and styled zone
    polygons — plus validation against documented SLF avalanche incidents.
  </div>
  <div class="hero-tags">
    <span class="tag">QGIS Processing</span>
    <span class="tag">swissALTI3D</span>
    <span class="tag">Open-Meteo</span>
    <span class="tag">Rasterio</span>
    <span class="tag">GeoPandas</span>
    <span class="tag">NumPy / GDAL</span>
    <span class="tag">MIT License</span>
  </div>
  <div class="btn-row">
    <a class="gh-btn" href="https://github.com/ntrojan/SWISSavalanche" target="_blank">View on GitHub →</a>
    <a class="gh-btn ghost" href="https://github.com/ntrojan/SWISSavalanche/archive/refs/heads/main.zip" target="_blank">Download ZIP</a>
  </div>
</div>

<div class="section-label">What it does</div>
<div class="feat-grid">
  <div class="feat-card">
    <div class="feat-title">Avalanche susceptibility analysis</div>
    <div class="feat-desc">Pick a study-area polygon or map extent and choose a snow-load approach.
    Output is a 4-class susceptibility raster, a continuous-score raster and styled zone polygons.
    Run it in climatology mode (averaging multiple winters) or for a single winter.</div>
  </div>
  <div class="feat-card">
    <div class="feat-title">Validation against incidents</div>
    <div class="feat-desc">Assess the accuracy of a susceptibility map against documented avalanche events.
    Provide your own incident data or use the official SLF dataset (records since 1970) clipped to the
    analysis area.</div>
  </div>
  <div class="feat-card">
    <div class="feat-title">Terrain morphology</div>
    <div class="feat-desc">Processes 2-metre swissALTI3D elevation data, deriving slope, aspect and
    curvature. Terrain tiles are fetched via the swisstopo STAC API and cached locally for efficiency.</div>
  </div>
  <div class="feat-card">
    <div class="feat-title">Snow-load modelling</div>
    <div class="feat-desc">Applies snow-load factors from Open-Meteo archives with optional elevation and
    wind-loading corrections, so susceptibility reflects how snow actually accumulates across the terrain.</div>
  </div>
</div>

<div class="section-label">Installation</div>
<div class="steps">
  <ol>
    <li>Download <code>swissavalanche.zip</code> (or compress the <code>swissavalanche/</code> folder from the repository).</li>
    <li>In QGIS, go to <code>Plugins → Manage and Install Plugins → Install from ZIP</code>.</li>
    <li>Enable <b>SwissAvalanche</b> — it is marked experimental, so tick <i>"Show also experimental plugins"</i> if needed.</li>
  </ol>
  <div style="font-size:0.8rem; color:var(--text-faint); padding:0 0 0.6rem 0;">
    Self-contained: the computational engine is bundled inside. Requires only standard QGIS packages
    (numpy, rasterio, geopandas, requests, GDAL) and an internet connection for initial data retrieval.
  </div>
</div>

<div class="section-label">Data sources</div>
<div class="src-list">
  • <b>swissALTI3D DTM</b> — via the swisstopo STAC API<br>
  • <b>Historical weather</b> — Open-Meteo archives<br>
  • <b>Avalanche-accident records</b> — WSL Institute for Snow and Avalanche Research (SLF)
</div>

<div class="section-label">Disclaimer</div>
<div class="disclaimer">
  This is a standalone tool, <b>not affiliated with or validated by SLF or swisstopo</b>. Susceptibility
  is not hazard: do not use it for operational safety decisions.
</div>

<div class="footer">Nicolò Trojan · QGIS plugin · MIT License</div>
""", unsafe_allow_html=True)
