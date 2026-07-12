# PRD: Consolidação do Mecanismo de Conhecimento

> Generated via /vibeflow:discover on 2026-07-12
> Ancorado em: `docs/AUDITORIA-MECANISMO-CONHECIMENTO-2026-07-12.md`
> Relacionado: `medhub-core-simplification.md`, `pipeline-conhecimento.md` (ciclo 3, implementado)

## Problem

O mecanismo de conhecimento do MedHub tem um núcleo bom (`app/engine/rag.py` two-tier, gold + `pdf_raw`) cercado de sobreposição histórica que se acumulou sem ser removida. Três mecanismos de busca/memória coexistem fazendo trabalho parcialmente redundante:

1. **Índice vetorial duplicado**: além do Chroma local de `rag.py`, um MCP `obsidian-notes-rag` reindexa **o mesmo vault, com o mesmo modelo** (`nomic-embed-text`), num store paralelo fora do repo. Nenhum código Python o consome — só um hook o reindexa a cada sessão (custo, zero uso). `ROADMAP.md L124` já decidiu descontinuá-lo, mas `AGENTE.md §2 L53` ainda manda o agente buscar por ele.
2. **Scaffold morto**: `app/memory/checkpointer.py` (LangGraph `SqliteSaver`) é scaffold de um agente que não existe no repo (confessado no `README.md L54`); `app/memory/tools.py` é citado no README mas **não existe**; `_bm25_rerank` está desabilitado por regressão medida (90%→73%) mas `rank-bm25` segue no `requirements.txt`.
3. **Drift doc-vs-realidade**: quatro estados divergem entre documento e código — motor de busca (MCP × `rag.py`), PRD `pipeline-conhecimento` ("AGUARDA go" × implementado PASS), F21 ("ABERTO" × resolvido no contrato v1.2), e o contador de resumos (README "44" / ESTADO "66" / HANDOFF "69" / real **69**).

O efeito é a "bagunça" percebida: não é código ruim, é **decisão tomada mas não propagada** e **redundância nunca removida**. Um agente (ou o operador) pode agir sobre informação obsoleta a qualquer momento.

## Target Audience

Primário: **o agente de IA do MedHub** — que hoje recebe instrução ambígua sobre qual motor de busca usar e carrega scaffold que não faz nada. Secundário: **o operador (Daniel)**, que precisa de documentação assertiva e de um mecanismo com uma só fonte de verdade para confiar na continuidade entre sessões.

## Proposed Solution

Uma **onda de consolidação** que reduz o mecanismo a uma única fonte de verdade, sem tocar o núcleo que funciona. Em alto nível:

- **Aposentar o índice redundante**: remover o MCP `obsidian-notes-rag` do `.mcp.json` e o hook de reindexação; `rag.py` local passa a ser o único motor de busca semântica.
- **Remover o scaffold morto**: apagar `checkpointer.py`, a referência a `tools.py` inexistente, o `_bm25_rerank` e a dep `rank-bm25`.
- **Reconciliar os quatro drifts**: reescrever `AGENTE.md §2` para apontar `rag.py`; marcar `pipeline-conhecimento` como IMPLEMENTADO; fechar F21 no ledger/HANDOFF; unificar o contador de resumos derivando de `find` (o MedHub já tem o padrão "números derivados, nunca digitados").
- **Robustez de continuidade (R5)**: dar a `rag.py.search()` um fallback textual (glob por `path.stem`/frontmatter, que `get_topic_context` já implementa) para o agente não ficar cego quando Ollama/Chroma estão offline.
- **Tornar o gap de cobertura visível (lado-ferramenta de R4)**: WARN em `auto_check --all` quando o tema da semana corrente não tem `.md` canônico, com ranking por rendimento via `cobertura_conhecimento.py`. **NÃO** destila conteúdo — só torna o débito impossível de ignorar.

O princípio-guia da auditoria: o mecanismo core não precisa ser reconstruído, precisa ser **nomeado, desobstruído e alimentado** — nesta ordem. Este PRD faz "nomear" e "desobstruir". "Alimentar" (a curadoria dos PDFs) é trabalho de conteúdo do operador, fora deste escopo.

## Success Criteria

