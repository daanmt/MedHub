# Auditoria do Mecanismo de Conhecimento — MedHub

> Data: 2026-07-12
> Autor: Stanford AI Architect (ai-eng) — modo M-OBS (observação de sistema irmão)
> Objeto: o mecanismo core que conecta RAG, indexação, gestão de conhecimento e agentes
> Âncoras brain/: `aieng-book-ch06` (RAG and Agents), `cs230-l8` (RAG pipeline), ADR-002 (curado vs quarentena)
> Método: 3 varreduras read-only sobre `C:\Users\daanm\MedHub` (código vivo, arquivos de conhecimento, governança) + medição direta do corpus

---

## 1. Veredito em uma frase

**O MedHub não sofre de falta de mecanismo de RAG — sofre de *sobreposição* de três mecanismos de conhecimento que fazem trabalho parcialmente igual, com um núcleo vivo e bom (`rag.py` two-tier) cercado de scaffold morto (LangGraph checkpointer, BM25) e de um *segundo* índice vetorial redundante (MCP obsidian) que indexa o mesmo vault com o mesmo modelo num store paralelo.** A dor real não é construir — é **consolidar para uma fonte de verdade** e **fechar o gap de curadoria** (274 PDFs de fonte nunca destilados em `.md` canônico).

Não existe "Open Knowledge Format" no código nem nos docs. O formato de conhecimento de facto do MedHub — e é um bom formato — é o **two-tier gold/bruto** herdado do ADR-002 do ai-eng: o `.md` curado é canon; o PDF bruto (`pdf_raw`) é fallback marcado; **bruto nunca vira gold só por existir** — promoção é ato humano de destilar. Este documento nomeia esse mecanismo como o core e mostra o que o cerca.

---

## 2. O mecanismo core, traduzido

Tudo que o operador listou — busca eficiente, documentação assertiva, relação ágil com agentes, código, gestão de conhecimento, continuidade — converge num **único pipeline de 4 estágios**. Ele já existe; está espalhado. Traduzido:

```
FONTE  →  CANON  →  ÍNDICE  →  RECUPERAÇÃO  →  AGENTE
(PDF)     (.md)     (Chroma)   (two-tier)      (contexto)
```

| Estágio | O que é | Onde vive hoje | Estado |
|---|---|---|---|
| **1. Fonte** | 343 PDFs Estratégia MED + Cronograma.pdf | `resumos/**/*.pdf`, `Cronograma.pdf` | bruto, imutável |
| **2. Canon** | 69 `.md` curados, schema fixo, linter-enforced | `resumos/{Área}/{Espec}/{Tema}.md` | **o coração** |
| **3. Índice** | embeddings ChromaDB, 2 collections | `data/chroma/` (207 MB) | vivo, duplicado |
| **4. Recuperação** | busca semântica two-tier gold→bruto | `app/engine/rag.py` | vivo, bom |
| **5. Agente** | injeção de contexto por tema | `app/engine/get_topic_context.py` | vivo, API estável |

**O `.md` curado (estágio 2) é o pivô de tudo.** Ele é simultaneamente: a documentação assertiva que o operador quer (schema uniforme, `## Armadilhas de Prova` obrigatória, validado no pre-commit); a unidade de indexação do RAG (chunking por H2/H3); a forma durável do conhecimento (decisão F18 — a "aula" é render efêmero do `.md`, nunca persistida); e a fonte que sombreia o PDF bruto no fallback. **Melhorar o mecanismo core = proteger e alimentar o `.md` canon.** Todo o resto (embeddings, collections, MCP) é infra a serviço dele.

Isto casa exatamente com o que o brain/ ensina:

- **[HIGH] `aieng-book-ch06`**: "Um sistema RAG = retriever (indexing + querying) + generator; o sucesso depende da qualidade do retriever." No MedHub a qualidade do retriever é **limitada pela qualidade e cobertura do canon `.md`**, não pelo algoritmo. Investir no algoritmo antes de fechar a cobertura é otimizar o estágio errado.
- **[HIGH] `aieng-book-ch06`**: "RAG é caso especial de agente onde o retriever é uma tool." `get_topic_context.py` é precisamente essa tool — a API estável que os agentes chamam em vez de tocar o SQL/vault direto. Está bem desenhada.
- **ADR-002 (ai-eng)**: bruto quarentenado (web/`pdf_raw`) nunca ganha status de canon por existir. O `pdf_raw` do MedHub aplica isto corretamente: `source=pdf_raw` fica visível, o agente trata como não-curado, o `.md` do mesmo tema o sombreia.

