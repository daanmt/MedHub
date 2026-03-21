import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# Estilização
st.set_page_config(page_title="Cronograma Inteligente", page_icon="📅", layout="wide")
st.title("📅 Cronograma e Curva de Esquecimento")

DB_PATH = 'ipub.db'

def carregar_dados_cronograma():
    if not os.path.exists(DB_PATH):
        return pd.DataFrame()
        
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        area AS Área,
        tema AS Tema,
        questoes_realizadas AS Feitas,
        questoes_acertadas AS Acertos,
        percentual_acertos AS '% Acerto',
        ultima_revisao AS 'Última Vez'
    FROM taxonomia_cronograma
    WHERE questoes_realizadas > 0
    ORDER BY percentual_acertos ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

df = carregar_dados_cronograma()

if df.empty:
    st.warning("Nenhum dado de cronograma encontrado. Rode as questões no Estratégia Med e atualize seu banco.")
    st.stop()

# Converter datas para cálculo de "Dias desde a última revisão"
# Tratando casos nulos ou datas inválidas exportadas pelo csv
hoje = datetime.now()
df['Última Vez'] = pd.to_datetime(df['Última Vez'], errors='coerce')
df['Dias Sem Rever'] = (hoje - df['Última Vez']).dt.days

# Lidando com NaNs lógicos (planilha do Sheets não preencheu última revisão)
df['Dias Sem Rever'] = df['Dias Sem Rever'].fillna(999).astype(int)

# ── Regras de Negócio: O que precisa de revisão urgente? ──
# 1. Performance menor que 70% OU Dias sem rever > 30 (Curva Vermelha)
mask_critico = (df['% Acerto'] < 70) | (df['Dias Sem Rever'] > 30)
# 2. Performance > 70% e Visto há menos de 30 dias (OK)
mask_ok = (df['% Acerto'] >= 80) & (df['Dias Sem Rever'] <= 15)
# 3. O resto é Atenção
mask_atencao = ~(mask_critico | mask_ok)

df_critico = df[mask_critico].copy()
df_atencao = df[mask_atencao].copy()
df_ok = df[mask_ok].copy()

# ── Métricas Superiores ──
col1, col2, col3 = st.columns(3)
col1.metric("🔴 Em Risco (Alta Prioridade)", len(df_critico))
col2.metric("🟡 Manutenção (Atenção)", len(df_atencao))
col3.metric("🟢 Zona de Domínio", len(df_ok))

st.divider()

# ── Exibição Visual ──
st.subheader("🔴 Foco Crítico (Revisão Imediata)")
st.caption("Matérias com aproveitamento baixo (<70%) ou não revisadas há mais de 1 mês. Gere flashcards ativos com a IA ou refaça questões.")

# Formatação visual amigável do DataFrame
def colorir_tabela(val):
    if isinstance(val, (int, float)):
        if val < 70:
            return 'color: #ef4444;'
        elif val >= 80:
            return 'color: #22c55e;'
    return ''

if not df_critico.empty:
    st.dataframe(df_critico.style.applymap(colorir_tabela, subset=['% Acerto']), use_container_width=True)
else:
    st.success("Tudo em dia! Nenhum tema crítico.")

st.subheader("🟡 Zonas de Atenção / Revisão Breve")
if not df_atencao.empty:
    st.dataframe(df_atencao.style.applymap(colorir_tabela, subset=['% Acerto']), use_container_width=True)

st.subheader("🟢 Temas Dominados")
st.caption("Matérias recentes e com alta perfomance.")
with st.expander("Ver lista de temas dominados"):
    if not df_ok.empty:
        st.dataframe(df_ok.style.applymap(colorir_tabela, subset=['% Acerto']), use_container_width=True)

# ── Call To Action para a Geração de Flashcards ──
st.divider()
st.subheader("🤖 Tutor Baseado em Dados")
st.markdown("Identificamos os pontos críticos da sua curva do esquecimento. Solicite à IA para rodar o comando `/gsd-gerar-reforco` apontando para um dos temas críticos acima, e geraremos flashcards dinâmicos baseados no seu resumo local via RAG para destruir a fraqueza.")
