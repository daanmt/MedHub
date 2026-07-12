# Spec: Consolidação do Mecanismo de Conhecimento — Parte 1 (Remoção de redundância e código morto)

> Gerado via /vibeflow:gen-spec on 2026-07-12
> PRD: `.vibeflow/prds/mecanismo-conhecimento-consolidacao.md`
> Parte 1 de 3 — pura remoção, sem novo comportamento
> Budget: ≤8 arquivos (ajustado de ≤6 no implement: a deleção de `checkpointer.py` cascateia para seus 2 importadores vivos — `app/memory/__init__.py` e `app/memory/inspect.py` — o que o DoD #3 "`import app.memory` não quebra" já implicava; escopo inalterado, contagem corrigida)

## Objective

Reduzir o mecanismo de busca a uma única fonte de verdade (`app/engine/rag.py`), removendo o índice vetorial redundante (MCP obsidian) e todo scaffold morto (LangGraph checkpointer, BM25) sem tocar o núcleo vivo.

## Context

Hoje coexistem dois índices vetoriais do **mesmo vault com o mesmo modelo**: o Chroma local de `rag.py` (vivo, consumido) e o MCP `obsidian-notes-rag` (`.mcp.json`), reindexado a cada sessão pelo hook `tools/hooks/memory_session_log.py` (linhas 42-63) mas **sem nenhum consumidor Python**. Além disso: `app/memory/checkpointer.py` é scaffold de um agente que não vive no repo (confessado em `README.md`); `app/memory/tools.py` é citado no README mas não existe; `_bm25_rerank` em `rag.py` está desabilitado por regressão medida (90%→73%) mas `rank-bm25` continua no `requirements.txt`. Nada disso participa de caminho vivo — é peso morto que sustenta a percepção de "bagunça".

## Definition of Done

1. `grep -ri "obsidian-notes-rag" .` (excluindo `docs/AUDITORIA-*`, `.vibeflow/`, `history/`) retorna **zero** referências vivas: bloco removido de `.mcp.json`; linhas 42-63 removidas de `tools/hooks/memory_session_log.py`.
2. O hook `memory_session_log.py` continua disparando a consolidação LangMem em background (linhas 29-40 intactas) e **não** tenta mais reindexar RAG — verificável rodando o hook com um `session_NNN.md` fictício e observando que só a mensagem `[Memory v1]` aparece.
3. `app/memory/checkpointer.py` deletado; a menção a `tools.py` e ao checkpointer no `README.md` removida ou marcada como histórica; `python -c "import app.memory"` não quebra.
4. `_bm25_rerank` e seu call-site removidos de `app/engine/rag.py`; `rank-bm25` removido de `requirements.txt`; `grep -r "bm25" app/ tools/` → zero.
5. **[qualidade]** `pytest` continua verde (mesma contagem de PASS pré-mudança, menos os testes que exercitavam código removido, se houver); nenhuma violação nova de `conventions.md` (`import sqlite3` só em `db.py`; pt-BR; flat design).
6. **[qualidade]** Nenhuma função viva perdeu caller: `search()`, `search_two_tier()`, `index_all()`, `index_pdfs_raw()` e a consolidação LangMem intactas e ainda referenciadas.

## Scope

- `.mcp.json`: remover o server `obsidian-notes-rag` (manter `pubmedmcp`).
- `tools/hooks/memory_session_log.py`: remover o bloco de reindex inline (42-63) e o `env` associado; preservar a consolidação em background.
- `app/memory/checkpointer.py`: deletar.
- `README.md`: remover/corrigir a referência a `tools.py` e ao checkpointer scaffold.
- `app/engine/rag.py`: remover `_bm25_rerank` e o ponto onde é (não) chamado.
- `requirements.txt`: remover `rank-bm25`.

## Anti-scope

- **NÃO** remover `app/memory/store.py`, `manager.py`, `schemas.py`, `inspect.py` — LangMem `consolidate_session` está vivo.
- **NÃO** tocar `search()`/`search_two_tier()`/two-tier/HyDE/multi-query/chunking.
- **NÃO** adicionar comportamento novo (fallback e WARN são Parte 3).
- **NÃO** editar docs de governança que descrevem o motor de busca (AGENTE.md/ROADMAP/HANDOFF) — isso é Parte 2 (reconciliação).
- **NÃO** reativar BM25 sob nenhuma forma.

## Technical Decisions

- **Deletar, não comentar** o código morto — comentar mantém a bagunça. Git preserva o histórico.
- **`langgraph-checkpoint-sqlite` no requirements**: manter por ora se `langmem`/`langgraph` o puxam transitivamente; só remover se `pip` confirmar que nada vivo o importa (verificar antes; não arriscar quebrar LangMem). Registrar a decisão no commit.
- O hook perde uma responsabilidade mas mantém a assinatura de saída (`hookSpecificOutput`) — agentes que leem o output não quebram.

## Applicable Patterns

- `patterns/domain-engine-api.md` — o engine permanece a interface estável; a remoção não altera contratos vivos.
- `patterns/agent-workflow-protocol.md` — o hook é parte do protocolo de sessão; preservar o contrato de background-consolidation.
- `conventions.md` — pt-BR, flat design, `sqlite3` só em `db.py`.

## Risks

- **Risco**: remover `rank-bm25` quebra um import esquecido. → Mitigação: `grep bm25` antes e depois; rodar `pytest`.
- **Risco**: o hook editado deixa de consolidar por engano. → Mitigação: DoD #2 testa o hook isoladamente com session fictícia.
- **Risco**: `langgraph-checkpoint-sqlite` é dep transitiva de `langmem` e removê-la quebra LangMem. → Mitigação: não remover sem confirmar; escopo desta parte é só `rank-bm25` + `checkpointer.py` (arquivo), não a dep do checkpoint-sqlite.
