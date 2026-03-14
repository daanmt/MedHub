import streamlit as st
import re
from utils.file_io import read_md, append_md

st.title("📖 Caderno de Erros")
st.markdown("Visualização da base de erros legada do `caderno_erros.md`.")

# --- FORMULÁRIO DE NOVO ERRO ---
with st.expander("🆕 Registrar Novo Erro", expanded=False):
    with st.form("form_novo_erro", clear_on_submit=True):
        st.subheader("Nova Armadilha de Prova")
        area = st.selectbox("Área", ["Cirurgia", "Clínica Médica", "Pediatria", "Ginecologia e Obstetrícia", "Medicina Preventiva e Saúde Pública"])
        tipo = st.selectbox("Tipo de Erro", ["Erro de aplicação", "Conhecimento parcial", "Lacuna de conhecimento", "Erro de diagnóstico", "Armadilha do examinador"])
        elo = st.text_input("Elo Quebrado (Qual habilidade faltou?)")
        
        questao = st.text_area("Caso/Enunciado (Questão)")
        errado = st.text_area("O que faltou (Seu Raciocínio Errado)")
        correto = st.text_area("Explicação correta")
        insight = st.text_input("Armadilha / nuance")
        dica = st.text_input("Informações-chave para revisão")
        
        submitted = st.form_submit_button("Salvar no Caderno de Erros")
        
        if submitted:
            novo_bloco = f"""
#### {insight if insight else (elo[:30] + '...')}

**Complexidade:** Média
**Elo quebrado:** {elo}
**Tipo de erro:** {tipo}

**Caso:** {questao}

**O que faltou:**
{errado}

**Explicação correta:**
{correto}

**Armadilha / nuance:**
{insight}

**Informações-chave para revisão:**
- {dica}
"""
            # Anexa no final (Futuramente o parser poderia achar a área e injetar no local certo)
            append_md("caderno_erros.md", novo_bloco)
            st.success("Erro salvo com sucesso! Backup `.bak` gerado.")

st.divider()

# --- FILTROS & LISTA ---
# Lendo raw data
raw_erros = read_md("caderno_erros.md")
# Parse burro pra quebrar em blocos de H4 ####
blocos = re.split(r'\\n####\\s+', raw_erros)

if len(blocos) > 1:
    st.sidebar.header("🔍 Filtros de Busca")
    busca = st.sidebar.text_input("Buscar palavra-chave...")
    
    st.subheader(f"Listando {len(blocos)-1} erros catalogados:")
    
    for bloco in reversed(blocos[1:]): # Mostra os ultimos q entraram
        linhas = bloco.split('\\n')
        titulo = linhas[0].strip()
        conteudo = '\\n'.join(linhas[1:])
        
        # Ignora se não bater com a busca
        if busca and busca.lower() not in bloco.lower():
            continue
            
        with st.expander(f"⚠️ {titulo}"):
            st.markdown(conteudo)
else:
    st.info("O `caderno_erros.md` não parece conter marcadores H4 padrão ou está vazio.")
