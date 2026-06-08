"""
========================================================================
  SORTE LANDSLIDE · Mesolcina (GR), 21 June 2024
  Geospatial analysis dashboard
  ----------------------------------------------------------------------
  streamlit run app.py
========================================================================
"""

import os, json, math, io, base64
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
import geopandas as gpd
import rasterio
from rasterio.warp import transform_bounds
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
from branca.element import MacroElement
from jinja2 import Template
import warnings
warnings.filterwarnings("ignore")


class MetricScale(MacroElement):
    """Leaflet scale bar, metric only (km / m), no miles."""
    _template = Template("""{% macro script(this, kwargs) %}
        L.control.scale({maxWidth:130, metric:true, imperial:false, position:'bottomleft'})
          .addTo({{this._parent.get_name()}});
    {% endmacro %}""")


class LockView(MacroElement):
    """Hard-lock panning to the map's maxBounds (no rubber-band drift)."""
    _template = Template("""{% macro script(this, kwargs) %}
        {{this._parent.get_name()}}.options.maxBoundsViscosity = 1.0;
    {% endmacro %}""")


class FitAndLockZoom(MacroElement):
    """Fit the AOI, then forbid zooming out below that initial level."""
    def __init__(self, bounds):
        super().__init__()
        # cast to plain floats — numpy float64 would render as np.float64(...) in the JS
        (s, w), (n, e) = bounds
        self.bounds = [[float(s), float(w)], [float(n), float(e)]]
    _template = Template("""{% macro script(this, kwargs) %}
        var _m = {{this._parent.get_name()}};
        _m.fitBounds({{ this.bounds }});
        _m.setMinZoom(_m.getZoom());          // default view is the furthest you can zoom out
    {% endmacro %}""")

st.set_page_config(
    page_title="Sorte Landslide · Geospatial Analysis",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM · light, professional
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
    --bg:          #f1f3f6;
    --surface:     #ffffff;
    --surface-2:   #f6f8fb;
    --border:      #e4e7ec;
    --border-soft: #d4d9e2;
    --text:        #1a2030;
    --text-dim:    #5b6577;
    --text-faint:  #97a0af;
    --accent:      #e0552d;
    --accent-dim:  rgba(224,85,45,0.10);
    --btn:         #232a38;
    --btn-h:       #313a4c;
    --blue:        #2f6fe0;
    --green:       #2fa968;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--text); }
.stApp, [data-testid="stApp"], [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"], .main, body {
    background-color: var(--bg) !important;
}
.block-container { padding: 0.1rem 1.6rem 0.6rem 1.6rem !important; max-width: 1560px !important; }
[data-testid="stMainBlockContainer"], [data-testid="stMain"] { padding-top: 0.1rem !important; }
[data-testid="stVerticalBlock"] { gap: 0.55rem !important; }
/* hide all top chrome (tag-agnostic: stHeader is a div in recent Streamlit) */
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="collapsedControl"], section[data-testid="stSidebar"] { display: none !important; }
#MainMenu, footer { visibility: hidden; }
/* pull the Home link tight to the top */
[data-testid="stPageLink"] { margin-top: 0 !important; margin-bottom: 0 !important; }
/* keep the interactive map clear of the lead text above it */
iframe[title*="st_folium"] { margin-top: 0.9rem !important; }

/* ── Typography ─────────────────────────────────────────────── */
.eyebrow { font-family:'IBM Plex Mono',monospace; font-size:0.62rem; letter-spacing:0.16em;
           text-transform:uppercase; color:var(--accent); }
.display { font-family:'Space Grotesk',sans-serif; font-weight:600; line-height:1.05; letter-spacing:-0.01em; }
.lead { font-size:0.84rem; color:var(--text-dim); line-height:1.6; }
.lead b { color:var(--text); font-weight:500; }

/* ── Top bar ────────────────────────────────────────────────── */
.topbar-title { font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:1.05rem; color:var(--text); line-height:1; }
.topbar-sub { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:var(--text-faint);
              letter-spacing:0.08em; text-transform:uppercase; margin-top:3px; }

/* ── View title bar ─────────────────────────────────────────── */
.viewbar-eye { font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:var(--accent); letter-spacing:0.1em; }
.viewbar-title { font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:1.25rem; color:var(--text); margin:0.1rem 0 0.15rem 0; }
.viewbar-lead { font-size:0.78rem; color:var(--text-dim); line-height:1.5; max-width:820px; }
.viewbar-lead b { color:var(--text); font-weight:500; }

/* ── KPI tiles ──────────────────────────────────────────────── */
.kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:0.6rem; }
.kpi { background:var(--surface); border:1px solid var(--border); border-radius:12px;
       padding:0.7rem 0.85rem; position:relative; overflow:hidden; }
.kpi::before { content:''; position:absolute; top:0; left:0; width:3px; height:100%; background:var(--accent); }
.kpi-val { font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:1.4rem; color:var(--text); line-height:1; }
.kpi-unit { font-size:0.72rem; font-weight:500; color:var(--text-dim); margin-left:0.2rem; }
.kpi-lbl { font-size:0.7rem; color:var(--text); margin-top:0.35rem; font-weight:500; }
.kpi-sub { font-size:0.6rem; color:var(--text-faint); margin-top:0.1rem; font-family:'IBM Plex Mono',monospace; }

/* ── Cards ──────────────────────────────────────────────────── */
.card { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:0.9rem 1.05rem; }
.card-h { font-size:0.78rem; font-weight:600; color:var(--text); margin-bottom:0.3rem; }
.card-b { font-size:0.75rem; color:var(--text-dim); line-height:1.55; }
.card-b b { color:var(--text); }

.lblabel { font-size:0.66rem; color:var(--text-faint); margin-bottom:4px;
           font-family:'IBM Plex Mono',monospace; letter-spacing:0.05em; text-transform:uppercase; }
.cap { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:var(--text-faint);
       text-align:center; margin-top:5px; }
.pill-row { display:flex; gap:0.4rem; flex-wrap:wrap; margin:0.5rem 0; }
.pill { background:var(--surface-2); border:1px solid var(--border); border-radius:30px; padding:0.18rem 0.65rem;
        font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:var(--text-dim); }
.pill b { color:var(--text); }

.row-item { display:flex; align-items:center; justify-content:space-between; background:var(--surface-2);
            border-left:3px solid; border-radius:0 8px 8px 0; padding:0.45rem 0.8rem; margin-bottom:0.35rem; }
.row-name { font-size:0.76rem; font-weight:500; color:var(--text); }
.row-val { font-family:'IBM Plex Mono',monospace; font-size:0.66rem; color:var(--text-dim); }

/* ════ Segmented control (st.radio horizontal) ════ */
div[role="radiogroup"] { gap:6px !important; }
div[role="radiogroup"] > label { background:var(--surface); border:1px solid var(--border); border-radius:9px;
    padding:0.42rem 1rem; margin:0 !important; cursor:pointer; transition:all 0.15s ease; }
