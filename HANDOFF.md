# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-18 (noite) -- **s187 (ENGENHARIA, janela 6)**: a reforma de engenharia fechou com **SELO DERIVADO** e, na sequencia, o operador **resolveu os gates**. **14 commits, harness verde em cada um, suite 858 -> 924, ZERO subagentes.** 4 achados novos (F115 F116 F117 **F118**), 6 fechados, 14 cabecalhos mentirosos corrigidos. 🔴 **Ele tambem derrubou uma premissa de ESTUDO que nenhum gate pegaria -- ver o item 2 abaixo.***

> 🔒 **O SELO:** `python tools/selo.py` -- **0 item sem terminal, 0 discordancia**. 100 achados: 81 FEITO · 5 SUPERADO · 5 PARCIAL · 1 FEITO(parcial) · **2 GATE do operador**. A tabela e **DERIVADA** (ledger + `git log` + `clausulas_check` + `consistencia_check` + docstring das suites), nunca digitada. `--markdown` para colar; `--sensores` para o escopo que cada sensor declara NAO alcancar.

## > Proximo passo imediato

1. 🔴 **A PROXIMA SESSAO E DE ESTUDO, nao de engenharia** (ordem do operador). Pauta, na ordem dele: revisao do **cronograma** e das tarefas abertas -> **adotar o cronograma EXTENSIVO do Estrategia MED** -> levantar **temas ja estudados x faltantes** -> planejar **questoes e cards ate 01/11**.
2. 🔴 **PREMISSA DE ESTUDO DERRUBADA POR ELE (18/09), e ela muda a alocacao de esforco.** O plano super-pondera **MFC**, e a UERJ tem **peso IGUAL entre as 5 areas** (20 questoes cada, Edital 2027). Medido:

   | Guia Estatistico (Estrategia MED, 2017-2023, N=835) | Edital 2027 |
   |---|---|
   | Cirurgia 13,89% · Pediatria 13,17% · Preventiva 11,50% | **20% cada** |
   | GO (gineco 10,42 + obst 8,62) = 19,04% | **20%** |
   | CM fatiada em 9 subespecialidades ~ **36%** | **20%** |

   O guia mede **incidencia historica por tema**, nao a **estrutura da prova** -- sub-representa Cirurgia, Pediatria e MFC e infla CM em ~16 pontos. **Quem aloca esforco por ele estuda uma prova que nao existe.**
   🔴 **Segundo defeito, da nossa casa:** a unica analise por edicao feita sobre os **cadernos originais** e a de MFC (`simulados/uerj/UERJ_MFC_por_edicao_2021-2026.md`, 104 questoes). **As outras 80 questoes de cada prova nao tem mapeamento nenhum.** A profundidade foi para o bloco de 20% que parecia novo, nao para os 80% que decidem a aprovacao.
   **Material disponivel, medido: 6 edicoes (2021-2026)** em `simulados/uerj/`, nao 10 -- as de 2019/2020 sairam do ar na Cepuerj. Ele pretende **resolver as provas**, entao os PDFs valem duas vezes (mapeamento + simulado).
   **Classe:** *unidade de medida errada* -- o instrumento existe, mede, e o que mede nao e o que a decisao precisa. Nenhum gate de engenharia acha isso; quem achou foi o olho dele, como no F115.
3. 🔺 **2 GATES seus seguem abertos** (os outros 4 foram resolvidos em 18/09):
   - **F87** -- quais cards pagam aluguel? O eixo IRMAO ganhou sensor (`cards_rendimento.py`), mas ele **nao alcanca** o achado: os 13 cards que voce cortou nunca entraram no baralho.
   - **F111/R8** -- decision brief de 10 linhas **entregue** no ledger. Decidir **na proxima sessao**, junto da adocao do extensivo: e ai que o defeito morde. Risco nomeado: 465 tarefas de teoria x 5 cards = 2.300 cards se a triagem afrouxar.
   - ⏳ **Validacao clinica do `TCE.md` reescrito** segue com voce (eu garanto forma, nao verdade).
4. 🃏 **Cards:** divida **72 atrasados + 31 p/ hoje**, pool 690. Fila de reforja **308 abertas**. 🔺 **48 candidatos de baixo rendimento** (`cards_rendimento.py`) -- #70 com 11 revisoes e stability 0,67d; 2 dos 6 piores sao de Polipos, area de fundacao ausente (pede **andaime**, nao reforja). 🔴 **Aula-base D10 de Acido-Base + Potassio ANTES de re-drillar os 6 segurados** (#595 #596 #598 #783 #786 #787).
5. 📚 **Questoes (Fase 1, semana 1 = 14 tarefas, 369q):** `plano.py --listar --semana 1`. Bulk -> `plano.py --concluir ID --sessao <id>`; erros -> Autopsia.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (44d; **inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7326 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~69.9q/dia (44d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 9 provas + ENAMED real 75. Proximo slot ~10/10 (cadencia de 4 semanas).
- **FSRS:** divida **72 atrasados + 31 p/ hoje** -- pool 690 nunca introduzidos (entram <=90/dia). Regua **v2** desde 18/09; revlog misto (3.067 v1 + 3 v2). Parametros seguem DEFAULT por decisao (F114).
- **Conteudo:** **135 resumos** (stub `[CIR] TCE.md` removido em 18/09). `Neurologia/TCE.md` **reescrito** (F104) -- pendente de validacao clinica dele.
- **Erros & Cards:** 1041 erros · **1512 cards ativos** (+5 do split do F105) · 0 needs_qualitative · taxonomia 302 temas. Reforja **308 abertas**.
- **Cronograma:** `plano_tarefas` = SSOT unica (Drive congelado na part-8). Visao consolidada: o painel.
- **Engenharia:** suite **924**; `auto_check` PASSED; ledger ate **F118**. **Selo: 100 achados, 2 ABERTOS** (F87, F111), ambos GATE nomeado -- `python tools/selo.py`. **Item 1.10:** 247 clausulas normativas -- **53 com CHECK · 69 declaradas · 125 orfas (49,4%)**. Os 4 portadores centrais estao **100%**: `analisar-questao` 28/28 · `revisar` 30/30 · `AGENTE` 41/41 · `revisao-calibrada` 50/50. Maiores orfaos restantes: `estilo-flashcard` 21 · `engenharia-cli` 18 · `cronograma-contract` 18 · `estilo-resumo` 17.
- **Posicao:** plano semana 1 (fase 1) · 0/14 tarefas da semana feitas [derivado: plano_tarefas]
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** (inscrito) · 📊 **Painel** (regenerar no fechamento, MESMA url): https://claude.ai/artifact/QctZqVoJriSviJetF8FYBQ

## Ultima sessao -- s187 (2026-09-18) -- ENGENHARIA, janela 6 (selo da reforma)

Detalhe em `history/session_187.md`. **ZERO subagentes** (nenhum lote passou o limiar do F93). Todo fix nasceu com teste antes do codigo; em 4 casos o teste pegou defeito meu antes do commit. 🔴 **A janela inteira tem UMA pergunta:** *o sensor alcanca exatamente o que diz alcancar?* -- **F115** (escopo MENOR que o necessario), **Invariante A** (sensor mirando a coisa vizinha), **G14b** (sensor olhando o registro vizinho), **F116** (escopo MAIOR que o declarado). Quatro faces, quatro gates novos.

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
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_187.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md * Selo: `python tools/selo.py`*
