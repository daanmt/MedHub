"""
Background memory consolidation for MedHub.

Called at session close (hook PostToolUse(Write) → spawn detached) to:
  1. Read history/session_NNN.md
  2. Extract weakness patterns → ("medhub", "weak_areas")
  3. Sync error_count in WeakAreas from ipub.db performance data

Namespace único: ("medhub", "weak_areas") — é o que o boot lê via
`inspect.load_context()`. Memória write-only foi removida (consolidacao-part-3).

Uses claude-haiku-4-5 (low cost). Sem ANTHROPIC_API_KEY só o sync de
contadores roda. Falhas são registradas em history/memory_errors.log
(o processo é spawnado detached, com stdout/stderr em DEVNULL).
"""

from __future__ import annotations

import os
import sqlite3
import unicodedata
from datetime import datetime
from pathlib import Path

from app.memory.store import SQLiteMemoryStore


_HISTORY_DIR = Path("history")
_IPUB_PATH = Path("ipub.db")
_ERROR_LOG = Path("history") / "memory_errors.log"
_HAIKU_MODEL = "claude-haiku-4-5-20251001"

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


def log_error(context: str, exc: BaseException | str) -> None:
    """Append 1 linha em history/memory_errors.log (ts + erro curto).

    Sem retry, sem bloqueio: o spawn é fire-and-forget e stdout/stderr vão
    para DEVNULL, então o arquivo é a única superfície de falha visível.
    """
    short = str(exc).replace("\n", " ")[:300]
    line = f"{datetime.now().isoformat(timespec='seconds')}\t{context}\t{type(exc).__name__ if isinstance(exc, BaseException) else 'Error'}: {short}\n"
    try:
        _ERROR_LOG.parent.mkdir(parents=True, exist_ok=True)
        with _ERROR_LOG.open("a", encoding="utf-8") as fh:
            fh.write(line)
    except Exception:
        pass  # logging nunca derruba a consolidação


def _read_session_log(session_num: int) -> str | None:
    path = _HISTORY_DIR / f"session_{session_num:03d}.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Contador de erros — matching EXATO por (area, tema)
# ---------------------------------------------------------------------------

def _norm(value: object) -> str:
    """Normaliza rótulo de taxonomia para comparação exata.

    Case-fold + remoção de acentos + colapso de espaços. NÃO faz substring:
    dois rótulos só casam se forem o MESMO rótulo.
    """
    if not value:
        return ""
    s = unicodedata.normalize("NFKD", str(value))
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return " ".join(s.split()).casefold()


def _load_ipub_error_counts(ipub_path: Path) -> dict[tuple[str, str], int]:
    """Erros por (area, tema) — a granularidade que desambigua sub-temas.

    GROUP BY area, tema (não só area): dois temas da mesma área produzem
    linhas distintas. Linhas cujos rótulos normalizam para o mesmo par são
    SOMADAS (múltiplos matches somam).

    🔴 F37 (corrigido na s159) — a fonte MUDOU, o contrato de retorno não.
    Antes: `SUM(questoes_realizadas - questoes_acertadas)` de
    `taxonomia_cronograma`. Esse campo é alimentado por sessões de volume que
    são atribuídas à ÁREA, e até a s159 `registrar_sessao_bulk` as espalhava
    por TODOS os temas da área — então cada tema carregava o acumulado inteiro
    da sua área (39.077 contra 6.631 reais = 5,9x de inflação).

    A consequência era silenciosa e séria: `_sync_error_counts` documenta
    *"WeakArea sem par correspondente recebe 0 — nunca herda o total da área"*,
    mas a defesa estava na camada errada — a fonte já tinha assado o total da
    área dentro de cada tema. O ranking de fraquezas do boot media QUANTO A
    ÁREA FOI ESTUDADA, não quão fraco o tema é. Exemplo medido na s159:
    `Ginecologia / Gravidez ectópica` aparecia como fraqueza persistente com
    "61 erros" e tinha **zero** erros atribuídos a ela em `questoes_erros`.

    Agora conta `questoes_erros` — a única superfície com atribuição real por
    tema (cada linha é um erro analisado, com tema_id resolvido no ato). Temas
    sem erro registrado simplesmente não aparecem no dict, que é o mesmo que
    receber 0 no chamador.
    """
    conn = sqlite3.connect(ipub_path)
    try:
        rows = conn.execute(
            """SELECT t.area,
                      t.tema,
                      COUNT(q.id) AS erros
               FROM questoes_erros q
               JOIN taxonomia_cronograma t ON t.id = q.tema_id
               GROUP BY t.area, t.tema"""
        ).fetchall()
    finally:
        conn.close()

    counts: dict[tuple[str, str], int] = {}
    for area, tema, erros in rows:
        if not erros or int(erros) <= 0:
            continue
        key = (_norm(area), _norm(tema))
        counts[key] = counts.get(key, 0) + int(erros)
    return counts


