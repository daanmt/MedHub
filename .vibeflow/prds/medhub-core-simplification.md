# PRD: MedHub — Do App de Páginas ao Motor de Estudo

> Generated via /vibeflow:discover on 2026-04-05
> Revisão incorporando visão de produto ampliada (contexto sessão 062)

---

## Problem

O MedHub tem uma tese forte — erro como dado primário, loop fechado entre diagnóstico,
conhecimento e retenção — mas a arquitetura atual não traduz isso num assistente coeso.
O sistema está organizado por tecnologias (SQLite, Streamlit, LangMem, LangGraph, MCP,
scripts) em vez de por jobs to be done. O resultado:

- LangMem coleta memória de padrões de fraqueza mas nenhuma UI a consome
- LangGraph está configurado mas não participa de nenhum workflow real
- Cards são gerados heuristicamente, sem o contexto clínico dos `resumos/`
- Tabelas legacy e campos duplicados no DB poluem qualquer inspeção
- Dead code (`flashcard_builder.py`, `4_simulados.py`, funções órfãs) aumenta overhead de manutenção
- O cronograma domina o modelo mental do produto, mas o gargalo real é processar erro e reter

O usuário sabe o que faz (processar questão, revisar card, consultar resumo), mas agentes
externos (Claude Code, Cursor, Antigravity) não têm interface estável para consultar o
domínio — o que errei? quais cards estão ativos? qual resumo cobre esse tema? As respostas
existem dispersas em queries ad hoc, scripts e namespaces de memória sem contrato definido.

## Target Audience

Único usuário: o próprio desenvolvedor/estudante, usando o sistema diariamente
para processar questões erradas e revisar flashcards via FSRS na preparação para o
ENARE 2026. Meta: 17.000 questões até outubro/2026.

## Proposed Solution

Reorientar o MedHub de "app com páginas" para um **motor de estudo centrado em erro**,
com memória consultável e interfaces finas. A transformação acontece em 2 fases:

**Fase 1 — Limpeza cirúrgica:** remover o que está morto sem tocar o core.

**Fase 2 — Reorientação arquitetural:** encapsular o domínio num Study Engine,
expor ferramentas estáveis para agentes externos, integrar resumos à geração de cards,
e expor padrões de fraqueza na UI.

O produto passa a ter 4 blocos coesos:
1. **Knowledge** — `resumos/` como cérebro clínico (consulta, links, armadilhas)
2. **Errors** — `ipub.db` como caderno estruturado (erro, padrão, elo quebrado, performance)
3. **Review** — flashcards + FSRS (revisão simples, confiável, auditável)
4. **Coach** — ferramentas do engine consumidas por agentes externos (Claude Code, Cursor,
   Antigravity): "o que estou errando?", "o que devo revisar?", "qual resumo conversa com isso?"
   — sem UI conversacional nativa no app

## Success Criteria

**Fase 1:**
- `python tools/audit_integrity.py` passa sem warnings
- `python tools/audit_flashcard_quality.py` retorna 277/277 OK
- `grep -r "flashcard_builder\|4_simulados\|fsrs_cache" app/ --include="*.py"` → zero resultados
- Streamlit sobe com 3 pages (dashboard, estudo, biblioteca); sem tabs quebradas

**Fase 2:**
- Agente externo pode importar `app/engine/get_topic_context("Cardiologia")` e receber resposta estruturada com resumo + erros recentes + cards ativos + weak_areas — sem precisar de queries ad hoc
- Cards gerados após a integração incluem conteúdo extraído do resumo correspondente
- Dashboard exibe padrões de fraqueza derivados de `weak_areas` (LangMem)
- `app/engine/` existe como módulo com pelo menos 3 operações encapsuladas, com contratos documentados (docstring + tipos) e testáveis isoladamente

---

## FASE 1 — Limpeza Cirúrgica

### Escopo

**DB (`ipub.db`):**
- DROP tabelas: `fsrs_cache_cards`, `fsrs_cache_revlog`, `cronograma_progresso`
- DROP colunas em `flashcards`: `frente`, `verso` (legado v4 — v5 está 100% populado)
- Pré-requisito: `SELECT COUNT(*) FROM flashcards WHERE frente_pergunta IS NULL AND frente IS NOT NULL` deve retornar 0
- Script `tools/cleanup_db.py`: backup automático → validação → DROPs

**Código morto a deletar:**
- `app/pages/4_simulados.py`
- `app/utils/flashcard_builder.py`
- Em `app/utils/db.py`: remover `record_cache_review()`, `get_cache_fsrs_state()`, `sync_git()`

**Streamlit:**
- `app/pages/2_estudo.py`: remover fallback legacy (renderização de `frente`/`verso`) — player usa exclusivamente v5
- `streamlit_app.py`: remover entrada de navegação para simulados
- `app/utils/db.py`: limpar queries que referenciam tabelas/colunas removidas

### Anti-escopo Fase 1
- NÃO tocar `app/utils/fsrs.py`
- NÃO tocar `tools/insert_questao.py`
- NÃO tocar `app/memory/` (LangMem/LangGraph)
- NÃO adicionar features
- NÃO mexer em `resumos/`

---

## FASE 2 — Reorientação Arquitetural

### Escopo

**2.1 — Study Engine (`app/engine/`)**

Novo módulo que encapsula as 5 operações centrais do produto:
```
app/engine/
  __init__.py
  analyze_error.py      → recebe questão + análise, chama insert_questao, retorna contexto
  get_topic_context.py  → dado tema/área, retorna resumo + erros + cards + weak_areas
  generate_flashcards.py → gera/refina cards com contexto do resumo (substitui heurística pura)
  get_review_queue.py   → retorna fila FSRS (atrasados / hoje / novos) com metadados
  summarize_performance.py → agrega métricas de ipub.db + weak_areas para display
```

