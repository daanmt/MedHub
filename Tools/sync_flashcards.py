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
    print("Gerando flashcards a partir do Caderno de Erros...")
    cursor.execute("SELECT id, tema_id, enunciado, elo_quebrado, armadilha_prova FROM questoes_erros")
    erros = cursor.fetchall()
    
    count = 0
    for err in erros:
        qid, tema_id, enunciado, elo, armadilha = err
        
        frente = f"DESAFIO DE ERRO: {enunciado[:200]}..."
        verso = f"**ELO QUEBRADO:** {elo}\n\n**ARMADILHA:** {armadilha}"
        
        # Verifica se já existe
        cursor.execute("SELECT id FROM flashcards WHERE questao_id = ?", (qid,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO flashcards (questao_id, tema_id, tipo, frente, verso) VALUES (?, ?, ?, ?, ?)",
                           (qid, tema_id, 'Erro', frente, verso))
            card_id = cursor.lastrowid
            
            # Inicializa FSRS
            cursor.execute('''
                INSERT INTO fsrs_cards (card_id, state, due, stability, difficulty, elapsed_days, scheduled_days, reps, lapses, last_review)
                VALUES (?, 0, ?, 0, 0, 0, 0, 0, 0, NULL)
            ''', (card_id, datetime.now()))
            count += 1
    print(f"  {count} novos cards de erros gerados.")

def sync_from_summaries(cursor):
    print("Gerando flashcards a partir dos Resumos Clínicos...")
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
            
            # Procura por Armadilhas (🔴), Alertas (⚠️) e Destaques (⭐)
            # Regex melhorada para pegar quase qualquer linha que tenha esses emojis
            alerts = re.findall(r'([🔴⚠️⭐])\s*(.*)', content)
            
            for emoji, text in alerts:
                if len(text.strip()) < 5: continue
                
                frente = f"REVISÃO ({emoji}) [{tema_name}]"
                verso = text.strip()
                
                # Verifica duplicata
                cursor.execute("SELECT id FROM flashcards WHERE frente = ? AND tema_id = ?", (frente, tema_id))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO flashcards (tema_id, tipo, frente, verso) VALUES (?, ?, ?, ?)",
                                   (tema_id, 'Resumo', frente, verso))
                    card_id = cursor.lastrowid
                    cursor.execute('''
                        INSERT INTO fsrs_cards (card_id, state, due, stability, difficulty, elapsed_days, scheduled_days, reps, lapses, last_review)
                        VALUES (?, 0, ?, 0, 0, 0, 0, 0, 0, NULL)
                    ''', (card_id, datetime.now()))
                    count += 1
    print(f"  {count} novos cards de resumos gerados.")

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
