# MEMÓRIA DA AUDITORIA — MedHub (F1→F81, ciclos, mecanismos, decisões) — 2026-09-08

> **O que é**: memória consolidada da auditoria de engenharia do MedHub, reconstruída de DOIS lados
> (registros do `/ai-eng` N=33→N=74 + o próprio repo `medhub`, read-only) porque os handoffs entre agentes
> foram apagados/arquivados e nenhum portador lido pelo boot carrega o ledger. **Portador**: cópia viva em
> `docs/MEMORIA-AUDITORIA.md` (medhub) com ponteiro de 1 linha no `HANDOFF.md` + citação no workflow de
> engenharia; snapshot datado em `ai-eng: brain/observed-systems/medhub-dossier-2026-09-08.md`.
> **Regras de manutenção**: (1) toda linha com número traz a data da medição; número sem data é claim que
> envelhece. (2) Fechamento de ciclo/hotfix atualiza a §3 (status) e a §2 (timeline) NA MESMA sessão, ou o
> dossiê vira o próprio F62. (3) O ledger detalhado continua sendo `AUDITORIA_MEDHUB.md` (drill-down);
> este arquivo é o índice que cabe numa leitura (<250 linhas). (4) Lápide (⚰️ data motivo) em vez de apagar.
> **Autoria**: Stanford AI Architect (Fable 5.1, sessão N=75) a partir de 2 colheitas Opus 5 (read-only) +
> 17 trocas do canal direto com a sessão medhub-18 (ledger `ai-eng: brain/observed-systems/exchange-log.jsonl`).
>
> 🔧 **Esta é a CÓPIA VIVA.** Divergências em relação ao snapshot do `/ai-eng` são deliberadas e estão marcadas
> in-loco. **Passe de verificação s171 (2026-09-08, medhub-18/Opus 5, HEAD `a9423d7`)**: §3 e §7 conferidas
> linha a linha contra o repo. Corrigidas: §1 contagem de status · §3 `SEM STATUS` 13→8 e `PARCIAL` 5+1→6+1
> (o bloco `Status F1-F9` do ledger não é alcançável por leitura de heading) · §7 **G2 e G4 meio-fechados**,
> **G6 fechado**, G5/G8/G10 re-medidos, G11 confirmado literal. **Acrescentados: G12 e G13** (achados novos
> desta passagem). §2, §4-§6 e §8-§10 não foram reverificados — ficam como o snapshot os deixou.

## 1. Estado em uma leitura (medido 2026-09-08)

| fato | valor | fonte |
|---|---|---|
| ids no ledger | **87** (F1–F85 + F77b + F79b) | `AUDITORIA_MEDHUB.md` 1518 ln (**F82-F85 numerados na s171**, `§6o`) |
| status escrito | 38 RESOLVIDO · **6+1 PARCIAL** (F7, F37-F41 + F57) · 12 ABERTO no cabeçalho · 7 ABERTO só em ESTADO/HANDOFF (F63-F69) · 2 ANTI-SCOPE (F55, F62) · 1 RECONCILIADO (F21) · **8 SEM STATUS** | §3 (remedido 09-08 por medhub-18) |
| commits desde 2026-06-01 | **262** · **129** `history/session_*.md` · s170 **SELADA** (9 commits, `session_170.md` presente, pushada até `a9423d7`) | `git log`, medido 09-08 pós-selo |
| suite | 317 (s160) → 358 (descolar 09-01) → 376 (s170 abertura) → **395** (após c4ce1db · d2026a1 · 06634b6, 09-08) | **re-medido no medhub 09-08: `395 passed em 16,68s`** |
| enforcement real | pre-commit `auto_check --staged` + suite pytest (check 2d BLOCKING) + schema do `ipub.db`; 2 BLOCK nominais (`HANDOFF_LONGO`, `SESSION_POINTER`) + 20 WARN | `auto_check.py`, matriz s160 `:1003` |
| boot lê | HANDOFF → ESTADO → reconcile → day_plan (hook) → workflow → último session → memória (hook) → RAG. **NÃO lê o ledger** | `AGENTE.md:45-54` |
| série gate-miss | F79 · F79b · F81 (conteúdo) + graphify/`reachability_check` (categoria) + fila-sem-estado/`avisos`/param-morto (tooling) | `AGENTE.md §10.8`; §5 |

