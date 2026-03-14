import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.parser import get_error_stats, parse_sessions

st.title("📈 Analytics e Progresso")
st.markdown("Acompanhe o ganho de retenção e as sessões de estudo ao longo do tempo.")

st.divider()

# --- GRÁFICOS DE ÁREA ---
st.subheader("Distribuição de Erros por Área")
stats = get_error_stats()
por_area = stats.get("por_area", {})

if por_area:
    df_areas = pd.DataFrame(list(por_area.items()), columns=["Área", "Erros"])
    
    c1, c2 = st.columns(2)
    with c1:
        # Gráfico Donut (Pie)
        fig_pie = px.pie(df_areas, values="Erros", names="Área", hole=0.4, title="Proporção de Erros")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        # Gráfico Treemap
        fig_tree = px.treemap(df_areas, path=["Área"], values="Erros", title="Visão Hierárquica")
        st.plotly_chart(fig_tree, use_container_width=True)
else:
    st.info("Não há dados de erros suficientes para gerar gráficos.")

st.divider()

# --- TIMELINE DE ESTUDO (Heatmap) ---
st.subheader("🔥 Frequência de Sessões (Timeline)")
df_sessions = parse_sessions()

if not df_sessions.empty:
    # Agrupa qtd de sessoes por data
    df_counts = df_sessions.groupby(df_sessions['data'].dt.date).size().reset_index(name='qtd')
    
    fig_time = px.bar(df_counts, x="data", y="qtd", title="Sessões de Estudo por Dia", labels={"data": "Data", "qtd": "Sessões registradas"})
    fig_time.update_traces(marker_color='#4A90D9')
    st.plotly_chart(fig_time, use_container_width=True)
    
    st.markdown("**Tabela de Dados Brutos (`history/`)**")
    st.dataframe(df_sessions[["data", "arquivo", "preview"]], use_container_width=True)
else:
    st.info("Nenhuma sessão registrada. Crie entradas na aba Histórico para preencher o gráfico.")
