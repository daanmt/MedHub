import streamlit as st
import plotly.express as px
from app.utils.db import get_db_metrics
from app.utils.file_io import read_md

st.title("🏠 Cronograma + Dashboard")
st.markdown("Visão holística do seu rendimento validado pelo Banco de Dados.")

# --- MÉTRICAS ---
st.subheader("📊 Métricas Consolidadas (SQLite)")
metrics = get_db_metrics()
total_erros = metrics["total"]
df_areas = metrics["df_areas"]

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Total de Erros Registrados", total_erros)
    
with col2:
    if not df_areas.empty:
        fig = px.bar(df_areas, x="Erros", y="Área", orientation='h', title="Erros por Área", height=250, template='plotly_dark', color_discrete_sequence=['#378ADD'])
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0), showlegend=False)
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Nenhum erro computado nas métricas ainda.")

st.divider()

# --- STATUS ---
st.subheader("📌 Status do Agente")
estado_content = read_md("ESTADO.md")
with st.expander("Ver `ESTADO.md` completo", expanded=False):
    if estado_content:
        st.markdown(estado_content)
    else:
        st.warning("Arquivo ESTADO.md não encontrado.")
