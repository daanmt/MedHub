import streamlit as st
import pandas as pd
import plotly.express as px
from app.utils.parser import parse_caderno_erros, parse_sessions
from app.utils.db import get_db_metrics
from app.utils.file_io import read_md

st.title("🏥 MedHub Dashboard")

# 1. Fonte de Verdade: SQLite (Performance Real)
db_data = get_db_metrics()

# 2. Fonte de Verdade: Caderno de Erros (Zero-DB Layer)
entries = parse_caderno_erros()

# --- MÉTRICAS DE PERFORMANCE ---
st.subheader("🎯 Desempenho Global")
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.metric("Questões Realizadas", db_data['total_questoes'])
with m_col2:
    st.metric("Total de Acertos", db_data['total_acertos'])
with m_col3:
    st.metric("Desempenho Geral", f"{db_data['media_desempenho']:.1f}%")

st.divider()

# --- APROVEITAMENTO POR ÁREA (Integrado de Progresso) ---
st.subheader("📈 Aproveitamento por Disciplina")
df_perf = db_data['df_areas']

if not df_perf.empty:
    fig_perf = px.bar(
        df_perf, x="Área", y="Desempenho",
        template="plotly_dark",
        text_auto='.1f',
        color="Desempenho",
        color_continuous_scale="RdYlGn",
        height=350
    )
    fig_perf.update_layout(yaxis_range=[0, 100], margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_perf, use_container_width=True)

st.divider()

# --- DISTRIBUIÇÃO DE LACUNAS ---
st.subheader("📖 Lacunas no Caderno de Erros")

if entries:
    df = pd.DataFrame(entries)
    df_areas = df.groupby('area').size().reset_index(name='Erros').sort_values('Erros', ascending=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Distribuição por Área")
        fig = px.bar(
            df_areas, 
            x='Erros', y='area',
            orientation='h',
            template='plotly_dark',
            color_discrete_sequence=['#378ADD'],
            labels={'Erros': 'Erros', 'area': 'Área'},
            height=350
        )
        fig.update_layout(
            margin=dict(l=0, r=20, t=30, b=0),
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
        )
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("#### Visão Hierárquica")
        fig_tree = px.treemap(
            df, 
            path=["area", "tema"], 
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            height=350
        )
        fig_tree.update_layout(margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_tree, use_container_width=True)
else:
    st.info("Nenhum erro registrado no caderno.")

st.divider()

# --- HISTÓRICO DE SESSÕES (Integrado de Progresso) ---
st.subheader("🗓️ Histórico de Sessões")
df_sessions = parse_sessions()

if not df_sessions.empty:
    # Heatmap de volume
    df_sessions['dt'] = pd.to_datetime(df_sessions['data'], errors='coerce')
    df_counts = df_sessions.dropna(subset=['dt']).groupby(df_sessions['dt'].dt.date).size().reset_index(name='qtd')
    
    fig_time = px.bar(
        df_counts, x="dt", y="qtd", 
        labels={"dt": "Data", "qtd": "Sessões"},
        template="plotly_dark",
        height=300
    )
    fig_time.update_traces(marker_color='#4A90D9')
    fig_time.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_time, use_container_width=True)
    
    st.markdown("#### Logs Recentes")
    for idx, row in df_sessions.head(10).iterrows():
        f_name = row['arquivo']
        preview = row.get('preview', 'Sem preview disponível.')
        with st.expander(f"📄 Sessão #{row['session_id']} | {row['data']} — {f_name}", expanded=False):
            st.caption(preview)
            if st.button("Ver log completo", key=f_name):
                content = read_md(f"history/{f_name}")
                st.markdown(content)
else:
    st.info("Nenhuma sessão registrada no histórico.")

st.divider()
