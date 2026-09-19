# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-19 (01h30) -- **s189 (ENGENHARIA, madrugada antes do simulado)**: a fila do `/ai-eng` executada em 5 fatias, cada uma com commit verde; **suite 933 -> 954, audit vibeflow PASS, selo verde, ZERO subagentes.** O plano de estudo NAO mudou (golden: os 115 overrides identicos; re-seed com 0 linha nova e 0 mudada). A proxima sessao e de ESTUDO (s190).*

> 🔒 **O SELO:** `python tools/selo.py` -- 0 item sem terminal, 0 discordancia. 107 achados: 87 FEITO · 5 SUPERADO · 5 PARCIAL · 1 FEITO(parcial) · **2 GATE do operador** (F87, F111). Tabela DERIVADA, nunca digitada.

## > Proximo passo imediato

1. 🔴 **SABADO 19/09 = DIAGNOSTICO: UERJ 2023 INTEIRA (100q, cronometrada)** -- `simulados/uerj/uerj_ad_2023_a.pdf`, gabarito `_b`. Registrar como `Simulado`, Autopsia por BLOCO. 🔴 **NAO abrir `simulados/uerj/uerj_mapa_questoes_2021-2026.json` antes de ele resolver cada prova (spoiler).**
2. 🔴 **Recalibrar a trilha NAO e reflexo de UMA prova (regra do `/ai-eng`, aritmetica):** 20q por bloco dao IC95 de +-21 pp num acerto de 60%; 3 provas +-12 pp; 6 provas +-9 pp. Logo: nao mexer em piso/teto por uma prova; peso de bloco so se move pelo acerto ACUMULADO nas provas UERJ (a partir da 3a). A Autopsia da 2023 e diagnostico de CONTEUDO. Quando for a hora: `core/cronograma/trilha/parametros.json` (estrategia) ou `trilha/custom.json` (uma linha, com `racional`) -> `python tools/trilha.py` (le o diff) -> `--gravar` -> `python tools/plano.py --semear --dry-run` -> `--apply --expect N`. Reverter a regra = 1 frase do operador.
3. 📚 **Trilha no banco** (`plano.py --listar --semana N`): S1 = UERJ 2023 + Hernias T1 (25q) + DMG T1 (19q) + aula de raciocinio diagnostico + Topicos em Pediatria (18q). **O boot agora da a cota do dia** (cabecalho do bloco Cronograma) e o ritmo da Fase 1 -- os dois DERIVADOS; numero de q/dia digitado aqui e proibido. Tema `sem registro de estudo` = aula-base ANTES da lista.
4. 👀 **Olhar UMA vez, sem pressa: `docs/RESERVA-FASE1.md`** -- 174 tarefas fora da fila; **13 de faixa ALTA da UERJ sem nenhuma tarefa na fila cobrindo o tema** (quase todas PARCIAL no Dashboard: Assistencia ao Parto, Pancreatite, DRGE, Endometriose, Colecistite T2, Arboviroses T3...). Trazer alguma = entrada em `trilha/custom.json`. Terminal 02/11, junto do F111.
5. 🔺 **Pedir a ele:** criar no banco do EMED 2 cadernos **UERJ 2017-2020** (filtro instituicao) -- estao na S7 (#1798/#1799) sem link.
6. 🃏 **Cards:** divida **103 atrasados + 26 p/ hoje** (129 vencidos), pool 690. Aula-base D10 de Acido-Base + Potassio antes de re-drillar #595 #596 #598 #783 #786 #787.

## A RECONCILIAR na proxima sessao (s190) -- ele chega com o resultado da UERJ 2023

1. **Registrar ANTES de analisar:** `registrar_sessao_bulk --area Simulado --feitas 100 --acertos N --data <dia da prova>` -> `plano.py --concluir 893 --sessao <id da LINHA>`. Pedir o acerto **por bloco** (Q1-20 CM · 21-40 CIR · 41-60 GO · 61-80 PED · 81-100 MFC) e o **racional declarado** de cada erro. So entao abrir o mapa da prova FEITA para a Autopsia.
2. **Volume feito fora de sessao:** listas da S1 (#38 Hernias · #26 DMG · #96 Topicos Ped) e cards -> `--concluir` + bulk. Conferir a divida FSRS (129 vencidos em 19/09).
3. **Dele:** gates F87 · **F111/R8** (decidir junto da Fase 2, 02/11) · validacao clinica do `TCE.md`.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (**inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7326 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo do marco de volume ~71.5q/dia (43d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 9 provas + ENAMED real 75. Agora: 1 prova UERJ inteira por fim de semana (2023 -> 2021 -> 2022 -> 2024 -> 2025 -> 2026).
- **FSRS:** divida 103 atrasados + 26 p/ hoje -- pool 690 nunca introduzidos (entram <=90/dia). Regua **v2** desde 18/09. Parametros seguem DEFAULT (F114).
- **Conteudo:** 135 resumos em resumos/. [derivado: glob] `Neurologia/TCE.md` reescrito (F104) -- pendente de validacao clinica dele.
- **Erros & Cards:** 1041 erros registrados · 1512 cards ativos · 0 needs_qualitative na fila · taxonomia 302 temas. [derivado: db] Reforja **308 abertas**.
- **Cronograma:** `plano_tarefas` = SSOT; **a Fase 1 sai de `tools/trilha.py`** (dado em 3 camadas em `core/cronograma/trilha/`: `parametros.json`, `custom.json`, `entrada/` fixada em 18/09) -> `plano_trilha.json` GERADO (115 overrides; editar a mao derruba o golden). `--mover` RECUSA linha da Fase 1 com a trilha ativa. `links_listas.json` com estado por tarefa (577 url / 482 sem link no PDF / 28 varios; faltando 0).
- **Engenharia:** suite **954**; `auto_check` PASSED; ledger ate **F125**; selo verde. Item 1.10: **127 orfas** (51,0%) com **catraca** (`BASE_ORFAS`). Spec `trilha-autoridade-unica`: audit **PASS**.
- **Posicao:** plano semana 1 (fase 1) · 0/5 tarefas da semana feitas · cota ~81q/dia ate 20/09 · Fase 1 ~76.6q/dia [derivado: plano_tarefas]
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** · 📊 **Painel**: https://claude.ai/artifact/QctZqVoJriSviJetF8FYBQ · 🩻 **Raio-X UERJ + trilha**: https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc

## Ultima sessao -- s189 (2026-09-18/19) -- ENGENHARIA: a Fase 1 com UMA autoridade

Detalhe em `history/session_189.md`. Na ordem do `/ai-eng` (`ai-eng-5a`): (1) F123 -- o "273 q/dia" do boot somava a Fase 2 e governava o recomendador; virou ritmo da Fase 1 + cota do dia, e o corte do hook de boot (8 linhas) passou a se declarar; (3) o gerador da trilha entrou no repo (F124) e trouxe um **loop infinito** herdado da s188 que travaria a recalibracao (F125, corrigido); (2) `plano.py --reserva`; (4) guard do `--mover`, estado explicito dos links, `links_exercicios.json` removido; (5) catraca do 1.10 e custo de subagente so pelo harness. Fatia 6 (regra de recalibracao como DADO) NAO feita -- o item 2 acima carrega a regra como texto.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- 🔴 **O piso/teto da trilha e conferido na regua do PROPRIO gerador** (bloco em que a UERJ cobra o tema) -- auto-consistencia. Pela area do EMED: CM 27,1% / CIR 18,7%, com as 7 linhas divergentes nominais em `python tools/trilha.py`; sem gate, por decisao do `/ai-eng`.
- 🔴 **A entrada do gerador e um snapshot de 18/09:** progresso posterior muda o status no banco, nunca a prioridade; re-snapshot sem exportador. O fim da Fase 1 tem duas fontes (ritmo: `FIM_CONTEUDO_ALVO` 01/11; cota: calendario da trilha 31/10).
- 🔴 **Duas autoridades que sobraram:** o `--mover` fora da Fase 1 ainda e desfeito pelo re-seed; `plano_custom.json` tem semana/ordem que a trilha sobrepoe em 28 de 29 tarefas custom.
- 🔴 **`audit_resumos` mede ESTRUTURA, nunca VERDADE CLINICA.** O gate `CONTRATO_REVOGADO` casa substring LITERAL.
- **F113 PARCIAL** (#689), **F110** sem gate, **F78**/**F2** DECLARADOS. `cards_rendimento` NAO fecha o F87.
- **Backlog de engenharia (depois de 02/11):** F122, redesenho do `--mover`, terminal da reserva, F111, fatia 6 (regra de recalibracao como dado + gold set de MFC com `concordancia_mfc.py`), prevalencia consumida em FAIXAS e nao em rank (mudaria a trilha).

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB. 💉 Diretrizes 2026 a conferir: Calendario Vacinal, GINA, ATLS 11 (parcial), SINAN.
- 🔴 **Ao responder item numerado do `/ai-eng`, casar por CONTEUDO, nunca por numero.** 📡 Canal = `SendMessage` entre sessoes locais (descobrir com `ListAgents`); o endereco muda a cada sessao dele -- responder pelo `from` da mensagem mais recente. Hook grava em `history/exchange-log.jsonl`.
- 🔴 **Regex sempre em string RAW** (`test_sem_caracter_de_controle`, BLOCK). Script de patch longo: arquivo no scratchpad, nunca heredoc gigante (quebrou na s189).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_189.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md * Selo: `python tools/selo.py`*
