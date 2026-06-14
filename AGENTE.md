---
type: bootstrap-protocol
layer: root
status: canonical
relates_to: [ESTADO, roadmap]
---

# AGENTE.md — Protocolo, Convenções e Arquitetura

Documento único de governança do MedHub. Toda sessão começa aqui.

---

## 1. Princípio Central

**Este projeto é uma jornada contínua.** Nunca comece do zero. Sua missão é herdar o estado da sessão anterior, executar a tarefa atual e preparar o terreno para a próxima.

---

## 2. Boot Sequence (obrigatório ao iniciar)

1. **`HANDOFF.md`** — camada operacional curta: próximo passo imediato + estado por frente. **Ler PRIMEIRO** (estrutura em `core/contracts/handoff-contract.md`).
2. **`ESTADO.md`** — snapshot macro: metas, indicador, marcos (`core/contracts/estado-contract.md`).
3. **Check de reconcile** — rodar o protocolo de `core/contracts/reconcile-contract.md` (planilha↔db↔ESTADO↔FSRS). BLOCKING → resolver antes de trabalho novo.
4. **Workflow da tarefa** — `.agents/workflows/{analisar-questoes,criar-resumo,registrar-sessao,gerar-reforco}.md`.
5. **Último log** — `history/session_NNN.md` mais recente (índice em `history/INDEX.md`).
6. **Memória longa** — carregada via hook `SessionStart`. Se não aparecer: `python -m app.memory.inspect --context`.
7. **RAG semântico durante a sessão** — `mcp__obsidian-notes-rag__search_notes` para localizar conteúdo em `resumos/` sem ler arquivos inteiros.

---

## 3. Protocolo de Fechamento

1. **Atualizar `HANDOFF.md`** — **sempre** (toda sessão significativa). Rotacionar "Última sessão" (substituir, não acumular) + atualizar "Estado por frente" + "Próximo passo imediato". Regras em `core/contracts/handoff-contract.md`.
2. **Atualizar `ESTADO.md`** — **só se o macro mudou** (indicador cruzou marco, nova frente, skill/contrato versionado). Não é diário de sessões. Regras em `core/contracts/estado-contract.md`.
3. **Registrar sessão** — novo `history/session_NNN.md` seguindo `.agents/workflows/registrar-sessao.md` + entry em `history/INDEX.md`.
4. **Git** — `git add` arquivos modificados (nunca `git add .`), commit semântico, push. `ipub.db` e `medhub_memory.db` não vão pro git.

---

## 4. Mentalidade Gold Standard

Toda interação reflete o nível de excelência dos resumos padrão-ouro (`Trauma.md`, `Insuficiência Cardíaca.md`):

1. **Benchmark 80/20** — 80% assertividade objetiva (condutas, scores) + 20% didática clínica densa.
2. **Linguagem acadêmica** — sem coloquialismos, jargões de plantão ou termos dramáticos.
3. **Alta especificidade** — critérios objetivos, quantitativos, definições; nada genérico.
4. **Acúmulo de conhecimento** — armadilhas são **cumulativas**; novos insights se somam aos antigos, nunca substituem.

---

## 5. Convenções

### 5.1 Tipos de nota

| `type` | Onde fica | Exemplo |
|---|---|---|
| `knowledge` | `resumos/` | `Insuficiência Cardíaca.md` |
| `bootstrap-protocol` | raiz | `AGENTE.md` |
| `snapshot` | raiz | `ESTADO.md` |
| `roadmap` | raiz | `ROADMAP.md` |
| `onboarding` | raiz | `README.md`, `CLAUDE.md` (stub) |
| `skill` | `.claude/commands/` | `estilo-resumo.md`, `analisar-questao.md` |
| `workflow` | `.agents/workflows/` | `analisar-questoes.md` |
| `hub` | qualquer nível | `resumos/INDEX.md` |
| `session` | `history/` | `session_071.md` |

### 5.2 Frontmatter mínimo

Notas de conhecimento clínico (`resumos/`):

```yaml
---
type: knowledge
area: [Clínica Médica | GO | Cirurgia | Pediatria | Preventiva]
especialidade: Cardiologia        # omitir se área == especialidade
status: [active | stub]
aliases: [IC]                     # apenas siglas consolidadas; omitir se não existir
---
```

Documentos raiz canônicos:

```yaml
---
type: [bootstrap-protocol | snapshot | roadmap | onboarding]
layer: root
status: canonical
relates_to: [ESTADO, AGENTE]      # máximo 3 referências
---
```

**Regra:** não adicionar campos decorativos. Se o campo não orienta busca ou filtragem, não existe.

### 5.3 Naming

- `resumos/{Área}/{Especialidade}/{Tema}.md`. Sentence case. Prefixos legados (`[GIN]`, `[OBS]`, `[CIR]`, `[ORL]`) não são propagados.
- `history/session_NNN.md` (três dígitos, zero-padded, numeração global sequencial). Não criar sessões retroativas.
- Raiz: docs canônicos em maiúsculas (`AGENTE.md`, `CLAUDE.md`, `ESTADO.md`, `README.md`, `ROADMAP.md`, `LICENSE`).

### 5.4 Wikilinks e aliases

- Wikilinks são intencionais. Use quando criam navegação real, não decoração.
- Aliases apenas para siglas clínicas consolidadas (≤3 por nota): `IC`, `DRC`, `LRA`, `TB`, `DM2`, `TCE`, `DUP`, `DITC`, `SUA`, `PLECT`.
- Notas de conhecimento não linkam de volta para docs raiz (evita ruído no grafo).

### 5.5 SSOTs (Single Sources of Truth)

| Domínio | SSOT | Commitar? |
|---|---|---|
| Erros, FSRS, cronograma | `ipub.db` | Não (local-only) |
| Conhecimento clínico | `resumos/**/*.md` | Sim |
| Estado do projeto | `ESTADO.md` | Sim |
| Workflows | `.agents/workflows/` | Sim |
| Memória longa do agente | `medhub_memory.db` | Não (local-only) |
| Chaves de API | `.env` | Não (gitignored) |

---

## 6. Decisões críticas (não reverter)

- **RAG canônico** = `app/engine/rag.py` (ChromaDB em `data/chroma/`, embeddings via Ollama `nomic-embed-text`, multi-query Raw + HyDE, ThreadPoolExecutor, context propagation no chunk, BM25 desabilitado por regressão). Baseline reproducible em `tools/eval/REPORT.md`.
- **Engine API** = `app/engine/` expõe 2 funções estáveis para Streamlit (e agentes externos): `get_topic_context()` e `summarize_performance()`. Agentes **não** fazem queries SQL diretas — vão pelo engine ou pelos CLIs em `tools/`.
- **Memory v1** = `app/memory/` (LangGraph SqliteSaver + LangMem). Backend `medhub_memory.db`, isolado do `ipub.db`. Smoke tests em `tools/test_memory.py`.
- **Siamese Twins** — Erro → DB (via `tools/insert_questao.py`). Lição/Armadilha → resumo correspondente em `resumos/`.
- **SSOT volumétrica** = `sessoes_bulk` no `ipub.db`. Ao informar "fiz X questões, acertei Y", o agente DEVE chamar `python tools/registrar_sessao_bulk.py --sessao NNN --area AREA --feitas X --acertos Y` ANTES de processar erros individuais.
- **Resumos seguem** `.claude/commands/estilo-resumo.md`. Bullets hierárquicos, marcadores ⭐/⚠️/🔴. Sem tabelas, sem fluxogramas ASCII.
- **Sessions numeradas globalmente** em `history/` — qualquer agente registra (sem fork por ferramenta).
- **Zero PDF** — `tools/extract_pdfs.py` extrai para `%TEMP%` e apaga o PDF original após consolidação no resumo.
- **Regra de Acúmulo** — armadilhas de prova são cumulativas; jamais sobrescrever, apenas somar.
- **Camada de estado contract-driven (sessão 075)** — estado vive em duas camadas: `HANDOFF.md` (operacional curto, ≤60 linhas, lido primeiro) + `ESTADO.md` (macro). Normatizado por `core/contracts/{handoff,estado,reconcile,fsrs-management}-contract.md`. Padrão adaptado do agente irmão `agente-daktus-content`. Boot roda check de reconcile; fechamento atualiza HANDOFF sempre.
- **FSRS bankruptcy (sessão 075)** — os 70 cards heurísticos legados foram aposentados (`needs_qualitative=2`), não regenerados. Go-forward: cards nascem qualitativos via `insert_questao.py`. Política em `core/contracts/fsrs-management-contract.md`.
- **Governança de evidência (sessão 076)** — afirmação clínica decisória (conduta/dose/cutoff/critério) é auditada contra a melhor evidência: hierarquia **sociedades BR + MS > RCT/meta + guidelines INT > consenso**, com **lente da banca** (o que ENAMED/ENARE espera). Conflito banca × evidência atual → ensina a resposta da banca **e** registra 🔴 armadilha "banca-dependente" (nunca silenciar). Substrato: `pubmedmcp` (verbatim por PMID/DOI) + WebSearch (sociedades BR em PDF) + obsidian-rag (local). Normatizado por `core/contracts/evidence-governance.md`; operado por `/pesquisar-evidencia` + subagente `evidence-researcher`. Adaptado do mecanismo de auditoria do `agente-daktus-content`. Escopo v1.0: go-forward + sob demanda (sem varredura retroativa).
- **Cards de altura graduada / andaime de pré-requisito (sessão 082)** — a altura de um flashcard é um **gradiente** (`base → mecanismo → nuance → topo`), carregado no campo `tipo`. Cards de andaime (altura < topo) reconstroem os elos **a montante** quando um **CLUSTER** de cards-alvo trava por falta de grounding (card isolado caindo = recall, não falta de base). Nascem **sem erro de origem** (`questao_id=NULL`), ancorados no resumo, via `tools/insert_card_base.py`. **Propagação local:** tapar o buraco costurando o degrau imediatamente adjacente; o nº de degraus é inferido da iteração com o estudante. O degrau `mecanismo` (porquê causal encadeado) é o de maior rendimento — o gap costuma ser **causalidade, não fato**. Calibração de compressão na revisão: a dose de fundação entregue **antes** do bloco escala com o quão frio está o tema (stability + acerto do cluster) — ver `/revisar` Camada 0. Régua de autoria em `.claude/commands/estilo-flashcard.md`. **Schema formal pendente (Tier 3):** altura ordinal + grafo `prereq_de` + ordenação automática da fila base→topo. Adaptado dos princípios de `ai-eng` (grounding, subcategory targeting, velocidade > perfeição).

