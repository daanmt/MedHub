---
type: snapshot
layer: root
status: canonical
relates_to: AGENTE, roadmap
---

# ESTADO — MedHub (Preparação para Residência Médica)
*Atualizado: 2026-04-16 (sessão 068) | Ferramenta: Antigravity*

---

Workspace state-driven de estudos médicos. Processa questões de prova, registra padrões de erro no banco SQLite (`ipub.db`) e mantém resumos clínicos estruturados em `resumos/`.

### 🚩 Metas Estratégicas (Roadmap 2026)
- **Meta Final:** 23.000 questões até 12/2026 (Custo/Q: R$ 0,20).
- **Marco ENARE:** 17.000 questões até 10/2026 (Custo/Q: R$ 0,24).
- **Indicador Atual (Abril):** 3.064 / 17.000 (Meta ENARE) — Faltam ~13.936 q.
- **Performance Geral:** 80,0% (2.453 acertos / 3.064 questões — fonte: sessoes_bulk).

---

## INÍCIO OBRIGATÓRIO DE SESSÃO

**Leia `AGENTE.md` antes de qualquer ação.** Este arquivo contém o protocolo de boot e a ordem de leitura para garantir a continuidade do projeto.

> [!IMPORTANT]
> **SINGLE SOURCE OF TRUTH (SSOT):** O banco SQLite (`ipub.db`) é a fonte de verdade para erros, métricas e estado FSRS. O `caderno_erros.md` textual foi arquivado em `history/legacy/`. O conteúdo clínico lapidado mora exclusivamente em `resumos/`. Regra "Siamese Twins": **o erro vai pro DB, a lição vai pro resumo (resumos/)**.

- **200+ erros estruturados** no SQLite (`ipub.db`) — consulte o Dashboard para número exato.
- **44+ resumos clínicos** consolidados em `resumos/`.
- **67 sessões** de estudo catalogadas em `history/`.
- **Memory v1 & v3 ativos**: `app/memory/` configurado com `ANTHROPIC_API_KEY` permanente e consolidação LLM funcional.
- **`sessoes_bulk`** — nova tabela (sessão 067): fonte de verdade para totais de questões/acertos por área. Populada com dados reais de 3.020 questões (sessões 001–066).

---

## Mapa de artefatos

### Infraestrutura
| Artefato | Arquivo |
|---|---|
| Bootstrap protocol | `AGENTE.md` |
| Estado do projeto | `ESTADO.md` (este arquivo) |
| Estado operacional curto | `ESTADO.md` (seção "Últimas sessões") |
| Direção do produto | `roadmap.md` |
| Dashboard Streamlit | `streamlit_app.py` |
| Parser Stateful | `app/utils/parser.py` |
| Player Flashcards | `app/pages/2_estudo.py` |
| CLI de Revisão FSRS | `tools/review_cli.py` |
| Auditoria FSRS | `tools/audit_fsrs.py` |
| Auditoria Qualidade Cards | `tools/audit_flashcard_quality.py` |
| Auditoria Integridade DB | `tools/audit_integrity.py` |
| Auditoria Resumos | `tools/audit_resumos.py` |
| Pipeline LLM Qualitativo | `tools/regenerate_cards_llm.py` |
| Indexador RAG (ChromaDB) | `tools/index_resumos.py` |
| Init schema DB | `tools/init_db.py` |
| Limpeza DB | `tools/cleanup_db.py` |
| Sync flashcards | `tools/sync_flashcards.py` |
| **Registro bulk de sessão** | **`tools/registrar_sessao_bulk.py`** |
| Migração histórica bulk | `tools/migrar_sessoes_bulk.py` |
| Migração schema flashcards | `tools/migrate_flashcards.py` |
| Migração memória | `tools/migrate_memory.py` |
| Session logs | `history/session_NNN.md` |

### Dados
| Artefato | Arquivo |
|---|---|
| Banco principal (erros, FSRS, cronograma) | `ipub.db` (local only — não commitar) |
| Chaves de API e Segredos | `.env` (local only — ignorado no git) |
| Memória cross-session | `medhub_memory.db` (local only — não commitar) |
| Backups datados | `artifacts/backups/ipub_backup_*.db` (local only) |

