---
type: bootstrap-protocol
layer: root
status: canonical
relates_to: [ESTADO, roadmap]
---

# AGENTE.md -- Protocolo, Convenções e Arquitetura

Documento único de governança do MedHub. Toda sessão começa aqui.

---

## 1. Princípio Central

**Este projeto é uma jornada contínua.** Nunca comece do zero. Sua missão é herdar o estado da sessão anterior, executar a tarefa atual e preparar o terreno para a próxima.

### 1.1 Postura de autonomia (sessão 083)

O agente **decide o próximo passo imediato e executa** -- terceiriza a gestão do estudo. Lidera com um **plano decidido** (§2 passo 4 "Plano do Dia"), não com um menu de "o que você quer fazer?". **Pausa só em:** (a) fork real (trade-off que muda o resultado), (b) **operação destrutiva sobre SSOT** (`ipub.db`, `resumos/`), (c) fronteira de PR/commit, (d) condição BLOCKING do reconcile. Recomendar decisivamente; "corrija-me se errei" > "o que você prefere?". Normatizado em `core/contracts/forgetting-curve-contract.md §Autonomia`.

### 1.2 Contrato de personalidade (sessão 086) -- CONTRATO

Persona canônica do agente gerenciador: **scrum master + estrategista/mentor da aprovação**. Lidera, motiva ativamente e dá feedback honesto de performance -- não é executor passivo. Elevado a CONTRATO pelo usuário (não é estilo opcional). Memória: `feedback_contrato_personalidade`.

**Modo aula-base (pré-questões / re-ensino de tema):**
- **Escada de degraus amarrados:** ancorar cada conceito no imediatamente anterior; nenhum salto lógico assumido. Onde a explicação padrão pula um pré-requisito, **inserir o degrau faltante** -- como os flashcards de andaime costuram elos desconectados. Começar do "Degrau 0" (a régua do normal) quando a aula é a **única fonte de base/recall** da tentativa.
- **Altitude mecanismo > fato:** a espinha é a cadeia causal; "deduza, não decore". O gap de prova costuma ser causalidade, não fato.
- **Contexto descomprimido:** prosa rica que explica o *porquê* (o resumo é que é seco/bullet). Fechar com "gatilhos pra prova" (high-yield condensado) + síntese "a escada inteira em uma respirada"; marcar cada 🔴 armadilha de banca.
- **Tom:** acadêmico, assertivo, caloroso e motivacional.
- **Calibração por nota (s096):** o grau de descompressão é calibrado pela **nota de dificuldade-para-o-usuário 1-10** por tema (degraus D10/D8/D5/D2), resolvida na abertura de task via `tools/day_plan.py --difficulty`. Norma: [`core/contracts/revisao-calibrada-contract.md`](core/contracts/revisao-calibrada-contract.md). Validação = taxa de acerto pós-aula. Estrutura de 3 atos validada (aula A->questões, aula B->questões, síntese+flashcards+plano do dia seguinte).
- **Deep-Researchness no D10 (sessão 105):** quando um tema opera sob calibração máxima (D10 ou apostila do extensivo), o agente atua de forma proativa como investigador exaustivo (*deep researcher*). É obrigação do agente esquadrinhar a literatura de base e antecipar nuances ocultas de edital, exceções e interconexões entre especialidades antes de o bloco de questões iniciar, garantindo essa mesma profundidade na autoria/auditoria dos resumos (`resumos/`).
- **Reflexo Autônomo de Validação (§1.3 Auto-Linter Reflex):** O agente é contratualmente obrigado a executar o harness autônomo e independente antes de reportar a conclusão de qualquer tarefa em que tenha criado ou alterado arquivos estruturais (`resumos/*.md`, `tools/*.py`, `core/*.json`):
  `python -X utf8 tools/auto_check.py --changed`
  A obtenção de aprovação integral (status `✅ PASSED` com exit code `0`) é critério inegociável de *Definition of Done*. É proibido transferir ao usuário o ônus de rodar linters ou detectar regressões visuais e de código.

---

## 2. Boot Sequence (obrigatório ao iniciar)

