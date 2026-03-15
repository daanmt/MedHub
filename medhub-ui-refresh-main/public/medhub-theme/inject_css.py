"""
MedHub — CSS Injector for Streamlit
Usage: import inject_css; inject_css.apply()
Place medhub_style.css in the same directory.
"""
import streamlit as st
from pathlib import Path


def apply():
    """Inject MedHub CSS into the Streamlit app."""
    css_path = Path(__file__).parent / "medhub_style.css"
    if css_path.exists():
        css = css_path.read_text()
    else:
        st.warning("medhub_style.css not found.")
        return
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