### Artefatos de passe LLM (auditoria)
| Sessão | Input | Output | Escopo |
|---|---|---|---|
| 058 | `artifacts/llm_runs/058/all_needs_qual.json` | `artifacts/llm_runs/058/all_improved.json` | 169 cards nq=1 |
| 057b/058 | `artifacts/llm_runs/058/pilot_cards.json` | `artifacts/llm_runs/058/pilot_output.json` | 20 cards piloto nq=0 |

### Arquivos aposentados
| Artefato | Localização | Motivo |
|---|---|---|
| `flashcards_cache.json` | `artifacts/legacy/` | Pipeline v1 de flashcards pré-ipub.db; `fsrs_cache_cards`=0 rows; nenhuma página ativa usa `flashcard_builder.py` |
| `HANDOFF_056.md` | `artifacts/legacy/` | Handoff de sessão 056; absorvido por ESTADO.md |

### Conteúdo
| Artefato | Arquivo |
|---|---|
| Resumos clínicos | `resumos/{Área}/{Subespecialidade}/{Tema}.md` |
| Spec de formatação | `.claude/commands/estilo-resumo.md` |
| Protocolo de análise | `.claude/commands/analisar-questao.md` |

### Material de referência (PDFs — não editáveis)
| Artefato | Pasta |
|---|---|
| Textos extraídos | `%TEMP%` — deletados ao final de cada sessão (Zero PDF) |

---

## Dois eixos de qualidade de flashcards

> **Atenção:** esses dois eixos são ortogonais — não confundir. Um card pode falhar em um eixo sem falhar no outro.

| Eixo | Campo / Ferramenta | Valores | Significado |
|---|---|---|---|
| **Sinais objetivos** | `audit_flashcard_quality.py` | CRÍTICO / ALTO / ARQT. | Detecta artefatos no conteúdo renderizado: letra de gabarito `(A)`, prefixo `"Sobre X:"`, badge `RESPOSTA DIRETA`, regra mestre vazia |
| **Fila qualitativa** | `needs_qualitative` | 0 = aprovado | Heurística OK ou passe LLM aplicado |
| | | 1 = pendente LLM | Marcado para reescrita qualitativa |
| | | 2 = aposentado | Excluído da fila FSRS (`WHERE needs_qualitative < 2`) |

**Estado atual (pós-sessão 058):**
- Sinais objetivos: **0/277** cards com sinal crítico/alto
- needs_qualitative=1: **0** cards pendentes
- Distribuição: `heuristic/nq=0`=87, `qualitative/nq=0`=190 (total=277)

**Trilha de auditoria do passe qualitativo:**
- Artefatos em `artifacts/llm_runs/058/` (não commitados — deriváveis do ipub.db)
- Os 20 cards do piloto (057b) eram do grupo nq=0 (sinais objetivos), não do grupo nq=1
- Os 169 do rollout (058) eram nq=1; grupos sem sobreposição (overlap=0)

---

## Últimas sessões

