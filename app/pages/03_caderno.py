import streamlit as st
import pandas as pd
from app.utils.parser import parse_caderno_erros, save_new_error

entries = parse_caderno_erros()
df = pd.DataFrame(entries) if entries else pd.DataFrame()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filtros")
    areas = sorted(df['area'].unique()) if not df.empty else []
    area_filter = st.multiselect("Área", areas)
    busca = st.text_input("Buscar", placeholder="Qualquer campo...")

    st.divider()
    with st.expander("➕ Novo erro"):
        with st.form("form_novo_erro"):
            area_f   = st.text_input("Área")
            tema_f   = st.text_input("Tema")
            titulo_f = st.text_input("Título")
            elo_f    = st.text_input("Elo quebrado")
            caso_f   = st.text_area("Caso clínico")
            expl_f   = st.text_area("Explicação")
            arm_f    = st.text_input("Armadilha (opcional)")
            if st.form_submit_button("Salvar"):
                if all([area_f, tema_f, titulo_f, elo_f, caso_f, expl_f]):
                    save_new_error(area_f, tema_f, titulo_f, elo_f, caso_f, expl_f, arm_f)
                    st.success("Salvo!")
                    st.rerun()
                else:
                    st.error("Preencha todos os campos.")

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.title("📖 Caderno de Erros")

if df.empty:
    st.info("Nenhum erro registrado.")
    st.stop()

# ── Filtragem ─────────────────────────────────────────────────────────────────
filtered = df.copy()
if area_filter:
    filtered = filtered[filtered['area'].isin(area_filter)]
if busca:
    bl = busca.lower()
    text_cols = ['titulo', 'elo_quebrado', 'caso', 'explicacao_correta', 'armadilha', 'o_que_faltou']
    mask = pd.Series(False, index=filtered.index)
    for col in text_cols:
        if col in filtered.columns:
            mask |= filtered[col].str.lower().str.contains(bl, na=False)
    filtered = filtered[mask]

st.caption(f"{len(filtered)} de {len(df)} entradas")
st.divider()

# ── Lista ─────────────────────────────────────────────────────────────────────
for _, row in filtered.iloc[::-1].iterrows():
    num    = row.get('numero', '')
    titulo = row.get('titulo', 'Sem título')
    area   = row.get('area', '')
    tema   = row.get('tema', '')

    with st.expander(f"#{num} · {titulo}"):
        st.caption(f"{area} › {tema}")
        st.divider()

        elo = row.get('elo_quebrado', '')
        if elo and elo != 'N/A':
            st.markdown(f"**Elo quebrado** — {elo}")

        caso = row.get('caso', '')
        if caso and caso != 'N/A':
            st.markdown(f"**Caso**")
            st.markdown(caso)

        expl = row.get('explicacao_correta', '')
        if expl and expl != 'N/A':
            st.success(expl)

        arm = row.get('armadilha', '')
        if arm and arm != 'N/A':
            st.warning(arm)

        faltou = row.get('o_que_faltou', '')
        if faltou and faltou != 'N/A':
            st.caption(f"**O que faltou:** {faltou}")
