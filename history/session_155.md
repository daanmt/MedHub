# Session 155 -- /graphify MVP (codigo + resumos Pediatria/GO com overlay de performance) + auditoria F37 + limpeza .vibeflow

**Data:** 2026-08-25
**Ferramenta:** Claude Code (Sonnet 5)
**Continuidade:** Sessao 154

---

## O que foi feito

### Arco 1 -- /graphify em tools/+core/ (piloto do skill)

Usuario invocou `/graphify` sem argumento. Deteccao inicial encontrou 622 arquivos (~800k palavras) no repo inteiro, acima do limite de escopo do skill; usuario escolheu `tools/ + core/` entre as opcoes apresentadas. Corpus resultante: 124 arquivos (112 codigo + 12 docs/contratos), 131k palavras -- sem necessidade de chave de API (extracao AST para codigo, 1 subagent Sonnet para os 12 `.md` de `core/contracts/` + READMEs). Grafo final: 1344 nos, 2408 arestas, 75 comunidades. Health check: 552 arestas dangling (esperado -- AST referenciando simbolos externos/stdlib nao extraidos como nos) + ~60 arestas colapsadas (relacoes multiplas entre o mesmo par de nos). 75 comunidades rotuladas manualmente (nomes 2-5 palavras por comunidade, ex.: "Cronograma Sync & Gap", "Auto-Check Harness", "RAG Eval & Evidence Governance"). Achado principal: `taxonomia_cronograma table` e o no de maior betweenness centrality do grafo, ponte entre 5 comunidades (migrations, flashcard quality, day-plan, review-log, review-radar) -- tracado no fechamento do Arco 1: a tabela tem **3 scripts de reparo dedicados** (`dedup_taxonomia.py`, `fix_taxonomy_bridge.py`, `popular_subtemas.py`), cicatriz estrutural dos varios pivots do projeto.

### Arco 2 -- Limpeza de `.vibeflow/patterns/` (achado durante a discussao de proximo passo)

Usuario pediu para investigar se `.vibeflow` (plugin spec-driven usado na construcao do MedHub) tinha entulho acumulado de pivots antigos, com constraint explicito: no maximo 3 subagents Sonnet se usados, priorizando eficiencia. Investigacao (sem subagents -- feita diretamente) revelou que a pergunta ja tinha sido respondida: auditoria de arquitetura da s144 (7 subagents + verificacao adversarial) concluiu **".vibeflow/ e mecanismo ativo, nao entulho"** -- `AUDITORIA_MEDHUB.md` cita `.vibeflow/{prds,specs,audits}/*.md` constantemente como trilha real de engenharia. Achado real, mais estreito: 3 dos 9 `patterns/` estavam **provadamente mortos** -- `design-system-usage.md`, `streamlit-page-structure.md` e `fsrs-review-flow.md` descreviam a UI Streamlit e o FSRS caseiro, ambos confirmados removidos por 3 fontes independentes (`AGENTE.md:153`, `.claude/commands/revisar.md:150`, ausencia de `app/pages/`/`styles.py`/`streamlit_app.py` no disco) -- zero referencia viva confirmada por grep no repo inteiro antes da delecao (regra do usuario: "fica ou morre, prova de zero referencia viva"). Os 6 patterns restantes ganharam frontmatter (`status: active`, `canonical_source:`, `last_verified: 2026-08-25`); `domain-engine-api.md` e `db-access-layer.md` tiveram conteudo corrigido (exports de `app.engine` ja eram 1, nao 5 como o pattern alegava; exemplos de codigo desatualizados removidos em favor de apontar pro docstring do modulo). Criado `.vibeflow/patterns/README.md` (guia de wayfinding). Bonus: `.claude/settings.local.json` tinha 2 entradas de permissao mortas (`py_compile` em arquivos Streamlit ja removidos) -- limpas.

### Arco 3 -- Grafo de conhecimento clinico: Pediatria + GO com overlay de performance (`ipub.db`)

