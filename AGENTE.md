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
- 🔴 **Gatilho da aula-base — HÍBRIDO POR DIFICULDADE (decisão do usuário, s126).** A aula-base **deixa de ser obrigatória antes de todo bloco**. Regra: **tema-zero ou nota D8+ → aula-base completa antes das questões** (é o caso que já se provou: Meningites 53% → 75%, Pneumo Intensiva II). **Tema D5 ou menor → questões primeiro**, e a aula entra **depois, mirando o buraco que o erro expôs** — não como cobertura preventiva do tema inteiro. Origem: Pedro Martins assistiu 73h de aula no ano inteiro e usou aula só como tapa-buraco reativo (o caso gasometria: errava repetidamente → leu uma revisão do NEJM → parou de errar). O custo da aula preventiva em tema fácil não se paga. **Não confundir com corte de escopo:** quando a aula acontece, a cobertura segue sendo piso fixo (Cláusula 10/Invariante E) — muda o *gatilho*, não a *profundidade*.
- **Regra D10 (extensivo) — única, idêntica em `tools/day_plan.py`, `core/contracts/revisao-calibrada-contract.md` e aqui (sessão 105/107):** material extensivo ou inferência sem nota explícita → degrau D10 + dever de Deep-Researchness; a nota explícita do usuário (fonte=usuario) sempre vence (precedência input > pergunta > inferência). Sob D10/extensivo o agente atua como investigador exaustivo (*deep researcher*): esquadrinha a literatura de base e antecipa nuances ocultas de edital, exceções e interconexões entre especialidades antes de o bloco de questões iniciar, garantindo essa mesma profundidade na autoria/auditoria dos resumos (`resumos/`).

### 1.3 Reflexo Autônomo de Validação (Auto-Linter Reflex)

O agente é contratualmente obrigado a executar o harness autônomo e independente antes de reportar a conclusão de qualquer tarefa em que tenha criado ou alterado arquivos estruturais (`resumos/*.md`, `tools/*.py`, `core/*.json`):

`python -X utf8 tools/auto_check.py --changed`

A obtenção de aprovação integral (status `✅ PASSED` com exit code `0`) é critério inegociável de *Definition of Done*. É proibido transferir ao usuário o ônus de rodar linters ou detectar regressões visuais e de código.

---

## 2. Boot Sequence (obrigatório ao iniciar)

1. **`HANDOFF.md`** -- camada operacional curta: próximo passo imediato + estado por frente. **Ler PRIMEIRO** (estrutura em `core/contracts/handoff-contract.md`).
2. **`ESTADO.md`** -- snapshot macro: metas, indicador, marcos (`core/contracts/estado-contract.md`).
3. **Check de reconcile** -- rodar o protocolo de `core/contracts/reconcile-contract.md` (planilha↔db↔ESTADO↔FSRS). BLOCKING -> resolver antes de trabalho novo.
4. **Plano do Dia** -- o hook `SessionStart` já rodou `tools/day_plan.py` e injetou o plano antes do 1o turno: **não re-rodar**. Liderar com ele e propor o passo imediato. Sob demanda: `--difficulty`, `--tempo H --energia alta|media|baixa`. Ritmo-alvo mede a **grade**, nunca a prova (`core/provas.json`, countdown no cabeçalho). Conclusão/ordem do cronograma: `reconcile-contract.md` W8. Normas: `forgetting-curve`/`orquestracao`/`cronograma`-contract. Pausas: §1.1.
5. **Workflow da tarefa** -- `.agents/workflows/{analisar-questoes,criar-resumo,registrar-sessao,gerar-reforco}.md`.
6. **Último log** -- `history/session_NNN.md` mais recente (índice em `history/INDEX.md`).
7. **Memória longa** -- carregada via hook `SessionStart`. Se não aparecer: `python -m app.memory.inspect --context`.
8. **RAG semântico durante a sessão** -- motor único = `app/engine/rag.py` (via `app/engine/get_topic_context.py`) para localizar conteúdo em `resumos/` sem ler arquivos inteiros. O MCP `obsidian-notes-rag` foi descontinuado (ROADMAP: indexava snapshot stale; decisão empírica) -- não usar.

