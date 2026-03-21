import streamlit as st
import os

st.set_page_config(page_title="Biblioteca & Tutor", page_icon="📚", layout="wide")

st.title("📚 Biblioteca")
st.markdown('<p style="color: #A8B3C2; margin-top: -15px;">Acesso ultrarrápido aos resumos (.md) e Fichas/Apostilas (.pdf).</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Resumos RAG (.md)", "🗂️ Fichas & Apostilas (.pdf)"])

@st.cache_data(ttl=300)
def carregar_resumos():
    lista = []
    if os.path.exists("Temas"):
        for root, dirs, files in os.walk("Temas"):
            for f in files:
                if f.endswith(".md"):
                    area = os.path.basename(root)
                    if area == "Temas" or area == "": area = "Geral"
                    lista.append({"area": area, "tema": f.replace(".md", ""), "path": os.path.join(root, f)})
    return sorted(lista, key=lambda x: (x['area'], x['tema']))

@st.cache_data(ttl=300)
def carregar_pdfs():
    lista = []
    dirs_to_search = ["Fichas", "Memorex"]
    for d in dirs_to_search:
        if os.path.exists(d):
            for root, dirs, files in os.walk(d):
                for f in files:
                    if f.endswith(".pdf"):
                        lista.append({"nome": f, "path": os.path.join(root, f)})
    return sorted(lista, key=lambda x: x['nome'])

# ── ABA 1: RESUMOS ───────────────────────────────────────────────────────────
with tab1:
    resumos = carregar_resumos()
    
    if 'resumo_aberto' not in st.session_state:
        st.session_state.resumo_aberto = None

    if st.session_state.resumo_aberto is not None:
        r = st.session_state.resumo_aberto
        col1, col2 = st.columns([1, 8])
        if col1.button("← Voltar Galeria"):
            st.session_state.resumo_aberto = None
            st.rerun()
        col2.caption(f"**{r['area']}** › {r['tema']}")
        
        try:
            with open(r['path'], 'r', encoding='utf-8') as fh:
                st.markdown(f'<div style="background:#0E1116; padding:30px; border-radius:12px; border:1px solid #202A36;">{fh.read()}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
    else:
        if not resumos:
            st.info("Nenhum arquivo .md encontrado na pasta Temas/")
        else:
            filt = st.text_input("Buscar Resumo", placeholder="Ex: Pneumonia...")
            filtered = [r for r in resumos if filt.lower() in r['tema'].lower()] if filt else resumos
            
            c = st.columns(3)
            for i, r in enumerate(filtered):
                with c[i%3]:
                    st.markdown(f"<div style='border:1px solid #202A36; padding:15px; border-radius:8px; margin-bottom:10px; background:#11161D;'><b>{r['tema']}</b><br><small style='color:#738093;'>{r['area']}</small></div>", unsafe_allow_html=True)
                    if st.button("Ler", key=f"r_{r['path']}", width='stretch'):
                        st.session_state.resumo_aberto = r
                        st.rerun()

# ── ABA 2: APOSTILAS / PDF ───────────────────────────────────────────────────
with tab2:
    pdfs = carregar_pdfs()
    if not pdfs:
        st.info("Nenhum arquivo PDF encontrado nas pastas Fichas/ ou Memorex/")
    else:
        for p in pdfs:
            st.markdown(f"📄 **{p['nome']}**")
            st.caption(f"`{p['path']}`")
            # PDF embedding cannot be done purely securely inline without iframe tricks due to brower security, so we provide the path.
            # Local streamlit server allows static hosting only if configured. We just list them.
        st.info("💡 As apostilas PDFs estão mapeadas. O Agente MCP RAG pode ler e absorver dados delas para montar simulados e analisar!")
