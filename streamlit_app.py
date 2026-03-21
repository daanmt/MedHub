import streamlit as st

st.set_page_config(
    page_title="MedHub - Especialista",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

pages = {
    "Hub Principal": [
        st.Page("app/pages/1_dashboard.py",    title="Dashboard & Métricas", icon="📊"),
        st.Page("app/pages/2_estudo.py",       title="Caderno & Retenção FSRS", icon="🧠"),
        st.Page("app/pages/3_biblioteca.py",   title="Biblioteca & PDFs", icon="📚"),
        st.Page("app/pages/4_simulados.py",    title="Simulados RAG", icon="🎯"),
    ],
}

pg = st.navigation(pages)
pg.run()
