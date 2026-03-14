import os
import streamlit as st
from app.utils.file_io import get_abs_path, read_md

st.title("🗓️ Histórico de Sessões")
st.markdown("Visualização das sessões de estudo passadas registradas pelo repositório.")

history_dir = get_abs_path("history")
if not history_dir.exists():
    st.warning("Diretório `history/` não encontrado.")
    st.stop()

# Lista de arquivos ordenados do mais recente pro mais antigo (baseado no nome do arquivo YYYY-MM-DD ou session_NNN)
files = sorted(history_dir.glob("*.md"), reverse=True)

if not files:
    st.info("Nenhuma sessão registrada ainda.")
else:
    for f in files:
        # Pega a primeira linha como titulo do expander
        content = read_md(f"history/{f.name}")
        # Ignora arquivos sem titulo
        lines = content.split("\\n")
        title = lines[0].replace("#", "").strip() if lines else f.name
        
        # extrai preview
        content_lines = [l for l in lines[2:] if l.strip()]
        preview = ' '.join(content_lines[:3])[:200] + '...' if content_lines else ''
        
        with st.expander(f"📄 {f.name} — {title}", expanded=False):
            col1, col2 = st.columns([3,1])
            with col1:
                st.caption(preview)
            with col2:
                if st.button("Ver completo", key=f.name):
                    st.markdown(content)
            st.divider()
