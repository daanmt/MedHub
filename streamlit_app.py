import streamlit as st

st.set_page_config(
    page_title="MedHub - Residência Médica",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "Estudo": [
        st.Page("app/pages/01_dashboard.py",    title="Dashboard",         icon="🏠"),
        st.Page("app/pages/02_flashcards.py",   title="Flashcards",        icon="🧠"),
        st.Page("app/pages/03_caderno.py",      title="Caderno de Erros",  icon="📖"),
        st.Page("app/pages/04_resumos.py",      title="Resumos",           icon="📚"),
    ],
    "Análise": [
        st.Page("app/pages/05_progresso.py",    title="Progresso e Histórico", icon="📈"),
    ],
}

pg = st.navigation(pages)
pg.run()
