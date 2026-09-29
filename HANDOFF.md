# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-28 (s204 SELADA) -- **s204 (Fable 5.1; /ai-eng fechado, report em arquivo)**: (1) AUDITORIA do F140 -- a causa escrita na s203 estava errada (era o passo de relearning de 10 min do py-fsrs, reincidencia do F32); (2) FIX por decisao do operador: **nota 1 volta so no dia seguinte** e **os novos do lote enchem o saldo do teto** (100/dia); (3) **ROTACAO DO LEDGER**: `AUDITORIA_MEDHUB.md` so tem o que esta em aberto (19), os 105 resolvidos foram para `history/auditoria/resolvidos.md`. `/loop` do backend DESLIGADO por ordem dele.
> 🏠 **MedHub HUB (1 artifact, fixado): https://claude.ai/artifact/3RksMfkzNWYSQD7D6JXNEr** -- abas Painel / Aulas / Cards / **Listas** (Questoes | Simulados) (Version 42). Republicar SEMPRE nesta URL (rito: `/hub-backend`, `/revisar` "DRENAR no player", `registrar-sessao` §6); `artifact-deleted` = recriar completo (capabilities de 3 regras, abaixo) e REPORTAR aqui. **Lote vivo `2026-09-29a`** = colecao `sessoes/2026-09-29a/notas` (100 cards, export de VESPERA para 29/09: 3 atrasados + 44 que vencem no dia + 53 novos; ja sob as regras da s204). O `2026-09-28b` saiu com 0/13 notas (nada a gravar). `2026-09-28a` 46/50 gravado (5 marcas de reforja, todas "Card longo": #367 #677 #678 #679 #1481). O `2026-09-26b` foi trocado a pedido dele com 12/51 gravados: RELER a colecao velha no fechamento. (o `sessao` nao e a data de hoje; trocou o lote, troca aqui). Colecoes `2026-09-22h` (220) e `2026-09-24a` (90) PODADAS no fechamento (releitura = 0 novas nas duas). Aulas Pediatria e DMG ja em TOPICOS; ele vai trazer o feedback.

> 📝 **SIMULADO DA VEZ = UERJ 2021 (60q, ~3 h) NO HUB:** aba Listas -> Simulados (o painel tem o atalho "resolver no hub"). Depois: 2022 (S3), 2024 (S4), 2025 (S5, 97q -- 3 anuladas fora), 2026 (S6). ⚰️ *Bancada EMED https://claude.ai/artifact/Q2Cojm89D9JwRyBYmCD5Db = historico da captura pelo Chrome, revogada em 26/09 (F135)*; entrada agora = PDF. 🔒 Conteudo so no `ipub.db` e nas colecoes `read admin` do hub; nunca no git.

> 🔒 **O SELO:** `python tools/selo.py` -- aberto x resolvido, DERIVADO. **19 em aberto, 105 resolvidos** (28/09). Do operador: F111, F87, F69, F68, F67, F65, F39. Do /ai-eng (triagem): F142, F141, F128, F127, F122. Engenharia: F129, F114, F113, F78, F63, F16, F2. Achado resolvido SAI da frente no selo (`--rotacionar` -> `--apply --expect N`); `--onde F<n>` acha qualquer um.

