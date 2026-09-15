# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-15 (noite) -- **s182 (ESTUDO)**: **ENAMED 2026 real = 75/100** (prova de 13/09), gabarito comentado das 100 questoes publicado, 25 erros persistidos com racional declarado (44 cards), 13 acertos-no-chute no ledger, 15 resumos com armadilhas novas. Volume **7.226 -> 7.326**.*

> 🔴 **RECURSOS DO ENAMED ATE 17/09 (acao do usuario).** As dele: **Q68** (pelve: angioembolizacao, nao "estabilizacao cirurgica") e **Q75** (epiglote "rigida" -- anulacao), mais **Q6** (A/C). Tambem cabem Q48 (PrEP 2025 = 7 dias), Q5 e Q99. Fundamentos por questao no artifact: https://claude.ai/artifact/TuXkndfMBRRjpErzM2fWEJ (copia em `artifacts/enamed-2026-comentado.html`). Permit de engenharia segue **CONSUMIDO**.

## > Proximo passo imediato

1. 🃏 **Divida FSRS: 78 atrasados + 28 de hoje = 106 vencidos** (o blackout de 13-14/09 caiu hoje); teto 90 em regime de divida. **Re-sondar #787 (hiperaldosteronismo) e #597 (Winter)** antes de ensino novo (herdado da s181). Os 44 cards do ENAMED estao no **pool (685)**, nao na fila vencida.
2. 🗓️ **Rescope UERJ + abertura da frente MFC (atrasado desde 14/09).** A prova real confirmou o miolo: **29/100 de Preventiva/APS**, cenario de UBS na maioria das demais, RAPS/indicadores/PrEP cobrados por portaria. Insumo: `artifacts/raio-x-simulados.html §3` + `history/session_182.md §2`.
3. 📚 **8 temas SEM RESUMO cairam no ENAMED:** RAPS, Anafilaxia (adulto), FA/Arritmias, Osteoporose, HPB/PSA, Oncologia pediatrica (Wilms x neuroblastoma), Coqueluche, TEA. Criar na ordem do peso UERJ (RAPS e APS primeiro). Farmacodermias e Vulva/Vagina seguem sem lastro.
4. 🔴 **Cluster = aula comparativa, nao cards (2a evidencia, s182).** Q52: *"fiz tantos cards de wilms x neuroblastoma e perdi uma questao de graca"*; Q53: Cirurgia Infantil com 53 cards caiu numa facil. Wilms x neuroblastoma e hernia x hidrocele x criptorquidia pedem tabela lado a lado na aula, nao mais cards.
5. 🔴 **Eixo nefro = tema-zero DECLARADO** (nota 9 `usuario` em Acido-Base e Potassio; herdado). Quando a grade chegar: `/aula-base` D9-D10 com onboarding do zero.
6. 🔴 **Reforja: 283 abertas** (sem marca nova nesta sessao). Triar e do operador.

## Fila de engenharia -- TIER 0 e 1 ZERADOS; permit consumido. Inventario: `docs/MEMORIA-AUDITORIA.md §11`

- 🧑‍⚖️ **Abertos:** **F98** (blackout so ve intervalo >= 4d -- **materializou hoje: 78 atrasados**) · **F99** (sem CLI por id -- a s182 leu ids por SELECT read-only) · **F100** (re-ensino nao fecha fato arbitrario; 4a medicao pendente no re-drill) · **F101-F105** (herdados). 🆕 **F106** `[SEM-LASTRO]` falso por NOME de tema outra vez (`Infecto/Esquistossomose` -> conteudo em `Parasitoses.md`; classe F103) · **F107** o gate `resposta-embutida` so acusa no writer -- **2 rollbacks** do lote hoje ate o pre-check com `card_checks.checar_resposta_embutida(card, {"titulo": ...})`; `insert_questao.py` nao tem `--dry-run`.
- 🔜 **Janela 4 (decidida pelo `/ai-eng`):** smell `db.py -> tools/card_checks` por `__file__`; por spec.
- 🧑‍⚖️ **Decisoes empilhadas do OPERADOR:** (a) `reforja.py --backfill --apply`; (b) RODADA 3 do `normalize_taxonomia` (8 temas novos entraram hoje); (c) overflow -> 15/09+ (aconteceu); (d) backfill UTC->local; (e) `--new-limit` x pool; (f) areas fantasma; (g) F64; (h) rotacao do ledger (~263 KB); (i) F57 lote de ESTUDO; (j) `/graphify`, F35, F87.

