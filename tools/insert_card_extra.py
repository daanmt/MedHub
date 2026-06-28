"""insert_card_extra.py — insere cards adicionais vinculados a um questao_id EXISTENTE.

Para atomização na curadoria (s097): quando reforjar um card gera um 2o conceito do
mesmo erro, este CLI cria o flashcard + fsrs_cards herdando o questao_id/tema_id do
original (diferente de insert_questao.py, que cria uma nova questao). Idempotente por
(questao_id, frente_pergunta). --dry-run é o default.

JSON de entrada: lista de
  {questao_id, tema_id, tipo?, frente_contexto?, frente_pergunta, verso_resposta,
   verso_regra_mestre?, verso_armadilha?, origem_card?}

Uso:
    python tools/insert_card_extra.py --from cards.json            # dry-run
    python tools/insert_card_extra.py --from cards.json --apply
"""
import sqlite3, json, argparse, os, sys
from datetime import datetime

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--from', dest='src', required=True)
    ap.add_argument('--apply', action='store_true', help='Grava (default: dry-run)')
    args = ap.parse_args()
    dry = not args.apply

    cards = json.load(open(args.src, encoding='utf-8'))
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    ins = skip = 0

    for c in cards:
        qid, tid = c.get('questao_id'), c.get('tema_id')
        if qid is None or tid is None:
            print(f"  [SKIP] sem questao_id/tema_id: {c.get('frente_pergunta','')[:50]}")
            skip += 1
            continue
        ex = cur.execute("SELECT id FROM flashcards WHERE questao_id=? AND frente_pergunta=?",
                         (qid, c['frente_pergunta'])).fetchone()
        if ex:
            print(f"  [SKIP] já existe card {ex[0]} (questao {qid})")
            skip += 1
            continue
        print(f"  [INSERT] questao {qid} tema {tid} (origem #{c.get('origem_card')}): {c['frente_pergunta'][:60]}")
        if not dry:
            cur.execute(
                "INSERT INTO flashcards (questao_id, tema_id, tipo, frente_contexto, frente_pergunta, "
                "verso_resposta, verso_regra_mestre, verso_armadilha, quality_source, needs_qualitative, card_version) "
                "VALUES (?,?,?,?,?,?,?,?, 'qualitative', 0, 1)",
                (qid, tid, c.get('tipo', 'conteudo'), c.get('frente_contexto', ''), c['frente_pergunta'],
                 c['verso_resposta'], c.get('verso_regra_mestre', ''), c.get('verso_armadilha', '')))
            cid = cur.lastrowid
            cur.execute("INSERT INTO fsrs_cards (card_id, state, due) VALUES (?, 0, ?)", (cid, datetime.now()))
        ins += 1

    if not dry:
        conn.commit()
        print(f"\nCommitado: {ins} inseridos, {skip} pulados.")
    else:
        print(f"\n(dry-run) {ins} seriam inseridos, {skip} pulados. Nada gravado.")
    conn.close()


if __name__ == "__main__":
    main()
