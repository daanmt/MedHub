# Spec: MedHub — Limpeza Cirúrgica

> Gerado via /vibeflow:gen-spec em 2026-04-05
> Fase 1 de 3 | PRD: `.vibeflow/prds/medhub-core-simplification.md`

## Objective

Remover tabelas legacy, colunas obsoletas e dead code sem alterar o core loop funcional
(erro → insert_questao → DB → FSRS).

## Context

O `ipub.db` tem 3 tabelas nunca usadas (`fsrs_cache_cards`, `fsrs_cache_revlog`,
`cronograma_progresso`) e a tabela `flashcards` tem 2 colunas do schema v4 (`frente`,
`verso`) que coexistem com o v5 — causando confusão em qualquer inspeção do banco.
`app/utils/db.py` tem 3 funções órfãs (`record_cache_review`, `get_cache_fsrs_state`,
`sync_git`) que nunca são chamadas. `4_simulados.py` está quebrado (Ollama local).
`flashcard_builder.py` nunca foi chamado pela UI. O player de flashcards em `2_estudo.py`
tem fallback v4→v5 que pode ser removido após a limpeza do schema.

## Definition of Done

- [ ] `python tools/cleanup_db.py` termina com exit 0; backup datado criado em `artifacts/backups/` **antes** de qualquer DROP
- [ ] `SELECT name FROM sqlite_master WHERE type='table'` não retorna `fsrs_cache_cards`, `fsrs_cache_revlog`, `cronograma_progresso`
- [ ] `SELECT frente FROM flashcards LIMIT 1` retorna erro `no such column: frente` (coluna removida)
- [ ] `python tools/audit_integrity.py` passa sem warnings
- [ ] `python tools/audit_flashcard_quality.py` retorna os mesmos N/N OK de antes da limpeza
- [ ] `grep -rn "flashcard_builder\|4_simulados\|fsrs_cache\|record_cache_review\|get_cache_fsrs_state\|sync_git" app/ tools/ --include="*.py"` → zero resultados
- [ ] Nenhum `import sqlite3` introduzido fora de `app/utils/db.py` e CLIs standalone (conventions.md Don't #1)

## Scope

| Arquivo | Ação |
|---|---|
| `tools/cleanup_db.py` | CRIAR — script CLI standalone com backup + validação + DROPs |
| `app/pages/4_simulados.py` | DELETAR |
| `app/utils/flashcard_builder.py` | DELETAR |
| `app/utils/db.py` | EDITAR — remover `record_cache_review()`, `get_cache_fsrs_state()`, `sync_git()` |
| `app/pages/2_estudo.py` | EDITAR — remover bloco de fallback legacy (`frente`/`verso` render path) |
| `streamlit_app.py` | VERIFICAR E EDITAR SE NECESSÁRIO — remover qualquer referência explícita a `4_simulados` |

## Anti-scope

- NÃO alterar `fsrs_cards`, `fsrs_revlog`, `questoes_erros`, `taxonomia_cronograma`, `flashcards` (exceto DROP das 2 colunas legacy)
- NÃO tocar `app/utils/fsrs.py`
- NÃO tocar `tools/insert_questao.py`
- NÃO remover `app/memory/` (LangMem permanece intacto)
- NÃO adicionar nenhuma feature

## Technical Decisions

**`cleanup_db.py` é um CLI standalone:**
Authorized exception per `db-access-layer.md` — usa `import sqlite3` diretamente, igual a `insert_questao.py`. Estrutura:
```python
# 1. Backup
shutil.copy2(DB_PATH, f"artifacts/backups/ipub_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
# 2. Validação pré-DROP (segurança)
cursor.execute("SELECT COUNT(*) FROM flashcards WHERE frente_pergunta IS NULL AND frente IS NOT NULL")
assert count == 0, "Migração v5 incompleta — abortar"
# 3. DROPs
cursor.execute("DROP TABLE IF EXISTS fsrs_cache_cards")
cursor.execute("DROP TABLE IF EXISTS fsrs_cache_revlog")
cursor.execute("DROP TABLE IF EXISTS cronograma_progresso")
cursor.execute("ALTER TABLE flashcards DROP COLUMN frente")
cursor.execute("ALTER TABLE flashcards DROP COLUMN verso")
```

**Verificação de versão SQLite:**
`ALTER TABLE ... DROP COLUMN` requer SQLite ≥ 3.35.0. Script deve verificar `sqlite3.sqlite_version_info >= (3, 35, 0)` e falhar com mensagem clara.

**Remoção de `frente`/`verso` em `2_estudo.py`:**
O bloco de fallback tem a forma:
```python
use_structured = bool(frente_pergunta.strip() and verso_resposta.strip())
front = frente_pergunta if use_structured else frente  # ← remover este branch
```
Após a limpeza, todos os cards têm v5 populado. Remover a condição e usar `frente_pergunta`/`verso_resposta` diretamente.

**Streamlit multipage:**
Deletar `4_simulados.py` remove automaticamente a page do menu (convenção de nomes). Verificar se `streamlit_app.py` tem `st.navigation()` ou `st.sidebar` com referência explícita — se sim, remover.

## Applicable Patterns

- **`db-access-layer.md`** — `cleanup_db.py` segue o padrão de CLI standalone: `import sqlite3` autorizado, `conn.close()` explícito, `conn.commit()` antes de fechar em escritas

## Risks

| Risco | Mitigação |
|---|---|
| SQLite < 3.35 não suporta DROP COLUMN | Script verifica versão no início; falha com mensagem clara antes de qualquer modificação |
| `frente_pergunta` NULL em algum card (migração v5 incompleta) | Validação pré-DROP aborta se COUNT > 0 |
| `2_estudo.py` ainda importa `sqlite3` para tab1 legada | Verificar: se o único uso de `import sqlite3` era o fallback, remover o import. Se há outros usos na mesma tab, deixar e registrar como known issue |
| `db.py` tem outras funções que chamam as 3 a remover | Grep por chamadas antes de remover; se encontrado, documentar e resolver primeiro |

## Dependencies

Nenhuma. Esta spec é executável imediatamente.
