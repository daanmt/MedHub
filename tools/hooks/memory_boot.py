#!/usr/bin/env python3
"""
SessionStart hook v2: injeta o boot compacto no início da sessão.

Bloco injetado: fraquezas top-N (memória longa) + resumo do Plano do Dia
(day_plan.py via subprocess, timeout 8s, fallback silencioso) + flag de
drift HANDOFF↔history + "Próximo passo imediato" do HANDOFF + texto-contrato
Presença->Expansão (o boot OFERECE o próximo ato, não executa a sessão).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Navega para project root: tools/hooks/memory_boot.py → tools/hooks → tools → MedHub/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
os.chdir(PROJECT_ROOT)
sys.path.insert(0, str(PROJECT_ROOT))

_DAY_PLAN_TIMEOUT = 8   # segundos; o boot nunca depende da saúde do day_plan
_DAY_PLAN_MAX_LINES = 8


def _memory_context() -> str:
    """Fraquezas top-N + perfil, via inspect.load_context (stdout capturado)."""
    try:
        import io
        import contextlib
        from app.memory.inspect import load_context

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            load_context()
        return buf.getvalue().strip()
    except FileNotFoundError:
        return "[Memory v1] medhub_memory.db ainda não existe — primeira sessão."
    except Exception as e:
        return f"[Memory v1] Aviso: {e}"


def _day_plan_summary() -> str:
    """Resumo do Plano do Dia por subprocess isolado; fallback silencioso."""
    try:
        r = subprocess.run(
            [sys.executable, "tools/day_plan.py"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=_DAY_PLAN_TIMEOUT, cwd=str(PROJECT_ROOT),
        )
        if r.returncode != 0:
            return ""
        lines = [ln for ln in r.stdout.strip().splitlines() if ln.strip()]
        return "\n".join(lines[:_DAY_PLAN_MAX_LINES])
    except Exception:
        return ""


def _read_handoff() -> str:
    try:
        return (PROJECT_ROOT / "HANDOFF.md").read_text(encoding="utf-8")
    except Exception:
        return ""


def _handoff_session(handoff: str) -> int | None:
    """Sessão citada no HANDOFF (primeira ocorrência de sNNN)."""
    m = re.search(r"\bs(\d{2,3})\b", handoff)
    return int(m.group(1)) if m else None


def _latest_session() -> int | None:
    """Maior NNN entre history/session_NNN.md."""
    nums = []
    for p in (PROJECT_ROOT / "history").glob("session_*.md"):
        m = re.match(r"session_(\d+)\.md$", p.name)
        if m:
            nums.append(int(m.group(1)))
    return max(nums) if nums else None


def _drift_flag(handoff: str) -> str:
    """Flag textual (não bloqueio) se HANDOFF e history divergem."""
    cited, latest = _handoff_session(handoff), _latest_session()
    if cited is None or latest is None or cited == latest:
        return ""
    return (f"⚠️ Drift de estado: HANDOFF.md cita s{cited}, mas o último log é "
            f"history/session_{latest:03d}.md — considerar reconcile antes de seguir.")


def _proximo_passo(handoff: str) -> str:
    """Primeira linha de conteúdo da seção 'Próximo passo imediato' do HANDOFF."""
    m = re.search(r"^##[^\n]*Pr[óo]ximo passo imediato[^\n]*\n(.*?)(?=\n##\s|\Z)",
                  handoff, re.M | re.S)
    if not m:
        return ""
    for ln in m.group(1).splitlines():
        ln = ln.strip()
        if ln:
            return ln[:300]
    return ""


_CONTRATO = (
    "[Boot v2 — contrato Presença->Expansão]\n"
    "Abra a sessão OFERECENDO o próximo ato — \"Próximo ato: X — sigo nele salvo "
    "redireção\" — e devolva o turno ao usuário. NÃO execute a sessão inteira na "
    "abertura: o boot oferece, o usuário decide."
)


def build_context() -> str:
    handoff = _read_handoff()
    sections = [_memory_context()]

    day_plan = _day_plan_summary()
    if day_plan:
        sections.append("## Plano do Dia (day_plan.py)\n" + day_plan)

    drift = _drift_flag(handoff)
    if drift:
        sections.append(drift)

    passo = _proximo_passo(handoff)
    if passo:
        sections.append("## Próximo passo imediato (HANDOFF.md)\n" + passo)

    sections.append(_CONTRATO)
    return "\n\n".join(s for s in sections if s)


if __name__ == "__main__":
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": build_context(),
        }
    }))
