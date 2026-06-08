import streamlit as st
import os

st.set_page_config(
    page_title="Lupi in Svizzera",
    page_icon="🐺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

html_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'lupi', 'index.html')

with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

st.components.v1.html(html_content, height=800, scrolling=False)