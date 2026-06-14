"""Rotina de curadoria de flashcards — refaz cards no padrão qualitativo.

Nascida na sessão 081: a revisão card-a-card expôs uma safra antiga (mar/2026)
com formulação fraca (perguntas circulares, decoreba de ordem, armadilha pedante)
que a auditoria automática (audit_flashcard_quality.py) não detecta — só o olho humano.
Este CLI permite reescrever esses cards in-place, preservando o card_id (e portanto
o estado FSRS), incrementando card_version.

Lê uma lista de edições de um JSON e aplica UPDATE em `flashcards` por card_id.
Cada item: {card_id, contexto?, pergunta?, resposta?, regra?, armadilha?, aposentar?}
  - aposentar=true  -> needs_qualitative=2 (remove da fila); não altera conteúdo.
  - caso contrário  -> atualiza os campos fornecidos, card_version+1,
                       quality_source='qualitative', needs_qualitative=0.

Uso:
  python tools/recurate_cards.py --from tmp/curadoria.json --dry-run
  python tools/recurate_cards.py --from tmp/curadoria.json
"""
import sqlite3
import os
import json
import argparse

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

FIELD_MAP = {
    'contexto': 'frente_contexto',
    'pergunta': 'frente_pergunta',
    'resposta': 'verso_resposta',
    'regra': 'verso_regra_mestre',
    'armadilha': 'verso_armadilha',
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--from', dest='src', required=True, help='JSON com a lista de edições')
    ap.add_argument('--dry-run', action='store_true', help='Mostra o que faria, sem gravar')
    args = ap.parse_args()

    with open(args.src, encoding='utf-8') as f:
        edits = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    n_refeitos = n_aposentados = 0

    for e in edits:
        cid = e['card_id']
        row = c.execute(
            "SELECT frente_pergunta, card_version, needs_qualitative FROM flashcards WHERE id=?",
            (cid,)).fetchone()
        if not row:
            print(f"  [SKIP] card {cid} inexistente")
            continue
        antiga, ver, _ = row[0], (row[1] or 1), row[2]

        if e.get('aposentar'):
            print(f"  [APOSENTAR] card {cid}: \"{(antiga or '')[:55]}...\"")
            if not args.dry_run:
                c.execute("UPDATE flashcards SET needs_qualitative=2 WHERE id=?", (cid,))
            n_aposentados += 1
            continue

        sets, vals, campos = [], [], []
        for k, col in FIELD_MAP.items():
            if e.get(k) is not None:
                sets.append(f"{col}=?")
                vals.append(e[k])
                campos.append(k)
        sets += ["card_version=?", "quality_source=?", "needs_qualitative=?"]
        vals += [ver + 1, 'qualitative', 0]
        vals.append(cid)
        print(f"  [REFAZER] card {cid} v{ver}->v{ver+1} | campos: {', '.join(campos)}")
        if not args.dry_run:
            c.execute(f"UPDATE flashcards SET {', '.join(sets)} WHERE id=?", vals)
        n_refeitos += 1

    if not args.dry_run:
        conn.commit()
        print(f"\nCommitado: {n_refeitos} refeitos, {n_aposentados} aposentados.")
    else:
        print(f"\n(dry-run) {n_refeitos} seriam refeitos, {n_aposentados} aposentados. Nada gravado.")
    conn.close()


if __name__ == '__main__':
    main()
