> **Status:** archived — phase complete. Frozen reference; not part of the active vibeflow surface.

# Spec: MedHub — Study Engine Core (Operações de Consulta)

> Gerado via /vibeflow:gen-spec em 2026-04-05
> Fase 2 de 3 | PRD: `.vibeflow/prds/medhub-core-simplification.md`

## Objective

Criar `app/engine/` como biblioteca de domínio com 3 funções de consulta estáveis,
tipadas e documentadas, consumíveis por agentes externos sem queries ad hoc.

## Context

Agentes externos (Claude Code, Cursor, Antigravity) hoje precisam conhecer o schema
do `ipub.db`, o layout de `resumos/`, e a API do LangMem para responder "o que errrei
em Cardiologia?" ou "quais cards vencem hoje?". Não existe interface unificada — cada
sessão reinventa as queries. O `app/engine/` é a solução: uma biblioteca Python pura
com contratos explícitos.

Esta spec cobre as 3 funções de **leitura** (sem efeitos colaterais). As funções de
escrita/geração ficam na Fase 3.

## Definition of Done

- [ ] `app/engine/__init__.py` exporta `get_topic_context`, `get_review_queue`, `summarize_performance`
- [ ] Cada função tem: type hints completos em parâmetros e retorno, docstring com descrição das chaves do dict retornado, retorno `dict` (nunca raw rows ou strings livres)
- [ ] `get_topic_context("Cardiologia")` retorna dict com chaves `resumo_path`, `resumo_content`, `erros_recentes`, `cards_ativos`, `weak_areas` sem lançar exceção quando qualquer fonte estiver vazia
- [ ] `get_review_queue()` retorna dict com chaves `atrasados`, `hoje`, `novos` (cada qual: `list[dict]` com `card_id`, `frente_pergunta`, `verso_resposta`, `due`)
- [ ] `summarize_performance(area=None)` retorna dict com `total_erros`, `taxa_acerto`, `padroes` (lista de weak_areas) sem chamar LangGraph nem lançar exceção se `medhub_memory.db` estiver ausente
- [ ] Nenhuma função em `app/engine/` importa `sqlite3` diretamente — todas chamam `app.utils.db` ou helpers de `app.memory` (conventions.md Don't #1 aplicado ao engine, sem exceção)
- [ ] `python -c "from app.engine import get_topic_context, get_review_queue, summarize_performance; print('OK')"` executa sem erro com o projeto em `sys.path`

## Scope

| Arquivo | Ação |
|---|---|
| `app/engine/__init__.py` | CRIAR — exports públicos do módulo |
| `app/engine/get_topic_context.py` | CRIAR — resumo index + query de erros/cards + LangMem weak_areas |
| `app/engine/get_review_queue.py` | CRIAR — fila FSRS por bucket |
| `app/engine/summarize_performance.py` | CRIAR — métricas de ipub.db + weak_areas |
| `app/utils/db.py` | EDITAR CONDICIONALMENTE — adicionar `get_cards_by_bucket()` e `get_erros_por_tema()` se não existirem |

## Anti-scope

- NÃO criar `generate_flashcards.py` ou `analyze_error.py` (Fase 3)
- NÃO modificar pages Streamlit (engine é biblioteca, não tem UI)
- NÃO ativar LangGraph em nenhum path
- NÃO expor como MCP server ou CLI nesta spec
- NÃO modificar `tools/insert_questao.py`

## Technical Decisions

**Resumo index — frontmatter + aliases, não filename:**
```python
# app/engine/get_topic_context.py
_resumo_index: dict[str, Path] | None = None  # lazy-loaded

def _build_index() -> dict[str, str]:
    """Constrói índice {termo_lower → path} a partir de frontmatter de resumos/."""
    index = {}
    for path in Path("resumos").rglob("*.md"):
        fm = _parse_frontmatter(path)
        if not fm:
            continue
        # Indexa por especialidade
        if esp := fm.get("especialidade"):
            index[esp.lower()] = str(path)
        # Indexa por cada alias
        for alias in fm.get("aliases", []):
            index[alias.lower()] = str(path)
    return index

def _find_resumo(tema: str) -> Path | None:
    index = _get_or_build_index()
    # Exact match
    if hit := index.get(tema.lower()):
        return Path(hit)
    # Fuzzy fallback
    matches = difflib.get_close_matches(tema.lower(), index.keys(), n=1, cutoff=0.6)
    return Path(index[matches[0]]) if matches else None
```

**LangMem read-only sem LangGraph:**
`summarize_performance()` acessa `weak_areas` e `session_insights` exclusivamente via
`app/memory/`. Se existir API pública (ex: `app.memory.store.search(namespace)`), usá-la.
Se não existir, **criar helper read-only em `app/memory/`** — por exemplo:
```python
# app/memory/reader.py
def get_weak_areas(area: str | None = None) -> list[dict]:
    """Lê weak_areas do SQLiteMemoryStore sem LangGraph. Retorna [] se DB ausente."""
    ...
```
`app/engine/` importa este helper. **Nunca importa `sqlite3` diretamente**, mesmo para
leitura de `medhub_memory.db`. Se `medhub_memory.db` não existir → retornar `[]` silenciosamente.

**`app/utils/db.py` — novas funções necessárias:**
Verificar se `get_flashcards_due()` (ou equivalente que retorna por bucket atrasado/hoje/novos)
já existe. Se não, adicionar:
```python
def get_cards_by_bucket() -> dict[str, list[dict]]:
    """Retorna flashcards divididos em atrasados/hoje/novos para o FSRS player."""
    conn = get_connection()
    now = datetime.now()
    # atrasados: due < hoje (state > 0)
    # hoje: due between hoje_inicio e hoje_fim (state > 0)
    # novos: state == 0, limit 10
    conn.close()
    return {"atrasados": [...], "hoje": [...], "novos": [...]}
```

**Retorno estruturado — sem exceções:**
Cada função do engine usa `try/except` amplo com fallback para dict vazio em cada fonte:
```python
def get_topic_context(tema: str, area: str | None = None) -> dict:
    resumo_path = _find_resumo(tema)
    erros = []
    try:
        erros = db.get_erros_por_tema(tema)
    except Exception:
        pass  # safe default
    ...
    return {"resumo_path": str(resumo_path) if resumo_path else None, ...}
```

## Applicable Patterns

- **`db-access-layer.md`** — engine chama db.py; `app/engine/` não importa `sqlite3` diretamente
- **`error-insertion-pipeline.md`** — entender o schema de `questoes_erros` para `get_erros_por_tema()`

## Risks

| Risco | Mitigação |
|---|---|
| Frontmatter de alguns resumos tem `type: resumo` / `status: ativo` (legacy) | Parser de frontmatter deve ser tolerante — extrair campos que existam, ignorar o resto |
| `[CIR] Trauma.md` tem prefixo `[CIR]` no nome — indexação por frontmatter resolve, mas fuzzy match no filename pode confundir | Fuzzy match opera sobre as chaves do índice (termos normalizados), não sobre file paths |
| `app/memory/` API pode exigir event loop assíncrono para `.search()` | Se async, criar `app/memory/reader.py` com leitura síncrona — não usar `asyncio.run()` em funções do engine nem fallback para sqlite3 direto |
| `get_review_queue()` duplicar lógica do FSRS player em `2_estudo.py` | Extrair para db.py a função de query; ambos chamam o mesmo db.py |

## Known Limitations (documentar na docstring)

- O índice de resumos é construído no primeiro acesso e cacheado em memória. Novos resumos
  adicionados durante uma sessão Python não serão indexados sem reinicializar o módulo.
- `medhub_memory.db` é local-only (não commitado). Em ambientes sem o arquivo, todas as
  funções do engine retornam `padroes: []` e `weak_areas: []` silenciosamente.

## Dependencies

- `.vibeflow/specs/medhub-cleanup.md` — executar antes (garante que colunas legacy foram removidas e db.py está limpo)
