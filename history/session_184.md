# Session 184 -- Absorcao das transcricoes de estudo + fundamentos pedagogicos nomeados + fila de reformas (sessao de PLANEJAMENTO)
**Data:** 2026-09-17 (18h45 -> noite)
**Ferramenta:** Claude Code / Fable 5.1 (principal) + 4 subagentes de varredura ISOLADOS (Opus x1, Sonnet x3) + 3 extratores graphify (Sonnet)
**Continuidade:** Sessao 183 (hibrido aprovado; player provado)
**Tipo:** ABSORCAO + PLANEJAMENTO (zero questoes, zero cards, zero reforma -- decisao do usuario)

---

## 0. O que o usuario trouxe

1. Duas transcricoes de J.R. Smith (Mayo Clinic, ortopedia): *"The Study System That Made Me A Doctor At The World's Top Hospital"* (Learn -> Retain -> Apply; Anki de manha; efeito de teste; simplicidade) e *"I NEVER Take Notes Anymore -- My Full AI System As A Doctor"* (captura -> resumo -> organizacao por IA; um documento vivo por tema; **friccao viciosa x virtuosa**). Pedido: *"absorver... para reforcar nossa arquitetura de ensino e aprendizagem"*.
2. Autorizacao de WebSearch **via subagentes isolados, lendo so o processamento deles** (prompt injection) -- regra nova, memoria `feedback_web_aberta_subagente_isolado`.
3. Pedido de checar o GitHub `open-spaced-repetition` e de usar `/graphify` para amarrar o contexto logico do MedHub.
4. Fechamento de escopo: *"Sintetize todos os achados em um documento na sua pasta raiz. Nao teremos condicoes de utilizar essa sessao para reformas, portanto esta e uma sessao de planejamento."*

## 1. O que foi feito

### 1.1 Mapa principio x mecanismo (principal)
- Leitura dos portadores de ensino (AGENTE §1.2/§6, `revisao-calibrada` v1.4, `fsrs-management` v1.3, `forgetting-curve`, `orquestracao`, `revisar.md`, `estilo-flashcard.md`, `analisar-questao.md`, `aula-base.md`, PLAYBOOK, ledger, MEMORIA-AUDITORIA) e mapeamento das afirmacoes dos dois videos a **17 principios** (P1-P17), cada um com estado CONFIRMA / TENSAO / LACUNA e a medida interna que o sustenta. Resultado: **14 CONFIRMA**; **F109** (premissa "cluster e pedagogicamente superior" errada; default intercalado certo), **F110** (friccoes virtuosas sem portador), **F111** (Fase 2 leitura-first sem recall no dia), **F112** (semantica das notas).
- **Ledger de friccoes** (secao 3 do FUNDAMENTOS): V1-V11 protegidas (recall antes do verso, recall a frio, nota honesta, relearning ate 4, racional declarado, ritual de prova, triagem humana, flip obrigatorio, questoes antes da aula em D5-, ensino so no fechamento, ler a Autopsia) x X1-X8 automatizadas (digitar erros, montar fila, virar card no chat, achar trecho, escrever resumo/Autopsia, numeros de estado, verificar fonte, servir card por id). Regra de decisao: *"o que de PROCESSAMENTO do aluno sai junto?"*.

