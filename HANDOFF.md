# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-12 (tarde) -- **s181 (ESTUDO)**: sabado de descanso com **113 cards** (fila vencida ZERADA + intake dos dormentes), eixo **nefro declarado nota 9**, pendencia fantasma de Diarreia desfeita, **Revisao dos Top-Erros** publicada. Volume inalterado em **7.226**.*

> 🔴 **ENAMED e AMANHA (dom 13/09) -- termometro, nao alvo.** Uma instrucao: **quando restarem duas, marca a que a analise apontou** (`docs/PLAYBOOK_EXECUCAO_PROVA.md` item 7). Ler de manha o artifact **Revisao dos Top-Erros** (14 temas D5-7 + 9 padroes): https://claude.ai/code/artifact/13609541-3e16-4599-9f48-b0501ac76b6e (copia em `artifacts/revisao-top-erros.html`). Permit de engenharia **CONSUMIDO**; janela 4 so com permit novo, verbatim, via `/ai-eng`.

## > Proximo passo imediato

1. 🎯 **Domingo: ENAMED.** Regra dos dois finalistas. Cards do dia 13-14 reaparecem dia 15 como atrasados (F98) -- **inclusive os 29 nota 1 de hoje**. Deixar.
2. 🗓️ **Segunda 14/09 = DECISAO:** rescope da grade para o formato UERJ (Clinica Medica 27% -> 20%, **MFC 6,7% -> 20% com zero questoes/cards/erros**), abertura da frente MFC (Gusso + Duncan) e **quais ~460 dos 641** nunca-introduzidos entram ate 01/11. Insumo: `artifacts/raio-x-simulados.html` §3.
3. 🃏 **Terca 15/09 = dia de divida** (~55 agendados + 29 do blackout; teto 90). **Re-sondar #787 (hiperaldosteronismo) e #597 (Winter)**, que travaram 2x no re-drill, ANTES de novo ensino. Os 3 nao gravados por defeito (#686, #784, #599) so voltam reforjados.
4. 🔴 **Eixo nefro = tema-zero DECLARADO** (nota 9 `usuario` em Acido-Base e Potassio; memoria `user_nefro_gasometria_dificuldade_declarada`). Quando a grade chegar em Nefrologia: `/aula-base` D9-D10 com onboarding do zero, escada fixa (HCO3/BE -> AG -> Winter -> gap osmolar).
5. 📚 **Conteudo sem lastro REAL:** Farmacodermias (DRESS falhou s179 x2 + s181) e Doencas de Vulva e Vagina (so PDF + cards.json). ⚰️ **Polipos e Neoplasias Intestinais TEM resumo** (`Polipose Intestinal e Cancer Colorretal.md`, 146 linhas) -- o `[SEM-LASTRO]` da s180 era falso por nome (F103). `Neurologia/TCE.md` esta coloquial e `[CIR] TCE.md` e stub (F104): reescrever, nao card.
6. 🔴 **Reforja: 283 abertas** (272 + 11 marcas da s181: 6 compostas, 1 frente nao autossuficiente, 1 frente/verso desconversam, 1 ambigua, 1 pacote, 1 taxonomia). Triar e do operador.

## Fila de engenharia -- TIER 0 e 1 ZERADOS; permit consumido. Inventario: `docs/MEMORIA-AUDITORIA.md §11`

- 🧑‍⚖️ **Abertos:** **F98** (blackout so ve intervalo >= 4d) · **F99** (sem CLI por id) · **F100** (re-ensino nao fecha fato arbitrario -- **3a medicao s181:** cairam de novo no drill, fecharam 4/4 no re-drill pos-mecanismo; testar em 15/09) · 🆕 **F101** (pendencia fantasma no HANDOFF sobreviveu 2 sessoes sem medir) · 🆕 **F102** (hook de drift: regex case-sensitive, falso positivo -- **hotfix de 1 linha**) · 🆕 **F103** (`[SEM-LASTRO]` falso por nome de tema) · 🆕 **F104** (TCE.md coloquial) · 🆕 **F105** (6 compostas antigas fora do alcance do WARN por 47 dias). Candidato s180: backfill do override no ledger de habilidades.
- 🔜 **Janela 4 (decidida pelo `/ai-eng`):** smell `db.py -> tools/card_checks` por `__file__`; por spec.
- 🧑‍⚖️ **Decisoes empilhadas do OPERADOR:** (a) `reforja.py --backfill --apply`; (b) RODADA 3 do `normalize_taxonomia`; (c) overflow 13-14/09 -> 15/09+; (d) backfill UTC->local; (e) `--new-limit` x pool; (f) areas fantasma; (g) F64; (h) rotacao do ledger (~260 KB); (i) F57 lote de ESTUDO; (j) `/graphify`, F35, F87.