**2026-04-16 | Gemini 3.1 Pro (sessão 068):** **Cirurgia Infantil e Refinamento de Dados**. Correção profunda visual (injetando `styles.py` globalmente na interface). Correção de 197 chaves (FKs) órfãs que causavam inexpressão dos flashcards antigamente criados em decorrência da deleção estrutural de taxonomia antiga. Inclusão da data de sessão local `data_sessao` provando consistência ao Foco Crítico. Aplicação da resolução da Cirurgia Infantil (44q registradas, com 1 deleção duplicada), obtendo 90% acerto e catalogando 4 itens. Reforço da idempontência do pipeline bulk.
**2026-04-16 | Antigravity (sessão 067):** **Correção de dados e arquitetura de rastreamento**. Diagnóstico do gap estrutural: `insert_questao.py` incrementava `questoes_realizadas` apenas por erros (não por acertos). Criada tabela `sessoes_bulk` como fonte de verdade para totais por área. Migração histórica de 3.020 questões (18 áreas) e 2.413 acertos (79,9%) via `migrar_sessoes_bulk.py` — fonte: `dashboard-emed.xlsx`. `taxonomia_cronograma` populada com 85 subtemas reais do Excel via `popular_subtemas.py` (ex: Neurologia > Demências q=156/a=137; Epilepsias q=148/a=115; AVC q=100/a=75). Discrepância de +40q entre Quadro Geral (2.980) e soma de subtemas (3.020) explicada: o QG exclui tarefas de "Revisão por Questões" cross-tema (Obstetrícia: QG=213 vs subtemas=253 — 40q de Ass. Parto não computadas no QG). Número real operacional: **3.020 questões**. Criação de `registrar_sessao_bulk.py` para uso em toda sessão futura. Dashboard reescrito: gráfico colorido por threshold, tabela por especialidade com erros, badges de tendência, gráfico temporal. `insert_questao.py` corrigido (separação volume/erros). `taxonomia_cronograma` deduplicada (14 linhas órfãs removidas).
**2026-04-10 | Antigravity (sessão 066):** **Análise de Questões — Síndromes Hipertensivas na Gestação**. Processamento de 6 questões erradas. Lacunas identificadas: (1) sequência de conduta na eclâmpsia ativa (via aérea antes do MgSO4 — convulsão autolimitada); (2) proteinúria como critério diagnóstico, não de gravidade (ACOG 2013+); (3) anatomia da 2ª onda trofoblástica (zona de junção miometrial); (4) DTG como causa de PE apenas antes de 20 semanas; (5) lógica OR nos critérios de gravidade (PA 140/90 + critérios órgão-alvo = grave); (6) conduta ambulatorial — sem restrição de sal, anti-hipertensivo só se PA ≥ 140/90. 6 inserções no SQLite (IDs 349–359) e resumo `Síndromes Hipertensivas na Gestação.md` completamente reescrito ao Gold Standard (sessão 065 havia gerado texto ilegível). Correção de 2 bugs no `tools/insert_questao.py` (colunas `frente`/`verso` removidas do INSERT; tabela `cronograma_progresso` ausente tratada com try/except).
**2026-04-09 | Antigravity (sessão 065):** **Síndromes Hipertensivas na Gestação**. Criação do resumo clínico referencial integrando os PDFs base (Medcel/Estratégia) e extração focada de Flashcards via extrator py. Cumprimento do Gold Standard 80/20, englobando manejo agudo ZUSPAN/PRITCHARD e limiares exatos de interrupção cronológica da gravidez. Implementação da "Armadilha de prova" retroativa baseada nos flashcards de alta prioridade. Limpeza completa dos artefatos originais e arquivos temporários de conversão.
**2026-04-07 | Antigravity (sessão 064):** **Otimização Avançada do RAG e Benchmarking**. Implementação de arquitetura multi-query (Híbrida: Raw + HyDE), propagação de contexto global (injeção de título em chunks), paralelismo de busca (ThreadPoolExecutor) e inclusão estrutural do reranker BM25 (atualmente desabilitado por regressão, tech debt para /discover). Auditoria de métricas: **Recall@5 atingiu 90%** (baseline corrigido p/ corpus real) e latência média estabilizada em ~5.2s. Implementação do carregamento seguro de API via `.env`/`python-dotenv`.
**2026-04-05 | Antigravity (sessão 063):** **Diagnóstico e documentação da arquitetura RAG**. Identificação e auditoria dos dois sistemas ChromaDB coexistentes: `app/engine/rag.py` (RAG canônico, `data/chroma/`, 688 chunks, `resumos/` clínicos) e `obsidian-notes-rag` MCP (auxiliar, vault completo, 862 chunks). Confirmação que não há conflito — paths físicos distintos, clients independentes. Bug documentado: servidor MCP sobe sem `--provider ollama` em sessões Antigravity. Sessão de revisão FSRS executada (5 atrasados Pediatria/TSV + 10 novos). Decisão arquitetural registrada em `.vibeflow/decisions.md`.
**2026-04-05 | Antigravity (sessão 062):** **Análise de Sepse Neonatal**. Processamento de 3 questões erradas sobre Iceícia e Sepse Neonatal. Lacunas identificadas: (1) perfil discriminador da *Listeria monocytogenes* (tríade LA marrom + exantema neonatal + monocitose); (2) exceção SBP para taquipneia isolada nas primeiras 6h (watchful waiting); (3) desatenção na classificação da ampicilina como penicilina. 3 insercões no SQLite (IDs 345–347) e resumo `Iceícia e Sepse Neonatal.md` atualizado com 2 novos blocos clínicos e 2 armadilhas cumulativas.
**2026-04-01 | Antigravity (sessão 061):** **Análise Massiva de Trauma e ATLS**. Processamento de 14 questões objetivas/discursivas erradas, rastreando vulnerabilidades nas escolhas minimamente invasivas ilusórias VS obviedades clínicas de peritonites e eviscerações desfiguradas. Foram performadas 14 injeções bem-sucedidas no SQLite `ipub.db` e aplicadas 14 modificações cumulativas via Regra do Escudo na documentação referencial `resumos/Cirurgia/[CIR] Trauma.md`, fortalecendo significativamente suas "Armadilhas de Prova".
**2026-03-29 | Antigravity (sessão 060):** **Análise de Gastroenterologia: DRGE e Pancreatite**. Cruzamento transversal de 8 erros práticos vindos de bloco de 44q. Foram documentados massivamente no `ipub.db` falhas ligadas a "Ansiedade de Intervenção": Indicação ansiosa de cirurgia precoce em necrose pancreática estéril crônica, CPRE desnecessária para icterícia transiente, superestimar o poder oncológico da Fundoplicatura no Barrett, e dieta pós-op de Nissen e Toupet. Enriquecimento duplo da seção "Armadilhas de Prova" dos respectivos resumos de DRGE e Pancreatite.
**2026-03-29 | Antigravity (sessão 059):** **Análise de Questões: Demências e EM**. Análise profunda de 4 erros e integração das lacunas: CADASIL, doênça de pequenos vasos (Binswanger), pegadinha clássica do falso-negativo no MEEM em pacientes de alta escolaridade (o diagnóstico reside nas AVDs prejudicadas) e conduta terapêutica cognitiva da EM. Inseridas as lacunas no db SQLite com sucesso e resumo `Demências.md` atualizado pela via da regra mútua do escudo.
**2026-03-28 | Claude Code (sessão 058 — faxina):** **Faxina controlada de artefatos + documentação**. Criada estrutura `artifacts/` (llm_runs/058/, backups/, legacy/). Movidos: 4 JSONs de passe LLM para llm_runs/058/ (auditoria), 3 backups para artifacts/backups/, flashcards_cache.json + HANDOFF_056.md para artifacts/legacy/. `.gitignore` atualizado (artifacts/backups/, artifacts/llm_runs/, .mcp.json). README.md reescrito (estrutura, dois eixos, política de artefatos). ESTADO.md: seção "Dois eixos de qualidade" adicionada, tabela de dados atualizada, relacionamento com HANDOFF.md removido.
**2026-03-28 | Claude Code (sessão 058):** **Passe qualitativo LLM + correção de taxonomia (Blocos 1-3)**. Rollout LLM completo em 189 cards (piloto 20 + rollout 169): qualidade 0/277 sinais críticos/altos (antes: 31/277), needs_qualitative=1→0. `Tools/fix_taxonomy_bridge.py` criado e executado: 21 tema_ids órfãos mapeados (INSERT OR IGNORE com IDs explícitos) — `audit_integrity` agora [OK] taxonomia. Filtro `needs_qualitative < 2` adicionado em `review_cli.py` e `2_estudo.py`. Suporte a aposentadoria (nq=2) em `regenerate_cards.py --apply`. Flag `--only-needs-qual` em `audit_flashcard_quality.py`. FSRS preservado (5 reviews, 5 stability>0). Distribuição final: 190 qualitative + 87 heuristic. **Auditoria de consistência numérica (pós-sessão):** os 20 do piloto eram todos `nq=0` (heuristic) no backup pré-aplicação — grupos piloto e rollout sem sobreposição (overlap=0). 20 piloto + 169 rollout + 1 correção manual = 190 qualitativos. 87 heurísticos são os que já passavam na heurística sem necessidade de LLM. Total: 277/277 contabilizados (`SELECT quality_source, needs_qualitative, COUNT(*) FROM flashcards GROUP BY 1,2` → heuristic/0=87, qualitative/0=190).
**2026-03-27 | Claude Code (sessão 057b):** **Refatoração de qualidade de flashcards (Fases 1-4)**. Auditoria permanente (`audit_flashcard_quality.py`): baseline era 277/277 ruins (100%). Fix no pipeline heurístico (`strip_letter_ref`, template armadilha). Regeneração completa de 277 cards: 239 heuristic OK + 38 heuristic_flagged. Resultado: 31/277 problemáticos (11.2%), 0 campos estruturados NULL. 169 cards marcados `needs_qualitative=1` para passe LLM. FSRS preservado (5 reviews, 5 stability>0). Pipeline LLM (`regenerate_cards_llm.py`) criado. Integridade auditada (`audit_integrity.py`). fix em `insert_questao.py` (fallback "Sobre X:" eliminado).
**2026-03-27 | Claude Code (sessão 057):** **FSRS operacional — CLI de revisão + fix Streamlit**. Substituição do `_avancar()` hardcoded em `2_estudo.py` por `record_review()` real. Criação de `Tools/review_cli.py` (3 buckets: atrasados/hoje/novos, args --limit/--new-limit/--area/--tema). Criação de `Tools/audit_fsrs.py` (auditoria operacional). ROADMAP.md reescrito com 4 trilhos (A Core Revisão, B Interfaces, C Fontes Cards, D Analytics).
**2026-03-27 | Claude Code (sessão 056):** **Pipeline flashcards v5 — migração + regeneração heurística**. Schema `flashcards` migrado com 8 novos campos. 277 cards regenerados (219 heuristic OK, 20 qualitative, 38 flagged). Ferramentas: `Tools/backup_db.py`, `Tools/migrate_flashcards.py`, `Tools/regenerate_cards.py`, `Tools/audit_cards.py`. `insert_questao.py` atualizado com 5 args estruturados.
**2026-03-27 | Claude Code (sessão 055):** **Automação do sistema de memória via hooks**. Auditoria completa das 4 camadas de memória. Correção do `manager.py` (2 managers separados, pt-BR, session_id injetado, `_sync_error_counts`). Migração de 37 WeakAreas para namespace correto. Fix do MCP obsidian-notes-rag em agente-daktus-content (env vars). Hooks automáticos: `memory_boot.py` (SessionStart) + `memory_session_log.py` (PostToolUse Write). AGENTE.md e registrar-sessao.md atualizados.
**2026-03-25 | Antigravity (sessão 051):** **Cirurgia Infantil**. Conclusão do resumo clínico, abrangendo de HDC a defeitos de parede abdominal. 80/20 benchmark e Zero PDF integral.
**2026-03-25 | Antigravity (sessão 050):** **Início de Cirurgia Infantil**. Extração de PDFs e mapeamento clínico.
**2026-03-25 | Antigravity (sessão 049):** **Icterícia e Sepse Neonatal (Pediatria)**. Criação do resumo clínico a partir de PDFs originais. Aplicação integral do Gold Standard 80/20 e workflow Zero PDF.
**2026-03-25 | Antigravity (sessão 048):** **Trauma Abdominal e Pélvico (Cirurgia)**.
**2026-03-25 | Antigravity (sessão 047):** **Leitura de produto completa.** Diagnóstico, visão de produto e roadmap evolutivo (7 linhas) elaborados a partir do estado real do repositório. Aplicação documental: `roadmap.md` reescrito (de backlog para direção de produto), `README.md` com parágrafo de visão, `ESTADO.md` alinhado ao novo roadmap.
**2026-03-25 | Claude Code (sessão 046):** **Memory v1 (LangGraph + LangMem + SQLiteMemoryStore)**. Implementação completa da camada de memória cross-session: `app/memory/` (store, checkpointer, schemas, tools, manager, inspect), `Tools/test_memory.py` (4/4 smoke tests), `MEMORY_ARCHITECTURE.md`. Atualização de AGENTE.md (boot step 5), `registrar-sessao.md` (passo 5 consolidação), `KNOWLEDGE_ARCHITECTURE.md` (seção 9), `requirements.txt`.
**2026-03-24 | Antigravity (sessão 045):** **Sífilis na Gestação e Congênita**. Análise de questão sobre RN de mãe mal tratada com VDRL reagente. Refinamento de fluxograma NTT e inclusão de armadilhas de reinfecção/parceiro. Registro no SQLite (ipub.db).
**2026-03-24 | Antigravity (sessão 044):** **Ginecologia (Úlceras Genitais)**. Criação do resumo clínico `Úlceras Genitais.md` e análise de 3 questões críticas (Herpes gestacional, Fluxograma > 4 sem). 3 erros registrados no SQLite. Limpeza "Zero PDF" executada.
**2026-03-23 | Antigravity (sessão 043):** **Auditoria arquitetural completa (inside job)**. Diagnóstico e correção de todos os documentos centrais. Alinhamento de ESTADO.md, README.md, HANDOFF.md, roadmap.md, workflows. Adição de wikilinks e frontmatter para Obsidian. Limpeza de referências obsoletas.
**2026-03-23 | Antigravity (sessão 042):** **Vigilância em Saúde**. Criação do resumo clínico `Vigilância em Saúde.md` a partir de PDFs originais. Foco em PNVS 2018, Saúde Única e competências ANVISA. Limpeza "Zero PDF" executada.
**2026-03-23 | Antigravity (sessão 041):** **Análise de Erros (Pediatria)**. Análise de 46 questões (42/46). Refinamento do resumo de Emergências Pediátricas (IOT, Pneumotórax, Adrenalina precoce). 4 erros registrados no SQLite (IDs 211-217).
**2026-03-23 | Antigravity (sessão 040):** **Análise de Erros (Dermatologia)**. Análise de 24 questões (16/24). Refinamento do resumo de Hanseníase e PLECT com regras de estesiometria, cultura em Sabouraud, Pentamidina e RX de tórax. Aplicação da Regra de Acúmulo de Armadilhas.
**2026-03-22 | Antigravity (sessão 039):** **Refinamento de Otorrinolaringologia**. Análise de 19 questões (13/19). Inclusão de cisto dermoide (USG hiperecogênico), hemangioma subglótico (Propranolol), fixação de traqueostomia e prognóstico HPV em orofaringe.
**2026-03-22 | Antigravity (sessão 038):** **Dermatologia (Hanseníase e PLECT)**. Criação do resumo clínico `Hanseníase e Síndromes Verrucosas.md`. Extração profunda de 2 apostilas, seguindo o padrão PLECT e 80/20. Limpeza total de PDFs executada.
**2026-03-22 | Antigravity (sessão 037):** **Otorrinolaringologia Cirúrgica**. Criação do resumo `Neoplasias, Congênitas e Traqueostomia.md` abrangendo do cisto tireoglosso ao esvaziamento cervical. Seguida rigorosamente a estética Gold Standard.
**2026-03-22 | Antigravity (sessão 036):** **Consolidação de Arboviroses**. Criação de `Arboviroses.md` (Dengue, Chikungunya, Zika) focando no diagnóstico diferencial e armadilhas clássicas. Remoção automatizada dos PDFs-base (Zero PDF).
**2026-03-21 | Antigravity (sessão 035):** **Reestruturação de Sífilis na Gestação**. Adição de seção de LCR, diagnóstico diferencial STORCH e ajustes em fluxogramas.
**2026-03-20 | Antigravity (sessão 034):** **Refinamento de DM e Auditoria**. Análise de 2 questões de Diabetes (CAD e Manejo). Audit completo do resumo `Diabetes Mellitus - Complicações Agudas.md`. Marca histórica de **100 erros** atingida no caderno e sincronizada no SQLite.
**2026-03-20 | Antigravity (sessão 033):** **Consolidação de Diabetes Agudo**. Criação do resumo clínico `Diabetes Mellitus - Complicações Agudas.md`. Cobertura completa de CAD (adulto/pediatria), EHH e Hipoglicemia.
**2026-03-18 | Antigravity (sessão 032):** **Refinamento Avançado de Colo e Governança**. Revisão profunda do resumo `[GIN] Rastreamento Colo.md` com diretrizes 2025 e análise de 9 erros.
**2026-03-16 | Antigravity (sessão 031):** **Expansão em Psiquiatria e Nefrologia**. Criação dos resumos de `Dependência Química.md`, `Intoxicações Exógenas.md` e `Lesão Renal Aguda.md`.
**2026-03-15 | Antigravity (sessão 030):** **Consolidação de Pancreatites**. Criação do resumo de `Pancreatite Aguda e Crônica.md`. Foco em critérios de Atlanta 2012.
**2026-03-15 | Antigravity (sessão 029):** **UI Refresh**. Implementado sistema de design Flat com `app/utils/styles.py`. Arquitetura híbrida de botões FSRS implementada.
**2026-03-14 | Antigravity (sessões 018–028):** Ver `history/session_NNN.md` para detalhes individuais.

