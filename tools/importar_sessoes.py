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
import json
import os
import sys

# Encoding do terminal Windows pela convencao do repo (auto_check.py:8): o
# `TextIOWrapper` que estava aqui SEQUESTRAVA o stdout global de quem apenas
# IMPORTA o modulo (quebrava qualquer harness que o coletasse). Reconfigurar e
# in-place e no-op quando o stream nao suporta.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
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

    # F60 (descolar part-6): exit simetrico, no padrao do `insert_questao.py`
    # (F27). Lote 100% rejeitado nao e sucesso -- sair 0 ali fazia o chamador
    # headless seguir em frente achando que o volume entrou. Parcial CONTINUA
    # saindo 0: o resumo acima ja conta as rejeitadas, linha a linha.
    if rows and len(invalidas) == len(rows):
        print("[ERRO] 100% das linhas foram rejeitadas -- nada foi importado.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
