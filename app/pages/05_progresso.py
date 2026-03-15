import streamlit as st
import plotly.express as px
import pandas as pd
from app.utils.parser import parse_sessions, parse_caderno_erros
from app.utils.file_io import read_md
from app.utils.db import get_db_metrics

st.title("📈 Progresso e Histórico")
st.markdown("Análise de lacunas e performance real (Híbrido Zero-DB + SQLite).")

# --- PERFORMANCE REAL (Baseada no Banco de Dados) ---
st.subheader("🎯 Aproveitamento por Disciplina")
db_metrics = get_db_metrics()
df_perf = db_metrics['df_areas']

if not df_perf.empty:
    fig_perf = px.bar(
        df_perf, x="Área", y="Desempenho",
        title="Aproveitamento (%) por Área de Estudo",
        template="plotly_dark",
        text_auto='.1f',
        color="Desempenho",
        color_continuous_scale="RdYlGn"
    )
    fig_perf.update_layout(yaxis_range=[0, 100])
    st.plotly_chart(fig_perf, use_container_width=True)
else:
    st.info("Aguardando dados de performance no banco de dados.")

st.divider()

# --- DISTRIBUIÇÃO (Baseada no Caderno de Erros) ---
st.subheader("📊 Distribuição de Lacunas")
entries = parse_caderno_erros()

if entries:
    df = pd.DataFrame(entries)
    df_areas = df.groupby('area').size().reset_index(name='Erros')
    
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(
            df_areas, values="Erros", names="area", hole=0.4, 
            title="Proporção de Erros por Área",
            template="plotly_dark"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        # Treemap Hierárquico
        fig_tree = px.treemap(
            df, path=["area", "tema"], 
            title="Visão Hierárquica de Lacunas",
            template="plotly_dark",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_tree.update_traces(hovertemplate='<b>%{label}</b><br>Erros: %{value}<extra></extra>')
        st.plotly_chart(fig_tree, use_container_width=True)
else:
    st.info("Nenhum erro registrado no caderno para análise.")

st.divider()

# --- HISTÓRICO DAS SESSÕES ---
st.subheader("🗓️ Histórico de Sessões")
df_sessions = parse_sessions()

if not df_sessions.empty:
    # Heatmap bar
    # Converter data string para datetime para o gráfico
    df_sessions['dt'] = pd.to_datetime(df_sessions['data'], errors='coerce')
    df_counts = df_sessions.dropna(subset=['dt']).groupby(df_sessions['dt'].dt.date).size().reset_index(name='qtd')
    
    fig_time = px.bar(
        df_counts, x="dt", y="qtd", 
        title="Volume de Sessões por Dia", 
        labels={"dt": "Data", "qtd": "Sessões"},
        template="plotly_dark"
    )
    fig_time.update_traces(marker_color='#4A90D9')
    st.plotly_chart(fig_time, use_container_width=True)
    
    st.markdown("### Logs Recentes")
    for idx, row in df_sessions.head(15).iterrows():
        f_name = row['arquivo']
        # Usamos o preview gerado pelo parser
        preview = row.get('preview', 'Sem preview disponível.')
        
        with st.expander(f"📄 Sessão #{row['session_id']} | {row['data']} — {f_name}", expanded=False):
            st.caption(preview)
            if st.button("Ver log completo", key=f_name):
                content = read_md(f"history/{f_name}")
                st.markdown(content)
else:
    st.info("Nenhuma sessão registrada no diretório history/.")