---

## 3. Mapa das camadas — vivo / morto / conflito

Quatro mecanismos coexistem. Só um deve sobreviver como fonte de verdade de busca.

| # | Camada | Store | Estado | Veredito |
|---|---|---|---|---|
| 1 | **`rag.py`** — Chroma + Ollama `nomic-embed-text`, two-tier, HyDE, multi-query | `data/chroma/` (`resumos` + `pdf_raw`) | **VIVO — canon** | **MANTER. É o core.** |
| 2 | **MCP `obsidian-notes-rag`** — reindexa o mesmo vault, mesmo modelo | `AppData/.../obsidian-notes-rag/medhub` (fora do repo) | **VIVO-paralelo, REDUNDANTE** | **APOSENTAR.** Segundo índice do mesmo conteúdo; nenhum código Python o consome — só um hook o reindexa a cada sessão (custo, zero uso). |
| 3a | **LangMem `consolidate_session`** — extrai insights/weak-areas via Haiku | `medhub_memory.db::memory_store` (571 rows) | **VIVO** | MANTER — é memória de agente (long-term), função distinta do RAG de conteúdo. |
| 3b | **LangGraph `SqliteSaver` checkpointer** | `medhub_memory.db::checkpoints` (nunca criada) | **MORTO — scaffold** | **REMOVER.** README confessa: "scaffold for an agent that does not live in this repo." `app/memory/tools.py` citado no README **nem existe**. |
| 4 | **`_bm25_rerank`** — reranking lexical | — | **MORTO — desabilitado** | **REMOVER** o código + tirar `rank-bm25` do requirements (regressão medida 90%→73%). |
| 5 | **`pubmedmcp`** | — (API externa) | VIVO | Manter — é tool de literatura sob demanda, não RAG de corpus. Fora do escopo. |

**Contradição das camadas 1 e 2**: `AGENTE.md §2 L53` manda o agente buscar via MCP obsidian; `ROADMAP.md L124` já decidiu empiricamente **descontinuar o MCP e ficar com `rag.py` local**. Duas fontes de verdade sobre qual é o motor de busca. Isto é o exemplo perfeito da "bagunça" — não é código ruim, é **decisão tomada mas não propagada**.

---

## 4. As quatro contradições vivas

Não são bugs de código — são **drifts de estado entre documento e realidade**. Cada uma é um ponto onde um agente (ou o operador) pode agir sobre informação obsoleta.

1. **Motor de busca duplo** (§3 acima). `AGENTE.md` diz MCP; `ROADMAP` diz `rag.py`. → Decidir: `rag.py` é o motor. Reescrever `AGENTE.md §2` e remover o hook de reindexação do MCP.

2. **PRD ciclo 3 "AGUARDA go" × já implementado PASS.** `.vibeflow/prds/pipeline-conhecimento.md L8` diz que aguarda aprovação; mas as 4 ondas foram implementadas e auditadas PASS em 2026-07-06 (`pipeline-conhecimento-part-{1..4}-audit.md`) e o `pdf_raw` está vivo (14.216 chunks). → O cabeçalho do PRD está stale; marcar IMPLEMENTADO. *(Nota: meu próprio STATE.md em ai-eng carregava a mesma stale — corrigido nesta sessão.)*

3. **F21 "ABERTO" × resolvido no contrato.** `AUDITORIA_MEDHUB.md L292` e `HANDOFF.md L27` marcam F21 como aberto ("fora do PRD por lapso"); verifiquei in-code: **está resolvido** — `revisao-calibrada-contract.md v1.2` Cláusula 10 + Invariante E ("descompressão calibrável × cobertura piso fixo; compressão encurta, nunca corta"). → Fechar F21 no ledger e no HANDOFF.

4. **Contadores de corpus divergentes.** README "44", ESTADO "66", HANDOFF "69". Medição real desta auditoria: **69 `.md`**. → Fonte única de contagem (derivar de `find`, não hardcode — o MedHub já tem o padrão "números derivados, nunca digitados" do ciclo 2).

---

## 5. O corpus em números (medido, não estimado)

| Métrica | Valor | Leitura |
|---|---|---|
| `.md` canon (gold) | **69** | a fonte de verdade real |
| Palavras no gold | **178.459** | — |
| **Tokens estimados do gold** | **~238.000** | **acima** do limiar de 200k do ch06 |
| PDFs de fonte | **343** | material bruto |
| **PDFs sem `.md` correspondente** | **~274 (80%)** | **o maior débito de conhecimento** |
| Chunks no Chroma gold | ~1.048 | — |
| Chunks no Chroma `pdf_raw` | ~14.216 | 13× o gold |
| Peso do vector store | 207 MB | — |

