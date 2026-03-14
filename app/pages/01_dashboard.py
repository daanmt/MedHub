import streamlit as st
import plotly.express as px
import pandas as pd
from app.utils.db import get_db_metrics, get_cronograma, update_cronograma_status
from app.utils.file_io import read_md

st.title("🏠 Cronograma + Dashboard")

df_crono = get_cronograma()

if not df_crono.empty:
    # Filtra apenas os temas PENDENTES (Single Source of Truth)
    # Ordenados pela posição original do Excel (pos_semana, pos_tema)
    df_next = df_crono[df_crono['Status'] != 'Concluído'].copy()
    
    st.subheader("🎯 Próximas Tarefas")
    
    if not df_next.empty:
        # Exibe os próximos temas (ex: top 15 para não poluir)
        st.dataframe(
            df_next[['Tema']].head(15),
            column_config={
                "Tema": st.column_config.TextColumn("Próximos Temas de Estudo", width="large"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.success("✨ Todas as tarefas foram concluídas! Você está em dia com o cronograma.")
else:
    st.warning("Cronograma não carregado. Utilize Tools/migrate_cronograma.py.")



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
