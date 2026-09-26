# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-26 (~14h local) -- **s200 (Opus 5.5)**: as 2 primeiras listas resolvidas NA ABA do hub (t96 Pediatria 13/18, t26 DMG 17/19; 7 erros + 3 incertezas registrados, cards #1749-1756). **Solucao MedHub v2 = CADEIA de elos** (pede + cadeia `{elo, chave}` + cada alternativa errada aponta o elo em que cai + `objetivo` de lista fechada por tema; brief `docs/SOLUCAO-MEDHUB-BRIEF.md`) em t26 t40 t49 t96; **riscadas** gravadas e lidas (`--erros` Leitura); `--status --por-objetivo` = mapa de fragilidade; aba **Listas** agrupada por semana do plano. Card nasce do elo que quebrou.*
> 🏠 **MedHub HUB (1 artifact, fixado): https://claude.ai/artifact/3RksMfkzNWYSQD7D6JXNEr** -- abas Painel / Aulas / Cards / **Listas** (Version 28). Republicar SEMPRE nesta URL (rito: `/hub-backend`, `/revisar` "DRENAR no player", `registrar-sessao` §6); `artifact-deleted` = recriar completo (capabilities de 3 regras, abaixo) e REPORTAR aqui. **Lote vivo `2026-09-26b`** = colecao `sessoes/2026-09-26b/notas` (51 cards, 11 ja gravados na s200, vespera exportada 25/09 ~21h depois da revisao de portugues; o `2026-09-26a` (56) ele ja drenou na noite de 25/09). (o `sessao` nao e a data de hoje; trocou o lote, troca aqui). Colecoes `2026-09-22h` (220) e `2026-09-24a` (90) PODADAS no fechamento (releitura = 0 novas nas duas). Aulas Pediatria e DMG ja em TOPICOS; ele vai trazer o feedback.

> 🗄️ **Bancada EMED https://claude.ai/artifact/Q2Cojm89D9JwRyBYmCD5Db** = so a FILA de listas (status `pendente/em_curso/capturada`); desde a s199 a captura e do Claude Code dirigindo o Chrome (o executor da extensao saiu do fluxo). 🔒 Conteudo EMED so no `ipub.db` e nas colecoes `read admin` do hub; nunca no git.

> 🔒 **O SELO:** `python tools/selo.py` -- tabela DERIVADA, nunca digitada. Ledger ate **F132** (F130/F131/F132 RESOLVIDOS na s195; F129 PARCIAL; F127/F128 DECLARADOS); 2 GATE do operador seguem (F87, F111).

> 🔴 **ABRIR A s201 POR AQUI:** (0) **VEREDITO DO /ai-eng sobre os 9 achados da s200 (autoauditoria no fim de `history/session_200.md`) = 1o item:** ler a resposta dele no canal/`history/exchange-log.jsonl`; 1, 7 e 9 sao so-dado; **2-6 e 8 NAO tem GO por silencio** (auditoria explicita pedida pelo operador) -- sem o veredito, nao implementar. t96 Q8 (elo 1 `nao_usou` x 'acertei o 1') = bifurcacao do operador. (a) **proxima lista = t49 Hernias (21q) ou t40 DMG (33q)**, ambas ja em v2 no hub; quando ele resolver: `ArtifactData list respostas` -> `--registrar --apply` -> `registrar_sessao_bulk` -> `plano.py --concluir` -> `--erros LISTA` (traz a Leitura das riscadas e a cadeia) -> racional declarado ANTES do diagnostico -> `insert_questao --errors-file` (`--sessao`/`--emed`) -> `analises/*` com `quebrou` 0-based na cadeia da solucao, SEM repetir a cadeia -> `listas/<id>` status resolvida; (b) **re-cunhar em v2 a lista que entrar na vez** (8 ainda v1: t1 t65 t68 t100 t3 t61 t651 t141; t61/t65 = lista de hernias, t100 = puericultura; tema novo = definir a lista fechada no brief ANTES do subagente); (c) t40 Q5/Q6/Q18/Q21/Q22 sem tabela na captura; (d) herdado da s199: captura PAUSADA (incidente do clique na t65) e gabaritos suspeitos t100 Q8, t68 Q13, t1 Q21, t65 Q18.

## > Proximo passo imediato

