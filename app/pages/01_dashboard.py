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
    # Seleção da Semana
    semanas_ordenadas = df_crono['Semana'].unique().tolist()
    default_index = 4 if len(semanas_ordenadas) > 4 else 0
    selected_week = st.selectbox("📅 Selecione a Semana", semanas_ordenadas, index=default_index)
    
    # Filtra apenas PENDENTES da semana selecionada
    df_week = df_crono[
        (df_crono['Semana'] == selected_week) & 
        (df_crono['Status'] != 'Concluído')
    ].copy()
    
    st.markdown(f"### 🎯 To-Do da Semana: {selected_week}")
    
    if not df_week.empty:
        # Coluna temporária para o Checkbox de conclusão
        df_week['Concluído'] = False
        
        edited_week = st.data_editor(
            df_week,
            column_config={
                "id": None,
                "Semana": None,
                "Status": None, # Status removido por ser redundante (tudo aqui é pendente)
                "Tema": st.column_config.TextColumn("Tema Pendente", width="large"),
                "Concluído": st.column_config.CheckboxColumn(
                    "Concluir",
                    help="Marque para concluir o tema e removê-lo da lista",
                    default=False,
                )
            },
            disabled=["Tema"],
            hide_index=True,
            use_container_width=True,
            height=300,
            key="minimal_todo_editor"
        )

        if st.button("🚀 Confirmar Temas Concluídos"):
            to_finish = edited_week[edited_week["Concluído"] == True]
            if not to_finish.empty:
                for _, row in to_finish.iterrows():
                    update_cronograma_status(row["id"], "Concluído")
                st.success(f"{len(to_finish)} tema(s) concluído(s)!")
                st.rerun()
            else:
                st.info("Nenhum tema selecionado.")
    else:
        st.success("✨ Tudo pronto! Não há temas pendentes para esta semana.")
else:
    st.warning("Cronograma vazio ou não carregado.")


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
