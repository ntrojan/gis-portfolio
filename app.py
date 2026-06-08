import streamlit as st

st.set_page_config(
    page_title="Nicolò Trojan · GIS Portfolio",
    page_icon="🌍",
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
    --accent: #2f6fe0;
}

html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
.stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stMainBlockContainer"] { background-color: var(--bg) !important; }
.block-container { padding: 2rem 3rem !important; max-width: 1100px !important; margin: 0 auto !important; }
header[data-testid="stHeader"], [data-testid="collapsedControl"],
section[data-testid="stSidebar"] { display: none !important; }
#MainMenu, footer { visibility: hidden; }

.hero { padding: 3rem 0 2rem 0; }
.hero-eyebrow { font-family: 'IBM Plex Mono', monospace; font-size: 0.7rem; letter-spacing: 0.18em;
                text-transform: uppercase; color: var(--accent); margin-bottom: 0.6rem; }
.hero-name { font-size: 3rem; font-weight: 700; color: var(--text); line-height: 1.05;
             letter-spacing: -0.02em; margin-bottom: 0.8rem; }
.hero-bio { font-size: 1rem; color: var(--text-dim); line-height: 1.7; max-width: 620px; margin-bottom: 1.4rem; }
.hero-bio b { color: var(--text); font-weight: 600; }
.hero-tags { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.8rem; }
.tag { background: var(--surface); border: 1px solid var(--border); border-radius: 30px;
       padding: 0.25rem 0.8rem; font-family: 'IBM Plex Mono', monospace;
       font-size: 0.65rem; color: var(--text-dim); letter-spacing: 0.04em; }
.hero-link a { font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; color: var(--accent);
               text-decoration: none; border-bottom: 1px solid transparent; transition: border 0.2s; }
.hero-link a:hover { border-bottom-color: var(--accent); }

.section-label { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; letter-spacing: 0.15em;
                 text-transform: uppercase; color: var(--text-faint); margin-bottom: 1rem; margin-top: 2.5rem; }

.card-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.proj-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
             padding: 1.2rem 1.3rem; position: relative; overflow: hidden;
             transition: box-shadow 0.2s; cursor: default; }
.proj-card:hover { box-shadow: 0 8px 28px rgba(26,32,48,0.10); }
.proj-card::before { content: ''; position: absolute; top: 0; left: 0;
                     width: 100%; height: 3px; background: var(--card-color, var(--accent)); }
.proj-num { font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem;
            color: var(--text-faint); margin-bottom: 0.8rem; }
.proj-emoji { font-size: 1.8rem; margin-bottom: 0.6rem; line-height: 1; }
.proj-title { font-size: 1rem; font-weight: 700; color: var(--text); margin-bottom: 0.4rem; }
.proj-desc { font-size: 0.78rem; color: var(--text-dim); line-height: 1.6; margin-bottom: 0.7rem; }
.proj-note { display: inline-block; background: #fff4ed; border: 1px solid #f3c9b3;
             color: #c2562a; border-radius: 6px; padding: 0.2rem 0.55rem; margin-bottom: 1rem;
             font-family: 'IBM Plex Mono', monospace; font-size: 0.6rem; line-height: 1.4; }
.proj-tech { display: flex; gap: 0.35rem; flex-wrap: wrap; margin-bottom: 1.1rem; }
.tech-pill { background: var(--bg); border: 1px solid var(--border); border-radius: 20px;
             padding: 0.15rem 0.6rem; font-family: 'IBM Plex Mono', monospace;
             font-size: 0.6rem; color: var(--text-faint); }
.proj-btn { display: inline-block; background: var(--text); color: #fff; border-radius: 8px;
            padding: 0.4rem 1rem; font-size: 0.75rem; font-weight: 600;
            text-decoration: none; transition: background 0.2s; }
.proj-btn:hover { background: var(--accent); color: #fff; }

.footer { margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid var(--border);
          font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem;
          color: var(--text-faint); text-align: center; }
</style>

<div class="hero">
  <div class="hero-eyebrow">GIS Portfolio</div>
  <div class="hero-name">Nicolò Trojan</div>
  <div class="hero-bio">
    Geographer specialised in <b>GIS and spatial visualisation</b>. Here I publish dashboards,
    plugins and other items on a range of topics I care about: from the alpine environment
    to mobility, from wildlife to natural hazards.
  </div>
  <div class="hero-tags">
    <span class="tag">GIS</span>
    <span class="tag">Spatial Analysis</span>
    <span class="tag">Python</span>
    <span class="tag">QGIS Plugins</span>
    <span class="tag">Web Mapping</span>
    <span class="tag">Remote Sensing</span>
  </div>
  <div class="hero-link">
    <a href="https://www.linkedin.com/in/nicolò-trojan-a50238269/" target="_blank">→ LinkedIn</a>
  </div>
</div>

<div class="section-label">Selected projects</div>

<div class="card-grid">

  <div class="proj-card" style="--card-color:#4fc3f7">
    <div class="proj-num">01</div>
    <div class="proj-emoji">⛷️</div>
    <div class="proj-title">MagicMeteo</div>
    <div class="proj-desc">Interactive weather map for every Magic Pass resort in Switzerland.
    5-day forecasts with time animation, multilingual and responsive.</div>
    <div class="proj-tech">
      <span class="tech-pill">MapLibre GL</span>
      <span class="tech-pill">Open-Meteo API</span>
      <span class="tech-pill">Chart.js</span>
      <span class="tech-pill">JavaScript</span>
    </div>
    <a class="proj-btn" href="/MagicMeteo" target="_self">Open →</a>
  </div>

  <div class="proj-card" style="--card-color:#81c784">
    <div class="proj-num">02</div>
    <div class="proj-emoji">🐺</div>
    <div class="proj-title">Wolves in Switzerland</div>
    <div class="proj-desc">Spatial and temporal analysis of wolf observations in Switzerland
    between 1999 and 2022, based on KORA genetic tracking data.</div>
    <div class="proj-note">Not updated: data up to August 2022.</div>
    <div class="proj-tech">
      <span class="tech-pill">Leaflet</span>
      <span class="tech-pill">D3.js</span>
      <span class="tech-pill">Turf.js</span>
      <span class="tech-pill">JavaScript</span>
    </div>
    <a class="proj-btn" href="/Lupi" target="_self">Open →</a>
  </div>

  <div class="proj-card" style="--card-color:#e0552d">
    <div class="proj-num">03</div>
    <div class="proj-emoji">🏔️</div>
    <div class="proj-title">Sorte Landslide</div>
    <div class="proj-desc">Geospatial dashboard on the Sorte landslide (Mesolcina, GR) of 21 June 2024.
    Sentinel-2 change detection, slope morphology and exposure of elements at risk.</div>
    <div class="proj-tech">
      <span class="tech-pill">Streamlit</span>
      <span class="tech-pill">GeoPandas</span>
      <span class="tech-pill">Rasterio</span>
      <span class="tech-pill">Folium</span>
    </div>
    <a class="proj-btn" href="/Sorte" target="_self">Open →</a>
  </div>

</div>

<div class="footer">Nicolò Trojan · Built with Streamlit · 2025</div>
""", unsafe_allow_html=True)