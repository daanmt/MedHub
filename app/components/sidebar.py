import streamlit as st
from utils.file_io import read_md

def render_sidebar():
    """Renderiza a barra lateral global da aplicação"""
    with st.sidebar:
        st.header("🏥 IPUB UI")
        st.markdown("*Sistema Local de Retenção*")
        st.divider()
        
        # Puxamos o estado macro
        estado = read_md("ESTADO.md")
        # Pega so as primeiras 3 linhas pra mostrar o status rapido
        linhas = estado.split('\\n') if estado else []
        resumo_estado = '\\n'.join(linhas[:3]) if len(linhas) >= 3 else "Estado indisponível"
        
        st.caption("Status do Projeto:")
        st.markdown(resumo_estado)
        
        st.divider()
        st.markdown("**Core Engines:**")
        st.markdown("- Zero DB Architecture (Markdown only)")
        st.markdown("- Parser Robótico Integrado")
        st.markdown("- FSRS via Claude Code")
