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
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card_checks  # gate de qualidade (part-4) — mesma biblioteca dos demais writers

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')

FIELD_MAP = {
    'contexto': 'frente_contexto',
    'pergunta': 'frente_pergunta',
    'resposta': 'verso_resposta',
    'regra': 'verso_regra_mestre',
    'armadilha': 'verso_armadilha',
    'tipo': 'tipo',
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--from', dest='src', required=True, help='JSON com a lista de edições')
    ap.add_argument('--dry-run', action='store_true', help='Mostra o que faria, sem gravar')
    args = ap.parse_args()

    with open(args.src, encoding='utf-8') as f:
        edits = json.load(f)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")  # part-4: FKs impostas
    c = conn.cursor()
    n_refeitos = n_aposentados = n_rejeitados = 0

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
        card_eq = {}
        for k, col in FIELD_MAP.items():
            if e.get(k) is not None:
                sets.append(f"{col}=?")
                vals.append(e[k])
                campos.append(k)
                card_eq[col] = e[k]

        # part-4: fim do no-op disfarcado — item sem campo valido NAO executa
        # UPDATE, NAO incrementa card_version, NAO flipa quality_source.
        if not campos:
            print(f"  [ERRO] card {cid}: nenhum campo valido "
                  f"({', '.join(sorted(FIELD_MAP))}) — item rejeitado, nada aplicado.")
            n_rejeitados += 1
            continue

        # Gate de qualidade (part-4) sobre os campos PRESENTES (edicao parcial
        # e legitima — nao exigir campos que o item nao esta alterando).
        erros_item = card_checks.checar_encoding(card_eq)
        for k, col in (("pergunta", "frente_pergunta"), ("resposta", "verso_resposta")):
            if e.get(k) is not None and not str(e[k]).strip():
                erros_item.append(f"{col} vazia")
        if card_eq.get("frente_pergunta"):
            t = card_checks.checar_pergunta_template(card_eq)
            if t:
                erros_item.append(t)
            emb = card_checks.checar_resposta_embutida(card_eq)
            if emb:
                erros_item.append(emb)
        if erros_item:
            print(f"  [ERRO] card {cid}: {' | '.join(erros_item)} — item rejeitado, nada aplicado.")
            n_rejeitados += 1
            continue

        sets += ["card_version=?", "quality_source=?", "needs_qualitative=?"]
        vals += [ver + 1, 'qualitative', 0]
        vals.append(cid)
        print(f"  [REFAZER] card {cid} v{ver}->v{ver+1} | campos: {', '.join(campos)}")
        if not args.dry_run:
            c.execute(f"UPDATE flashcards SET {', '.join(sets)} WHERE id=?", vals)
        n_refeitos += 1

    if not args.dry_run:
        conn.commit()
        print(f"\nCommitado: {n_refeitos} refeitos, {n_aposentados} aposentados, "
              f"{n_rejeitados} rejeitado(s) pelo gate.")
    else:
        print(f"\n(dry-run) {n_refeitos} seriam refeitos, {n_aposentados} aposentados, "
              f"{n_rejeitados} rejeitado(s). Nada gravado.")
    conn.close()
    if n_rejeitados:
        sys.exit(1)  # part-4: rejeicao e visivel no exit code (fail-loud)


if __name__ == '__main__':
    main()
