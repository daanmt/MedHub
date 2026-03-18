from app.utils.styles import metric_card
import streamlit as st
import pandas as pd
import plotly.express as px
from app.utils.parser import parse_caderno_erros
from app.utils.db import get_db_metrics

st.title("📊 MedHub Dashboard")
st.markdown('<p style="color: #A8B3C2; margin-top: -15px; margin-bottom: 30px;">Visão geral do seu progresso de estudos</p>', unsafe_allow_html=True)

# ── Sidebar: Reimportar EMED ──────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Dados EMED")
    if st.button("🔄 Reimportar dados EMED", width='stretch'):
        try:
            import sys, os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
            from Tools.import_performance_excel import import_performance
            with st.spinner("Importando Excel..."):
                ok, msg = import_performance()
            if ok:
                st.success(msg)
                st.cache_data.clear()
                st.rerun()
            else:
                st.error(msg)
        except Exception as e:
            st.error(f"Erro: {e}")

# 1. Fonte de Verdade
entries = parse_caderno_erros()
try:
    db_data = get_db_metrics()
    has_db = db_data['total_questoes'] > 0
except Exception:
    has_db = False
    db_data = {'total_questoes': 0, 'total_acertos': 0, 'media_desempenho': 0.0, 'df_areas': pd.DataFrame()}

# --- MÉTRICAS DE PERFORMANCE ---
st.subheader("🎯 Desempenho Global")
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    metric_card("Questões Realizadas", str(db_data['total_questoes']) if has_db else "—")
with m_col2:
    metric_card("Total de Acertos", str(db_data['total_acertos']) if has_db else "—")
with m_col3:
    metric_card("Desempenho Geral", f"{db_data['media_desempenho']:.1f}%" if has_db else "—", delta="Em evolução" if has_db else None, delta_type="up")

st.markdown("<br>", unsafe_allow_html=True)

# --- APROVEITAMENTO POR ÁREA ---
st.subheader("📈 Aproveitamento por Disciplina")
df_perf = db_data['df_areas']

if has_db and not df_perf.empty:
    fig_perf = px.bar(
        df_perf, x="Desempenho", y="Área",
        orientation='h',
        template="plotly_dark",
        text_auto='.1f',
        color_discrete_sequence=["#2F6BFF"],
        height=350
    )
    fig_perf.update_layout(
        xaxis_range=[0, 100],
        margin=dict(l=0, r=20, t=30, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#A8B3C2"),
        showlegend=False,
    )
    st.plotly_chart(fig_perf, width='stretch')
else:
    st.info("Clique em '🔄 Reimportar dados EMED' no menu lateral para importar os dados da planilha.")

# --- DISTRIBUIÇÃO DE LACUNAS ---
st.subheader("📖 Lacunas no Caderno de Erros")

if entries:
    df = pd.DataFrame(entries)
    df_areas = df.groupby('area').size().reset_index(name='Erros').sort_values('Erros', ascending=True)
    fig = px.bar(
        df_areas,
        x='Erros', y='area',
        orientation='h',
        template='plotly_dark',
        color_discrete_sequence=['#2F6BFF'],
        labels={'Erros': 'Erros', 'area': 'Área'},
        height=350
    )
    fig.update_layout(
        margin=dict(l=0, r=20, t=0, b=0),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter", color="#A8B3C2"),
    )
    st.plotly_chart(fig, width='stretch')
else:
    st.info("Nenhum erro registrado no caderno.")

st.divider()