## 2. Linha do tempo (ciclos; N = sessão do ai-eng, s = sessão do medhub)

| data | sessão | executor | entrega | achados | audit |
|---|---|---|---|---|---|
| 06-04 | N=33 | ai-eng | estudo dos contratos daktus→MedHub (4 contratos = ablação natural do padrão) | — | — |
| 06-17 | — | ai-eng | PRD F0 grounded-QA (FastAPI+Supabase) | **nunca adotado** (advisory superseded) | — |
| 06-23 | N=53 | ai-eng | scout de portfólio: reconcile modelo×realidade do medhub | — | — |
| 07-05 | s108 | estudo | ledger aberto | F1–F9 | — |
| 07-05 | N=63 · ciclo 1 | ai-eng | PRD `engenharia-ledger-f1-f13`, 5 ondas; pytest 13→36 | F10–F15 | 5/5 PASS |
| 07-05/06 | N=64 · ciclo 2 | ai-eng | `orquestracao-preparacao` (posição SSOT, recomendador, anti-reincidência) + expurgo F11 (git filter-repo) | F20, F27, F28; F22–F26 resolvidos | 4/4 PASS |
| 07-06/08 | s110-s113 | estudo | F29 (drift planilha-db) e F33 resolvidos ao vivo | F29–F34 | PASS |
| 07-09 | s115 | ai-eng | `boot-cronograma-drive-confiavel` (3 parts) | F30/F31/F34 | PASS |
| 07-12 | N=65 | ai-eng | auditoria M-OBS do RAG (3 das 4 dores = drift doc×código) + `mecanismo-conhecimento-consolidacao` | F21 reconciliado | 3/3 PASS |
| 07-12 | N=66 | ai-eng | auto-evolução: sensor `DOC_DRIFT` (check 7) · ledger-of-self · `plano_dia` · `--aderencia` · `reflect.py`; pytest 63→115 | — | 5/5 PASS |
| 07-19→08-24 | s124-s154 | estudo | registros retroativos; drenagem 90/100 cards | F35–F41 | — |
| 08-14/15 | N=71 | ai-eng | flashcards P0-P2 (fallback morto fail-loud · lock otimista · **card_checks nos writers** · calibração 68/68) + P3 (revlog c/ `card_version`+`selection_reason` · eventos flush pós-commit) + consolidação 1-7 (10 mortes · boot 272→56 palavras · `reachability_check` v0 91/91); pytest 182→278. Incidente: subagent apagou 180 PDFs → restauração 180/180 → **D63/D64** | — | 6/6 · 4/4 · 7 parts |
| 08-21 | N=73 | ai-eng | handoff de engenharia lote/5 (taxonomia canônica · spread · pré/pós-ENAMED), via courier | — | — |
| 08-30 | s159/s160 | estudo + ai-eng (read-only) | auditoria pura do motor (`docs/HANDOFF-AUDITORIA-MEDHUB.md`): 4 varreduras + matriz de portadores + swap test | F42–F44 · **F45–F60** | zero patch |
| 09-01 | N=74 · DESCOLAR | ai-eng (+Opus parts 6-7) | PRD `descolar-motor-determinismo` + 7 specs: painel DÍVIDA (F54) · allowlist writers (F49) · mortes F50/F51 + `IMPORT_DANGLING` · boot verdadeiro (F45-47) · contrato-verdade (B2 BLOCK, matriz v1.2, F52/53/56) · RAG sensores (F48) · exit codes (F60) · history-integrity (F58) · memórias nomeadas (F57) · deny/poda (F59); pytest 317→358 | F61; F45–F61 resolvidos | **PASS 7/7** |
| 09-02/05 | s162-s165 | Opus/Fable no medhub | veredito da des-colagem; camada de PREVALÊNCIA (89 temas) | F63–F69 | — |
| 09-05/07 | s166-s169 | Fable/Opus no medhub | README reescrito · 2 hotfixes · varredura drift D1-D12 · sprint 725q · substrato PubMed | F70–F80 (+F77b, F79b) | 2 traces hotfix |
| 09-08 | s170 ↔ N=75 | medhub-18 ↔ ai-eng (canal direto) | contrato `revisao-calibrada` v1.3 (PREPARAR revogado) · §10.6-10.8 · 3 auditorias por subagente (reforja · pool · graphify) → **hotfix reforja-sem-rastro (c4ce1db)** · **guarda ratchet do verso (d2026a1, 06634b6)**; pytest 376→395 | F81 + achados §5 | 2 audits PASS (ai-eng) |