---

## 3. Protocolo de Fechamento

1. **Atualizar `HANDOFF.md`** -- **sempre** (toda sessão significativa). Rotacionar "Última sessão" (substituir, não acumular) + atualizar "Estado por frente" + "Próximo passo imediato". Regras em `core/contracts/handoff-contract.md`. **Números derivados (F6):** o bloco numérico do "Estado por frente" (volume, perf, FSRS, backlog) é gerado por `python tools/day_plan.py --handoff-block` -- nunca digitado à mão; só o texto qualitativo é manual.
2. **Atualizar `ESTADO.md`** -- **só se o macro mudou** (indicador cruzou marco, nova frente, skill/contrato versionado). Não é diário de sessões. Regras em `core/contracts/estado-contract.md`.
3. **Registrar sessão** -- novo `history/session_NNN.md` seguindo `.agents/workflows/registrar-sessao.md` + entry em `history/INDEX.md`. **Invariante de ponteiro (F1):** o `auto_check` verifica que o ponteiro do HANDOFF não excede `max(history/session_NNN) + 1` (WARN `SESSION_POINTER_DRIFT`) -- selar a sessão aqui é o que mantém o passo 1 legítimo.
4. **Auto-higiene** -- **arquivo absorvido/integrado em doc mais estável SAI no mesmo commit do selo**; relatório incorporado por outro mais fresco SAI. Veredito **binário** (fica ou é deletado) -- sem `archive/`, sem "deixa por enquanto": o conteúdo já vive no doc que o absorveu, e a cópia órfã só existe para envelhecer e mentir. Vale para relatórios de sessão, specs cumpridas, scratch de `tmp/` e backups fora da rotação. O que NÃO sai: SSOT (`resumos/`, `history/`, `core/`), dívida ativa declarada no HANDOFF e PDFs-fonte EMED.
5. **Git** -- `git add` arquivos modificados (nunca `git add .`), commit semântico, push. `ipub.db` e `medhub_memory.db` não vão pro git.

**Checklist do rito:** HANDOFF -> ESTADO (se o macro mudou) -> `session_NNN` + INDEX -> **auto-higiene (o que foi absorvido saiu?)** -> commit semântico.

---

## 4. Mentalidade Gold Standard

Toda interação reflete o nível de excelência dos resumos padrão-ouro (`Trauma.md`, `Insuficiência Cardíaca.md`):

