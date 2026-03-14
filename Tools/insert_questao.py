import sqlite3
import argparse
import sys
from datetime import datetime

DB_PATH = 'ipub.db'

def insert_questao(area, tema, enunciado, correta, chamada, erro, elo, armadilha):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verifica se o Tema já existe. Se não existir, cria.
        cursor.execute("SELECT id FROM taxonomia_cronograma WHERE tema = ?", (tema,))
        row = cursor.fetchone()
        
        if row:
            tema_id = row[0]
        else:
            # Novo tema no cronograma (Atenção: Idealmente o Dashboard dita isso)
            cursor.execute('''
                INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas, percentual_acertos, ultima_revisao)
                VALUES (?, ?, 0, 0, 0, ?)
            ''', (area, tema, datetime.now().strftime('%Y-%m-%d')))
            tema_id = cursor.lastrowid

        # 1. Inserir a Questão Erro
        cursor.execute('''
            INSERT INTO questoes_erros 
            (tema_id, enunciado, alternativa_correta, alternativa_marcada, tipo_erro, elo_quebrado, armadilha_prova)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (tema_id, enunciado, correta, chamada, erro, elo, armadilha))
        questao_id = cursor.lastrowid

        # 2. Gerar Flashcard FSRS Automático (a partir do elo / armadilha)
        frente_texto = f"[{area} - {tema}]\nQual o equívoco principal e regra sobre:\n{elo}?"
        verso_texto = f"Regra/Aprendizado:\n{armadilha}"
        
        cursor.execute('''
            INSERT INTO flashcards (questao_id, tema_id, tipo, frente, verso)
            VALUES (?, ?, 'FrontBack', ?, ?)
        ''', (questao_id, tema_id, frente_texto, verso_texto))
        card_id = cursor.lastrowid

        # 3. Inicializar o FSRS Card (New state)
        # state = 0 (New)
        cursor.execute('''
            INSERT INTO fsrs_cards (card_id, state)
            VALUES (?, 0)
        ''', (card_id,))

        # 4. Atualizar métricas do cronograma (realizou +1 questão crua)
        # O insert de erro pressupõe erro, logo apenas questoes_realizadas sobe. 
        cursor.execute('''
            UPDATE taxonomia_cronograma
            SET questoes_realizadas = questoes_realizadas + 1,
                ultima_revisao = ?
            WHERE id = ?
        ''', (datetime.now().strftime('%Y-%m-%d'), tema_id))
        
        # O cálculo percentual de acertos é recalculado a cada nova inserção
        cursor.execute('''
            UPDATE taxonomia_cronograma
            SET percentual_acertos = CASE 
                WHEN questoes_realizadas > 0 THEN (CAST(questoes_acertadas AS REAL) / questoes_realizadas) * 100
                ELSE 0 
            END
            WHERE id = ?
        ''', (tema_id,))

        conn.commit()
        print(f"Sucesso! Questão inserida no SQLite. Flashcard FSRS [ID: {card_id}] gerado.")

    except Exception as e:
        print(f"Erro ao inserir no banco: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Script para pipeline Agente -> SQLite")
    parser.add_argument("--area", required=True, help="Área (Ex: Cirurgia)")
    parser.add_argument("--tema", required=True, help="Tema (Ex: Trauma)")
    parser.add_argument("--enunciado", required=True, help="Texto do enunciado")
    parser.add_argument("--correta", required=True, help="Alternativa correta")
    parser.add_argument("--marcada", required=True, help="Alternativa do aluno")
    parser.add_argument("--erro", required=True, help="Classificação (Ex: Erro de Aplicação)")
    parser.add_argument("--elo", required=True, help="Habilidade/Elo Quebrado")
    parser.add_argument("--armadilha", required=True, help="Explicação/Regra/Armadilha de Prova")

    args = parser.parse_args()
    
    insert_questao(
        area=args.area, 
        tema=args.tema, 
        enunciado=args.enunciado, 
        correta=args.correta, 
        chamada=args.marcada, 
        erro=args.erro, 
        elo=args.elo, 
        armadilha=args.armadilha
    )
