from app.utils.styles import flashcard_front, flashcard_back
import streamlit as st
import random
from app.utils.parser import parse_caderno_erros
from app.utils.flashcard_builder import load_or_generate_flashcards
from app.utils.db import record_cache_review, get_cache_due_count

st.title("🧠 Player de Flashcards")

# ── Sidebar: Governança e Filtros ──────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configurar")
    entries_raw = parse_caderno_erros()
    all_cards = load_or_generate_flashcards(entries_raw)
    
    areas_list = sorted(set(c.get('area', 'Geral') for c in all_cards if c.get('area')))
    area_filtro = st.multiselect("Filtrar por Área", options=areas_list, default=areas_list)
    embaralhar = st.toggle("Embaralhar", value=True)
    
    due_count = get_cache_due_count()
    if due_count > 0:
        st.markdown(f'<div style="color:#D9A441; font-size:0.82rem; margin-bottom:8px;">⏰ {due_count} card(s) vencido(s) para revisão</div>', unsafe_allow_html=True)

    st.divider()
    if st.button("➕ Gerar novos cards", width='stretch'):
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

def _advance(rating: int = 0):
    """Avança para o próximo card, opcionalmente gravando rating FSRS."""
    if rating > 0:
        erro_origem = card.get('erro_origem')
        if erro_origem is not None:
            try:
                new_state = record_cache_review(int(erro_origem), rating)
                st.session_state.fc_last_scheduled = new_state.get('scheduled_days', 0)
            except Exception:
                pass
    st.session_state.fc_idx = (st.session_state.fc_idx + 1) % total
    st.session_state.fc_verso = False
    st.rerun()

if not st.session_state.fc_verso:
    # FRENTE
    flashcard_front(
        category=f"{card.get('area','')} › {card.get('tema','')}  ·  Erro #{card.get('erro_origem','')}",
        question=card.get("frente_pergunta", ""),
        context=card.get("frente_contexto", "")
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Revelar resposta →", width='stretch', type="primary"):
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
    
    # Botões FSRS — rating persiste no SQLite local (ipub.db)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Novamente", width='stretch', key="fsrs_again"): _advance(rating=1)
    with col2:
        if st.button("Difícil", width='stretch', key="fsrs_hard"): _advance(rating=2)
    with col3:
        if st.button("Bom", width='stretch', key="fsrs_good"): _advance(rating=3)
    with col4:
        if st.button("Fácil", width='stretch', key="fsrs_easy"): _advance(rating=4)

st.divider()
with st.container():
    c_prev, c_skip = st.columns([1, 1])
    with c_prev:
        if st.button("← Voltar anterior", width='stretch'):
            st.session_state.fc_idx = (st.session_state.fc_idx - 1) % total
            st.session_state.fc_verso = False
            st.rerun()
    with c_skip:
        if st.button("Pular card ⏭️", width='stretch'): _advance(rating=0)
