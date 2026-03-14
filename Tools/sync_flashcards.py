import sqlite3
import os
import re
from datetime import datetime

DB_PATH = 'ipub.db'

def get_tema_id(cursor, area_hint, tema_name):
    # Tenta encontrar o tema_id exato ou aproximado
    cursor.execute("SELECT id FROM taxonomia_cronograma WHERE tema LIKE ? LIMIT 1", (f"%{tema_name}%",))
    row = cursor.fetchone()
    return row[0] if row else None

def sync_from_errors(cursor):
    print("Gerando flashcards CLÍNICOS a partir do Caderno de Erros...")
    # Buscamos mais detalhes para o verso
    cursor.execute("SELECT id, tema_id, enunciado, elo_quebrado, armadilha_prova, alternativa_correta FROM questoes_erros")
    erros = cursor.fetchall()
    
    count = 0
    for err in erros:
        qid, tema_id, enunciado, elo, armadilha, correta = err
        
        # Frente: O contexto clínico real (limpo de spoilers)
        enunciado_limpo = re.sub(r'(?i)(?:Marcou|Gabarito|Resposta|A questÃ£o era|O gabarito foi).*', '', enunciado).strip()
        frente = f"### [SIMULADO IPUB: Erro Real]\n{enunciado_limpo}\n\n**🧠 DESAFIO:** Qual o diagnóstico/conduta e qual o elo de conhecimento a ser restaurado?"
        # Verso: A solução pedagógica
        verso = f"✅ **ALTERNATIVA CORRETA:** {correta}\n\n🧠 **ELO QUEBRADO:** {elo}\n\n🔴 **ARMADILHA:** {armadilha}"
        
        # Como o estilo mudou radicalmente, vamos permitir re-gerar se o tipo for o mesmo mas a frente for diferente
        cursor.execute("SELECT id FROM flashcards WHERE questao_id = ?", (qid,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO flashcards (questao_id, tema_id, tipo, frente, verso) VALUES (?, ?, ?, ?, ?)",
                           (qid, tema_id, 'Erro', frente, verso))
            card_id = cursor.lastrowid
            cursor.execute('''
                INSERT INTO fsrs_cards (card_id, state, due, stability, difficulty, elapsed_days, scheduled_days, reps, lapses, last_review)
                VALUES (?, 0, ?, 0, 0, 0, 0, 0, 0, NULL)
            ''', (card_id, datetime.now()))
            count += 1
    print(f"  {count} novos cards clínicos de erros gerados.")

def sync_from_summaries(cursor):
    print("Gerando flashcards de REVISÃO (High-Level) a partir dos Resumos Clínicos...")
    temas_dir = 'Temas'
    count = 0
    
    for root, dirs, files in os.walk(temas_dir):
        for file in files:
            if not file.endswith('.md'): continue
            
            tema_name = file.replace('.md', '')
            tema_id = get_tema_id(cursor, None, tema_name)
            if not tema_id: continue
            
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Procura por marcadores 🔴, ⚠️, ⭐
            alerts = re.findall(r'([🔴⚠️⭐])\s*(.*)', content)
            
            for emoji, text in alerts:
                text = text.strip()
                if len(text) < 5: continue
                
                # Prompts de alto nível
                prompt = "O que você sabe sobre este ponto?"
                if emoji == '🔴': 
                    prompt = "Qual a **ARMADILHA CLÁSSICA** de prova sobre este tópico?"
                elif emoji == '⚠️':
                    prompt = "Qual o **PADRÃO DE PROVA** ou conduta essencial aqui?"
                elif emoji == '⭐':
                    prompt = "O que é **FUNDAMENTAL DOMINAR** sobre este assunto?"

                # Extrai tópico em negrito se existir
                match_bold = re.match(r'\*\*(.*?)\*\*:(.*)', text)
                if match_bold:
                    topico = match_bold.group(1)
                    frente = f"### [REVISÃO: {tema_name}]\n\n**TÓPICO:** {topico}\n\n**🧠 DESAFIO:** {prompt} {emoji}"
                    verso = text
                else:
                    frente = f"### [REVISÃO: {tema_name}]\n\n**🧠 DESAFIO:** {prompt} {emoji}\n\n*Pista:* {text[:60]}..."
                    verso = text
                
                # Verifica duplicata
                cursor.execute("SELECT id FROM flashcards WHERE verso = ? AND tema_id = ?", (verso, tema_id))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO flashcards (tema_id, tipo, frente, verso) VALUES (?, ?, ?, ?)",
                                   (tema_id, 'Resumo', frente, verso))
                    card_id = cursor.lastrowid
                    cursor.execute('''
                        INSERT INTO fsrs_cards (card_id, state, due)
                        VALUES (?, 0, ?)
                    ''', (card_id, datetime.now()))
                    count += 1
    print(f"  {count} novos cards de revisão de alto nível gerados.")

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    sync_from_errors(cursor)
    sync_from_summaries(cursor)
    
    conn.commit()
    conn.close()
    print("Sincronização concluída com sucesso!")

if __name__ == "__main__":
    main()
