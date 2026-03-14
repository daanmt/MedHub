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

# --- BLOCO 2: EXPLORADOR DE LACUNAS (MODO CONSULTA) ---
st.subheader("📖 Explorador de Lacunas")

# Filtros na sidebar
from app.utils.parser import parse_caderno_erros
entries = parse_caderno_erros()

with st.sidebar:
    st.divider()
    st.markdown("### Filtros do Caderno")
    areas_disp = sorted(set(e.get('area', 'Geral') for e in entries))
    area_sel = st.multiselect("Filtrar por Área", areas_disp)
    busca = st.text_input("Buscar termo", placeholder="Ex: Púrura, Vaso, Dose...")

# Aplicar filtros
filtered = entries
if area_sel:
    filtered = [e for e in filtered if e.get('area') in area_sel]
if busca:
    busca_low = busca.lower()
    filtered = [e for e in filtered if busca_low in str(e).lower()]

if filtered:
    st.caption(f"Exibindo {len(filtered)} erros encontrados.")
    for entry in filtered:
        # Título do expander: Erro #N — Área › Tema
        with st.expander(f"Erro #{entry.get('numero', '?')} — {entry.get('area', 'Geral')} › {entry.get('tema', 'Miscelânea')}"):
            if entry.get('enunciado'):
                st.markdown(f"**Caso:** {entry['enunciado']}")
                st.divider()
            
            st.error(f"**Elo Quebrado:** {entry.get('elo_quebrado', 'N/A')}")
            st.info(f"**Conceito de Ouro:** {entry.get('conceito_de_ouro', 'N/A')}", icon="🧠")
            
            if entry.get('armadilha_prova') and entry.get('armadilha_prova') != "N/A":
                st.warning(f"**Gatilho do Examinador:** {entry['armadilha_prova']}", icon="⚠️")
            
            st.caption(f"Gabarito: {entry.get('alternativa_correta', 'N/A')} | Tipo: {entry.get('tipo_erro', 'N/A')}")
else:
    st.info("Nenhum erro encontrado com os filtros aplicados.")

st.divider()

st.divider()