## Estado por frente

- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (47d). **ENAMED 13/09 FEITO: 75/100** (termometro; abaixo da serie S6-S9).
- **Volume & Metas:** 7326 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~65.4q/dia (47d p/ UERJ/MFC (prova 01/11)). 🔴 A grade NAO fecha a meta.
- **Simulados:** 9 provas + ENAMED real · S6 80 · S7 82 · S8 82,1 · S9 86 · **ENAMED 75**. Serie: 264 erros. ENAMED: 62 solidas / 13 chute / 25 erradas; Cardio 3/5, Preventiva 5/29.
- **FSRS:** divida 78 atrasados + 28 p/ hoje -- pool 685 nunca introduzidos (entram <=90/dia). **s182: 44 cards novos (ids 1630-1673); zero drenagem hoje.**
- **Conteudo:** 136 resumos em resumos/. [derivado: glob] **+15 resumos com 2-3 armadilhas do ENAMED.** Sem lastro: 8 temas do ENAMED + Farmacodermias + Vulva/Vagina.
- **Erros & Cards:** 1041 erros registrados · 1476 cards ativos · 2 needs_qualitative na fila · taxonomia 302 temas. [derivado: db] Reforja: **283 abertas**. Ledger: +6 padroes com `--questao-id`, +13 `incerteza`.
- **Engenharia:** suite 621 · `auto_check --changed` PASSED · ledger **109 ids** (F106, F107 novos).
- **Posicao:** conteudo S17 (nominal S25, atraso 8 sem) [derivado: preparacao_estado]
- **Datas:** fim da grade 09/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario). Recurso ENAMED ate **17/09**.

## Ultima sessao -- s182 (2026-09-15, 12h -> 19h) -- ESTUDO

Detalhe integral em `history/session_182.md`. 📄 **Gabarito comentado das 100** via 5 subagentes Opus em paralelo (794k tokens, ~25 min): 94 CONCORDA / 6 CONTESTAVEIS; 2 claims re-medidos pelo principal (PCDT PrEP 2025 = 7 dias; ATLS 11 = 3 mL x kg x %SCQ em 16 h). 🔴 **Os 25 erros com a letra dele:** discriminador **identificado e nao usado** (Q19, Q37, Q40 -- *"circulei os 3 dias... mas nao os utilizei"*) vira sub-estado do padrao-mestre; override do modal declarado na Q69; 2 fatos FALSOS carregados (hernia infantil "fecha", "triciclico nunca em idoso"); Q19 = reincidencia da ectopica da s085. 44 cards de 57 candidatos (13 cortados pelo teste de regenerabilidade); 3 erros `banca-divergente` sem card. Custo total de subagentes: **6 spawns, ~1,03M tokens, ~53 min**.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- **ENAMED sem distribuicao de candidatos:** o override do modal e n=1 DECLARADO (Q69), nao medido; "8 faceis perdidas" e proxy.
- **F100 4a medicao:** pendente (re-drill de 15/09 nao aconteceu). **F98** materializou (78 atrasados). **F7/F104:** classes semanticas, nao-verificaveis por gate.
- **D5** mede presenca, nao semantica · **G10** isenta por LINHA · **G5** sensivel a arquivo novo · gate de revogacao casa substring literal.
- Herdadas e vivas: **F35** · **F89** · **F79b** · **F66** (34% de orfandade) · **F64** · eixo C do **F81** · sitios gemeos do **F80b**.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB: baixar uma vez resolve beta-hCG e cortes da PE.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial -- queimados ja conferido), SINAN 2026.
- ⚠️ Drive 50d sem sync (F72); Dashboard EMED x db medido pelo boot (F35).
- 📡 Canal com o `/ai-eng` em `history/exchange-log.jsonl`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_182.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
