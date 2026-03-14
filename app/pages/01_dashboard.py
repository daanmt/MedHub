import streamlit as st
import plotly.express as px
import pandas as pd
from app.utils.db import get_db_metrics, get_cronograma, update_cronograma_status
from app.utils.file_io import read_md

st.title("🏠 Cronograma + Dashboard")
st.markdown("Visão holística do seu rendimento e planejamento de estudos.")

# --- CRONOGRAMA ---
st.subheader("📅 Cronograma de Estudos")

df_crono = get_cronograma()

if not df_crono.empty:
    # Seleção da Semana (Default: última semana com algo concluído ou 5)
    semanas_ordenadas = df_crono['Semana'].unique().tolist()
    # Pega a semana de Sífilis (index 4 = Semana 5)
    default_index = 4 if len(semanas_ordenadas) > 4 else 0
    
    selected_week = st.selectbox("Selecione a Semana", semanas_ordenadas, index=default_index)
    
    # Filtra dados da semana
    df_week = df_crono[df_crono['Semana'] == selected_week].copy()
    
    st.markdown(f"### 📋 Temas da Semana: {selected_week}")
    
    # Visualização Simplificada e Estética
    # Usamos o data_editor mas configurado para ser a peça central
    edited_week = st.data_editor(
        df_week,
        column_config={
            "id": None,
            "Semana": None, # Esconde semana já que está no título
            "Tema": st.column_config.TextColumn("Tema de Estudo", width="large"),
            "Status": st.column_config.SelectboxColumn(
                "Status",
                options=["Pendente", "Lendo", "Concluído"],
                required=True,
                width="medium"
            )
        },
        disabled=["Tema"],
        hide_index=True,
        use_container_width=True,
        height=300,
        key="weekly_editor"
    )

    if st.button("💾 Salvar Progresso Semanal"):
        # Compara apenas os itens da semana
        original_week = df_crono[df_crono['Semana'] == selected_week]
        diff = edited_week[edited_week["Status"] != original_week["Status"].values]
        
        if not diff.empty:
            for _, row in diff.iterrows():
                update_cronograma_status(row["id"], row["Status"])
            st.success("✅ Progresso da semana atualizado!")
            st.rerun()
else:
    st.warning("Cronograma não encontrado.")


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
