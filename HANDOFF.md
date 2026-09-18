# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-18 (noite) -- **s187 (ENGENHARIA, janela 6)**: a reforma de engenharia fechou com **SELO DERIVADO**. **11 commits, harness verde em cada um, suite 858 -> 912, ZERO subagentes.** 3 achados novos (F115 F116 F117), 4 fechados, 14 cabecalhos mentirosos corrigidos.*

> 🔒 **O SELO:** `python tools/selo.py` -- **0 item sem terminal, 0 discordancia**. 99 achados: 78 FEITO · 5 SUPERADO · 5 PARCIAL · 1 FEITO(parcial) · **4 GATE do operador**. A tabela e **DERIVADA** (ledger + `git log` + `clausulas_check` + `consistencia_check` + docstring das suites), nunca digitada. `--markdown` para colar; `--sensores` para o escopo que cada sensor declara NAO alcancar.

## > Proximo passo imediato

1. 🔴 **NAO HA FILA DE ENGENHARIA ABERTA.** A proxima janela so abre por ordem do operador, com as respostas dos gates abaixo. O default voltou a ser **ESTUDO**.
2. 🔺 **6 GATES do operador, cada um com a pergunta de 1 linha:**
   - **stub `[CIR] TCE.md`** -- apago? (17 linhas, `status: stub`, 3 armadilhas genericas; grep §10.4 feito, zero citador vivo). Parei por `§1.1(b)`: destrutivo sobre `resumos/` e a clausula e dele.
   - **`Neurologia/TCE.md` reescrito** -- validar clinicamente. Eu garanto FORMA (`/estilo-resumo`), nao VERDADE.
   - **F87** -- quais cards pagam aluguel? O harness ve FORMA, nunca RENDIMENTO.
   - **F100** -- re-ensinar nao fechou 3 pontos da s175: mudo o metodo de re-ensino?
   - **F105** -- triar as 11 marcas de pergunta composta abertas na fila de reforja?
   - **F111/R8** -- o extensivo leitura-first garante recall no dia 1? (decision brief, prazo **02/11**).
