import streamlit as st
from app.utils.parser import parse_caderno_erros, save_new_error

st.title("📖 Caderno de Erros")

# Fonte de Verdade (Zero-DB)
entries = parse_caderno_erros()

st.caption(f"{len(entries)} erros registrados para revisão.")

# ── Sidebar: Filtros ─────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Consultar")
    areas = sorted(set(e.get('area', 'Geral') for e in entries if e.get('area')))
    area_sel = st.multiselect("Filtrar por Área", areas)
    busca = st.text_input("Buscar termo", placeholder="Ex: Púrpura, Adenosina...")

# ── Formulário: Novo Erro ───────────────────────────────────────────────────
with st.expander("➕ Registrar novo erro", expanded=False):
    with st.form("form_novo_erro"):
        col1, col2 = st.columns(2)
        area_f = col1.text_input("Área (Ex: Pediatria)")
        tema_f = col1.text_input("Tema (Ex: Cardiologia)")
        titulo_f = col2.text_input("Título Curto do Erro")
        elo_f = col2.text_input("Elo Quebrado (Habilidade)")
        
        caso_f = st.text_area("Caso Clínico (Resumo)")
        expl_f = st.text_area("Explicação Correta / Regra Mestre")
        arm_f = st.text_input("Armadilha / Nuance (Opcional)")
        
        if st.form_submit_button("Salvar no Caderno"):
            if area_f and tema_f and titulo_f and elo_f and caso_f and expl_f:
                save_new_error(area_f, tema_f, titulo_f, elo_f, caso_f, expl_f, arm_f)
                st.success("Erro registrado com sucesso! Atualizando base...")
                st.rerun()
            else:
                st.error("Por favor, preencha todos os campos obrigatórios.")

st.divider()

# ── Listagem de Erros ───────────────────────────────────────────────────────
filtered = entries
if area_sel:
    filtered = [e for e in filtered if e.get('area') in area_sel]
if busca:
    filtered = [e for e in filtered if busca.lower() in str(e).lower()]

if filtered:
    st.caption(f"Exibindo {len(filtered)} erros encontrados.")
    for entry in reversed(filtered): # Mostrar os mais recentes primeiro
        label = f"Erro #{entry.get('numero', '?')} — {entry.get('area')} › {entry.get('tema')}"
        with st.expander(label):
            st.markdown(f"**Caso:** {entry.get('caso')}")
            st.divider()
            st.error(f"**Elo Quebrado:** {entry.get('elo_quebrado')}")
            st.info(f"🧠 **Regra mestre:** {entry.get('explicacao_correta')}")
            if entry.get('armadilha') and entry.get('armadilha') != "N/A":
                st.warning(f"⚠️ **Gatilho examinador:** {entry['armadilha']}")
else:
    st.info("Nenhum erro encontrado com os filtros aplicados.")
