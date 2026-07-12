"""Rito de REFLECTION da propria execucao (degrau 4/4 da auto-evolucao).

No FECHAMENTO de sessao de engenharia (baixa frequencia; nunca em commit/boot),
consome o ledger-of-self (degrau 2) e produz 1 datum honesto sobre a execucao
das rotinas: o que recorreu, o que degradou, o que resolveu. Com sinal, emite
UMA proposta de proximo ciclo ancorada em evidencia (fingerprint) -- e PARA:
o rito nao executa nada; o portao de execucao e humano.

Honestidade obrigatoria: sem mudanca no ledger desde o ultimo datum, o datum e
literalmente "(sem sinal novo)" e o rito para. Nunca fabricar sinal. Proposta
sem evidencia referenciavel = recusada. Score v1 = recorrencia pura.

Fronteira clinica: reflete sobre engenharia (drift, WARNs, recorrencia) --
NUNCA sobre erros clinicos do usuario nem conteudo medico.

GATE ANTI-DECORATIVO (herdado do arquiteto ai-eng): se em ate 3 execucoes
REAIS este rito nao alterar nenhuma decisao de ciclo observavel, REMOVER a
tool -- reflexo que nao muda decisao e decoracao. Medir nas 3 primeiras.

Escreve APENAS history/reflection_data.jsonl. Uso: python tools/reflect.py
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).parent))
from ledger_self import abertos, validar_jsonl  # noqa: E402

ROOT_DIR = Path(__file__).parent.parent.resolve()
DATA_NAME = "reflection_data.jsonl"
SEM_SINAL = "(sem sinal novo)"


def _data_path(root=None):
    root = Path(root).resolve() if root else ROOT_DIR
    return root / "history" / DATA_NAME


def _ultimo_datum(root=None):
    p = _data_path(root)
    if not p.exists():
        return None
    ultimo = None
    for linha in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if not linha.strip():
            continue
        try:
            ultimo = json.loads(linha)
        except Exception:
            print(f"[WARN] REFLECT: linha corrompida em {DATA_NAME} -- ignorada.")
    return ultimo


def _candidato_valido(v):
    """Proposta exige evidencia integra: fingerprint + check + occurrences>=1."""
    try:
        return bool(v.get("fingerprint")) and bool(v.get("check")) and \
            int(v.get("occurrences", 0)) >= 1
    except Exception:
        return False


def _aderencia_contexto():
    """Enriquecimento OPCIONAL (part-2): blocos pulados em dias FECHADOS da
    ultima semana (nunca o dia corrente -- nota do audit part-2). Falha -> None."""
    try:
        from datetime import date
        from day_plan import aderencia
        ontem = date.fromordinal(date.today().toordinal() - 1)
        dias = aderencia(fim=ontem, semanas=1)
        pulados = sum(1 for d in dias for b in d.get("blocos", [])
                      if b.get("status") == "pulado")
        com_plano = sum(1 for d in dias if not d.get("sem_plano"))
        return {"dias_com_plano": com_plano, "blocos_pulados": pulados}
    except Exception:
        return None


def run_reflect(root=None):
    """Executa o rito. Retorna o datum gravado. Escreve SO o proprio datum."""
    agora = datetime.now(timezone.utc).isoformat(timespec="seconds")
    # try separado por input: estado corrompido nao pode apagar o sinal dos
    # eventos (e vice-versa) -- degradacao independente, WARN visivel.
    try:
        eventos, _ = validar_jsonl(root=root)
    except Exception as e:
        print(f"[WARN] REFLECT: eventos do ledger-of-self ilegiveis ({e}).")
        eventos = []
    try:
        vivos = abertos(root=root)
    except Exception as e:
        print(f"[WARN] REFLECT: estado do ledger-of-self ilegivel ({e}).")
        vivos = []

    anterior = _ultimo_datum(root)
    desde = (anterior or {}).get("ts")
    snapshot_anterior = (anterior or {}).get("snapshot") or {}

    novos = [e for e in eventos if desde is None or e.get("ts", "") > desde]
    snapshot = {v["fingerprint"]: int(v.get("occurrences", 1)) for v in vivos
                if v.get("fingerprint")}
    recorreu = {fp: occ for fp, occ in snapshot.items()
                if occ != snapshot_anterior.get(fp)}

    sinal = bool(novos) or bool(recorreu)
    datum = {"ts": agora, "janela_desde": desde, "sinal": sinal,
             "snapshot": snapshot, "proposta": None}

    if not sinal:
        datum["resumo"] = SEM_SINAL
    else:
        achados = [{"fingerprint": v["fingerprint"], "check": v.get("check"),
                    "alvo": v.get("alvo"), "occurrences": v.get("occurrences")}
                   for v in vivos]
        datum["achados"] = achados
        datum["eventos_na_janela"] = {"opened": sum(1 for e in novos
                                                    if e.get("event") == "opened"),
                                      "resolved": sum(1 for e in novos
                                                      if e.get("event") == "resolved")}
        candidatos = [v for v in vivos if _candidato_valido(v)]
        if candidatos:
            top = max(candidatos, key=lambda v: int(v.get("occurrences", 1)))
            datum["proposta"] = {
                "titulo": f"atacar achado recorrente: {top['check']} :: {top['alvo']}",
                "evidencia": [top["fingerprint"]],
                "score_recorrencia": int(top.get("occurrences", 1)),
            }
            datum["resumo"] = (f"{len(vivos)} aberto(s); "
                               f"{len(novos)} evento(s) na janela; proposta ancorada "
                               f"em {top['fingerprint']} ({top['occurrences']}x)")
        else:
            datum["resumo"] = (f"{len(novos)} evento(s) na janela; sem candidato com "
                               f"evidencia integra -- nenhuma proposta (anti-fabricacao)")
        ctx = _aderencia_contexto() if root is None else None
        if ctx:
            datum["contexto_aderencia"] = ctx

    p = _data_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(datum, ensure_ascii=False) + "\n")
    return datum


def main():
    ap = argparse.ArgumentParser(
        description="REFLECTION da execucao de engenharia (rito de fechamento; "
                    "gated -- propoe, nunca executa).")
    ap.add_argument("--json", action="store_true", help="imprime o datum cru")
    args = ap.parse_args()
    datum = run_reflect()
    if args.json:
        print(json.dumps(datum, ensure_ascii=False, indent=2))
        return 0
    print(f"reflect: {datum.get('resumo', SEM_SINAL)}")
    if datum.get("proposta"):
        pr = datum["proposta"]
        print(f"  proposta (gated -- aguarda go humano): {pr['titulo']}")
        print(f"  evidencia: {', '.join(pr['evidencia'])} · "
              f"recorrencia {pr['score_recorrencia']}x")
    return 0


if __name__ == "__main__":
    sys.exit(main())
