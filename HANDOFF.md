# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-09 -- S174 (Claude Code / Fable 5.1, sessao de ENGENHARIA com o `/ai-eng` ao lado): **ciclo A do destilado fechado** -- 5 hotfixes selados (F71 F88 F80 F85 F76), suite 413 -> 452, consolidacao vibeflow 10/10 sem regressao; A6 medido (dry-run), execucao e do operador*

> 🔴 **Engenharia so em sessao DEDICADA, contexto limpo dos dois lados.** A sessao autorizada em 09/09 **aconteceu (s174)**; a proxima e o **bloco B** (specs F81 + fila de reforja), GO ja dado, **so quando o operador abrir outra janela**. Janela de estudo nao toca engenharia. Semana de **ENAMED (dom 13/09)**: questoes, simulados e cards. **Ler `history/session_173.md §5`** -- a semana esta decidida pelo usuario.

## > Proximo passo imediato

1. 📥 **PROXIMA SESSAO = ESTUDO: ele vem com QUESTOES** (avisou no fechamento da s174). Provavelmente as listas de qua 09: Diarreia R (41) + Pneumonias Bact. T I (16) + Uro T I (20) + Pneumonias na Infancia T (24). Ordem dura: **`registrar_sessao_bulk` ANTES de analisar** -> `/analisar-questao` em **1 subagent por lote** -> cards sob o **teste de regenerabilidade**. ⚠️ Se as listas nao sairam, o `S17 verde` da s173 nao fechou -- perguntar, nao assumir. **Zero engenharia nessa janela.**
2. 🃏 **Qui 10:** fila FSRS (o balanceador agora conhece a prova: **13/09 zerado**, 48 cards em 12/09, **17 presos em 14/09** -- ver item 5.b). Alvo do usuario ~100 cards/dia qui-sex-sab (acima do teto 60/90; alerta dado na s173). Intake FIFO ate ele redefinir a regua de "card bom" **com ele** (F87).
3. 🎯 **Simulado 9 (qui) e 10 (sab):** `--area Simulado` direto no CLI; erros analisados no mesmo dia. Domingo: **ENAMED** = termometro.
4. 📚 **Backlog de conteudo:** 6 temas do Simulado 8 sem resumo (Doenca Hemorroidaria, Lesoes Hepaticas Focais, Abdome Agudo Obstrutivo, Farmacodermias, Esquistossomose, Liquido Amniotico) + s172 (Disturbios Resp. Neonatais, Infeccoes Congenitas, cerclagem).
5. 🧑‍⚖️ **Decisoes empilhadas do OPERADOR (o `/ai-eng` leva numa rodada so; ninguem decide por ele):** (a) **RODADA 3 do `normalize_taxonomia`** -- `docs/DRYRUN-F65-F67-2026-09-09.md` §4: 10 grupos duplicados (fundir?), 35 cards e 201 erros presos em `[bulk]` (tema real de cada um); (b) **17 cards em overflow no dia 14/09** (#321 #558 #788 #1187 #245 #706 #381 #823 #1479 #1159 #707 #553 #709 #419 #486 #632 #463) -- mover a mao para antes da prova ou deixar; (c) **backfill UTC->local** do historico de `review_time`/`data_registro`/`reviewed_at` (shift constante -3h; dry-run + COUNT por linhas que mudam de dia) -- sim/nao; (d) os de sempre: apagao do `/graphify`, contexto obrigatorio em card novo, F62/F55/F37, planilha ainda e fonte? (F35), **regua de "card bom" (F87)**.

## Fila de engenharia (proxima sessao DEDICADA; protocolo `AGENTE.md §10.6-8`, D71) -- ORDEM SELADA pelo `/ai-eng` em 09/09 (fechamento do ciclo A): o boot da proxima janela NAO re-deriva
0. **Inventario COMPLETO da divida = `docs/MEMORIA-AUDITORIA.md §11`** (4 tiers, pedido do operador: "resolver progressivamente"). Abrir a janela com o **Tier 3** (30 min: re-medir e marcar os 8 achados sem status F16-F20 F27 F28 F32), depois o Tier 0 abaixo.
1. **F80b como hotfix, PRIMEIRO** (mesma costura do F80 do lado do LEITOR): `get_cards_by_bucket`/`get_fresh_error_cards` comparam `fc.due` local com `datetime('now')` UTC -- fila mente 3h em 48h. Remedio: leitor unico de "agora" = `db.agora()`; varredura estrutural que falha nomeando o arquivo se um SELECT ainda usar `datetime('now')`. Teste = instante congelado as 22h local, card `due` 23h NAO pode aparecer como vencido.
2. **B1 -> B2 -> B4 (se <=1h) -> B3** (GO de 08-09/09): B1 spec **F81** (predicado contexto x pergunta; DoD por CADA um dos 7 writers; fixtures #1568/#1574 no 1o predicado; contador de gate-miss com classe lendo **`fsrs_revlog.reason_servido`** do F76) -> B2 spec **fila de reforja como estado** (`reforja_marks` lifecycle; #792 3x, #321) -> B4 F77/F77b -> B3 F35 (reporta, nao bloqueia, **com a IDADE da planilha**).
3. **F89 depois do B1:** o MECANISMO (`AREAS_VALIDAS` unica + fail-loud nos 3 writers de taxonomia + WARN no auto_check) e engenharia e nao depende do operador; a LISTA e conteudo dele (RODADA 3). Escrever a spec contra a lista atual; a RODADA 3 muda a lista, nao o mecanismo.
4. **Promote dos 3 stubs** (`.vibeflow/audits/2026-09-09-hotfix-consolidation.md`) = GO, loop local: contrato do calendario de provas (F71) · contrato da zona canonica LOCAL (F80) · `reason_servido` como campo do F81 (F76).
5. **Smell declarado, sem data:** `app/utils/db.py` importa `tools/card_checks.py` por `__file__`; mover = spec.

## Estado por frente

- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (53d). ENAMED 13/09 (**4d**) termometro.
- **Volume & Metas:** 7036 / 10400 (perf. ~79.0%). Hoje: 0. Ritmo-alvo ~63.5q/dia (53d p/ UERJ/MFC (prova 01/11)).
- **FSRS:** divida 0 atrasados + 9 p/ hoje -- pool 659 nunca introduzidos (entram <=60/dia).
- **Conteudo:** 136 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 987 erros registrados · 1395 cards ativos · 2 needs_qualitative na fila · taxonomia 286 temas. [derivado: db]
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem) [derivado: preparacao_estado]. Sprint "S20 ate 12/09" da s168 esta **morto**.
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario).

