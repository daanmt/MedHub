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

if not entries:
    st.info("Nenhum erro registrado no caderno.")
else:
    df = pd.DataFrame(entries)
    
    # Filtros Flat
    c1, c2 = st.columns(2)
    with c1:
        area_filter = st.multiselect("Filtrar por Área", options=sorted(df['area'].unique()))
    with c2:
        # Assuming 'tema' is a column in your DataFrame
        tema_filter = st.text_input("Buscar por Tema")
    
    filtered_df = df.copy()
    if area_filter:
        filtered_df = filtered_df[filtered_df['area'].isin(area_filter)]
    if tema_filter:
        filtered_df = filtered_df[filtered_df['tema'].str.contains(tema_filter, case=False, na=False)]

    st.markdown(f"**{len(filtered_df)}** entradas encontradas", unsafe_allow_html=True)
    st.divider()

    # Display cards in reverse order (most recent first)
    for idx, row in filtered_df.iloc[::-1].iterrows():
        with st.container():
            # Ensure 'erro', 'correto', 'complexidade', 'tipo_erro' columns exist or handle missing keys
            # Using .get() for robustness if these keys might be missing in some entries
            content = f"""
            <div style="margin-bottom: 8px;"><b>Caso:</b> {row.get('caso', 'N/A')}</div>
            <div style="margin-bottom: 8px;"><b>O que errei:</b> {row.get('elo_quebrado', 'N/A')}</div>
            <div style="color: #1FA971; font-weight: 500;"><b>Explicação Correta:</b> {row.get('explicacao_correta', 'N/A')}</div>
            """
            # Add armadilha if it exists and is not "N/A"
            if row.get('armadilha') and row.get('armadilha') != "N/A":
                content += f"<div style='color: #FFC107; font-weight: 500; margin-top: 8px;'>⚠️ <b>Gatilho examinador:</b> {row['armadilha']}</div>"

            content_card(
                title=f"{row.get('titulo', 'Erro sem título')}", # Use 'titulo' from original structure
                subtitle=f"{row.get('area', 'N/A')} • {row.get('tema', 'N/A')}", # Simplified subtitle
                content=content
            )
            st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
