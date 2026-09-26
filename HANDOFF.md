# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-26 (~07h local) -- **s199 (Opus 5.5)**: o banco de questoes virou fluxo. **Claude Code dirigindo o Chrome** = caminho padrao da captura (subagente Sonnet por lista, escopo publico, JSON local em `tmp/chrome/questoes/` -> `emed_banco.py --ingerir`); **Solucao MedHub** propria por lista (subagente Opus, sem o comentario do professor; `emed_solucoes`, `--solucoes`, bloco na aba Questoes com "conferir no professor"); **elo erro -> card** (`insert_questao --sessao/--emed`); **hub semeado com 10 listas** (t26 t96 t40 t49 t68 t100 t3 t61 t651 t141, 418/5000 docs) e publicado (Version 22). API interna do EMED recusada. Captura custa ~16-22k tokens/questao.*
> 🏠 **MedHub HUB (1 artifact, fixado): https://claude.ai/artifact/3RksMfkzNWYSQD7D6JXNEr** -- abas Painel / Aulas / Cards. Republicar SEMPRE nesta URL (rito: `/hub-backend`, `/revisar` "DRENAR no player", `registrar-sessao` §6); `artifact-deleted` = recriar completo (capabilities de 3 regras, abaixo) e REPORTAR aqui. **Lote vivo `2026-09-26b`** = colecao `sessoes/2026-09-26b/notas` (51 cards, vespera exportada 25/09 ~21h depois da revisao de portugues; o `2026-09-26a` (56) ele ja drenou na noite de 25/09). (o `sessao` nao e a data de hoje; trocou o lote, troca aqui). Colecoes `2026-09-22h` (220) e `2026-09-24a` (90) PODADAS no fechamento (releitura = 0 novas nas duas). Aulas Pediatria e DMG ja em TOPICOS; ele vai trazer o feedback.

> 🗄️ **Bancada EMED https://claude.ai/artifact/Q2Cojm89D9JwRyBYmCD5Db** = so a FILA de listas (status `pendente/em_curso/capturada`); desde a s199 a captura e do Claude Code dirigindo o Chrome (o executor da extensao saiu do fluxo). 🔒 Conteudo EMED so no `ipub.db` e nas colecoes `read admin` do hub; nunca no git.

> 🔒 **O SELO:** `python tools/selo.py` -- tabela DERIVADA, nunca digitada. Ledger ate **F132** (F130/F131/F132 RESOLVIDOS na s195; F129 PARCIAL; F127/F128 DECLARADOS); 2 GATE do operador seguem (F87, F111).

> 🔴 **ABRIR A s200 POR AQUI:** (a) `claude --chrome` e conferir `list_connected_browsers` (a extensao desconecta; ele reabre o Chrome); (b) t1 JA no hub (47 q, Q23/24/46 discursivas fora; 4 divergentes); **t65 em captura ao fechar a s199** -> se `tmp/chrome/questoes/t65_*.json` existir, `--ingerir` -> Solucao Opus -> `--solucoes` -> `--exportar t65 --out tmp/emed_export_s199` -> `ArtifactData batch set` no hub; (c) **reconferir 2 gabaritos suspeitos de leitura requentada** (gabarito = o da questao anterior E solucao divergente): t100 Q8 (B), t68 Q13 (C) e t1 Q21 (C); (d) seguir a fila com o brief v3.2 (scratchpad da s199 some; o metodo esta em `history/session_199.md`): S2 t819 -> t146 -> t63; S3 t833 t112 t710 t832 t683 t75 t577 t376 t743 t122 t124 t127; (e) quando ele marcar lista como RESOLVIDA no hub: `--registrar` + `registrar_sessao_bulk` + `plano.py --concluir` + analise dos erros com `insert_questao --sessao --emed` -> `analises/*` (ainda nao exercitado com dado real); t96 esta em 11/18 no hub, registrada no banco local; (f) depois da fila: rodada de UI do hub com o feedback dele (listas, analises, experiencia). Tique `/banco-emed` custa ~5k tokens de contexto por disparo: preferir 30 min.

## > Proximo passo imediato