## 3. Ledger F1→F81 por status (transcrito literalmente do cabeçalho; medido 2026-09-08)

| status | ids |
|---|---|
| **RESOLVIDO** (41) | F1 · F10–F15 · F22–F26 · F29–F31 · F33 · F34 · F43–F54 · F56 · F58–F61 · F70 · F73 · F74 · F79 · **F82 · F83 · F84** (s171) |
| **PARCIAL / causa-raiz** (6+1) | **F7 (heurística de competidor: WARN experimental, curadoria pendente — `:110-124`)** · F37 (dado histórico inflado: decisão do dono) · F38 (literal: `RESOLVIDO (s159) -- guarda entregue; 1 instância histórica a recuperar`) · F39 (detector ok; reforja 8/358) · F40/F41 (fila de reforja) · F57 (`RESOLVIDO-parcial`: 5 memórias nomeadas; 72 restantes) |
| **ABERTO — cabeçalho** (13) | F35 · F36 (ALTA) · F42 · F71 · F72 · F76 · F77 · F77b · F78 · F79b · F80 · F81 · **F85** (justificativa órfã, fecha no item 7) |
| **ABERTO — só ESTADO/HANDOFF** (7) | F63 (ALTA) · F64 · F65 (ALTA) · F66 (ALTA) · F67 · F68 · F69 — sem marcador no ledger |
| **ANTI-SCOPE** (2) | F55 (pre-commit `--staged` valida FS, não índice) · F62 (rotação do próprio ledger = política do dono) |
| **RECONCILIADO** (1) | F21 |
| **SEM STATUS ESCRITO** (8) | F16 · F17 · F18 · F19 · F20 · F27 · F28 · F32 |
| ~~SEM STATUS~~ -> **status escrito, fora do heading** (9) | 🔧 **correção 09-08:** F1-F9 têm status explícito no bloco `**Status F1-F9:**` (`AUDITORIA_MEDHUB.md:110-124`), que a leitura por heading não alcança: F1/F3/F4/F5/F6/F8/F9 = **ENTREGUE (p1..p5)** · F2 = **NÃO REPRODUZIDO (medido, p5) / ABERTO-DORMENTE** · F7 = **PARCIAL**. A nota original ("F3/F4/F6/F9 entregues por contrato, sem marcador") subestimava: o marcador existe, só não está no `###` |
| **contraditório** (1) | F75: cabeçalho "9 resolvidos/3 abertos", tabela = 10/2 (D5, D11 abertos) |
| ~~obsoletos sem lápide~~ | ⚰️ **FECHADO na s171.** F5 e F8 receberam lápide na redação acordada: *mecanismo **ENTREGUE** (p5 / p3) -> **objeto revogado** em `revisao-calibrada-contract.md` Cláusula 11 / `:74` (v1.3, s170)*. Corpo preservado como evidência histórica, não norma ativa |

⚰️ ~~Achados de hoje sem F-id~~ -> **NUMERADOS na s171** (`AUDITORIA_MEDHUB.md §6o`), fechando o G2: **F82** reforja-sem-rastro (`c4ce1db`, RESOLVIDO) · **F83** ratchet do verso (`d2026a1`, RESOLVIDO; sub-achado `permitir_atomicidade` **DEFERIDO** dentro dele) · **F84** fail-open dentro do próprio fix (`06634b6`, RESOLVIDO) · **F85** justificativa órfã `db.py:765` (**ABERTO**, fecha no item 7). Claims envelhecidos `db.py:9` e `fsrs_queue.py:9` são **Classe 2** dentro do F85 — documentação, sem teste. `get_topic_context.py:19` é lápide em pretérito: **não tocar**.

