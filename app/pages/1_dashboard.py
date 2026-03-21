import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(page_title="MedHub Dashboard", page_icon="📊", layout="wide")
DB_PATH = 'ipub.db'

def get_dashboard_data():
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM taxonomia_cronograma", conn)
    conn.close()
    return df

st.title("📊 Painel Central")
st.markdown('<p style="color: #A8B3C2; margin-top: -15px; margin-bottom: 30px;">A Métrica como Bússola.</p>', unsafe_allow_html=True)

df = get_dashboard_data()

if df is not None and not df.empty:
    feitas = int(df['questoes_realizadas'].sum())
    acertos = int(df['questoes_acertadas'].sum())
    perf = (acertos / feitas * 100) if feitas > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Questões (EMED)", feitas)
    m2.metric("Acertos", acertos)
    m3.metric("Desempenho Geral", f"{perf:.1f}%")

    st.divider()

    c1, c2 = st.columns([1.5, 1])

    with c1:
        st.subheader("📈 Aproveitamento por Especialidade")
        # Normalização visual pro Gráfico
        df_area_norm = df.copy()
        df_area_norm['area'] = df_area_norm['area'].apply(lambda x: 'Ginecologia e Obstetrícia' if x in ['GO', 'Ginecologia'] else x)
        
        df_area = df_area_norm.groupby('area').agg({'questoes_realizadas':'sum', 'questoes_acertadas':'sum'}).reset_index()
        df_area['perf'] = (df_area['questoes_acertadas'] / df_area['questoes_realizadas'] * 100).fillna(0)
        
        fig = px.bar(df_area, x='perf', y='area', orientation='h', template='plotly_dark', color_discrete_sequence=['#2F6BFF'])
        fig.update_layout(xaxis_range=[0, 100], margin=dict(l=0, r=20, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, width='stretch')

    with c2:
        st.subheader("🚨 Foco Crítico (Revisão)")
        st.caption("Temas com baixa performance ou não vistos há muito tempo.")
        
        # Regra de Esquecimento (FSRS Heurística)
        df['dias_sem_ver'] = (datetime.now() - pd.to_datetime(df['ultima_revisao'])).dt.days
        df['dias_sem_ver'] = df['dias_sem_ver'].fillna(999)
        
        # Filtra temas que já foram estudadados (realizadas > 0)
        # E que NÃO foram vistos nos últimos 3 dias (período de proteção / memória curta)
        df_elegiveis = df[(df['questoes_realizadas'] > 0) & (df['dias_sem_ver'] > 3)].copy()
        
        # O Peso de Revisão prioriza TEMPO SEM VER e BAIXA PERFORMANCE
        if not df_elegiveis.empty:
            df_elegiveis['fator_risco'] = df_elegiveis['dias_sem_ver'] + ((100 - df_elegiveis['percentual_acertos']) * 0.5)
            critico = df_elegiveis.sort_values(by='fator_risco', ascending=False).head(8)
            
            for _, r in critico.iterrows():
                st.markdown(f"""
                <div style="background: #11161D; border-left: 3px solid #D9534F; border-radius: 6px; padding: 10px; margin-bottom: 8px;">
                    <div style="font-size: 0.85rem; color: #A8B3C2;">{r['area']}</div>
                    <div style="font-weight: 600; color: #F3F7FC;">{r['tema']}</div>
                    <div style="font-size: 0.8rem; color: #D9A441;">Acertos: {r['percentual_acertos']:.1f}% | Há {int(r['dias_sem_ver'])} dias</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 Você está em dia! Nenhum tema crítico mapeado para revisão urgente hoje.")

else:
    st.info("Banco de dados vazio ou inicializando.")
