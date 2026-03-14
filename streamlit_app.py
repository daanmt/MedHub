import streamlit as st

st.set_page_config(
    page_title="IPUB — Residência Médica",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "Estudo": [
        st.Page("app/pages/01_dashboard.py",       title="Dashboard",        icon="🏠"),
        st.Page("app/pages/02_caderno_erros.py",   title="Caderno de Erros", icon="📖"),
        st.Page("app/pages/03_resumos.py",         title="Resumos por Área", icon="📚"),
    ],
    "Análise": [
        st.Page("app/pages/04_progresso.py",       title="Progresso",        icon="📈"),
        st.Page("app/pages/05_historico.py",       title="Histórico",        icon="🗓️"),
    ],
}

pg = st.navigation(pages)
pg.run()
