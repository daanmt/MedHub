# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-27 ~23:55 — **s095: sessão de engenharia + cards**. Forjou os **21 flashcards do dia** (#589-609, 5 temas da s094) + construiu o **sistema de sync do cronograma F1-F4** (derivador + grade.json + radar + day_plan + contrato) + fechamento formal. **Sem questões novas** (dia de build). Acumulado **4.112 (41% da meta-prova 10k)**.*

## ▶ Próximo passo imediato — s096
**A) Implementar o PRD de Revisão Calibrada** (agora **DESBLOQUEADO** — F1 sync pronto): schema `dificuldade` em `taxonomia_cronograma` + `infer_nota()` + fundir `/revisar`+`/refrescar`. **Pré-req:** fix `_find_resumo` (indexar `path.stem.lower()` em `get_topic_context._build_index`) — hoje a resolução tema→resumo é fuzzy frágil e o `infer_nota` depende dela.
**B) Semana 11** (estudo): começa com FSRS vencidos + ≥100q. Próximos temas (da grade): Medicina de Família, Doenças Exantemáticas (Rev), Cirurgia Infantil Pt 3 (Rev), Vulvovaginites, Síndromes Hipertensivas, Imunizações, Sepse.
**C) FSRS:** drenar #554-609 + vencidos (`/revisar`); backlog = 14 atrasados + 12 hoje + 291 novos.
**D) Carry-over:** sessão dedicada de Cirurgia; integrar `/schedule` no calendário.

## Sistema de sync do cronograma (s095 — NOVO, F1-F4 completo)
- **`tools/cronograma.py`** (derivador único, read-only) + **`core/cronograma/grade.json`** (30 sem · 352 tasks · 10218q; commitado). Subcomandos `--rebuild`/`--check`/`--json`/`--gap`/`--radar`/`--validate`. Validado: S10=273, S11-28=6689/222.
- **`day_plan.py`** agora lê a grade: conteúdo **S11** vs calendário **S13** (~2 sem atrás), temas + dois ritmos (grade ~85/dia · meta 10k ~75/dia).
- **Contrato** `core/contracts/cronograma-contract.md` + skill `/cronograma` + reconcile **W5-W7**. 🔴 read-only no db; único write = ponteiro `Próxima = SNN`.
- **Achado p/ a frente do PRD:** `_find_resumo` indexa só frontmatter (não nome de arquivo) → resolução frágil; fix aditivo pendente.

## Frentes vivas
- **PRD Revisão Calibrada** (`docs/plans/s094-revisao-calibrada-PRD.md`): aprovado, **DESBLOQUEADO**. Implementar (frente A).
- **Registro onboarding fundacional**: aplicado (Ácido-Base, Pneumo).

## Plano da sprint (s093)
**Meta-prova 10.000 + gatilho S13 (~12/07):** ≥5.600 → 12k; <5.200 → 10k. **Ritmo 3+1 + simulado dominical** (~90-100q/dia ON); 14 simulados × 100q (11 pré-ENAMED).

## Estado por frente
- **Volume & Metas:** **4.112 / 10.000 (41%)** [teto 12k]. Perf. geral 79,5%. Sem questões na s095 (engenharia). `--gap` (de S11): cronograma cobre os 10k a **88% de execução**; 12k exige banco extra (+1199).
- **Cronograma (SSOT `Cronograma.pdf`):** **sync F1-F4 LIVE**. **Próxima = S11** (conteúdo); calendário nominal S13. `grade.json` versionado.
- **Conteúdo:** **51 resumos**. Gaps: reescrever `TCE.md` + `Sistemas de Informação em Saúde.md`; ectópica.
- **Erros & Cards:** **364 erros · ~410 cards** (#609 último; +21 na s095). FSRS backlog: #554-609 + vencidos.

## Pendências ativas
- Fix `_find_resumo` (pré-req do PRD). Limpeza `[bulk]`/`Geral` da taxonomia. Re-drill dos bugs nº1 (426/435/84/78/70/104). Sessão Cirurgia + `/schedule`.

---
*Histórico: history/INDEX.md · Macro: ESTADO.md · Planos: docs/plans/s094-revisao-calibrada-PRD.md · s094-ultraplan.md · Contrato: core/contracts/cronograma-contract.md*
