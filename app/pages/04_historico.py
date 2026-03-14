import streamlit as st
import plotly.express as px
import pandas as pd
from app.utils.parser import parse_sessions
from app.utils.db import get_db_metrics
from app.utils.file_io import read_md

st.title("📈 Progresso e Histórico")
st.markdown("Timeline de estudos e distribuição detalhada de erros.")

# --- DISTRIBUIÇÃO ---
st.subheader("Distribuição do Aprendizado")
metrics = get_db_metrics()
df_areas = metrics["df_areas"]

if not df_areas.empty:
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(df_areas, values="Erros", names="Área", hole=0.4, title="Proporção de Erros")
        st.plotly_chart(fig_pie, width="stretch")
        
    with c2:
        fig_tree = px.treemap(df_areas, path=["Área"], values="Erros", title="Visão Hierárquica", color="Erros", color_continuous_scale='RdBu_r')
        fig_tree.update_traces(hovertemplate='<b>%{label}</b><br>Erros: %{value}<extra></extra>')
        st.plotly_chart(fig_tree, width="stretch")

st.divider()

# --- HISTÓRICO DAS SESSÕES ---
st.subheader("🗓️ Histórico de Sessões")
df_sessions = parse_sessions()

if not df_sessions.empty:
    # Heatmap bar
    df_counts = df_sessions.groupby(df_sessions['data'].dt.date).size().reset_index(name='qtd')
    fig_time = px.bar(df_counts, x="data", y="qtd", title="Volume de Sessões por Dia", labels={"data": "Data", "qtd": "Sessões"})
    fig_time.update_traces(marker_color='#4A90D9')
    st.plotly_chart(fig_time, width="stretch")
    
    st.markdown("### Logs Recentes")
    for idx, row in df_sessions.head(10).iterrows():
        label = row['data'].strftime('%Y-%m-%d') if not pd.isnull(row['data']) else "Data Indefinida"
        f_name = row['arquivo']
        
        content = read_md(f"history/{f_name}")
        lines = content.split('\n')
        title = lines[0].replace("#", "").strip() if lines else f_name
        
        content_lines = [l for l in lines[2:] if l.strip()]
        preview = ' '.join(content_lines[:3])[:200] + '...' if content_lines else ''
        
        with st.expander(f"📄 {label} | {f_name} — {title}", expanded=False):
            c1_exp, c2_exp = st.columns([3,1])
            with c1_exp:
                st.caption(preview)
            with c2_exp:
                if st.button("Ver log completo", key=f_name):
                    st.markdown(content)
else:
    st.info("Nenhuma sessão registrada no diretório history/.")
