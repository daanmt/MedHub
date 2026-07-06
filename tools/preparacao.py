"""
preparacao.py -- posicao SSOT da preparacao no cronograma (PRD orquestracao, part-1).

A semana de conteudo vive em ipub.db (tabela preparacao_estado), gravada por
comando explicito -- nunca mais parseada de texto (op-3 do ledger). day_plan e
auto_check leem daqui; o HANDOFF passa a receber a posicao como SAIDA derivada
(--handoff-block), nunca como input.

Uso:
    python tools/preparacao.py --set-semana 12 [--fonte operador]
    python tools/preparacao.py --show
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

import app.utils.db as db  # noqa: E402


def main():
    ap = argparse.ArgumentParser(
        description="Posicao SSOT da preparacao (semana de conteudo do cronograma).")
    acao = ap.add_mutually_exclusive_group(required=True)
    acao.add_argument("--set-semana", type=int, metavar="N", dest="set_semana",
                      help="Grava a semana de conteudo atual (ex.: 12)")
    acao.add_argument("--show", action="store_true",
                      help="Exibe a posicao registrada")
    ap.add_argument("--fonte", default="operador",
                    help="Origem da atualizacao (default: operador)")
    args = ap.parse_args()

    if args.set_semana is not None:
        if args.set_semana < 1:
            print("[ERRO] Semana deve ser >= 1.")
            sys.exit(2)
        db.set_preparacao("semana_conteudo", args.set_semana, fonte=args.fonte)
        print("[OK] Posicao registrada: semana de conteudo S%d (fonte: %s)"
              % (args.set_semana, args.fonte))
        return

    item = db.get_preparacao("semana_conteudo")
    if not item:
        print("[INFO] Nenhuma posicao registrada. Use --set-semana N.")
        return
    print("Posicao: semana de conteudo S%s" % item["valor"])
    print("  atualizado_em: %s | fonte: %s" % (item["atualizado_em"], item["fonte"] or "-"))


if __name__ == "__main__":
    main()
