import streamlit as st
import plotly.express as px
import pandas as pd
from app.utils.db import get_db_metrics, get_cronograma, update_cronograma_status
from app.utils.file_io import read_md

st.title("🏠 Cronograma + Dashboard")
st.markdown("Visão holística do seu rendimento e planejamento de estudos.")

# --- CRONOGRAMA ---
st.subheader("📅 Cronograma")

df_crono = get_cronograma()

if not df_crono.empty:
    # Remove o ID da visualização mas mantém para referência
    edited_df = st.data_editor(
        df_crono,
        column_config={
            "id": None, 
            "Semana": st.column_config.TextColumn("Semana", width="small"),
            "Tema": st.column_config.TextColumn("Tema de Estudo", width="large"),
            "Status": st.column_config.SelectboxColumn(
                "Status",
                help="Seu progresso",
                options=["Pendente", "Lendo", "Concluído"],
                required=True,
                width="small"
            )
        },
        disabled=["Semana", "Tema"],
        hide_index=True,
        use_container_width=True,
        height=500,
        key="cronograma_editor"
    )

    # Lógica de salvamento (se houver alterações)
    if st.button("💾 Salvar Evolução do Cronograma"):
        # Compara o DataFrame original com o editado para encontrar mudanças
        diff = edited_df[edited_df["Status"] != df_crono["Status"]]
        if not diff.empty:
            for _, row in diff.iterrows():
                update_cronograma_status(row["id"], row["Status"])
            st.success(f"Progresso atualizado em {len(diff)} tema(s)!")
            st.rerun()
        else:
            st.info("Nenhuma alteração detectada no cronograma.")
else:
    st.warning("Cronograma não encontrado no banco de dados. Execute a migração (Tools/migrate_cronograma.py).")

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
