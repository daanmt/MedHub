# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-10 -- **S177 (ENGENHARIA, janela 2)**: Tier 0 FECHADO + 4 itens do Tier 1, suite **503 -> 578**, **0 spawns**. HEAD `de9596f`, main == origin/main.*

> 🔴 **A janela 2 fechou no 1.4, por teto de contexto -- nao por fim de fila.** **Semana de ENAMED (dom 13/09): questoes, simulados e cards.** A engenharia so recomeca quando o operador abrir outra janela; a fila abaixo **NAO se re-deriva**, ja esta ordenada.

## > Proximo passo imediato

1. 🃏 **VOLTAR AO ESTUDO.** Re-drill dos **12 cards nota 1-2 da s175** (so as frentes; **nao gravar FSRS** -- e consolidacao) + fila FSRS do dia + intake novo.
2. ❓ **DUAS PERGUNTAS ABERTAS da s175**, curtas, na abertura: (a) **fork da PAC Q3** -- *"quando voce marcou A, estava afirmando que o pneumococo NAO e o agente mais provavel naquele etilista diabetico, ou marcando a que achou verdadeira?"*; (b) **valores laboratoriais da Uro II Q2** (eram imagem) -- se havia relacao PSA livre/total, o gabarito fecha sem depender do corte NAO-VERIFICAVEL.
3. 🎯 **Simulado 9 (qui) e 10 (sab):** `--area Simulado` direto no CLI; erros analisados no mesmo dia. Domingo: **ENAMED** = termometro.
4. 🆕 **O boot mudou de cara (s177).** Duas linhas novas no Plano do Dia: **`Planilha x db (W1/F35)`** -- hoje diz `NAO MEDIDO` e vai dizer isso ate alguem gravar o snapshot ao ler o Drive -- e o **saldo do teto** (`usados/teto`). E o gatilho do regime de divida agora e **`vencidos = atrasados + hoje`** (F64), nao mais so `atrasados`.
5. 📚 **Backlog de conteudo:** 6 temas do Simulado 8 sem resumo (Doenca Hemorroidaria, Lesoes Hepaticas Focais, Abdome Agudo Obstrutivo, Farmacodermias, Esquistossomose, Liquido Amniotico) + s172 (Disturbios Resp. Neonatais, Infeccoes Congenitas, cerclagem). **395 PDFs / 135 `.md` / 327 orfaos** (`cobertura_conhecimento.py`, so `/extrair-pdf` o alcanca -- F16).

## Fila de engenharia -- ORDEM SELADA, o boot NAO re-deriva. Inventario: `docs/MEMORIA-AUDITORIA.md §11`

- ⚰️ **FEITO na s176:** 0.0 (F93+F90) · Tier 3 · 0.1 (F80b) · 0.1b (F91) · 0.2 (B1/F81) · 0.3 (B2) · 0.4 (B4/F77+F77b).
- ⚰️ **FEITO na s177:** **0.5** (B3/F35) · **0.6** (F89 + rider F94) · **0.7** (promotes x3 + 6 cabecalhos corrigidos) · **1.1** (F79b) · **1.2** (F64 + rider F95) · **1.3** (F66) · **1.4** (F42). **Tier 0 ZERADO.**
- 🔜 **Tier 1, retomar em:** **1.5 F7** (heuristica de competidor: medir precisao sobre a base -> promover a BLOCK ou matar) -> **1.6 F39** (40% do baralho nao-atomico; fila mecanica, reforja e do operador) -> **1.7 D5** (CLIs sem assinatura canonica em skill) -> **1.8 varredura unica** (G5 · G6 · G10 · G11 · G3 · G1/G8 · D11 · **(ii') do F90** · **G14 novo: CHECK cabecalho x lapide do §11** · **derivar `_PORTADORES_NORMA`, F95**) -> **1.9 sem data**. **1.10 segue CANDIDATO, aguardando GO do OPERADOR.**
- 🧑‍⚖️ **Decisoes empilhadas do OPERADOR:** (a) `reforja.py --backfill --apply` (9 linhas em dry-run); (b) **RODADA 3** do `normalize_taxonomia` -- agora com **18 linhas fantasma medidas** (39 cards + 33 erros); (c) 17-19 cards em overflow no 13-14/09; (d) backfill UTC->local; (e) `--new-limit` x pool 671; (f) 🆕 **`Oncologia`/`Urologia`/`Radiologia`/`Medicina de Emergencia` sao areas?** (F66 mediu a classe inteira; a lista e dele, `core/areas.json`); (g) 🆕 **F64 mudou politica de estudo** -- teto pode ir a 90 em dias que seriam 60; fonte = a posicao dele na s162, e o `/ai-eng` leva o efeito a ele; (h) os de sempre: apagao do `/graphify`, planilha ainda e fonte? (F35), regua de "card bom" (F87), F62/F55/F37.

## Estado por frente

- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (52d). ENAMED 13/09 (**3d**) termometro.
- **Volume & Metas:** **7126** / 10400 (perf. ~79.0%). Ritmo-alvo ~63.0q/dia.
- **FSRS:** divida 0 atrasados + 4 p/ hoje -- pool **671** nunca introduzidos (entram <=60/dia).
- **Conteudo:** 136 resumos. **Cobertura medida: 327 temas com PDF e sem `.md`.**
- **Erros & Cards:** **1002** erros · **1419** cards ativos · taxonomia **288** temas.
- **Engenharia:** suite **578** · `auto_check --changed` PASSED · ledger **97 ids** · **12 hotfix docs nao consolidados** (`audit --consolidate-hotfixes`).
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem).
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario).