1. `.mcp.json` não contém mais `obsidian-notes-rag`; nenhum hook o reindexa; `grep obsidian-notes-rag` no repo retorna zero refs vivas.
2. `app/memory/checkpointer.py` e a referência a `tools.py` no README removidos; `rank-bm25` fora do `requirements.txt`; `pytest` continua verde.
3. `AGENTE.md`, `ROADMAP.md`, `pipeline-conhecimento.md` (header), `AUDITORIA_MEDHUB.md` (F21) e `HANDOFF.md` concordam entre si sobre motor de busca, estado do ciclo 3 e F21 — verificável por leitura cruzada.
4. Contador de resumos aparece em **um** lugar canônico, derivado em runtime; os demais docs referenciam, não hardcodam.
5. Com Ollama parado, um agente que chama o engine ainda recebe conteúdo relevante por tema (fallback textual), em vez de `[]`.
6. `auto_check --all` emite WARN quando o tema da semana não tem `.md` canônico.

## Scope v0

- Remoção do MCP obsidian (`.mcp.json` + hook em `tools/hooks/memory_session_log.py`).
- Remoção de scaffold morto (`checkpointer.py`, ref `tools.py`, `_bm25_rerank`, dep `rank-bm25`).
- Reconciliação dos 4 drifts nos docs (AGENTE.md, ROADMAP.md, pipeline-conhecimento.md header, AUDITORIA_MEDHUB.md F21, HANDOFF.md).
- Contador de resumos derivado (fonte única).
- Fallback textual no engine RAG.
- WARN de cobertura no `auto_check --all` (ranking já existe em `cobertura_conhecimento.py`).

## Anti-scope

- **NÃO destilar PDFs em `.md`** — isso é autoria de conteúdo clínico (trabalho do operador), não engenharia. Este PRD só torna o gap visível.
- **NÃO tocar** chunking, collections, qualidade ou embeddings do gold — o ciclo 3 já os fixou.
- **NÃO reativar BM25** (regressão medida).
- **NÃO adicionar** deps, modelos ou vector stores novos — `nomic-embed-text` local basta para 238k tokens de gold.
- **NÃO introduzir GraphRAG/KG** — o corpus não justifica; segue como mesa Tier-3 no ai-eng.
- **NÃO remover** a Camada 3a (LangMem `consolidate_session`) — é memória de agente viva, função distinta do RAG de conteúdo.
- **NÃO persistir** a "aula" como artefato (decisão F18 — o `.md` é a forma durável).

## Technical Context

- **Núcleo a preservar**: `app/engine/rag.py` (two-tier gold→`pdf_raw`, HyDE, multi-query, chunking H2/H3), `app/engine/get_topic_context.py` (API estável que agentes chamam — pattern `domain-engine-api.md`).
- **Padrões a seguir**: `patterns/domain-engine-api.md` (agentes vão pelo engine, nunca SQL direto), `patterns/db-access-layer.md` (só `db.py` importa sqlite3), `patterns/agent-workflow-protocol.md` (AGENTE.md é contrato). Convenções pt-BR, flat design, números derivados.
- **Corpus medido (2026-07-12)**: 69 `.md` gold ≈ 178.459 palavras ≈ **238k tokens** (acima do limiar de 200k que justifica RAG — `aieng-book-ch06`); 343 PDFs de fonte, ~274 sem `.md`; Chroma 207 MB (gold ~1.048 chunks, `pdf_raw` ~14.216).
- **Fallback textual (R5)**: reusar a lógica de índice `{termo→path}` de `get_topic_context.py` (rglob + `path.stem` + frontmatter + difflib) como degradação de `rag.py.search()` — infra já existe, é wiring.
- **Restrição de continuidade**: o índice de resumos é cacheado em memória do processo (`get_topic_context.py`) — resumos novos numa sessão não aparecem sem reiniciar; considerar invalidação, mas fora do v0 se aumentar risco.
- **Budget**: ≤6 arquivos por task (index.md). A onda deve ser fatiada — a reconciliação de docs e a remoção de código são tasks separadas.

## Open Questions

- **Sobreposição com `medhub-core-simplification.md`**: esse PRD já pode cobrir parte da remoção de scaffold — verificar na fase de gen-spec para não duplicar; se cobrir, este PRD cede R2 a ele e foca R1/R3/R5.
- **Invalidação do cache do índice de resumos**: entra no v0 (R5) ou vira débito registrado? Recomendação: registrar como follow-up se aumentar o blast radius do fallback.
- **Cadência de curadoria (R4 real)**: a destilação dos 274 PDFs precisa de um PRD próprio de *conteúdo* (ou de uma rotina de estudo), não de engenharia — decisão do operador sobre quando abrir.
