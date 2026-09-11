"""importar_sessoes.py — importa volume de sessões em lote a partir de JSON.

Wrapper fino sobre ``registrar()`` de ``registrar_sessao_bulk.py``: lê um JSON
com linhas já mapeadas de uma planilha (pelo agente) e registra cada uma em
``sessoes_bulk``, com validação e resumo. A persistência canônica e a
idempotência vêm de ``registrar()`` — este script não reimplementa nada disso.

Uso:
    python tools/importar_sessoes.py --rows-file <linhas.json>
    python tools/importar_sessoes.py --snapshot --total N --ultimo-lancamento AAAA-MM-DD
    python tools/importar_sessoes.py --show-snapshot

Cada linha do JSON: {sessao:int, area:str, feitas:int, acertos:int, data?:str, obs?:str}

O fluxo agêntico completo (autenticar Google Drive via /mcp → ler a planilha →
mapear colunas → normalizar área → gravar) está em
``.claude/commands/importar-planilha.md``.

**Snapshot da planilha (B3/F35, s176).** O mesmo momento em que o agente lê a
planilha é o único em que os números dela existem -- então é aqui que o
snapshot é gravado (`preparacao_estado.planilha_snapshot`). Ele não importa
volume: serve ao reconcile W1, que passa a REPORTAR no boot (`day_plan
--planilha`) o delta planilha x db e a **idade da planilha**. Sem snapshot, o
boot diz `NAO MEDIDO` -- nunca assume delta zero.
"""
import argparse
import json
import os
import sys
from datetime import date

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

import app.utils.db as db  # noqa: E402
from tools.registrar_sessao_bulk import registrar, AREAS_VALIDAS  # noqa: E402

CHAVE_SNAPSHOT = "planilha_snapshot"


def montar_snapshot(total=None, por_area=None, ultimo_lancamento=None, hoje=None):
    """Valida e monta o payload do snapshot da planilha. Puro -- sem db, testável.

    Levanta ValueError com os dois números na mensagem quando a planilha é
    internamente inconsistente (DoD 5): `total` declarado que não bate com a
    soma das abas por disciplina é exatamente o bug de fórmula do Quadro Geral
    achado na s075 (Obstetrícia somava acertos). Gravar um dado que já se sabe
    torto é pior do que não gravar -- o relatório do boot herdaria o erro com a
    mesma confiança de um dado bom.
    """
    hoje = hoje or date.today()
    if por_area is not None:
        if not isinstance(por_area, dict) or not por_area:
            raise ValueError("--por-area precisa ser um objeto JSON {area: feitas} nao vazio")
        limpo = {}
        for area, feitas in por_area.items():
            try:
                n = int(feitas)
            except (TypeError, ValueError):
                raise ValueError(f"valor nao numerico em --por-area: {area!r} -> {feitas!r}")
            if n < 0:
                raise ValueError(f"valor negativo em --por-area: {area!r} -> {n}")
            limpo[str(area).strip()] = n
        por_area = limpo
        soma = sum(por_area.values())
        if total is None:
            total = soma
        elif int(total) != soma:
            raise ValueError(
                f"planilha internamente inconsistente: --total {int(total)} x soma das "
                f"{len(por_area)} abas {soma} (delta {int(total) - soma}). As abas por "
                "disciplina sao autoritativas (reconcile-contract W1); conferir o Quadro Geral")
    if total is None:
        raise ValueError("informe --total ou --por-area")
    total = int(total)
    if total < 0:
        raise ValueError(f"--total negativo: {total}")
    if not ultimo_lancamento:
        raise ValueError("--ultimo-lancamento e obrigatorio: e a IDADE da planilha (F35)")
    try:
        ultimo = date.fromisoformat(str(ultimo_lancamento))
    except ValueError:
        raise ValueError(f"--ultimo-lancamento nao e AAAA-MM-DD: {ultimo_lancamento!r}")
    if ultimo > hoje:
        raise ValueError(f"--ultimo-lancamento no futuro: {ultimo.isoformat()} > {hoje.isoformat()}")
    return {"total": total, "por_area": por_area,
            "ultimo_lancamento": ultimo.isoformat(),
            "lido_em": db.agora().isoformat(timespec="seconds"),
            "fonte_viva": True, "motivo_abandono": None, "declarado_em": None}


