import streamlit as st
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.utils.db import get_caderno_detalhado
from app.utils.styles import inject_styles

st.set_page_config(page_title="Caderno de Erros", page_icon="📓", layout="wide")
inject_styles()

st.markdown('<p style="color: #A8B3C2;">Consulta read-only dos elos quebrados registrados em <code>questoes_erros</code>.</p>', unsafe_allow_html=True)
st.info("🧠 A revisão espaçada agora é conversacional: use `/revisar` no Claude Code (funciona inclusive pelo celular).")

@st.cache_data(ttl=60)
def load_caderno():
    return get_caderno_detalhado()

try:
    df_erros = load_caderno()
except Exception as e:
    st.error("⚠️ Erro ao ler o banco de dados.")
    st.code(str(e))
    st.stop()

if df_erros.empty:
    st.info("Nenhum erro cadastrado ainda no banco de dados.")
else:
    areas = sorted(df_erros['area'].unique())
    filtro_area = st.multiselect("Filtrar Especialidade", areas, placeholder="Todas", key="filt_cad")

    f_df = df_erros[df_erros['area'].isin(filtro_area)] if filtro_area else df_erros

    st.caption(f"{len(f_df)} erro(s) no filtro atual.")

    for _, r in f_df.iterrows():
        with st.expander(f"Erro #{r['id']} · {r['titulo']}"):
            st.caption(f"{r['area']} › {r['tema']}")
            if r['elo']:
                st.markdown(f"**🔗 Elo Quebrado:** {r['elo']}")
            if r['caso']:
                st.markdown(f"**📝 Caso:** {r['caso']}")
            if r['explicacao']:
                st.success(r['explicacao'])
            if r['armadilha']:
                st.warning(f"**Armadilha:** {r['armadilha']}")
