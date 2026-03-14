import streamlit as st

st.set_page_config(
    page_title="IPUB — Residência Médica",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "Estudo": [
        st.Page("pages/01_dashboard.py",       title="Dashboard",        icon="🏠"),
        st.Page("pages/02_caderno_erros.py",   title="Caderno de Erros", icon="📖"),
        st.Page("pages/03_resumos.py",         title="Resumos por Área", icon="📚"),
    ],
    "Análise": [
        st.Page("pages/04_progresso.py",       title="Progresso",        icon="📈"),
        st.Page("pages/05_historico.py",       title="Histórico",        icon="🗓️"),
    ],
}

pg = st.navigation(pages)
pg.run()