> 🔴 **ABRIR A s205 POR AQUI:** (1) **UERJ 2021 (t1793)** -- ele foi resolver no hub ao fechar a s203 e pediu: *"mais tarde discutimos os erros"*. Se o `/loop` da s203 ja registrou (`listas/t1793` resolvida + linha `--area Simulado` no `sessoes_bulk` + tarefa 1793 feita), ir DIRETO para a Autopsia/discussao dos erros com ele (`/banco-emed` passo 4, racional declarado primeiro); senao, `--registrar` idempotente (dry-run -> `--apply --expect N`) e o bulk com acerto por bloco, e so entao a Autopsia. (2) 🆕 **Cards:** lote `2026-09-29a` (100) no ar desde 28/09 22h30, publicado a pedido dele. O `/loop` esta DESLIGADO: abrir a sessao gravando o hub (`/revisar` passo 1 ou 1 tique de `/hub-backend`). 7 cards do lote tem o CONTEXTO cortado no meio da frase (#671 #762 #764 #765 #766 #767 #768) -> curadoria. (3) /ai-eng: report da s204 em `~/ai-eng/HANDOFF-MEDHUB-F140-AUDITORIA-2026-09-28.md` (triagem de F141/F142); checkpoint da s203 (golden t3, F138, F139) segue PENDENTE. (4) Perguntas ao operador: meta FIXA (implementada) x DERIVADA do plano (10.668); "semana 1" do boot x semana de calendario do painel; nota 4 = 72,6% das notas da regua v2 (o contrato a chama de rara). (5) 10 cards com marca de reforja -> curadoria.

## > Proximo passo imediato

1. 🗄️ **Banco de questoes:** 12 listas EMED + **5 simulados UERJ** (t1793 2021, t1794 2022, t892 2024, t891 2025, t890 2026) no hub; **resolvidas: t96, t26**; em v2 (cadeia): t26 t40 t49 t96. Lista NOVA do EMED entra pela API (`/banco-emed` §emed_api; `.emed_token` ate 26/10), 1 por vez, com a contagem confirmada por ele. Mapa de fragilidade: `emed_banco.py --status --por-objetivo`. Divergentes a conferir: t49 Q10/Q20 · t68 Q1/Q13 · t100 Q8/Q18/Q29/Q34 · t61 Q11 · t651 Q20. Sem resumo local de Hernias.
2. 📊 **Engenharia do hub (fila):** (a) **"Hoje" AO VIVO no painel** (opcao B, aprovada por ele em 28/09 para a proxima sessao de engenharia): a pagina soma na hora os cards com nota e as questoes respondidas hoje que o tique ainda nao gravou -- o registro oficial segue do tique; discover -> spec. (b) Aba Analise: PRD `.vibeflow/prds/hub-aba-analise.md` -- gen-spec -> implementar. (c) **Fila de cards (s204):** F141 (card de 1 dia servido com menos de 24 h cai no ramo de curto prazo: 212 revisoes) e F142 (sem trava de 2a gravacao no mesmo dia; teto conta linha) esperam a triagem do /ai-eng. Evidencia crua em `tmp/f140_auditoria/`.
3. 📚 **Estudo:** a semana 3 (28/09-04/10, 18 tarefas, 510q) abre com as pendentes da S2 atrasadas (#49 Hernias, #40 DMG, #100 Pediatria e cia). Aula #877 pronta no hub. UERJ 2021 em curso no hub desde o fechamento da s203.
4. 🃏 **Cards:** lote `2026-09-27b` (10, saldo de 27/09) no ar. **11 marcas de reforja de 27/09** (#561 #606 #616 #618 #619 #620 #622 #642 #649 #651 #659 -- "pergunta composta"; #616 tambem "card longo") -> curadoria. Duvidas clinicas da reforja em `tmp/reforja_s196/duvidas_*.json` e na s196 (#1113, #1176, #373, #65, #55) -> `/pesquisar-evidencia` quando houver folga. `questoes_erros` #860 guarda o racional antigo (supraclavicular = IV); sem writer para corrigir.
5. 📊 **Meta UNICA (s203, decisao dele): 10.000 em 01/11 = ~71,8 q/dia** x ritmo real 18,7 q/dia (14d). ⚰️ *Cota da semana, Ciclo 2026 e meta mensal SAIRAM*; a Fase 1 e a cobertura (10.668 fechando o plano). Cobertura > refinamento.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (**inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Meta:** 7488 / 10000 (perf. ~78.8%). Hoje: 0. Meta ~73.9q/dia (34d p/ UERJ/MFC (prova 01/11)).
- **Simulados:** 10 provas + ENAMED real 75. **UERJ 2023 = 58** (solidas 44/60). Sequencia: ~~2023~~ -> 2021 -> 2022 -> 2024 -> 2025 -> 2026.
- **FSRS:** divida 0 atrasados + 3 p/ hoje -- pool 655 nunca introduzidos (entram <=100/dia).
- **Conteudo:** 135 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 1094 erros registrados · 1589 cards ativos · 0 needs_qualitative na fila · taxonomia 320 temas. [derivado: db]
- **Cronograma:** `plano_tarefas` = SSOT; Fase 1 GERADA por `tools/trilha.py`. #38 Hernias FEITA (sb 131, 25q/21). 🔴 A linha "Posicao" do `--handoff-block` ainda diz "semana 1" (semana por POSICAO no plano, o defeito que a auditoria achou no painel e que o painel V4 ja corrigiu); a semana de calendario e a **S3** (28/09-04/10) -- `plano.py --panorama` manda.
- **Posicao:** plano semana 1 (fase 1) · 4/5 tarefas da semana feitas · Fase 1: 3180q pendentes -> 10668 fechando o plano [derivado: plano_tarefas] -- a semana de calendario e a S3 (`plano.py --panorama` manda)
- **Engenharia:** suite **1245** (s204, medida por `python -m pytest tools/ -q` e conferida no pre-commit -- F136); `tools/emed_api.py` (lista do EMED pela API, sem LLM, whitelist na fronteira; golden t3 VERDE desde 27/09, mapa medido na 1a corrida real); **F137 fechado**: `backup_db.fixar_antes_do_ato` no 1o write de cards_prune, recurate_cards, dedup/normalize_taxonomia e do emed_banco que sobrescreve, `--desfixar ID --motivo`; caminho PDF `tools/prova_pdf.py` (provas de banca); Solucao v2 em cadeia + `core/objetivos.json`; hub V4 + aba Listas Questoes | Simulados; `/hub-backend` + `plano.py --concluir --leitura`.
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** · 🩻 Raio-X UERJ (foto de 18/09): https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc

## Ultima sessao -- s204 (2026-09-28) -- F140 auditado e corrigido; ledger rotacionado (19 abertos na frente, 105 no historico)

Detalhe em `history/session_204.md`. Commits `eaaae16` (auditoria), `6c32845` (fix do F140) e o da rotacao. Auditorias em `.vibeflow/audits/`: `f140-fila-pos-bloco`, `nota1-volta-no-dia-seguinte` (PASS), `ledger-rotacao` (PASS). 5 subagentes read-only (978.976 tokens, `usage` do harness). `/loop` do backend desligado em 28/09 (job `3f6af4b9` cancelado). Anterior: s203.

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
