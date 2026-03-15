import streamlit as st
import pandas as pd
import plotly.express as px
from app.utils.parser import parse_caderno_erros
from app.utils.db import get_db_metrics

st.title("🏠 Dashboard")

# 1. Fonte de Verdade: SQLite (Performance Real)
db_data = get_db_metrics()

# 2. Fonte de Verdade: Caderno de Erros (Zero-DB Layer)
entries = parse_caderno_erros()

# --- MÉTRICAS DE PERFORMANCE ---
st.subheader("🎯 Desempenho Global (DB)")
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.metric("Questões Realizadas", db_data['total_questoes'])
with m_col2:
    st.metric("Total de Acertos", db_data['total_acertos'])
with m_col3:
    st.metric("Desempenho Geral", f"{db_data['media_desempenho']:.1f}%")

st.divider()

# --- DETALHAMENTO DO CADERNO ---
st.subheader("📖 Lacunas no Caderno de Erros")

st.divider()

# Preparar dados para gráficos
df = pd.DataFrame(entries)
df_areas = df.groupby('area').size().reset_index(name='Erros').sort_values('Erros', ascending=True)

# Linha de Gráficos
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
    fig.update_traces(hovertemplate='<b>%{y}</b><br>%{x} erros registrados<extra></extra>')
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
    fig_tree.update_traces(
        hovertemplate='<b>%{label}</b><br>Erros: %{value}<extra></extra>'
    )
    fig_tree.update_layout(margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig_tree, use_container_width=True)

st.divider()

# Tabela detalhada
st.markdown("#### Detalhamento Disciplinar")
st.dataframe(
    df_areas.sort_values('Erros', ascending=False),
    column_config={"area": "Disciplina", "Erros": st.column_config.NumberColumn("Qtd Erros")},
    hide_index=True,
    use_container_width=True
)

st.divider()
