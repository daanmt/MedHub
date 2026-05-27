# Archived migrations

One-shot scripts whose target migration has been applied. Kept for historical traceability — they are NOT part of the active toolchain and must not be re-run blindly. The canonical schema is in `Tools/init_db.py`.

| Script | What it did | When |
|---|---|---|
| `migrar_sessoes_bulk.py` | Created `sessoes_bulk` table and seeded it from a hard-coded `HISTORICO` list of (area, questoes_feitas, questoes_acertadas) tuples reflecting the user's pre-app study record. Superseded: `sessoes_bulk` is now created by `Tools/init_db.py`; new rows are written by `Tools/registrar_sessao_bulk.py`. | Pre-sessão 067 |
| `migrate_flashcards.py` | `ALTER TABLE flashcards` adding the v5 columns (`frente_contexto`, `frente_pergunta`, `verso_resposta`, `verso_regra_mestre`, `verso_armadilha`, `quality_source`, `card_version`, `needs_qualitative`). Superseded: v5 columns are now in the canonical `Tools/init_db.py`. | Sessão 057b (flashcards v5) |
| `migrate_memory.py` | One-time namespace move in `medhub_memory.db`: `medhub/session_insights` → `medhub/weak_areas`. Done; no further calls. | Sessão 055 (memory architecture) |
| `popular_subtemas.py` | Reconstructed `taxonomia_cronograma` from `dashboard-emed.xlsx` (no longer tracked). One-shot taxonomy seed. | Sessão 067 |
| `fix_taxonomy_bridge.py` | Bridged orphan `tema_ids` (1–21, 27, 37–41) created by `insert_questao.py` before the Excel ETL started IDs at 22. One-shot data healing. | Pre-sessão 067 |
| `cleanup_db.py` | Dropped legacy `frente` / `verso` columns from `flashcards` and three legacy tables (`fsrs_cache_cards`, `fsrs_cache_revlog`, `cronograma_progresso`) after the v5 migration completed. Backup-first; idempotent on already-clean DBs. | Post-sessão 057b |

If a similar migration is needed again, write a new dated script in `Tools/` — do not copy from here. The patterns are useful (backup-first, dry-run flag, schema validation) but the targets and assumptions are stale.