## Ultima sessao -- s174 (2026-09-09, tarde) -- ENGENHARIA (operador fora do terminal; `/ai-eng` conduziu)
**Ciclo A, ordem do `/ai-eng` (F71 -> F80 -> A5 -> F85 -> F76), 5 traces + 5 suites vermelhas antes de cada fix:** **F71** `015dac0` balanceador le `core/provas.json` (blackout = prova + 1 dia; alvo em blackout vai para ANTES; sem vaga = overflow declarado) + `fsrs_load.py --blackout [--apply]` (§10.7) -- **34 cards movidos no db real, 17 overflow**. **F88** `91c40e2` (A5 numerado) `performance.volume_vs_marco` e a unica conta de volume (`--gap` dizia 10000/6305, boot 10400/7036) + `app/utils/provas.py` leitor unico + overflow no boot. **F80** `37e0859` relogio unico `db.agora()` LOCAL nos 4 writers de carimbo -- **a ALTERA "UTC no db" do `/ai-eng` caiu** diante da evidencia de que o nucleo FSRS grava local; historico UTC declarado, backfill = operador. **F85** `f658e9f` gate de `card_checks` fail-loud (justificativa orfa da UI Streamlit removida). **F76** `b8929b3` `--record` recomputa o bucket e grava `reason_servido`; divergencia = WARN + SQL.
**Audit:** `vibeflow --consolidate-hotfixes` sobre 10 docs: 0 regressed, 3 promote, Critical Gate limpo. **A6:** dry-run medido -- o normalizador esta VAZIO para F65/F67 (RODADA 2 ja aplicada); arquivo p/ operador. **Estudo: nenhum** (sessao dedicada).

## Padroes de erro ativos (ultima medicao: s173, leitura de drill -- sem nova medicao na s174)
- 🔴 **Armadilha literal do card e o que ele marca** (6 cards) · 🔴 **Fato no contexto errado** / numero de protocolo vazando (hep B 3 -> triplice) · 🔴 **Ancoragem no achado saliente** (padrao-mestre) · 🔴 **No do fluxograma nao lido** + **clozapina x carbamazepina** (5o encontro).

## Pendencias/observacoes ativas
- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB: baixar uma vez resolve beta-hCG e cortes da PE.
- 🃏 Reforja: **#792 (3a marcacao)**, #582/#583 compostas, #243, #561, #321 (rated 4, defeito intacto) + passivo ~37 -- vira fila mecanica no B2.
- 🔬 Ledger: **abertos (11 F + 7 so-ESTADO + 2 D):** F35 F36 F42 F72 F77 F77b F78 F79b F81 F87 **F89** · F63-F69 · D5 D11. **Fechados na s174:** F71 F76 F80 F85 F88.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial), SINAN 2026.
- ⚠️ Drive 45d sem sync (F72); Dashboard EMED 6.288 x db 7.036 -- db e a fonte fiel (F35: planilha ainda e fonte? -> operador).
- 📚 **Frente MFC (Gusso + Duncan)** abre 14/09; rescope da grade pro formato UERJ.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_174.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
