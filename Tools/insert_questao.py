import sqlite3
import argparse
import sys
from datetime import datetime
import os
import re
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

def _extract_key_term(elo: str) -> str:
    """Extrai o termo médico principal do elo para usar na pergunta."""
    stopwords = ['habilidade', 'confundiu', 'esqueceu', 'não lembrou', 
                 'erro ao', 'falhou em', 'priorizar', 'identificar', 'prioritário']
    result = elo
    for sw in stopwords:
        result = result.lower().replace(sw, '').strip()
    return result[:80]

def _invert_elo_to_question(elo: str, tema: str) -> str:
    """Transforma texto do elo quebrado em pergunta cirúrgica."""
    elo_lower = elo.lower()
    
    # Padrões de limiar numérico
    if any(x in elo_lower for x in ['limiar', 'ponto de corte', '< ', '> ', 'mg/dl', 'mg/kg', 'bpm']):
        return f"Em {tema}: qual o valor limiar/dose correto para {_extract_key_term(elo)}?"
    
    # Padrões de sequência/prioridade
    if any(x in elo_lower for x in ['antes', 'primeiro', 'prioritário', 'sequência', 'ordem']):
        return f"Em {tema}: qual a sequência correta de conduta? (Dica: a ordem importa)"
    
    # Padrões de critério diagnóstico
    if any(x in elo_lower for x in ['critério', 'diagnóstico', 'definição', 'classificação']):
        return f"Quais os critérios diagnósticos / definição de {_extract_key_term(elo)}?"
    
    # Padrões de indicação/contraindicação
    if any(x in elo_lower for x in ['indicação', 'contraindicação', 'quando', 'em quais']):
        return f"Quais as indicações/contraindicações de {_extract_key_term(elo)} em {tema}?"
    
    # Fallback genérico mas cirúrgico
    return f"Sobre {tema}: {elo.rstrip('.')}?"

def insert_questao(area, tema, enunciado, correta, chamada, erro, elo, armadilha, 
                   complexidade="Média", habilidades="N/A", faltou="N/A", explicacao="N/A", titulo="Erro sem título"):
    # print(f"DEBUG: Tentando inserir no banco: {os.path.abspath(DB_PATH)}")
    conn = None
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

        # 2. Gerar Flashcards Doutrina IPUB v4.0 (A partir do Elo)
        # Extrai contexto mínimo (1 linha)
        enunciado_limpo = re.sub(r'(?i)(?:Marcou|Gabarito|Resposta|A questÃ£o era|O gabarito foi).*', '', enunciado).strip()
        caso_resumo = (enunciado_limpo.split('.')[0] if '.' in enunciado_limpo else enunciado_limpo)[:120]
        
        cards_to_insert = []
        
        # --- Card 1: O Elo Quebrado (Obrigatorio) ---
        pergunta_elo = _invert_elo_to_question(habilidades if habilidades != "N/A" else elo, tema)
        frente_elo = f"**Contexto:** {caso_resumo}\n\n**Pergunta:** {pergunta_elo}"
        
        verso_elo = (
            f"✅ **RESPOSTA DIRETA:** {correta}\n\n"
            f"🧠 **REGRA MESTRE:**\n{explicacao[:300] if explicacao != 'N/A' else 'Verificar caderno.'}"
        )
        
        cards_to_insert.append(('elo_quebrado', frente_elo, verso_elo))
        
        # --- Card 2: A Armadilha (Se relevante) ---
        if armadilha and len(armadilha) > 20 and armadilha != "N/A":
            trigger_match = re.search(r'(?i)(?:descreve|apresenta|usa|coloca)\s+(.*?)(?=\s+para|\.|\Z)', armadilha)
            trigger = trigger_match.group(1) if trigger_match else "este cenário"
            
            frente_arm = f"**⚠️ ARMADILHA:** O examinador costuma usar *{trigger}* para te induzir ao erro em {tema}."
            verso_arm = f"**Gatilho:** {armadilha}\n\n**Como evitar:** Releia o ponto da regra mestre sobre este distrator."
            cards_to_insert.append(('armadilha', frente_arm, verso_arm))

        # Inserção dos cards
        for tipo_card, frente, verso in cards_to_insert:
            cursor.execute('''
                INSERT INTO flashcards (questao_id, tema_id, tipo, frente, verso)
                VALUES (?, ?, ?, ?, ?)
            ''', (questao_id, tema_id, tipo_card, frente, verso))
            card_id = cursor.lastrowid

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
        return True

    except Exception as e:
        print(f"Erro ao inserir no banco: {e}")
        return False
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
