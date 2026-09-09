# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-09 -- S173 (Claude Code / Fable 5.1): **109 cards drenados**; a coorte do Simulado 8 estreou em **43%** (2x a media de estreia); re-drill ganhou a **regra do corte do loop**; Simulado 8 registrado (**7.036**); RAG reindexado; 3 cards reforjados + 2 aposentados*

> 🔴 **A FILA DE ENGENHARIA SEGUE CONGELADA** por decisao do operador -- retoma em sessao dedicada, contexto limpo dos dois lados. Esta e semana de **ENAMED (dom 13/09)**: questoes, simulados e cards. **Ler `history/session_173.md §5` antes de agir** -- a semana esta decidida pelo usuario.

## > Proximo passo imediato

1. 📥 **ERROS DAS LISTAS DE HOJE (qua 09):** ele saiu para Diarreia R (41) + Pneumonias Bact. T I (16) + Uro T I (20) + Pneumonias na Infancia T (24) e volta com os erros. Ordem dura: **registrar volume por area (`registrar_sessao_bulk`) ANTES de analisar** -> `/analisar-questao` em **1 subagent por lote** (nao fan-out) -> cards sob o **teste de regenerabilidade** (`estilo-flashcard` §Triagem). Diarreia e o teste de que a correcao da s172 (virgula que virava conjuncao no criterio de ATB) pegou.
2. 🃏 **Amanha (qui 10):** fila FSRS ~64 vencidos + 3 reforjados sem nota (#367, #1568, #1574) + 8 em relearning. Alvo do usuario: **~100 cards/dia qui-sex-sab** (acima do teto 60/90 do contrato; alerta dado 1x na s173, **ele discordou da mitigacao por prevalencia** -- ver §5 do log). Intake segue FIFO ate ele redefinir a regua de "card bom" **com ele**.
3. 🎯 **Simulado 9 (qui) e Simulado 10 (sab manha):** registrar como `--area Simulado` direto no CLI (a planilha NAO tem aba de simulado preenchida; precedente s167/s173). Erros viram analise no mesmo dia. Domingo: **ENAMED** = termometro de execucao, nao de conteudo.
4. 📚 **Backlog de conteudo (nao executado):** 6 temas do Simulado 8 **sem resumo no repo** -- Doenca Hemorroidaria, Lesoes Hepaticas Focais, Abdome Agudo Obstrutivo (PDF existe), Farmacodermias (PDF existe), Esquistossomose, Liquido Amniotico. Mais os da s172: Disturbios Respiratorios Neonatais, Infeccoes Congenitas, cerclagem/prematuridade.
5. 🔧 **Engenharia: sessao dedicada AUTORIZADA pelo operador (09/09, tarde)** -- ele abre janela limpa aqui com o `/ai-eng` ao lado. **Ler nesta ordem:** [`docs/MEMORIA-AUDITORIA.md`](docs/MEMORIA-AUDITORIA.md) -> [`docs/DESTILADO-ENG-2026-09-09.md`](docs/DESTILADO-ENG-2026-09-09.md) (A: 6 hotfixes · B: 4 specs c/ GO · C: decisoes do operador). **D71:** implement E audit daqui (vibeflow: hotfix/spec/implement/audit); `/ai-eng` orquestra; silencio = GO. O destilado e **consumido** (deletado) no selo da sessao de engenharia.

## Fila de engenharia acordada com o `/ai-eng` (GO dado, nao executada)
Protocolo em `AGENTE.md §10.6-8`: destilado <=3k + remedio por achado -> GO/NO-GO/ALTERA.
- **Spec F81** -- predicado contexto x pergunta em `card_checks.py`; DoD por CADA um dos 7 writers; pergunta generica so como CONJUNCAO; eixo C declarado nao verificavel. **s173 achou mais 2 fixtures de F81:** #1568 e #1574 (contexto de um dx, pergunta sobre o outro).
- **Spec da fila de reforja** -- `reforja_marks` com lifecycle (nunca booleana). **#792 foi marcado pela 3a vez (s158/s166/s173) e nunca reforjado** -- e a prova viva de que a prosa nao e fila.
- **Dry-run do lote 600-799** sob `§10.7`; gatilho do operador.
- **4 achados de 08/09 sem F-id** (G2) · **Pendente do operador:** apagao do `/graphify` (nao aprovado) · contexto obrigatorio em card novo.

## Estado por frente

- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (53d). ENAMED 13/09 (**4d**) termometro.
- **Volume & Metas:** 7036 / 10400 (perf. ~79.0%). Hoje: 0. Ritmo-alvo ~63.5q/dia (53d p/ UERJ/MFC (prova 01/11)).
- **FSRS:** divida 0 atrasados + 9 p/ hoje -- pool 659 nunca introduzidos (entram <=60/dia).
- **Conteudo:** 136 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 987 erros registrados · 1395 cards ativos · 2 needs_qualitative na fila · taxonomia 286 temas. [derivado: db]
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem) [derivado: preparacao_estado]. **S17 verde fecha hoje** se as 4 listas sairem; sprint "S20 ate 12/09" da s168 esta **morto** (115 de 725 feitas).
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario).

