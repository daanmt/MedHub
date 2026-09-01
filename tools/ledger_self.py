"""Ledger-of-self: memoria estruturada dos WARNs do harness (degrau 2 da auto-evolucao).

Os checks do auto_check ja DETECTAM inconsistencias; este modulo faz os achados
sobreviverem ao stdout: cada um vira evento com fingerprint, recorrencia e ciclo
de vida (opened -> resolved -> reopened). Dois artefatos, contratos distintos:

  history/ledger_self.jsonl        -- eventos de TRANSICAO, append-only, versionado
  history/ledger_self_state.json   -- estado corrente DERIVADO (occurrences,
                                      last_seen), reescrito a cada run; nao versionado

Fronteira clinica: so achados de execucao/estado do sistema (drift, paridade,
cobertura estrutural). Payloads carregam valores divergentes/paths/labels --
nunca conteudo de card ou resumo. O ledger humano (AUDITORIA_MEDHUB.md) e
INTOCADO por este modulo.

Uso pelo harness: from ledger_self import record  (chamado por check que rodou)
Uso standalone:   python tools/ledger_self.py --list
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

ROOT_DIR = Path(__file__).parent.parent.resolve()
JSONL_NAME = "ledger_self.jsonl"
STATE_NAME = "ledger_self_state.json"


def _paths(root=None):
    root = Path(root).resolve() if root else ROOT_DIR
    hist = root / "history"
    return hist / JSONL_NAME, hist / STATE_NAME


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def fingerprint(check, alvo):
    """Estavel sob re-run: check + alvo normalizado; payload (valores) fica FORA
    para que a mesma divergencia com numeros novos siga sendo o mesmo achado."""
    bruto = f"{check}|{str(alvo).strip().lower()}"
    return hashlib.sha1(bruto.encode("utf-8")).hexdigest()[:12]


def _load_state(state_path):
    if not state_path.exists():
        return {}
    try:
        return json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        print(f"[WARN] LEDGER_SELF: estado derivado ilegivel ({state_path.name}); "
              f"reiniciando estado (o .jsonl de eventos permanece integro).")
        return {}


def _append_event(jsonl_path, evento):
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    with jsonl_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")


def record(check, findings, root=None):
    """Registra o resultado de UM check que RODOU neste run.

    check: tag curta do check (ex.: 'doc_drift', 'session_pointer').
    findings: lista de {'alvo': str, 'payload': dict-opcional}. Vazia = check limpo.

    Transicoes: achado novo -> evento 'opened'; achado que sumiu -> 'resolved';
    achado persistente -> so occurrences/last_seen no estado (zero linhas novas).
    So resolve fingerprints DESTE check (check que nao rodou nao resolve nada).
    Nunca lanca excecao (harness resilience): falha vira WARN no stdout.
    """
    try:
        jsonl_path, state_path = _paths(root)
        state = _load_state(state_path)
        agora = _now()
        vistos = set()
        for f_ in findings:
            alvo = f_.get("alvo", "?")
            payload = f_.get("payload", {})
            fp = fingerprint(check, alvo)
            vistos.add(fp)
            entrada = state.get(fp)
            if entrada and entrada.get("status") == "open":
                entrada["occurrences"] = int(entrada.get("occurrences", 1)) + 1
                entrada["last_seen"] = agora
                entrada["payload"] = payload
            else:
                _append_event(jsonl_path, {"ts": agora, "event": "opened",
                                           "check": check, "fingerprint": fp,
                                           "alvo": alvo, "payload": payload})
                state[fp] = {"check": check, "alvo": alvo, "status": "open",
                             "opened_at": agora, "last_seen": agora,
                             "occurrences": 1, "payload": payload}
        # fingerprints abertos DESTE check que nao apareceram -> resolved
        for fp, entrada in state.items():
            if (entrada.get("check") == check and entrada.get("status") == "open"
                    and fp not in vistos):
                _append_event(jsonl_path, {"ts": agora, "event": "resolved",
                                           "check": check, "fingerprint": fp,
                                           "alvo": entrada.get("alvo", "?")})
                entrada["status"] = "resolved"
                entrada["resolved_at"] = agora
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=1),
                              encoding="utf-8")
    except Exception as e:
        print(f"[WARN] LEDGER_SELF: falha ao registrar ({e}) -- deteccao segue; "
              f"so a memoria deste run se perdeu.")


def abertos(root=None):
    """Achados abertos ordenados por recorrencia (desc) -- o top da divida viva."""
    _, state_path = _paths(root)
    state = _load_state(state_path)
    vivos = [dict(v, fingerprint=k) for k, v in state.items()
             if v.get("status") == "open"]
    return sorted(vivos, key=lambda v: (-int(v.get("occurrences", 1)),
                                        v.get("opened_at", "")))


def _idade_dias(iso_ts):
    """Dias desde um timestamp ISO do ledger; 0 se ilegivel (nunca crash)."""
    try:
        dt = datetime.fromisoformat(str(iso_ts))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return max(0, (datetime.now(timezone.utc) - dt).days)
    except Exception:
        return 0


def painel_divida(root=None, top=5):
    """Bloco DIVIDA (descolar part-1, F54/P5): o LEITOR obrigatorio que as superficies de
    sinal nao tinham -- 279 abertos com o mesmo WARN visto 102x em 36 dias e zero chamadores
    de abertos() em codigo. Ordena por idade x ocorrencias (o antigo E frequente sobe junto).
    Sensor: detecta e reporta, nunca corrige/bloqueia (warn-first). Retorna linhas prontas."""
    linhas = []
    try:
        vivos = abertos(root)
        root_p = Path(root).resolve() if root else ROOT_DIR

        def _score(v):
            return _idade_dias(v.get("opened_at", "")) * int(v.get("occurrences", 1))

        rank = sorted(vivos, key=_score, reverse=True)
        linhas.append(f"== DIVIDA == ({len(vivos)} aberto(s) no ledger-of-self)")
        for v in rank[:top]:
            linhas.append(f"  [{int(v.get('occurrences', 1)):>3}x | {_idade_dias(v.get('opened_at', '')):>3}d] "
                          f"{v.get('check', '?')} :: {v.get('alvo', '?')}")
        if len(rank) > top:
            por_check = {}
            for v in rank[top:]:
                por_check[v.get("check", "?")] = por_check.get(v.get("check", "?"), 0) + 1
            resto = ", ".join(f"{c}: {n}" for c, n in sorted(por_check.items(), key=lambda x: -x[1])[:4])
            linhas.append(f"  (+{len(rank) - top} abertos: {resto})")

        mel = root_p / "history" / "memory_errors.log"
        if mel.exists():
            ls = [l for l in mel.read_text(encoding="utf-8", errors="replace").splitlines() if l.strip()]
            if ls:
                linhas.append(f"  memory_errors.log: {len(ls)} linha(s); ultima: {ls[-1][:90]}")
        aud = root_p / "AUDITORIA_MEDHUB.md"
        if aud.exists():
            linhas.append(f"  AUDITORIA_MEDHUB.md: {aud.stat().st_size / 1024:.0f} KB")
        if len(linhas) == 1:
            linhas.append("  (sem divida registrada)")
    except Exception as e:  # noqa: BLE001 -- painel nunca derruba o harness
        linhas.append(f"== DIVIDA == (painel indisponivel: {e})")
    return linhas


def validar_jsonl(root=None):
    """Le o .jsonl defensivamente; linha corrompida vira WARN, nunca crash.
    Retorna (eventos_validos, linhas_corrompidas)."""
    jsonl_path, _ = _paths(root)
    eventos, corrompidas = [], 0
    if not jsonl_path.exists():
        return eventos, corrompidas
    for i, linha in enumerate(
            jsonl_path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not linha.strip():
            continue
        try:
            eventos.append(json.loads(linha))
        except Exception:
            corrompidas += 1
            print(f"[WARN] LEDGER_SELF: linha {i} do {JSONL_NAME} corrompida -- ignorada.")
    return eventos, corrompidas


def main():
    parser = argparse.ArgumentParser(
        description="Ledger-of-self do harness (achados abertos por recorrencia).")
    parser.add_argument("--list", action="store_true",
                        help="lista achados abertos ordenados por recorrencia")
    parser.add_argument("--json", action="store_true",
                        help="saida machine-readable")
    args = parser.parse_args()
    if not args.list and not args.json:
        parser.print_help()
        return 0
    validar_jsonl()  # WARN visivel para linhas corrompidas
    vivos = abertos()
    if args.json:
        print(json.dumps(vivos, ensure_ascii=False, indent=2))
        return 0
    if not vivos:
        print("ledger-of-self: 0 achados abertos.")
        return 0
    print(f"ledger-of-self: {len(vivos)} achado(s) aberto(s) -- top da divida viva:")
    for v in vivos:
        print(f"  [{v['occurrences']:>3}x] {v['check']} :: {v['alvo']} "
              f"(desde {v.get('opened_at', '?')}, visto {v.get('last_seen', '?')})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
