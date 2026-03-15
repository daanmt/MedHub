import streamlit as st
from app.utils.styles import inject_styles

st.set_page_config(
    page_title="MedHub - Residência Médica",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

pages = {
    "Estudo": [
        st.Page("app/pages/01_dashboard.py",    title="Dashboard",         icon="🏠"),
        st.Page("app/pages/02_flashcards.py",   title="Flashcards",        icon="🧠"),
        st.Page("app/pages/03_caderno.py",      title="Caderno de Erros",  icon="📖"),
        st.Page("app/pages/04_resumos.py",      title="Resumos",           icon="📚"),
    ],
}

pg = st.navigation(pages)
pg.run()
