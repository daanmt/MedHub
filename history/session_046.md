# Session 046 — Memory v1: LangGraph + LangMem + SQLiteMemoryStore

**Data:** 2026-03-25
**Ferramenta:** Claude Code
**Continuidade:** Sessão 045 (Sífilis Congênita)

---

## O que foi feito

- Implementação completa da Camada 2/3 de memória (Memory v1)
- 4/4 smoke tests passaram sem erros
- Atualização de todos os docs canônicos para registrar a nova arquitetura

## Artefatos criados/modificados

**Criados:**
- `app/memory/__init__.py` — exports: get_store, get_checkpointer, get_memory_tools
- `app/memory/store.py` — SQLiteMemoryStore (interface BaseStore, ~170 linhas)
- `app/memory/checkpointer.py` — helpers SqliteSaver (get_checkpointer, get_thread_config, get_session_history)
- `app/memory/schemas.py` — Pydantic: UserProfile, WeakArea, WorkflowRule, SessionInsight
- `app/memory/tools.py` — get_memory_tools() com 6 ferramentas LangMem (5 manage + 1 search)
- `app/memory/manager.py` — consolidate_session() com LLM + fallback heurístico
- `app/memory/inspect.py` — CLI observabilidade (--namespace, --threads, --dump, --stats, --context)
- `tools/test_memory.py` — 4 smoke tests (persistência, cross-thread, search, consolidação)
- `MEMORY_ARCHITECTURE.md` — documentação das 3 camadas, thread model, namespaces, governance

**Modificados:**
- `requirements.txt` — adicionado langgraph, langgraph-checkpoint-sqlite, langmem
- `AGENTE.md` — boot sequence: passo 5 (carregar memória longa via inspect.py --context)
- `.agents/workflows/registrar-sessao.md` — passo 5 (consolidate_session ao fechar)
- `KNOWLEDGE_ARCHITECTURE.md` — seção 9 (arquitetura de memória de agentes, 3 camadas)
- `ESTADO.md` — atualizado: sessão 046, Memory v1 ativo, 46 sessões
- `HANDOFF.md` — atualizado com estado atual

## Decisões tomadas

- Backend SQLite (`medhub_memory.db`) separado do `ipub.db` — zero acoplamento
- Conexões SQLite abertas e fechadas explicitamente por operação (evita file-locking no Windows)
- Thread model: `thread_id = "session_{NNN:03d}"` — mapeamento 1:1 com `history/session_NNN.md`
- Fallback heurístico no manager.py quando `ANTHROPIC_API_KEY` ausente (não quebra o workflow)
- `SQLiteMemoryStore` implementa `BaseStore` diretamente (~170 linhas) — sem dependência de PostgreSQL

## Próximos passos

- Usar `manage_weak_areas` e `manage_profile` em sessão clínica real
- Rodar `python -m app.memory.manager <NNN>` ao fechar próxima sessão clínica
- v2: adicionar busca semântica com `sqlite-vec` (já instalado)
