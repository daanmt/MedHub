import streamlit as st
import pandas as pd
from app.utils.db import get_caderno_erros

st.title("📖 Caderno de Erros (DB)")
st.markdown("Todos os seus flashcards e erros mapeados, agora alimentados e filtrados via DataFrame pelo `ipub.db`.")

df_erros = get_caderno_erros()

if not df_erros.empty:
    st.dataframe(
        df_erros,
        width="stretch",
        hide_index=True,
        height=600
    )
else:
    st.info("Nenhuma questão registrada no Banco de Dados.")