Pages Streamlit e CLI passam a chamar o engine em vez de fazer queries diretas.
(Migração gradual: não reescrever tudo de uma vez — começar por `get_topic_context` e `get_review_queue`.)

**2.2 — Tool Layer para Agentes Externos**

As funções do `app/engine/` são a interface do coach — não há UI conversacional nativa.
Agentes externos (Claude Code, Cursor, Antigravity) importam ou chamam o engine diretamente.

Requisitos de contrato para cada função do engine:
- **Assinatura tipada:** parâmetros e retorno com type hints explícitos
- **Docstring de uso:** descreve o que retorna e como um agente deve interpretar
- **Retorno estruturado:** `dict` ou `dataclass` — nunca string livre
- **Tratamento de not-found:** retorno explícito (ex: `{"resumo": None, "motivo": "tema não indexado"}`)

Exemplo de uso por agente externo:
```python
from app.engine import get_topic_context, summarize_performance

ctx = get_topic_context("Sepse Neonatal")
# → {"resumo": "...", "erros_recentes": [...], "cards_ativos": [...], "weak_areas": [...]}

perf = summarize_performance(area="Pediatria")
# → {"total_erros": 12, "taxa_acerto": 0.68, "padroes": [...]}
```

LangMem (`weak_areas`, `session_insights`) é consultado via `app/memory/` nas funções
do engine que precisam de contexto histórico — sem LangGraph no caminho principal.

**2.3 — Contexto Clínico na Geração de Cards**

Em `generate_flashcards()` do engine (e por extensão em `insert_questao.py`):
- Ao inserir erro de tema X, buscar `resumos/**/<tema>.md` correspondente
- Extrair seção relevante (trecho com o elo quebrado)
- Injetar no prompt de geração do card como `contexto_clinico`

Resultado: `frente_pergunta` e `verso_armadilha` ancorados no raciocínio do próprio resumo
do usuário, não em heurística genérica.

**2.4 — Painel de Padrões de Erro**

Em `app/pages/1_dashboard.py`, nova seção "Padrões de Fraqueza":
- Lê `weak_areas` namespace de `medhub_memory.db` (LangMem)
- Exibe em cards: área, padrão de erro, error_count, última ocorrência
- Exemplos de output:
  - "Cardiologia — troca conduta inicial por definitiva (7 erros)"
  - "Neonatologia — interpretação de gravidade (4 erros)"

LangMem passa a ter surface area real no produto.

### Anti-escopo Fase 2
- NÃO construir retrieval semântico (MCP/obsidian-rag) — leitura local direta de `resumos/`
- NÃO ativar simulados
- NÃO construir interface conversacional nativa no Streamlit
- NÃO ativar LangGraph no caminho principal do app (permanece congelado)
- NÃO remover `taxonomia_cronograma` do DB (ainda usado por `insert_questao.py` para counters)
  — apenas retirar do modelo mental da UI (não exibir como "cronograma")
- NÃO reescrever todas as pages para usar o engine de uma vez — migração gradual

---

## Technical Context

**O que já existe e é reaproveitado:**

| Arquivo | Reuso |
|---|---|
| `app/memory/` (LangMem) | Engine consulta `weak_areas` + `session_insights` — LangGraph permanece congelado |
| `app/utils/fsrs.py` | Intocado — `get_review_queue()` chama as funções existentes |
| `app/utils/db.py` | Engine chama db.py; regra de SSOT mantida |
| `tools/insert_questao.py` | Chama `generate_flashcards()` do engine em vez de heurística interna |
| `tools/regenerate_cards_llm.py` | Mantido para passe qualitativo retroativo |
| `tools/audit_*.py` | Smoke tests de Fase 1 e validação contínua |

**Padrões a seguir:**
- `import sqlite3` apenas em `app/utils/db.py` e CLIs standalone — `app/engine/` usa `db.py`
- Flat dark design system via `app/utils/styles.py` (COLORS, inject_styles)
- Todas as páginas começam com `inject_styles()` antes de qualquer conteúdo

**Decisões de stack (Fase 2):**
- LangGraph: **congelado** — não está no caminho principal do app
- LangMem: **consultado** pelo engine (read-only em `weak_areas` + `session_insights`) e exposto no painel de padrões
- MCP/Obsidian-RAG: **opcional** — não é fundação da Fase 2
- SQLite: **mantido** — ruído de schema foi o problema, não a tecnologia

## Open Questions

1. **Search em resumos (Fase 2):** `get_topic_context()` precisa achar o arquivo `.md`
   certo dado um tema. Os nomes de arquivo não são normalizados (ex: `[CIR] Trauma.md`
   vs `Insuficiência Cardíaca.md`). Definir na spec: índice por frontmatter (`especialidade` + `aliases`)
   ou fuzzy match por nome de arquivo?

2. **Contratos do engine:** As funções de `app/engine/` serão consumidas por agentes via
   `import` direto (Python) ou também expostas como CLI/MCP tools? Definir na spec para
   garantir que os contratos de retorno sejam compatíveis com ambos os usos.

3. **Cronograma:** `taxonomia_cronograma` fica no DB (usado por `insert_questao.py`),
   mas some da UI. O dashboard atual usa essa tabela para métricas de progresso —
   confirmar quais métricas sobrevivem e quais são substituídas pelo painel de padrões.
