# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-07-05 -- **s108: fila FSRS de atrasados ZERADA (43 cards) + auditoria de engenharia iniciada (ledger vivo AUDITORIA_MEDHUB.md, F1-F9). Drift F1 do ponteiro de sessao RESOLVIDO.***

## > Proximo passo imediato -- s109 (NOVA SESSAO, contexto limpo)
**A) VOLUME -- Questoes da Semana 12 (~120q), 1a leva com FOCO EM APENDICITE.** Trilha principal do dia: executar as questoes da S12 comecando pelo bloco de apendicite. Refresh calibrado por tema antes de cada bloco (PREPARAR sob Invariante D; rating so apos janela de override, Invariante C); cada erro vira card ancorado no elo metacognitivo. **Toda friccao de engenharia observada no uso vira achado F16+ no ledger `AUDITORIA_MEDHUB.md`** (mesmo template; e o insumo do ciclo 2 do Fable).
**B) ENGENHARIA -- 1o ciclo Fable ENTREGUE (2026-07-05).** PRD + 5 specs + implement + audit (fluxo vibeflow completo): F1/F3/F4/F5/F6/F8/F9/F10/F12/F13 entregues; F2 medido (nao reproduz); F7 heuristica calibrada (reforge 95/120 segue com o coordenador via /curar-cards); F11 = runbook GATED (`docs/runbook-expurgo-ipub-git.md`, aval do operador). Detalhe: ledger secao 3b + `.vibeflow/audits/engenharia-ledger-part-*`. NOVO NO FLUXO: fechamento usa `day_plan --handoff-block` (numeros derivados) + fila com `--cluster` + `--review-plan` + janela de override ANTES do `--record` (Invariante C). O ledger segue vivo: **proximos achados comecam em F16**. **CICLO 2 ARMADO (operador, 2026-07-05):** apos a leva de exercicios (apendicite), o Fable consome o ledger F16+ e toca o ciclo 2 com escopo ja autorizado: (a) **expurgo do blob ipub.db** (executar `docs/runbook-expurgo-ipub-git.md` -- pre-condicoes do runbook conferidas na janela: backup mirror, tree limpo, sem clones divergentes); (b) **validar parametros do teto dinamico** com dados reais de divida; (c) **reforge dos cards 95/120** (120 passa pelo gate de evidencia `/pesquisar-evidencia` antes).

## Padroes de erro vivos -- atencao do scrum master
- RED **Pneumotorax hipertensivo (asma AESP pos-IOT):** assimetria de murmurio + dessaturacao subita = puncao de alivio ANTES de mexer no ventilador. **REINCIDIU na s108** (card 213, nota 1) -- leak persistente, prioridade.
- RED **Bug nº1 / parar antes de completar a verificacao:** sifilis congenita (card 189) -- incerteza sobre adequacao materna = TRATAR o RN, nunca observar. Regra do operador: falta de info materna = inadequada = tratar RN (50k UI/kg/dose, 10d).
- RED **Reacao Reversa (Tipo 1):** neurite aguda = Prednisona 1 mg/kg/dia e MANTER a PQT.
- RED **PTT:** hemolise mecanica (Coombs negativo, esquizocitos) -> plasmaferese de urgencia (heparina contraindicada).

## Estado por frente
- **Volume & Metas:** 4454 / 12000 (perf. ~79.0%). Hoje: 0. Ritmo-alvo ~107.8q/dia (70d p/ ENAMED). [derivado: day_plan --handoff-block] | Proximo: S12 (~120q).
- **Conteudo:** 61 resumos. Gaps: TCE.md, Sistemas de Informacao em Saude.md.
- **Erros & Cards:** sem cards novos na s108 (revisao + engenharia). 2 cards mal-calibrados p/ reforge: **95** (HCE x TGA) e **120** (heterotopica x corpo luteo; via gate de evidencia).
- **FSRS:** 1 atrasados + 2 hoje. Backlog: 351 novos. [derivado: day_plan --handoff-block] (43 drenados na s108; re-drill assentado: 213, 205.)
- **Infraestrutura:** NOVO ledger de engenharia `AUDITORIA_MEDHUB.md` (F1-F9; F1 resolvido). F3/F7/F8/F9 nasceram do uso vivo. Ledger e vivo -- acumula ate o Fable derivar o PRD.

## Pendencias ativas
Reescrever TCE.md + Sistemas de Informacao em Saude.md. Reforjar cards 95/120. Fable: derivar PRD do ledger (ordem sugerida F1+F6 -> F3 -> F9 -> F8 -> F7 -> F4 -> F2 -> F5).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_108.md * Ledger de engenharia: AUDITORIA_MEDHUB.md*
