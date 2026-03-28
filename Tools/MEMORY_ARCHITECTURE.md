---
type: architecture
layer: root
status: canonical
relates_to: AGENTE, ESTADO, KNOWLEDGE_ARCHITECTURE
---

# MEMORY_ARCHITECTURE — MedHub Memory v1

## Visão geral

MedHub opera com um modelo de memória em três camadas complementares.
Cada camada tem responsabilidade exclusiva — **não duplicar informação entre elas**.

```
┌────────────────────────────────────────────────────────────┐
│ CAMADA 1 — Canônica (repositório git)                      │
│  AGENTE.md · ESTADO.md · Temas/ · ipub.db    │
│  Fonte de verdade para conteúdo clínico e estado do projeto│
└────────────────────────────────────────────────────────────┘
        ↑ lida no boot, atualizada ao fechar sessão
┌────────────────────────────────────────────────────────────┐
│ CAMADA 2 — Short-term (LangGraph checkpointer)             │
│  SqliteSaver → medhub_memory.db::checkpoints               │
│  thread_id = "session_{NNN:03d}"                           │
│  Escopo: within-session state restoration                  │
└────────────────────────────────────────────────────────────┘
        ↑ restaurada automaticamente por thread_id
┌────────────────────────────────────────────────────────────┐
│ CAMADA 3 — Long-term (LangMem + SQLiteMemoryStore)         │
│  SQLiteMemoryStore → medhub_memory.db::memory_store        │
│  Namespaces: profile · weak_areas · workflow_rules ·       │
│             session_insights · study_preferences           │
└────────────────────────────────────────────────────────────┘
```

---

## Thread model

`thread_id = f"session_{NNN:03d}"`

Mapeia 1:1 com `history/session_NNN.md`. Cada sessão tem seu checkpoint isolado.
A continuidade *cross-session* fica exclusivamente na Camada 3.

---

## Backend: `medhub_memory.db`

Dois bancos SQLite distintos — **zero acoplamento**:

| Arquivo | Conteúdo | Commitar? |
|---|---|---|
| `ipub.db` | Erros clínicos, FSRS, cronograma | Não |
| `medhub_memory.db` | Checkpoints + long-term store | Não |

---

## Namespaces Camada 3

| Namespace | Schema | Hot/Background | Descrição |
|---|---|---|---|
| `("medhub", "profile")` | `UserProfile` | Hot | Prova-alvo, ritmo, formato preferido |
| `("medhub", "study_preferences")` | freeform | Hot | Verbosidade, estilo de resposta |
| `("medhub", "workflow_rules")` | `WorkflowRule` | Hot | Regras procedurais descobertas em sessão |
| `("medhub", "weak_areas")` | `WeakArea` | Background | Padrões de fraqueza agregados por área |
| `("medhub", "session_insights")` | `SessionInsight` | Background | Insights memoráveis de sessões passadas |

**Hot** = escrito durante a conversa quando o usuário menciona preferências ou padrões.
**Background** = escrito ao fechar sessão via `consolidate_session()`.

---

## Política de governança

### O que entra na Camada 3

- Preferências explicitamente declaradas ("prefiro respostas mais curtas")
- Padrões de fraqueza agregados (não dados brutos — esses ficam no `ipub.db`)
- Regras procedurais descobertas em sessão (não replicar o que já está em `AGENTE.md`)
- Insights episódicos memoráveis (não o log completo — esse fica em `history/`)

### O que NUNCA entra

- Conteúdo de `Temas/*.md` (já no repo)
- Dados brutos de `ipub.db` (já estruturados lá)
- Logs completos de sessão (já em `history/`)
- Estado de `ESTADO.md` (documento único de estado/handoff)

### Anti-drift

`workflow_rules` são comparadas com `AGENTE.md` antes de persistir.
Não duplicar o que já está canonicamente documentado.

---

## Módulos

| Arquivo | Função |
|---|---|
| `app/memory/store.py` | `SQLiteMemoryStore` — interface BaseStore sobre SQLite |
| `app/memory/checkpointer.py` | Helpers: `get_checkpointer()`, `get_thread_config()`, `get_session_history()` |
| `app/memory/schemas.py` | Pydantic models: `UserProfile`, `WeakArea`, `WorkflowRule`, `SessionInsight` |
| `app/memory/tools.py` | `get_memory_tools(store)` — wraps LangMem create_manage/search_memory_tool |
| `app/memory/manager.py` | `consolidate_session(NNN)` — background consolidation ao fechar sessão |
| `app/memory/inspect.py` | CLI: `--namespace`, `--threads`, `--dump`, `--stats`, `--context` |
| `app/memory/__init__.py` | Re-exports: `get_store()`, `get_checkpointer()`, `get_memory_tools()` |

---

## Como inspecionar

```bash
# Ver memória de um namespace
python -m app.memory.inspect --namespace medhub/weak_areas

# Listar threads (sessões com checkpoint)
python -m app.memory.inspect --threads

# Dump completo
python -m app.memory.inspect --dump

# Estatísticas
python -m app.memory.inspect --stats

# Contexto compacto para boot do agente
python -m app.memory.inspect --context
```

---

## Como consolidar ao fechar sessão

```bash
# Via CLI
python -m app.memory.manager 46

# Via Python
from app.memory.manager import consolidate_session
consolidate_session(46)
```

Requer `ANTHROPIC_API_KEY` para consolidação LLM (usa `claude-haiku-4-5`).
Sem key, usa fallback heurístico (lista áreas trabalhadas).

---

## Smoke tests

```bash
python Tools/test_memory.py
```

4 testes: persistência, cross-thread, search, consolidation.

---

## Ordem de leitura do agente no boot (atualizada)

```
1. AGENTE.md          (boot protocol)
2. ESTADO.md          (snapshot canônico)
3. ESTADO.md seção "Últimas sessões" (próximo passo)
4. app/memory context (python app/memory/inspect.py --context)
5. Workflow da tarefa (.agents/workflows/)
6. Temas relevantes   (via Temas/INDEX.md)
```

---

## Roadmap v2

| Feature | Dependência |
|---|---|
| Busca semântica por embeddings | `sqlite-vec` já instalado — adicionar em `store.py` |
| TTL / max_entries por namespace | Adicionar no `manager.py` |
| Deduplicação LLM de `weak_areas` | LangMem `create_memory_store_manager` com schema |
| Dashboard Streamlit de memória | Nova page em `app/pages/` |
