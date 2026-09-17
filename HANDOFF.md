# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-17 (noite) -- **s184 (ABSORCAO + PLANEJAMENTO, sem reforma)**: 2 transcricoes (J.R. Smith) absorvidas + 4 varreduras de web aberta em subagentes ISOLADOS + `graphify --update` escopado -> `docs/FUNDAMENTOS-APRENDIZAGEM.md` (17 principios x mecanismo; ledger de friccoes) e **`PLANEJAMENTO-APRENDIZAGEM-2026-09-17.md`** (raiz: sintese + fila R1-R11). Achado ALTO **F112**: nota 2 e agendada como ACERTO pelo FSRS (14 dias) e nota 4 = 52% das revisoes. Zero questoes, zero cards hoje.*

> ✅ Recursos do ENAMED enviados (16/09). **Inscricao UERJ fecha 01/10 (acao do usuario).** Permit de engenharia (PRD `plano-ssot-e-cards-v2`, GO do `/ai-eng`, silencio = GO) segue valendo; a fila nova (R1-R11) entra por spec, na ordem do PLANEJAMENTO §5.

## > Proximo passo imediato

1. 🃏 **Lote do player de hoje/amanha:** `--export-player --limit 60` -> `--build-player` -> republicar a MESMA URL (https://claude.ai/artifact/T53xLp1Wdba6W72Mvdid6Y, `url` + `capabilities: {db: {}}`); colecao `sessoes/<data>/notas`; fechamento `--record-lote` dry-run -> `--apply --expect N`. Regime de divida: **115 vencidos (86 + 29), teto 90**. 🔴 Eixo nefro (#787 3 quedas, #597): `/aula-base` D9-D10 de Acido-Base + Potassio ANTES de novo drill.
2. 🧭 **Conduta que ja vale (sem reforma, `PLANEJAMENTO §4.4`):** ler o ledger de friccoes (`FUNDAMENTOS §3`) antes de propor "reducao de atrito"; `errou` com racional declarado = insumo nº 1 da Autopsia; a regra dos dois finalistas NAO e "primeiro instinto"; teste do override do modal = proximo simulado.
3. 📚 **Questoes (Fase 1, semana 1):** `python tools/plano.py --listar --semana 1` (Vitalidade Fetal T, Cirurgia Vascular R, SUA R, Pneumonias na Infancia T); bulk -> `plano.py --concluir ID --sessao <id>`; erros -> Autopsia (`analisar-questao.md §3.3`).
4. 📚 **Frente MFC-UERJ (2 resumos/sem):** P4 -> AMI -> raciocinio dx quantitativo -> MCCP -> polifarmacia -> paliativos -> rastreamento; treino Q81-100 (`simulados/uerj/`) + REVALIDA (`simulados/inep/`).
5. 🗓️ Revisao de status por area (173 linhas): `plano.py --pendencia-revisao` -> `--revisar-area` -> `--confirmar-area --apply --expect N`; rebalancear a semana 3 (794q). 8 temas sem resumo do ENAMED seguem como tarefas `custom`. Reforja: 283 abertas.

## Fila de engenharia -- permit de 16/09 (PRD `plano-ssot-e-cards-v2`) + fila da s184 (`PLANEJAMENTO-APRENDIZAGEM-2026-09-17.md §5`)

- **PRD v2 pendente, nesta ordem:** part-4 e part-6 em PARALELO (arquivos disjuntos) -> part-7 painel -> part-8 congelar Drive. Specs em `.vibeflow/specs/plano-ssot-e-cards-v2-part-N.md`. Regra que funcionou: 1 subagente por parte, `model` explicito, commit antes da onda seguinte.
- **Fila s184 (planejada, NADA executado):** **R1** CLI read-only de otimizacao do FSRS (ainda nao existe; `Optimizer` + CMRR do py-fsrs sobre 2.981 revisoes; parametros em dado versionado) -> **R3+R4+R5+R6** num commit de docs (riders F109 no contrato FSRS/`revisar.md`; web isolada em `analisar-questao §0`; playbook answer-changing; ponteiro do ledger de friccoes) -> **R2** decisao do operador sobre a regua de notas (F112; toca `record_review` = spec) -> **R7** leech proprio -> **R8** intake por tarefa na Fase 2 (F111, decisao; antes de 02/11) -> R9 N-of-1 -> R10 gatilho de memoria -> R11 grafo por sessao. Mais F107 (`--dry-run`) e F99 (`--card`).
- Abertos herdados: F98-F107; F38 falso positivo de 13/09 declarado no teste vivo. Decisoes do operador empilhadas (a)-(k) da s182/s183.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (45d). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48 de 02/11 ate o ENAMED 2027 (data ASSUMIDA).
- **Volume & Metas:** 7326 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~68.3q/dia (45d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 9 provas + ENAMED real 75. Corpus `simulados/inep/` (23 PDFs) e `simulados/uerj/` (2021-2026).
- **FSRS:** divida 86 atrasados + 29 p/ hoje -- pool 685 nunca introduzidos (entram <=90/dia). [derivado] 🔴 **F112:** revlog 2.981 = 563x1 / 338x2 / 528x3 / 1.552x4; nota 2 agenda em 14,2 d, nota 4 em 34,3 d -- regua deslocada 1 degrau vs. semantica FSRS; parametros ainda DEFAULT.
- **Conteudo:** 136 resumos em resumos/. [derivado: glob] Preventiva: so 3/22 decks pagam aluguel na UERJ; P4, polifarmacia, paliativos e MCCP sem resumo.
- **Erros & Cards:** 1041 erros registrados · 1476 cards ativos · 2 needs_qualitative na fila · taxonomia 302 temas. [derivado: db] Reforja 283.
- **Cronograma:** `plano_tarefas` = SSOT (896: extensivo 735 / rf 139 / custom 22). Fase 1 = semanas 1-7 (~3.050q para 2.760). Dashboard do Drive congelado em `dashboard_snapshot.json`.
- **Ensino (s184):** `docs/FUNDAMENTOS-APRENDIZAGEM.md` = principio x mecanismo (14/17 CONFIRMA; F109 tensao, F110 lacuna, F111 plano, F112 motor) + ledger de friccoes V1-V11/X1-X8 + fontes (relatorios em `docs/research/`). `AGENTE.md §6` aponta.
- **Engenharia:** suite 714; `auto_check --changed` PASSED na s184; ledger ate **F112** (§6y); grafo `graphify-out/` atualizado em escopo (104 codigo + 43 portadores; 536 docs pendentes no manifesto).
- **Posicao:** conteudo S17 (nominal S25, atraso 8 sem) [derivado: preparacao_estado]
- **Datas:** fim da grade 09/10 · **UERJ 01/11** · inscricao UERJ ate **01/10**.

## Ultima sessao -- s184 (2026-09-17, 18h45 -> noite) -- ABSORCAO + PLANEJAMENTO

Detalhe em `history/session_184.md`. Usuario trouxe 2 transcricoes, autorizou web via subagentes ISOLADOS (regra nova, memoria `feedback_web_aberta_subagente_isolado`), pediu `open-spaced-repetition` + `/graphify`, e fechou: *"sessao de planejamento"*. **4 varreduras (Opus x1, Sonnet x3; ~618k tokens; ~23 min de relogio) + 3 extratores graphify (Sonnet)**; 1 medicao read-only no db (F112). Portadores: FUNDAMENTOS, PLANEJAMENTO (raiz), ledger §6y (F108-F112 + lapide no F3), `docs/research/` (4 relatorios), memoria x2. Nenhum contrato/skill/codigo tocado.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- Data do ENAMED 2027 e horas na residencia sao ASSUNCOES. F112 mede intervalo agendado, nao retencao por nota (cruzar com a revisao seguinte e parte da spec R1/R2). Ledger de friccoes = eixo semantico, sem gate (F110). Grafo: 536 docs mudados NAO re-extraidos (pendentes por desenho).
- Herdadas e vivas: F100 (4a medicao: #787 falhou) · F98 · F7/F104 (semanticas) · D5 · G10 · G5 · F35 · F89 · F79b · F66 · F64 · eixo C do F81 · F80b.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB. 💉 Diretrizes 2026 a conferir: Calendario Vacinal, GINA, ATLS 11 (parcial), SINAN.
- 📡 Canal com o `/ai-eng` em `history/exchange-log.jsonl` -- levar o destilado do PLANEJAMENTO §5 (fila R1-R11) para GO/NO-GO.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_184.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
