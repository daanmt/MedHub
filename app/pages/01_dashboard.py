import streamlit as st
import plotly.express as px
import pandas as pd
from app.utils.db import get_db_metrics, get_cronograma, update_cronograma_status
from app.utils.file_io import read_md

st.title("🏠 Dashboard")

df_crono = get_cronograma()

if not df_crono.empty:
    # Identifica a 'Semana Ativa' (Primeira semana que possui temas pendentes)
    pending_df = df_crono[df_crono['Status'] != 'Concluído']
    pending_weeks = pending_df['Semana'].unique().tolist()
    
    if pending_weeks:
        active_week = pending_weeks[0]
        
        # Filtra apenas os temas PENDENTES da Semana Ativa
        df_display = df_crono[
            (df_crono['Semana'] == active_week) & 
            (df_crono['Status'] != 'Concluído')
        ].copy()
        
        st.subheader(f"🎯 Próximas Tarefas: {active_week}")
        
        if not df_display.empty:
            st.dataframe(
                df_display[['Tema']],
                column_config={
                    "Tema": st.column_config.TextColumn("Tema de Estudo", width="large"),
                },
                hide_index=True,
                width="stretch"
            )
        else:
            st.rerun()
    else:
        st.success("✨ Todas as tarefas foram concluídas! Você encerrou o cronograma.")
else:
    st.warning("Cronograma não carregado. Utilize Tools/migrate_cronograma.py.")

st.divider()

# --- MÉTRICAS ---
st.subheader("📊 Métricas de Performance")
metrics = get_db_metrics()

# Linha de Cards de Resumo
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric("Total de Erros", metrics["total_erros"], delta_color="inverse")
with col_m2:
    st.metric("Total de Acertos", metrics["total_acertos"])
with col_m3:
    st.metric("Questões Realizadas", metrics["total_questoes"])
with col_m4:
    st.metric("Desempenho Geral", f"{metrics['media_desempenho']:.1f}%")

st.markdown("#### Detalhamento por Disciplina")
df_areas = metrics["df_areas"]

if not df_areas.empty:
    # Gráfico Comparativo: Barra Horizontal (Plan v2.0)
    fig = px.bar(
        df_areas.sort_values('Erros'), 
        x='Erros', y='Área',
        orientation='h',
        template='plotly_dark',
        color_discrete_sequence=['#378ADD'],
        labels={'Erros': 'Erros', 'Área': 'Área'},
    )
    fig.update_layout(
        margin=dict(l=0, r=20, t=30, b=0),
        showlegend=False,
        height=300,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    fig.update_traces(hovertemplate='%{y}: %{x} erros<extra></extra>')
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de Performance
    st.dataframe(
        df_areas[['Área', 'Total', 'Acertos', 'Erros', 'Desempenho']],
        column_config={
            "Desempenho": st.column_config.NumberColumn("Aproveitamento", format="%.1f%%"),
        },
        hide_index=True,
        width="stretch"
    )
else:
    st.info("Aguardando registro de questões para gerar estatísticas detalhadas.")

st.divider()

# --- SESSÕES RECENTES ---
st.subheader("🗓️ Sessões Recentes")
from app.utils.parser import parse_sessions
df_sessions = parse_sessions()

if not df_sessions.empty:
    for idx, row in df_sessions.head(5).iterrows():
        st.write(f"📄 **{row['data']}** — SESSÃO #{row['session_id']}")
    st.caption("Veja o histórico completo na aba 'Análise'.")
else:
    st.caption("Nenhuma sessão registrada recentemente.")

st.divider()