div[role="radiogroup"] > label:hover { border-color:var(--border-soft); background:var(--surface-2); }
div[role="radiogroup"] > label > div:first-child { display:none !important; }
div[role="radiogroup"] > label p { font-size:0.76rem !important; color:var(--text-dim) !important; font-weight:500 !important; }
div[role="radiogroup"] > label:has(input:checked) { background:var(--accent); border-color:var(--accent); }
div[role="radiogroup"] > label:has(input:checked) p { color:#fff !important; }

/* ── Popover (info "i" buttons) ─────────────────────────────── */
[data-testid="stPopover"] button {
    background:var(--surface) !important; border:1px solid var(--border) !important;
    color:var(--text-dim) !important; border-radius:8px !important; font-size:0.72rem !important;
    font-weight:500 !important; padding:0.28rem 0.7rem !important; min-height:0 !important; }
[data-testid="stPopover"] button:hover { border-color:var(--accent) !important; color:var(--accent) !important; }

/* ── Sliders ────────────────────────────────────────────────── */
[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] { background:var(--accent) !important; }

/* ── Tabs ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] { gap:4px; border-bottom:1px solid var(--border); }
.stTabs [data-baseweb="tab"] { font-size:0.72rem; color:var(--text-dim); font-weight:500; padding:0.35rem 0.85rem; border-radius:8px 8px 0 0; }
.stTabs [aria-selected="true"] { color:var(--accent) !important; background:var(--accent-dim) !important; }
.stTabs [data-baseweb="tab-highlight"] { background:var(--accent) !important; }

/* ── Metric ─────────────────────────────────────────────────── */
[data-testid="stMetric"] { background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:0.5rem 0.8rem; }
[data-testid="stMetricLabel"] p { font-size:0.64rem !important; color:var(--text-dim) !important; }
[data-testid="stMetricValue"] { font-family:'Space Grotesk',sans-serif !important; font-size:1.15rem !important;
    font-weight:600 !important; color:var(--text) !important; }
[data-testid="stMetricDelta"] { font-size:0.58rem !important; color:var(--text-faint) !important; }

/* ── Buttons ────────────────────────────────────────────────── */
.stButton button { background:var(--btn); color:#fff; border:none; border-radius:10px;
    font-weight:600; font-size:0.84rem; padding:0.55rem 1.4rem; }
.stButton button:hover { background:var(--btn-h); color:#fff; }

[data-baseweb="checkbox"] div[aria-checked="true"] { background:var(--accent) !important; }
hr { border-color:var(--border) !important; margin:0.7rem 0 !important; }
[data-testid="stDataFrame"] { border:1px solid var(--border); border-radius:10px; }
[data-testid="stExpander"] { border:1px solid var(--border) !important; border-radius:12px !important; background:var(--surface) !important; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
#  PATHS
# ════════════════════════════════════════════════════════════════════
BASE = os.path.dirname(os.path.abspath(__file__))
PATHS = {
    "aoi":        os.path.join(BASE, "data/processed/watershed/aoi_lostallo_union.gpkg"),
    "frana":      os.path.join(BASE, "data/processed/vectors/landslide_perimeter.gpkg"),
    "buildings":  os.path.join(BASE, "data/processed/vectors/exposure_buildings.gpkg"),
    "roads":      os.path.join(BASE, "data/processed/vectors/exposure_roads.gpkg"),
    "stats":      os.path.join(BASE, "data/processed/exposure_stats.json"),
    "slope":      os.path.join(BASE, "data/processed/rasters/slope.tif"),
    "twi":        os.path.join(BASE, "data/processed/rasters/twi.tif"),
    "susc_class": os.path.join(BASE, "data/processed/rasters/susceptibility_class.tif"),
    "s2_pre":     os.path.join(BASE, "data/raw/sentinel/sorte_S2_PRE_optical.tif"),
    "s2_post":    os.path.join(BASE, "data/raw/sentinel/sorte_S2_POST_optical.tif"),
    "ndvi_pre":   os.path.join(BASE, "data/raw/sentinel/sorte_NDVI_PRE.tif"),
    "ndvi_post":  os.path.join(BASE, "data/raw/sentinel/sorte_NDVI_POST.tif"),
    "ndvi_diff":  os.path.join(BASE, "data/raw/sentinel/sorte_NDVI_diff.tif"),
    "mask_clean": os.path.join(BASE, "data/processed/rasters/landslide_mask_clean.tif"),
}
AOI_CENTER = [46.3058, 9.1860]
AOI_BOUNDS = [[46.27209, 9.14490], [46.33946, 9.22697]]

# ════════════════════════════════════════════════════════════════════
#  DATA LOADERS (cached)
# ════════════════════════════════════════════════════════════════════
@st.cache_data
def load_vector(path):
    if not os.path.exists(path): return None
    return gpd.read_file(path).to_crs("EPSG:4326")

@st.cache_data
def load_stats():
    if not os.path.exists(PATHS["stats"]): return {}
    with open(PATHS["stats"]) as f: return json.load(f)

@st.cache_data
def load_arr(path):
    if not os.path.exists(path): return None, None
    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float32); nd, res, crs = src.nodata, src.res, src.crs
    if nd is not None: arr[arr == nd] = np.nan
    pxa = (abs(res[0])*111320*math.cos(math.radians(46.3))*abs(res[1])*111320
           if crs.is_geographic else abs(res[0])*abs(res[1]))
    return arr, pxa

@st.cache_data
def raster_stats(path):
    arr, _ = load_arr(path)
    if arr is None: return {}
    f = arr[np.isfinite(arr)].flatten()
    return {"min":float(np.min(f)),"max":float(np.max(f)),"mean":float(np.mean(f)),
            "median":float(np.median(f)),"p5":float(np.percentile(f,5)),"p95":float(np.percentile(f,95))}

@st.cache_data
def susc_dist(path):
    arr, pxa = load_arr(path)
    if arr is None: return {}, {}
    f = arr[np.isfinite(arr)].astype(int); n = len(f)
    lbl = {1:"Low",2:"Moderate",3:"High",4:"Very high"}
    return ({lbl[k]: round(np.sum(f==k)/n*100,1) for k in [1,2,3,4]},
            {lbl[k]: round(np.sum(f==k)*pxa/1e6,2) for k in [1,2,3,4]})

@st.cache_data
def raster_overlay(path, cmap_name, vmin, vmax, alpha=160):
    import matplotlib.pyplot as plt; from PIL import Image
    if not os.path.exists(path): return None, None
    with rasterio.open(path) as src:
        arr = src.read(1).astype(np.float32); nd = src.nodata
        bounds = transform_bounds(src.crs,"EPSG:4326",*src.bounds)
    if nd is not None: arr[arr==nd] = np.nan
    nm = np.isnan(arr); n = np.where(nm,0.,np.clip((arr-vmin)/max(vmax-vmin,1e-9),0,1))
    rgba = (plt.get_cmap(cmap_name)(n)*255).astype(np.uint8); rgba[nm,3]=0; rgba[~nm,3]=alpha
    img = Image.fromarray(rgba,"RGBA")
    if max(img.size)>900: r=900/max(img.size); img=img.resize((int(img.width*r),int(img.height*r)),Image.LANCZOS)
    buf=io.BytesIO(); img.save(buf,"PNG")
    return "data:image/png;base64,"+base64.b64encode(buf.getvalue()).decode(), bounds

@st.cache_data
def render_single(path, cmap_name, vmin, vmax, maxpx=720):
    import matplotlib.pyplot as plt; from PIL import Image
    arr, _ = load_arr(path)
    if arr is None: return None
    nm = np.isnan(arr); n = np.where(nm,0.,np.clip((arr-vmin)/max(vmax-vmin,1e-9),0,1))
    rgba = (plt.get_cmap(cmap_name)(n)*255).astype(np.uint8); rgba[nm,3]=0
    img = Image.fromarray(rgba,"RGBA")
    if max(img.size)>maxpx: r=maxpx/max(img.size); img=img.resize((int(img.width*r),int(img.height*r)),Image.LANCZOS)
    return img

@st.cache_data
def render_rgb(path, maxpx=900):
    from PIL import Image
    if not os.path.exists(path): return None
    with rasterio.open(path) as src:
        cnt=src.count; r=src.read(1).astype(np.float32)
        g=src.read(2).astype(np.float32) if cnt>=3 else r
        b=src.read(3).astype(np.float32) if cnt>=3 else r
    def norm(x): p2,p98=np.nanpercentile(x,2),np.nanpercentile(x,98); return np.clip((x-p2)/max(p98-p2,1e-9),0,1)
    img=Image.fromarray((np.stack([norm(r),norm(g),norm(b)],-1)*255).astype(np.uint8),"RGB")
    if max(img.size)>maxpx: r2=maxpx/max(img.size); img=img.resize((int(img.width*r2),int(img.height*r2)),Image.LANCZOS)
    return img

@st.cache_data
def ndvi_highlight(threshold):
    import matplotlib.pyplot as plt; from PIL import Image
    arr, pxa = load_arr(PATHS["ndvi_diff"])
    if arr is None: return None, 0.
    area = float(np.nansum(arr>threshold)*pxa/1e6)
    nm = np.isnan(arr); n = np.where(nm,0.,np.clip((arr-(-0.5))/1.0,0,1))
    rgba=(plt.get_cmap("RdBu")(n)*255).astype(np.uint8); rgba[nm,3]=0; rgba[~nm,3]=185
    rgba[(~nm)&(arr>threshold)]=[224,85,45,255]
    img=Image.fromarray(rgba,"RGBA")
    if max(img.size)>720: r=720/max(img.size); img=img.resize((int(img.width*r),int(img.height*r)),Image.LANCZOS)
    return img, area

@st.cache_data
def story_map_html(height_px=520):
    """Before/after swipe slider with Sentinel-2 PRE/POST ortho."""
    from PIL import Image
    a = render_rgb(PATHS["s2_pre"], 1100); b = render_rgb(PATHS["s2_post"], 1100)
    if a is None or b is None: return None
    w, h = min(a.width,b.width), min(a.height,b.height)
    a = a.resize((w,h),Image.LANCZOS); b = b.resize((w,h),Image.LANCZOS)
    def tb(img): buf=io.BytesIO(); img.save(buf,"PNG"); return base64.b64encode(buf.getvalue()).decode()
    ba, bb = tb(a), tb(b)
    return ("""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;display:flex;justify-content:center;align-items:flex-start}
.comp{position:relative;height:__H__px;aspect-ratio:__AR__;max-width:100%;overflow:hidden;
      border-radius:14px;border:1px solid #dde3ec;user-select:none;box-shadow:0 4px 20px rgba(27,36,48,.10)}
.comp img.base{display:block;height:100%;width:auto}
.after{position:absolute;inset:0;clip-path:inset(0 50% 0 0);pointer-events:none}
.after img{position:absolute;inset:0;height:100%;width:100%;object-fit:cover}
.hd{position:absolute;top:0;left:calc(50% - 1px);width:2px;height:100%;background:#fff;
    box-shadow:0 0 8px rgba(0,0,0,.45)}
.hd-b{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:46px;height:46px;background:#fff;
      border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:16px;color:#1b2430;
      box-shadow:0 3px 12px rgba(0,0,0,.35);cursor:ew-resize;font-weight:600;letter-spacing:-2px}
.tag{position:absolute;top:13px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:#fff;
     background:rgba(27,36,48,.78);padding:5px 11px;border-radius:7px;letter-spacing:.05em;pointer-events:none;backdrop-filter:blur(6px)}
.tag-l{left:13px}.tag-r{right:13px}
.hint{position:absolute;bottom:13px;left:50%;transform:translateX(-50%);font-family:'IBM Plex Mono',monospace;
      font-size:10px;color:#1b2430;background:rgba(255,255,255,.88);padding:4px 12px;border-radius:20px;
      pointer-events:none;transition:opacity .3s}
</style></head><body>
<div class="comp" id="c">
  <img class="base" src="data:image/png;base64,__POST__"/>
  <div class="after" id="a"><img src="data:image/png;base64,__PRE__"/></div>
  <div class="hd" id="h"><div class="hd-b" id="k">‹›</div></div>
  <span class="tag tag-l">BEFORE · summer 2023</span>
  <span class="tag tag-r">AFTER · July 2024</span>
  <span class="hint" id="hint">grab the handle and drag</span>
</div>
<script>
const c=document.getElementById('c'),a=document.getElementById('a'),h=document.getElementById('h'),k=document.getElementById('k'),hint=document.getElementById('hint');
let drag=false;
function u(x){const r=c.getBoundingClientRect(),p=Math.min(Math.max((x-r.left)/r.width*100,0),100);
  a.style.clipPath='inset(0 '+(100-p)+'% 0 0)';h.style.left='calc('+p+'% - 1px)';}
function start(e){drag=true;if(hint)hint.style.opacity=0;e.preventDefault&&e.preventDefault();}
k.addEventListener('mousedown',start);
window.addEventListener('mouseup',()=>drag=false);
window.addEventListener('mousemove',e=>{if(drag)u(e.clientX)});
k.addEventListener('touchstart',start,{passive:false});
window.addEventListener('touchend',()=>drag=false);
window.addEventListener('touchmove',e=>{if(drag)u(e.touches[0].clientX)},{passive:false});
</script></body></html>"""
        .replace("__H__", str(height_px))
        .replace("__AR__", f"{w}/{h}")
        .replace("__PRE__", ba).replace("__POST__", bb))

# ════════════════════════════════════════════════════════════════════
#  LOAD
# ════════════════════════════════════════════════════════════════════
stats       = load_stats()
buf_results = stats.get("buffer_results", {})
area_frana  = stats.get("area_frana_km2", 3.20)
n_poly      = stats.get("n_poligoni_frana", 124)
gdf_aoi     = load_vector(PATHS["aoi"])
gdf_frana   = load_vector(PATHS["frana"])
gdf_build   = load_vector(PATHS["buildings"])
gdf_roads   = load_vector(PATHS["roads"])

PLT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
           font=dict(family="Inter, sans-serif", size=11, color="#5a6678"),
           margin=dict(l=44,r=12,t=10,b=38),
           xaxis=dict(gridcolor="#e6eaf1", zerolinecolor="#dde3ec"),
           yaxis=dict(gridcolor="#e6eaf1", zerolinecolor="#dde3ec"))

LAYER_LEGEND = {
    "Susceptibility": ("Landslide susceptibility",
        "Relative likelihood of failure from the composite morphological model.",
        '<div style="display:flex;gap:0;margin:6px 0 3px">'
        '<div style="flex:1;height:9px;background:#1a9850"></div><div style="flex:1;height:9px;background:#a6d96a"></div>'
        '<div style="flex:1;height:9px;background:#fdae61"></div><div style="flex:1;height:9px;background:#d73027"></div></div>'
        '<div style="display:flex;justify-content:space-between;font-size:9px;color:#5a6678"><span>Low</span><span>Very high</span></div>'),
    "Slope": ("Slope angle",
        "Terrain steepness. Above ~30° the risk of shallow sliding rises sharply.",
        '<div style="height:9px;border-radius:2px;margin:6px 0 3px;background:linear-gradient(90deg,#ffffb2,#fed976,#feb24c,#fd8d3c,#f03b20,#bd0026)"></div>'
        '<div style="display:flex;justify-content:space-between;font-size:9px;color:#5a6678"><span>0°</span><span>30°</span><span>60°+</span></div>'),
    "TWI": ("Topographic wetness (TWI)",
        "Tendency to accumulate water. High values = saturated, less stable ground.",
        '<div style="height:9px;border-radius:2px;margin:6px 0 3px;background:linear-gradient(90deg,#f7fbff,#c6dbef,#9ecae1,#6baed6,#3182bd,#08519c)"></div>'
        '<div style="display:flex;justify-content:space-between;font-size:9px;color:#5a6678"><span>dry</span><span>saturated</span></div>'),
}

def viewbar(eyebrow, title, lead):
    st.markdown(f"""<div style="margin-bottom:0.6rem">
        <div class="viewbar-eye">{eyebrow}</div>
        <div class="viewbar-title">{title}</div>
        <div class="viewbar-lead">{lead}</div></div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
#  EXTRA STYLES  (key-figures strip + historical event box)
# ════════════════════════════════════════════════════════════════════
st.markdown("""<style>
.figbar { display:flex; gap:0; background:var(--surface); border:1px solid var(--border);
          border-radius:12px; overflow:hidden; }
.fig { flex:1; padding:0.5rem 0.95rem; border-right:1px solid var(--border); }
.fig:last-child { border-right:none; }
.fig-v { font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:1.2rem; color:var(--text); line-height:1; }
.fig-u { font-size:0.62rem; color:var(--text-dim); margin-left:2px; font-weight:500; }
.fig-l { display:block; font-size:0.57rem; color:var(--text-faint); font-family:'IBM Plex Mono',monospace;
         margin-top:3px; text-transform:uppercase; letter-spacing:0.04em; }
.event-box { background:var(--surface); border:1px solid var(--border); border-left:3px solid var(--accent);
             border-radius:12px; padding:0.9rem 1.05rem; }
.event-h { font-family:'Space Grotesk',sans-serif; font-weight:600; font-size:0.95rem; color:var(--text); margin-bottom:0.45rem; }
.event-b { font-size:0.78rem; color:var(--text-dim); line-height:1.6; }
.event-b b { color:var(--text); }
.event-src { font-family:'IBM Plex Mono',monospace; font-size:0.58rem; color:var(--text-faint); margin-top:0.7rem; line-height:1.5; }
.note { font-size:0.74rem; color:var(--text-dim); line-height:1.55; margin:0.35rem 0 0.2rem 0; }
.note b { color:var(--text); }

/* ── Home button (top-left page link) ───────────────────────── */
[data-testid="stPageLink-NavLink"] {
    display:inline-flex; background:var(--surface); border:1px solid var(--border);
    border-radius:10px; padding:0.3rem 0.85rem; transition:all 0.15s ease; }
[data-testid="stPageLink-NavLink"]:hover { border-color:var(--accent); background:var(--surface-2); }
[data-testid="stPageLink-NavLink"] p, [data-testid="stPageLink-NavLink"] span {
    color:var(--text-dim) !important; font-size:0.78rem !important; font-weight:500 !important; margin:0 !important; }
[data-testid="stPageLink-NavLink"]:hover p, [data-testid="stPageLink-NavLink"]:hover span { color:var(--accent) !important; }
</style>""", unsafe_allow_html=True)

st.page_link("app.py", label="← Home")

# ════════════════════════════════════════════════════════════════════
#  WELCOME SCREEN
# ════════════════════════════════════════════════════════════════════
if "entered" not in st.session_state:
    st.session_state.entered = False

if not st.session_state.entered:
    _, wc, _ = st.columns([1, 3.2, 1])
    with wc:
        st.markdown("""
        <div style="text-align:center;padding:2.2rem 0 0.4rem 0">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;letter-spacing:0.16em;
                      text-transform:uppercase;color:#e0552d">Geospatial analysis · Mesolcina (GR) · Switzerland</div>
          <div style="font-family:'Space Grotesk',sans-serif;font-weight:600;font-size:3rem;color:#1b2430;margin:0.7rem 0 0.3rem 0">
              Sorte Landslide</div>
          <div style="font-family:'IBM Plex Mono',monospace;color:#8a94a6;font-size:0.78rem">21 June 2024</div>
        </div>
        <div style="text-align:center;max-width:560px;margin:1.1rem auto 1.7rem auto;
                    font-size:0.86rem;color:#5a6678;line-height:1.65">
          An end-to-end study of the landslide event: from <b style="color:#1b2430">satellite delineation</b>
          of the failure body, to the <b style="color:#1b2430">morphological context</b> of the slope,
          to the <b style="color:#1b2430">exposure assessment</b> of buildings and infrastructure.
          This dashboard is interactive: switch views to explore.
        </div>
        """, unsafe_allow_html=True)

        cards = [
            ("01","Before / After","Swipe between Sentinel-2 imagery acquired before and after the event to see the failure scar appear."),
            ("02","Interactive map","The landslide outline on Swiss orthophoto. Toggle analysis layers, adjust opacity, click buildings for details."),
            ("03","Statistics","Change detection, slope & wetness morphology, and exposure of buildings and roads."),
            ("04","Methodology","Full processing pipeline, data sources, parameters and limitations of the analysis."),
        ]
        cc = st.columns(4)
        for col, (num, t, d) in zip(cc, cards):
            with col:
                st.markdown(f"""<div class="card" style="height:100%">
                    <div style="font-family:'IBM Plex Mono',monospace;font-size:0.7rem;color:#e0552d;margin-bottom:0.5rem">{num}</div>
                    <div class="card-h">{t}</div><div class="card-b">{d}</div></div>""", unsafe_allow_html=True)

        st.markdown("""<div style="font-family:'IBM Plex Mono',monospace;font-size:0.64rem;color:#8a94a6;
            text-align:center;margin:1.3rem 0 0.9rem 0;line-height:1.9">
            SOURCES&nbsp;·&nbsp; swissALTI3D 2m DTM (swisstopo) &nbsp;·&nbsp; Sentinel-2 L2A (Google Earth Engine)
            &nbsp;·&nbsp; BAFU watersheds &nbsp;·&nbsp; OpenStreetMap &nbsp;·&nbsp; EPSG:2056</div>""", unsafe_allow_html=True)

        b1, b2, b3 = st.columns([1, 1.4, 1])
        with b2:
            if st.button("Open dashboard  →", use_container_width=True):
                st.session_state.entered = True
                st.rerun()
    st.stop()

# ════════════════════════════════════════════════════════════════════
#  TOP BAR  +  ALWAYS-VISIBLE KEY FIGURES
# ════════════════════════════════════════════════════════════════════
tb_l, tb_c = st.columns([1.3, 4])
with tb_l:
    st.markdown("""<div style="padding-top:2px">
        <div class="topbar-title">Sorte Landslide</div>
        <div class="topbar-sub">Mesolcina (GR) · 21 Jun 2024</div></div>""", unsafe_allow_html=True)
with tb_c:
    view = st.radio("view", ["Before / After", "Map", "Statistics", "Methodology"],
                    horizontal=True, label_visibility="collapsed")

st.markdown('<hr style="margin:0.45rem 0 0.7rem 0"/>', unsafe_allow_html=True)

def kpi_strip():
    """Headline figures: shown only on Before/After and Statistics."""
    ed  = buf_results.get("diretto", {}).get("edifici_colpiti", "n/a")
    km  = buf_results.get("diretto", {}).get("strade_km", "n/a")
    ed5 = buf_results.get("500m", {}).get("edifici_colpiti", "n/a")
    st.markdown(f"""
    <div class="figbar" style="margin:0 0 0.7rem 0">
      <div class="fig"><span class="fig-v">{area_frana:.2f}<span class="fig-u">km²</span></span><span class="fig-l">Landslide area</span></div>
      <div class="fig"><span class="fig-v">{n_poly}</span><span class="fig-l">Mapped polygons</span></div>
      <div class="fig"><span class="fig-v">{ed}</span><span class="fig-l">Buildings in footprint</span></div>
      <div class="fig"><span class="fig-v">{km}<span class="fig-u">km</span></span><span class="fig-l">Roads in footprint</span></div>
      <div class="fig"><span class="fig-v">{ed5}</span><span class="fig-l">Buildings within 500 m</span></div>
      <div class="fig"><span class="fig-v">31.82<span class="fig-u">km²</span></span><span class="fig-l">Watershed AOI</span></div>
    </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
#  VIEW 1 · BEFORE / AFTER  (default)
# ════════════════════════════════════════════════════════════════════
if view == "Before / After":
    kpi_strip()
    st.markdown('<div class="viewbar-eye">01 · SATELLITE EVIDENCE</div>'
                '<div class="viewbar-title" style="margin:0.1rem 0 0.6rem 0">Before and after the landslide</div>',
                unsafe_allow_html=True)

    cl, cr = st.columns([1, 1], gap="large")
    with cl:
        html_story = story_map_html(height_px=576)
        if html_story:
            components.html(html_story, height=596, scrolling=False)
        else:
            st.info("Sentinel-2 imagery not found in data/raw/sentinel/.")
    with cr:
        st.markdown("""
        <div class="card" style="margin-bottom:0.7rem">
          <div class="event-h">How to read it</div>
          <div class="event-b">
            Grab the handle and drag it across the image to wipe between the Sentinel-2 view
            <b>before</b> (summer 2023) and <b>after</b> (July 2024) the event: both true-colour,
            10 m/pixel. Where the slope failed, vegetation gave way to bare soil and debris: the
            pale scar in the <i>after</i> image. This visual contrast is what the automatic NDVI
            delineation (see <b>Statistics</b>) converts into a measured footprint of <b>%s km²</b>.
          </div>
        </div>
        <div class="event-box">
          <div class="event-h">The event · 21 June 2024</div>
          <div class="event-b">
            On the night of 21 June 2024, after <b>extremely intense rainfall</b>, a <b>debris flow</b>
            rushed down a steep gully above the hamlet of <b>Sorte</b>, in the municipality of
            <b>Lostallo</b> (Val Mesolcina / Misox, canton Graubünden). The settlement sits on the
            alluvial fan at the mouth of that gully (the natural deposition zone of past flows), so the
            mass of water, mud and rock struck the houses directly, <b>destroying three of them</b>.
            <b>Three people lost their lives</b> and one was rescued.<br><br>
            Debris and the swollen <b>Moesa</b> river tore away roughly 200 m of the <b>A13 motorway</b>.
            As the A13 is a primary trans-Alpine corridor between northern and southern Switzerland,
            its closure disrupted freight and regional traffic far beyond the valley for an extended
            period. Around twenty residents were evacuated, and a response of some <b>200 personnel</b>
            with excavators, search dogs, drones and army helicopters worked the site in the following days.<br><br>
            The Sorte failure was one of several debris flows and floods that hit the southern Alps that
            same weekend, on ground already saturated by repeated intense convective storms: a reminder
            of how quickly steep alpine catchments can mobilise after extreme rainfall.
          </div>
          <div class="event-src">Sources · AGU Landslide Blog (D. Petley) · RSI · laRegione · Euronews&nbsp;&nbsp;|&nbsp;&nbsp;~46.293° N, 9.180° E</div>
        </div>
        """ % f"{area_frana:.2f}", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
#  VIEW 2 · INTERACTIVE MAP
# ════════════════════════════════════════════════════════════════════
elif view == "Map":
    mh_l, mh_r = st.columns([4, 1.15])
    with mh_l:
        st.markdown('<div class="viewbar-eye">02 · TERRITORIAL VIEW</div>'
            '<div class="viewbar-title" style="margin:0.1rem 0 0.15rem 0">Failure location, terrain & exposure</div>'
            '<div class="viewbar-lead" style="max-width:780px;color:#2a3142">The <b style="color:#e0552d">orange polygon</b> is the '
            'mapped failure body. Pick an analysis layer to reveal the terrain predisposition behind it and the '
            'exposed buildings around it. Click a building for its attributes. Controls are in the menu on the right.</div>',
            unsafe_allow_html=True)
    with mh_r:
        st.markdown('<div class="lblabel">Map controls</div>', unsafe_allow_html=True)
        with st.popover("Layers & options", use_container_width=True):
            layer_choice = st.radio("Analysis layer", ["None", "Susceptibility", "Slope", "TWI"],
                help="None = clean view · Susceptibility = modelled failure likelihood (4 classes) · "
                     "Slope = steepness (0-60°+) · TWI = where water concentrates.")
            opacity = st.slider("Layer opacity", 0, 100, 70, 5)
            basemap = st.radio("Basemap", ["Dark map", "Swiss orthophoto", "Light map"])
            st.markdown("<hr/>", unsafe_allow_html=True)
            show_frana = st.toggle("Landslide outline", True)
            show_build = st.toggle("Exposed buildings", True)
            show_roads = st.toggle("Roads", False)
            raggio = st.select_slider("Exposure buffer", ["none","100 m","250 m","500 m"], "none",
                                      help="Distance ring around the landslide showing its zone of influence.")

    # ── Build map ── (locked to the AOI: no panning away, no zooming too far out)
    if gdf_aoi is not None:
        minx, miny, maxx, maxy = gdf_aoi.total_bounds
    else:
        (miny, minx), (maxy, maxx) = AOI_BOUNDS[0], AOI_BOUNDS[1]
    PAD = 0.004  # ~400 m breathing room around the AOI
    m = folium.Map(location=AOI_CENTER, tiles=None, control_scale=False,
                   max_zoom=19, max_bounds=True,
                   min_lat=miny - PAD, max_lat=maxy + PAD,
                   min_lon=minx - PAD, max_lon=maxx + PAD)
    m.add_child(MetricScale())
    m.add_child(LockView())
    if basemap == "Swiss orthophoto":
        folium.TileLayer("https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage/default/current/3857/{z}/{x}/{y}.jpeg",
                         attr="© swisstopo", name="Orthophoto", max_zoom=19).add_to(m)
    elif basemap == "Dark map":
        folium.TileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                         attr="© CARTO", name="Dark map", max_zoom=19).add_to(m)
    else:
        folium.TileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                         attr="© CARTO", name="Light map", max_zoom=19).add_to(m)
    # Initial framing + zoom-out lock are applied at the end (after all layers).

    layer_cfg = {"Susceptibility":(PATHS["susc_class"],"RdYlGn_r",1,4),
                 "Slope":(PATHS["slope"],"YlOrRd",0,60),
                 "TWI":(PATHS["twi"],"Blues",0,12)}
    if layer_choice != "None":
        rpath, cmap, vmin, vmax = layer_cfg[layer_choice]
        img_data, bounds = raster_overlay(rpath, cmap, vmin, vmax, alpha=int(opacity/100*255))
        if img_data:
            folium.raster_layers.ImageOverlay(image=img_data,
                bounds=[[bounds[1],bounds[0]],[bounds[3],bounds[2]]], opacity=1.0, z_index=10).add_to(m)

    if gdf_aoi is not None:
        folium.GeoJson(gdf_aoi.__geo_interface__,
            style_function=lambda _: {"fillColor":"transparent","color":"#d99a1f","weight":1.6,"dashArray":"6 5"}).add_to(m)
    if show_roads and gdf_roads is not None:
        folium.GeoJson(gdf_roads.__geo_interface__,
            style_function=lambda _: {"color":"#d99a1f","weight":1.5,"opacity":0.75}).add_to(m)

    bm = {"none":0,"100 m":100,"250 m":250,"500 m":500}[raggio]
    if bm > 0 and gdf_frana is not None:
        gdf_buf = gpd.GeoDataFrame(geometry=gdf_frana.to_crs("EPSG:2056").buffer(bm).to_crs("EPSG:4326"), crs="EPSG:4326")
        folium.GeoJson(gdf_buf.__geo_interface__,
            style_function=lambda _: {"fillColor":"#d99a1f","fillOpacity":0.10,"color":"#d99a1f","weight":1.2,"dashArray":"4 4"}).add_to(m)

    exp_colors = {"diretta":"#e0552d","100m":"#f0962a","250m":"#e6c419","500m":"#5bb56a","oltre_500m":"#9aa6b8"}
    exp_names  = {"diretta":"In footprint","100m":"≤ 100 m","250m":"≤ 250 m","500m":"≤ 500 m","oltre_500m":"> 500 m"}
    cat_en     = {"Altro":"Other","Residenziale":"Residential","Accessorio":"Accessory",
                  "Commerciale":"Commercial","Pubblico":"Public"}
    _empty = {"nan","none","<na>",""}
    def _has(v): return v is not None and str(v).strip().lower() not in _empty

    if show_build and gdf_build is not None:
        b = gdf_build.copy()
        b["_exp"] = b["esposizione"].astype(str) if "esposizione" in b.columns else "oltre_500m"
        b["_cat"] = b["categoria"].map(lambda v: cat_en.get(str(v), str(v))) if "categoria" in b.columns else "Building"

        def info_lines(row):                                   # only populated attributes
            out = []
            if "categoria" in row and _has(row["categoria"]):
                out.append(("Category", cat_en.get(str(row["categoria"]), str(row["categoria"]))))
            if "building" in row and _has(row["building"]) and str(row["building"]).lower() != "yes":
                out.append(("Type", str(row["building"])))
            if "name" in row and _has(row["name"]):
                out.append(("Name", str(row["name"])))
            if "amenity" in row and _has(row["amenity"]):
                out.append(("Function", str(row["amenity"])))
            if "levels" in row and _has(row["levels"]):
                try: lv = str(int(float(row["levels"])))
                except Exception: lv = str(row["levels"])
                out.append(("Floors", lv))
            out.append(("Exposure", exp_names.get(str(row["_exp"]), str(row["_exp"]))))
            return "\n".join(f"{k}: {v}" for k, v in out)

        b["info"] = b.apply(info_lines, axis=1)
        disp = b[["info", "_cat", "_exp", "geometry"]]

        def build_style(f):
            c = exp_colors.get(f["properties"].get("_exp", "oltre_500m"), "#9aa6b8")
            return {"fillColor": c, "color": c, "weight": 0.4, "fillOpacity": 0.88}

        pop_style = ("font-family:'IBM Plex Mono',monospace;font-size:11px;background:#fff;"
                     "color:#1a2030;border:1px solid #e4e7ec;border-radius:8px;padding:6px 8px;"
                     "white-space:pre-line;line-height:1.55")
        folium.GeoJson(disp.__geo_interface__, name="Buildings", style_function=build_style,
            highlight_function=lambda _: {"weight": 1.6, "color": "#1a2030", "fillOpacity": 0.95},
            tooltip=folium.GeoJsonTooltip(fields=["_cat"], labels=False, sticky=True, style=pop_style),
            popup=folium.GeoJsonPopup(fields=["info"], labels=False, max_width=240, style=pop_style)).add_to(m)

    if show_frana and gdf_frana is not None:
        folium.GeoJson(gdf_frana.__geo_interface__,
            style_function=lambda _: {"fillColor":"#e0552d","fillOpacity":0.16,"color":"#e0552d","weight":3}).add_to(m)
        try:
            cen = gdf_frana.to_crs("EPSG:2056").unary_union.centroid
            cll = gpd.GeoSeries([cen], crs="EPSG:2056").to_crs("EPSG:4326").iloc[0]
            folium.Marker([cll.y, cll.x], icon=folium.DivIcon(html=(
                '<div style="transform:translate(-50%,-50%);white-space:nowrap;font-family:\'IBM Plex Mono\',monospace;'
                'font-size:10px;color:#fff;background:rgba(224,85,45,0.94);padding:3px 9px;border-radius:20px;'
                'box-shadow:0 2px 8px rgba(0,0,0,.3)">LANDSLIDE · {:.2f} km²</div>'.format(area_frana)))).add_to(m)
        except Exception:
            pass

    # dynamic legend
    parts = []
    if layer_choice != "None":
        name, expl, ramp = LAYER_LEGEND[layer_choice]
        parts.append(f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;color:#e0552d;letter-spacing:.1em;margin-bottom:1px">ACTIVE LAYER</div>'
                     f'<div style="font-size:11px;color:#1b2430;font-weight:600">{name}</div>'
                     f'<div style="font-size:9.5px;color:#5a6678;line-height:1.4;margin-top:2px">{expl}</div>{ramp}<div style="height:8px"></div>')
    if show_build:
        parts.append('<div style="font-family:\'IBM Plex Mono\',monospace;font-size:9px;color:#5a6678;letter-spacing:.1em;margin-bottom:3px">BUILDING EXPOSURE</div>'
            '<div style="line-height:1.8;font-size:10px">'
            '<span style="color:#e0552d">●</span> Footprint &nbsp;<span style="color:#f0962a">●</span> 100m &nbsp;'
            '<span style="color:#e6c419">●</span> 250m &nbsp;<span style="color:#5bb56a">●</span> 500m</div>')
    parts.append('<div style="font-size:10px;margin-top:3px"><span style="color:#d99a1f">▱</span> Watershed AOI</div>')
    legend_html = ('<div style="position:absolute;top:12px;right:12px;z-index:9999;max-width:240px;'
        'background:rgba(255,255,255,0.94);border:1px solid #e4e7ec;border-radius:12px;padding:11px 14px;'
        'font-family:Inter,sans-serif;color:#1a2030;backdrop-filter:blur(8px);box-shadow:0 6px 22px rgba(26,32,48,.16)">'
        + "".join(parts) + '</div>')
    m.get_root().html.add_child(folium.Element(legend_html))

    # Frame the AOI and lock the minimum zoom to that initial level
    m.add_child(FitAndLockZoom([[miny, minx], [maxy, maxx]]))

    st_folium(m, width="100%", height=600, returned_objects=[])

# ════════════════════════════════════════════════════════════════════
#  VIEW 3 · STATISTICS
# ════════════════════════════════════════════════════════════════════
elif view == "Statistics":
    kpi_strip()
    st.markdown('<div class="viewbar-eye">03 · QUANTITATIVE ANALYSIS</div>'
        '<div class="viewbar-title" style="margin:0.1rem 0 0.5rem 0">From imagery to risk figures</div>',
        unsafe_allow_html=True)
    sub = st.radio("substat", ["Change detection", "Morphology", "Exposure"],
                   horizontal=True, label_visibility="collapsed")
    st.markdown('<div style="height:0.5rem"></div>', unsafe_allow_html=True)

    LEG = dict(font_size=10, bgcolor="rgba(0,0,0,0)", orientation="h", y=1.1, x=0)

    # ── 3A · CHANGE DETECTION ─────────────────────────────────
    if sub == "Change detection":
        c1, c2 = st.columns([1, 1], gap="large")
        with c1:
            st.markdown('<div class="lblabel">Detection threshold · live</div>', unsafe_allow_html=True)
            threshold = st.slider("NDVI diff threshold", -0.30, 0.60, 0.10, 0.01, format="%.2f",
                                  label_visibility="collapsed",
                                  help="Lower = larger area (more false positives) · Higher = more conservative.")
            img_thr, area_thr = ndvi_highlight(threshold)
            if img_thr: st.image(img_thr, use_container_width=True)
            st.markdown('<div class="cap">Orange = classified landslide · Blue = intact vegetation · Red = NDVI loss</div>',
                        unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="card-b" style="margin-bottom:0.6rem">The footprint is delineated from the drop in '
                        'vegetation index between before and after. <b>NDVI = (NIR − Red)/(NIR + Red)</b>; pixels whose '
                        'NDVI loss exceeds the threshold are flagged as failure. The project keeps <b>0.10</b> (plus a '
                        'bare-soil rule), then removes patches &lt; 50 px (~5 000 m²).</div>', unsafe_allow_html=True)
            k1, k2 = st.columns(2)
            k1.metric("Classified area", f"{area_thr:.2f} km²", delta=f"at threshold {threshold:.2f}", delta_color="off")
            k2.metric("Project footprint", f"{area_frana:.2f} km²", delta="threshold 0.10", delta_color="off")
            arr_diff, _ = load_arr(PATHS["ndvi_diff"])
            if arr_diff is not None:
                flat = arr_diff[np.isfinite(arr_diff)].flatten()
                if len(flat) > 60000: flat = flat[np.random.choice(len(flat),60000,replace=False)]
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=flat[flat<=threshold], nbinsx=55, marker_color="#2f6fe0", opacity=0.55, name="Stable vegetation"))
                fig.add_trace(go.Histogram(x=flat[flat>threshold], nbinsx=55, marker_color="#e0552d", opacity=0.9, name="Classified landslide"))
                fig.add_vline(x=threshold, line_dash="dash", line_color="#d99a1f")
                fig.update_layout(**PLT, height=232, barmode="overlay", showlegend=True, legend=LEG,
                                  xaxis_title="NDVI difference (before − after)", yaxis_title="pixels")
                st.plotly_chart(fig, use_container_width=True)
            st.markdown('<div class="lblabel" style="margin-top:0.2rem">NDVI before &amp; after the event</div>', unsafe_allow_html=True)
            pc1, pc2 = st.columns(2)
            with pc1:
                im = render_single(PATHS["ndvi_pre"], "RdYlGn", -0.2, 0.8)
                if im: st.image(im, use_container_width=True)
                st.markdown('<div class="cap">Before · 2023: green = dense vegetation</div>', unsafe_allow_html=True)
            with pc2:
                im = render_single(PATHS["ndvi_post"], "RdYlGn", -0.2, 0.8)
                if im: st.image(im, use_container_width=True)
                st.markdown('<div class="cap">After · 2024: bare scar turns red</div>', unsafe_allow_html=True)

    # ── 3B · MORPHOLOGY ───────────────────────────────────────
    elif sub == "Morphology":
        st.markdown('<div class="card-b" style="margin-bottom:0.7rem">Steep slopes and high topographic wetness are the '
                    'morphological pre-conditions for failure, both computed from the swissALTI3D 2 m DTM. Move each '
                    'slider to measure how much of the catchment crosses a chosen value.</div>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1], gap="large")
        with c1:
            st.markdown('<div class="lblabel">Slope · steepness of the terrain</div>', unsafe_allow_html=True)
            arr, pxa = load_arr(PATHS["slope"]); s = raster_stats(PATHS["slope"])
            st.markdown(f'<div class="pill-row"><span class="pill">Mean <b>{s["mean"]:.1f}°</b></span>'
                f'<span class="pill">Median <b>{s["median"]:.1f}°</b></span>'
                f'<span class="pill">Max <b>{s["max"]:.1f}°</b></span></div>', unsafe_allow_html=True)
            thr = st.slider("Slope threshold (°)", 0, 80, 35, 1, key="sl")
            if arr is not None:
                flat = arr[np.isfinite(arr)].flatten()
                if len(flat) > 150000: flat = flat[np.random.choice(len(flat),150000,replace=False)]
                above = float(np.nansum(arr>thr)*pxa/1e6); pct = round(np.sum(flat>thr)/len(flat)*100,1)
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=flat[flat<=thr], nbinsx=55, marker_color="#2f6fe0", opacity=0.55, name=f"≤ {thr}°"))
                fig.add_trace(go.Histogram(x=flat[flat>thr], nbinsx=55, marker_color="#e0552d", opacity=0.9, name=f"> {thr}°"))
                fig.add_vline(x=thr, line_dash="dash", line_color="#d99a1f")
                fig.update_layout(**PLT, height=300, barmode="overlay", showlegend=True, legend=LEG,
                                  xaxis_title="Slope (°)", yaxis_title="pixels")
                st.plotly_chart(fig, use_container_width=True)
                a, b = st.columns(2)
                a.metric(f"Area above {thr}°", f"{above:.1f} km²")
                b.metric("Share of catchment", f"{pct:.0f}%")
        with c2:
            st.markdown('<div class="lblabel">TWI · topographic wetness (water concentration)</div>', unsafe_allow_html=True)
            arr2, pxa2 = load_arr(PATHS["twi"]); s2 = raster_stats(PATHS["twi"])
            st.markdown(f'<div class="pill-row"><span class="pill">Mean <b>{s2["mean"]:.2f}</b></span>'
                f'<span class="pill">Median <b>{s2["median"]:.2f}</b></span>'
                f'<span class="pill">P95 <b>{s2["p95"]:.2f}</b></span></div>', unsafe_allow_html=True)
            thr2 = st.slider("TWI threshold", 0.0, 15.0, 8.0, 0.5, key="tw")
            if arr2 is not None:
                flat2 = arr2[np.isfinite(arr2)].flatten()
                if len(flat2) > 150000: flat2 = flat2[np.random.choice(len(flat2),150000,replace=False)]
                above2 = float(np.nansum(arr2>thr2)*pxa2/1e6); pct2 = round(np.sum(flat2>thr2)/len(flat2)*100,1)
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=flat2[flat2<=thr2], nbinsx=55, marker_color="#2f6fe0", opacity=0.55, name=f"≤ {thr2}"))
                fig.add_trace(go.Histogram(x=flat2[flat2>thr2], nbinsx=55, marker_color="#2fa968", opacity=0.9, name=f"> {thr2}"))
                fig.add_vline(x=thr2, line_dash="dash", line_color="#d99a1f")
                fig.update_layout(**PLT, height=300, barmode="overlay", showlegend=True, legend=LEG,
                                  xaxis_title="TWI", yaxis_title="pixels")
                st.plotly_chart(fig, use_container_width=True)
                a2, b2 = st.columns(2)
                a2.metric(f"Area above {thr2}", f"{above2:.1f} km²")
                b2.metric("Share of catchment", f"{pct2:.0f}%")

    # ── 3C · EXPOSURE ─────────────────────────────────────────
    else:
        if buf_results:
            labels = ["Footprint","≤ 100 m","≤ 250 m","≤ 500 m"]; keys = ["diretto","100m","250m","500m"]
            colors = ["#e0552d","#f0962a","#e6c419","#5bb56a"]
            st.markdown('<div class="card-b" style="margin-bottom:0.7rem">Elements potentially at risk: OpenStreetMap '
                        'buildings and roads within the footprint and within 100 / 250 / 500 m of it. Exposure is '
                        '<b>physical proximity to the hazard</b>, not structural vulnerability; counts are cumulative.</div>',
                        unsafe_allow_html=True)
            c1, c2 = st.columns([1, 1], gap="large")
            with c1:
                st.markdown('<div class="lblabel">Buildings exposed by distance band</div>', unsafe_allow_html=True)
                n_ed = [buf_results.get(k,{}).get("edifici_colpiti",0) for k in keys]
                fig = go.Figure(go.Bar(x=labels, y=n_ed, marker_color=colors, marker_line_color="#fff", marker_line_width=1.5,
                    text=n_ed, textposition="outside", textfont=dict(size=13, color="#1a2030", family="Space Grotesk")))
                fig.update_layout(**PLT, height=320, showlegend=False, yaxis_title="buildings", yaxis_range=[0,max(n_ed)*1.25])
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.markdown('<div class="lblabel">Roads exposed by distance band (km)</div>', unsafe_allow_html=True)
                km_v = [buf_results.get(k,{}).get("strade_km",0) for k in keys]
                fig = go.Figure(go.Bar(x=labels, y=km_v, marker_color=colors, marker_line_color="#fff", marker_line_width=1.5,
                    text=[f"{v:.1f}" for v in km_v], textposition="outside", textfont=dict(size=13, color="#1a2030", family="Space Grotesk")))
                fig.update_layout(**PLT, height=320, showlegend=False, yaxis_title="km", yaxis_range=[0,max(km_v)*1.25])
                st.plotly_chart(fig, use_container_width=True)

            if gdf_build is not None and "esposizione" in gdf_build.columns:
                with st.popover("Explore exposed buildings: attribute table", use_container_width=True):
                    zl = st.radio("zone", ["Footprint","100 m","250 m","500 m"], horizontal=True, label_visibility="collapsed")
                    zk = {"Footprint":"diretta","100 m":"100m","250 m":"250m","500 m":"500m"}[zl]
                    dfz = gdf_build[gdf_build["esposizione"]==zk].copy()
                    dfz = dfz.drop(columns=[c for c in dfz.columns if c=="geometry"], errors="ignore")
                    ren = {"esposizione":"Zone","categoria":"Category","building":"OSM type","name":"Name",
                           "amenity":"Function","levels":"Floors","building_id":"ID"}
                    dfz = dfz.rename(columns={k:v for k,v in ren.items() if k in dfz.columns})
                    dfz = dfz[[c for c in dfz.columns if dfz[c].notna().sum()>0]]
                    d1, d2 = st.columns([3,1])
                    with d1: st.dataframe(dfz, use_container_width=True, hide_index=True, height=240)
                    with d2:
                        st.metric("Buildings", len(dfz))
                        if "Category" in dfz.columns and len(dfz):
                            st.markdown('<div class="lblabel" style="margin-top:0.4rem">By category</div>', unsafe_allow_html=True)
                            for t, c in dfz["Category"].value_counts().head(6).items():
                                st.markdown(f'<div style="display:flex;justify-content:space-between;font-size:0.72rem;'
                                    f'color:#5b6577;padding:.1rem 0"><span>{t}</span>'
                                    f'<span style="font-family:\'IBM Plex Mono\',monospace;color:#1a2030">{c}</span></div>',
                                    unsafe_allow_html=True)
        else:
            st.info("Run exposure.py to generate the exposure statistics.")