## 4. Mecanismos construídos (o que existe e quem o dispara)

| mecanismo | onde | severidade / gatilho | origem |
|---|---|---|---|
| suite pytest inteira | `auto_check.py` check 2d | 🔴 BLOCKING (pre-commit) | F44 (s159) |
| registro de suites (3 registros: `python_files` + auto_check + bridge) | check 14 `SUITES_ORFAS` + `test_suites_orfas.py` | WARN | F43 |
| ponteiro de sessão (só adiantado) | check 4 `SESSION_POINTER` | 🔴 BLOCK | F1 + F56 |
| HANDOFF ≤60 linhas | check 11 `HANDOFF_LONGO` | 🔴 BLOCK | consolidação p4 |
| sensor doc×código | check 7 `DOC_DRIFT` / `doc_drift.py` | WARN | N=66 |
| predicados de card (7 públicos; compara frente×verso, **nunca contexto×pergunta**) | `tools/card_checks.py` (212 ln) nos writers | erros/avisos por writer | N=71 |
| atomicidade (`LIMITE_CHARS=220`) + **ratchet de não-crescimento do verso** + telemetria len/frases | `audit_card_atomicity.py` · `recurate_cards.py` · `db.update_flashcard_fields` | check 9 WARN · ratchet = erro/RuntimeError | F39 · 09-08 |
| allowlist de writers (12 entradas; 7 escrevem `flashcards`) | `test_writer_allowlist.py` | teste | F49 |
| painel de DÍVIDA (leitor obrigatório do `ledger_self.jsonl`, 692 ln) | `auto_check.py:757` | imprime sempre | F54 |
| eventos append-only (`generation` · `reincidencia` · **`reforja`** com version antes/depois) | `tools/event_log.py` → `history/generation_log.jsonl` | flush pós-commit; nunca texto clínico | P3 · 09-08 |
| alcançabilidade (só `tools/*.py` + `app/**/*.py`) | `reachability_check.py` (289 ln) | WARN, só `--all` | N=71 (categoria declarativa fora: §5) |
| contratos (9 em `core/contracts/`) | reconcile-contract v1.2 (B2 BLOCK), fsrs v1.1, revisao-calibrada **v1.3** | frontmatter ≠ corpo em 2 (evidence-governance, revisao-calibrada) + 1 sem campo | s160 anexo |
| hooks do harness | `SessionStart` memory_boot · `PostToolUse` memory_session_log | — | `.claude/settings.json` |
| fila de reforja | `tools/cards_regen_queue.py` filtra `quality_source='heuristic'` (população aposentada na s075) | **cega ao passivo real**; passivo em prosa (12/13/15/38 conflitantes) | 1/3 de 09-08 |

## 5. Lições transferíveis (série gate-miss + Reachability-Debt)

> Âncoras do brain do ai-eng (para quem quiser a fonte, não obrigatórias para o medhub): medir o instrumento antes do resultado `[arxiv-benchmarking-tool-calling-evals]` · análise de erro dirige o próximo passo `[cs230-l6]` · fragilidade de loops de auto-melhoria (o fix que piora) `[arxiv-fragility-self-improving-agents]` · staleness por conteúdo, não por data `[arxiv-stagedworkspace]` · dado agent-ready é estruturado, não blob `[arxiv-umodel-observability]` · eval é gate de migração, não relatório `[web-agent-evals]` · definiteness: contrato diz o que NÃO cobre `[law-contracts-geis]`.

