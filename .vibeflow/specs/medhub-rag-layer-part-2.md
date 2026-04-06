# Spec: MedHub RAG Layer — Part 2: Integration & UI

> Generated via /vibeflow:gen-spec on 2026-04-05
> PRD: .vibeflow/prds/medhub-rag-layer.md

## Objective

Substituir `_extract_relevant_section()` por `relevant_chunks` no pipeline de geração de flashcards, e expor busca semântica na tab "Resumos RAG" da Biblioteca.

## Context

Após Part 1, `get_topic_context()` retorna `relevant_chunks: list[dict]`. Dois consumidores precisam ser atualizados:

1. **`generate_flashcards.py`** — hoje usa `_extract_relevant_section(resumo_content, elo_quebrado)` para extrair trecho por keyword match em H3. Com RAG disponível, o trecho semântico vem direto de `relevant_chunks[0]["text"]`, mais preciso e sem depender de overlap léxico.

2. **`3_biblioteca.py`** — tab1 "Resumos RAG" é um `os.walk` file browser sem busca. Com o index ChromaDB disponível, uma caixa de busca semântica é trivial de adicionar e de alto valor para demonstração (entrevista, uso diário).

## Definition of Done

1. `generate_contextual_cards()` aceita `relevant_chunks: list[dict]` como parâmetro opcional; quando não-vazio, usa `relevant_chunks[0]["text"]` como `trecho` em `_llm_generate()` e pula `_extract_relevant_section()` — assinatura retrocompatível (parâmetro com default `None`)
2. `3_biblioteca.py` tab1 tem `st.text_input("Busca semântica", ...)` acima da lista de resumos; ao submeter query não-vazia, chama `rag.search(query, n_results=5)` e renderiza cada resultado como `st.expander(section_header)` com texto do chunk + link `[→ Abrir resumo]`
3. UI de busca exibe mensagem de estado quando sem resultados ou quando ChromaDB/Ollama offline — sem `st.error` não tratado, sem crash
4. **Quality gate:** segue `streamlit-page-structure` pattern — `inject_styles()` chamado no topo; sem `import sqlite3`; sem gradientes/shadows (flat design); `@st.cache_data` não aplicado ao resultado da busca semântica (resultado muda com o índice, não deve cachear por TTL)

## Scope

- **`app/engine/generate_flashcards.py`** (modificar) — adicionar parâmetro `relevant_chunks` e usá-lo como `trecho` quando disponível
- **`app/pages/3_biblioteca.py`** (modificar) — adicionar busca semântica na tab1

## Anti-scope

- Não modificar `tools/insert_questao.py` — ele chama `generate_contextual_cards()` sem `relevant_chunks`; fallback para `_extract_relevant_section()` é o comportamento correto nesses casos
- Não criar nova página nem nova tab para RAG — busca fica dentro da tab1 existente
- Não mostrar scores de distância/similaridade no UI (usuário final não precisa)
- Não adicionar paginação de resultados — top-5 chunks são suficientes
- Não modificar `app/engine/rag.py` ou `get_topic_context.py` — consolidados na Part 1

## Technical Decisions

### Assinatura retrocompatível em `generate_contextual_cards()`

```python
def generate_contextual_cards(
    tema: str,
    elo_quebrado: str,
    armadilha: Optional[str] = None,
    resumo_content: Optional[str] = None,
    relevant_chunks: Optional[list[dict]] = None,  # NEW
) -> list[dict]:
    if relevant_chunks:
        trecho = relevant_chunks[0]["text"]
    elif resumo_content:
        trecho = _extract_relevant_section(resumo_content, elo_quebrado)
    else:
        return _heuristic_generate(elo_quebrado, armadilha)
    
    try:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY não definida")
        cards = _llm_generate(elo_quebrado, armadilha, trecho)
        for c in cards:
            c["quality_source"] = "contextual"
            c["needs_qualitative"] = 0
        return cards
    except Exception:
        return _heuristic_generate(elo_quebrado, armadilha)
```

**Rationale:** `tools/insert_questao.py` chama `generate_contextual_cards(tema, elo, armadilha, resumo_content)` — sem `relevant_chunks`. Essa chamada continua funcionando exatamente como antes. O parâmetro novo só é usado quando o caller (`2_estudo.py` ou agente) passa explicitamente os chunks recuperados via RAG.

`_extract_relevant_section()` permanece no arquivo — ainda é o fallback para casos sem RAG.

### UI de busca na Biblioteca

```python
# tab1 — ANTES da lista de resumos existente
query = st.text_input("Busca semântica", placeholder="Ex: critérios SIRS neonato, manejo sepse choque...")

if query.strip():
    try:
        from app.engine.rag import search as rag_search, _CHROMA_AVAILABLE
        if not _CHROMA_AVAILABLE:
            st.info("Índice semântico não disponível. Execute: python tools/index_resumos.py")
        else:
            resultados = rag_search(query.strip(), n_results=5)
            if not resultados:
                st.caption("Nenhum resultado. O índice pode estar vazio — execute tools/index_resumos.py")
            else:
                for r in resultados:
                    section = r["metadata"].get("section", "—")
                    source = r["metadata"].get("source", "")
                    with st.expander(f"{section}  ·  {Path(source).stem if source else ''}"):
                        st.markdown(r["text"])
                        if source:
                            st.caption(f"Fonte: `{source}`")
    except Exception as e:
        st.warning(f"Busca semântica indisponível: {e}")

st.divider()
# ... lista de resumos existente continua abaixo
```

**`@st.cache_data` deliberadamente ausente** na busca: o índice ChromaDB é mutável (reindexação manual) e queries são arbitrárias — cachear por TTL retornaria resultados stale sem benefício real.

**Estado da busca:** usar `st.text_input` sem `on_change` — Streamlit re-executa a página a cada keystroke por padrão, mas com debounce implícito do browser. Não usar `st.form` (adiciona Submit button desnecessário para busca ad-hoc).

## Applicable Patterns

- **`streamlit-page-structure.md`** — página começa com `st.set_page_config` + `inject_styles()`; tabs com `st.tabs`; sem st.expander no top level (expanders são usados dentro de uma tab, ok)
- **`design-system-usage.md`** — flat design; sem gradientes; usar `st.caption()` para metadados secundários (fonte do chunk)

## Risks

| Risco | Probabilidade | Mitigação |
|-------|--------------|-----------|
| Ollama offline ao usar busca na Biblioteca | Média | `try/except` no bloco de busca mostra `st.warning` — não crasha |
| ChromaDB não indexado (data/chroma/ vazio) | Alta no first-run | `st.info` orientando a rodar `tools/index_resumos.py` |
| Caller antigo de `generate_contextual_cards()` quebrar | Baixa | Parâmetro `relevant_chunks=None` com default — retrocompatível |
| `relevant_chunks[0]["text"]` muito longo para o prompt | Baixa | Chunks são bounded a 1500 chars por Part 1 — seguro para o contexto de Haiku |

## Dependencies

- `.vibeflow/specs/medhub-rag-layer-part-1.md` — deve estar implementado antes desta spec
