import streamlit as st
import random
import json
from pathlib import Path
from app.utils.parser import parse_caderno_erros, read_md
from app.utils.flashcard_builder import load_or_generate_flashcards, CACHE_PATH

ROOT = Path(__file__).parent.parent.parent
CADERNO_PATH = ROOT / "caderno_erros.md"

st.set_page_config(page_title="Flashcards IPUB", layout="centered")

# ── CSS CUSTOMIZADO (v3.0 Ultra-Clean) ──────────────────────────────────────
st.markdown("""
<style>
.stAlert { border-radius: 12px; border: none; }
.contexto-clinico { color: #888; font-style: italic; font-size: 0.95rem; margin-bottom: 0.8rem; }
.pergunta-cirurgica { font-size: 1.35rem; font-weight: 600; line-height: 1.4; color: #FFF; margin-bottom: 1.5rem; }
.block-container { max-width: 700px; padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

st.title("🧠 Flashcards")

# ── Sidebar: Filtros e Inteligência ──────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configurar")
    
    # Busca dados reais do caderno
    entries_raw = parse_caderno_erros()
    # Carrega flashcards (com cache)
    all_cards = load_or_generate_flashcards(entries_raw)
    
    areas_list = sorted(set(c.get('area', 'Geral') for c in all_cards if c.get('area')))
    area_filtro = st.multiselect("Filtrar por Área", options=areas_list, default=areas_list)
    embaralhar = st.toggle("Embaralhar", value=True)
    
    st.divider()
    st.caption("Controle LLM (Claude 3.5)")
    
    if st.button("➕ Gerar novos cards", use_container_width=True):
        st.cache_data.clear()
        with st.spinner("Gerando lacunas..."):
            load_or_generate_flashcards(entries_raw, force_regen=False)
        st.success("Novos cards gerados!")
        # Reseta ordem para evitar crash de índice
        for key in ['fc_order', 'fc_idx', 'fc_verso']:
            st.session_state.pop(key, None)
        st.rerun()
    
    if st.button("🔄 Regenerar tudo", use_container_width=True):
        st.cache_data.clear()
        with st.spinner("Refazendo base completa..."):
            load_or_generate_flashcards(entries_raw, force_regen=True)
        st.success("Base MedHub regenerada.")
        for key in ['fc_order', 'fc_idx', 'fc_verso']:
            st.session_state.pop(key, None)
        st.rerun()

# ── Filtragem ───────────────────────────────────────────────────────────────
filtered = [c for c in all_cards if c.get('area') in area_filtro]

if not filtered:
    st.info("Nenhum flashcard disponível para os filtros selecionados.")
    st.stop()

# ── Ordem e Estado (FIX SHUFFLE CRASH) ──────────────────────────────────────
# Sempre usamos o fc_order para referenciar o índice na lista 'filtered'
if 'fc_order' not in st.session_state or len(st.session_state.fc_order) != len(filtered):
    order = list(range(len(filtered)))
    if embaralhar:
        random.shuffle(order)
    st.session_state.fc_order = order
    st.session_state.fc_idx = 0
    st.session_state.fc_verso = False

if 'fc_idx' not in st.session_state: st.session_state.fc_idx = 0
if 'fc_verso' not in st.session_state: st.session_state.fc_verso = False

# Proteção contra overflow
st.session_state.fc_idx %= len(filtered)
idx_ref = st.session_state.fc_order[st.session_state.fc_idx]
card = filtered[idx_ref]
total = len(filtered)

# ── UI Player ───────────────────────────────────────────────────────────────
st.caption(f"{card.get('area','')} › {card.get('tema','')}  ·  Erro #{card.get('erro_origem','')}")
st.progress((st.session_state.fc_idx + 1) / total, text=f"Card {st.session_state.fc_idx + 1} de {total}")

st.divider()

if not st.session_state.fc_verso:
    # FRENTE
    if card.get('frente_contexto'):
        st.markdown(f'<p class="contexto-clinico">{card["frente_contexto"]}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="pergunta-cirurgica">{card["frente_pergunta"]}</p>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("Revelar resposta →", use_container_width=True, type="primary"):
        st.session_state.fc_verso = True
        st.rerun()
else:
    # VERSO
    st.markdown(f"**{card['verso_resposta']}**")
    st.markdown("<br>", unsafe_allow_html=True)
    
    if card.get('verso_regra_mestre'):
        st.info(f"🧠 **Regra mestre:** {card['verso_regra_mestre']}")
    if card.get('verso_armadilha'):
        st.warning(f"⚠️ **Gatilho examinador:** {card['verso_armadilha']}")
        
    st.divider()
    
    # Navegação Pura (FSRS backend only)
    c1, c2, c3 = st.columns(3)
    
    def _next():
        st.session_state.fc_idx = (st.session_state.fc_idx + 1) % total
        st.session_state.fc_verso = False
        st.rerun()
        
    def _prev():
        st.session_state.fc_idx = (st.session_state.fc_idx - 1) % total
        st.session_state.fc_verso = False
        st.rerun()

    with c1:
        if st.button("← Voltar", use_container_width=True): _prev()
    with c2:
        if st.button("Próximo →", use_container_width=True, type="primary"): _next()
    with c3:
        if st.button("⏭️ Pular", use_container_width=True): _next()
