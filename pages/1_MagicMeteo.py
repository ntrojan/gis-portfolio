import streamlit as st

st.set_page_config(
    page_title="MagicMeteo",
    page_icon="⛷️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.components.v1.iframe(
    "https://ntrojan.github.io/gis-portfolio/static/magicmeteo/index.html",
    height=800,
    scrolling=False
)