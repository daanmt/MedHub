import os
import streamlit as st
from utils.file_io import get_abs_path, read_md

st.title("📚 Resumos Clínicos")

temas_dir = get_abs_path("Temas")
if not temas_dir.exists():
    st.warning("Diretório `Temas/` não encontrado.")
    st.stop()

# Varredura hierárquica usando os.walk
areas = [d for d in os.listdir(temas_dir) if os.path.isdir(temas_dir / d)]

if not areas:
    st.info("Nenhuma área de estudo encontrada na pasta Temas.")
    st.stop()

# Layout de navegação
col_nav, col_content = st.columns([1, 3])

with col_nav:
    st.subheader("Navegação")
    selected_area = st.radio("Selecione a Área:", areas)
    
    area_path = temas_dir / selected_area
    materiais = [f for f in os.listdir(area_path) if f.endswith('.md')]
    
    if materiais:
        selected_file = st.radio("Selecione o Resumo:", materiais)
    else:
        selected_file = None
        st.write("Vazio.")

with col_content:
    if selected_file:
        file_rel_path = f"Temas/{selected_area}/{selected_file}"
        content = read_md(file_rel_path)
        
        c1, c2 = st.columns([3, 1])
        with c1:
            st.subheader(selected_file.replace(".md", ""))
        with c2:
            modo_edicao = st.toggle("Modo Edição ✏️")

        if modo_edicao:
            novo_conteudo = st.text_area("Editor Markdown Raw:", value=content, height=800)
            if st.button("💾 Salvar Alterações"):
                from utils.file_io import write_md
                write_md(file_rel_path, novo_conteudo)
                st.success("Arquivo salvo com sucesso e backup `.bak` gerado!")
                st.rerun()
        else:
            st.markdown(content)
    else:
        st.info("Selecione um arquivo na barra lateral para visualizar.")
