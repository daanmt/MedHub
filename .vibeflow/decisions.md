# Decision Log
> Newest first. Updated automatically by the architect agent.

## 2026-04-23 — CLIs Python com emoji: forçar UTF-8 no stdout (Windows cp1252)

**Contexto:** Implementação de `tools/performance.py` (skill `/performance`) usa emojis de faixa (🟢🟡🟠🔴🟣) para classificação visual de custo/questão. Primeira execução em Windows crashou com `UnicodeEncodeError: 'charmap' codec can't encode '\U0001f7e3'` — o cp1252 default do Windows não cobre planos astrais Unicode, e ao rodar via subprocess (como Claude Code faz via Bash) o stdout é cp1252, não UTF-8.

**Decisão:** CLIs em `tools/` que imprimem emoji DEVEM incluir no topo de `main()`:
```python
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass  # Python < 3.7
```

**Pitfall para futuros scripts:** `insert_questao.py` e `registrar_sessao_bulk.py` também sofrem disso (imprimem `quest�o` em vez de `questão`), mas com caracteres pt-BR o cp1252 degrada sem crashar. Com emojis do plano astral (U+1F7E0+), crasha. Para qualquer novo CLI com emoji, aplicar a reconfiguração.

---

## 2026-04-23 — Drift de taxonomia em `sessoes_bulk`: aceitar como diagnóstico visível

**Contexto:** Auditoria de `performance.py` expôs duas inconsistências de dados:
1. `"Obstetricia"` (sem acento) no DB vs `"Obstetrícia"` em `AREAS_VALIDAS` — falsamente listada como gap.
2. `"GO"` criado como área paralela a Ginecologia/Obstetricia na sessão 071.

**Decisão:** Não normalizar em `performance.py`. O script deve revelar fielmente o drift. Futuras consolidações de dados em SQL migration script separado (fora do escopo do v0). Correção cirúrgica:
- Sessões futuras: usar exatamente os nomes de `AREAS_VALIDAS` de `registrar_sessao_bulk.py` ao chamar `--area`.
- Para dados históricos: criar `tools/normalizar_areas.py` quando prioridade justificar (tech debt).

---

## 2026-04-07 — BM25 como re-ranker pós-Chroma: alpha=0.8, Threshold Fixo, Desabilitado por Regressão

**Contexto:** O BM25 foi implementado para resolver colisões léxicas (Placenta vs DPP), mas degradou o Recall global (90% → 73%) ao elevar termos genéricos ("tratar", "diagnóstico") de outras especialidades.

**Decisão:**
- **Alpha=0.8:** Redução drástica da influência léxica para evitar falsos positivos em corpus médico denso.
- **Threshold Fixo (0.35):** Normalização do score coseno ancorada no limite de corte do RAG, não no máximo relativo do lote recuperado. Isso garante estabilidade de score independente da qualidade do vizinho.
- **Desabilitado em Produção:** O reranker BM25 permanece no código (`_bm25_rerank`), mas a chamada em `search()` foi comentada/removida. **Tech Debt para /discover**: O sistema performa melhor com Coseno Puro + HyDE + Context Propagation no momento.

**HyDE cache & Parallellism:** 
- `_HYDE_CACHE` module-level p/ evitar re-chamadas de API na mesma sessão.
- `ThreadPoolExecutor` no `search()` dispara HyDE e `get_collection()` em paralelo: latência final = `max(LLM, DB)`, não a soma. Redução média de ~1s no TTFT.


---

## 2026-04-05 — Arquitetura RAG: dois índices, papéis distintos, sem conflito

**Contexto:** O projeto tinha `obsidian-notes-rag` MCP instalado sem clareza sobre seu papel. Após diagnóstico (sessão 063), ficou claro que coexistem dois sistemas ChromaDB com propósitos distintos.

**Decisão:**

| Sistema | Path | Corpus | Consumido por |
|---|---|---|---|
| `app/engine/rag.py` | `data/chroma/` (688 chunks) | `resumos/**/*.md` (44 arquivos clínicos, chunking H2/H3) | `get_topic_context()`, `generate_contextual_cards()`, `3_biblioteca.py` — via Python import |
| `obsidian-notes-rag` MCP | `AppData/Local/obsidian-notes-rag/medhub/` (862 chunks) | Vault completo (147 md, inclui ESTADO, history, etc.) | Agentes externos via MCP protocol |

**RAG canônico = `app/engine/rag.py`**. É o sistema fundação, integrado ao engine, com fallback silencioso (`_CHROMA_AVAILABLE = False → []`). Não depende de processo externo.

**MCP `obsidian-notes-rag` = auxiliar opcional**. Útil para agentes que precisam buscar qualquer nota do vault (não só resumos clínicos). Bug conhecido: o servidor sobe sem `--provider ollama` em sessões Antigravity (lê configuração global, não o `.mcp.json` local). O `.mcp.json` no repositório está correto — precisa restart do servidor MCP para herdar `--provider ollama --model nomic-embed-text:latest`.

**Eles não se interferem**: paths físicos distintos, clients ChromaDB independentes.

**Pitfall:** O MCP falha silenciosamente com `OPENAI_API_KEY not set` quando o servidor sobe sem `--provider ollama`. Não confundir com falha do RAG interno — são sistemas independentes.

**Grep de referências RAG:** `grep -rn "rag\|chroma\|obsidian" app/ tools/ --include="*.py"` para auditar referências antes de qualquer refatoração.

---

## 2026-04-05 — DROP COLUMN quebra audit scripts que referenciam colunas legacy

**Contexto:** `medhub-cleanup` spec dropou `frente`/`verso` de `flashcards`. `tools/audit_flashcard_quality.py` usava essas colunas em `EFF_FRONT`/`EFF_BACK` (CASE ELSE fallback), quebrando com `OperationalError: no such column: verso`.

**Pitfall:** Ao dropar colunas de schema migration, verificar TODOS os scripts em `tools/` que referenciam essas colunas — não apenas os listados no scope da spec.

**Fix:** Simplificar `EFF_FRONT`/`EFF_BACK` para `COALESCE(NULLIF(TRIM(campo_v5), ''), '[placeholder]')` — sem ELSE fallback para colunas legacy.

**Grep de segurança pré-DROP:** `grep -rn "frente\|verso" tools/ --include="*.py"` antes de executar qualquer DROP COLUMN de colunas com nomes comuns.