- **Gate-miss** (`AGENTE.md §10.8`): achado de leitura humana que um gate deveria pegar → fixture de regressão + contador. Taxonomia medida hoje: **conteúdo** (F79, F79b, F81: um caso fora do gate) · **tooling** (fila sem estado; predicado só em `avisos`; parâmetro morto) · **categoria** (`reachability_check` cego a tudo que não é Python: `.agents/rules` `always_on` sem leitor, `graphify-out/` 880k tokens sem consumidor, o próprio ledger fora do boot).
- **Reachability-Debt, 3 variantes** ("está correto?" ≠ "alguém chega aqui?"): (1) *lê o nada* — CLI mirando população vazia há ~95 sessões; (2) *ninguém lê* — artefato/categoria sem leitor mecânico; (3) *lê uma razão que já não existe* — justificativa órfã governando um `except` (discriminador: **a premissa está no caminho de decisão?** 1 de 4 ocorrências). Remédio: leitor mecânico ou morte (D63: arquivar ≠ resposta).
- **Claim-Aging** (extensão de D67, N=3 num dia, dois lados): "5 writers" (eram 7) · "python_files é o único registro" (são 3) · "atomicidade não bloqueia" (bloqueava via CLI). *Descrever um mecanismo exige ler o mecanismo atual, não o lembrado*; re-afirmar = re-medir.
- **Fix-Introduces-Defect** [MEDIUM]: reforja engorda o verso (v4: 46,8% com achado; 20/47 acima de 220 chars; confundidor de seleção declarado) → guarda ratchet + telemetria antes/depois; o número vira medição em poucas sessões.
- **Enforcement fail-open contradiz "aviso não existe"** dentro do próprio fix — pego em audit, corrigido no dia (06634b6). O gate que não pode rodar recusa a escrita.
- **Média mente**: pool state=0 tem 21,9% de achados vs 25,3% do rodado, mas é 2,0× pior no eixo A do F81 e 2,7× em contexto vazio; lote 600-799 = 20% do pool com 41,5% dos defeitos de frente (é o lote, não a época — contraprova 900-999).

## 6. Decisões que governam a coevolução (ai-eng; verificado_contra no `preference-signal.md`)

D53 corte-como-recomendação, completo-como-opção · **D54** tema do ciclo = dor do dono; severidade ordena dentro do tema ·
D55 verify-before-build (ledger+HANDOFF+código, nunca ROADMAP) · **D56** no irmão delegado o arquiteto executa design→spec→implement→audit ·
D57 claim de schema exige `PRAGMA` · D61 advisory = auto-relato + inspeção read-only profunda · **D62** canal direto agente↔agente (courier; agora mensagens + ledger) ·
**D63** auto-higiene no rito; obsoleto SAI; sem `archive/` · **D64** operação em massa = COUNT-ASSERT + dry-run + verificação pós-op no contrato ·
D65 sub-agent longo grava incremental · D66 ingestão termina com triagem por destinatário · **D67** número em canônico = medido na resposta (+ extensão 09-08: mecanismo) · D68 a ~80% da janela: self-handoff + subagents.
Do lado medhub (s170): §10.6 protocolo de achado com o /ai-eng (destilado ≤3k + remédio spec|hotfix|só-dado|nada → GO/NO-GO/ALTERA) · §10.7 COUNT-ASSERT · §10.8 série gate-miss · política "regra nova nasce WARN, vira BLOCK quando a base zerar" (`AGENTE.md:167`).

## 7. Inconsistências medidas em 2026-09-08 (memória que o próprio repo contradiz)