---

## 7. Workflows & Skills

### 7.1 Workflows (`.agents/workflows/`)

| Tarefa | Workflow |
|---|---|
| Criar resumo de tema | `.agents/workflows/criar-resumo.md` |
| Analisar questões erradas | `.agents/workflows/analisar-questoes.md` |
| Registrar sessão no history | `.agents/workflows/registrar-sessao.md` |
| Gerar flashcards de reforço | `.agents/workflows/gerar-reforco.md` |

### 7.2 Contrato — Skills × Workflows × CLIs

As duas superfícies coexistem sob três regras invioláveis:

- **Skills (`.claude/commands/*.md`) são referência atômica.** Especificam protocolo, assinatura de CLI, padrão de estilo, template de resposta. Não contêm sequência de passos numerados nem orquestração.
- **Workflows (`.agents/workflows/*.md`) são orquestração imperativa.** Numeram passos, invocam skills por nome/path (`.claude/commands/<skill>.md`), mas nunca reespecificam o conteúdo das skills. Quando um workflow precisa de detalhe de CLI, regra de estilo ou protocolo de análise, ele referencia a skill e termina ali.
- **Cada CLI em `tools/` tem assinatura canônica em UMA skill.** A assinatura completa (todos os flags, semântica de cada argumento) vive em exatamente um `.claude/commands/*.md`. Workflows referenciam por nome de skill + seção; jamais copiam a invocação.

Qualquer duplicação semântica entre workflow e skill é defeito por contrato. Edições futuras a uma skill não exigem edição-espelho em workflows porque workflows não carregam o conteúdo da skill.

### 7.3 Skills / Slash commands (`.claude/commands/`)

| Skill | Função |
|---|---|
| `/estilo-resumo` | Padrão de formatação **obrigatório** para resumos |
| `/analisar-questao` | Protocolo de análise + invocação do `insert_questao.py` |
| `/extrair-pdf` | Wrapper para `extract_pdfs.py` (política Zero PDF) |
| `/auditar-resumos` | Linter de qualidade para `resumos/` |
| `/performance` | Checagem rápida (questões, metas, custo/Q, áreas fracas) — read-only |
| `/pesquisar-evidencia` | Busca + auditoria de evidência de afirmação clínica decisória (hierarquia BR>INT>consenso + lente da banca); veredito + fonte. Governado por `core/contracts/evidence-governance.md` |

