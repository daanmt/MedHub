"""event_log.py — eventos append-only do pipeline de flashcards (P3 part-4).

Fatos imutáveis (`generation`, `reincidencia`) em `history/generation_log.jsonl`.
NÃO usa `ledger_self` de propósito: lá, achados têm ciclo opened/resolved —
registrar eventos por essa via marcaria eventos passados como 'resolved' a cada
corrida (semânticas incompatíveis; correção consciente do C.8.1 do relatório).

Contratos: nunca levanta exceção (falha → WARN no stdout, retorno False);
eventos carregam SÓ ids/contagens/tags — NUNCA texto clínico.
"""
import json
import os
from datetime import datetime

LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "history", "generation_log.jsonl")


def registrar(tipo, dados, log_path=None):
    """Appenda 1 evento {ts, tipo, **dados}. True/False; nunca levanta."""
    try:
        path = log_path or LOG_PATH
        os.makedirs(os.path.dirname(path), exist_ok=True)
        evento = {"ts": datetime.now().isoformat(timespec="seconds"), "tipo": tipo}
        evento.update(dados)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(evento, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        print(f"[WARN] EVENT_LOG: evento '{tipo}' nao persistido ({e}).")
        return False


def eventos(tipo=None, log_path=None):
    """Lê eventos (filtro opcional por tipo). Linha corrompida é pulada com WARN."""
    path = log_path or LOG_PATH
    out = []
    if not os.path.exists(path):
        return out
    try:
        with open(path, encoding="utf-8") as fh:
            for i, linha in enumerate(fh):
                linha = linha.strip()
                if not linha:
                    continue
                try:
                    ev = json.loads(linha)
                except Exception:
                    print(f"[WARN] EVENT_LOG: linha {i + 1} corrompida — pulada.")
                    continue
                if tipo is None or ev.get("tipo") == tipo:
                    out.append(ev)
    except Exception as e:
        print(f"[WARN] EVENT_LOG: leitura falhou ({e}).")
    return out
