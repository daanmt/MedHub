import streamlit as st
import os

TEMAS_DIR = "Temas"
resumos = []
for root, dirs, files in os.walk(TEMAS_DIR):
    for f in files:
        if f.endswith(".md"):
            area = os.path.basename(root)
            resumos.append({"area": area, "tema": f.replace(".md", ""), "path": os.path.join(root, f)})

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filtros")
    areas = sorted(set(r['area'] for r in resumos))
    area_filter = st.multiselect("Área", areas)
    busca = st.text_input("Buscar", placeholder="Nome do tema...")

# ── Session state ─────────────────────────────────────────────────────────────
if 'resumo_aberto' not in st.session_state:
    st.session_state.resumo_aberto = None

# ── Full view ─────────────────────────────────────────────────────────────────
if st.session_state.resumo_aberto is not None:
    r = st.session_state.resumo_aberto
    if st.button("← Voltar"):
        st.session_state.resumo_aberto = None
        st.rerun()
    st.caption(f"{r['area']} › {r['tema']}")
    st.divider()
    try:
        with open(r['path'], 'r', encoding='utf-8') as fh:
            st.markdown(fh.read())
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
    st.stop()

# ── Grid view ─────────────────────────────────────────────────────────────────
st.title("📚 Resumos Clínicos")
st.markdown('<p style="color: #A8B3C2; margin-top: -15px; margin-bottom: 30px;">Acervo consolidado de temas de alta prevalência</p>', unsafe_allow_html=True)

if not resumos:
    st.info("Nenhum resumo encontrado em Temas/.")
    st.stop()

filtered = resumos
if area_filter:
    filtered = [r for r in filtered if r['area'] in area_filter]
if busca:
    filtered = [r for r in filtered if busca.lower() in r['tema'].lower()]

st.caption(f"{len(filtered)} resumo(s)")
st.divider()

cols = st.columns(2)
for i, r in enumerate(filtered):
    with cols[i % 2]:
        st.markdown(
            f'<div style="background:#11161D; border:1px solid #202A36; border-radius:10px; '
            f'padding:14px 18px; margin-bottom:4px;">'
            f'<div style="font-weight:600; font-size:0.9rem;">{r["tema"]}</div>'
            f'<div style="color:#738093; font-size:0.75rem; margin-top:3px;">{r["area"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        if st.button("Abrir", key=r['path'], width='stretch'):
            st.session_state.resumo_aberto = r
            st.rerun()
        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)