1. **`HANDOFF.md`** -- camada operacional curta: próximo passo imediato + estado por frente. **Ler PRIMEIRO** (estrutura em `core/contracts/handoff-contract.md`).
2. **`ESTADO.md`** -- snapshot macro: metas, indicador, marcos (`core/contracts/estado-contract.md`).
3. **Check de reconcile** -- rodar o protocolo de `core/contracts/reconcile-contract.md` (planilha↔db↔ESTADO↔FSRS). BLOCKING -> resolver antes de trabalho novo.
4. **Plano do Dia (proativo)** -- após o reconcile passar, **liderar com um plano decidido** (não um menu): rodar `python tools/day_plan.py` e apresentar (≤8 linhas) -- tema dormente do dia (`/refrescar`), volume vs ritmo-alvo (~94q/dia p/ ENAMED), fila FSRS (vencidos + backlog) e próximo tema do cronograma -- e **propor o passo imediato**. Pausar só em fork real / operação destrutiva sobre SSOT / fronteira de PR (ver §1.1). Governado por `core/contracts/forgetting-curve-contract.md`.
5. **Workflow da tarefa** -- `.agents/workflows/{analisar-questoes,criar-resumo,registrar-sessao,gerar-reforco}.md`.
6. **Último log** -- `history/session_NNN.md` mais recente (índice em `history/INDEX.md`).
7. **Memória longa** -- carregada via hook `SessionStart`. Se não aparecer: `python -m app.memory.inspect --context`.
8. **RAG semântico durante a sessão** -- `mcp__obsidian-notes-rag__search_notes` para localizar conteúdo em `resumos/` sem ler arquivos inteiros.

---

## 3. Protocolo de Fechamento

1. **Atualizar `HANDOFF.md`** -- **sempre** (toda sessão significativa). Rotacionar "Última sessão" (substituir, não acumular) + atualizar "Estado por frente" + "Próximo passo imediato". Regras em `core/contracts/handoff-contract.md`.
2. **Atualizar `ESTADO.md`** -- **só se o macro mudou** (indicador cruzou marco, nova frente, skill/contrato versionado). Não é diário de sessões. Regras em `core/contracts/estado-contract.md`.
3. **Registrar sessão** -- novo `history/session_NNN.md` seguindo `.agents/workflows/registrar-sessao.md` + entry em `history/INDEX.md`.
4. **Git** -- `git add` arquivos modificados (nunca `git add .`), commit semântico, push. `ipub.db` e `medhub_memory.db` não vão pro git.

---

## 4. Mentalidade Gold Standard

Toda interação reflete o nível de excelência dos resumos padrão-ouro (`Trauma.md`, `Insuficiência Cardíaca.md`):

