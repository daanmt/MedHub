# Decision Log
> Newest first. Updated automatically by the architect agent.

## 2026-04-05 — DROP COLUMN quebra audit scripts que referenciam colunas legacy

**Contexto:** `medhub-cleanup` spec dropou `frente`/`verso` de `flashcards`. `tools/audit_flashcard_quality.py` usava essas colunas em `EFF_FRONT`/`EFF_BACK` (CASE ELSE fallback), quebrando com `OperationalError: no such column: verso`.

**Pitfall:** Ao dropar colunas de schema migration, verificar TODOS os scripts em `tools/` que referenciam essas colunas — não apenas os listados no scope da spec.

**Fix:** Simplificar `EFF_FRONT`/`EFF_BACK` para `COALESCE(NULLIF(TRIM(campo_v5), ''), '[placeholder]')` — sem ELSE fallback para colunas legacy.

**Grep de segurança pré-DROP:** `grep -rn "frente\|verso" tools/ --include="*.py"` antes de executar qualquer DROP COLUMN de colunas com nomes comuns.