# ════════════════════════════════════════════════════════════════════
#  VIEW 4 · METHODOLOGY
# ════════════════════════════════════════════════════════════════════
elif view == "Methodology":
    viewbar("04 · HOW IT WAS DONE", "Methodology & data",
            "The full processing chain, the exact parameters used at each step, and the limitations "
            "of the analysis.")

    box = st.container(height=520, border=False)
    with box:
        m1, m2 = st.columns(2)
        with m1:
            st.markdown("""
            <div class="card" style="margin-bottom:0.7rem">
              <div class="card-h">1 · Data sources</div>
              <div class="card-b">
              • <b>Terrain</b>: swissALTI3D digital terrain model, <b>2 m</b> resolution (swisstopo),
                337 tiles downloaded and mosaicked, then clipped to the watershed AOI.<br>
              • <b>Satellite</b>: Sentinel-2 L2A surface reflectance, via Google Earth Engine.
                PRE = July 2023 median composite; POST = 25 Jun to 31 Jul 2024 median composite
                (cloud cover &lt; 20%).<br>
              • <b>Watershed AOI</b>: BAFU EZGG-CH sub-basins (17 basins, <b>31.82 km²</b>) draining toward Lostallo.<br>
              • <b>Exposure</b>: OpenStreetMap buildings (multipolygons) and roads (highways).<br>
              • <b>Reference system</b>: CH1903+ / LV95 (EPSG:2056).
              </div>
            </div>

            <div class="card" style="margin-bottom:0.7rem">
              <div class="card-h">2 · Change detection: landslide outline</div>
              <div class="card-b">
              NDVI computed from Sentinel-2 bands B8 (NIR) and B4 (Red):
              <code>NDVI = (NIR − Red) / (NIR + Red)</code>.<br>
              The before/after difference <code>NDVI_diff = NDVI_pre − NDVI_post</code> isolates vegetation loss.<br><br>
              <b>Classification rule:</b><br>
              <code>NDVI_diff &gt; 0.10</code> &nbsp;OR&nbsp;
              <code>(NDVI_post &lt; 0.20 AND NDVI_pre &gt; 0.25)</code>.<br><br>
              <b>Clean-up:</b> connected-component filter removing patches &lt; 50 pixels (3×3 connectivity,
              ≈ 5 000 m²). The raster mask is reprojected to EPSG:2056, clipped to the watershed and
              vectorised → <b>""" + f"{n_poly}" + """ polygons, """ + f"{area_frana:.2f}" + """ km²</b>.
              </div>
            </div>
            """, unsafe_allow_html=True)

        with m2:
            st.markdown("""
            <div class="card" style="margin-bottom:0.7rem">
              <div class="card-h">3 · Morphology (WhiteboxTools)</div>
              <div class="card-b">
              Computed on the 2 m DTM clipped to the AOI:<br>
              • Slope (degrees) and profile / plan curvature.<br>
              • Depression breaching (least-cost, dist = 5, fill).<br>
              • D8 flow pointer → D8 flow accumulation (cells).<br>
              • <b>TWI</b> = ln(specific catchment area / tan slope).<br><br>
              <b>Susceptibility index</b>: each factor normalised 0-1 and combined:<br>
              <code>0.40·slope + 0.25·TWI + 0.20·profile curvature + 0.15·log(1+flow acc.)</code><br>
              Weights from alpine debris-flow literature. The continuous index is split into
              <b>4 classes at the quartiles</b> (25 / 50 / 75%).
              </div>
            </div>

            <div class="card" style="margin-bottom:0.7rem">
              <div class="card-h">4 · Exposure</div>
              <div class="card-b">
              OSM buildings and roads clipped to the AOI. Buffers of 0 / 100 / 250 / 500 m built around the
              landslide union; buildings counted by spatial intersection, road length by clipping.<br>
              <b>Footprint:</b> """ + f"{buf_results.get('diretto',{}).get('edifici_colpiti','n/a')}" + """ buildings ·
              """ + f"{buf_results.get('diretto',{}).get('strade_km','n/a')}" + """ km roads. &nbsp;
              <b>Within 500 m:</b> """ + f"{buf_results.get('500m',{}).get('edifici_colpiti','n/a')}" + """ buildings ·
              """ + f"{buf_results.get('500m',{}).get('strade_km','n/a')}" + """ km.
              </div>
            </div>

            <div class="card" style="border-left:3px solid var(--accent)">
              <div class="card-h">5 · Limitations</div>
              <div class="card-b">
              The susceptibility model is <b>morphological and static</b>: it does not include rainfall,
              real soil saturation, lithology or land cover. The Sentinel-2 outline (10 m/pixel) has
              <b>not been field-validated</b> and may include co-located clearings or shadow artefacts.
              Exposure reflects proximity only, not structural fragility.
              </div>
            </div>
            """, unsafe_allow_html=True)
