# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-18 (23h) -- **s188 (ESTUDO/orquestracao)**: as 6 provas da UERJ (520q) mapeadas por tema, cruzadas com o que ele estudou, com a Reta Final de 30 sem, o extensivo de 52 e as cores do Drive; o plano virou **TRILHA como dado** e esta gravado no banco. **9 subagentes (1,74M tokens, ~49 min em paralelo), suite 924 -> 933, harness verde, selo verde.** Relatorio: https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc*

> 🔒 **O SELO:** `python tools/selo.py` -- **0 item sem terminal, 0 discordancia**. 100 achados: 81 FEITO · 5 SUPERADO · 5 PARCIAL · 1 FEITO(parcial) · **2 GATE do operador**. A tabela e **DERIVADA** (ledger + `git log` + `clausulas_check` + `consistencia_check` + docstring das suites), nunca digitada. `--markdown` para colar; `--sensores` para o escopo que cada sensor declara NAO alcancar.

## > Proximo passo imediato

1. 🔴 **SABADO 19/09 = DIAGNOSTICO: UERJ 2023 INTEIRA (100q, cronometrada)** -- `simulados/uerj/uerj_ad_2023_a.pdf`, gabarito `_b`. Registrar como `Simulado`, Autopsia por BLOCO, e **recalibrar o peso dos blocos da S2** pelo acerto medido na banca real (hoje o acerto por bloco na UERJ e DESCONHECIDO). 🔴 **NAO abrir `simulados/uerj/uerj_mapa_questoes_2021-2026.json` antes de ele resolver cada prova (spoiler).**
2. 📚 **Trilha da Fase 1 no banco** (`plano.py --listar --semana N`; dia a dia no artifact acima): S1 = UERJ 2023 + Hernias T1 (25q) + DMG T1 (19q) + aula de raciocinio diagnostico + Topicos em Pediatria (18q). 1 prova UERJ inteira por fim de semana (2023 -> 2021 -> 2022 -> 2024 -> 2025 -> 2026); S7 sem tema novo. **Tema `sem registro de estudo` = aula-base ANTES da lista** (48 temas-zero na trilha; 11 deles nem lista tem no EMED -- viram sessao de aula + 10-15q do banco).
3. 🔴 **O que os dados disseram sobre MFC (F121), para nao re-litigar:** o defeito era SEQUENCIA e corte (S1-S2 ~40% MFC, 7 resumos antes de qualquer lista, CM cortada), **nao valor** -- 8 temas cobrem metade do bloco de MFC contra 20 na CM; tema a tema MFC e o maior retorno da prova. Na trilha: 10 sessoes de MFC intercaladas (nunca abrindo a semana) + o bloco de 20q dentro das 6 provas. **Tuberculose e o tema nº1 da prova inteira (14q, 4 blocos)** -> aula "TB 360" na S2.
4. 🔺 **Pedir a ele:** criar no banco do EMED 2 cadernos **UERJ 2017-2020** (filtro instituicao) -- questoes autenticas que nao existem em PDF; estao na S7 (#1798/#1799) sem link.
5. 🔺 **Gates dele seguem abertos:** F87 · **F111/R8** (decidir junto da Fase 2, 02/11) · validacao clinica do `TCE.md`. **Para o `/ai-eng` auditar:** F119-F123 no ledger + spec `trilha-uerj-plano-como-dado` (F122/F123 DECLARADOS, com remedio proposto).
6. 🃏 **Cards:** divida **72 atrasados + 31 p/ hoje**, pool 690, reforja 308 abertas. Aula-base D10 de Acido-Base + Potassio antes de re-drillar #595 #596 #598 #783 #786 #787.

## A RECONCILIAR na proxima sessao (s189) -- ele chega com o resultado da UERJ 2023

1. **Registrar ANTES de analisar:** `registrar_sessao_bulk --area Simulado --feitas 100 --acertos N --data <dia da prova>` -> `plano.py --concluir 893 --sessao <id da LINHA>`. Pedir o acerto **por bloco** (Q1-20 CM · 21-40 CIR · 41-60 GO · 61-80 PED · 81-100 MFC) e o **racional declarado** de cada erro.
2. **Recalibrar a S2 pelo acerto por bloco:** geradores em `scratch/s188_trilha/` (local, fora do git): ajustar `PISO`/`TETO` ou `trilha_custom.py`, `python -X utf8 gera_trilha.py --gravar`, depois `plano.py --semear --dry-run` -> `--apply --expect 0`. So entao abrir o mapa da prova FEITA (`uerj_mapa_questoes_2021-2026.json`) para a Autopsia.
3. **Volume feito fora de sessao:** listas da S1 (#38 Hernias · #26 DMG · #96 Topicos Ped) e cards -> `--concluir` + bulk; conferir a divida FSRS (103 vencidos em 18/09).
4. **`/ai-eng` RESPONDEU (`ai-eng-5a`, 18/09 23h30): GO no conjunto, 2 ALTERA.** Verbatim: `docs/VEREDITO-AIENG-s188.md`. Ordem dele ate 01/11 (tudo pequeno; **estudo rege**; silencio = GO): **(a) 🔴 F123a** -- a linha `cobrir o plano ~273 q/dia` do boot esta ERRADA (divide a Fase 2 pelos dias da Fase 1): corrigir (Fase 1 / dias da Fase 1) ou REMOVER; **ate la IGNORAR esse numero -- o certo e ~77 q/dia**; (b) listar a RESERVA (46 linhas que a `fase1_exclusiva` tirou da fila) por peso UERJ, WARN se alguma for de faixa alta, e o operador OLHA uma vez; (c) guard: `--mover` RECUSA linha da Fase 1 com trilha ativa; (d) remover `links_exercicios.json`; (e) teste de PROPRIEDADE sobre `plano_trilha.json` (19-25% por bloco, calendario, 6 simulados) + cota do dia no `day_plan` = questoes restantes da semana / dias restantes. Pergunta dele em aberto (F119): linha sem link distingue "nao existe lista" de "link faltando"? Depois de 02/11: F122, catraca das clausulas orfas, redesenho do `--mover`, terminal da reserva, F111.
5. **Dele:** criar os 2 cadernos UERJ 2017-2020 no banco do EMED (#1798/#1799 sem link) · gates F87, F111/R8, `TCE.md`.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (44d; **inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7326 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~69.9q/dia (44d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 9 provas + ENAMED real 75. Proximo slot ~10/10 (cadencia de 4 semanas).
- **FSRS:** divida **72 atrasados + 31 p/ hoje** -- pool 690 nunca introduzidos (entram <=90/dia). Regua **v2** desde 18/09; revlog misto (3.067 v1 + 3 v2). Parametros seguem DEFAULT por decisao (F114).
- **Conteudo:** **135 resumos** (stub `[CIR] TCE.md` removido em 18/09). `Neurologia/TCE.md` **reescrito** (F104) -- pendente de validacao clinica dele.
- **Erros & Cards:** 1041 erros · **1512 cards ativos** (+5 do split do F105) · 0 needs_qualitative · taxonomia 302 temas. Reforja **308 abertas**.
- **Cronograma:** `plano_tarefas` = SSOT; **a Fase 1 e ditada por `core/cronograma/plano_trilha.json`** (115 overrides; editar o JSON + `--semear --apply`; o `--mover` e desfeito pelo re-seed). Links das listas: `links_listas.json` (66 -> 381 linhas com link). Incidencia UERJ: `prevalencia_uerj.json`.
- **Engenharia:** suite **933**; `auto_check` PASSED; ledger ate **F123**; selo verde (`python tools/selo.py`). Item 1.10: 257 clausulas -- 56 CHECK · 69 declaradas · **132 orfas** (+7 vindas da skill/spec novas, nao anotadas na s188).
- **Posicao:** plano semana 1 (fase 1) · 0/5 tarefas da semana feitas [derivado: plano_tarefas]
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** (inscrito) · 📊 **Painel** (regenerar no fechamento, MESMA url): https://claude.ai/artifact/QctZqVoJriSviJetF8FYBQ · 🩻 **Raio-X UERJ + trilha**: https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc

## Ultima sessao -- s188 (2026-09-18) -- ESTUDO/orquestracao: Raio-X UERJ + trilha como dado

Detalhe em `history/session_188.md`. **9 subagentes** (5 Sonnet classificando 1 edicao cada, 1 Opus nos links, 1 Sonnet na reforma, 1 Sonnet web ISOLADO, 1 Haiku no export do Drive); principal nunca parado. Numero de filho so entrou com lente independente (amostra a olho 15/15 · concordancia com o mapa manual de MFC 78% estrito/~90% lido · gabarito web 5/5). 🔴 **Custo auto-relatado por filho NAO e confiavel** (35-40 min declarados x 8,5 min medidos): usar o `usage` do harness.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- 🔴 **DECLARADO e NAO construido, com a contagem que sustenta cada decisao:** (a) **3a forma de cabecalho mentiroso** -- achado cujo SUJEITO foi removido (F36/F72); nem o G14 (quer lapide no §11) nem o G14b (quer portador reivindicando) a veem; base = 2, nao paga gate. (b) **Familia de tokens no `CONTRATO_REVOGADO`** -- dos 23 termos do §12 so **2** tem limiar numerico, e sao a mesma regra do F117: maquinaria para N=1. (c) **Coluna `origem` no revlog** (player x chat) -- hoje a origem se infere por timestamp; candidato, nao construido.
- 🔴 **`audit_resumos` mede ESTRUTURA, nunca VERDADE CLINICA** -- e agora diz isso na propria saida. Ele imprimia PASSED sobre um `TCE.md` que afirmava que o manitol "perfura a barreira encefalica", o oposto do mecanismo. **PASSED != clinicamente correto.**
- 🔴 **O item 1.10 nao esta completo:** 125 clausulas orfas em 14 portadores. O mecanismo e o entregavel; a anotacao restante e julgamento por portador, com a contagem acima e o WARN 16c como burn-down.
- 🔴 **O gate `CONTRATO_REVOGADO` casa substring LITERAL.** O F117 provou: a s186 cadastrou a redacao do player e a do chat sobreviveu. Uma 4a parafrase passaria. A garantia e o rito de cadastrar TODAS as redacoes.
- **F113 PARCIAL** -- **#685 corrigido em 18/09** (reescrito com acentuacao no split do F105); **#689 segue**, residuo irregular. **F110** sem gate por construcao. **F78**/**F2** DECLARADOS com data. 🔴 **`cards_rendimento` NAO fecha o F87:** os 13 cards cortados nunca entraram no baralho -- nenhum sinal do FSRS os alcanca.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB. 💉 Diretrizes 2026 a conferir: Calendario Vacinal, GINA, ATLS 11 (parcial), SINAN.
- 🔴 **Ao responder item numerado do `/ai-eng`, casar por CONTEUDO, nunca por numero.** 📡 **Canal = `SendMessage` entre sessoes locais** -- ⚰️ **o endereco da janela 6 (N=80) MORREU em 18/09** e nada e devido entre nos; a proxima sessao dele manda 1 mensagem de presenca com endereco novo **so se o operador reabrir engenharia** (descobrir com `ListAgents`). 🔴 **O endereco MUDA a cada sessao dele** -- responder sempre pelo `from` da mensagem mais recente. Hook grava em `history/exchange-log.jsonl`.
- 🔴 **Convencao que a janela escreveu, e o gate que a sustenta: regex sempre em string RAW.** Escrevi uma sequencia de escape numa string nao-raw por heredoc e gravei **backspace (0x08)** dentro de dois regexes do `selo.py` -- um deles fazia TODO achado RESOLVIDO aparecer como "SEM TERMINAL". O ledger ja registrava essa classe para o `audit_resumos` ("linter verde, check morto"). Virou `test_sem_caracter_de_controle` (BLOCK), **que me pegou repetindo o mesmo erro 10 minutos depois**.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_188.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md * Selo: `python tools/selo.py`*
