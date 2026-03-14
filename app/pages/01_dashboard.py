import streamlit as st
import plotly.express as px
from app.utils.parser import get_error_stats, parse_sessions
from app.utils.file_io import read_md

st.title("🏠 Dashboard")
st.markdown("Bem-vindo ao centro de controle do IPUB.")

# --- 1. MÉTRICAS (Caderno de Erros) ---
st.subheader("📊 Métricas de Erros")
stats = get_error_stats()
total_erros = stats.get("total", 0)
por_area = stats.get("por_area", {})

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Total de Erros Registrados", total_erros)
    
with col2:
    if por_area:
        import pandas as pd
        df_areas = pd.DataFrame(list(por_area.items()), columns=["Área", "Erros"])
        fig = px.bar(df_areas, x="Erros", y="Área", orientation='h', title="Erros por Área", height=250)
        fig.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhum erro computado nas métricas ainda.")

st.divider()

# --- 2. ÚLTIMO ESTADO ---
st.subheader("📌 Status do Agente")
estado_content = read_md("ESTADO.md")
with st.expander("Ver `ESTADO.md` completo", expanded=False):
    if estado_content:
        st.markdown(estado_content)
    else:
        st.warning("Arquivo ESTADO.md não encontrado.")

st.divider()

# --- 3. SESSÕES RECENTES ---
st.subheader("🗓️ Sessões de Estudo Recentes")
df_sessions = parse_sessions()
if not df_sessions.empty:
    for idx, row in df_sessions.head(3).iterrows():
        label = row['data'].strftime('%Y-%m-%d') if not pd.isnull(row['data']) else "Data Indefinida"
        with st.expander(f"{label} - {row['arquivo']}"):
            content = read_md(f"history/{row['arquivo']}")
            st.markdown(content)
else:
    st.info("Nenhuma sessão registrada no diretório history/.")
