# .vibeflow/patterns/ — what this is

Not consumed by vibeflow tooling — this file is for the human (or a future auditing agent)
who lands in this directory and wants to know what's here before reading further.

## What patterns are

Concrete, code-level implementation patterns (with examples) that `vibeflow:gen-spec` grounds
new specs in. They're a **different layer** than governance: `AGENTE.md`, `core/contracts/`,
and `.claude/commands/` are the normative SSOTs; patterns here describe *how the code shapes
that governance in practice*, for spec-time context. Written and updated by `vibeflow:analyze`
(inside `<!-- vibeflow:auto:start/end -->` markers) and `vibeflow:teach` (outside them).

## Active patterns (6, all in the registry — see `../index.md`)

| Pattern | Canonical source (if it conflicts with this file, canonical wins) |
|---|---|
| `db-access-layer.md` | `app/utils/db.py` module docstring |
| `domain-engine-api.md` | `app/engine/__init__.py` + `app/engine/rag.py` |
| `error-insertion-pipeline.md` | `tools/insert_questao.py` docstring + `.claude/commands/analisar-questao.md` §9 |
| `warn-first-check.md` | `tools/auto_check.py`, `tools/doc_drift.py`, `tools/ledger_self.py` (code is the contract) |
| `agent-workflow-protocol.md` | `AGENTE.md` §2-3, §6 — this pattern is a mirror, not the SSOT |
| `clinical-summary-format.md` | `.claude/commands/estilo-resumo.md` — this pattern is a mirror, not the SSOT |

Each carries `status: active`, `canonical_source:`, and `last_verified:` in its frontmatter
(outside the auto-managed block, so `:analyze` won't strip them). If `last_verified` looks old
relative to the modules it covers, treat its code examples with suspicion before citing them.

## Removed (2026-08-25)

`design-system-usage.md`, `streamlit-page-structure.md`, `fsrs-review-flow.md` — all three
described the Streamlit UI (pages, `styles.py`, the FSRS player), which was fully deleted from
the codebase across several earlier sessions ("consolidacao part-1" onward). Confirmed zero
live references repo-wide (code, skills, workflows, contracts, settings) before deletion — only
historical mentions remained in `README.md`, `ROADMAP.md`, `AUDITORIA_MEDHUB.md`, and
`history/*.md`, which is expected and fine (those are narrative records, not dependencies).
Study/review/performance are now skills (`/revisar`, `/performance`), not screens — see
`AGENTE.md` and `core/contracts/fsrs-management-contract.md`.

## Known drift risk

Line-number citations (`file.py (lines N-M)`) rot fast — `db.py` alone tripled in length since
several patterns were first written. Prefer function-name citations over line numbers when
editing a pattern by hand.
