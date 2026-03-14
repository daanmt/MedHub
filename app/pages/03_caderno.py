import streamlit as st
import pandas as pd
from datetime import datetime
from app.utils.db import (
    get_due_cards_count, 
    get_next_due_card, 
    record_review, 
    get_erros_resumidos,
    sync_git
)

# --- SIDEBAR: SINCRONIZAÇÃO ---
with st.sidebar:
    st.header("⚙️ Configurações")
    if st.button("🔄 Sincronizar com GitHub", use_container_width=True):
        with st.spinner("Sincronizando banco de dados..."):
            success, message = sync_git()
            if success:
                st.success(message)
            else:
                st.error(message)
    st.divider()
    st.caption("IPUB v2.0 | FSRS Spaced Repetition")

st.title("🗂️ Flashcards e Caderno de Erros")
st.markdown("Integração total do seu estudo ativo com o algoritmo de repetição espaçada FSRS.")

# --- BLOCO 1: HOT TOPICS (REVISÃO PENDENTE) ---
st.subheader("🔥 Hot Topics: Revisões para Hoje")
due_count = get_due_cards_count()

col_h1, col_h2 = st.columns([1, 3])
with col_h1:
    st.metric("Cards Vencidos", due_count, delta="Revisão Urgente" if due_count > 0 else "Em dia", delta_color="inverse" if due_count > 0 else "normal")
with col_h2:
    if due_count > 0:
        st.info(f"Você tem {due_count} flashcards que precisam ser revisados hoje para garantir a retenção de longo prazo.")
    else:
        st.success("Parabéns! Sua meta de revisões está em dia.")

st.divider()

# --- BLOCO 2: PLAYER DE FLASHCARDS (HYPER-FLASHCARDS v5.0) ---
st.subheader("🧠 Estúdio de Flashcards (Inteligente)")

# Lógica de carregamento de cards (Prioriza Cache JSON v5.0)
from app.utils.flashcard_builder import load_or_generate_flashcards, CACHE_PATH
from app.utils.parser import parse_caderno_erros
import json

# Busca erros brutos via PARSER (Zero DB Architecture)
errors_brutos = parse_caderno_erros()

# Painel de Controle
with st.expander("⚙️ Gerenciador de Inteligência", expanded=False):
    st.caption("Arquitetura v5.0: Geração via LLM Claude + Cache Local.")
    sc_col1, sc_col2 = st.columns(2)
    with sc_col1:
        if st.button("➕ Gerar novos flashcards", use_container_width=True):
            with st.spinner("Gerando lacunas..."):
                load_or_generate_flashcards(errors_brutos, force_regen=False)
                st.success("Novos cards gerados!")
                st.rerun()
    with sc_col2:
        if st.button("🔄 Regenerar Tudo (LLM)", use_container_width=True):
            with st.spinner("Refazendo base..."):
                load_or_generate_flashcards(errors_brutos, force_regen=True)
                st.success("Base v5.0 consolidada!")
                st.rerun()

# Carrega cards para o player
flashcards_raw = []
if CACHE_PATH.exists():
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        flashcards_raw = json.load(f)

# Inicializa estado
if 'fc_idx' not in st.session_state:
    st.session_state.fc_idx = 0
if 'flashcard_mode' not in st.session_state:
    st.session_state.flashcard_mode = 'front'

if flashcards_raw:
    total_raw = len(flashcards_raw)
    idx = st.session_state.fc_idx % total_raw
    card = flashcards_raw[idx]

    # Header de progresso
    st.markdown(f"**{card['area']} › {card['tema']}**")
    st.progress(min((idx + 1) / total_raw, 1.0))

    # --- FRENTE ---
    if st.session_state.flashcard_mode == 'front':
        with st.container(border=True):
            st.caption("🔗 ELO QUEBRADO · MODO RETENÇÃO")
            if card.get('frente_contexto'):
                st.markdown(f"**Contexto:** {card['frente_contexto']}")
            st.divider()
            st.markdown(f"### {card['frente_pergunta']}")
            
        if st.button("Revelar Resposta 💡", use_container_width=True, type="primary"):
            st.session_state.flashcard_mode = 'back'
            st.rerun()
            
    # --- VERSO ---
    else:
        with st.container(border=True):
            st.markdown(f"### {card['verso_resposta']}")
            st.info(f"**Regra Mestre:** {card['verso_regra_mestre']}", icon="🧠")
            if card.get('verso_armadilha'):
                st.warning(f"**Gatilho do Examinador:** {card['verso_armadilha']}", icon="⚠️")
            
        st.write("---")
        st.caption("Como foi o seu desempenho?")
        r_col1, r_col2, r_col3 = st.columns(3)
        
        from app.utils.db import record_review, get_connection
        
        def next_fc():
            st.session_state.fc_idx = (st.session_state.fc_idx + 1) % total_raw
            st.session_state.flashcard_mode = 'front'

        # Busca o ID do flashcard no banco (Bridge para Backend FSRS)
        def get_db_card_id(error_id):
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute("SELECT id FROM flashcards WHERE questao_id = ?", (error_id,))
                res = c.fetchone()
                conn.close()
                return res[0] if res else None
            except:
                return None

        db_card_id = get_db_card_id(card['erro_origem'])

        with r_col1:
            if st.button("Errei / Revisar 🔴", use_container_width=True):
                if db_card_id: record_review(db_card_id, 1)
                next_fc()
                st.rerun()
        with r_col2:
            if st.button("Difícil 🟠", use_container_width=True):
                if db_card_id: record_review(db_card_id, 2)
                next_fc()
                st.rerun()
        with r_col3:
            if st.button("Acertei! 🟢", use_container_width=True):
                if db_card_id: record_review(db_card_id, 3)
                next_fc()
                st.rerun()
else:
    st.info("Nenhum flashcard v5.0 encontrado. Clique em 'Gerar novos flashcards' acima para iniciar a inteligência artificial.")

st.divider()

# --- BLOCO 3: CADERNO DE ERROS 2.0 (MODO CONSULTA) ---
st.subheader("📖 Explorador de Lacunas (Consertando o Elo)")

df_erros = get_erros_resumidos()

if not df_erros.empty:
    temas_disponiveis = df_erros['TemaFull'].unique()
    selected_tema = st.selectbox("Selecione um Tema para revisar seus erros:", temas_disponiveis)
    
    if selected_tema:
        erros_tema = df_erros[df_erros['TemaFull'] == selected_tema]
        
        for idx, row in erros_tema.iterrows():
            with st.expander(f"Erro ID {row['id']} - {row['tipo_erro']}", expanded=True):
                st.error(f"**Elo Quebrado:** {row['elo_quebrado']}")
                st.warning(f"**Armadilha de Prova:** {row['armadilha_prova']}")
else:
    st.info("O seu caderno de erros está vazio.")

st.divider()
