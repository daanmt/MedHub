import streamlit as st
import os

st.set_page_config(page_title="Resumos Clínicos", page_icon="📚", layout="wide")

TEMAS_DIR = "Temas"

@st.cache_data(ttl=300)
def carregar_arquitetura_temas():
    lista = []
    if not os.path.exists(TEMAS_DIR):
        return lista
    for root, dirs, files in os.walk(TEMAS_DIR):
        for f in files:
            if f.endswith(".md"):
                area = os.path.basename(root)
                # Fallback genérico se estiver na raiz
                if area == TEMAS_DIR or area == "": area = "Geral"
                
                lista.append({
                    "area": area, 
                    "tema": f.replace(".md", ""), 
                    "path": os.path.join(root, f)
                })
    return sorted(lista, key=lambda x: (x['area'], x['tema']))

resumos = carregar_arquitetura_temas()

# ── Custom CSS para melhorar a beleza tipográfica ─────────────────────────────
st.markdown("""
<style>
    .resumo-card {
        background: #11161D; 
        border: 1px solid #202A36; 
        border-radius: 12px; 
        padding: 16px 20px; 
        margin-bottom: 12px;
        transition: transform 0.2s, border-color 0.2s;
    }
    .resumo-card:hover {
        border-color: #2F6BFF;
    }
    .resumo-title {
        font-weight: 600; font-size: 1.05rem; color: #F3F7FC;
    }
    .resumo-area {
        color: #738093; font-size: 0.8rem; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.05em;
    }
    .markdown-viewer {
        background: #0E1116;
        padding: 40px;
        border-radius: 16px;
        border: 1px solid #202A36;
        line-height: 1.8;
        font-size: 1.05rem;
    }
    .markdown-viewer h1, .markdown-viewer h2, .markdown-viewer h3 {
        color: #F3F7FC !important;
        margin-top: 1.5em;
        margin-bottom: 0.8em;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔍 Navegação")
    areas = sorted(set(r['area'] for r in resumos))
    area_filter = st.multiselect("Filtrar Especialidade", areas, placeholder="Todas as Áreas")
    busca = st.text_input("Palavra-chave", placeholder="Ex: Sífilis...")

# ── Session state ─────────────────────────────────────────────────────────────
if 'resumo_aberto' not in st.session_state:
    st.session_state.resumo_aberto = None

# ── Full view (Modo Leitura Dinâmica) ─────────────────────────────────────────
if st.session_state.resumo_aberto is not None:
    r = st.session_state.resumo_aberto
    
    col1, col2 = st.columns([1, 8])
    with col1:
        if st.button("← Voltar"):
            st.session_state.resumo_aberto = None
            st.rerun()
            
    with col2:
        st.caption(f"**📚 {r['area']}** › {r['tema']}")
    
    st.divider()
    
    try:
        with open(r['path'], 'r', encoding='utf-8') as fh:
            content = fh.read()
            st.markdown(f'<div class="markdown-viewer">{content}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
    st.stop()

# ── Grid view (Modo Biblioteca) ───────────────────────────────────────────────
st.title("📚 Biblioteca RAG")
st.markdown('<p style="color: #A8B3C2; margin-top: -15px; margin-bottom: 30px;">Acervo otimizado de resumos indexados pelo Obsidian.</p>', unsafe_allow_html=True)

if not resumos:
    st.info("Sua biblioteca está vazia. Crie arquivos `.md` na pasta `Temas/` para eles aparecerem aqui.")
    st.stop()

filtered = resumos
if area_filter:
    filtered = [r for r in filtered if r['area'] in area_filter]
if busca:
    filtered = [r for r in filtered if busca.lower() in r['tema'].lower()]

if not filtered:
    st.warning("Nenhum resumo encontrou com esses filtros.")
    st.stop()

st.caption(f"Mostrando {len(filtered)} resumos")
st.divider()

cols = st.columns(3) # Usa 3 colunas para um grid mais estético
for i, r in enumerate(filtered):
    with cols[i % 3]:
        st.markdown(
            f'<div class="resumo-card">'
            f'<div class="resumo-title">{r["tema"]}</div>'
            f'<div class="resumo-area">{r["area"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
        if st.button("Ler resumo", key=f"btn_{r['path']}", use_container_width=True):
            st.session_state.resumo_aberto = r
            st.rerun()
        st.markdown("<div style='margin-bottom:8px;'></div>", unsafe_allow_html=True)
