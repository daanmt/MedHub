---
tags: [agent, workflow, boot, closure, protocol, session, ssot]
modules: [.agents/workflows/, AGENTE.md]
applies_to: [workflows, commands, sessions]
confidence: inferred
---
# Pattern: Agent Workflow Protocol

<!-- vibeflow:auto:start -->
## What
Mandatory boot and closure sequence every agent session must follow. Ensures state continuity, SSOT discipline ("siamese twins" rule), and session auditability. Defined in `AGENTE.md` and referenced by all `.agents/workflows/*.md` files.

## Where
- `AGENTE.md` — canonical boot/closure protocol
- `ESTADO.md` — state SSOT updated at session close
- `.agents/workflows/analisar-questoes.md` — error analysis workflow
- `.agents/workflows/criar-resumo.md` — summary creation workflow
- `.agents/workflows/registrar-sessao.md` — session registration workflow
- `history/session_NNN.md` — per-session audit trail

## The Pattern

**Boot sequence (always, every session):**
```
1. Read AGENTE.md                    # boot protocol
2. Read ESTADO.md                    # current project state snapshot
3. Read relevant workflow (.agents/workflows/<workflow>.md)
4. Read relevant skill (.claude/commands/<skill>.md) if applicable
5. Proceed with task
```

**SSOT "siamese twins" rule:**
```
Wrong answer → insert_questao.py → ipub.db (questoes_erros + flashcards)
Lesson learned → update resumo → resumos/<Especialidade>/<Tema>.md

Both must happen. Never one without the other on a significant error.
```

**Error analysis workflow (analisar-questoes.md):**
```
1. Extract metadata: enunciado, alternativas, gabarito, area, tema
2. Identify: elo quebrado, tipo de erro, armadilha, habilidades sequenciais
3. Invoke: python tools/insert_questao.py --area X --tema Y ... [all args]
4. Update resumo: add insight to relevant section OR add to armadilhas
   - Rule: armadilhas section is cumulative (only add, never delete)
   - Rule: no duplication — check if insight already exists before adding
5. Closure protocol (below)
```

**Summary creation workflow (criar-resumo.md):**
```
1. Extract PDF: python tools/extract_pdfs.py <path>
2. Read estilo-resumo.md spec
3. Write resumo with 80/20 benchmark
4. Self-audit against auditar-resumos.md checklist
5. Zero PDF policy: delete PDF + temp .txt files
6. Closure protocol (below)
```

**Closure sequence (every session):**
```
1. Update ESTADO.md with:
   - Current date
   - What changed (errors added, resumos updated, tools fixed, etc.)
   - Counts: N errors, N flashcards, N resumos
   - Next priority action
2. Create history/session_NNN.md with:
   - Session number (increment from last)
   - Date
   - What was done (bullet list)
   - Files changed
   - Next steps
3. Git commit: "sessao NNN: <one-line description>"
```

**Session log format (history/session_NNN.md):**
```markdown
# Sessão NNN — YYYY-MM-DD

## O que foi feito
- [ação concreta e verificável]
- [outra ação]

## Arquivos alterados
- `path/to/file.md` — descrição da mudança

## Próximos passos
- [prioridade 1]
- [prioridade 2]
```

## Rules
- Boot: AGENTE.md FIRST, then ESTADO.md — always, no exceptions
- SSOT: errors go to `ipub.db`, lessons go to `resumos/` — both, every time
- Armadilhas: cumulative — never delete, only add/refine new insights
- Session numbers: sequential, zero-padded to 3 digits (session_060.md, session_061.md...)
- Git commit message: `sessao NNN: <verb> <what>` (lowercase, concise)
- `ESTADO.md` is updated at session end — it's the state snapshot for the next session boot
- Zero PDF policy: always delete PDFs + temp files after extraction (no binary files in repo)
- Never batch-register multiple errors in one workflow call — one call per error

## Examples from this codebase

File: `.agents/workflows/analisar-questoes.md` — full 5-step error analysis with insert_questao invocation

File: `AGENTE.md` — canonical boot sequence (read first, defines order of all other reads)

File: `history/session_060.md` — example session log with structured format
<!-- vibeflow:auto:end -->

## Anti-patterns
- Starting work without reading AGENTE.md + ESTADO.md — leads to duplicate work, stale context
- Updating resumo without inserting error to DB (or vice versa) — violates siamese twins rule
- Deleting or overwriting existing armadilhas — they accumulate across sessions intentionally
- Creating `history/session_NNN.md` without updating `ESTADO.md` first — ESTADO.md is the primary state record
- Batch-committing multiple sessions worth of errors — each error is a discrete event with its own insert call
