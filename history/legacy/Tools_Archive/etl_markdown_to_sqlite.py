import re
import sys
import os

# Adds Tools folder to path so we can import insert_questao
sys.path.append(os.path.join(os.path.dirname(__file__), 'Tools'))
from insert_questao import insert_questao

def extract_field(pattern, text, default=""):
    match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return default

def etl():
    print(f"DEBUG: CWD: {os.getcwd()}")
    print(f"DEBUG: sys.path: {sys.path}")
    print("Iniciando varredura ETL (Extract, Transform, Load) do caderno_erros.md...")
    try:
        with open('caderno_erros.md', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("Arquivo caderno_erros.md não encontrado!")
        return

    # Evita que o índice de áreas seja lido como a área atual
    if '## Índice de Áreas' in content:
        content = content.replace('## Índice de Áreas', '<!-- index -->')
    
    current_area = "Geral"
    current_tema = "Geral"
    
    lines = content.split('\n')
    current_block = []
    blocks = []
    
    for line in lines:
        if line.startswith('## '):
            current_area = line.replace('## ', '').strip()
        elif line.startswith('### '):
            current_tema = line.replace('### ', '').strip()
        elif line.startswith('#### '):
            if current_block:
                blocks.append((current_area, current_tema, '\n'.join(current_block)))
            current_block = [line]
        else:
            if current_block:
                current_block.append(line)
    
    if current_block:
        blocks.append((current_area, current_tema, '\n'.join(current_block)))
    
    print(f"Encontrados {len(blocks)} blocos de erros/questões legados. Iniciando injeção...\n")
    
    success_count = 0
    for area, tema, block_text in blocks:
        try:
            title = block_text.split('\n')[0].replace('####', '').strip()
            
            # Extrações de campos chave usando lookaheads
            elo = extract_field(r'\*\*Elo quebrado:\*\*(.*?)(?=\n\*\*|\n---)', block_text, "N/A")
            erro = extract_field(r'\*\*Tipo de erro:\*\*(.*?)(?=\n\*\*|\n---)', block_text, "N/A")
            complexidade = extract_field(r'\*\*Complexidade:\*\*(.*?)(?=\n\*\*|\n---)', block_text, "Média")
            
            # Caso
            caso = extract_field(r'\*\*Caso:\*\*(.*?)(?=\n\*\*|\n---)', block_text, "")
            
            # Habilidades Sequenciais (pode ser múltipla linhas)
            habilidades = extract_field(r'\*\*Habilidades sequenciais:\*\*(.*?)(?=\n\*\*|\n---)', block_text, "N/A")
            
            # O que faltou
            faltou = extract_field(r'\*\*O que faltou:\*\*(.*?)(?=\n\*\*|\n---)', block_text, "N/A")
            
            # Explicação correta
            explicacao = extract_field(r'\*\*Explicação correta:\*\*(.*?)(?=\n\*\*|\n---)', block_text, "")
            
            # Informações-chave (pode servir como Conceito de Ouro se a explicação for curta)
            chaves = extract_field(r'\*\*Informações-chave para revisão:\*\*(.*?)(?=\n---|<!--|\Z)', block_text, "")
            
            if not explicacao and chaves:
                explicacao = chaves
            
            # Armadilha / nuance
            armadilha = extract_field(r'\*\*Armadilha / nuance:\*\*(.*?)(?=\n\*\*|\n---)', block_text, "N/A")
            
            # Heurística para gabarito se não estiver explícito
            correta = "Ver Explicação"
            c_match = re.search(r'gabarito\s*(?:era|foi|:)?\s*(.*?)(?:\.|\n|$)', block_text, re.IGNORECASE)
            if c_match: correta = c_match.group(1).strip()
            
            marcada = "N/A"
            m_match = re.search(r'[Mm]arcou\s+(.*?)(?:,|\n)', block_text)
            if m_match: marcada = m_match.group(1).strip()
            
            # Dispara a inserção no banco de dados e a geração do flashcard
            insert_questao(
                area=area,
                tema=tema,
                enunciado=caso if caso else title,
                correta=correta,
                chamada=marcada,
                erro=erro,
                elo=elo,
                armadilha=armadilha,
                complexidade=complexidade,
                habilidades=habilidades,
                faltou=faltou,
                explicacao=explicacao,
                titulo=title
            )
            success_count += 1
            print(f"[OK] {title[:40]}...")
            
        except Exception as e:
            print(f"[ERRO] Falha ao processar bloco: {str(e)}")
            
    print(f"\n🚀 SUCESSO! {success_count} questões foram parseadas e convertidas em Flashcards FSRS no ipub.db.")

if __name__ == '__main__':
    etl()