## Ultima sessao -- s177 (2026-09-10, noite/madrugada) -- ENGENHARIA

**Permit do operador, verbatim: "Vamos continuar a sessao de engenharia ate o final, pois nao irei estudar mais hoje"**. Detalhe integral em `history/session_177.md`.
🔴 **O fio do dia: QUATRO fixtures da ordem nao reproduziam mais** -- o #367 do F79b foi reforjado; o `6.288` do Dashboard nao tem data nem comando; o passivo do F89 cresceu (7 -> 18 linhas); e a direcao (d) do F66 **deixou de existir** porque o 0.6, tres horas antes, trocou a fonte do vocabulario. **Regra:** *fixture que cicatriza e DADO, nao motivo de parada* -- desde que a CLASSE siga real e o remedio seja prospectivo.
**Tres achados de graca:** **F94** (2 CLIs sequestravam o stdout global no `import`, irmaos de defeito ja consertado, invisiveis porque nenhum teste os importava) · **F95** (o registro de PORTADORES do gate era manual e tinha buraco: o contrato FSRS carregava um `PREPARAR` prescritivo, clausula ⚰️ **revogada** na s170 -- **o F90 um nivel acima**) · **o byte invisivel** (13 `\b` viraram backspace literal num heredoc: `sed`/`grep` nao mostram, a suite fica verde, o predicado nunca casa nada).
**Dois defeitos meus**, ambos pegos **conferindo o numero do painel DEPOIS da suite** -- que ficou verde nas duas vezes.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- **F35:** fidelidade do snapshot ao Drive **nao verificavel** enquanto o F36 nao tiver transporte -- valida-se coerencia interna, nunca fidelidade.
- **F89:** o gate e de **vocabulario**, nao de **verdade** (Apendicite sob `Pediatria` passa em tudo).
- **F79b:** mede **ausencia** de vinheta, nao suficiencia; FP 0 vale para os **1419 cards que existem**.
- **F66:** **34% de orfandade permanece**; o efeito no ranking do boot **nao foi medido** (aparece so na proxima consolidacao).
- **F64:** o agravante da sessao que cruza a meia-noite **nao** foi resolvido -- sintoma legivel, nao sensor.
- **Eixo C do F81** e **faixa 0.55-0.79** do contexto-redundante seguem como na s176; **#792 e sentinela**.
- **Sitios gemeos do F80b em `tools/`** (`audit_fsrs.py`, `variancia.py`) seguem deferidos.

## Pendencias/observacoes ativas

- 🃏 **Reforja:** `python tools/reforja.py --fila` e a **unica cifra citavel** do passivo.
- 📊 **Painel novo:** `vocab de memoria: 100 WeakArea(s) sem area canonica` -- conta **item aberto**, nao linha de log (F66).
- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB: baixar uma vez resolve beta-hCG e cortes da PE.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial), SINAN 2026.
- ⚠️ Drive 46d sem sync (F72); Dashboard EMED x db -- agora **medido pelo boot**, nao por memoria (F35).
- 📚 **Frente MFC (Gusso + Duncan)** abre 14/09; rescope da grade pro formato UERJ.
- 📡 Canal com o `/ai-eng` N=78 em `history/exchange-log.jsonl`. Portador dele: `C:/Users/daanm/ai-eng/brain/interactions/2026-09-10-handoff-medhub-reforma-subagents.md`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_177.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
