from app.utils.styles import flashcard_front, flashcard_back
import streamlit as st
import random
import sqlite3
import os
from app.utils.db import record_cache_review, get_cache_due_count

st.title("🧠 Player de Flashcards")

DB_PATH = 'ipub.db'

@st.cache_data(ttl=60)
def load_flashcards_from_db():
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Pega os cards que estão vencidos ou que nunca foram vistos (state=0)
    cursor.execute('''
    SELECT f.id, f.tipo, f.frente, f.verso, f.questao_id, t.area, t.tema, c.due, c.state
    FROM flashcards f
    JOIN taxonomia_cronograma t ON f.tema_id = t.id
    JOIN fsrs_cards c ON f.id = c.card_id
    WHERE c.due <= datetime('now') OR c.state = 0
    ''')
    rows = cursor.fetchall()
    cards = []
    for row in rows:
        cards.append({
            'card_id': row[0],
            'tipo': row[1],
            'frente_pergunta': row[2],
            'verso_resposta': row[3],
            'erro_origem': row[4],
            'area': row[5],
            'tema': row[6],
            'due': row[7],
            'state': row[8],
        })
    conn.close()
    return cards

# ── Sidebar: Governança e Filtros ──────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configurar")
    all_cards = load_flashcards_from_db()
    
    areas_list = sorted(set(c.get('area', 'Geral') for c in all_cards if c.get('area')))
    area_filtro = st.multiselect("Filtrar por Área", options=areas_list, default=areas_list)
    embaralhar = st.toggle("Embaralhar", value=True)
    
    due_count = len([c for c in all_cards if c['state'] != 0])
    new_count = len([c for c in all_cards if c['state'] == 0])
    
    st.markdown(f'<div style="color:#D9A441; font-size:0.82rem; margin-bottom:4px;">⏰ {due_count} card(s) para revisão</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="color:#1FA971; font-size:0.82rem; margin-bottom:8px;">✨ {new_count} card(s) novos</div>', unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔄 Sincronizar FSRS", width='stretch'):
        st.cache_data.clear()
        for key in ['fc_order', 'fc_idx', 'fc_verso']:
            st.session_state.pop(key, None)
        st.rerun()

# ── Lógica de Filtro e Estado ────────────────────────────────────────────────
filtered = [c for c in all_cards if c.get('area') in area_filtro]
if not filtered:
    st.info("Nenhum flashcard vencido ou novo disponível para os filtros selecionados! Você está em dia! 🎉")
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
    """Avança para o próximo card, gravando rating FSRS no banco de dados."""
    if rating > 0:
        card_id = card.get('card_id')
        if card_id is not None:
            try:
                # O script de record_cache_review precisa ser adaptado ou podemos apenas dar update direto no banco.
                # Como app.utils.db.record_cache_review foi feito pra JSON, vamos usar sqlite local para rating simplificado FSRS.
                conn = sqlite3.connect('ipub.db')
                c = conn.cursor()
                # Atualizando data dependendo do rating (simplificado FSRS)
                dias_add = {1: 0, 2: 1, 3: 3, 4: 7}[rating]
                c.execute(f"UPDATE fsrs_cards SET state=2, due=datetime('now', '+{dias_add} days') WHERE card_id=?", (card_id,))
                
                # Inserindo no RevLog
                c.execute("INSERT INTO fsrs_revlog (card_id, rating, state) VALUES (?, ?, ?)", (card_id, rating, 2))
                conn.commit()
                conn.close()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")
                
    st.session_state.fc_idx = (st.session_state.fc_idx + 1) % total
    st.session_state.fc_verso = False
    
    # Se chegamos ao fim, recarrega
    if st.session_state.fc_idx == 0:
        st.cache_data.clear()
        st.session_state.pop('fc_order', None)
        
    st.rerun()

if not st.session_state.fc_verso:
    # FRENTE
    flashcard_front(
        category=f"{card.get('area')} › {card.get('tema')}",
        question=card.get("frente_pergunta", ""),
        context=""
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Revelar resposta →", width='stretch', type="primary"):
        st.session_state.fc_verso = True
        st.rerun()
else:
    # VERSO
    flashcard_back(
        answer=card.get('verso_resposta', ''),
        master_rule=None,
        trap=None
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botões FSRS — rating persiste no SQLite local (ipub.db)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Novamente", width='stretch', key="fsrs_again"): _advance(rating=1)
    with col2:
        if st.button("Difícil (1d)", width='stretch', key="fsrs_hard"): _advance(rating=2)
    with col3:
        if st.button("Bom (3d)", width='stretch', key="fsrs_good"): _advance(rating=3)
    with col4:
        if st.button("Fácil (7d)", width='stretch', key="fsrs_easy"): _advance(rating=4)

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