Usuario propos testar `/graphify` no conteudo clinico real (nao so arquitetura), como MVP da integracao e como estudo pratico de knowledge graphs/ontology engineering. Escopo acordado: `resumos/Pediatria/` (17 `.md`) + `resumos/GO/` (25 `.md`, cobre Ginecologia+Obstetricia apesar do nome da pasta) -- 42 arquivos, so notas pessoais (`.md`), nao os PDFs-fonte do EMED (material generico, ja servido pelo RAG). Plano formal escrito via `EnterPlanMode`/`ExitPlanMode` (arquivo em `C:\Users\daanm\.claude\plans\reactive-hugging-sunbeam.md`), aprovado pelo usuario.

**Fase A (extracao semantica, 2 subagents Sonnet):** 227+263 = 490 nos, 190+273 = 463 arestas, 6 hyperedges. Cobriu diagnosticos diferenciais, medicamentos, criterios diagnosticos e as secoes de "armadilha"/"regra mestre" de cada resumo (guardadas como atributo `rationale` no no, nao como no separado).

**Fase B (overlay deterministico de `ipub.db`, sem LLM):** script em duas partes. B1 -- consulta `taxonomia_cronograma`/`questoes_erros`/`flashcards`/`fsrs_cards`/`habilidades` escopados pra Pediatria/GO/Ginecologia/Obstetricia; casamento tema-arquivo via `normaliza_stem()` (reuso de `tools/cobertura_conhecimento.py`) + scorer fuzzy (`SequenceMatcher` + Jaccard de tokens, calibrado empiricamente pra texto cross-source, thresholds 0.60/0.40) + 6 overrides manuais pra casos com zero overlap lexical mas match semantico real (ex.: "Suplementacao de Ferro" -> "Deficiencias Vitaminicas e Profilaxias"). Resultado: 57/80 temas casados; 23 genuinamente sem resumo dedicado apesar de volume real de questoes (`PTI`=428q, `Traumatismo Cranioencefalico`=428q, `Doenca de Kawasaki`, `Bronquiolite`, `Meningite Tuberculosa`, `Anafilaxia e Urticaria`, entre outros). B2 -- resolve os arquivos casados contra os IDs reais de no do grafo da Fase A (padrao empirico: `{stem}_{stem}` como no primario por arquivo) e emite fragmento no schema do graphify (nos `erro`/`flashcard`/`habilidade_recorrente`, arestas EXTRACTED/confidence=1.0 -- dado estruturado, sem necessidade de LLM). Achado lateral durante a construcao: 56 flashcards em escopo tinham `questao_id` apontando pra erros de **outras areas** (Cirurgia/Pneumo/Hemato, todos em temas `[bulk]`) -- refinamento de tema entre o erro bulk-importado e o card corrigido depois; arestas descartadas por estarem fora de escopo, nao um bug do script.

**Fase C+D (merge + sintese):** merge no nivel de extracao (nao via CLI `merge-graphs`, que so opera sobre grafos ja construidos e derrubava ~700 arestas cujo alvo nao existia isoladamente no fragmento). Grafo final: 1258 nos, 1541 arestas, 133 comunidades, saude limpa (so 6 arestas colapsadas residuais). Sintese das 3 perguntas diagnosticas do plano:
1. **Conceitos ima-de-erro:** `VOP (Vacina Oral Poliomielite -- descontinuada)` com 21 erros -- vacina que o proprio resumo do usuario marca como descontinuada, ainda cobrada repetidamente; confirma estruturalmente a fraqueza persistente ja nomeada em memoria ("Pediatria/Imunizacoes"). Tambem: Eclampsia (21), Pre-Natal (20, maior grau do grafo inteiro), Cervicite Gonococo+Chlamydia (15).
2. **Bem anotado mas nunca revisado de fato:** `Placenta Previa` (10 conexoes no resumo, unico flashcard vinculado com `reps=0`).
3. **Habilidades recorrentes cruzando Pediatria<->GO:** "rotular cada alternativa V/F" (4 ocorrencias, 3 areas) e "marcar a falsa" (2 ocorrencias, 2 areas) -- mesma familia do bug de enunciado negativo, agora visivel como ponte entre especialidades, nao so por tema. Validou a tese "padrao metacognitivo > conteudo clinico" a partir de um angulo novo.

