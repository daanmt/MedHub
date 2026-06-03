# Audit Report: Onda A · Part 2 — FSRS Fiel à Referência

**Verdict: PASS**

> Auditado em 2026-06-03 contra `.vibeflow/specs/agent-first-onda-a-part-2.md`.

### DoD Checklist

- [x] **1 — Interface preservada.** `app/utils/fsrs.py::FSRS` expõe `init_card()` e `evaluate(card, rating)` retornando dict com **exatamente** as 9 chaves (`state, stability, difficulty, elapsed_days, scheduled_days, reps, lapses, last_review, due`) — verificado no test_fsrs check 1. `record_review()` e `review_cli.py` funcionam sem alteração de assinatura (smoke de `record_review(3,3)` OK; `review_cli.py` parseia).
- [x] **2 — Cálculo segue a referência.** Adapter sobre `py-fsrs` 6.3.1 (`Scheduler.review_card`), `desired_retention=0.9`. Fidelidade verificada: `stability(new,Good)` do adapter == py-fsrs direto (check 6, |Δ|<1e-9).
- [x] **3 — `elapsed_days` é tempo real.** Calculado de `last_review` até agora; card novo → 0 (check 1). Não mais espelho de `scheduled_days`.
- [x] **4 — `test_fsrs.py` com ≥5 sequências.** 6 grupos de teste / 14 asserções (new+Good, Easy>Good, Good x3 no vencimento, Again→Relearning+lapse, Again em novo sem lapse, fidelidade). `python tools/test_fsrs.py` → todos OK, exit 0.
- [x] **5 — Estados sem conflação.** Mapeamento fiel (1/2/3 + 0=New); Again em Review → Relearning(3) distinto (check 4). Fase Learning bypassada por `learning_steps=()` (decisão documentada na spec atualizada — `step` não persistido; evita "trap de learning"; modelo DSR puro). `relearning_steps` default preserva Relearning.
- [x] **6 — (Quality) Dependência + schema.** `fsrs>=6.3.1` pinado em `requirements.txt`. Schema `fsrs_cards` inalterado (10 colunas originais). `import sqlite3` em `fsrs.py` = 0. `fsrs.py` antigo substituído (não duplicado). `py_compile` OK.

### Pattern Compliance

- [x] **fsrs-review-flow.md** — semântica de ratings (1-4) e escrita dual preservadas; `evaluate()` continua puro (sem I/O); `record_review()` inalterado consome o novo shape.
- [x] **db-access-layer.md** — `evaluate()` sem I/O de DB; persistência permanece em `record_review()`.

### Convention Compliance

- Sem `import sqlite3` novo; pt-BR; docstrings canônicas. Nenhum Don't violado.

### Decisão arquitetural registrada

- **`learning_steps=()` + `relearning_steps` default + `enable_fuzzing=False`**: opera o modelo DSR puro (intervalos em dias desde a 1ª revisão), contorna a não-persistência do `step` do py-fsrs sem mudar o schema, preserva o estado Relearning, e torna o agendamento determinístico. Trade-off aceito: sem fase de learning de minutos (irrelevante para deck de residência).

### Tests

`python tools/test_fsrs.py` → PASS (14/14, exit 0). Smoke de `record_review` (card real #3) com captura+restauração: state→Review, stability 63.25, scheduled 63 dias, FSRS restaurado (zero alteração líquida).

### Próximo passo

Ready to ship. Onda A completa (part-1 conversacional + part-2 FSRS fiel).
