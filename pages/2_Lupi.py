import streamlit as st

st.set_page_config(
    page_title="Lupi in Svizzera",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.components.v1.iframe(
    "https://ntrojan.github.io/gis-portfolio/static/lupi/index.html",
    height=800,
    scrolling=False
)