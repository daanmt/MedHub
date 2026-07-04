# Legacy sessions (001-028)

Pre-modernization era. Sessions in this directory predate three major architecture changes the project went through:

- **Sessão 055** -- automation of the memory layer via SessionStart + PostToolUse hooks; before this, agent memory was manual.
- **Sessão 058** -- `HANDOFF.md` retired, `caderno_erros.md` archived (now in `history/legacy/`), `flashcards_cache.json` archived. Workflows that previously updated those files were rewired to `ESTADO.md` and `ipub.db` exclusively.
- **Sessão 067** -- `sessoes_bulk` table introduced as SSOT for per-session totals, replacing the per-error counter in `taxonomia_cronograma`.

Files here reference the old conventions. A reader landing in one of them will see instructions to update `caderno_erros.md` or `HANDOFF.md` -- those instructions no longer apply. Treat these sessions as the project's **biography**, not as a how-to.

For the active timeline (sessions 029+), see [`../INDEX.md`](../INDEX.md).