### 1.2 Quatro varreduras de web aberta (subagentes isolados; relatorios em `docs/research/2026-09-17-0N-*.md`)
- **1 -- ciencia da aprendizagem (Opus, 178k tokens, 16 min, 31 buscas):** 13/13 itens com fonte primaria. Confirmados: Kornell 2009 (90% / 72%); intercalacao em ECG 46% x 30% (Hatala 2003, PMID 12652166) e radiografia 57% x 43%; R&K 2006 (61% x 40%, d = 1,26); Dunlosky 2013 (tabela literal); productive failure d = 0,36 (Sinha & Kapur 2021, meta-analise); successive relearning >60% x <20% em 24 dias; Deng 2015 (questoes e cards preditores INDEPENDENTES; deck pronto nao prediz; **Step 2 CK sem beneficio de Anki**); answer changing 51% errada->certa x 25%; anotar a mao = replicacoes nulas. **10 afirmacoes dos videos marcadas SUPERESTIMADAS** ("70% em 24h" = savings 0,33 em silabas, n = 1; Custers 2010: 2/3 a 3/4 retidos em 1 ano em medicina).
- **2 -- agentes de IA e offloading (Sonnet, 155k, 14 min, 25 buscas):** Bastani et al. 2025, PNAS (N ~ 1.000): IA sem guardrail **+48% na pratica / -17% na prova**; guardrail socratico +127% / 0. Bisra 2018: autoexplicacao g = 0,55. Graber 2005 (fechamento prematuro = erro nº 1) mas **Sherbino 2014 RCT nulo** para ensinar vies. Metcalfe 2017 (hypercorrection). BKT/DKT/HLR/FSRS: nenhum modela esquecimento por TEMA. Khanmigo e taxa de erro de flashcard-LLM = NAO VERIFICADO.
- **3 -- engenharia de agentes (Sonnet, 161k, 12 min, 34 buscas):** Anthropic/Cognition convergem ("fan-out so leitura; escrita single-threaded" = "eu orquestro, subagentes varrem"); ADR/living docs; **falta gatilho algoritmico de consolidacao de memoria**; **conflito agente autor = agente avaliador** nao coberto pela literatura de automation bias; N-of-1 (Kravitz & Duan 2014); Bloom "2 sigma" contestado (g ~ 0,70); COUNT-ASSERT e nomenclatura local.
- **4 -- open-spaced-repetition (Sonnet, 124k, 7 min, 30 buscas):** `fsrs` 6.3.2 = FSRS-6; `Optimizer(review_logs).compute_optimal_parameters()`; minimo 400-1.000 revisoes (MedHub tem 2.981, folga 3-7x, roda DEFAULT); `compute_optimal_retention` (CMRR); `learning_steps=()` gradua direto; **Again e o unico lapso; "Hard" nunca para erro parcial**; leech e do Anki, nao do algoritmo.

### 1.3 Medicao read-only no `ipub.db` (F112)
- `file:ipub.db?mode=ro`; `fsrs_revlog` = 2.981 (563x1 / 338x2 / 528x3 / 1.552x4). Com `state=2`: nota 1 -> 1,0 dia; **nota 2 -> 14,2 dias (312)**; nota 3 -> 16,7; **nota 4 -> 34,3 dias (1.551 = 52%)**. Conferido no codigo instalado: `Scheduler.review_card`, ramo `State.Review`, `case Rating.Hard | Rating.Good | Rating.Easy` = caminho de acerto; adaptador `app/utils/fsrs.py` passa `Rating(rating)` direto e so conta lapse em 1. `revisar.md` passo 4 define 2 = "recall parcial sem o alvo". Achado **ALTA**, remedio = spec (toca `record_review`).

### 1.4 `graphify --update` escopado
- Deteccao incremental: 683 arquivos mudados desde 30/08 (104 codigo, 579 docs; 3 deletados). Re-extrair 579 docs custaria milhoes de tokens: escopo restrito a **43 portadores de governanca/ensino** (raiz, docs, workflows, contratos, skills, `session_170-183`) em 3 extratores Sonnet; **104 arquivos de codigo pelo AST** (gratis: 1.755 nos, 3.732 arestas); 536 docs mudados ficam **pendentes no manifesto** por desenho (`clear_semantic`), nao carimbados.
- **Resultado:** grafo **1.940 -> 3.383 nos, 3.374 -> 5.993 arestas, 178 -> 253 comunidades**; 97% EXTRACTED; saude OK (0 dangling/missing/self-loop). 70 comunidades rotuladas a mao, 183 finas pelo no de maior grau. `graph.html` (3,1 MB) e `GRAPH_REPORT.md` regenerados; cost.json corrigido com os tokens reais dos extratores.
- **Amarracao do contexto logico:** os 31 nos do `FUNDAMENTOS` entraram como arestas `implements` para os mecanismos (P9 -> estilo-flashcard + audit_card_atomicity; P12 -> aula-base; P4 -> /revisar; P5 -> gatilho hibrido + F100; P3 -> fsrs_balance; P6 -> fsrs_queue; P11 -> contrato FSRS; F109 -> F3), com centro de gravidade na comunidade "Revisao Calibrada - contrato v1.3". Pontes: `Skill: Revisar` (betweenness 0,078 -- onde o F112 vive), evidence-governance (0,053), Session 183 (0,052). God nodes: `get_connection()` 67, Session 183 47, `SQLiteMemoryStore` 34, AGENTE 27. Lacuna apontada: 191 nos fracos, incluindo `DORMENTE_DIAS = 21` e `REPETITION_WINDOW_DAYS` (constantes da curva por tema citadas por um portador so).

