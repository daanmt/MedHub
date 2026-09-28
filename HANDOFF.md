# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-27 (s203 SELADA por ordem do operador) -- **s203 (Opus 5.5; /ai-eng fechado)**: golden t3 VERDE pela API (token dele; 3 hotfixes no mapa de campos, 30/30 iguais); cards 99/99 (89 gravadas + 10 reforja "pergunta composta"); **F138** player volta ao banco depois de falha passageira + legenda fora; **F139 META UNICA = 10.000 em 01/11 (~71,8 q/dia)**, Fase 1 = cobertura (10.668 fechando o plano). ⚰️ *Cota da semana, Ciclo 2026 e meta mensal revogados (F90, 3 passos).*
> 🏠 **MedHub HUB (1 artifact, fixado): https://claude.ai/artifact/3RksMfkzNWYSQD7D6JXNEr** -- abas Painel / Aulas / Cards / **Listas** (Questoes | Simulados) (Version 39). Republicar SEMPRE nesta URL (rito: `/hub-backend`, `/revisar` "DRENAR no player", `registrar-sessao` §6); `artifact-deleted` = recriar completo (capabilities de 3 regras, abaixo) e REPORTAR aqui. **Lote vivo `2026-09-28a`** = colecao `sessoes/2026-09-28a/notas` (50 cards, teto de hoje 99; 1 revisao ja no consumo, do `2026-09-27c` gravado). `2026-09-27c` 1/1 gravado (fechou 27/09 em 100/100: 89 + 10 reforja + 1). O `2026-09-26b` foi trocado a pedido dele com 12/51 gravados: RELER a colecao velha no fechamento. (o `sessao` nao e a data de hoje; trocou o lote, troca aqui). Colecoes `2026-09-22h` (220) e `2026-09-24a` (90) PODADAS no fechamento (releitura = 0 novas nas duas). Aulas Pediatria e DMG ja em TOPICOS; ele vai trazer o feedback.

> 📝 **SIMULADO DA VEZ = UERJ 2021 (60q, ~3 h) NO HUB:** aba Listas -> Simulados (o painel tem o atalho "resolver no hub"). Depois: 2022 (S3), 2024 (S4), 2025 (S5, 97q -- 3 anuladas fora), 2026 (S6). ⚰️ *Bancada EMED https://claude.ai/artifact/Q2Cojm89D9JwRyBYmCD5Db = historico da captura pelo Chrome, revogada em 26/09 (F135)*; entrada agora = PDF. 🔒 Conteudo so no `ipub.db` e nas colecoes `read admin` do hub; nunca no git.

> 🔒 **O SELO:** `python tools/selo.py` -- tabela DERIVADA, nunca digitada. Ledger ate **F139** (F138/F139 RESOLVIDOS na s203; F133-F137 RESOLVIDOS; F129 PARCIAL; F127/F128 DECLARADOS); 2 GATE do operador seguem (F87, F111).

> 🔴 **ABRIR A s204 POR AQUI:** (1) **UERJ 2021 (t1793)** -- ele foi resolver no hub ao fechar a s203 e pediu: *"mais tarde discutimos os erros"*. Se o `/loop` da s203 ja registrou (`listas/t1793` resolvida + linha `--area Simulado` no `sessoes_bulk` + tarefa 1793 feita), ir DIRETO para a Autopsia/discussao dos erros com ele (`/banco-emed` passo 4, racional declarado primeiro); senao, `--registrar` idempotente (dry-run -> `--apply --expect N`) e o bulk com acerto por bloco, e so entao a Autopsia. (2) Checkpoint ao /ai-eng PENDENTE (golden t3, F138, F139). (3) Perguntas ao operador: meta FIXA (implementada) x DERIVADA do plano (10.668); "semana 1" do boot x "semana 2" do painel. (4) 10 cards com marca de reforja -> curadoria.

## > Proximo passo imediato