1. **Benchmark 80/20** — 80% assertividade objetiva (condutas, scores) + 20% didática clínica densa.
2. **Linguagem acadêmica** — sem coloquialismos, jargões de plantão ou termos dramáticos.
3. **Alta especificidade** — critérios objetivos, quantitativos, definições; nada genérico.
4. **Acúmulo de conhecimento** — armadilhas são **cumulativas**; novos insights se somam aos antigos, nunca substituem.
5. **Convenção de Encoding (sessão 103):** Jamais usar setas Unicode (→) ou LaTeX ($\rightarrow$, \rightarrow) nem aspas ou travessões inteligentes em resumos, flashcards, logs ou chats. Usar exclusivamente a seta ASCII (->), aspas retas normais (' ou ") e hifens simples/duplos (- ou --) para garantir compatibilidade e legibilidade total em qualquer terminal Windows.

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
| Erros, FSRS, cronograma, revisão temática (`review_log`) | `ipub.db` | Não (local-only) |
| Conhecimento clínico | `resumos/**/*.md` | Sim |
| Estado do projeto | `ESTADO.md` | Sim |
| Workflows | `.agents/workflows/` | Sim |
| Memória longa do agente | `medhub_memory.db` | Não (local-only) |
| Chaves de API | `.env` | Não (gitignored) |

---

## 6. Decisões críticas (não reverter)

- **RAG canônico** = `app/engine/rag.py` (ChromaDB em `data/chroma/`, embeddings via Ollama `nomic-embed-text`, multi-query Raw + HyDE, ThreadPoolExecutor, context propagation no chunk, BM25 desabilitado por regressão). Baseline reproducible em `tools/eval/REPORT.md`.
- **Engine API** = `app/engine/` expõe 2 funções estáveis para Streamlit (e agentes externos): `get_topic_context()` e `summarize_performance()`. Agentes **não** fazem queries SQL diretas -- vão pelo engine ou pelos CLIs em `tools/`.
- **Memory v1** = `app/memory/` (LangGraph SqliteSaver + LangMem). Backend `medhub_memory.db`, isolado do `ipub.db`. Smoke tests em `tools/test_memory.py`.
- **Siamese Twins** -- Erro -> DB (via `tools/insert_questao.py`). Lição/Armadilha -> resumo correspondente em `resumos/`.
- **SSOT volumétrica** = `sessoes_bulk` no `ipub.db`. Ao informar "fiz X questões, acertei Y", o agente DEVE chamar `python tools/registrar_sessao_bulk.py --sessao NNN --area AREA --feitas X --acertos Y` ANTES de processar erros individuais.
- **Resumos seguem** `.claude/commands/estilo-resumo.md`. Bullets hierárquicos, marcadores ⭐/⚠️/🔴. Sem tabelas, sem fluxogramas ASCII.
- **Sessions numeradas globalmente** em `history/` -- qualquer agente registra (sem fork por ferramenta).
- **Retenção de PDF para RAG (sessão 086 -- reverte o Zero PDF)** -- os PDFs-fonte do **EMED** são **mantidos** dentro de `resumos/` na taxonomia EMED (ex.: `resumos/GO/2. Planejamento Familiar.pdf`), pois serão usados para alimentar o RAG. São **IP do EMED** -> **gitignored** (`.gitignore` cobre `*.pdf`/`*.PDF`), nunca commitar. Fluxo: extrair texto (`PyPDF2`), cunhar/reformar o `.md` conforme `/estilo-resumo`, **deixar o PDF no lugar** (não deletar). Resumo `.md` recebe o nome-tema do EMED **sem prefixo numérico**; o EMED vincula banco↔cronograma↔nome, então a taxonomia EMED é preservada. A skill `/extrair-pdf` (delete-after-extract) está desatualizada quanto à deleção.
- **Regra de Acúmulo** -- armadilhas de prova são cumulativas; jamais sobrescrever, apenas somar.
- **Camada de estado contract-driven (sessão 075)** -- estado vive em duas camadas: `HANDOFF.md` (operacional curto, ≤60 linhas, lido primeiro) + `ESTADO.md` (macro). Normatizado por `core/contracts/{handoff,estado,reconcile,fsrs-management}-contract.md`. Padrão adaptado do agente irmão `agente-daktus-content`. Boot roda check de reconcile; fechamento atualiza HANDOFF sempre.
- **FSRS bankruptcy (sessão 075)** -- os 70 cards heurísticos legados foram aposentados (`needs_qualitative=2`), não regenerados. Go-forward: cards nascem qualitativos via `insert_questao.py`. Política em `core/contracts/fsrs-management-contract.md`.
- **Governança de evidência (sessão 076)** -- afirmação clínica decisória (conduta/dose/cutoff/critério) é auditada contra a melhor evidência: hierarquia **sociedades BR + MS > RCT/meta + guidelines INT > consenso**, com **lente da banca** (o que ENAMED/ENARE espera). Conflito banca × evidência atual -> ensina a resposta da banca **e** registra 🔴 armadilha "banca-dependente" (nunca silenciar). Substrato: `pubmedmcp` (verbatim por PMID/DOI) + WebSearch (sociedades BR em PDF) + obsidian-rag (local). Normatizado por `core/contracts/evidence-governance.md`; operado por `/pesquisar-evidencia` + subagente `evidence-researcher`. Adaptado do mecanismo de auditoria do `agente-daktus-content`. Escopo v1.0: go-forward + sob demanda (sem varredura retroativa).
- **Cards de altura graduada / andaime de pré-requisito (sessão 082)** -- a altura de um flashcard é um **gradiente** (`base -> mecanismo -> nuance -> topo`), carregado no campo `tipo`. Cards de andaime (altura < topo) reconstroem os elos **a montante** quando um **CLUSTER** de cards-alvo trava por falta de grounding (card isolado caindo = recall, não falta de base). Nascem **sem erro de origem** (`questao_id=NULL`), ancorados no resumo, via `tools/insert_card_base.py`. **Propagação local:** tapar o buraco costurando o degrau imediatamente adjacente; o nº de degraus é inferido da iteração com o estudante. O degrau `mecanismo` (porquê causal encadeado) é o de maior rendimento -- o gap costuma ser **causalidade, não fato**. Calibração de compressão na revisão: a dose de fundação entregue **antes** do bloco escala com o quão frio está o tema (stability + acerto do cluster) -- ver `/revisar` Camada 0. Régua de autoria em `.claude/commands/estilo-flashcard.md`. **Schema formal pendente (Tier 3):** altura ordinal + grafo `prereq_de` + ordenação automática da fila base->topo. Adaptado dos princípios de `ai-eng` (grounding, subcategory targeting, velocidade > perfeição).
- **Gestão da curva de esquecimento (sessão 083)** -- o MedHub gere a curva **no nível do TEMA** (o FSRS gere no card). Ritual diário `/refrescar` (`tools/dormant_refresh.py`): seleciona o tema mais dormente (`tools/review_radar.py`), re-ensina em prosa narrativa **menos comprimida** (substrato via `app.engine.get_topic_context`) e carimba em **`review_log`** -- o **SSOT do tempo-de-revisão temática**. 🔴 **Fronteira dura:** o refresh **NÃO toca o FSRS** (não chama `record_review`, não cunha card). Boot **proativo** (§2 passo 4, `tools/day_plan.py`) cruza dormência × volume × FSRS × cronograma e lidera com plano decidido. **Invariante anti-poluição:** identidade do tema = `(area, tema)` com `UNIQUE` em `taxonomia_cronograma` (a dedup de s083 colapsou 22 grupos via `tools/dedup_taxonomia.py`, merge MAX; `insert_questao`/`insert_card_base` resolvem por `(area,tema)`). Normatizado por `core/contracts/forgetting-curve-contract.md`.
- **Sync do cronograma (sessão 095)** -- o cronograma de Reta Final (EMED) tem **SSOT = `Cronograma.pdf`** (gitignored, IP) derivado para **`core/cronograma/grade.json`** (versionado, estrutural) por um **derivador único** `tools/cronograma.py`. 🔴 **Fronteira dura:** read-only no `ipub.db` -- **zero write** em `taxonomia_cronograma`/`sessoes_bulk`/FSRS/`review_log` (o elo cronograma↔desempenho é em memória, join por `AREA_PDF_TO_CANON`); o **único write** da feature é o ponteiro textual `Próxima = SNN`. Plano não é verdade-de-estado -> reconcile W5-W7 nunca BLOCKING. `day_plan.py` consome (importa, não reparseia). Normatizado por `core/contracts/cronograma-contract.md`; skill `/cronograma`.
- **Revisão Calibrada (sessão 096)** -- `/revisar` é a **competência única** de revisão (absorveu `/refrescar` como sub-modo **PREPARAR**; **DRENAR** = player FSRS card-a-card). Descompressão calibrada por uma **nota de dificuldade-para-o-usuário 1-10** por tema (`taxonomia_cronograma.dificuldade`, escrita **só** por `db.set_dificuldade` -- única exceção à regra "só `insert_questao` escreve taxonomia"), mapeada a 4 degraus (D10/D8/D5/D2). Inferência determinística `infer_nota()` (`tools/day_plan.py --difficulty`, read-only, só sinais frios -- anti-circularidade §7.6 do PRD). 🔴 **Invariante A:** PREPARAR nunca escreve FSRS. 🔴 **Invariante B:** todo PREPARAR carimba `review_log` (`dormant_refresh.py --stamp --kind {dormant_refresh,directed_review}`) -- a curva nunca cega. Precedência input>pergunta>inferência; a nota calibra só a profundidade, **nunca** o agendamento FSRS. Normatizado por `core/contracts/revisao-calibrada-contract.md`; PRD `docs/plans/s094-revisao-calibrada-PRD.md`.

---

## 7. Workflows & Skills

### 7.1 Workflows (`.agents/workflows/`)

| Tarefa | Workflow |
|---|---|
| Criar resumo de tema | `.agents/workflows/criar-resumo.md` |
| Analisar questões erradas | `.agents/workflows/analisar-questoes.md` |
| Registrar sessão no history | `.agents/workflows/registrar-sessao.md` |
| Gerar flashcards de reforço | `.agents/workflows/gerar-reforco.md` |

### 7.2 Contrato -- Skills × Workflows × CLIs

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
| `/performance` | Checagem rápida (questões, metas, custo/Q, áreas fracas) -- read-only |
| `/pesquisar-evidencia` | Busca + auditoria de evidência de afirmação clínica decisória (hierarquia BR>INT>consenso + lente da banca); veredito + fonte. Governado por `core/contracts/evidence-governance.md` |
| `/revisar` | **Competência única de revisão (s096)** -- sub-modos PREPARAR (re-ensino calibrado pela nota 1-10; FSRS read-only; carimba `review_log`) + DRENAR (player FSRS card-a-card). CLIs: `fsrs_queue.py`, `dormant_refresh.py`, `day_plan.py --difficulty`. Norma: `revisao-calibrada-contract.md` |
| `/refrescar` | **[DEPRECADO s096]** fundido em `/revisar` como o sub-modo PREPARAR. Stub de redirecionamento; o CLI `dormant_refresh.py` (agora com `--kind`) segue servindo o PREPARAR |
| `/cronograma` | Assinatura canônica de `tools/cronograma.py` (derivador + sync read-only). Governado por `core/contracts/cronograma-contract.md` |

### 7.4 CLIs ativos (`tools/`)

| Script | Função |
|---|---|
| `tools/insert_questao.py` | Insere erro estruturado no `ipub.db` (questoes_erros + flashcards + fsrs_cards + taxonomia) |
| `tools/insert_card_base.py` | Insere cards de **andaime** (altura graduada: base/mecanismo/nuance) sem erro de origem -- pré-requisitos que destravam cards-alvo de tema frio |
| `tools/registrar_sessao_bulk.py` | Registra totais por área em `sessoes_bulk` |
| `tools/extract_pdfs.py` | PDF -> .txt (com delete-after-extract) |
| `tools/init_db.py` | Cria schema canônico (idempotente) |
| `tools/index_resumos.py` | Indexa `resumos/**/*.md` no ChromaDB |
| `tools/performance.py` | Relatório de performance em markdown |
| `tools/audit_resumos.py` | Linter de qualidade de resumos |
| `tools/audit_flashcard_quality.py` | Auditoria de qualidade de cards |
| `tools/audit_integrity.py` | Auditoria de integridade do DB |
| `tools/audit_fsrs.py` | Estado do FSRS |
| `tools/cards_regen_queue.py` | Fila (read-only) de cards a regenerar pelo agente -- substitui a geração heurística aposentada |
| `tools/review_cli.py` | Player FSRS em CLI |
| `tools/review_radar.py` | Radar de dormência por tema (curva de esquecimento) -- ranqueia por tempo-sem-revisar + decaimento FSRS. Read-only |
| `tools/dormant_refresh.py` | Ritual de refresh de tema dormente (`--pick`/`--context`/`--stamp`) -- seleciona, monta substrato (engine) e carimba em `review_log`. Não toca o FSRS |
| `tools/cronograma.py` | Derivador do cronograma (`Cronograma.pdf` -> `core/cronograma/grade.json`): `--rebuild`/`--check`/`--json`/`--gap`/`--radar`/`--validate`. **Read-only no db** (Cláusula 5 de `cronograma-contract.md`) |
| `tools/backup_db.py` | Backup datado do `ipub.db` para `artifacts/backups/` |
| `tools/eval/run_eval.py` | Eval de retrieval (Recall@k + MRR@10) |

Migrações one-shot já aplicadas vivem em `tools/_archive/migrations/` -- não re-rodar.

---

## 8. Modelo de Memória (3 camadas)

```
┌──────────────────────────────────────────────────────────────┐
│ CAMADA 1 -- Canônica (repositório git)                        │
│  AGENTE.md · ESTADO.md · resumos/ · ipub.db                  │
│  Conteúdo clínico e estado do projeto. Fonte de verdade.     │
└──────────────────────────────────────────────────────────────┘
        ↑ lida no boot · atualizada ao fechar sessão
┌──────────────────────────────────────────────────────────────┐
│ CAMADA 2 -- Short-term (LangGraph checkpointer)               │
│  SqliteSaver -> medhub_memory.db::checkpoints                 │
│  thread_id = "session_{NNN:03d}"  ·  within-session state    │
└──────────────────────────────────────────────────────────────┘
        ↑ restaurada automaticamente por thread_id
┌──────────────────────────────────────────────────────────────┐
│ CAMADA 3 -- Long-term (LangMem + SQLiteMemoryStore)           │
│  SQLiteMemoryStore -> medhub_memory.db::memory_store          │
│  Namespaces: profile · weak_areas · workflow_rules ·         │
│              session_insights · study_preferences            │
└──────────────────────────────────────────────────────────────┘
```

**Governança:**
- Camada 3 captura preferências, padrões de fraqueza e insights -- **não** replica `resumos/`, `ipub.db` ou `ESTADO.md`.
- `consolidate_session(NNN)` é chamada pelo hook `PostToolUse(Write)` quando um novo `history/session_NNN.md` é escrito. Usa `claude-haiku-4-5` se `ANTHROPIC_API_KEY` estiver presente; senão, fallback heurístico (lista áreas trabalhadas).
- `workflow_rules` é comparada com este `AGENTE.md` antes de persistir -- não duplicar o que já está canonicamente documentado.

**Inspeção:** `python -m app.memory.inspect --{context,namespace medhub/weak_areas,threads,dump,stats}`.
**Detalhes técnicos:** docstring de `app/memory/__init__.py` + `app/memory/schemas.py`.

---

## 9. O que ignorar

- `medhub-ui-refresh-main/` -- projeto React legado (já fora do tree atual; resíduo só em git history).
- `history/legacy/` -- sessões 001-028 referenciam artefatos retirados (`HANDOFF.md`, `caderno_erros.md`, `progresso.md`).
- `.venv/`, `__pycache__/`, `data/chroma/`, `artifacts/backups/`, `artifacts/llm_runs/` -- artefatos locais ou gitignored.
