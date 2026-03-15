from app.utils.styles import content_card
import streamlit as st
import os

st.title("📚 Resumos Clínicos")
st.markdown('<p style="color: #A8B3C2; margin-top: -15px; margin-bottom: 30px;">Acervo consolidado de temas de alta prevalência</p>', unsafe_allow_html=True)

# Listar arquivos
TEMAS_DIR = "Temas"
resumos = []
for root, dirs, files in os.walk(TEMAS_DIR):
    for f in files:
        if f.endswith(".md"):
            area = os.path.basename(root)
            resumos.append({"area": area, "tema": f.replace(".md", ""), "path": os.path.join(root, f)})

if not resumos:
    st.info("Nenhum resumo encontrado.")
else:
    # Filtros Flat
    areas = sorted(list(set(r['area'] for r in resumos)))
    c1, c2 = st.columns([1, 2])
    with c1:
        selected_area = st.selectbox("Área", ["Todas"] + areas)
    with c2:
        search = st.text_input("Buscar tema")
    
    st.divider()

    filtered = resumos
    if selected_area != "Todas":
        filtered = [r for r in filtered if r['area'] == selected_area]
    if search:
        filtered = [r for r in filtered if search.lower() in r['tema'].lower()]

    # Grid de cards
    cols = st.columns(2)
    for i, r in enumerate(filtered):
        with cols[i % 2]:
            content = f'<div style="color: #A8B3C2; font-size: 0.85rem; margin-bottom: 12px;">Consulte o guia completo de condutas e diagnósticos para {r["tema"]}.</div>'
            content_card(
                title=r['tema'],
                subtitle=r['area'],
                content=content
            )
            if st.button(f"Abrir: {r['tema']}", key=r['path']):
                with open(r['path'], 'r', encoding='utf-8') as f:
                    st.markdown(f.read())
            st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
