"""insert_card_base.py — insere flashcards de PRÉ-REQUISITO (altitude base) no ipub.db.

Nascido na sessão 082. Um card-base não vem de um erro de questão — vem de uma
LACUNA DE FUNDAÇÃO detectada quando um CLUSTER de cards avançados (o "elo
metacognitivo" de questões) trava por falta de grounding. Ele reconstrói os elos
A MONTANTE (conceitos primitivos do tema) para que os cards-alvo fiquem acessíveis.

ALTURA GRADUADA (s082): a "altura" de um card não é binária (base × topo) — é uma
escada: base → mecanismo → nuance/detalhe → topo (o card de erro/elo metacognitivo).
O campo `tipo` carrega a altura ('base', 'mecanismo', 'nuance', ...). Este CLI insere
cards de qualquer altura de ANDAIME (default 'base'). Quantos degraus são precisos é
inferido da iteração: onde um elo trava, costura-se o degrau imediatamente adjacente
(propagação local), em vez de só repetir o topo.

Diferença para insert_questao.py:
  - questao_id = NULL  → não há erro de origem; a âncora é o resumo + o cluster.
  - tipo = 'base'      → marca de altitude; cards de erro são 'conteudo'/'elo_quebrado'.
  - Não escreve em questoes_erros; só flashcards + fsrs_cards (state 0).

Cada card-base segue .claude/commands/estilo-flashcard.md (atômico, recall de
conteúdo, regra-mestre transferível, armadilha ancorada). Grounding obrigatório:
um card-base só existe se sua razão de ser couber em 1 linha ancorada no resumo +
no cluster que o motivou (ai-eng: "especificidade sem contexto é criptografia").

Idempotente: pula um card se já existir card-base com a mesma frente_pergunta no
mesmo tema (evita duplicar em re-execução). Preserva FSRS dos que já existem.

Uso:
  python tools/insert_card_base.py --area Pediatria --tema "Cardiopatias Congênitas" \
         --from tmp/cards_base_cardio.json --dry-run
  python tools/insert_card_base.py --area Pediatria --tema "Cardiopatias Congênitas" \
         --from tmp/cards_base_cardio.json

JSON: lista de objetos. Campos por card:
  frente_pergunta     (obrigatório)
  verso_resposta      (obrigatório)
  frente_contexto     (opcional; vazio se a pergunta é conceitual direta)
  verso_regra_mestre  (opcional)
  verso_armadilha     (opcional)
  tipo                (opcional; default 'base')
"""
import sqlite3
import os
import io
import sys
import json
import argparse
from datetime import datetime

# Saída em UTF-8 — evita UnicodeEncodeError no console cp1252 do Windows.
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')


def get_or_create_tema(cursor, area, tema):
    cursor.execute("SELECT id FROM taxonomia_cronograma WHERE tema = ?", (tema,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(
        "INSERT INTO taxonomia_cronograma (area, tema, questoes_realizadas, "
        "questoes_acertadas, percentual_acertos, ultima_revisao) VALUES (?, ?, 0, 0, 0, ?)",
        (area, tema, datetime.now().strftime('%Y-%m-%d')))
    return cursor.lastrowid


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--area', required=True)
    ap.add_argument('--tema', required=True)
    ap.add_argument('--from', dest='src', required=True, help='JSON com a lista de cards-base')
    ap.add_argument('--dry-run', action='store_true', help='Mostra o que faria, sem gravar')
    args = ap.parse_args()

    with open(args.src, encoding='utf-8') as f:
        cards = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    tema_id = get_or_create_tema(c, args.area, args.tema)

    n_novos = n_skip = 0
    for i, card in enumerate(cards):
        fp = (card.get('frente_pergunta') or '').strip()
        vr = (card.get('verso_resposta') or '').strip()
        if not fp or not vr:
            raise ValueError(f"Card {i}: 'frente_pergunta' e 'verso_resposta' são obrigatórios")
        tipo = card.get('tipo') or 'base'

        # Idempotência: pula se já existe card de mesma altura (tipo) com a mesma pergunta no tema.
        c.execute("SELECT id FROM flashcards WHERE tema_id=? AND frente_pergunta=? AND tipo=?",
                  (tema_id, fp, tipo))
        existing = c.fetchone()
        if existing:
            print(f"  [SKIP] já existe card '{tipo}' [id {existing[0]}]: \"{fp[:55]}...\"")
            n_skip += 1
            continue

        print(f"  [NOVO] {tipo}: \"{fp[:60]}...\"")
        if not args.dry_run:
            c.execute(
                "INSERT INTO flashcards (questao_id, tema_id, tipo, frente_contexto, "
                "frente_pergunta, verso_resposta, verso_regra_mestre, verso_armadilha, "
                "quality_source, needs_qualitative) "
                "VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, 'qualitative', 0)",
                (tema_id, tipo, card.get('frente_contexto') or '', fp, vr,
                 card.get('verso_regra_mestre') or '', card.get('verso_armadilha') or ''))
            card_id = c.lastrowid
            c.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (?, 0, ?)",
                      (card_id, datetime.now()))

        n_novos += 1

    if not args.dry_run:
        conn.commit()
        print(f"\nCommitado: {n_novos} cards de andaime novos, {n_skip} pulados (já existiam). tema_id={tema_id}.")
    else:
        print(f"\n(dry-run) {n_novos} seriam criados, {n_skip} pulados. Nada gravado.")
    conn.close()


if __name__ == '__main__':
    main()
