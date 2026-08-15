# Spec: consolidacao-part-3 — memória: simplificação radical

> PRD: `consolidacao-alcancabilidade.md` · Decisão do operador + auditoria funcional (memória FUNCIONA-PARCIAL; refutado "nunca funcionou"): manter o que é lido, matar o write-only, consertar o contador.

## Objective
A camada de memória fica com exatamente o que o boot usa — e o número que ela injeta volta a significar algo.

## Definition of Done
1. [ ] **Contador consertado** (`app/memory/manager.py:79-128`): `GROUP BY area, tema` + matching EXATO por (area, tema) usando o campo `especialidade`/`tema` do WeakArea (sem substring bidirecional, sem `break` no primeiro hit; múltiplos matches = SOMA). Teste novo com fixture: 2 sub-temas da mesma área recebem counts DIFERENTES; sub-tema sem match recebe 0/None, nunca o total da área.
2. [ ] **`session_insights` morre**: geração removida de `manager.py`; purge das 514 linhas do namespace em `medhub_memory.db` (backup único `artifacts/backups/medhub_memory_pre_purge_20260814.db` antes); schema/`schemas.py` limpo; `tools/test_memory.py` ajustado ou removido se só testava isso.
3. [ ] **Doc honesta**: `AGENTE.md` — seção Camada 2 (SqliteSaver/checkpoints, :247-250) REMOVIDA; namespaces fantasma (`profile`, `study_preferences`, `workflow_rules` — 0 linhas desde março) saem de `schemas.py` e da doc, OU ganham writer real (não neste ciclo → saem).
4. [ ] **Falha visível**: o spawn fire-and-forget (`memory_session_log.py`) ganha o mínimo — o processo filho escreve erro em `history/memory_errors.log` quando falha (append, 1 linha); sem retry, sem bloqueio.
5. [ ] `load_context()` continua funcionando (smoke pós-mudança: retorna weak_areas com counts corrigidos); boot injeta o mesmo shape.
6. [ ] `pytest` verde; grep `session_insights|checkpointer|SqliteSaver` (fora de history/.vibeflow/artifacts) → 0 refs vivas.

## Scope
`app/memory/{manager.py,schemas.py,inspect.py}` · `tools/hooks/memory_session_log.py` · `tools/test_memory.py` · `AGENTE.md` (seções citadas) · novo teste (allowlist `pytest.ini`).

## Anti-scope
NÃO remover langgraph/langmem das deps (store BaseStore os usa e funciona); NÃO tocar `weak_areas` além do contador; NÃO criar memória nova.