1. 🗄️ **Banco EMED (s200):** 12 listas no hub; **resolvidas: t96, t26**; em v2 (cadeia): t26 t40 t49 t96. Mapa de fragilidade: `emed_banco.py --status --por-objetivo` (DMG: criterio diagnostico 10/10; DM previo x DMG 3/4; vigilancia fetal 0/1). Divergentes a conferir no professor: t49 Q10/Q20 · t68 Q1/Q13 · t100 Q8/Q18/Q29/Q34 · t61 Q11 · t651 Q20. Sem resumo local de Hernias (4 listas no plano). `questoes_erros.o_que_faltou` do erro 1092 ficou com a inferencia antiga (sem CLI de correcao). PRD `.vibeflow/prds/banco-questoes-emed.md`.
2. 📊 **Aba Analise do hub:** PRD `.vibeflow/prds/hub-aba-analise.md` -- a cadeia v2 + `analises/*` + `--por-objetivo` ja sao o insumo (mapa de fragilidade por objetivo, acumulado entre listas). gen-spec -> implementar.
3. 📚 **Estudo:** #26 e #96 FEITAS na s200; proximas da semana 2 (fecha 27/09): #49 Hernias, #40 DMG, #100 Pediatria; fim de semana = **UERJ 2021** (60q). Aula #877 pronta no hub.
4. 🃏 **Cards:** fila `2026-09-26b` (51, 11 gravados na s200) no ar; cards novos #1749-1756 entram pela fila. Marcas humanas abertas = 0. Duvidas clinicas da reforja em `tmp/reforja_s196/duvidas_*.json` e na s196 (#1113, #1176, #373, #65, #55) -> `/pesquisar-evidencia` quando houver folga. Resumo `[GIN] CA de Mama.md` ainda diz supraclavicular ipsilateral = estadio IV (errado; AJCC 8 = N3c).
5. 📊 **Ritmo e o alarme real:** 17,9 q/dia (7d) x 79,7 necessarios ate 01/11. Cobertura > refinamento.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (**inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7488 / 10400 (perf. ~78.8%). Hoje: 37. Ritmo do marco de volume ~80.9q/dia (36d p/ UERJ/MFC (prova 01/11)).
- **Simulados:** 10 provas + ENAMED real 75. **UERJ 2023 = 58** (solidas 44/60). Sequencia: ~~2023~~ -> 2021 -> 2022 -> 2024 -> 2025 -> 2026.
- **FSRS:** divida 2 atrasados + 30 p/ hoje -- pool 717 nunca introduzidos (entram <=100/dia).
- **Conteudo:** 135 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 1094 erros registrados · 1589 cards ativos · 0 needs_qualitative na fila · taxonomia 320 temas. [derivado: db]
- **Cronograma:** `plano_tarefas` = SSOT; Fase 1 GERADA por `tools/trilha.py`. #38 Hernias FEITA (sb 131, 25q/21). 🔴 A linha "Posicao" do `--handoff-block` ainda diz "semana 1" (semana por POSICAO no plano, o defeito que a auditoria achou no painel e que o painel V4 ja corrigiu); a semana de calendario e a **S2** (21-27/09) -- `plano.py --panorama` manda.
- **Posicao:** plano semana 1 (fase 1) · 4/5 tarefas da semana feitas · cota ~237q/dia ate 27/09 · Fase 1 ~88.3q/dia [derivado: plano_tarefas] -- a semana de calendario e a S2 (`plano.py --panorama` manda)
- **Engenharia:** suite **1120** (s200); Solucao v2 em cadeia + `objetivo` + `riscadas` (`db.solucao_v2_problemas`, `--por-objetivo`, `leitura_metacognitiva`); teto 100/150 (`day_plan.TETO_BASE`); **Bancada EMED v2 + `emed_banco.py` + `/banco-emed`** (s197); hub V4 (painel pelo leitor do panorama, quadro `core/hub_quadro.json`, `hub.py --precisa-publicar`, timer ativo, tela de fim com agenda); `/hub-backend` + `plano.py --concluir --leitura`.
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** · 🩻 Raio-X UERJ (foto de 18/09): https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc

## Ultima sessao -- s200 (2026-09-26, sabado) -- listas resolvidas no hub, Solucao em cadeia de elos, objetivo e riscadas

Detalhe e custo em `history/session_200.md`. Commits `2e56694` (banca/tema, mediana), `da62e95` (cadeia v2, objetivo, riscadas, aba Listas, semanas), `e1843ab` (Elo N explicito, botao contextual), `3a4540a` (**estado de cada elo = diagnostico**, `analises.estados`: ok/quebrou/nao_usou/nao_avaliado; letras = evidencia -- correcao de modelo DELE). Racional da t96 fechado; report ao /ai-eng enviado no fechamento (autoauditoria em `history/session_200.md`). Operador aprovou a cadeia e os objetivos ("era exatamente isso"; "o refino na cadeia ... fundamental para refinar inclusive os cards"). Custo: 8 subagentes, ~1,15M tokens; a v1 das solucoes (642k) foi superada pela v2 (440k) no mesmo dia.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- 🔴 **Backend so vale com PC acordado e sessao aberta;** latencia = intervalo do `/loop`. Tique barrado pelo classificador ou pedindo aprovacao = para e relata, nunca contorna. Nunca testado ainda em `/loop` real (so 1 tique a mao).
- 🔴 **O mapa UERJ erra rotulo (F128)**; recalibrar a trilha so pelo acerto ACUMULADO, a partir da 3a prova UERJ (regra do `/ai-eng`, s189).
- **F113 PARCIAL** (+ F129), **F110** sem gate, **F78**/**F2** DECLARADOS. Pasta travada `.claude/worktrees/agent-acda9b545d40f697d` (sobra da s194; o `reachability_check` ja a ignora) -- remover so com OK dele (`git worktree remove --force`). Patch do botao em `tmp/patch_s194_pedido_cards.diff` (fora do git).
- 🏠 **O owner passa por cima das regras do `db`** (conta compartilhada): a fronteira real e o writer. Poda de `sessoes/2026-09-22h` (220 docs) pendente: releitura = 0 novas, 0 quarentena -> pode podar no proximo fechamento de cards.

## Pendencias/observacoes ativas

- 🔴 **Instrucao para o OPERADOR fora das 8 primeiras linhas deste arquivo nao e instrucao, e arquivo.**
- 🔴 **Commit com subagente em paralelo:** `git add` so dos proprios paths; commit barrado -> `git restore --staged` so dos seus (s194: um filho levou o log da sessao junto no commit dele).
- 🔴 **Brief de subagente com conteudo clinico se escreve COM acentos**; regex sempre em string RAW; patch longo = arquivo no scratchpad.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_194.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md * Selo: `python tools/selo.py`*
