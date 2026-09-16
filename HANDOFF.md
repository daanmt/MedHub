# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-16 (tarde) -- **s183 (PLANEJAMENTO)**: **hibrido APROVADO** (RF rescopada ate 01/11 + extensivo S21-S48 como espinha do ENAMED 2027); **norte reordenado** (Psiquiatria/IPUB via ENAMED 2027, alvo 95%; UERJ/MFC = plano B; USP fora); Dashboard do Drive = catalogo do EXTENSIVO; corpus INEP (23 PDFs) + cadernos UERJ 2021-2026 em `simulados/`; Medcards = banco de referencia. Volume 7.326 (sem estudo hoje).*

> 🔴 **RECURSOS DO ENAMED ATE 17/09 (acao do usuario):** Q68, Q75, Q6 (+Q48, Q5, Q99) -- fundamentos em `artifacts/enamed-2026-comentado.html`. **Inscricao UERJ fecha 01/10.** Permit de engenharia segue CONSUMIDO.

## > Proximo passo imediato

1. 🃏📚 **Quarta 17/09:** 60 cards (106 vencidos; teto 60, regime de divida) + 60 questoes da Fase 1: **Vitalidade Fetal T (25) + Cirurgia Vascular R (35 de 43)** da S17. Re-sondar #787 (hiperaldosteronismo) e #597 (Winter) antes de ensino novo.
2. 📚 **Frente MFC-UERJ abre 17/09 (2 resumos/semana, ordem do ranking REAL 2021-2026):** Prevencao Quaternaria -> Avaliacao Multidimensional do Idoso -> Raciocinio diagnostico quantitativo (vinheta dor precordial + TE, caiu nas 6 edicoes) -> MCCP -> Polifarmacia/desprescricao -> Paliativos na APS -> Rastreamento BR. Fonte por subtema (Gusso/Duncan): `simulados/uerj/UERJ_MFC_por_edicao_2021-2026.md §3.1`. Treino: bloco Q81-100 dos cadernos 2023-2026 em `simulados/uerj/` + REVALIDA em `simulados/inep/`.
3. 🗓️ **Fase 1 (16/09 -> 01/11, 2.760q a 60/dia):** RF S17-S28 pendente = 139 tarefas / 4.036q; orcamento: MFC-EMED ~210 (MFC Revisao 50, Idoso 32, RpQ 41, Etica R 39, Financiamento ~50) · PED 564 · CIR 469 · GO ~790 · CM dirigida ~320 (Acido-base/K RpQ, Nefrolitiase R, HAS R, FA/PCR, Polipos RpQ, DITC, Anemias/Leucemias) · 8 temas sem resumo 160 · INEP/UERJ MFC ~200. **Cortado ate 01/11:** Estatistica Medica, NRs, IVAS pt.2, Polo Posterior, Cirrose, DPOC, Derrame/Neoplasia pulmonar, Onco cutanea, Ortopedia. Detalhe: `history/session_183.md §3`.
4. 🔴 **8 temas SEM RESUMO do ENAMED seguem:** RAPS, Anafilaxia, FA/Arritmias, Osteoporose, HPB/PSA, Onco ped, Coqueluche, TEA (Medcards cobre 6/8 como referencia; RAPS e TEA = 0).
5. 🧭 **Termometro mensal INEP:** REVALIDA 2025/2 como 1o (data a marcar). ~95% no INEP calibra o 90-95+ do ENAMED.
6. 🔴 Reforja: 283 abertas (sem marca nova).

## Fila de engenharia -- permit CONSUMIDO; itens novos por spec (GO do `/ai-eng`)

- 🆕 **PRD `plano-ssot-e-cards-v2` (s183, permit do usuario em 16/09 -- *"planejamento mais estavel, orquestrado por voce"*):** 6 partes em ordem P6 Autopsia diaria -> P5 poda (lote 1 = **125 aposentados sem revlog/reforja** de 192; 67 com historico ficam) -> P1 `plano_tarefas` SSOT + `grade_extensivo.json` -> P2 ledger de listas (`sessoes_bulk.tarefa_id`, `tools/listas.py`) -> P3 painel gerado (Drive deixa de ser SSOT) -> P4 player de cards em Artifact. Abertas p/ o usuario: Drive vira historico?; aprovar lote 1; player desktop ou celular-first. `.vibeflow/prds/plano-ssot-e-cards-v2.md`.
- 🆕 **E1** `grade_extensivo.json` derivado do `[52 wk] Cronograma Extensivo.pdf` (parser prototipo no scratch da s183): o `Realizada?` do Dashboard passa a casar 1:1 (674/735 por nome) e a familia **F72** morre. **E2** CLI `tools/medcards.py --query --tema` (espelho do `emed_flashcards`, `html.parser`). **F108** extrator regex de HTML engoliu cutoffs (123 cards; licao na memoria).
- Abertos herdados: F98-F107 (s182). Decisoes empilhadas do OPERADOR: (a)-(j) da s182 + **(k) conciliar 7 areas divergentes na planilha** (Obst -59, Dermato +41, Cirurgia +40, Ortopedia -27, Endocrino -24, Pneumo +16, Gineco -26).