## Estado por frente

- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (50d). ENAMED 13/09 (**amanha**) termometro.
- **Volume & Metas:** 7226 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~63.5q/dia (50d p/ UERJ/MFC (prova 01/11)). 🔴 A grade NAO fecha a meta (~1.250 abaixo).
- **Simulados:** 9 provas · S6 80 · S7 82 · S8 82,1 · S9 86. Serie: 239 erros = 60% execucao x 40% lacuna. Gargalo: override do modal (13/13 no S9).
- **FSRS:** divida 0 atrasados + 13 p/ hoje -- pool 641 nunca introduzidos (entram <=60/dia). (13 = relearning de hoje.) **s181: 113 cards, 53x4/26x3/5x2/29x1**; vencidos 79% >= 3, novos 41%.
- **Conteudo:** 136 resumos em resumos/. [derivado: glob] Sem lastro: Farmacodermias, Vulva/Vagina. 3 armadilhas somadas hoje (Meningites, Anexiais, Epilepsias).
- **Erros & Cards:** 1016 erros registrados · 1432 cards ativos · 2 needs_qualitative na fila · taxonomia 294 temas. [derivado: db] Reforja: **283 abertas**.
- **Engenharia:** suite 621 · `auto_check --all` PASSED · ledger **107 ids** (F101-F105 novos).
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem) [derivado: preparacao_estado]
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario).

## Ultima sessao -- s181 (2026-09-12, manha -> tarde) -- ESTUDO

Detalhe integral em `history/session_181.md`. 🃏 **113 cards** em 8 blocos (pipeline de 2; ele respondeu 30 por turno): fila vencida de 86 zerada (79% >= 3; Vulvovaginites 10/10, Cirurgia Infantil com os 4 fatos do F100 caindo pela 3a vez) + intake de 27 novos dos dormentes (41%). Re-drill de 34: 28 fecharam, 3 parciais, 2 travaram (#787, #597), 1 reforja. RD em 6 eixos, 18 carimbos, 4 notas (2 `usuario`). 🔴 **Ele declarou:** *"dificuldade muito grande com hidroeletroliticos x fisiologia renal x gasometria"*. 🕵️ **Pendencia fantasma:** Diarreia 41/34 JA estava no banco (s175 §2o ato, Pediatria, 09/09) -- s179/s180 copiaram o texto do 1o ato; nao registrei (dobraria). 🎯 **Revisao dos Top-Erros** publicada (14 temas em 5 areas + 9 padroes).

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- **F100 3a medicao:** n=1 sessao, sonda imediata apos ensino; o teste e o retorno de 15/09. **Override do modal:** n=13, uma prova.
- **F98/F99:** guarda de blackout nao ve intervalo < 4d · sem leitor por id. **F7:** classe real, nao-verificavel por gate. **F104:** coloquialismo e semantico, o linter nao pega.
- **D5** mede presenca, nao semantica · **G10** isenta por LINHA · **G5** sensivel a arquivo novo · gate de revogacao casa substring literal.
- Herdadas e vivas: **F35** · **F89** · **F79b** · **F66** (34% de orfandade) · **F64** · eixo C do **F81** · sitios gemeos do **F80b**.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB: baixar uma vez resolve beta-hCG e cortes da PE.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial), SINAN 2026.
- ⚠️ Drive 47d sem sync (F72); Dashboard EMED x db medido pelo boot (F35).
- 📡 Canal com o `/ai-eng` em `history/exchange-log.jsonl`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_181.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
