import os
import streamlit as st
from utils.file_io import get_abs_path, read_md

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
        lines = content.split("\\n")
        title = lines[0].replace("#", "").strip() if lines else f.name
        
        with st.expander(f"📝 {f.name} — {title}"):
            st.markdown(content)
