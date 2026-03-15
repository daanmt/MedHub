from app.utils.styles import flashcard_front, flashcard_back
import streamlit as st
import random
import os
from pathlib import Path
from app.utils.parser import parse_caderno_erros
from app.utils.flashcard_builder import load_or_generate_flashcards

st.title("🧠 Player de Flashcards")

# ── Sidebar: Governança e Filtros ──────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configurar")
    entries_raw = parse_caderno_erros()
    all_cards = load_or_generate_flashcards(entries_raw)
    
    areas_list = sorted(set(c.get('area', 'Geral') for c in all_cards if c.get('area')))
    area_filtro = st.multiselect("Filtrar por Área", options=areas_list, default=areas_list)
    embaralhar = st.toggle("Embaralhar", value=True)
    
    st.divider()
    if st.button("➕ Gerar novos cards", use_container_width=True):
        st.cache_data.clear()
        with st.spinner("Gerando lacunas..."):
            load_or_generate_flashcards(entries_raw, force_regen=False)
        st.success("Novos cards gerados!")
        for key in ['fc_order', 'fc_idx', 'fc_verso']:
            st.session_state.pop(key, None)
        st.rerun()

# ── Lógica de Filtro e Estado ────────────────────────────────────────────────
filtered = [c for c in all_cards if c.get('area') in area_filtro]
if not filtered:
    st.info("Nenhum flashcard disponível para os filtros selecionados.")
    st.stop()

if 'fc_order' not in st.session_state or len(st.session_state.fc_order) != len(filtered):
    order = list(range(len(filtered)))
    if embaralhar: random.shuffle(order)
    st.session_state.fc_order = order
    st.session_state.fc_idx = 0
    st.session_state.fc_verso = False

st.session_state.fc_idx %= len(filtered)
idx_ref = st.session_state.fc_order[st.session_state.fc_idx]
card = filtered[idx_ref]
total = len(filtered)

# ── UI Player (Flat Layout) ──────────────────────────────────────────────────
st.progress((st.session_state.fc_idx + 1) / total, text=f"Progresso: {st.session_state.fc_idx + 1} de {total}")

def _advance():
    st.session_state.fc_idx = (st.session_state.fc_idx + 1) % total
    st.session_state.fc_verso = False
    st.rerun()

if not st.session_state.fc_verso:
    # FRENTE
    flashcard_front(
        category=f"{card.get('area','')} › {card.get('tema','')}  ·  Erro #{card.get('erro_origem','')}",
        question=card["frente_pergunta"]
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Revelar resposta →", use_container_width=True, type="primary"):
        st.session_state.fc_verso = True
        st.rerun()
else:
    # VERSO
    flashcard_back(
        answer=card['verso_resposta'],
        master_rule=card.get('verso_regra_mestre'),
        trap=card.get('verso_armadilha')
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Hybrid FSRS Buttons (Standard Streamlit + CSS Targeting in styles.py)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Novamente", use_container_width=True, key="fsrs_again"): _advance()
    with col2:
        if st.button("Difícil", use_container_width=True, key="fsrs_hard"): _advance()
    with col3:
        if st.button("Bom", use_container_width=True, key="fsrs_good"): _advance()
    with col4:
        if st.button("Fácil", use_container_width=True, key="fsrs_easy"): _advance()

st.divider()
with st.container():
    c_prev, c_skip = st.columns([1, 1])
    with c_prev:
        if st.button("← Voltar anterior", use_container_width=True):
            st.session_state.fc_idx = (st.session_state.fc_idx - 1) % total
            st.session_state.fc_verso = False
            st.rerun()
    with c_skip:
        if st.button("Pular card ⏭️", use_container_width=True): _advance()