## Estado por frente

- **Norte:** 🎯 **Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%)**. Plano B: **UERJ/MFC 01/11/2026 (46d)**. USP fora. Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo **S21-S48** (425 tarefas, 1.002 h, ~6.600q) de 02/11 ate o ENAMED 2027 (~set/2027, data ASSUMIDA); horas 12-15/sem em R1 ou 20+ trabalhando.
- **Volume & Metas:** 7326 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~66.8q/dia (46d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 9 provas + ENAMED real 75. **Corpus novo:** `simulados/inep/` (ENAMED 2025 x2 cadernos + gabaritos; REVALIDA 2022/1-2026/1; 23 PDFs oficiais) e `simulados/uerj/` (cadernos AD 2021-2026).
- **FSRS:** divida 106 atrasados + 27 p/ hoje -- pool 685 nunca introduzidos (entram <=90/dia). [derivado]
- **Conteudo:** 136 resumos em resumos/. [derivado: glob] Preventiva: **so 3/22 decks pagam aluguel na UERJ** (MFC, Idoso, Testes Dx); P4, polifarmacia, paliativos e MCCP **sem resumo**.
- **Erros & Cards:** 1041 erros registrados · 1476 cards ativos · 2 needs_qualitative na fila · taxonomia 302 temas. [derivado: db] Reforja 283.
- **Cronograma:** Dashboard do Drive = **707 tarefas do EXTENSIVO** (nao da RF); feitas 178 (25%), temas tocados 39%; entrada util = **S21**. W1 gravado 16/09 (planilha 6.349 x db 7.326).
- **Engenharia:** `.gitignore` cobre `*.apkg` e `Medcards 2022/`; suite 621; ledger 109 ids (+E1, E2, F108 propostos).
- **Posicao:** conteudo S17 (nominal S25, atraso 8 sem) [derivado: preparacao_estado] -- na RF; no extensivo, ver linha Cronograma.
- **Datas:** fim da grade 09/10 · **UERJ 01/11** · inscricao UERJ ate **01/10** · recurso ENAMED ate **17/09**.

## Ultima sessao -- s183 (2026-09-16, 13h -> 17h30) -- PLANEJAMENTO

Detalhe em `history/session_183.md`. **5 subagentes (Opus x3, Sonnet x2), ~1,01M tokens, ~75 min de relogio em 2 ondas**; 6 numeros load-bearing re-medidos pelo principal e confirmados. Achados: Dashboard = catalogo do extensivo (raiz do F72); extensivo nativo = 33,5 h/sem e **39 q/dia** (migrar ja = +25% horas e ~1.380q a menos ate a UERJ); guia UERJ classifica por TEMA e o caderno por BLOCO -- **o bloco MFC de 20q existe desde 2021** (104q lidas: 92% MFC clinica, **Etica 0/104**, P4 = tema-mestre); Medcards 54% atomico + 1 bug MEU de extracao medido e corrigido (F108).

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- Data do ENAMED 2027 e horas na residencia sao **ASSUNCOES**. UERJ 2019-2020 nao verificadas (PDFs removidos da Cepuerj). Gabarito REVALIDA 2026/1 so com login. 2 graficos do guia UERJ corrompidos (Endocrino, Pneumo). Top-5 das outras 4 areas na UERJ = leitura qualitativa, nao contagem.
- Herdadas e vivas: **F100** 4a medicao pendente · **F98** · F7/F104 (semanticas) · D5 · G10 · G5 · F35 · F89 · F79b · F66 · F64 · eixo C do F81 · F80b.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB. 💉 Diretrizes 2026 a conferir: Calendario Vacinal, GINA, ATLS 11 (parcial), SINAN.
- 📡 Canal com o `/ai-eng` em `history/exchange-log.jsonl`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_183.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