def _sync_error_counts(store: SQLiteMemoryStore, ipub_path: Path | str = _IPUB_PATH) -> int:
    """Atualiza error_count nas WeakAreas com dados quantitativos de ipub.db.

    Match EXATO do par (WeakArea.area, WeakArea.especialidade) contra o par
    (taxonomia_cronograma.area, .tema). Sem substring, sem `break` no primeiro
    hit: sub-temas distintos da mesma área recebem counts distintos, e
    WeakArea sem par correspondente recebe 0 — nunca herda o total da área.

    Retorna o número de WeakAreas atualizadas.
    """
    path = Path(ipub_path)
    if not path.exists():
        return 0

    try:
        counts = _load_ipub_error_counts(path)
    except Exception as e:
        log_error("sync_error_counts/read_ipub", e)
        print(f"[memory/manager] Não foi possível ler ipub.db: {e}")
        return 0

    if not counts:
        return 0

    existing = store.search(("medhub", "weak_areas"), limit=1000)
    updated = 0
    for item in existing:
        val = item.value
        if not isinstance(val, dict):
            continue
        if "kind" in val and val.get("kind") != "WeakArea":
            continue
        # Envelope LangMem {"kind", "content"} ou dict plano legado
        content = val.get("content") if isinstance(val.get("content"), dict) else val
        if not isinstance(content, dict):
            continue

        key = (_norm(content.get("area")), _norm(content.get("especialidade")))
        matched = counts.get(key, 0)  # sem match = 0, NUNCA o total da área

        if content.get("error_count", 0) != matched:
            content["error_count"] = matched
            store.put(("medhub", "weak_areas"), item.key, val)
            updated += 1

    if updated:
        print(f"[memory/manager] error_count atualizado em {updated} WeakAreas via ipub.db")
    return updated


# ---------------------------------------------------------------------------
# Consolidação
# ---------------------------------------------------------------------------

def _llm_consolidate(
    session_log: str,
    session_num: int,
    store: SQLiteMemoryStore,
) -> None:
    """Extrai WeakAreas do log da sessão para o namespace medhub/weak_areas."""
    try:
        from langmem import create_memory_store_manager
        from langchain_anthropic import ChatAnthropic
        from app.memory.schemas import WeakArea

        llm = ChatAnthropic(model=_HAIKU_MODEL, api_key=os.environ["ANTHROPIC_API_KEY"])
        session_id = f"session_{session_num:03d}"

        # Injeta session_id no conteúdo para evitar alucinação de UUID
        content = f"[SESSÃO: {session_id}]\n\n{session_log}"
        config = {"configurable": {"thread_id": session_id}}

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
        log_error(f"llm_consolidate/session_{session_num:03d}", e)
        print(f"[memory/manager] LLM consolidation skipped: {e}")


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

    if os.environ.get("ANTHROPIC_API_KEY"):
        _llm_consolidate(log_text, session_num, store)
    else:
        print("[memory/manager] ANTHROPIC_API_KEY ausente — extração de WeakArea pulada.")

    # Sincronizar error_count de ipub.db (roda mesmo sem API key).
    # _IPUB_PATH explícito: mantém o path patchável em teste.
    _sync_error_counts(store, _IPUB_PATH)

    print(f"[memory/manager] {session_id} consolidado.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: python -m app.memory.manager <session_num>")
        sys.exit(1)

    # Processo filho de um spawn detached: sem try/except global a falha é muda.
    try:
        consolidate_session(int(sys.argv[1]))
    except BaseException as e:  # noqa: BLE001 — última linha de defesa do filho
        log_error(f"consolidate_session/{sys.argv[1]}", e)
        sys.exit(1)