1. 🗄️ **Banco EMED (s199):** 11 listas capturadas no banco local (t26 t96 t49 t40 da s197; t68 t100 t3 t61 t651 t141 na s199 + t1 em curso) e 10 no hub com Solucao MedHub (as 4 da s197 tem comentario/forum antigos, sem Solucao MedHub). Divergentes a conferir no professor: t68 Q1/Q13 · t100 Q8/Q18/Q29/Q34 · t61 Q11 · t651 Q20. Discursiva t3 Q24 fora (`tmp/chrome_discursivas/`). Cadernos menores que o previsto: t3 31 (32), t651 30 (43). Custo medio: captura ~450k tokens/lista, solucao ~120k. Alternativa de custo ~zero em aberto: PDF do caderno com gabarito, se o EMED oferecer (perguntei, sem resposta). PRD `.vibeflow/prds/banco-questoes-emed.md`.
2. 📊 **Aba Analise do hub:** PRD `.vibeflow/prds/hub-aba-analise.md` -- pode se apoiar nas `analises/*` da Bancada (mesma cadeia em degraus + veredito). gen-spec -> implementar.
3. 📚 **Estudo:** listas DMG #26 (19q) e Pediatria #96 (18q) seguem abertas (ele focou em cards e aulas no 25/09); fim de semana = **UERJ 2021** (60q). Aula #877 pronta no hub.
4. 🃏 **Cards:** fila `2026-09-26b` (51) no ar. Marcas humanas abertas = 0. Duvidas clinicas da reforja em `tmp/reforja_s196/duvidas_*.json` e na s196 (#1113, #1176, #373, #65, #55) -> `/pesquisar-evidencia` quando houver folga. Resumo `[GIN] CA de Mama.md` ainda diz supraclavicular ipsilateral = estadio IV (errado; AJCC 8 = N3c).
5. 📊 **Ritmo e o alarme real:** 17,9 q/dia (7d) x 79,7 necessarios ate 01/11. Cobertura > refinamento.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (**inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7451 / 10400 (perf. ~78.8%). Hoje: 0. Ritmo do marco de volume ~81.9q/dia (36d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 10 provas + ENAMED real 75. **UERJ 2023 = 58** (solidas 44/60). Sequencia: ~~2023~~ -> 2021 -> 2022 -> 2024 -> 2025 -> 2026.
- **FSRS:** divida 13 atrasados + 28 p/ hoje -- pool 709 nunca introduzidos (entram <=100/dia). [derivado: day_plan --handoff-block]
- **Conteudo:** 135 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 1087 erros registrados · 1581 cards ativos · 0 needs_qualitative na fila · taxonomia 318 temas. [derivado: db]
- **Cronograma:** `plano_tarefas` = SSOT; Fase 1 GERADA por `tools/trilha.py`. #38 Hernias FEITA (sb 131, 25q/21). 🔴 A linha "Posicao" do `--handoff-block` ainda diz "semana 1" (semana por POSICAO no plano, o defeito que a auditoria achou no painel e que o painel V4 ja corrigiu); a semana de calendario e a **S2** (21-27/09) -- `plano.py --panorama` manda.
- **Posicao:** plano semana 1 (fase 1) · 2/5 tarefas da semana feitas · cota ~256q/dia ate 27/09 · Fase 1 ~89.4q/dia [derivado: plano_tarefas] -- a semana de calendario e a S2 (`plano.py --panorama` manda)
- **Engenharia:** suite **1097** coletados (s197); teto 100/150 (`day_plan.TETO_BASE`); **Bancada EMED v2 + `emed_banco.py` + `/banco-emed`** (s197); hub V4 (painel pelo leitor do panorama, quadro `core/hub_quadro.json`, `hub.py --precisa-publicar`, timer ativo, tela de fim com agenda); `/hub-backend` + `plano.py --concluir --leitura`.
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** · 🩻 Raio-X UERJ (foto de 18/09): https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc

## Ultima sessao -- s199 (2026-09-26, madrugada) -- banco de questoes: captura pelo Claude Code, Solucao MedHub, elo erro -> card

Detalhe e tabela de custo em `history/session_199.md`. Commits `6dd7707` (elo erro -> card, 13 testes), `209c870` (emed_solucoes), `00e5ec0` (bloco na aba Questoes), `9ef7f88` (painel, Version 22), `32232da` (log). Decisoes do operador: sem API do EMED; Solucao MedHub sem ler o comentario; semear o hub autorizado (privacidade conferida com `as_level: interact`). SBP 2026 do ferro profilatico (6 meses, 10-12,5 mg/dia em ciclos) confirmada no sentido: banca-dependente para a UERJ -> card + resumo de Pediatria pendentes.

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
