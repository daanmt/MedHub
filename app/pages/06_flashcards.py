import streamlit as st
import json
import random
from pathlib import Path
from app.utils.parser import parse_caderno_erros, read_md
from app.utils.flashcard_builder import load_or_generate_flashcards, CACHE_PATH

ROOT = Path(__file__).parent.parent.parent
CADERNO_PATH = ROOT / "caderno_erros.md"

st.set_page_config(page_title="Flashcards IPUB", layout="centered")

# ── CSS CUSTOMIZADO (v2.0 Polish) ───────────────────────────────────────────
st.markdown("""
<style>
/* Caixas de destaque mais leves no dark mode */
.stAlert {
    border-radius: 12px;
    border-left-width: 6px;
    border-top: none;
    border-right: none;
    border-bottom: none;
}
/* Estilo para o Contexto */
.contexto-clinico {
    color: #888;
    font-style: italic;
    font-size: 0.95rem;
    margin-bottom: 1rem;
}
/* Estilo para a Pergunta */
.pergunta-cirurgica {
    font-size: 1.4rem;
    font-weight: 600;
    line-height: 1.4;
    color: #FFF;
    margin-bottom: 2rem;
}
/* Limita largura para foco */
.block-container { max-width: 700px; padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
st.title("🧠 Estúdio de Flashcards")

# ── Filtros de sessão (sidebar) ──────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configurar Sessão")
    
    # Busca dados reais do caderno para coletar áreas
    entries_raw = parse_caderno_erros()
    areas_list = sorted(set(e.get('area', 'Geral') for e in entries_raw))
    
    area_filtro = st.multiselect("Filtrar por Área", options=areas_list, default=areas_list)
    tipo_filtro = st.multiselect(
        "Tipo de Flashcard",
        options=["elo_quebrado", "armadilha"],
        default=["elo_quebrado", "armadilha"],
        format_func=lambda x: {"elo_quebrado": "🔗 Elo Quebrado", "armadilha": "⚠️ Armadilha"}[x]
    )
    embaralhar = st.toggle("Embaralhar ordem", value=True)
    
    st.divider()
    st.caption("Inteligência Artificial (v5.0)")
    if st.button("➕ Gerar cards para novos erros", use_container_width=True):
        with st.spinner("Conectando ao Claude..."):
            load_or_generate_flashcards(entries_raw, force_regen=False)
        st.success("Novos cards gerados!")
        st.rerun()
    
    if st.button("🔄 Regenerar base completa", use_container_width=True):
        with st.spinner("Refazendo toda a base..."):
            load_or_generate_flashcards(entries_raw, force_regen=True)
        st.success("Base regenerada com sucesso.")
        st.rerun()

# ── Carregamento e Filtragem ────────────────────────────────────────────────
# Prioriza Cache do Builder
flashcards_raw = []
if CACHE_PATH.exists():
    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        flashcards_raw = json.load(f)

# Filtra conforme sidebar
filtered = [
    c for c in flashcards_raw
    if c.get('area') in area_filtro
    and (c.get('tipo') in tipo_filtro or not c.get('tipo'))
]

if not filtered:
    st.info("Nenhum flashcard encontrado para os filtros selecionados.")
    st.stop()

# Gerenciamento de ordem (Shuffle)
if embaralhar:
    if 'fc_shuffled_ids' not in st.session_state or st.session_state.get('last_filter') != str(area_filtro) + str(tipo_filtro):
        random.shuffle(filtered)
        st.session_state.fc_shuffled_ids = [c['id'] for c in filtered]
        st.session_state.last_filter = str(area_filtro) + str(tipo_filtro)
    
    # Reordena o original conforme o shuffle guardado
    id_map = {c['id']: c for c in filtered}
    filtered = [id_map[cid] for cid in st.session_state.fc_shuffled_ids if cid in id_map]

# ── Estado da Sessão ────────────────────────────────────────────────────────
if 'fc_idx' not in st.session_state:
    st.session_state.fc_idx = 0
if 'fc_verso' not in st.session_state:
    st.session_state.fc_verso = False
if 'fc_session_log' not in st.session_state:
    st.session_state.fc_session_log = []

# Ajusta index se filtros reduziram o dataset
idx = min(st.session_state.fc_idx, len(filtered) - 1)
card = filtered[idx]
total = len(filtered)

# ── Métricas da Sessão ──────────────────────────────────────────────────────
acertos = sum(1 for l in st.session_state.fc_session_log if l['resultado'] == 'acertou')
revistos = len(st.session_state.fc_session_log)

col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric("Card", f"{idx + 1} / {total}")
col_m2.metric("Acertos", acertos)
col_m3.metric("Taxa", f"{int(acertos/revistos*100)}%" if revistos else "—")

st.progress(min((idx + 1) / total, 1.0))

# ── Breadcrumb ────────────────────────────────────────────────────────────────
tipo_ico = {"elo_quebrado": "🔗", "armadilha": "⚠️"}.get(card.get('tipo', 'elo_quebrado'), "📋")
tipo_txt = card.get('tipo','elo_quebrado').replace('_', ' ').capitalize()
st.caption(f"{card.get('area','')} › {card.get('tema','')}  ·  {tipo_ico} {tipo_txt}  ·  Erro #{card.get('erro_origem','')}")

st.divider()

# ── FRENTE ───────────────────────────────────────────────────────────────────
if not st.session_state.fc_verso:
    with st.container():
        if card.get('frente_contexto'):
            st.markdown(f'<p class="contexto-clinico">{card["frente_contexto"]}</p>', unsafe_allow_html=True)
        
        st.markdown(f'<p class="pergunta-cirurgica">{card["frente_pergunta"]}</p>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Revelar resposta →", use_container_width=True, type="primary"):
            st.session_state.fc_verso = True
            st.rerun()

# ── VERSO ─────────────────────────────────────────────────────────────────────
else:
    with st.container():
        # Resposta sem o ### enorme (v2.0 Polish)
        st.markdown(f"**{card['verso_resposta']}**")
        st.markdown("<br>", unsafe_allow_html=True)

        if card.get('verso_regra_mestre'):
            st.info(f"**Regra mestre:** {card['verso_regra_mestre']}", icon="🧠")

        if card.get('verso_armadilha'):
            st.warning(f"**Gatilho do examinador:** {card['verso_armadilha']}", icon="⚠️")

        st.divider()
        st.markdown("**Como foi o seu desempenho?**")
        
        c1, c2, c3 = st.columns(3)
        
        def _advance(resultado: str, card_id: str, error_id: int):
            from app.utils.db import record_review, get_connection
            
            # Bridge para FSRS (se disponível)
            try:
                conn = get_connection()
                c = conn.cursor()
                c.execute("SELECT id FROM flashcards WHERE questao_id = ?", (error_id,))
                res = c.fetchone()
                conn.close()
                if res: record_review(res[0], {"errou": 1, "dificil": 2, "acertou": 3}[resultado])
            except:
                pass

            st.session_state.fc_session_log.append({'card_id': card_id, 'resultado': resultado})
            st.session_state.fc_idx += 1
            st.session_state.fc_verso = False
            
            if st.session_state.fc_idx >= len(filtered):
                st.session_state.fc_idx = 0
                st.session_state.fc_shuffled_ids = None # Força novo shuffle se quiser
            st.rerun()

        with c1:
            if st.button("Errei 🔴", use_container_width=True):
                _advance('errou', card['id'], card.get('erro_origem', 0))
        with c2:
            if st.button("Difícil 🟠", use_container_width=True):
                _advance('dificil', card['id'], card.get('erro_origem', 0))
        with c3:
            if st.button("Acertei! 🟢", use_container_width=True):
                _advance('acertou', card['id'], card.get('erro_origem', 0))
