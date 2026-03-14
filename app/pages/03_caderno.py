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

# --- BLOCO 2: PLAYER DE FLASHCARDS (ANKI UI) ---
st.subheader("🧠 Estúdio de Flashcards (Ativo)")

# Inicializa estado da sessão de flashcards
if 'flashcard_mode' not in st.session_state:
    st.session_state.flashcard_mode = 'front' # 'front' ou 'back'
if 'current_card' not in st.session_state:
    st.session_state.current_card = get_next_due_card()

def next_card():
    st.session_state.current_card = get_next_due_card()
    st.session_state.flashcard_mode = 'front'

card = st.session_state.current_card

if card:
    total = due_count if due_count > 0 else 1 # Fallback para evitar divisão por zero
    idx = st.session_state.get('fc_idx', 0)
    
    # Header de contexto e progresso
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown(f"**{card['area']} › {card['tema']}**")
    with col_t2:
        st.caption(f"Card {idx+1}/{due_count}")
    
    st.progress(min((idx + 1) / total, 1.0))

    # --- FRENTE ---
    if st.session_state.flashcard_mode == 'front':
        with st.container(border=True):
            tipo_label = {"elo_quebrado": "🔗 Elo Quebrado", "armadilha": "⚠️ Armadilha"}.get(
                card.get('tipo', 'elo_quebrado'), "📋"
            )
            st.caption(f"{tipo_label} · Simulado IPUB")
            st.divider()
            st.markdown(card['frente'])
            
        if st.button("Revelar Resposta 💡", use_container_width=True, type="primary"):
            st.session_state.flashcard_mode = 'back'
            st.rerun()
            
    # --- VERSO ---
    else:
        with st.container(border=True):
            st.markdown(card['verso'])
            
            # Tenta extrair regra mestre se não estiver no verso formatado
            # (No novo motor v4.0 já está no verso, mas mantemos redundância visual se necessário)
            
        st.write("---")
        st.caption("Como foi o seu desempenho?")
        r_col1, r_col2, r_col3 = st.columns(3)
        
        with r_col1:
            if st.button("Errei / Revisar 🔴", use_container_width=True):
                record_review(card['flashcard_id'], 1)
                next_card()
                st.rerun()
        with r_col2:
            if st.button("Difícil 🟠", use_container_width=True):
                record_review(card['flashcard_id'], 2)
                next_card()
                st.rerun()
        with r_col3:
            if st.button("Acertei! 🟢", use_container_width=True):
                record_review(card['flashcard_id'], 3)
                next_card()
                st.rerun()
else:
    st.info("Nenhum flashcard pendente para revisão no momento. Ótimo trabalho!")

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
