import streamlit as st

st.set_page_config(
    page_title="MagicMeteo",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
  header[data-testid="stHeader"], [data-testid="collapsedControl"],
  section[data-testid="stSidebar"] { display: none !important; }
  .block-container { padding: 0.15rem 1rem 0 1rem !important; max-width: 100% !important; }
  [data-testid="stMainBlockContainer"] { padding-top: 0.15rem !important; }
  [data-testid="stVerticalBlock"] { gap: 0.4rem !important; }
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

st.components.v1.iframe(
    "https://ntrojan.github.io/gis-portfolio/static/magicmeteo/index.html",
    height=800,
    scrolling=False
)
