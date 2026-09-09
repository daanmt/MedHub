# Destilado de engenharia -- 2026-09-09 (pos-s173), para o `/ai-eng`

Protocolo `AGENTE.md §10.6` (D71): **implement E audit sao do MedHub** (loop vibeflow); o `/ai-eng` orquestra sequencia e da GO/NO-GO/ALTERA. Silencio = GO. Cru: `AUDITORIA_MEDHUB.md` + `docs/MEMORIA-AUDITORIA.md`. ⚰️ Este arquivo e consumido ao fim da sessao de engenharia (auto-higiene §3.4).

## A. hotfix (defeito reproduzivel; teste de regressao ANTES do fix) -- ordem proposta
1. **F85** `db.py:765` -- `except` governado por premissa morta (justificativa orfa). Pequeno.
2. **F80** -- writers do `ipub.db` discordam de fuso: `fsrs_revlog`/`questoes_erros` em UTC, `sessoes_bulk` em local. Teste: 1 gravacao em cada, mesma hora, mesmo offset.
3. **F71** -- `fsrs_balance` nao le `core/provas.json`: empurrou cards para o dia seguinte ao ENAMED. Remedio: blackout do dia de prova (+1) na escolha do dia.
4. **F76** -- `fsrs_queue --record --reason` aceita proveniencia divergente do card servido. Remedio: WARN (nao BLOCK).
5. **NOVO s173 (sem F-id, G2)** -- `cronograma.py --gap` reporta meta 10000 / acumulado 6305 enquanto `day_plan` reporta 10400 / 7036: duas fontes para o mesmo numero (viola G4 "fonte unica"). Numerar e apontar `--gap` para `provas.json`/`MARCOS` + `sessoes_bulk`.
6. **F65 / F67** -- balde `[bulk] <Area>` (72 cards fora do radar) e taxonomia duplicada: `normalize_taxonomia.py` existe; falta rodar sob `§10.7` (COUNT-ASSERT + dry-run). Gatilho: operador.

## B. spec (lacuna de gate) -- GO ja dado em 08/09
1. **F81** predicado contexto x pergunta em `card_checks.py`. Fixtures: 3 originais + **#1568 e #1574 (s173)** = 5. DoD por CADA um dos 7 writers; "pergunta generica" so em CONJUNCAO com contexto pobre; eixo C declarado nao verificavel; contador de gate-miss (F79/F79b/F81).
2. **Fila de reforja como estado** (`reforja_marks` com lifecycle, nunca booleana; fechamento explicito). Fixture viva: **#792 marcado na s158, s166 e s173, nunca reforjado**; #321 v2 com defeito intacto.
3. **F35** reconcile W1 (planilha x db) manual -- s173 mostrou que o Dashboard esta em 6.288 e o db em 7.036 (o dono parou de lancar): o check deve **reportar**, nao bloquear.
4. **F77/F77b** `grade.json` sem contagem por tarefa (rateio erra 3x); `_parse_detail` ja extrai no s168 -- persistir no derivador.

## C. so-dado / decisao do operador (ninguem decide por ele)
- **F87** harness cego a rendimento: remedio e a **regua de "card bom" co-definida com o operador** (decisao s173: refinar a triagem na geracao, nao o teto). Spec so DEPOIS dessa sessao com ele.
- Contexto obrigatorio em card novo (49% do pool sem) -- WARN ou BLOCK no gate 0->1.
- Apagao do `/graphify` -- parado no passo 1 (fixture do check de alcancabilidade).
- Dry-run do lote 600-799 (132 cards) -- conteudo clinico, gatilho do dono.
- F62 rotacao do ledger (189 KB) · F55 · F37 historico · F63 (prioridade nao viaja com o repo) · F36/F72 (binario do Drive = ritual do usuario).
- F66 memoria de fraquezas 45% orfa por abreviacao (`memory_errors.log` 1027 linhas, hoje: "Pediatric Head Injury Assessment" fora do vocabulario) -- spec de vocabulario restrito (F45 reaberto na pratica).
- F78 figuras do PDF · F42 espelho revertido (WARN existe) · F68/F69 (taxonomia/diretrizes = conteudo).

## D. pedido ao `/ai-eng`
Sequencia proposta: **A1-A5 num unico ciclo de hotfixes** (5 traces, 5 testes) -> audit vibeflow -> **B1** -> **B2**. Responder GO / NO-GO / ALTERA por item, num envio. Duvida nova de escopo: perguntar antes de escrever.