**A leitura que importa** — `aieng-book-ch06 [MEDIUM]`: "se a knowledge base < 200k tokens (~500 páginas), pode incluir tudo no prompt sem RAG; acima disso, RAG passa a valer." O gold do MedHub está em **238k tokens** — ou seja, **atravessou o limiar há pouco**. Isso tem duas consequências:

- **Ter RAG é justificado** (o gold já não cabe confortavelmente num prompt), então a Camada 1 não é over-engineering.
- **Mas a margem é estreita.** O gold sozinho quase caberia. A complexidade real (segundo índice MCP, `pdf_raw` de 14k chunks) é desproporcional ao tamanho do canon. **A prioridade não é mais infra de retrieval — é curadoria**: transformar parte dos 274 PDFs órfãos em `.md` gold. Cada PDF destilado melhora o retriever mais do que qualquer ajuste de algoritmo, porque move conteúdo de "fallback não-curado" para "canon sombreador".

Isto é o padrão **data-centric** do brain/ (`aieng-book-ch08`): a alavanca está nos dados, não no modelo. E o **"form vs facts"** do ch06/ch07: a lacuna do MedHub é de *fatos* (cobertura), não de *comportamento* (o retriever funciona).

---

## 6. Recomendações priorizadas

Ordenadas por (impacto no core ÷ custo). As três primeiras são higiene de baixo risco; as duas últimas são a alavanca real.

| # | Ação | Tipo | Por quê |
|---|---|---|---|
| **R1** | **Aposentar o MCP obsidian** — remover o server do `.mcp.json` e o hook de reindexação; reescrever `AGENTE.md §2` para apontar `rag.py` | consolidar | Elimina o 2º índice redundante e a contradição nº1. Zero perda (nada o consome). |
| **R2** | **Remover scaffold morto** — `checkpointer.py`, referência a `tools.py` inexistente no README, `_bm25_rerank` + `rank-bm25` do requirements | limpar | Reduz a superfície "bagunça" sem tocar nada vivo. |
| **R3** | **Reconciliar os 4 drifts de estado** (§4) — fechar F21, marcar PRD implementado, unificar contador de resumos derivando de `find` | continuidade | A "bagunça" é sobretudo doc-vs-realidade. Fechar isto é o maior ganho de *documentação assertiva* por hora investida. |
| **R4** | **Fechar cobertura** — usar `tools/cobertura_conhecimento.py` para priorizar os 274 PDFs órfãos por rendimento (grade × volume de erro) e destilar em lote os top-N | curadoria | A alavanca real do retriever (§5). Move conteúdo de fallback→canon. Já tem o CLI; falta a cadência. |
| **R5** | **Um fallback textual no engine** — hoje `rag.py.search()` retorna `[]` se Ollama/Chroma cai; só a UI degrada para `os.walk`. Dar ao engine um fallback lexical (glob por `path.stem`/frontmatter, que `get_topic_context` já faz) | robustez | Continuidade: o agente não deve ficar cego quando o Ollama está offline. Baixo custo, usa infra existente. |

**O que NÃO fazer** (anti-escopo, para não recriar a bagunça):
- Não reativar BM25 (regressão medida).
- Não trocar embeddings nem adicionar deps (o `nomic-embed-text` local basta para 238k tokens).
- Não tocar chunking/collection/qualidade do gold (o ciclo 3 já os fixou).
- Não persistir a "aula" como artefato (F18 — o `.md` é a forma durável).
- Não introduzir GraphRAG/KG agora — o brain/ mantém essa ponte como gap aberto (mesa Tier-3); o corpus de 238k tokens não a justifica.

---

## 7. Como isto vira o próximo ciclo

Esta auditoria é o insumo do `/vibeflow:discover` que a segue. O PRD do próximo ciclo do MedHub deve escopar **R1+R2+R3 como uma onda de consolidação** (higiene, baixo risco, alta clareza) e **R4 como a onda de curadoria** (a alavanca de valor). R5 é aditivo, entra onde couber.

O mecanismo core não precisa ser reconstruído. Precisa ser **nomeado, desobstruído e alimentado** — nesta ordem.

---

*Registro M-OBS correspondente: `ai-eng/brain/observed-systems/2026-07-12-medhub-mecanismo-conhecimento.md`. Este documento é imutável (convenção de artefato dated); revisões futuras criam novo arquivo.*
