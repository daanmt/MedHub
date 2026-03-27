"""
Background memory consolidation for MedHub.

Called at session close (via registrar-sessao.md workflow) to:
  1. Read history/session_NNN.md
  2. Extract clinical insights → ("medhub", "session_insights")
  3. Extract weakness patterns → ("medhub", "weak_areas")
  4. Sync error_count in WeakAreas from ipub.db performance data

Uses two separate create_memory_store_manager instances (one per schema)
so each schema lands in its own namespace.

Uses claude-haiku-4-5 (low cost). Graceful fallback if ANTHROPIC_API_KEY absent.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from app.memory.store import SQLiteMemoryStore


_HISTORY_DIR = Path("history")
_HAIKU_MODEL = "claude-haiku-4-5-20251001"

_SI_INSTRUCTIONS = """
Você é um analisador de logs de sessão de estudo médico para residência médica.
Extraia insights clínicos memoráveis: distinções diagnósticas, armadilhas de prova,
critérios objetivos e condutas específicas identificados nesta sessão.

Regras obrigatórias:
- Escreva SEMPRE em português brasileiro (pt-BR)
- O campo session_id do SessionInsight DEVE ser exatamente o valor indicado na linha
  [SESSÃO: session_NNN] no início do log (ex: "session_054") — nunca invente um UUID
- Ignore detalhes de workflow/infraestrutura — foque exclusivamente no conteúdo médico-clínico
- Prefira insights densos com valores específicos (doses, escores, critérios diagnósticos)
- Cada insight deve ser autocontido e compreensível fora do contexto da sessão
"""

_WA_INSTRUCTIONS = """
Você é um analisador de padrões de erro para estudo médico para residência médica.
Extraia padrões de fraqueza recorrentes por área/especialidade identificados nesta sessão.

Regras obrigatórias:
- Escreva SEMPRE em português brasileiro (pt-BR)
- Extraia WeakArea SOMENTE se o log contiver análise explícita de questões erradas
- O campo pattern deve descrever o mecanismo cognitivo do erro: qual confusão conceitual,
  qual critério desconhecido, qual distinção não dominada — não apenas o tema geral