### 1.5 Portadores criados/atualizados
- `docs/FUNDAMENTOS-APRENDIZAGEM.md` (novo; explicativo, nao normativo; P1-P17, ledger de friccoes, 6 secoes de fontes com forca de evidencia).
- `PLANEJAMENTO-APRENDIZAGEM-2026-09-17.md` (raiz; sintese de todos os achados + fila R1-R11 + custos).
- `AUDITORIA_MEDHUB.md §6y`: F108 (registro pendente da s183), F109, F110, F111, F112 + lapide no F3.
- `AGENTE.md §6` (1 bullet-ponteiro), `README.md` (linha do `docs/`), `docs/research/` (4 relatorios crus, 180 KB).
- Memoria: `project_fundamentos_aprendizagem`, `feedback_web_aberta_subagente_isolado`; `MEMORY.md` compactado de 19,8 KB para 12,9 KB (hook de tamanho).
- `auto_check --changed`: **PASSED** (WARNs herdados F38/F89, nenhum novo). Nenhum contrato, skill ou codigo tocado.

## 2. Decisoes tomadas (usuario, 17/09/2026)
- Web aberta = subagentes isolados; principal le so o destilado.
- Sessao de **planejamento**: nada de reforma; sintese em documento na raiz.
- `open-spaced-repetition` e `/graphify` como insumos.

## 3. Achados para o ledger (todos registrados em §6y)
- **F108** registrado (extrator regex; corpus v2 no scratch; regra vai para o CLI Medcards E2).
- **F109** premissa do cluster x intercalacao (so-dado + riders R3).
- **F110** friccoes virtuosas sem portador (portador criado; gate impossivel, declarado; R6).
- **F111** Fase 2 sem recall no dia (decisao do operador; R8; prazo 02/11).
- **F112** regua de notas deslocada vs. FSRS (ALTA; R1 read-only -> R2 decisao -> spec).

## 4. Artefatos criados/modificados
`docs/FUNDAMENTOS-APRENDIZAGEM.md` · `PLANEJAMENTO-APRENDIZAGEM-2026-09-17.md` · `AUDITORIA_MEDHUB.md` · `AGENTE.md` · `README.md` · `docs/research/2026-09-17-0{1,2,3,4}-*.md` · `graphify-out/` (graph.json, GRAPH_REPORT.md, graph.html, manifest.json, cost.json) · `HANDOFF.md` · `ESTADO.md` · `history/INDEX.md` · este log. Nada escrito em `ipub.db`, `resumos/`, `core/contracts/`, `.claude/commands/`, `tools/`.

## 5. Custo dos subagentes (F93, clausula 10)
Varredura 1 Opus 178.290 tokens / 16 min · Varredura 2 Sonnet 154.674 / 14 min · Varredura 3 Sonnet 161.177 / 12 min · Varredura 4 Sonnet 123.522 / 7 min = **617.663 tokens, ~49 min de filho, ~23 min de relogio (3 em paralelo + 1)**. Extratores graphify (Sonnet): chunk 1 477.932 / 30 min · chunk 2 262.134 / 21 min · chunk 3 269.827 / 24 min = **~1,01M tokens, ~75 min de filho, ~30 de relogio**. **Total da sessao: 7 spawns, ~1,63M tokens.** Zero sub-delegacao; zero escrita fora do scratch; numeros load-bearing re-medidos pelo principal: rating semantics (codigo instalado + revlog), Kornell 90%/72% (abstract), Bastani +48%/-17% (PNAS), py-fsrs Optimizer (pacote 6.3.2 no `.venv`).

## 6. Proximos passos
- **Proximo ato de estudo:** lote do player (regime de divida: 115 vencidos, teto 90) e `/aula-base` D10 de Acido-Base + Potassio antes de re-drillar #787/#597.
- **Fila de engenharia (GO do `/ai-eng`):** R1 -> R3+R4+R5+R6 -> R2 -> R7 -> R8 (antes de 02/11) -> R9 -> R10 -> R11; mais F107 e F99. Detalhe: `PLANEJAMENTO-APRENDIZAGEM-2026-09-17.md §5`.
- Inscricao UERJ ate 01/10.
