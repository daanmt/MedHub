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
        df_area = df.groupby('area').agg({'questoes_realizadas':'sum', 'questoes_acertadas':'sum'}).reset_index()
        df_area['perf'] = (df_area['questoes_acertadas'] / df_area['questoes_realizadas'] * 100).fillna(0)
        
        fig = px.bar(df_area, x='perf', y='area', orientation='h', template='plotly_dark', color_discrete_sequence=['#2F6BFF'])
        fig.update_layout(xaxis_range=[0, 100], margin=dict(l=0, r=20, t=10, b=0), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("🚨 Foco Crítico (Revisão)")
        st.caption("Temas com baixa performance ou não vistos há muito tempo.")
        
        # Calculate scores
        df['dias_sem_ver'] = (datetime.now() - pd.to_datetime(df['ultima_revisao'])).dt.days
        df['dias_sem_ver'] = df['dias_sem_ver'].fillna(999)
        # Sort by worst performance and highest days
        critico = df[df['questoes_realizadas'] > 0].sort_values(by=['percentual_acertos', 'dias_sem_ver'], ascending=[True, False]).head(8)
        
        for _, r in critico.iterrows():
            st.markdown(f"""
            <div style="background: #11161D; border-left: 3px solid #D9534F; border-radius: 6px; padding: 10px; margin-bottom: 8px;">
                <div style="font-size: 0.85rem; color: #A8B3C2;">{r['area']}</div>
                <div style="font-weight: 600; color: #F3F7FC;">{r['tema']}</div>
                <div style="font-size: 0.8rem; color: #D9A441;">Acertos: {r['percentual_acertos']:.1f}% | Há {int(r['dias_sem_ver'])} dias</div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.info("Banco de dados vazio ou inicializando.")
