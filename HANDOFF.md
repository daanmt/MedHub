# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-17 (noite) -- **s184 (ABSORCAO + PLANEJAMENTO + lote do player)**: fundamentos pedagogicos nomeados (`docs/FUNDAMENTOS-APRENDIZAGEM.md`), sintese + fila R1-R11 em **`PLANEJAMENTO-APRENDIZAGEM-2026-09-17.md`** (raiz), ledger F108-F113, grafo atualizado. **Lote de 90 no player: 86 gravadas, 80% >= 3, 30 min; 5 defeitos marcados.** Achado ALTO **F112** (nota 2 = acerto no FSRS). **Inscricao na UERJ FEITA pelo usuario.** Zero questoes hoje.*

> ✅ Recursos do ENAMED enviados (16/09). ✅ **Inscricao UERJ feita (17/09).** 🔧 **Proxima sessao = ENGENHARIA DEDICADA** (decisao do usuario): permit do PRD `plano-ssot-e-cards-v2` (GO do `/ai-eng`, silencio = GO) + fila R1-R11 por spec (`PLANEJAMENTO §5`).

## > Proximo passo imediato

1. 🔧 **Sessao de engenharia (ordem):** (a) em PARALELO, arquivos disjuntos -- **R1** CLI read-only de otimizacao do FSRS (`Optimizer` + CMRR do py-fsrs sobre 3.067 revisoes; parametros em dado versionado; adaptador so le apos GO) + **PRD part-4** (`day_plan` le o plano; contratos v1.3) + **PRD part-6** (ledger de listas); (b) **commit de docs**: R3 riders F109 (contrato FSRS + `revisar.md`), R4 web isolada (`analisar-questao §0`), R5 playbook answer-changing, R6 ponteiro do ledger de friccoes, **F113** regra de acentuacao em `estilo-flashcard.md` (+ `sync_skills`); (c) **R2** decisao do operador sobre a regua de notas (F112), com o numero do R1 na mao; (d) part-7 painel -> part-8 congelar Drive; (e) **R7** leech proprio + **F113** reforja em lote (`recurate_cards.py`, so acentos); (f) R8 intake da Fase 2 antes de 02/11. Regra que funcionou: 1 subagente por parte, `model` explicito, commit antes da onda seguinte; `AUDITORIA_MEDHUB.md` em chunk proprio se o grafo for atualizado (R11).
2. 🃏 **Cards (rito do player):** fila baixa nos proximos dias (18/09: 31 · 19/09: 26 · 20/09: 24 · 21/09: 25 · 22/09: 24) -> lote = vencidos + **intake ~30/dia fraco-primeiro** do pool de 685 ate o teto 60. 🔴 **Aula-base D10 de Acido-Base + Potassio ANTES de re-drillar os 6 segurados** (#595 #596 #598 #783 #786 #787, ainda vencidos). Defeitos abertos: #419 #685 #688 #689 #373 (reforja 288).
3. 📚 **Questoes (Fase 1, semana 1 = 14 tarefas, ~389q; `plano.py --listar --semana 1`):** Pneumonias na Infancia T (24) -> SUA R (42) + Vitalidade Fetal (25+36) -> Cirurgia Vascular R (43) -> MFC extensivo (50) + Saude do Idoso (32+41) -> RAPS (20) + UERJ 2026 bloco MFC Q81-100 (20) -> Pre-natal/parto (36). Resumos custom da semana: **Prevencao Quaternaria** e **AMI**. Bulk -> `plano.py --concluir ID --sessao <id>`; erros -> Autopsia.
4. 🧭 **Conduta que ja vale (`PLANEJAMENTO §4.4`):** ler o ledger de friccoes antes de propor "reducao de atrito"; `errou` com racional declarado = insumo nº 1; regra dos dois finalistas nao e "primeiro instinto".
5. 🗓️ Revisao de status por area (173 linhas) e rebalanceio da semana 3 (794q) seguem pendentes; 8 temas sem resumo = tarefas `custom`.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (45d; **inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48 de 02/11 ate o ENAMED 2027 (data ASSUMIDA).
- **Volume & Metas:** 7326 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~68.3q/dia (45d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block, antes do lote]
- **Simulados:** 9 provas + ENAMED real 75. Corpus `simulados/inep/` e `simulados/uerj/`.
- **FSRS:** **86 revisoes gravadas em 17/09 (revlog 3.067)**: 61x4 / 8x3 / 2x2 / 15x1 (+4 defeito sem nota) = 80% >= 3; atrasados remanescentes 10 (6 nefro segurados + 4 defeitos); pool 685. 🔴 **F112:** nota 2 agenda em 14,2 d e nota 4 (52% do revlog) em 34,3 -- regua deslocada; parametros DEFAULT.
- **Conteudo:** 136 resumos. Preventiva: so 3/22 decks pagam aluguel na UERJ; P4, polifarmacia, paliativos e MCCP sem resumo.
- **Erros & Cards:** 1041 erros · 1476 cards ativos · taxonomia 302 temas. Reforja **288** (+5 do player). **F113:** cards recentes sem acentuacao lidos como "erro de portugues" (feedback no player).
- **Cronograma:** `plano_tarefas` = SSOT (896). Fase 1 = semanas 1-7 (~3.050q para 2.760). Dashboard do Drive congelado.
- **Ensino (s184):** `docs/FUNDAMENTOS-APRENDIZAGEM.md` (P1-P17; 14 CONFIRMA; F109-F112) + ledger de friccoes; `AGENTE.md §6` aponta; fontes em `docs/research/`.
- **Engenharia:** suite 714; `auto_check` PASSED; ledger ate **F113** (§6y); grafo 3.383 nos / 253 comunidades (536 docs pendentes no manifesto).
- **Posicao:** conteudo S17 (nominal S25, atraso 8 sem) [derivado: preparacao_estado]
- **Datas:** fim da grade 09/10 · **UERJ 01/11** (inscrito) · proximo slot de simulado ~10/10 (R3, cadencia de 4 semanas).

## Ultima sessao -- s184 (2026-09-17, 18h45 -> 21h) -- ABSORCAO + PLANEJAMENTO + lote do player

Detalhe em `history/session_184.md`. 4 varreduras isoladas (~618k tokens) + 3 extratores graphify (~1,01M) + 1 medicao read-only (F112). Portadores: FUNDAMENTOS, PLANEJAMENTO (raiz), ledger §6y (F108-F113 + lapide no F3), `docs/research/`, memoria x2 (+ indice compactado). **Lote do player: 90 cards em 30 min, 86 gravadas (COUNT-ASSERT ok), 5 defeitos -> reforja; Revisao Direcionada em 14 temas com carimbo `review_log`.** Nenhum contrato, skill ou codigo tocado (sessao de planejamento).

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- Data do ENAMED 2027 e horas na residencia sao ASSUNCOES. F112 mede intervalo agendado, nao retencao por nota. Ledger de friccoes sem gate (F110). F113 sem medicao de proporcao no baralho. Nota da aula (F18c) **nao registrada** na RD de hoje. Grafo: 536 docs mudados nao re-extraidos.
- Herdadas e vivas: F100 (4a medicao: #787 falhou) · F98 · F7/F104 · D5 · G10 · G5 · F35 · F89 · F79b · F66 · F64 · eixo C do F81 · F80b.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB. 💉 Diretrizes 2026 a conferir: Calendario Vacinal, GINA, ATLS 11 (parcial), SINAN.
- 📡 Canal com o `/ai-eng` em `history/exchange-log.jsonl` -- levar o destilado do PLANEJAMENTO §5 (fila R1-R11 + F113) para GO/NO-GO na abertura da sessao de engenharia.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_184.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
