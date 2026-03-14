import sqlite3
import argparse
import sys
from datetime import datetime

import os
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

def insert_questao(area, tema, enunciado, correta, chamada, erro, elo, armadilha, 
                   complexidade="Média", habilidades="N/A", faltou="N/A", explicacao="N/A", titulo="Erro sem título"):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verifica se o Tema já existe. Se não existir, cria.
        cursor.execute("SELECT id FROM taxonomia_cronograma WHERE tema = ?", (tema,))
        row = cursor.fetchone()
        
        if row:
            tema_id = row[0]
        else:
            cursor.execute('''
                INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, questoes_acertadas, percentual_acertos, ultima_revisao)
                VALUES (?, ?, 0, 0, 0, ?)
            ''', (area, tema, datetime.now().strftime('%Y-%m-%d')))
            tema_id = cursor.lastrowid

        # 1. Inserir a Questão Erro com Schema Expandido
        cursor.execute('''
            INSERT INTO questoes_erros 
            (tema_id, titulo, complexidade, enunciado, alternativa_correta, alternativa_marcada, 
             tipo_erro, habilidades_sequenciais, o_que_faltou, explicacao_correta, armadilha_prova)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tema_id, titulo, complexidade, enunciado, correta, chamada, 
              erro, habilidades, faltou, explicacao, armadilha))
        questao_id = cursor.lastrowid

        # 2. Gerar Flashcard FSRS de ALTO NÍVEL (Análise Cognitiva)
        frente_texto = f"### [DESAFIO IPUB: {tema}]\n\n**CASO CLÍNICO:**\n{enunciado}\n\n---\n**🧠 DESAFIO:** Qual foi o elo quebrado neste raciocínio e qual a correção fundamental?"
        
        verso_texto = (
            f"✅ **GABARITO:** {correta}\n\n"
            f"🪜 **CADEIA DE RACIOCÍNIO:**\n{habilidades}\n\n"
            f"💔 **ELO QUEBRADO:** {elo}\n\n"
            f"🧐 **O QUE FALTOU:** {faltou}\n\n"
            f"💡 **EXPLICAÇÃO CORRETA:**\n{explicacao}\n\n"
            f"🔴 **ARMADILHA/NUANCE:** {armadilha}"
        )
        
        cursor.execute('''
            INSERT INTO flashcards (questao_id, tema_id, tipo, frente, verso)
            VALUES (?, ?, 'Erro', ?, ?)
        ''', (questao_id, tema_id, frente_texto, verso_texto))
        card_id = cursor.lastrowid

        # 3. Inicializar o FSRS Card (New state)
        cursor.execute('''
            INSERT INTO fsrs_cards (card_id, state, due)
            VALUES (?, 0, ?)
        ''', (card_id, datetime.now()))

        # 4. Atualizar métricas do cronograma
        cursor.execute('''
            UPDATE taxonomia_cronograma
            SET questoes_realizadas = questoes_realizadas + 1,
                ultima_revisao = ?
            WHERE id = ?
        ''', (datetime.now().strftime('%Y-%m-%d'), tema_id))
        
        cursor.execute('''
            UPDATE cronograma_progresso 
            SET status = 'Concluído', updated_at = CURRENT_TIMESTAMP
            WHERE tema LIKE ?
        ''', (f"%{tema}%",))

        cursor.execute('''
            UPDATE taxonomia_cronograma
            SET percentual_acertos = CASE 
                WHEN questoes_realizadas > 0 THEN (CAST(questoes_acertadas AS REAL) / questoes_realizadas) * 100
                ELSE 0 
            END
            WHERE id = ?
        ''', (tema_id,))

        conn.commit()
        print(f"Sucesso! Questão '{titulo}' inserida. Flashcard IPUB High-Level [ID: {card_id}] gerado.")

    except Exception as e:
        print(f"Erro ao inserir no banco: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Script para pipeline Agente -> SQLite")
    parser.add_argument("--area", required=True)
    parser.add_argument("--tema", required=True)
    parser.add_argument("--enunciado", required=True)
    parser.add_argument("--correta", required=True)
    parser.add_argument("--marcada", required=True)
    parser.add_argument("--erro", required=True)
    parser.add_argument("--elo", required=True)
    parser.add_argument("--armadilha", required=True)
    parser.add_argument("--complexidade", default="Média")
    parser.add_argument("--habilidades", default="N/A")
    parser.add_argument("--faltou", default="N/A")
    parser.add_argument("--explicacao", default="N/A")
    parser.add_argument("--titulo", default="Erro sem título")

    args = parser.parse_args()
    
    insert_questao(
        area=args.area, 
        tema=args.tema, 
        enunciado=args.enunciado, 
        correta=args.correta, 
        chamada=args.marcada, 
        erro=args.erro, 
        elo=args.elo, 
        armadilha=args.armadilha,
        complexidade=args.complexidade,
        habilidades=args.habilidades,
        faltou=args.faltou,
        explicacao=args.explicacao,
        titulo=args.titulo
    )
