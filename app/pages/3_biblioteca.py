import streamlit as st
import os
from pathlib import Path

from app.utils.styles import inject_styles

st.set_page_config(page_title="Biblioteca & Tutor", page_icon="📚", layout="wide")
inject_styles()

st.title("📚 Biblioteca")
st.markdown('<p style="color: #A8B3C2; margin-top: -15px;">Acesso ultrarrápido aos resumos (.md).</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 Resumos RAG (.md)", "🗂️ Fichas & Apostilas (.pdf)"])

@st.cache_data(ttl=300)
def carregar_resumos():
    lista = []
    if os.path.exists("resumos"):
        for root, dirs, files in os.walk("resumos"):
            for f in files:
                if f.endswith(".md"):
                    area = os.path.basename(root)
                    if area == "resumos" or area == "": area = "Geral"
                    lista.append({"area": area, "tema": f.replace(".md", ""), "path": os.path.join(root, f)})
    return sorted(lista, key=lambda x: (x['area'], x['tema']))

@st.cache_data(ttl=300)
def carregar_pdfs():
    # As pastas Fichas/ e Memorex/ foram removidas pelo usuário por não serem utilizadas.
    # Mantemos a função por compatibilidade caso novas pastas de PDF sejam adicionadas.
    lista = []
    dirs_to_search = ["pdf", "apostilas"] # Novos padrões lowercase
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
        # ── BUSCA SEMÂNTICA ───────────────────────────────────────────────────
        query = st.text_input("Busca semântica", placeholder="Ex: critérios SIRS neonato, manejo sepse choque...")

        if query.strip():
            try:
                from app.engine.rag import search as rag_search, _CHROMA_AVAILABLE
                if not _CHROMA_AVAILABLE:
                    st.info("Índice semântico não disponível. Execute: python tools/index_resumos.py")
                else:
                    resultados = rag_search(query.strip(), n_results=5)
                    if not resultados:
                        st.caption("Nenhum resultado. O índice pode estar vazio — execute tools/index_resumos.py")
                    else:
                        for r in resultados:
                            section = r["metadata"].get("section", "—")
                            source = r["metadata"].get("source", "")
                            with st.expander(f"{section}  ·  {Path(source).stem if source else ''}"):
                                st.markdown(r["text"])
                                if source:
                                    st.caption(f"Fonte: `{source}`")
            except Exception as e:
                st.warning(f"Busca semântica indisponível: {e}")

        st.divider()

        # ── GALERIA DE RESUMOS ────────────────────────────────────────────────
        if not resumos:
            st.info("Nenhum arquivo .md encontrado na pasta resumos/")
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
        st.info("Nenhum arquivo PDF encontrado (as pastas legadas Fichas/ e Memorex/ foram removidas).")
    else:
        for p in pdfs:
            st.markdown(f"📄 **{p['nome']}**")
            st.caption(f"`{p['path']}`")
            # PDF embedding cannot be done purely securely inline without iframe tricks due to brower security, so we provide the path.
            # Local streamlit server allows static hosting only if configured. We just list them.
        st.info("💡 As apostilas PDFs estão mapeadas. O Agente MCP RAG pode ler e absorver dados delas para montar simulados e analisar!")
