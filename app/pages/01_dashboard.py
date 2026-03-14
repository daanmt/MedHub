import streamlit as st
import plotly.express as px
import pandas as pd
from app.utils.db import get_db_metrics
from app.utils.file_io import read_md

st.title("🏠 Cronograma + Dashboard")
st.markdown("Visão holística do seu rendimento e planejamento de estudos.")

# --- CRONOGRAMA ---
st.subheader("📅 Cronograma")

@st.cache_data
def load_cronograma():
    try:
        # Garante o nome exato do arquivo sem espaços duplos acidentais
        filename = "Cronograma de Reta Final.xlsx"
        df = pd.read_excel(filename, header=1)
        # Limpa formatação vazia do Excel
        df = df.dropna(how='all', axis=1).fillna("")
        return df
    except Exception as e:
        return pd.DataFrame()

df_crono = load_cronograma()
if not df_crono.empty:
    st.dataframe(df_crono, width="stretch", height=400)
else:
    st.warning("Arquivo `Cronograma de Reta Final.xlsx` não encontrado na raiz ou formato inválido.")

st.divider()

# --- MÉTRICAS ---
st.subheader("📊 Métricas Consolidadas")
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