3. 🃏 **Cards:** divida **72 atrasados + 31 p/ hoje**, pool 685. **Fila de reforja 318** (+30: os candidatos `comprimento_total` do F115, ingeridos sob o rito §10.7, reversiveis por `--descartar`). 🔴 **Aula-base D10 de Acido-Base + Potassio ANTES de re-drillar os 6 segurados** (#595 #596 #598 #783 #786 #787). **#685 e #689** seguem com erro de portugues que regra nenhuma pega (F113).
4. 📚 **Questoes (Fase 1, semana 1 = 14 tarefas, 369q; `plano.py --listar --semana 1`):** Prevencao Quaternaria (resumo) -> AMI (resumo) -> MFC extensivo Revisao (50) -> Saude do Idoso T+R (32). Bulk -> `plano.py --concluir ID --sessao <id>`; erros -> Autopsia.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (44d; **inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7326 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~69.9q/dia (44d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 9 provas + ENAMED real 75. Proximo slot ~10/10 (cadencia de 4 semanas).
- **FSRS:** divida **72 atrasados + 31 p/ hoje** -- pool 685 nunca introduzidos (entram <=90/dia). Regua **v2** desde 18/09; revlog misto (3.067 v1 + 3 v2). Parametros seguem DEFAULT por decisao (F114).
- **Conteudo:** 136 resumos. `Neurologia/TCE.md` **reescrito** (F104). Preventiva: so 3/22 decks pagam aluguel na UERJ.
- **Erros & Cards:** 1041 erros · **1507 cards ativos** · 0 needs_qualitative na fila · taxonomia 302 temas. Reforja **318**.
- **Cronograma:** `plano_tarefas` = SSOT unica (Drive congelado na part-8). Visao consolidada: o painel.
- **Engenharia:** suite **912**; `auto_check` PASSED; ledger ate **F117**. **Item 1.10:** 247 clausulas normativas -- **53 com CHECK · 69 declaradas · 125 orfas (49,4%)**. Os 4 portadores centrais estao **100%**: `analisar-questao` 28/28 · `revisar` 30/30 · `AGENTE` 41/41 · `revisao-calibrada` 50/50. Maiores orfaos restantes: `estilo-flashcard` 21 · `engenharia-cli` 18 · `cronograma-contract` 18 · `estilo-resumo` 17.
- **Posicao:** plano semana 1 (fase 1) · 0/14 tarefas da semana feitas [derivado: plano_tarefas]
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** (inscrito) · 📊 **Painel** (regenerar no fechamento, MESMA url): https://claude.ai/artifact/QctZqVoJriSviJetF8FYBQ

## Ultima sessao -- s187 (2026-09-18) -- ENGENHARIA, janela 6 (selo da reforma)

Detalhe em `history/session_187.md`. **ZERO subagentes** (nenhum lote passou o limiar do F93). Todo fix nasceu com teste antes do codigo; em 4 casos o teste pegou defeito meu antes do commit. 🔴 **A janela inteira tem UMA pergunta:** *o sensor alcanca exatamente o que diz alcancar?* -- **F115** (escopo MENOR que o necessario), **Invariante A** (sensor mirando a coisa vizinha), **G14b** (sensor olhando o registro vizinho), **F116** (escopo MAIOR que o declarado). Quatro faces, quatro gates novos.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- 🔴 **DECLARADO e NAO construido, com a contagem que sustenta cada decisao:** (a) **3a forma de cabecalho mentiroso** -- achado cujo SUJEITO foi removido (F36/F72); nem o G14 (quer lapide no §11) nem o G14b (quer portador reivindicando) a veem; base = 2, nao paga gate. (b) **Familia de tokens no `CONTRATO_REVOGADO`** -- dos 23 termos do §12 so **2** tem limiar numerico, e sao a mesma regra do F117: maquinaria para N=1. (c) **Coluna `origem` no revlog** (player x chat) -- hoje a origem se infere por timestamp; candidato, nao construido.
- 🔴 **`audit_resumos` mede ESTRUTURA, nunca VERDADE CLINICA** -- e agora diz isso na propria saida. Ele imprimia PASSED sobre um `TCE.md` que afirmava que o manitol "perfura a barreira encefalica", o oposto do mecanismo. **PASSED != clinicamente correto.**
- 🔴 **O item 1.10 nao esta completo:** 125 clausulas orfas em 14 portadores. O mecanismo e o entregavel; a anotacao restante e julgamento por portador, com a contagem acima e o WARN 16c como burn-down.
- 🔴 **O gate `CONTRATO_REVOGADO` casa substring LITERAL.** O F117 provou: a s186 cadastrou a redacao do player e a do chat sobreviveu. Uma 4a parafrase passaria. A garantia e o rito de cadastrar TODAS as redacoes.
- **F113 PARCIAL** (#685/#689 intocados, residuo irregular). **F110** sem gate por construcao. **F78** e **F2** DECLARADOS nao-verificaveis com data de revisao.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB. 💉 Diretrizes 2026 a conferir: Calendario Vacinal, GINA, ATLS 11 (parcial), SINAN.
- 📡 **Canal com o `/ai-eng` = `SendMessage` entre sessoes locais** (descobrir com `ListAgents`). 🔴 **O endereco MUDA a cada sessao dele** -- responder sempre pelo `from` da mensagem mais recente. Hook grava em `history/exchange-log.jsonl`.
- 🔴 **Convencao que a janela escreveu, e o gate que a sustenta: regex sempre em string RAW.** Escrevi uma sequencia de escape numa string nao-raw por heredoc e gravei **backspace (0x08)** dentro de dois regexes do `selo.py` -- um deles fazia TODO achado RESOLVIDO aparecer como "SEM TERMINAL". O ledger ja registrava essa classe para o `audit_resumos` ("linter verde, check morto"). Virou `test_sem_caracter_de_controle` (BLOCK), **que me pegou repetindo o mesmo erro 10 minutos depois**.
- 🔴 **Ao responder item numerado do `/ai-eng`, casar por CONTEUDO, nunca por numero** -- os dois inventarios sao independentes.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_187.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md * Selo: `python tools/selo.py`*
