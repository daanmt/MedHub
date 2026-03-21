import sqlite3
import csv
import os
from datetime import datetime
import re

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'dashboard_umed.csv')

def importar_dashboard():
    print(f"Lendo dados de {CSV_PATH}...")
    
    # Agregação por Tema (Assunto)
    temas_stats = {}
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        # Pular cabeçalhos (as 3 primeiras linhas são complexas)
        next(reader)
        next(reader)
        next(reader)
        
        for row in reader:
            if len(row) < 8:
                continue
                
            assunto = row[2].strip()
            if not assunto or assunto == 'Assunto' or "Total" in row[1]:
                continue
                
            feitas_str = row[5].strip()
            acertos_str = row[6].strip()
            
            feitas = int(feitas_str) if feitas_str and feitas_str.isdigit() else 0
            acertos = int(acertos_str) if acertos_str and acertos_str.isdigit() else 0
            
            if assunto not in temas_stats:
                temas_stats[assunto] = {'feitas': 0, 'acertos': 0}
                
            temas_stats[assunto]['feitas'] += feitas
            temas_stats[assunto]['acertos'] += acertos

    # Inserir no SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    atualizados = 0
    inseridos = 0
    
    for tema, stats in temas_stats.items():
        if stats['feitas'] == 0:
            continue # Pula se não tiver dados numéricos concretos
            
        feitas = stats['feitas']
        acertos = stats['acertos']
        percentual = (acertos / feitas * 100) if feitas > 0 else 0.0
        
        # Limpar o nome do tema (remover quebras de linha caso existam)
        tema_limpo = " / ".join(tema.split('\n'))
        
        # Tentar achar o tema no banco
        cursor.execute("SELECT id, questoes_realizadas FROM taxonomia_cronograma WHERE tema LIKE ?", (f"%{tema_limpo}%",))
        row = cursor.fetchone()
        
        if row:
            tema_id = row[0]
            feitas_banco = row[1]
            
            # Atualiza apenas se o CSV tiver mais dados (assumindo que o CSV é a base offline mais rica até o momento)
            if feitas > feitas_banco:
                cursor.execute('''
                    UPDATE taxonomia_cronograma 
                    SET questoes_realizadas = ?, questoes_acertadas = ?, percentual_acertos = ?, ultima_revisao = ?
                    WHERE id = ?
                ''', (feitas, acertos, percentual, datetime.now().strftime('%Y-%m-%d'), tema_id))
                atualizados += 1
        else:
            # Insere novo
            # A área nós podemos herdar depois ou deixar como "Não Definida" provisoriamente
            cursor.execute('''
                INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas, percentual_acertos, ultima_revisao)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ('Importado via CSV', tema_limpo, feitas, acertos, percentual, datetime.now().strftime('%Y-%m-%d')))
            inseridos += 1
            
    conn.commit()
    conn.close()
    
    print(f"Migração concluída! Foram inseridos {inseridos} novos temas e atualizados {atualizados} temas existentes a partir do CSV do Google Sheets.")

if __name__ == '__main__':
    importar_dashboard()
