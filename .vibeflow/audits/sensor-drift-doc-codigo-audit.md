# Audit Report: sensor-drift-doc-codigo (degrau 1/4)

> Auditado em 2026-07-12 — Fable/ai-eng. Implementação: commit `fa7cc2c`.
> Spec: `.vibeflow/specs/sensor-drift-doc-codigo.md`

**Verdict: PASS**

### Testes (gate obrigatório)

`python -m pytest -q` → **79 passed** (63 baseline + 16 da suíte nova), 0 failed.
Suíte nova coletada de fato (a whitelist `python_files` do `pytest.ini` exigiu inclusão
explícita — sem isso o run global dava 63 e o "pytest verde" seria decorativo).

### DoD Checklist

- [x] **1. 4 espécies verificadas** — `tools/doc_drift.py`: `RE_SQLITE`/`RE_SYMBOL`/
  `RE_PATH`/`RE_UNIQUE` + verificadores dedicados; `tools/test_doc_drift.py` cobre
  true→silêncio e false→WARN para cada espécie (16 testes).
- [x] **2. Check 7 no relatório, WARN não altera exit-code** — linha "Sensor de drift
  doc-vs-código (DOC_DRIFT)" no relatório do `--all`; prova viva executada: anotação
  falsificada → `[WARN] DOC_DRIFT: HANDOFF.md:22 -- doc afirma 99, db responde 13`,
  exit 0; restaurada → 0 achados. `success=True` no padrão dos checks 4/5/6.
- [x] **3. Seeds anotados com semântica correta** — 4 seeds: `path tools/test_fsrs.py
  exists` + `symbol app/utils/db.py::get_next_due_card absent` + `unique
  taxonomia_cronograma (area, tema) exists` (ROADMAP) e `sqlite COUNT cards 797-809 == 13`
  (HANDOFF). Semântica WARN = doc ≠ realidade aplicada (correção sobre o PRD, prevista na spec).
- [x] **4. Run real com 0 WARN** — `python tools/doc_drift.py` → "0 achados". Exigiu
  reconciliar claim REALMENTE stale: o ROADMAP dizia "ABERTO: UNIQUE(area,tema)" mas o
  índice `ux_taxonomia_area_tema` existe desde a s083 (`dedup_taxonomia.py`, `init_db.py`).
  O sensor pagou-se antes de nascer — drift real detectado na própria implantação.
- [x] **5. Malformada → WARN sintaxe, allowlist provada** — `DOC_DRIFT_SYNTAX` testado;
  `ALLOWLIST` hardcoded (4 docs); testes: anotação plantada em `resumos/` e em doc fora
  da allowlist são ignoradas; guarda extra: espécie `sqlite` recusa não-SELECT e a
  conexão é `mode=ro` (URI) — o sensor não escreve nem por bug (teste prova db intacto).
- [x] **6. Craftsmanship** — pytest 79 verde; CLI argparse standalone (`--json`);
  prints pt-BR; conexões fechadas em `finally`; tools/ = exceção autorizada do pattern
  db-access-layer; zero violação dos Don'ts.

### Pattern Compliance

- [x] `db-access-layer.md` — conexão própria de tool standalone (exceção autorizada),
  read-only por URI, fechada em `finally`. Sem `sqlite3` fora dos locais permitidos.
- [x] `error-insertion-pipeline.md` (convenções CLI) — argparse, stdout legível,
  exit codes coerentes (0 sempre; WARN-first).
- [x] Template WARN-first dos checks 4/5/6 — check 7 replica exatamente (função
  importada + `[WARN] TAG:` + `success=True` + badge no relatório). 2º uso da família —
  candidata a pattern doc formal (`warn-first-check.md`) segue de pé para o fim da série.

### Convention Violations

Nenhuma.

### Critical Gate

- ✅ Verificado [SEC-adjacente] `tools/doc_drift.py` — f-string em `PRAGMA index_list({tabela})`:
  `tabela` é regex-constrained a `\w+` E a conexão é read-only — sem vetor de injeção útil.
- ✅ Verificado [DS106-adjacente] `tools/test_doc_drift.py` — string `"DELETE FROM flashcards"`
  é fixture que PROVA a recusa de não-SELECT (nunca executada; teste asserta db intacto).
- Clean — no destructive operations detected.

### Achados colaterais (fora do escopo desta spec, registrados)

1. **Item 2 do handoff de integridade é não-item**: `UNIQUE(area,tema)` existe desde a
   s083. A "confirmação sem a constraint em 2026-07-12" foi erro de verificação da
   auditoria externa (N=65). PRD de integridade precisa de correção (fora do budget desta
   spec; corrigir antes de executá-lo).
2. **`pytest.ini` whitelist fixa** é a mesma classe de furo do F35 (lista fixa de suítes
   no `auto_check`) — reforça a prioridade do item 1 do handoff de integridade.
