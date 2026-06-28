---
type: spec
projeto: MedHub
feature: revisao-calibrada
part: 3
slug: revisao-calibrada-part-3-barreiras
status: ready
relates_to:
  - docs/plans/s094-revisao-calibrada-PRD.md
  - tools/dormant_refresh.py
  - app/utils/db.py
  - core/contracts/forgetting-curve-contract.md
---

# Spec — Revisão Calibrada · Parte 3: Barreiras de Integridade (Invariantes A e B)

> Deriva do PRD R2 §5.3. Cobre **DoD-8 (barreira A)** e **DoD-9 (barreira B)**. Depende da Parte 1.

## Objective
O sub-modo PREPARAR alimenta a curva de dormência (`review_log`) em **todo** disparo — sem nunca mover o FSRS — e isso vira **auditável por teste**.

## Context
Hoje `tools/dormant_refresh.py --stamp` grava `review_log` sempre com `kind='dormant_refresh'` (só temas vindos do radar). Na fusão, PREPARAR também abre por tema do **cronograma** (não-dormente); se o carimbo não for garantido, o radar passa a achar que o tema "nunca foi revisto" (loop, score distorcido) — o buraco que a Invariante B fecha. A Invariante A (PREPARAR read-only no FSRS) já é a fronteira dura de `forgetting-curve-contract.md`, mas não havia **teste** que falhasse se fosse violada.

## Definition of Done
1. **`--kind` parametrizável.** `tools/dormant_refresh.py --stamp ... --kind {dormant_refresh,directed_review}` grava `review_log` com o `kind` informado; default = `dormant_refresh` (compat). `--kind` inválido → erro de argparse.
2. **Barreira B auditável (curva alimentada).** Teste: após `--stamp --kind directed_review` para um tema, há **exatamente 1** linha nova em `review_log` para aquele `tema_id` com `kind='directed_review'`.
3. **Barreira A auditável (FSRS intocado).** Teste: `SELECT COUNT(*) FROM fsrs_revlog` e o `MAX(due)`/contagem de `fsrs_cards` são **idênticos** antes e depois de um `--stamp` (PREPARAR não move o FSRS).
4. **Gate estático.** Grep/AST: `dormant_refresh.py` não chama `record_review`, não tem `INSERT INTO fsrs_revlog` nem `UPDATE fsrs_cards`. (Asserção que falha se alguém adicionar.)
5. **Craftsmanship gate.** Testes isolados (usam um `ipub.db` de teste ou transação revertida — **nunca** sujam o banco real); seguem o padrão de `tools/test_*.py`. `import sqlite3` só onde já permitido (db.py / CLI standalone).

## Scope
- Adicionar `--kind` ao argparse de `dormant_refresh.py` e repassá-lo a `db.log_review(kind=...)`.
- `tests/test_barreiras_preparar.py` (ou `tools/test_barreiras_preparar.py`, seguindo o local de `test_memory.py`): cobre DoD-2, DoD-3, DoD-4 acima.
- Garantir `db.log_review` já aceita `kind` (aceita — `{dormant_refresh,directed_review,resumo_read,backfill}`); só validar.

## Anti-scope
- A prosa do PREPARAR / mapa de degraus (Parte 4, documental).
- `infer_nota` (Parte 2).
- Refatorar o FSRS ou `record_review`.
- Implementar o loop PREPARAR→DRENAR em código (é protocolo de agente em markdown — Parte 4).

## Technical Decisions
- **Barreira como teste, não como runtime guard.** PREPARAR/DRENAR são protocolo de agente (markdown), não funções; a barreira executável vive no único ponto de código que PREPARAR toca: `dormant_refresh.py` (carimbo) — testá-lo cobre a Invariante. O contrato (Parte 4) carrega a barreira textual.
- **Teste sem sujar o banco real.** Usar `tmp` db (copiar schema via `init_db`) ou conexão com `ROLLBACK`. Decisão: db temporário em `scratchpad`/`tmp`, descartado no fim — determinístico e isolado.
- **`--kind` default compat** = `dormant_refresh`: nenhuma invocação atual quebra.

## Applicable Patterns
- `db-access-layer.md` — `log_review` já é o ponto único; não duplicar SQL.
- `fsrs-review-flow.md` — referência da fronteira: só `record_review` move FSRS; PREPARAR não o chama.
- Padrão de teste de `tools/test_memory.py` (smoke test standalone).

## Risks
- **Teste flako por banco compartilhado.** Mitigação: db temporário isolado, nunca o `ipub.db` real.
- **Falsa sensação de cobertura** (testar só o caminho feliz). Mitigação: DoD-4 é um gate estático (grep) que pega regressão futura mesmo sem rodar o caminho.

## Dependencies
- `.vibeflow/specs/revisao-calibrada-part-1-fundacao-dados.md` (schema estável; `log_review` já existente).
