# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-28 ~02:30 — **s096: implementou o PRD de Revisão Calibrada (4 partes) + sessão FSRS + resumo de ectópica**. Via `/gen-spec` fatiou o PRD em 4 specs e entregou os 10 DoD (**63 testes verdes**). Revisou **32 cards** (drenou os 31 vencidos). Criou o resumo gold de **ectópica**. Definiu a **política de cards (teto 30/dia)**. Sem questões novas (dia de engenharia+revisão). Acumulado **4.112 (41% da meta-prova 10k)**.*

## ▶ Próximo passo imediato — s097
**A) Semana 11 (estudo):** começar com **questões** (meta jun: faltam **388 em 3 dias** → ~129/dia p/ bater 4.500). Temas da grade: Medicina de Família, Doenças Exantemáticas (Rev), Cirurgia Infantil Pt 3 (Rev), Vulvovaginites, Imunizações, Sepse, Síndromes Hipertensivas.
**B) Cards (nova política):** **teto 30/dia = agendados + 15 backlog** priorizado pela área da S11; **sempre PREPARAR antes** (refresh calibrado). Amanhã: **6 re-aprendizados** (ectópica #114/116/118, #70, #130, #95) + **8 agendados** (#122,142,13,94,132,134,441,442).
**C) Revisão Calibrada:** ratificar o contrato (`pending-ratification`) após 1º uso real; integrar `day_plan --difficulty` na abertura de task do boot.

## Revisão Calibrada (s096 — LIVE, frente A concluída)
- **Schema:** `taxonomia_cronograma` +`dificuldade`/`dificuldade_fonte`/`dificuldade_at`; escrita só por `db.set_dificuldade` (8 notas §4.7 semeadas). Fix `_find_resumo` (indexa `path.stem`).
- **Inferência:** `tools/day_plan.py --difficulty "<area>" "<tema>"` → nota_inferida + degrau + propósito + divergência (read-only, só sinais frios).
- **Fusão:** `/revisar` = PREPARAR (FSRS read-only, carimba `review_log`) + DRENAR (escreve FSRS). `/refrescar` deprecado. 🔴 Invariantes A (não toca FSRS) e B (sempre carimba) com testes.
- **Norma:** `core/contracts/revisao-calibrada-contract.md` (pending-ratification); 4 specs em `.vibeflow/specs/`; 63 testes em `tools/test_revisao_calibrada.py`.

## Modelo FSRS (auditado na s096)
- **Agendados** (`state>0`, **119**): têm `due`, determinístico — ~5-10/dia de manutenção.
- **Novos** (`state=0`, **290**): pilha SEM data; entram só por `--new-limit`. Backlog cresce > do que 10/dia enxuga → política teto 30/dia + 15 backlog (`feedback_politica_cards_diaria`).

## Estado por frente
- **Volume & Metas:** **4.112 / 10.000 (41%)** [teto 12k]. Perf. geral **79,5%**. Meta jun 4.500: déficit 388 (3 dias). Custo/q acum. R$0,77 · mês R$0,22.
- **Cronograma (SSOT `Cronograma.pdf`):** sync F1-F4 LIVE. **Próxima = S11** (conteúdo); calendário nominal S13. `grade.json` em dia.
- **Conteúdo:** **52 resumos** (+ectópica gold). Gaps: reescrever `TCE.md` + `Sistemas de Informação em Saúde.md`.
- **Erros & Cards:** **364 erros · ~408 cards ativos** (#609 último; #104 aposentado). FSRS: 0 atrasados · 6 hoje (re-aprendizado) · 290 novos.

## Plano da sprint (s093)
**Meta-prova 10.000 + gatilho S13 (~12/07):** ≥5.600 → 12k; <5.200 → 10k. **Ritmo 3+1 + simulado dominical**; 14 simulados × 100q.

## Pendências ativas
Ratificar contrato Revisão Calibrada. Reescrever `TCE.md`. Limpeza `[bulk]`/`Geral` da taxonomia. Re-drill bugs nº1 (#70 reincidiu). Sessão Cirurgia + integrar `/schedule`. Áreas fracas: Dermato 67% · Cardio 67% · Otorrino 68% · Nefro 70% · Hemato 72%.

---
*Histórico: history/INDEX.md · Macro: ESTADO.md · Contrato novo: core/contracts/revisao-calibrada-contract.md · Specs: .vibeflow/specs/revisao-calibrada-part-*.md*