### Arco 4 -- Achado F37 (auditoria): anomalia de `questoes_realizadas` flagrada pelo usuario

Usuario notou que PTI e Traumatismo Cranioencefalico tinham exatamente 428 questoes cada -- "parece estranho". Investigacao confirmou: nao e coincidencia. `Pediatria:PTI`, `Pediatria:Traumatismo Cranioencefalico na crianca` e `Pediatria:Asma na infancia` (ids 219/222/233) tem `questoes_realizadas`, `questoes_acertadas` **e** `percentual_acertos` **byte-identicos** (428/358/83.6448...%), todos com `ultima_revisao='2026-08-23'`. Padrao sistemico, nao isolado: **128 de 269 temas (48%)** compartilham valor duplicado com >=2 outros temas de areas nao relacionadas (ex.: 105 questoes em 21 temas cruzando Pediatria/Endocrino/Obstetricia). Cruzamento com `AUDITORIA_MEDHUB.md` confirmou que isto e o achado **F37** ja registrado (s128, 2026-07-25, status ABERTO ate hoje): campo orfao, inflado ~3.7x, que "metas e performance" corretamente NAO leem (essas fontes usam `sessoes_bulk`). O valor novo desta sessao: prova de que o campo **continua sendo escrito** por algum processo em lote 3 dias atras (2026-08-23), nao e so residuo da migracao original -- evidencia nova anexada ao F37 existente (nao virou achado novo).

### Arco 5 -- Status de preparacao (pos-achado F37)

Como o usuario pediu mais informacao sobre preparo/performance/fila FSRS, os numeros foram puxados exclusivamente das fontes que o proprio F37 confirma como limpas: `python tools/day_plan.py --json` (via `.venv`, `sessoes_bulk`-based), `tools/variancia.py --json`, `tools/fsrs_queue.py --list`, `tools/fsrs_load.py --json`, `tools/review_radar.py`. Sintese entregue ao usuario: zona COBERTURA (54% da grade, desempenho alto 79% mas variancia alta 10.1pp -> simulado prescrito e em debito desde 17/08); ritmo real 49.5q/dia vs necessario pra fechar o atraso do cronograma 77.0q/dia (deficit projetado de 34 dias); fila FSRS com 64 cards visiveis (36 hoje + 12 atrasados + 10 novos + 6 erros_frescos), forecast de carga caindo rapido nas proximas 3 semanas; 29 temas dormentes (>=21d), cluster notavel em Cardio/Nefro/Endocrino parado ha 46-57 dias; padrao recorrente #1 do banco INTEIRO (nao so Pediatria/GO) e "incorporar atualizacao recente de diretriz (versao antiga na memoria)" -- 7 ocorrencias, 7 temas distintos.

## Padroes de erro identificados

- **Confirmado estruturalmente via grafo:** VOP (vacina descontinuada) como imã de erro em Imunizacoes -- reforca achado ja nomeado no radar de fraquezas persistentes.
- **Novo, cruzando especialidades:** "rotular cada alternativa V/F" / "marcar a falsa" (familia do bug de enunciado negativo) aparece em Pediatria E GO/Ginecologia/Obstetricia -- nao e fraqueza de tema, e execucao de leitura.
- **Achado de infraestrutura de dados, nao de conteudo clinico:** F37 (`questoes_realizadas` inflado/duplicado) tem instancia fresca de 3 dias atras -- o campo nao e so lixo historico, alguma escrita em lote ainda o alimenta incorretamente.