- Se não houver questões erradas analisadas nesta sessão, NÃO extraia nada
- Prefira padrões específicos e acionáveis (ex: "confunde X com Y em situação Z")
"""


def _read_session_log(session_num: int) -> str | None:
    path = _HISTORY_DIR / f"session_{session_num:03d}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _extract_areas_from_log(log_text: str) -> list[str]:
    """Heuristic area extraction used in fallback path."""
    known_areas = [
        "Clínica Médica", "Cardiologia", "Pneumologia", "Nefrologia",
        "Gastroenterologia", "Endocrinologia", "Reumatologia", "Neurologia",
        "Hematologia", "Infectologia",
        "GO", "Ginecologia", "Obstetrícia",
        "Pediatria", "Neonatologia",
        "Cirurgia", "Ortopedia", "Neurocirurgia",
        "Preventiva", "Saúde Pública", "Epidemiologia",
        "Psiquiatria", "Dermatologia", "Oftalmologia", "Otorrinolaringologia",
        "Urologia", "Oncologia",
    ]
    return [a for a in known_areas if a.lower() in log_text.lower()]


def _sync_error_counts(store: SQLiteMemoryStore) -> None:
    """Atualiza error_count nas WeakAreas com dados quantitativos de ipub.db.

    Usa taxonomia_cronograma: SUM(questoes_realizadas - questoes_acertadas) por área.
    Matching por substring (area name em ipub.db vs WeakArea.area).
    """
    ipub_path = Path("ipub.db")
    if not ipub_path.exists():
        return

    try:
        conn = sqlite3.connect(ipub_path)
        rows = conn.execute(
            """SELECT area,
                      SUM(questoes_realizadas - questoes_acertadas) as erros
               FROM taxonomia_cronograma
               WHERE questoes_realizadas > 0
               GROUP BY area"""
        ).fetchall()
        conn.close()
    except Exception as e:
        print(f"[memory/manager] Não foi possível ler ipub.db: {e}")
        return

    # Mapa de area_ipub → error_count
    ipub_counts: dict[str, int] = {r[0].lower(): int(r[1]) for r in rows if r[1]}

    if not ipub_counts:
        return

    existing = store.search(("medhub", "weak_areas"), limit=200)
    updated = 0
    for item in existing:
        val = item.value
        if val.get("kind") != "WeakArea":
            continue
        wa_area = val.get("content", {}).get("area", "").lower()
        # Tenta match por substring em ambas as direções
        matched_count = None
        for ipub_area, count in ipub_counts.items():
            if ipub_area in wa_area or wa_area in ipub_area:
                matched_count = count
                break
        if matched_count is not None and val.get("content", {}).get("error_count", 0) != matched_count:
            val["content"]["error_count"] = matched_count
            store.put(("medhub", "weak_areas"), item.key, val)
            updated += 1

    if updated:
        print(f"[memory/manager] error_count atualizado em {updated} WeakAreas via ipub.db")


def _llm_consolidate(
    session_log: str,
    session_num: int,
    store: SQLiteMemoryStore,
) -> None:
    """Dois managers LLM: SessionInsight e WeakArea em namespaces separados."""
    try:
        from langmem import create_memory_store_manager
        from langchain_anthropic import ChatAnthropic
        from app.memory.schemas import SessionInsight, WeakArea

        llm = ChatAnthropic(model=_HAIKU_MODEL, api_key=os.environ["ANTHROPIC_API_KEY"])
        session_id = f"session_{session_num:03d}"

        # Injeta session_id no conteúdo para evitar alucinação de UUID
        content = f"[SESSÃO: {session_id}]\n\n{session_log}"
        config = {"configurable": {"thread_id": session_id}}

        # Manager A: SessionInsight → medhub/session_insights
        si_manager = create_memory_store_manager(
            llm,
            schemas=[SessionInsight],
            store=store,
            namespace=("medhub", "session_insights"),
            instructions=_SI_INSTRUCTIONS,
        )
        si_manager.invoke({"messages": [{"role": "user", "content": content}]}, config=config)
        print(f"[memory/manager] SessionInsights consolidados para {session_id}")

        # Manager B: WeakArea → medhub/weak_areas
        wa_manager = create_memory_store_manager(
            llm,
            schemas=[WeakArea],
            store=store,
            namespace=("medhub", "weak_areas"),
            instructions=_WA_INSTRUCTIONS,
        )
        wa_manager.invoke({"messages": [{"role": "user", "content": content}]}, config=config)
        print(f"[memory/manager] WeakAreas consolidadas para {session_id}")

    except Exception as e:
        print(f"[memory/manager] LLM consolidation skipped: {e}")


def _fallback_consolidate(
    session_log: str,
    session_num: int,
    store: SQLiteMemoryStore,
) -> None:
    """Consolidação heurística quando ANTHROPIC_API_KEY ausente."""
    areas = _extract_areas_from_log(session_log)
    if not areas:
        return

    session_id = f"session_{session_num:03d}"
    store.put(
        ("medhub", "session_insights"),
        session_id,
        {
            "kind": "SessionInsight",
            "content": {
                "session_id": session_id,
                "insight": f"Áreas trabalhadas: {', '.join(areas)}",
                "area": areas[0],
            },
        },
    )
    print(f"[memory/manager] Fallback insight salvo para {session_id}: {areas}")


def consolidate_session(
    session_num: int,
    store: SQLiteMemoryStore | None = None,
    db_path: str = "medhub_memory.db",
) -> None:
    """Entry point principal — consolida sessão na memória longa.

    Args:
        session_num: Número da sessão (ex: 54)
        store: Store opcional; se None, cria a partir de db_path
        db_path: Caminho para medhub_memory.db
    """
    if store is None:
        store = SQLiteMemoryStore(db_path)

    session_id = f"session_{session_num:03d}"
    log_text = _read_session_log(session_num)

    if log_text is None:
        print(f"[memory/manager] Sessão {session_id} não encontrada em history/. Pulando.")
        return

    print(f"[memory/manager] Consolidando {session_id}...")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        _llm_consolidate(log_text, session_num, store)
    else:
        _fallback_consolidate(log_text, session_num, store)

    # Sincronizar error_count de ipub.db (independente do path LLM/fallback)
    _sync_error_counts(store)

    print(f"[memory/manager] {session_id} consolidado.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python -m app.memory.manager <session_num>")
        sys.exit(1)

    consolidate_session(int(sys.argv[1]))
