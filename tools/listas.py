#!/usr/bin/env python3
"""listas.py -- ledger de LISTAS de exercicios: quais listas do plano ja foram feitas,
com quantas questoes e com que acerto, sem ler o Drive.

Spec: `.vibeflow/specs/plano-ssot-e-cards-v2-part-6.md`. Depende da part-2
(`plano_tarefas`) e da coluna `sessoes_bulk.tarefa_id` desta parte.

O problema que este CLI fecha: a SSOT volumetrica (`sessoes_bulk`) sempre soube
QUANTAS questoes foram feitas e nunca soube de QUAL lista -- o elo morava em prosa
livre (`observacoes`) e a unica visao "por lista" era o Dashboard do Drive, que vai
ser congelado. Com o elo em coluna, "listas feitas x previstas, com acertos" vira
consulta local.

Tres modos, exatamente UM por invocacao:

    --backfill    casa `observacoes` com `plano_tarefas.tema` e grava o vinculo das
                  sessoes INEQUIVOCAS. Dry-run e o default; `--apply` exige
                  `--expect N` (COUNT-ASSERT, AGENTE.md secao 10.7).
    --progresso   por tarefa: url_lista | q_previstas | feitas | acertos | %, com
                  totais por bloco UERJ e o delta contra o orcamento da Fase 1.
    --pendentes   as listas previstas que ainda nao tem sessao nenhuma vinculada.

🔴 O backfill NUNCA chuta. O casamento e por normalizacao (casefold + sem acento) e
substring EXATA do tema dentro da observacao, delimitada por fronteira de palavra --
nao ha fuzzy, nao ha stemming, nao ha "melhor candidata". A s183 mediu 54/735 nomes
divergentes entre as fontes: fuzzy compraria falso vinculo em tema homonimo
(Pneumonias na Infancia x Pneumonias Bacterianas). Duas candidatas ou mais = AMBIGUA,
fica NULL e sai na lista para o humano decidir (`registrar_sessao_bulk.py --vincular`).

Limites declarados (verification-stack, AGENTE.md 10.8):
  - tema BUNDLADO ("A; B") e casado inteiro, nunca por partes -- quebrar em partes
    multiplicaria candidatas e o ganho seria chute disfarcado de cobertura;
  - sessao de `area='Simulado'` nao tem lista no plano por definicao: sai fora do
    casamento e e reportada a parte como termometro;
  - o vinculo nao conclui tarefa nenhuma (isso e `plano.py --concluir`), e este CLI
    e read-only fora do `--backfill --apply`.

Camada fina sobre `app.utils.db` -- nao importa `sqlite3` e nao tem escrita propria: o
backfill grava por `db.vincular_sessao_tarefa`. A normalizacao e a de `tools/plano.py`
(uma funcao so, ja testada). Assinatura canonica em `.claude/commands/engenharia-cli.md`.

Uso:
    python tools/listas.py --backfill --dry-run
    python tools/listas.py --backfill --apply --expect 31
    python tools/listas.py --progresso [--bloco MFC] [--semana 3] [--json]
    python tools/listas.py --pendentes [--bloco PED] [--json]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.utils import db  # noqa: E402
import plano  # noqa: E402

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

#: Orcamento de questoes da Fase 1 (semanas 1-7, ate a prova da UERJ em 01/11),
#: medido em `history/session_183.md` secao 3. Numero de PLANEJAMENTO: o delta que
#: este CLI imprime e "quanto ja foi feito do que foi orcado", nunca uma meta nova.
ORCAMENTO_FASE1 = 2760

#: Fronteira da Fase 1 no `semana_plano` (part-2: Fase 1 = 7 semanas ate 01/11).
SEMANAS_FASE1 = 7

#: Area cujas sessoes sao termometro e nao lista do plano (Risk da spec).
AREA_TERMOMETRO = "Simulado"

BLOCOS = ("MFC", "PED", "CIR", "GO", "CM")


# ------------------------------------------------------------------ casamento

def casa_tema(observacoes, tema):
    """A observacao da sessao contem o tema como substring EXATA (pos-normalizacao)?

    Fronteira de palavra dos dois lados: sem isso um tema curto ("SUA") casaria dentro
    de outra palavra e o "casamento exato" seria exato so no nome. Normalizacao unica:
    `plano.normalizar` (casefold, sem acento, `-`/`|` viram espaco).
    """
    obs = plano.normalizar(observacoes)
    alvo = plano.normalizar(tema)
    if not obs or not alvo:
        return False
    inicio = obs.find(alvo)
    while inicio != -1:
        fim = inicio + len(alvo)
        antes_ok = inicio == 0 or not obs[inicio - 1].isalnum()
        depois_ok = fim == len(obs) or not obs[fim].isalnum()
        if antes_ok and depois_ok:
            return True
        inicio = obs.find(alvo, inicio + 1)
    return False


def candidatas(sessao, tarefas):
    """Tarefas do plano que respondem por esta sessao: MESMA area e tema contido na
    observacao. Devolve a lista inteira -- quem decide o desfecho e `classificar`."""
    area = sessao.get("area")
    return [t for t in tarefas
            if t.get("area") and t.get("tema")
            and str(t["area"]) == str(area)
            and casa_tema(sessao.get("observacoes"), t["tema"])]


def classificar(sessoes, tarefas):
    """Os 3 desfechos do backfill + os termometros, sem tocar no banco.

    `{casadas: [(sessao, tarefa)], ambiguas: [(sessao, [tarefas])],
      sem_match: [sessao], termometros: [sessao]}`.
    """
    saida = {"casadas": [], "ambiguas": [], "sem_match": [], "termometros": []}
    for s in sessoes:
        if s.get("tarefa_id") is not None:
            continue                       # ja vinculada: backfill so preenche NULL
        if str(s.get("area")) == AREA_TERMOMETRO:
            saida["termometros"].append(s)
            continue
        cands = candidatas(s, tarefas)
        if len(cands) == 1:
            saida["casadas"].append((s, cands[0]))
        elif len(cands) > 1:
            saida["ambiguas"].append((s, cands))
        else:
            saida["sem_match"].append(s)
    return saida


def _rotulo(sessao):
    obs = (sessao.get("observacoes") or "").strip()
    if len(obs) > 62:
        obs = obs[:59] + "..."
    return "#%-4d %-10s %-12s %s" % (sessao["id"], sessao.get("data_sessao") or "?",
                                     sessao.get("area") or "?", obs or "(sem observacao)")


# -------------------------------------------------------------------- backfill

def backfill(apply=False, expect=None):
    """Rito COUNT-ASSERT da AGENTE.md secao 10.7: mede, imprime, e so grava quando o
    numero declarado bate com o medido NA HORA. Devolve `(exit_code, medida)`."""
    tarefas = db.plano_listar()
    sessoes = db.sessoes_bulk_listar()
    r = classificar(sessoes, tarefas)
    n_casadas = len(r["casadas"])

    print()
    print("=" * 74)
    print("  Backfill do elo sessao -> lista  (sessoes_bulk.tarefa_id)")
    print("=" * 74)
    print("  sessoes sem vinculo : %d   (de %d em sessoes_bulk)" % (
        n_casadas + len(r["ambiguas"]) + len(r["sem_match"]) + len(r["termometros"]),
        len(sessoes)))
    print("  tarefas no plano    : %d" % len(tarefas))
    print()
    print("  %d casadas / %d ambiguas (2+ candidatas) / %d sem match" % (
        n_casadas, len(r["ambiguas"]), len(r["sem_match"])))
    print("  + %d termometro(s) (area=%s: nao tem lista no plano, ficam NULL por regra)"
          % (len(r["termometros"]), AREA_TERMOMETRO))
    print()

    if r["casadas"]:
        print("  CASADAS (inequivocas -- sao estas que o --apply grava):")
        for s, t in r["casadas"]:
            print("    %s" % _rotulo(s))
            print("        -> tarefa #%d | %s | %s" % (t["id"], t.get("tipo_norm") or "?",
                                                       t.get("tema")))
        print()
    if r["ambiguas"]:
        print("  AMBIGUAS (ficam NULL -- decida com "
              "`registrar_sessao_bulk.py --vincular ID --tarefa ID`):")
        for s, cands in r["ambiguas"]:
            print("    %s" % _rotulo(s))
            print("        candidatas: %s" % ", ".join(
                "#%d (%s, %s)" % (c["id"], c.get("fonte"), c.get("tema")) for c in cands[:6]))
            if len(cands) > 6:
                print("        ... +%d candidata(s)" % (len(cands) - 6))
        print()
    if r["sem_match"]:
        print("  SEM MATCH (ficam NULL -- nome divergente ou observacao vazia):")
        for s in r["sem_match"]:
            print("    %s" % _rotulo(s))
        print()

    if not apply:
        print("  [DRY-RUN] nada gravado. Para gravar: "
              "`python tools/listas.py --backfill --apply --expect %d`" % n_casadas)
        print()
        return 0, r

    if expect is None or int(expect) != n_casadas:
        print("  [RECUSADO] COUNT-ASSERT: --expect %s x %d casadas medidas agora. "
              "Nada gravado." % (expect, n_casadas))
        print()
        return 2, r

    gravadas, recusadas = 0, []
    for s, t in r["casadas"]:
        try:
            db.vincular_sessao_tarefa(s["id"], t["id"])
            gravadas += 1
        except (ValueError, db.VinculoAreaDivergente) as e:
            recusadas.append("sessao %d -> tarefa %d: %s" % (s["id"], t["id"], e))
    print("  [OK] %d vinculo(s) gravado(s)." % gravadas)
    for linha in recusadas:
        print("  [ERRO] %s" % linha)
    print()
    return (0 if not recusadas else 2), r


# ------------------------------------------------------------------- progresso

def _agregar(tarefas, sessoes):
    """Soma `feitas`/`acertos` por tarefa a partir das sessoes VINCULADAS -- a unica
    fonte de volume (AGENTE.md secao 6). `plano_tarefas` nao carrega contagem propria.
    """
    por_tarefa = {}
    for s in sessoes:
        tid = s.get("tarefa_id")
        if tid is None:
            continue
        alvo = por_tarefa.setdefault(int(tid), {"feitas": 0, "acertos": 0, "sessoes": []})
        alvo["feitas"] += int(s.get("questoes_feitas") or 0)
        alvo["acertos"] += int(s.get("questoes_acertadas") or 0)
        alvo["sessoes"].append(s["id"])
    linhas = []
    for t in tarefas:
        agr = por_tarefa.get(int(t["id"]), {"feitas": 0, "acertos": 0, "sessoes": []})
        linhas.append({
            "id": int(t["id"]), "bloco": t.get("bloco"), "semana_plano": t.get("semana_plano"),
            "area": t.get("area"), "tema": t.get("tema"), "tipo_norm": t.get("tipo_norm"),
            "status": t.get("status"), "url_lista": t.get("url_lista"),
            "q_previstas": float(t.get("q_previstas") or 0),
            "feitas": agr["feitas"], "acertos": agr["acertos"],
            "sessoes": agr["sessoes"],
            "pct": round(agr["acertos"] / agr["feitas"] * 100, 1) if agr["feitas"] else None,
        })
    return linhas


def _totais_por_bloco(linhas):
    tot = {}
    for l in linhas:
        b = tot.setdefault(l["bloco"] or "CM", {"tarefas": 0, "q_previstas": 0.0,
                                                "feitas": 0, "acertos": 0})
        b["tarefas"] += 1
        b["q_previstas"] += l["q_previstas"]
        b["feitas"] += l["feitas"]
        b["acertos"] += l["acertos"]
    for b in tot.values():
        b["pct"] = round(b["acertos"] / b["feitas"] * 100, 1) if b["feitas"] else None
    return tot


def _orcamento_fase1(todas_linhas):
    """Delta contra o orcamento da Fase 1 (`history/session_183.md` secao 3). Medido
    sobre o plano INTEIRO das semanas 1-7, nunca sobre o recorte dos filtros -- o
    orcamento e global, e filtrar o denominador daria um percentual bonito e falso."""
    feitas = sum(l["feitas"] for l in todas_linhas
                 if l["semana_plano"] is not None and l["semana_plano"] <= SEMANAS_FASE1)
    return {"orcamento": ORCAMENTO_FASE1, "feitas": feitas,
            "falta": max(ORCAMENTO_FASE1 - feitas, 0),
            "pct": round(feitas / ORCAMENTO_FASE1 * 100, 1) if ORCAMENTO_FASE1 else 0.0}


def _linha_tarefa(l):
    url = l["url_lista"] or "-"
    if len(url) > 34:
        url = url[:31] + "..."
    pct = "%5.1f%%" % l["pct"] if l["pct"] is not None else "    --"
    return "  #%-4d %-3s S%-3s %-30.30s %-34s %6.0f %5d %5d %s" % (
        l["id"], l["bloco"] or "?",
        l["semana_plano"] if l["semana_plano"] is not None else "-",
        l["tema"] or "(sem tema)", url, l["q_previstas"], l["feitas"], l["acertos"], pct)


def _cabecalho_tabela():
    print("  %-5s %-3s %-4s %-30s %-34s %6s %5s %5s %6s" % (
        "id", "blk", "sem", "tema", "url_lista", "q_prev", "feit", "acer", "%"))
    print("  " + "-" * 100)


def progresso(bloco=None, semana=None, como_json=False):
    """Listas FEITAS (ao menos uma sessao vinculada), por tarefa, com totais por bloco
    UERJ e o delta do orcamento da Fase 1. Read-only."""
    sessoes = db.sessoes_bulk_listar()
    todas = _agregar(db.plano_listar(), sessoes)
    filtradas = [l for l in _agregar(db.plano_listar(semana=semana, bloco=bloco), sessoes)
                 if l["feitas"] > 0]
    filtradas.sort(key=lambda l: (l["semana_plano"] is None, l["semana_plano"] or 0, l["id"]))
    soltas = [s for s in sessoes if s.get("tarefa_id") is None]
    vol_solto = sum(int(s.get("questoes_feitas") or 0) for s in soltas)
    payload = {"modo": "progresso", "filtros": {"bloco": bloco, "semana": semana},
               "tarefas": filtradas, "blocos": _totais_por_bloco(filtradas),
               "orcamento_fase1": _orcamento_fase1(todas),
               "sem_vinculo": {"sessoes": len(soltas), "questoes": vol_solto}}
    if como_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return 0, payload

    print()
    print("=" * 74)
    print("  Listas FEITAS -- progresso por tarefa do plano")
    print("=" * 74)
    if not filtradas:
        print("  Nenhuma tarefa com sessao vinculada neste recorte "
              "(rode `--backfill --dry-run`).")
    else:
        _cabecalho_tabela()
        for l in filtradas:
            print(_linha_tarefa(l))
        print()
        print("  Totais por bloco UERJ:")
        for b in BLOCOS:
            t = payload["blocos"].get(b)
            if not t:
                continue
            pct = "%.1f%%" % t["pct"] if t["pct"] is not None else "--"
            print("    %-4s %3d lista(s) | previstas %6.0f | feitas %5d | acertos %5d | %s"
                  % (b, t["tarefas"], t["q_previstas"], t["feitas"], t["acertos"], pct))
    o = payload["orcamento_fase1"]
    print()
    print("  Orcamento Fase 1 (semanas 1-%d, history/session_183.md secao 3): "
          "%d previstas | %d feitas (%.1f%%) | faltam %d"
          % (SEMANAS_FASE1, o["orcamento"], o["feitas"], o["pct"], o["falta"]))
    print("  Volume SEM lista (termometros + nao casadas): %d sessao(oes) / %d questoes"
          % (len(soltas), vol_solto))
    print()
    return 0, payload


def pendentes(bloco=None, semana=None, como_json=False):
    """Listas previstas e ainda sem nenhuma sessao vinculada. Read-only.

    `status='cortada'` fica de fora (saiu do plano por decisao do usuario) e `feita`
    sem sessao vinculada ENTRA, com a marca -- e exatamente a dívida que o vinculo
    existe para expor: tarefa dada como feita cujo volume ninguem consegue apontar.
    """
    sessoes = db.sessoes_bulk_listar()
    todas = _agregar(db.plano_listar(), sessoes)
    linhas = [l for l in _agregar(db.plano_listar(semana=semana, bloco=bloco), sessoes)
              if l["feitas"] == 0 and l["status"] != "cortada"]
    linhas.sort(key=lambda l: (l["semana_plano"] is None, l["semana_plano"] or 0, l["id"]))
    payload = {"modo": "pendentes", "filtros": {"bloco": bloco, "semana": semana},
               "tarefas": linhas, "blocos": _totais_por_bloco(linhas),
               "orcamento_fase1": _orcamento_fase1(todas),
               "feitas_sem_volume": [l["id"] for l in linhas if l["status"] == "feita"]}
    if como_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))
        return 0, payload

    print()
    print("=" * 74)
    print("  Listas PREVISTAS sem sessao vinculada")
    print("=" * 74)
    if not linhas:
        print("  Nenhuma: toda tarefa do recorte tem volume vinculado.")
        print()
        return 0, payload
    _cabecalho_tabela()
    for l in linhas:
        print(_linha_tarefa(l))
    print()
    print("  Totais por bloco UERJ:")
    for b in BLOCOS:
        t = payload["blocos"].get(b)
        if not t:
            continue
        print("    %-4s %3d lista(s) | previstas %6.0f questoes" % (b, t["tarefas"],
                                                                    t["q_previstas"]))
    o = payload["orcamento_fase1"]
    print()
    print("  Orcamento Fase 1 (semanas 1-%d, history/session_183.md secao 3): "
          "%d previstas | %d feitas (%.1f%%) | faltam %d"
          % (SEMANAS_FASE1, o["orcamento"], o["feitas"], o["pct"], o["falta"]))
    marcadas = payload["feitas_sem_volume"]
    if marcadas:
        print()
        print("  🔴 %d tarefa(s) com status='feita' e ZERO volume vinculado "
              "(divida do status aproximado): %s" % (
                  len(marcadas), ", ".join("#%d" % i for i in marcadas[:12])
                  + (", ..." if len(marcadas) > 12 else "")))
    print()
    return 0, payload


# ------------------------------------------------------------------------- CLI

def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Ledger de listas de exercicios (sessoes_bulk.tarefa_id x plano_tarefas).")
    ap.add_argument("--backfill", action="store_true",
                    help="casa observacoes x tema do plano e grava so as inequivocas "
                         "(dry-run e o default)")
    ap.add_argument("--dry-run", action="store_true",
                    help="explicita o default do --backfill: mede e nao grava")
    ap.add_argument("--apply", action="store_true", help="grava (exige --expect N)")
    ap.add_argument("--expect", type=int, metavar="N",
                    help="COUNT-ASSERT: N de sessoes casadas esperadas; difere do "
                         "medido agora -> recusa (exit 2) sem gravar")
    ap.add_argument("--progresso", action="store_true",
                    help="listas feitas por tarefa, com totais por bloco (read-only)")
    ap.add_argument("--pendentes", action="store_true",
                    help="listas previstas sem sessao vinculada (read-only)")
    ap.add_argument("--bloco", choices=list(BLOCOS),
                    help="filtro: bloco de peso UERJ, derivado de area")
    ap.add_argument("--semana", type=int, metavar="N", help="filtro: semana do plano")
    ap.add_argument("--json", action="store_true", help="saida em JSON")
    args = ap.parse_args(argv)

    modos = {"--backfill": args.backfill, "--progresso": args.progresso,
             "--pendentes": args.pendentes}
    ligados = [nome for nome, ativo in modos.items() if ativo]
    if len(ligados) != 1:
        ap.error("informe exatamente UM modo (" + " | ".join(modos) + "); recebido: "
                 + (", ".join(ligados) if ligados else "nenhum"))
    if args.apply and args.dry_run:
        ap.error("--apply e --dry-run sao mutuamente exclusivos")

    if ligados[0] == "--backfill":
        if args.apply and args.expect is None:
            ap.error("--apply exige --expect N")
        code, _ = backfill(apply=args.apply, expect=args.expect)
        return code
    if ligados[0] == "--progresso":
        code, _ = progresso(bloco=args.bloco, semana=args.semana, como_json=args.json)
        return code
    code, _ = pendentes(bloco=args.bloco, semana=args.semana, como_json=args.json)
    return code


if __name__ == "__main__":
    sys.exit(main())