## Artefatos criados/modificados

- `.vibeflow/patterns/`: 3 arquivos deletados (`design-system-usage.md`, `streamlit-page-structure.md`, `fsrs-review-flow.md`); `domain-engine-api.md` e `db-access-layer.md` com conteudo corrigido; 6 patterns sobreviventes com frontmatter novo; `README.md` novo.
- `.vibeflow/index.md`: nota de "patterns obsoletos" atualizada pra registrar a delecao.
- `.claude/settings.local.json`: 2 entradas de permissao mortas removidas (`py_compile` em arquivos Streamlit inexistentes).
- `.gitignore`: `graphify-out/` adicionado (mesma politica de `artifacts/backups|llm_runs|audits/` -- saida de ferramenta regeneravel, nao versionada).
- `graphify-out/` (nao versionado): grafo `tools/+core/` (1344 nos) e grafo `pediatria-go/` (1258 nos, com overlay de `ipub.db`) -- `graph.json`, `graph.html`, `GRAPH_REPORT.md` cada.
- `AUDITORIA_MEDHUB.md`: evidencia nova anexada ao achado F37 existente (nao um achado novo -- reincidencia confirmada com prova concreta de 2026-08-23).
- `HANDOFF.md`: fechamento desta sessao.

## Decisoes tomadas

- `/graphify` em conteudo grande (>500 arquivos) exige escolha explicita de escopo com o usuario antes de rodar -- corpus code-only pula extracao semantica (so AST, gratis); corpus com `.md` precisa de subagents dedicados por chunk (~20-25 arquivos cada).
- Overlay de dados relacionais (`ipub.db`) sobre um grafo LLM-extraido deve ser **autorado deterministicamente** (schema do graphify, confidence=EXTRACTED/1.0), nunca passado por um subagent -- e dado estruturado, nao prosa; um LLM so reformataria com risco de erro.
- Merge de um fragmento dependente (nos que referenciam nos de outro grafo) tem que acontecer no **nivel de extracao** (antes do build), nao via `graphify merge-graphs` (que opera sobre grafos ja construidos e derruba arestas cujo alvo nao existe isoladamente em cada lado).
- `.vibeflow/patterns/` mortos (UI removida) foram **deletados**, nao movidos pra `historical/` -- a regra do usuario e binaria (fica ou morre, prova de zero referencia), nao existe estado intermediario de arquivamento.
- `graphify-out/` entra no `.gitignore` -- saida de ferramenta regeneravel (7.1MB), mesma politica ja aplicada a `artifacts/`.

## Proximos passos

1. **Auditoria ampla do banco (F37+F40+F41)** -- segue pendente desde s148, agora com **evidencia fresca de F37** (2026-08-23, nao so residuo antigo) somada ao escopo. Rastrear quem ainda escreve `taxonomia_cronograma.questoes_realizadas` em lote (`insert_questao.py`? `/importar-planilha`? migracao?).
2. **Usuario trara na proxima sessao: ou o simulado (em debito desde 17/08), ou as questoes dos 2 blocos (Pediatria 51q + Ginecologia 57q, ultimas tarefas do S16), alem de flashcards.** Nao decidir por ele -- oferecer as opcoes na abertura.
3. Itens ja pendentes da s154 continuam abertos: 3 flags de card sem confirmacao (1411/283/319), `card_id=120` pra `/pesquisar-evidencia`, Revisao Direcionada dedicada pra "remedio certo, sequencia errada" + "exame normal exclui".
4. 23 temas sem resumo dedicado identificados no grafo Pediatria/GO (PTI, TCE, Kawasaki, Bronquiolite, Meningite Tuberculosa, Anafilaxia, entre outros) -- candidatos a aula-base futura, nao urgente.
5. `graph.html` de ambos os grafos disponivel em `graphify-out/` (nao versionado, local) pra exploracao visual se o usuario quiser.