| # | achado | fonte |
|---|---|---|
| G1 | ledger (179 KB) fora do boot; 1 menção em AGENTE §10.1, 0 em HANDOFF/ESTADO; cresce sem rotação (F62 anti-scope) | `AGENTE.md:45-54` |
| G2 | ⚰️ **FECHADO (s171).** Citação pendurada resolvida em `d9ecbbe`; **F-ids escritos**: `c4ce1db`=**F82**, `d2026a1`=**F83**, `06634b6`=**F84**, `db.py:765`=**F85** | `AUDITORIA_MEDHUB.md §6o` |
| G3 | F75 cabeçalho 9/3 × tabela 10/2 (consumidores ESTADO/HANDOFF seguem a tabela) | `:1385` vs `:1389-1401` |
| G4 | **METADE FECHADA (09-08, `64a8a9a`).** A auto-contradição 970/1.353 × 903/1.213 **morreu**: *Volume & Metas* e *Erros & Cards* agora dizem "ver acima -- **fonte unica no arquivo** (G4, s170)". **Permanece:** F64, F35, F36, F42 fora da lista de abertos do HANDOFF (**14 de 19 viajam**; F81 citado à parte como "novo", não na lista). **Novo:** o cabeçalho do `ESTADO.md` ainda carimba **s166 / 2026-09-06** enquanto o corpo carrega edições da s170 — o arquivo foi editado sem re-carimbar | `ESTADO.md:10,33,42`; `HANDOFF.md:42` |
| G5 | **DE PÉ, instância trocada (09-08).** `audit_fsrs.py` e `calibrate_card_checks.py` **já estão** na tabela — esse par envelheceu. Medição de hoje: `reachability_check --tabela` = **42 linhas**, `AGENTE.md` = **41**; o ausente é **`tools/exchange_log.py`** (nascido na s170, `3b034a5`). A tabela gerada volta a ficar stale a cada CLI novo — é a classe, não o par | `AGENTE.md:214`; diff contra `--tabela` |
| G6 | ⚰️ **FECHADO (09-08, antes do reinício).** `history/session_170.md` existe (9.490 B, 20:13) e o `HANDOFF.md` está rotacionado para s170. **A causa mecânica permanece aberta:** `SESSION_POINTER` só pega ponteiro adiantado, não atrasado — G6 fechou por disciplina humana, não por gate | `history/session_170.md`; `HANDOFF.md:2` |
| G7 | passivo de reforja: 12 / 13 / 15 / 38 (com duplicata #1424) — nenhuma cifra vive numa fila mecânica; #321 em v2 com o defeito intacto | `HANDOFF.md:41`, `session_167.md:17`, `:1409` |
| G8 | `memory_errors.log` 7 → 505 → **630** linhas (F66 aberto: o número mede execuções do sensor, não dívida); `ledger_self.jsonl` 462 → 692 → **694**; ledger **179.476 B = 175 KiB** (o painel arredonda para "175 KB" — mesma medida). **Os três se moveram dentro do mesmo dia** — é o caso-exemplo da regra de manutenção (1): número sem data é claim que envelhece | `wc -l`, medido 09-08 pós-`a9423d7` |
| G9 | ⚰️ **FECHADO (s171).** Lápides em `AUDITORIA_MEDHUB.md:68` e `:91`, na redação *ENTREGUE (pN) -> objeto revogado em `<contrato>`* | `AUDITORIA_MEDHUB.md:68,91` |
| G10 | **DE PÉ.** Suite real medida hoje: **395 passed em 16,68s**. `README.md:18` e `:191` seguem dizendo **365**; `ESTADO.md:46` cita a série 317->358 (histórico legítimo). `ESTADO.md:64` continua apontando `tools/autopsia_template.py` como "modelo canônico" — `ls tools/autopsia*.py` = **No such file**. 🔴 **Gate-miss de categoria (§10.8):** o check `MEMORY_POINTERS` (F57) acusa **exatamente esses dois paths** — mas só porque estão citados em `memory/*.md`; a citação idêntica dentro do `ESTADO.md` **nenhum gate vê**. O sensor existe e o alcance dele para na fronteira do diretório | `pytest tools/ -q`; `auto_check --all`; README, ESTADO |
| G11 | **CONFIRMADO literalmente (09-08).** `evidence-governance` frontmatter `1.0` × changelog `v1.1 (2026-09-07)`; `revisao-calibrada` frontmatter `1.0` × título **"Versão 1.3"**; `orquestracao-contract` sem campo `version`. Os outros 6 batem | `core/contracts/` |
| **G12** 🆕 | 🔴 **`revisao-calibrada-contract.md` v1.3 contradiz a si mesmo.** A **Cláusula 11** (`:146`) mata o PREPARAR e declara que cluster frio (F5) "deixa de disparar aquecimento"; a **Cláusula 5b** (`:130`) **sobreviveu intacta** mandando o DRENAR "**oferecer** o PREPARAR proativamente" com limiar `>=25`. 5b é lida **antes** de 11. Mesma classe do G4 — dentro do contrato que a s170 acabou de reescrever, e no arquivo que o G11 já acusa | `core/contracts/revisao-calibrada-contract.md:130` vs `:146` |
| **G13** 🆕 | `ESTADO.md:60` ("Abertura da próxima") ainda prescreve "Aula-base + **refresh Camada 0** antes de cada bloco". A Camada 0 foi revogada na v1.3. Menor que o G12 (prosa de plano, não cláusula normativa), mesma família | `ESTADO.md:60` |

## 8. Lacunas do lado ai-eng (para o dossiê não fingir simetria)

- F61–F80 não têm espelho nenhum nos registros do ai-eng (só chegam aqui por este dossiê); vão de **33 dias** (07-12→08-14) sem observação; ciclo-3 `pipeline-conhecimento` (F16-F19) e o handoff de integridade nunca reconciliados.
- `AUDITORIA_MEDHUB.md`, PRDs/specs/audits dos ciclos e `descolar-motor-cycle-audit.md` **não existem no disco do ai-eng** — o ledger F só chega por citação; `advisory-ledger.md` não indexa os 8 ciclos; `portfolio.md` marca `last_observed: 2026-06-23`.
- Âncoras `arquivo:linha` de F45–F60 foram medidas no HEAD `9e3785a` (30/08); o `descolar` mexeu em 15 dos 16 arquivos — provavelmente não valem mais.
- O ai-eng tem a mesma doença: 67 de 192 artefatos declarativos sem leitor mecânico nem de contrato (`.vibeflow/` 36/37; `.codex/` sem hooks; 12/17 da quarentena; 12/13 das expansion-proposals) — varredura 09-08.

## 9. Fila do operador (decisões empilhadas; ninguém decide por ele)

1. **Apagão do graphify** (`graphify-out/` + `.agents/rules|workflows/graphify.md`; skill global fica) — só após a fixture sintética do check de alcançabilidade declarativa estar verde (§5 categoria) e §10.4 grep.
2. **Reforja dirigida do lote 600-799** (132 cards; state=0, fora da rotação) — dry-run + COUNT-ASSERT §10.7; guarda ratchet já existe; gatilho nominal, conteúdo clínico é do dono.
3. **Contexto obrigatório em card novo?** (49% do pool com `frente_contexto` vazio) — decide se o gate de seleção 0→1 trata contexto vazio como WARN (hoje) ou BLOCK; eixo A (containment ≥0,70) = BLOCK.
4. **F62** rotação do ledger (179 KB) — política do dono; este dossiê é o índice, não a rotação. **F55** pre-commit `--staged`. **F37** dado histórico inflado.
5. Spec **F81** (+ predicado "pergunta genérica" só em conjunção com contexto pobre; 7 writers; contador de gate-miss) e spec **fila de reforja como estado** (`reforja_marks` com lifecycle; prosa vira derivada do painel) — GO dado pelo ai-eng em 09-08, aguardam a fila do operador.

## 10. Ponteiros (drill-down)

`AUDITORIA_MEDHUB.md` (ledger) · `docs/HANDOFF-AUDITORIA-MEDHUB.md` (auditoria s160) · `.vibeflow/audits/descolar-motor-cycle-audit.md` (PASS 7/7) ·
`.vibeflow/hotfixes/2026-09-08-reforja-sem-rastro.md` · `tools/test_reforja_event_log.py` · `tools/test_ratchet_verso.py` · `history/INDEX.md` ·
ai-eng: `brain/observability/sessions/2026-07-05-medhub-vibeflow-cycle.md` … `2026-09-01-descolagem-pericia-medhub.md` · `brain/observed-systems/exchange-log.jsonl` (17 trocas de 09-08, texto integral) ·
`brain/feedback/preference-signal.md` (D53–D68) · `HANDOFF-MEDHUB-COLA.md` (dossiê s160, consumido).
