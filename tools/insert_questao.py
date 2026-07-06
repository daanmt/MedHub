"""
CLI canônica para registrar um erro de questão no `ipub.db` atomicamente.

Transação de 4 passos em commit único:
1. Insert/update em `taxonomia_cronograma` (cria área+tema se não existir).
2. Insert em `questoes_erros` com metadados do erro.
3. Insert de cards em `flashcards`: N cards atômicos via `--cards-file`
   (cunhados pelo agente, ver `.claude/commands/estilo-flashcard.md`), ou
   caminho legado 1-2 cards a partir dos campos estruturados.
4. Init de estado FSRS em `fsrs_cards` para cada card.

Assinatura canônica (17 args: 8 obrigatórios + 9 opcionais/qualidade) em
`.claude/commands/analisar-questao.md §9`. Exit 0 em sucesso, 1 em falha.
"""

import sqlite3
import argparse
import json
import sys
from datetime import datetime
import os
import re
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

# --- Reincidencia (F25, PRD orquestracao part-3) ----------------------------
# Matcher lexical simples: normaliza, remove stopwords minimas, mede overlap de
# tokens. WARN informativo (politica s106/107) -- NUNCA bloqueia o insert.
LIMIAR_OVERLAP = 0.5   # fracao de tokens compartilhados sobre o MENOR conjunto
STOPWORDS = {"de", "da", "do", "das", "dos", "em", "no", "na", "nos", "nas",
             "um", "uma", "para", "por", "com", "sem", "que", "nao", "não",
             "mais", "menos", "antes", "apos", "após", "entre", "sobre",
             "qual", "quando", "como", "deve", "pode", "caso", "paciente"}


def _tokens(texto):
    """Tokens normalizados (>= 4 chars, sem stopwords) p/ o match lexical."""
    palavras = re.findall(r"[a-zA-ZÀ-ÿ0-9<>=]{4,}", (texto or "").lower())
    return {p for p in palavras if p not in STOPWORDS}


def checar_reincidencia(conn, tema_id, questao_id_novo, texto_novo):
    """F25: cruza o erro novo contra erros/cards EXISTENTES do mesmo tema.
    Retorna lista de hits [(tipo, id, overlap)]; vazia quando nada casa."""
    novos = _tokens(texto_novo)
    if not novos:
        return []
    hits = []
    cur = conn.cursor()
    cur.execute("SELECT id, habilidades_sequenciais, o_que_faltou FROM questoes_erros "
                "WHERE tema_id = ? AND id <> ?", (tema_id, questao_id_novo))
    for qid, hab, faltou in cur.fetchall():
        antigos = _tokens((hab or "") + " " + (faltou or ""))
        if antigos:
            overlap = len(novos & antigos) / min(len(novos), len(antigos))
            if overlap >= LIMIAR_OVERLAP:
                hits.append(("erro", qid, round(overlap, 2)))
    cur.execute("SELECT id, frente_pergunta, verso_resposta, verso_regra_mestre, "
                "verso_armadilha FROM flashcards "
                "WHERE tema_id = ? AND (questao_id IS NULL OR questao_id <> ?)",
                (tema_id, questao_id_novo))
    for cid, fp, vr, vrm, va in cur.fetchall():
        antigos = _tokens(" ".join(filter(None, (fp, vr, vrm, va))))
        if antigos:
            overlap = len(novos & antigos) / min(len(novos), len(antigos))
            if overlap >= LIMIAR_OVERLAP:
                hits.append(("card", cid, round(overlap, 2)))
    return hits


