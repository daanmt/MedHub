"""importar_sessoes.py — importa volume de sessões em lote a partir de JSON.

Wrapper fino sobre ``registrar()`` de ``registrar_sessao_bulk.py``: lê um JSON
com linhas já mapeadas de uma planilha (pelo agente) e registra cada uma em
``sessoes_bulk``, com validação e resumo. A persistência canônica e a
idempotência vêm de ``registrar()`` — este script não reimplementa nada disso.

Uso:
    python tools/importar_sessoes.py --rows-file <linhas.json>

Cada linha do JSON: {sessao:int, area:str, feitas:int, acertos:int, data?:str, obs?:str}

O fluxo agêntico completo (autenticar Google Drive via /mcp → ler a planilha →
mapear colunas → normalizar área → gravar) está em
``.claude/commands/importar-planilha.md``.
"""
import argparse
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.registrar_sessao_bulk import registrar, AREAS_VALIDAS  # noqa: E402


def importar(rows):
    """Registra cada linha válida; reporta as inválidas sem abortar o lote.

    Returns (inseridas, puladas, invalidas) onde invalidas é lista de
    (indice, motivo).
    """
    inseridas, puladas, invalidas = 0, 0, []
    for i, r in enumerate(rows):
        area = (r.get("area") or "").strip()
        try:
            sessao = int(r["sessao"])
            feitas = int(r["feitas"])
            acertos = int(r["acertos"])
        except (KeyError, TypeError, ValueError):
            invalidas.append((i, "campos sessao/feitas/acertos ausentes ou invalidos"))
            continue
        if area not in AREAS_VALIDAS:
            invalidas.append((i, f"area invalida: {area!r}"))
            continue
        if acertos > feitas:
            invalidas.append((i, f"acertos ({acertos}) > feitas ({feitas})"))
            continue
        ok = registrar(sessao_num=sessao, area=area, feitas=feitas, acertos=acertos,
                       data=r.get("data"), obs=r.get("obs", ""))
        if ok:
            inseridas += 1
        else:
            puladas += 1  # já existia (idempotência de registrar)
    return inseridas, puladas, invalidas


def main():
    parser = argparse.ArgumentParser(
        description="Importa volume de sessões em lote (JSON) para sessoes_bulk."
    )
    parser.add_argument("--rows-file", dest="rows_file", required=True,
                        help="Path do JSON com a lista de linhas mapeadas")
    args = parser.parse_args()

    with open(args.rows_file, encoding="utf-8") as fh:
        rows = json.load(fh)

    inseridas, puladas, invalidas = importar(rows)
    print(f"\n== Import: {inseridas} inseridas | {puladas} puladas (ja existiam) | "
          f"{len(invalidas)} invalidas ==")
    for i, motivo in invalidas:
        print(f"  [linha {i}] {motivo}")


if __name__ == "__main__":
    main()