1. **Benchmark 80/20** — 80% assertividade objetiva (condutas, scores) + 20% didática clínica densa.
2. **Linguagem acadêmica** — sem coloquialismos, jargões de plantão ou termos dramáticos.
3. **Alta especificidade** — critérios objetivos, quantitativos, definições; nada genérico.
4. **Acúmulo de conhecimento** — armadilhas são **cumulativas**; novos insights se somam aos antigos, nunca substituem.
5. **Convenção de Encoding e Zero LaTeX (sessão 103/108):** Jamais utilizar sintaxe de LaTeX inline (`$ ... $` ou `$$ ... $$`), comandos matemáticos (`\rightarrow`, `\le`, `\ge`, `\mu`), ou cifrões encapsulando números e desigualdades (`$< 60$`, `$> 1000$`, `$\rightarrow$`) em resumos, flashcards, logs ou respostas no chat. É terminantemente proibido o uso de setas Unicode (→), aspas ou travessões inteligentes (–, —). Usar exclusivamente Markdown e ASCII limpo: seta simples (`->`), sinais de menor/maior diretos (`< 60`, `> 1000`, `<=`, `>=`), aspas retas normais (' ou ") e hifens simples/duplos (- ou --), garantindo legibilidade perfeita e zero quebra visual em qualquer terminal ou app externo.

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

- **RAG canônico** = `app/engine/rag.py` (ChromaDB em `data/chroma/`, embeddings via Ollama `nomic-embed-text`, multi-query Raw + HyDE, ThreadPoolExecutor, context propagation no chunk, **gold-only**: a collection `pdf_raw` e o `search_two_tier()` foram removidos na consolidacao part-2). Baseline reproducible em `tools/eval/REPORT.md`. (BM25 rerank removido em 2026-07-12 -- era regressivo no corpus médico; ver `.vibeflow/audits/mecanismo-conhecimento-consolidacao-part-1-audit.md`.)
- **Engine API** = `app/engine/` expõe **1 superficie estavel** para agentes: `get_topic_context()` (sobre `rag.py`). `summarize_performance()` foi removido junto com a UI Streamlit -- performance sai pela skill `/performance` + CLIs. Agentes **não** fazem queries SQL diretas -- vão pelo engine ou pelos CLIs em `tools/`.
- **Memory v1** = `app/memory/` (LangMem + `SQLiteMemoryStore`). Backend `medhub_memory.db`, isolado do `ipub.db`. Smoke tests em `tools/test_memory.py`.
- **Siamese Twins** -- Erro -> DB (via `tools/insert_questao.py`). Lição/Armadilha -> resumo correspondente em `resumos/`.
- **SSOT volumétrica** = `sessoes_bulk` no `ipub.db`. Ao informar "fiz X questões, acertei Y", o agente DEVE chamar `python tools/registrar_sessao_bulk.py --sessao NNN --area AREA --feitas X --acertos Y` ANTES de processar erros individuais.
- **Resumos seguem** `.claude/commands/estilo-resumo.md`. Bullets hierárquicos, marcadores ⭐/⚠️/🔴. Sem tabelas, sem fluxogramas ASCII.
- **Sessions numeradas globalmente** em `history/` -- qualquer agente registra (sem fork por ferramenta).
- **Retenção de PDF para RAG (sessão 086 -- reverte o Zero PDF)** -- os PDFs-fonte do **EMED** são **mantidos** dentro de `resumos/` na taxonomia EMED (ex.: `resumos/GO/2. Planejamento Familiar.pdf`), pois serão usados para alimentar o RAG. São **IP do EMED** -> **gitignored** (`.gitignore` cobre `*.pdf`/`*.PDF`), nunca commitar. Fluxo: extrair texto (`PyPDF2`), cunhar/reformar o `.md` conforme `/estilo-resumo`, **deixar o PDF no lugar** (não deletar). Resumo `.md` recebe o nome-tema do EMED **sem prefixo numérico**; o EMED vincula banco↔cronograma↔nome, então a taxonomia EMED é preservada. A skill `/extrair-pdf` (delete-after-extract) está desatualizada quanto à deleção.
- **Regra de Acúmulo** -- armadilhas de prova são cumulativas; jamais sobrescrever, apenas somar.
- **Camada de estado contract-driven (sessão 075)** -- estado vive em duas camadas: `HANDOFF.md` (operacional curto, ≤60 linhas, lido primeiro) + `ESTADO.md` (macro). Normatizado por `core/contracts/{handoff,estado,reconcile,fsrs-management}-contract.md`. Padrão adaptado do agente irmão `agente-daktus-content`. Boot roda check de reconcile; fechamento atualiza HANDOFF sempre.
- **FSRS bankruptcy (sessão 075)** -- os 70 cards heurísticos legados foram aposentados (`needs_qualitative=2`), não regenerados. Go-forward: cards nascem qualitativos via `insert_questao.py`. Política em `core/contracts/fsrs-management-contract.md`.
- **Governança de evidência (sessão 076)** -- afirmação clínica decisória (conduta/dose/cutoff/critério) é auditada contra a melhor evidência: hierarquia **sociedades BR + MS > RCT/meta + guidelines INT > consenso**, com **lente da banca** (o que ENAMED/ENARE espera). Conflito banca × evidência atual -> ensina a resposta da banca **e** registra 🔴 armadilha "banca-dependente" (nunca silenciar). Substrato: `pubmedmcp` (verbatim por PMID/DOI) + WebSearch (sociedades BR em PDF) + RAG local (`app/engine/rag.py`). Normatizado por `core/contracts/evidence-governance.md`; operado por `/pesquisar-evidencia` + subagente `evidence-researcher`. Adaptado do mecanismo de auditoria do `agente-daktus-content`. Escopo v1.0: go-forward + sob demanda (sem varredura retroativa).
- **Cards de altura graduada / andaime de pré-requisito (sessão 082)** -- a altura de um flashcard é um **gradiente** (`base -> mecanismo -> nuance -> topo`), carregado no campo `tipo`. Cards de andaime (altura < topo) reconstroem os elos **a montante** quando um **CLUSTER** de cards-alvo trava por falta de grounding (card isolado caindo = recall, não falta de base). Nascem **sem erro de origem** (`questao_id=NULL`), ancorados no resumo, via `tools/insert_card_base.py`. **Propagação local:** tapar o buraco costurando o degrau imediatamente adjacente; o nº de degraus é inferido da iteração com o estudante. O degrau `mecanismo` (porquê causal encadeado) é o de maior rendimento -- o gap costuma ser **causalidade, não fato**. Calibração de compressão na revisão: a dose de fundação entregue **antes** do bloco escala com o quão frio está o tema (stability + acerto do cluster) -- ver `/revisar` Camada 0. Régua de autoria em `.claude/commands/estilo-flashcard.md`. **Schema formal pendente (Tier 3):** altura ordinal + grafo `prereq_de` + ordenação automática da fila base->topo. Adaptado dos princípios de `ai-eng` (grounding, subcategory targeting, velocidade > perfeição).
- **Gestão da curva de esquecimento (sessão 083)** -- o MedHub gere a curva **no nível do TEMA** (o FSRS gere no card). Ritual diário `/refrescar` (`tools/dormant_refresh.py`): seleciona o tema mais dormente (`tools/review_radar.py`), re-ensina em prosa narrativa **menos comprimida** (substrato via `app.engine.get_topic_context`) e carimba em **`review_log`** -- o **SSOT do tempo-de-revisão temática**. 🔴 **Fronteira dura:** o refresh **NÃO toca o FSRS** (não chama `record_review`, não cunha card). Boot **proativo** (§2 passo 4, `tools/day_plan.py`) cruza dormência × volume × FSRS × cronograma e lidera com plano decidido. **Invariante anti-poluição:** identidade do tema = `(area, tema)` com `UNIQUE` em `taxonomia_cronograma` (a dedup de s083 colapsou 22 grupos via `tools/dedup_taxonomia.py`, merge MAX; `insert_questao`/`insert_card_base` resolvem por `(area,tema)`). Normatizado por `core/contracts/forgetting-curve-contract.md`.
- **Sync do cronograma (sessão 095)** -- o cronograma de Reta Final (EMED) tem **SSOT = `Cronograma.pdf`** (gitignored, IP) derivado para **`core/cronograma/grade.json`** (versionado, estrutural) por um **derivador único** `tools/cronograma.py`. 🔴 **Fronteira dura:** read-only no `ipub.db` -- **zero write** em `taxonomia_cronograma`/`sessoes_bulk`/FSRS/`review_log` (o elo cronograma↔desempenho é em memória, join por `AREA_PDF_TO_CANON`); o **único write** da feature é o ponteiro textual `Próxima = SNN`. Plano não é verdade-de-estado -> reconcile W5-W7 nunca BLOCKING. `day_plan.py` consome (importa, não reparseia). Normatizado por `core/contracts/cronograma-contract.md`; skill `/cronograma`.
- **Harness autônomo staged-only + warning-first (sessão 106/107)** -- `tools/auto_check.py` valida antes do commit: o git pre-commit hook roda `--staged` (audita só o que será selado, quotepath-safe p/ caminhos acentuados), e o Reflexo Autônomo §1.3 roda `--changed` (árvore). Achados têm **duas severidades**: **BLOCK** (exit 1, bloqueia — Armadilhas ausente, tabela ASCII, `UnicodeDecodeError`) e **WARN** (exit 0, só adverte, agregado por tipo — frontmatter §5.2 incompleto, encoding não-ASCII proibido, drift de paridade command↔skill). Regra nova **nasce WARN** e só vira BLOCK "quando a base zerar". Normatizado pelas specs `autogovernanca-proativa-part-2/3`.
- **Fonte canônica de skills = `.claude/commands` + espelhos gerados (sessão 107)** -- `.claude/commands/*.md` é a **fonte canônica única** das skills; os `.agents/skills/source-command-*/SKILL.md` são **build artifacts** gerados por `tools/sync_skills.py` (nunca editados à mão). `sync_skills --check` (consumido pelo `auto_check`) acusa quando alguém edita o canônico sem regenerar o espelho (WARN de paridade, não bloqueia). Estende a disciplina §7.2 ("assinatura canônica em UMA skill") ao par command↔skill.
- **Load balancing do agendamento FSRS (sessão 128)** -- o FSRS agenda cada card isoladamente (`due = hoje + I`) e ninguém olha o calendário, o que produz carga **grumosa**: 48 cards num dia ao lado de dias com 2. Como a curva de retenção é ~plana numa vizinhança pequena de `I`, existe folga de graça: `app/utils/fsrs_balance.py` escolhe, **dentro dessa folga**, o dia de **menor carga já agendada**. 🔴 **Fronteiras duras:** (a) **não toca `stability` nem `difficulty`** -- move apenas a DATA; (b) janela conservadora de **±5% do intervalo** (piso 1 dia, teto 10); (c) só card de **revisão (`state == 2`) com intervalo >= 4 dias** -- passos de aprendizado/relearning são intra-sessão e mover 1 dia num card de 2 dias é erro de 50%, não folga; (d) **nunca agenda no passado ou hoje**; (e) empate preserva o dia que o FSRS calculou (só desvia com ganho real). O módulo é **puro** (recebe a carga como dict, não importa `sqlite3`) -- a consulta vive em `db.carga_agendada`, respeitando a regra de SSOT, e por isso a regra é testável sem banco. Ponto de aplicação: dentro de `record_review`, o **caminho único de escrita do FSRS**; falha no balanceamento nunca derruba a gravação da revisão (degrada para o `due` original com WARN). Visibilidade: `tools/fsrs_load.py` mostra a distribuição e o **CV** (desvio/média) que o achatamento deve derrubar. Suíte `tools/test_fsrs_balance.py` é **BLOCKING** no `auto_check` (check 2c) -- regressão aqui corrompe a curva.
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
| Curar/reforjar o backlog de flashcards | `.agents/workflows/curar-cards.md` |

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

> **Tabela GERADA — não editar à mão.** Regenerar com `python tools/reachability_check.py --tabela` e colar aqui.
> Antes da consolidação part-6 esta tabela era mantida à mão e listava 21 dos CLIs vivos; o check de alcançabilidade encontrou os demais. Uma tabela digitada à mão envelhece em silêncio — que é exatamente o defeito (*construído-e-nunca-conectado*, achado D4) que o check existe para pegar.
> Colunas: **O que faz** vem da 1ª linha da docstring do módulo (`—` = módulo sem docstring, lacuna a fechar); **Alcançado por** são os referenciadores vivos que o check encontrou.

| CLI | O que faz | Alcancado por |
|---|---|---|
| `tools/audit_card_atomicity.py` | Check de ATOMICIDADE de flashcard (spec: estilo-flashcard.md §Formato atomico) | `.agents/skills/source-command-estilo-flashcard/SKILL.md`, `.claude/commands/estilo-flashcard.md` (+5) |
| `tools/audit_flashcard_quality.py` | — | `.agents/workflows/curar-cards.md` (+3) |
| `tools/audit_resumos.py` | — | `.agents/skills/source-command-auditar-resumos/SKILL.md`, `.claude/commands/auditar-resumos.md` (+4) |
| `tools/auto_check.py` | — | `.agents/skills/source-command-estilo-resumo/SKILL.md`, `.claude/commands/estilo-resumo.md` (+14) |
| `tools/backfill_review_log.py` | semeia review_log com a ÚLTIMA REVISÃO REAL por tema | `core/contracts/forgetting-curve-contract.md` |
| `tools/backup_db.py` | — | `.agents/workflows/curar-cards.md` (+2) |
| `tools/card_checks.py` | biblioteca ÚNICA de predicados de qualidade de flashcard | `pytest.ini` (+10) |
| `tools/card_self_sufficiency.py` | Check de auto-suficiencia de flashcard (check 8 do auto_check -- spec | `tools/auto_check.py`, `tools/test_card_self_sufficiency.py` |
| `tools/cards_regen_queue.py` | fila de regeneração de flashcards em JSON | `.agents/skills/source-command-estilo-flashcard/SKILL.md`, `.claude/commands/estilo-flashcard.md` (+1) |
| `tools/check_fk_orphans.py` | varredura read-only de integridade do ipub.db | `.claude/settings.local.json` (+3) |
| `tools/cobertura_conhecimento.py` | — | `.agents/skills/source-command-extrair-pdf/SKILL.md`, `.claude/commands/extrair-pdf.md` (+3) |
| `tools/cronograma.py` | Derivador único do cronograma de Reta Final (read-only) | `.agents/skills/source-command-cronograma/SKILL.md`, `.agents/skills/source-command-importar-planilha/SKILL.md` (+15) |
| `tools/day_plan.py` | Plano do Dia para o boot proativo | `.agents/skills/source-command-cronograma/SKILL.md`, `.agents/skills/source-command-revisar/SKILL.md` (+21) |
| `tools/dedup_taxonomia.py` | colapsa linhas duplicadas (area,tema) em taxonomia_cronograma | `.agents/workflows/curar-cards.md`, `core/contracts/forgetting-curve-contract.md` (+2) |
| `tools/detect_clones.py` | near-duplicates de flashcards POR TEMA | `.agents/workflows/curar-cards.md` |
| `tools/doc_drift.py` | Sensor de drift doc-vs-codigo (check 7 do auto_check -- degrau 1 da auto-evolucao) | `pytest.ini` (+6) |
| `tools/dormant_refresh.py` | ritual diário de refresh de tema DORMENTE | `.agents/skills/source-command-refrescar/SKILL.md`, `.agents/skills/source-command-revisar/SKILL.md` (+7) |
| `tools/emed_flashcards.py` | Corpus de flashcards do EMED 2024 -- colheita, extracao e consulta | `.agents/skills/source-command-analisar-questao/SKILL.md`, `.agents/skills/source-command-estilo-flashcard/SKILL.md` (+4) |
| `tools/event_log.py` | eventos append-only do pipeline de flashcards (P3 part-4) | `tools/insert_questao.py`, `tools/learning_efficacy.py` (+1) |
| `tools/extract_pdfs.py` | — | `.agents/skills/source-command-extrair-pdf/SKILL.md`, `.agents/workflows/criar-resumo.md` (+2) |
| `tools/fsrs_load.py` | Previsao de carga do calendario FSRS (s128) -- read-only | `tools/auto_check.py` |
| `tools/fsrs_queue.py` | fila de revisão FSRS em JSON para revisão conversacional | `.agents/skills/source-command-revisar/SKILL.md`, `.claude/commands/revisar.md` (+9) |
| `tools/habilidades.py` | — | `.agents/skills/source-command-analisar-questao/SKILL.md`, `.claude/commands/analisar-questao.md` (+5) |
| `tools/importar_sessoes.py` | importa volume de sessões em lote a partir de JSON | `.agents/skills/source-command-importar-planilha/SKILL.md`, `.claude/commands/importar-planilha.md` (+1) |
| `tools/index_resumos.py` | — | `.agents/workflows/registrar-sessao.md` (+2) |
| `tools/init_db.py` | — | `tools/check_fk_orphans.py`, `tools/test_habilidades.py` (+1) |
| `tools/insert_card_base.py` | insere flashcards de PRÉ-REQUISITO (altitude base) no ipub.db | `.agents/skills/source-command-estilo-flashcard/SKILL.md`, `.agents/skills/source-command-revisar/SKILL.md` (+7) |
| `tools/insert_card_extra.py` | insere cards adicionais vinculados a um questao_id EXISTENTE | `.agents/workflows/curar-cards.md` (+3) |
| `tools/insert_questao.py` | — | `.agents/skills/source-command-analisar-questao/SKILL.md`, `.agents/skills/source-command-estilo-flashcard/SKILL.md` (+28) |
| `tools/learning_efficacy.py` | eficácia de aprendizado por dimensão (P3 part-4) | `tools/test_event_log_efficacy.py` |
| `tools/ledger_self.py` | Ledger-of-self: memoria estruturada dos WARNs do harness (degrau 2 da auto-evolucao) | `pytest.ini` (+6) |
| `tools/normalize_taxonomia.py` | saneia taxonomia_cronograma (Fase 1 da curadoria de cards, s097) | `.agents/workflows/curar-cards.md` |
| `tools/performance.py` | — | `.agents/skills/source-command-cronograma/SKILL.md`, `.agents/skills/source-command-performance/SKILL.md` (+10) |
| `tools/preparacao.py` | — | `core/contracts/cronograma-contract.md`, `pytest.ini` (+7) |
| `tools/reachability_check.py` | check de ALCANCABILIDADE v0 (consolidacao part-6) | `tools/auto_check.py`, `tools/test_reachability.py` |
| `tools/recurate_cards.py` | o reescritor in-place CANONICO de flashcards | `.agents/workflows/curar-cards.md` (+4) |
| `tools/registrar_sessao_bulk.py` | — | `.agents/skills/source-command-importar-planilha/SKILL.md`, `.agents/skills/source-command-performance/SKILL.md` (+10) |
| `tools/review_radar.py` | Radar de dormência por TEMA | `.claude/settings.local.json`, `core/contracts/forgetting-curve-contract.md` (+2) |
| `tools/setup_hooks.py` | — | `tools/test_autonomia_hooks.py` |
| `tools/sync_skills.py` | gerador determinístico das skills agent-agnostic | `tools/auto_check.py` |
| `tools/variancia.py` | — | `.agents/skills/source-command-performance/SKILL.md`, `.claude/commands/performance.md` (+5) |

Migrações one-shot já aplicadas vivem em `tools/_archive/migrations/` -- não re-rodar.

---

## 8. Modelo de Memória (2 camadas)

```
┌──────────────────────────────────────────────────────────────┐
│ CAMADA 1 -- Canônica (repositório git)                        │
│  AGENTE.md · ESTADO.md · resumos/ · ipub.db                  │
│  Conteúdo clínico e estado do projeto. Fonte de verdade.     │
└──────────────────────────────────────────────────────────────┘
        ↑ lida no boot · atualizada ao fechar sessão
┌──────────────────────────────────────────────────────────────┐
│ CAMADA 3 -- Long-term (LangMem + SQLiteMemoryStore)           │
│  SQLiteMemoryStore -> medhub_memory.db::memory_store          │
│  Namespace: weak_areas (único -- tem writer E leitor)        │
└──────────────────────────────────────────────────────────────┘
```

**Governança:**
- Camada 3 captura padrões de fraqueza -- **não** replica `resumos/`, `ipub.db` ou `ESTADO.md`.
- `consolidate_session(NNN)` é chamada pelo hook `PostToolUse(Write)` quando um novo `history/session_NNN.md` é escrito. Usa `claude-haiku-4-5` se `ANTHROPIC_API_KEY` estiver presente; sem a chave, só o sync de `error_count` roda.
- `error_count` vem de `ipub.db` por match **exato** do par (area, tema); par sem correspondência fica em 0 -- nunca herda o total da área.
- Falha da consolidação (processo filho, detached) é registrada em `history/memory_errors.log`.

**Inspeção:** `python -m app.memory.inspect --{context,namespace medhub/weak_areas,dump,stats}`.
**Detalhes técnicos:** docstring de `app/memory/__init__.py` + `app/memory/schemas.py`.

---

## 9. O que ignorar

- `medhub-ui-refresh-main/` -- projeto React legado (já fora do tree atual; resíduo só em git history).
- `history/legacy/` -- sessões 001-028 referenciam artefatos retirados (`HANDOFF.md`, `caderno_erros.md`, `progresso.md`).
- `.venv/`, `__pycache__/`, `data/chroma/`, `artifacts/backups/`, `artifacts/llm_runs/` -- artefatos locais ou gitignored.