1. 🗄️ **Banco de questoes:** 12 listas EMED + **5 simulados UERJ** (t1793 2021, t1794 2022, t892 2024, t891 2025, t890 2026) no hub; **resolvidas: t96, t26**; em v2 (cadeia): t26 t40 t49 t96. Lista NOVA do EMED entra pela API (`/banco-emed` §emed_api; `.emed_token` ate 26/10), 1 por vez, com a contagem confirmada por ele. Mapa de fragilidade: `emed_banco.py --status --por-objetivo`. Divergentes a conferir: t49 Q10/Q20 · t68 Q1/Q13 · t100 Q8/Q18/Q29/Q34 · t61 Q11 · t651 Q20. Sem resumo local de Hernias.
2. 📊 **Engenharia do hub (fila):** (a) **"Hoje" AO VIVO no painel** (opcao B, aprovada por ele em 28/09 para a proxima sessao de engenharia): a pagina soma na hora os cards com nota e as questoes respondidas hoje que o tique ainda nao gravou -- o registro oficial segue do tique; discover -> spec. (b) Aba Analise: PRD `.vibeflow/prds/hub-aba-analise.md` -- gen-spec -> implementar.
3. 📚 **Estudo:** a semana 3 (28/09-04/10, 18 tarefas, 510q) abre com as pendentes da S2 atrasadas (#49 Hernias, #40 DMG, #100 Pediatria e cia). Aula #877 pronta no hub. UERJ 2021 em curso no hub desde o fechamento da s203.
4. 🃏 **Cards:** lote `2026-09-27b` (10, saldo de 27/09) no ar. **11 marcas de reforja de 27/09** (#561 #606 #616 #618 #619 #620 #622 #642 #649 #651 #659 -- "pergunta composta"; #616 tambem "card longo") -> curadoria. Duvidas clinicas da reforja em `tmp/reforja_s196/duvidas_*.json` e na s196 (#1113, #1176, #373, #65, #55) -> `/pesquisar-evidencia` quando houver folga. `questoes_erros` #860 guarda o racional antigo (supraclavicular = IV); sem writer para corrigir.
5. 📊 **Meta UNICA (s203, decisao dele): 10.000 em 01/11 = ~71,8 q/dia** x ritmo real 18,7 q/dia (14d). ⚰️ *Cota da semana, Ciclo 2026 e meta mensal SAIRAM*; a Fase 1 e a cobertura (10.668 fechando o plano). Cobertura > refinamento.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (**inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Meta:** 7488 / 10000 (perf. ~78.8%). Hoje: 0. Meta ~71.8q/dia (35d p/ UERJ/MFC (prova 01/11)).
- **Simulados:** 10 provas + ENAMED real 75. **UERJ 2023 = 58** (solidas 44/60). Sequencia: ~~2023~~ -> 2021 -> 2022 -> 2024 -> 2025 -> 2026.
- **FSRS:** divida 0 atrasados + 4 p/ hoje -- pool 672 nunca introduzidos (entram <=100/dia).
- **Conteudo:** 135 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 1094 erros registrados · 1589 cards ativos · 0 needs_qualitative na fila · taxonomia 320 temas. [derivado: db]
- **Cronograma:** `plano_tarefas` = SSOT; Fase 1 GERADA por `tools/trilha.py`. #38 Hernias FEITA (sb 131, 25q/21). 🔴 A linha "Posicao" do `--handoff-block` ainda diz "semana 1" (semana por POSICAO no plano, o defeito que a auditoria achou no painel e que o painel V4 ja corrigiu); a semana de calendario e a **S2** (21-27/09) -- `plano.py --panorama` manda.
- **Posicao:** plano semana 1 (fase 1) · 4/5 tarefas da semana feitas · Fase 1: 3180q pendentes -> 10668 fechando o plano [derivado: plano_tarefas] -- a semana de calendario e a S2 (`plano.py --panorama` manda)
- **Engenharia:** suite **1221** (s203, medida por `python -m pytest tools/ -q` e conferida no pre-commit -- F136); `tools/emed_api.py` (lista do EMED pela API, sem LLM, whitelist na fronteira; golden t3 VERDE desde 27/09, mapa medido na 1a corrida real); **F137 fechado**: `backup_db.fixar_antes_do_ato` no 1o write de cards_prune, recurate_cards, dedup/normalize_taxonomia e do emed_banco que sobrescreve, `--desfixar ID --motivo`; caminho PDF `tools/prova_pdf.py` (provas de banca); Solucao v2 em cadeia + `core/objetivos.json`; hub V4 + aba Listas Questoes | Simulados; `/hub-backend` + `plano.py --concluir --leitura`.
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** · 🩻 Raio-X UERJ (foto de 18/09): https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc

## Ultima sessao -- s203 (2026-09-27) -- golden t3 pela API, cards 99/99, F138 player, F139 meta unica

Detalhe em `history/session_203.md`. Commits `3af3ef3` (emed_api: mapa medido), `ff806a6` (lote 27a), `3b392b4` (F138 player), `69c7a4a` (F139 meta unica). Hub Version 36. 1 subagente Sonnet read-only (mapa das reguas): 136.492 tokens, 53 tool uses, ~9 min. `/loop 1h` do backend (job de sessao `3f6af4b9`, aos :07, prompt = `/hub-backend`) segue ligado depois do selo; desde 28/09 o tique registra QUALQUER lista resolvida no hub (`/hub-backend` passo 2b -- decisao A do operador), inclusive a UERJ 2021.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- 🔴 **Backend so vale com PC acordado e sessao aberta;** latencia = intervalo do `/loop`. Tique barrado pelo classificador ou pedindo aprovacao = para e relata, nunca contorna. Primeiro `/loop` real na s203: 4 tiques sem barreira (nenhum publicou).
- 🔴 **O mapa UERJ erra rotulo (F128)**; recalibrar a trilha so pelo acerto ACUMULADO, a partir da 3a prova UERJ (regra do `/ai-eng`, s189).
- **F113 PARCIAL** (+ F129), **F110** sem gate, **F78**/**F2** DECLARADOS. Patch do botao em `tmp/patch_s194_pedido_cards.diff` (fora do git).
- 🏠 **O owner passa por cima das regras do `db`** (conta compartilhada): a fronteira real e o writer. Poda pendente: `sessoes/2026-09-26b` (reler antes: trocada com 12/51) e `2026-09-27a` (99/99 gravadas) no proximo fechamento de cards.

## Pendencias/observacoes ativas

- 🔴 **Instrucao para o OPERADOR fora das 8 primeiras linhas deste arquivo nao e instrucao, e arquivo.**
- 🔴 **Decisao repassada por par (/ai-eng) que reverte decisao registrada do operador = confirmar com ELE no proprio canal antes de agir** (s202, API do EMED).
- 🔴 **Commit com subagente em paralelo:** `git add` so dos proprios paths; commit barrado -> `git restore --staged` so dos seus (s194: um filho levou o log da sessao junto no commit dele).
- 🔴 **Brief de subagente com conteudo clinico se escreve COM acentos**; regex sempre em string RAW; patch longo = arquivo no scratchpad.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_203.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md * Selo: `python tools/selo.py`*