def insert_questao(area, tema, enunciado, correta, chamada, erro, elo, armadilha,
                   complexidade="Media", habilidades="N/A", faltou="N/A", explicacao="N/A", titulo="Erro sem titulo",
                   frente_contexto=None, frente_pergunta=None,
                   verso_resposta=None, verso_regra_mestre=None, verso_armadilha=None,
                   cards=None):
    # print(f"DEBUG: Tentando inserir no banco: {os.path.abspath(DB_PATH)}")
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Verifica se o Tema já existe (por (area, tema) — evita re-poluir; UNIQUE no schema). Se não existir, cria.
        cursor.execute("SELECT id FROM taxonomia_cronograma WHERE area = ? AND tema = ?", (area, tema))
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

        # 2. Gerar Flashcards IPUB v5.0
        if cards is not None:
            # Caminho agent-first: N cards atômicos já cunhados pela régua
            # (.claude/commands/estilo-flashcard.md). Substitui a geração fixa
            # elo+armadilha; todos os cards são qualitativos.
            cards_to_insert = []
            for i, c in enumerate(cards):
                fp_card = (c.get('frente_pergunta') or '').strip()
                vr_card = (c.get('verso_resposta') or '').strip()
                if not fp_card or not vr_card:
                    raise ValueError(f"Card {i}: 'frente_pergunta' e 'verso_resposta' sao obrigatorios")
                cards_to_insert.append((
                    c.get('tipo') or 'conteudo',
                    '', '',  # frente/verso legados — nao usados no INSERT v5
                    c.get('frente_contexto') or '',
                    fp_card, vr_card,
                    c.get('verso_regra_mestre') or '',
                    c.get('verso_armadilha') or '',
                    'qualitative',
                ))
        else:
            enunciado_limpo = re.sub(r'(?i)(?:Marcou|Gabarito|Resposta|O gabarito foi).*', '', enunciado).strip()
            caso_resumo = (enunciado_limpo.split('.')[0] if '.' in enunciado_limpo else enunciado_limpo)[:120]

            # Determinar qualidade e fonte dos campos estruturados
            use_qualitative = all([frente_pergunta, verso_resposta])
            qual_source_elo = 'qualitative' if use_qualitative else 'heuristic'

            # Campos estruturados: usar args explícitos ou gerar heurística
            fc = frente_contexto or caso_resumo
            fp = frente_pergunta or f"{tema}: qual a conduta/criterio correto?"
            vr = verso_resposta or (correta if len(correta) >= 8 else explicacao[:200] if explicacao != "N/A" else "")
            vrm = verso_regra_mestre or (explicacao[:300] if explicacao != "N/A" else "")
            va_elo = verso_armadilha or (armadilha[:200] if armadilha != "N/A" else "")

            # Frente/verso legados (mantidos para fallback da UI)
            frente_elo = f"**Contexto:** {caso_resumo}\n\n**Pergunta:** {fp}"
            verso_elo = f"**RESPOSTA DIRETA:** {correta}\n\n**REGRA MESTRE:**\n{explicacao[:300] if explicacao != 'N/A' else 'Verificar caderno.'}"

            cards_to_insert = [('elo_quebrado', frente_elo, verso_elo, fc, fp, vr, vrm, va_elo, qual_source_elo)]

            # --- Card 2: A Armadilha (se relevante) ---
            # Só no caminho PURAMENTE legado: quando o agente passou campos
            # qualitativos (frente_pergunta + verso_resposta), a armadilha já
            # está em verso_armadilha do card 1 — gerar o card heurístico aqui
            # duplicaria o conteúdo (bug s077: #413 qualitativo + #414 heurístico).
            if not use_qualitative and armadilha and len(armadilha) > 20 and armadilha != "N/A":
                trigger_match = re.search(r'(?i)(?:descreve|apresenta|usa|coloca)\s+(.*?)(?=\s+para|\.|\Z)', armadilha)
                trigger = trigger_match.group(1) if trigger_match else "este cenario"
                frente_arm = f"**ARMADILHA:** O examinador costuma usar {trigger} para induzir ao erro em {tema}."
                verso_arm = f"**Gatilho:** {armadilha}\n\n**Como evitar:** Reler a regra mestre sobre este distrator."
                va_arm = armadilha[:200] if armadilha != "N/A" else ""
                cards_to_insert.append(('armadilha', frente_arm, verso_arm, caso_resumo[:100],
                                        f"Qual o distrator tipico do examinador em: {titulo}?",
                                        armadilha[:200], explicacao[:200] if explicacao != "N/A" else "", va_arm, 'heuristic'))

        # Inserção dos cards
        for tipo_card, frente, verso, fc_, fp_, vr_, vrm_, va_, qs_ in cards_to_insert:
            needs_q = 0 if qs_ == 'qualitative' else 1
            cursor.execute('''
                INSERT INTO flashcards (questao_id, tema_id, tipo,
                                        frente_contexto, frente_pergunta, verso_resposta,
                                        verso_regra_mestre, verso_armadilha,
                                        quality_source, needs_qualitative)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (questao_id, tema_id, tipo_card,
                  fc_, fp_, vr_, vrm_, va_, qs_, needs_q))
            card_id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO fsrs_cards (card_id, state, due)
                VALUES (?, 0, ?)
            ''', (card_id, datetime.now()))

        # 4. Atualizar ultima_revisao do tema (usado pelo widget Foco Crítico).
        #    NOTA ARQUITETURAL: questoes_realizadas e questoes_acertadas NÃO são
        #    incrementados aqui. O volume de questões é registrado via
        #    tools/registrar_sessao_bulk.py (separação de responsabilidades).
        cursor.execute('''
            UPDATE taxonomia_cronograma
            SET ultima_revisao = ?
            WHERE id = ?
        ''', (datetime.now().strftime('%Y-%m-%d'), tema_id))

        try:
            cursor.execute('''
                UPDATE cronograma_progresso
                SET status = 'Concluído', updated_at = CURRENT_TIMESTAMP
                WHERE tema LIKE ?
            ''', (f"%{tema}%",))
        except Exception:
            pass  # tabela opcional — ignorar se não existir

        conn.commit()
        print(f"Sucesso! Questão '{titulo}' inserida. Flashcard IPUB High-Level [ID: {card_id}] gerado.")

        # F25 (pos-commit, read-only): sinaliza reincidencia sobre elo ja registrado.
        # O matcher NUNCA altera o resultado do insert (WARN informativo).
        try:
            texto_novo = " ".join(t for t in (
                elo, faltou if faltou != "N/A" else "", habilidades if habilidades != "N/A" else ""
            ) if t)
            hits = checar_reincidencia(conn, tema_id, questao_id, texto_novo)
            if hits:
                alvos = ", ".join("%s %d (overlap %.2f)" % h for h in hits[:5])
                print("[REINCIDENCIA] elo similar a: %s -- %dx no tema. "
                      "Candidato a padrao vivo (HANDOFF) e mini-drill "
                      "(fsrs_queue --pre-bloco)." % (alvos, len(hits)))
        except Exception:
            pass

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
    parser.add_argument("--titulo", default="Erro sem titulo")
    # Campos estruturados para flashcard qualitativo (opcionais)
    parser.add_argument("--frente_contexto", default=None)
    parser.add_argument("--frente_pergunta", default=None)
    parser.add_argument("--verso_resposta", default=None)
    parser.add_argument("--verso_regra_mestre", default=None)
    parser.add_argument("--verso_armadilha", default=None)
    # Caminho agent-first: lista de N cards atômicos em JSON (UTF-8).
    # Cada item: {tipo?, frente_contexto?, frente_pergunta, verso_resposta, verso_regra_mestre?, verso_armadilha?}.
    # Quando fornecido, substitui a geração fixa elo+armadilha.
    parser.add_argument("--cards-file", dest="cards_file", default=None,
                        help="Path para JSON com lista de cards atômicos (ver estilo-flashcard.md)")

    args = parser.parse_args()

    cards = None
    if args.cards_file:
        with open(args.cards_file, encoding="utf-8") as fh:
            cards = json.load(fh)

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
        titulo=args.titulo,
        frente_contexto=args.frente_contexto,
        frente_pergunta=args.frente_pergunta,
        verso_resposta=args.verso_resposta,
        verso_regra_mestre=args.verso_regra_mestre,
        verso_armadilha=args.verso_armadilha,
        cards=cards,
    )