---

## Próximos passos

Ver [[roadmap]] — Linhas Evolutivas.

Prioridade imediata:
1. **Pipeline RAG inverso:** `app/engine/rag.py` já tem 688 chunks indexados. Integrar `get_topic_context()` para retornar `relevant_chunks` e usar em `generate_contextual_cards()` — conforme spec `medhub-rag-layer.md`.
2. **Busca semântica na Biblioteca:** Adicionar `st.text_input` em `3_biblioteca.py` tab1 chamando `rag.search()` — já especificado no PRD.
3. **Meta Volumétrica:** Processar questões erradas continuamente (meta ENARE 17k até out/2026).
4. **Expansão de Conteúdo:** Avançar em `resumos/` (GO: DIP e Sangramentos).

---

## Decisões críticas (não reverter)

- **RAG canônico = `app/engine/rag.py`**: ChromaDB local em `data/chroma/` (688 chunks), corpus = `resumos/**/*.md`, embedding via Ollama `nomic-embed-text`. **Arquitetura V2 (Sessão 064):** Multi-query (Raw + HyDE), ThreadPoolExecutor p/ paralelismo de busca, Context Propagation (título injetado no chunk), BM25 desabilitado no sort final por regressão (tech debt p/ /discover).
- **RAG Latência Target: ~5s**: Paralelismo de busca obrigatório para não somar tempos de rede LLM e rede local.
- **Study Engine = `app/engine/`**: Interface estável para agentes externos. Funções: `get_review_queue()`, `get_topic_context()`, `summarize_performance()`, `analyze_error()`, `generate_contextual_cards()`. Agentes NÃO fazem queries SQL diretas — usam o engine.
- **Memory v1**: `app/memory/` (LangGraph + LangMem + SQLiteMemoryStore). Backend: `medhub_memory.db`. Não acoplado ao `ipub.db`. Smoke tests em `tools/test_memory.py`.
- **Governança via AGENTE.md**: O boot e o fechamento seguem estritamente o `AGENTE.md`.
- **SSOT = ipub.db / sessoes_bulk**: O total de questões/ acertos por área é authoritative em `sessoes_bulk`. O diagnóstico do erro é gravado via CLI (`tools/insert_questao.py`) no banco. O `caderno_erros.md` textual foi arquivado em `history/legacy/`.
- **Protocolo de Registro de Sessão**: Ao informar "fiz X questões, acertei Y", o agente DEVE chamar `tools/registrar_sessao_bulk.py --sessao NNN --area AREA --feitas X --acertos Y` ANTES de processar os erros. Essa é a única forma de manter os contadores de performance precisos.
- **Siamese Twins V2.0**: Erro → DB. Lição/Armadilha → Resumo em `resumos/`.
- **Resumos seguem** `.claude/commands/estilo-resumo.md` — bullets hierárquicos, ⭐/⚠️/🔴; sem tabelas, sem fluxogramas ASCII.
- **Sessions numeradas globalmente** em `history/` — qualquer agente registra.
- **Zero PDF**: `extract_pdfs.py` extrai para `%TEMP%` e apaga o PDF original após consolidação.
- **Regra de Acúmulo**: Seção "Armadilhas de Prova" é cumulativa — nunca remover armadilhas antigas.

---

## Para retomar: leia nesta ordem

1. **`ESTADO.md`** (este arquivo) — visão geral do projeto + onde a última sessão parou (seção "Últimas sessões").
2. **`AGENTE.md`** — protocolo de boot e fechamento (regras que governam a sessão).

> `HANDOFF.md` foi aposentado na sessão 058 — `ESTADO.md` é o documento único de estado/handoff.

---

## Contexto do repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao final de cada sessão: atualizar este arquivo e registrar em `history/`.*
