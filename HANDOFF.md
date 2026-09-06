# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-06 (tarde) -- S166 (Claude Code / Fable 5.1): bloco 1 drenado (62 cards, 77% retencao) + sessao de engenharia curta (README reescrito, 2 hotfixes, varredura de drift F75)*

## > Proximo passo imediato

1. 🎯 **Receber o Simulado 7 (ENAMED, feito em 06/09).** Registrar volume ANTES dos erros: `python tools/registrar_sessao_bulk.py --sessao 167 --area Simulado --feitas N --acertos Y`. Autopsia dos erros (fan-out de subagentes se 30+; senao 1 subagente) -> `insert_questao.py` -> cards `fresh_error`. Ler o resultado como termometro de EXECUCAO (S6: 80%, 10/18 erros por execucao): ritual "qual dado EXCLUI o que eu ia marcar?".
2. 🔁 **Drenagem de 90 cards a noite de 06/09 (decisao do usuario: matar a fila do dia; sprint 120/dia ate 13/09).** Fila: 33 que venceram na virada do dia + 45 atrasados genuinos + 2 sobras do redrill (#245 Kasai, #741 flora anaerobia) + ~10 novos por prevalencia (`--prevalencia`, abre em **Cirurgia Infantil**, tronco D10 obrigatorio antes: fraqueza nº 1, 43 cards nunca vistos). 🔴 **10 cards em relearning ja gravados na s166 voltam como `vencido` no `--list`** (245, 740, 741, 577, 1381, 736, 313, 706, 709, 1270): so drillar pela frente, **nao regravar** ate a proxima sessao-calendario. Pipeline de 2 blocos; feedback so dos 1-2; redrill no fechamento.
3. **Reforja pendente:** #792 (frente aberta), #4 (composta farmaco+concentracao), #1117 (contexto contradiz pergunta) + 15 itens anteriores (821,702,283,505,411,570,128,705,1360,470,1415,1086,1126 + 311/313 ja feitos).
4. **Cunhagem fraco-primeiro (ate 12/09), 8-10 atomicos/tema dos decks EMED:** SCA (zero tudo), Derrame pleural, Crise hipertensiva, Dislipidemia nova, Obesidade/SM, Dermatoses infecciosas, SUA (roxo S17), Down, Kawasaki, Diarreia, Puberdade/Baixa estatura, Convulsao febril, Choque/Phoenix, TB/ILTB, ITU, Saude do trabalhador.
5. **Grade S17 roxos ate 13/09:** Diarreia (Teoria, sem resumo -> aula-base) -> SUA (Teoria) -> APS (Revisao) -> Diarreia (Revisao) -> Urologia I -> Pneumonias I. ~66q/dia. (Ordem = esta lista, NAO a do `day_plan` -- Drive 42d sem sync, F72.)
6. **Inscricao UERJ** fecha 01/10 (Cepuerj, R$ 380). Acao do usuario.
7. 🔬 **Engenharia aberta (ledger §4p):** F71 balanceador x provas.json (S/M), F72 day_plan recomenda tema de snapshot stale (S), D5 skills `day-plan`/`curar-cards` (M), D11 escopo do doc_drift (S); F63/F65-F69 seguem.

## Estado por frente
- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (56d). ENAMED 13/09 (7d) termometro.
- **Volume & Metas:** 6721 / 10400 (perf. ~78.8%). Hoje: 0 (Simulado 7 ainda nao registrado). Ritmo-alvo ~65.7q/dia (56d p/ UERJ/MFC (prova 01/11)).
- **FSRS:** divida 55 atrasados + 33 p/ hoje -- pool 634 nunca introduzidos (entram <=60/dia; sprint 120 ate 13/09).
- **Conteudo:** 128 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 940 erros registrados · 1289 cards ativos · 2 needs_qualitative na fila · taxonomia 270 temas. [derivado: db]
- **Posicao:** conteudo S17 (nominal S23, atraso 6 sem) [derivado: preparacao_estado]
- **Prevalencia:** `core/cronograma/prevalencia_enamed.json` (5 aulas). Pendentes: Ped II, Preventiva II (12/09), Cirurgia II, CM II.
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**.

## Ultima sessao -- s166 (2026-09-05 noite -> 06 tarde): BLOCO 1 + ENGENHARIA
**Estudo:** bloco 1 completo, 62 cards em 4 sub-blocos (Epilepsias+ABC 15, Vulvovaginites/Ulceras/Planejamento 15, Colecistite/Apendicite/bulk/Polipos 16, singletons 16): **40x4 / 8x3 / 3x2 / 11x1 = 77% retencao, 65% perfeito** (s164: 54%/43%); Epilepsias 27% -> 11/11 no nucleo; familia ABC (#788/#789/#540) caiu na 4a passagem. Erros repetidos: #1381 alitiasica (fecha pelo cenario, ignora Tokyo A+B), #1270 AGC (colposcopia x avaliacao endometrial). Lacunas limpas: #740 Thayer-Martin, #1478 Gram do cancro mole, #736 ATB profilatico, #706 peritoniectomia, #1473/#1474 VNI e MgSO4 (S6). Redrill 11/13 fechado. 5 reforjas in-place (#245, #667, #741, #577, #311/#313), 3 carimbos `review_log` (Vulvovaginites, Colecistite, Apendicite). Zero questoes nos 2 dias; o usuario fez o Simulado 7 fora da sessao.
**Engenharia (pedido do usuario apos notar a contradicao day_plan x HANDOFF):** README reescrito do zero por subagente (30 afirmacoes obsoletas: Streamlit, RAG two-tier, "zero testes"); hotfix F70 (`[FSRS_BALANCE]` no stdout quebrava o JSON do `--record`) e F73 (`cronograma.py --check` morto: PDF em `data/`), ambos com teste vermelho->verde e trace em `.vibeflow/hotfixes/`; varredura de drift por subagente = 12 achados (F75), 9 corrigidos na hora (contrato FSRS com a excecao do sprint, tabela §7.4 regenerada, enum de veredito, flags faltantes em 2 skills, AGENTS.md, workflow registrar-sessao, ROADMAP x2, vibeflow index). auto_check --all e --changed PASSED.

## Pendencias/observacoes ativas
- 🔴 **Simulado 7 nao registrado** -- primeira acao da s167.
- 🔴 **Inscricao UERJ** -- fecha 01/10.
- 📚 **Frente MFC (Gusso + Duncan)** -- abre 14/09. Rescope da grade pro formato UERJ em 14/09.
- 💉 Diretrizes novas a conferir nos resumos: Calendario Vacinal 2026, GINA 2026, Reanimacao SBP 2026, Dislipidemia 2025, ATLS 11 (parcial), SINAN 2026 (F69).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_166.md*