def ler_snapshot():
    """Snapshot cru gravado, ou None. Nunca levanta -- o boot não quebra por isso."""
    try:
        item = db.get_preparacao(CHAVE_SNAPSHOT)
        return json.loads(item["valor"]) if item else None
    except Exception:
        return None


def gravar_snapshot(snap, fonte="agente_planilha"):
    db.set_preparacao(CHAVE_SNAPSHOT, json.dumps(snap, ensure_ascii=False), fonte=fonte)


def declarar_abandono(motivo, hoje=None):
    """Registra a resposta do operador a 'a planilha ainda e fonte?' (Tier 2.4).

    Muda o PESO do relatório (o boot para de cobrar), nunca o mecanismo: o
    último delta medido continua gravado e continua sendo exibido.
    """
    hoje = hoje or date.today()
    snap = ler_snapshot() or {"total": None, "por_area": None, "ultimo_lancamento": None,
                              "lido_em": None}
    snap.update({"fonte_viva": False, "motivo_abandono": str(motivo).strip(),
                 "declarado_em": hoje.isoformat()})
    gravar_snapshot(snap, fonte="operador")
    return snap


def _carregar_por_area(bruto):
    """JSON inline ou @caminho.json."""
    if bruto is None:
        return None
    if bruto.startswith("@"):
        with open(bruto[1:], encoding="utf-8") as fh:
            return json.load(fh)
    return json.loads(bruto)


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
        description="Importa volume de sessões em lote (JSON) para sessoes_bulk; "
                    "e grava o snapshot da planilha que alimenta o reconcile W1 (F35)."
    )
    parser.add_argument("--rows-file", dest="rows_file",
                        help="Path do JSON com a lista de linhas mapeadas")
    parser.add_argument("--snapshot", action="store_true",
                        help="Grava o snapshot da planilha (nao importa volume): "
                             "--total/--por-area + --ultimo-lancamento")
    parser.add_argument("--show-snapshot", action="store_true", dest="show_snapshot",
                        help="Imprime o snapshot gravado (JSON) e sai")
    parser.add_argument("--total", type=int, default=None,
                        help="Total de questoes na planilha (opcional se --por-area)")
    parser.add_argument("--por-area", dest="por_area", default=None, metavar="JSON",
                        help='Somas das ABAS por disciplina: \'{"Pediatria": 512}\' ou @arquivo.json '
                             "(autoritativas por W1; o Quadro Geral ja teve bug de formula)")
    parser.add_argument("--ultimo-lancamento", dest="ultimo_lancamento", default=None,
                        metavar="AAAA-MM-DD",
                        help="Data da ultima tarefa lancada DENTRO da planilha (a idade dela)")
    parser.add_argument("--abandonada", default=None, metavar="MOTIVO",
                        help="Declara que a planilha deixou de ser fonte (resposta do operador): "
                             "o boot para de cobrar e mantem o ultimo delta medido")
    args = parser.parse_args()

    if args.show_snapshot:
        print(json.dumps(ler_snapshot(), ensure_ascii=False, indent=2))
        return 0

    if args.abandonada:
        snap = declarar_abandono(args.abandonada)
        print(f"[OK] planilha declarada ABANDONADA em {snap['declarado_em']}: {snap['motivo_abandono']}")
        print("     O reconcile W1 segue reportando -- suspenso, nao desligado.")
        return 0

    if args.snapshot:
        try:
            snap = montar_snapshot(total=args.total,
                                   por_area=_carregar_por_area(args.por_area),
                                   ultimo_lancamento=args.ultimo_lancamento)
        except ValueError as e:
            print(f"[ERRO] snapshot recusado: {e}")
            return 2
        gravar_snapshot(snap)
        abas = f" · {len(snap['por_area'])} abas" if snap["por_area"] else " · SEM detalhe por area"
        print(f"[OK] snapshot da planilha: {snap['total']}q{abas} · ultimo lancamento "
              f"{snap['ultimo_lancamento']} · lido em {snap['lido_em'][:10]}")
        print("     Confira o reconcile: python tools/day_plan.py --planilha")
        return 0

    if not args.rows_file:
        parser.error("informe --rows-file, --snapshot, --show-snapshot ou --abandonada")

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