### 7.4 CLIs ativos (`tools/`)

| Script | Função |
|---|---|
| `tools/insert_questao.py` | Insere erro estruturado no `ipub.db` (questoes_erros + flashcards + fsrs_cards + taxonomia) |
| `tools/insert_card_base.py` | Insere cards de **andaime** (altura graduada: base/mecanismo/nuance) sem erro de origem — pré-requisitos que destravam cards-alvo de tema frio |
| `tools/registrar_sessao_bulk.py` | Registra totais por área em `sessoes_bulk` |
| `tools/extract_pdfs.py` | PDF → .txt (com delete-after-extract) |
| `tools/init_db.py` | Cria schema canônico (idempotente) |
| `tools/index_resumos.py` | Indexa `resumos/**/*.md` no ChromaDB |
| `tools/performance.py` | Relatório de performance em markdown |
| `tools/audit_resumos.py` | Linter de qualidade de resumos |
| `tools/audit_flashcard_quality.py` | Auditoria de qualidade de cards |
| `tools/audit_integrity.py` | Auditoria de integridade do DB |
| `tools/audit_fsrs.py` | Estado do FSRS |
| `tools/cards_regen_queue.py` | Fila (read-only) de cards a regenerar pelo agente — substitui a geração heurística aposentada |
| `tools/review_cli.py` | Player FSRS em CLI |
| `tools/backup_db.py` | Backup datado do `ipub.db` para `artifacts/backups/` |
| `tools/eval/run_eval.py` | Eval de retrieval (Recall@k + MRR@10) |

Migrações one-shot já aplicadas vivem em `tools/_archive/migrations/` — não re-rodar.

---

## 8. Modelo de Memória (3 camadas)

```
┌──────────────────────────────────────────────────────────────┐
│ CAMADA 1 — Canônica (repositório git)                        │
│  AGENTE.md · ESTADO.md · resumos/ · ipub.db                  │
│  Conteúdo clínico e estado do projeto. Fonte de verdade.     │
└──────────────────────────────────────────────────────────────┘
        ↑ lida no boot · atualizada ao fechar sessão
┌──────────────────────────────────────────────────────────────┐
│ CAMADA 2 — Short-term (LangGraph checkpointer)               │
│  SqliteSaver → medhub_memory.db::checkpoints                 │
│  thread_id = "session_{NNN:03d}"  ·  within-session state    │
└──────────────────────────────────────────────────────────────┘
        ↑ restaurada automaticamente por thread_id
┌──────────────────────────────────────────────────────────────┐
│ CAMADA 3 — Long-term (LangMem + SQLiteMemoryStore)           │
│  SQLiteMemoryStore → medhub_memory.db::memory_store          │
│  Namespaces: profile · weak_areas · workflow_rules ·         │
│              session_insights · study_preferences            │
└──────────────────────────────────────────────────────────────┘
```

**Governança:**
- Camada 3 captura preferências, padrões de fraqueza e insights — **não** replica `resumos/`, `ipub.db` ou `ESTADO.md`.
- `consolidate_session(NNN)` é chamada pelo hook `PostToolUse(Write)` quando um novo `history/session_NNN.md` é escrito. Usa `claude-haiku-4-5` se `ANTHROPIC_API_KEY` estiver presente; senão, fallback heurístico (lista áreas trabalhadas).
- `workflow_rules` é comparada com este `AGENTE.md` antes de persistir — não duplicar o que já está canonicamente documentado.

**Inspeção:** `python -m app.memory.inspect --{context,namespace medhub/weak_areas,threads,dump,stats}`.
**Detalhes técnicos:** docstring de `app/memory/__init__.py` + `app/memory/schemas.py`.

---

## 9. O que ignorar

- `medhub-ui-refresh-main/` — projeto React legado (já fora do tree atual; resíduo só em git history).
- `history/legacy/` — sessões 001-028 referenciam artefatos retirados (`HANDOFF.md`, `caderno_erros.md`, `progresso.md`).
- `.venv/`, `__pycache__/`, `data/chroma/`, `artifacts/backups/`, `artifacts/llm_runs/` — artefatos locais ou gitignored.
