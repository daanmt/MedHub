import streamlit as st
import sqlite3
import requests
import json
import random
import os

st.set_page_config(page_title="Simulados RAG", page_icon="🎯", layout="wide")

DB_PATH = 'ipub.db'

# Carrega os temas críticos do DB
@st.cache_data(ttl=60)
def get_critical_themes():
    if not os.path.exists(DB_PATH): return []
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT tema, area, percentual_acertos FROM taxonomia_cronograma WHERE percentual_acertos < 80 ORDER BY percentual_acertos ASC LIMIT 10")
        return [{"tema": r[0], "area": r[1], "perf": r[2]} for r in c.fetchall()]
    except:
        return []

st.title("🎯 Simulados Inteligentes (Fase 4)")
st.markdown('<p style="color: #A8B3C2; margin-top: -15px;">Micro-testes gerados sob demanda pelo seu Tutor AI baseados nas suas fraquezas.</p>', unsafe_allow_html=True)

themes = get_critical_themes()

if not themes:
    st.success("Não há temas críticos com performance abaixo de 80%. Você está dominando o conteúdo!")
    st.stop()

st.sidebar.header("⚙️ Configurar Simulado")
selected_theme = st.sidebar.selectbox("Foco do Simulado (Prioridade)", [f"{t['area']} › {t['tema']} ({t['perf']:.1f}%)" for t in themes])

# Pega o string limpo
clean_theme = selected_theme.split("›")[1].split("(")[0].strip()

# Inicializa sessão para a Questão Corrente
if 'simulado_q' not in st.session_state:
    st.session_state.simulado_q = None
    st.session_state.simulado_ans = False

def gerar_questao(tema):
    prompt = f"""
    Atue como um examinador de Residência Médica (Revalida/SUS).
    Crie UMA questão de múltipla escolha DÍFICIL focada APENAS no tema: {tema}.
    A questão deve ter um caso clínico enxuto e 4 alternativas (A, B, C, D).
    Devolva EXATAMENTE um JSON com as seguintes chaves (sem markdown, raw JSON apenas):
    {{
      "enunciado": "Caso clínico aqui...",
      "A": "opção 1",
      "B": "opção 2",
      "C": "opção 3",
      "D": "opção 4",
      "correta": "A",
      "explicacao": "Por que a resposta é certa e porque as outras são armadilhas..."
    }}
    """
    try:
        # Tenta usar Ollama local
        res = requests.post("http://localhost:11434/api/generate", json={
            "model": "llama3", # Ajuste baseado no modelo que o usuário tiver baixado (ou nomic)
            "system": "Retorne apenas o JSON. Seja conciso.",
            "prompt": prompt,
            "stream": False
        }, timeout=30)
        
        if res.status_code == 200:
            text = res.json().get('response', '')
            # Clean possible markdown wrap
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            return json.loads(text.strip())
    except Exception as e:
        return {"erro": str(e)}
    return None

if st.button("🚀 Gerar Questão de " + clean_theme, type="primary"):
    with st.spinner("O Tutor está redigindo a questão clínica baseada nas suas fraquezas..."):
        q = gerar_questao(clean_theme)
        if q and "erro" not in q:
            st.session_state.simulado_q = q
            st.session_state.simulado_ans = False
        else:
            st.error(f"Erro ao conectar com o Tutor AI Local (Ollama) ou formato inválido.\nCertifique-se de que o Ollama está rodando o modelo 'llama3' (ou similar).\nLog: {q.get('erro', 'Desconhecido') if q else 'Sem resposta'}")

st.divider()

if st.session_state.simulado_q and "erro" not in st.session_state.simulado_q:
    q = st.session_state.simulado_q
    
    st.markdown(f'<div style="background:#11161D; border:1px solid #202A36; padding:20px; border-radius:12px; font-size:1.1rem; border-left: 4px solid #2F6BFF;">{q.get("enunciado", "")}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    op_a = st.button(f"A) {q.get('A', '')}", use_container_width=True)
    op_b = st.button(f"B) {q.get('B', '')}", use_container_width=True)
    op_c = st.button(f"C) {q.get('C', '')}", use_container_width=True)
    op_d = st.button(f"D) {q.get('D', '')}", use_container_width=True)
    
    ans = None
    if op_a: ans = "A"
    if op_b: ans = "B"
    if op_c: ans = "C"
    if op_d: ans = "D"
    
    if ans:
        st.session_state.simulado_ans = True
        if ans == q.get('correta', ''):
            st.success(f"Correto! Resposta {ans}.")
        else:
            st.error(f"Incorreto. Você marcou {ans}, mas a correta era {q.get('correta', '')}.")
            
    if st.session_state.simulado_ans:
        with st.expander("📖 Ver Explicação do Tutor", expanded=True):
            st.info(q.get('explicacao', 'Sem explicação gerada.'))
            st.caption("Anotações de fraqueza são logadas silenciosamente no banco.")
