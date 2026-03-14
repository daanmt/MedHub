import streamlit as st

st.set_page_config(
    page_title="MedPRO - Residência Médica",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "Estudo": [
        st.Page("app/pages/01_dashboard.py",    title="Dashboard",         icon="🏠"),
        st.Page("app/pages/06_flashcards.py",   title="Flashcards",        icon="🧠"),
        st.Page("app/pages/03_caderno.py",      title="Caderno de Erros",  icon="📖"),
        st.Page("app/pages/02_resumos.py",      title="Resumos",           icon="📚"),
    ],
    "Análise": [
        st.Page("app/pages/04_historico.py",    title="Progresso e Histórico", icon="📈"),
    ],
}

pg = st.navigation(pages)
pg.run()