## Ultima sessao -- s173 (2026-09-09, manha)
**Drill:** 65 vencidos + 44 do Simulado 8, 10 blocos de 11. **57x4 · 22x3 · 4x2 · 22x1**, retencao 54%. **Coorte S8: 43%** (novos 44%, erros frescos 38%) contra 22%/25% da s169 -- **o corte de regenerabilidade dobrou a estreia**. Cauda: **Imunizacoes 3 de 4 em nota 1** no mesmo dia da analise (erro 14 do S8 voltando; "3 doses" da hepatite B vazando para a triplice viral). Resumo expandido com a conta do resgate.
**Re-drill:** 26 cards nota 1-2, 23 sairam em 2 passagens; 3 travaram em "nao lembro" -> **regra do corte do loop** (2x "nao lembro" = sai do loop, reonboarding curto na Revisao Direcionada) gravada em `revisar.md` + memoria. **Revisao Direcionada** em 6 eixos; 11 temas carimbados; 5 notas `fonte='aula'`.
**Cards:** #365 e #610 aposentados a pedido; #367/#1568/#1574 reforjados (ratchet do verso barrou a 1a versao do #1568 -- funcionou). Defeitos reportados: #792 (3a vez), #582/#583 compostas, #1381/#1080/#421 binarias.

## Padroes de erro ativos (ultima medicao: s173, leitura de drill)
- 🔴 **Armadilha literal do card e o que ele marca** (6 cards: antifungico p/ VB, grau III com lesao vascular, HPV 2 doses, ceftriaxona 1 g, esquisto 1 semana, operar CCR sem estadiar).
- 🔴 **Fato no contexto errado** ("isodenso" dado na pancreatite, depois certo na coledocolitiase) e **numero de um protocolo vazando para outro** (hep B 3 -> triplice).
- 🔴 **Ancoragem no achado saliente** (DM1 -> glicose em vez de via aerea; "UTI sem calculo" -> colecistite sem contar A+B). Padrao-mestre segue.
- 🔴 **O no do fluxograma nao e lido** (s170, 5 areas) e **clozapina x carbamazepina** (5o encontro) -- sem nova medicao.

## Pendencias/observacoes ativas
- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB: baixar uma vez resolve beta-hCG e cortes da PE.
- 🃏 Reforja: **#792 (3a marcacao)**, #582/#583 compostas, #243, #561, #321 (rated 4 hoje, defeito intacto) + passivo ~37.
- 🔬 Ledger: **abertos (21 F + 2 D):** F87, F85, F81, F80, F79b, F78, F77b, F77, F76, F72, F71, F42, F36, F35 · F63-F69 · D5, D11.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial), SINAN 2026.
- ⚠️ Drive 45d sem sync (F72); Dashboard EMED mostra 6.288 (ciclo regular) x db 7.036 -- o usuario parou de lancar na planilha; db e a fonte fiel.
- 📚 **Frente MFC (Gusso + Duncan)** abre 14/09; rescope da grade pro formato UERJ.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_173.md * Trocas: history/exchange-log.jsonl*
