---
type: spec
projeto: MedHub
feature: revisao-calibrada
part: 1
slug: revisao-calibrada-part-1-fundacao-dados
status: ready
relates_to:
  - docs/plans/s094-revisao-calibrada-PRD.md
  - app/engine/get_topic_context.py
  - app/utils/db.py
  - .vibeflow/patterns/db-access-layer.md
---

# Spec — Revisão Calibrada · Parte 1: Fundação de Dados

> Deriva de `docs/plans/s094-revisao-calibrada-PRD.md` (R1 §4.5, pré-req §0/§7.7). Cobre **DoD-1, DoD-2** do PRD + o pré-req técnico `_find_resumo`.

## Objective
A nota de dificuldade 1-10 por tema passa a ter onde morar (schema + helpers em `db.py`) e o resolvedor tema→resumo deixa de ser frágil (indexa o nome do arquivo).

## Context
`taxonomia_cronograma` hoje tem `id, area, tema, questoes_realizadas, questoes_acertadas, percentual_acertos, ultima_revisao` — sem campo de dificuldade. `app/engine/get_topic_context._build_index()` indexa **só frontmatter** (`especialidade`/`area`/`aliases`), nunca `path.stem`; logo um tema como "Hepatites Virais" cai no fuzzy `difflib` (cutoff 0.6) e a resolução é instável. O `infer_nota()` da Parte 2 depende de `_find_resumo` confiável (sinal `leu_tema`/`resumo_existe`). Esta parte é a base de tudo — sem dependências.

## Definition of Done
1. **Schema.** `PRAGMA table_info(taxonomia_cronograma)` lista `dificuldade` (INTEGER), `dificuldade_fonte` (TEXT), `dificuldade_at` (TIMESTAMP). Migração idempotente: rodar 2× não falha nem duplica colunas.
2. **Helpers roundtrip.** `db.set_dificuldade(area, tema, 7, 'usuario')` grava; `db.get_dificuldade(area, tema)` retorna `{'nota':7,'fonte':'usuario','at':<iso>}`. Tema inexistente → `set_dificuldade` retorna `False`; `get_dificuldade` → `None`.
3. **Seed.** As 8 notas-exemplo (§4.7) persistidas com `fonte='usuario'`; releitura confirma valores exatos (Hepatites=8, MFC Teoria I=3, D. Exantemáticas Rev=6, Cirurgia Infantil=8, Vulvovaginites=7, Sínd. Hipertensivas=6, Imunizações=9, Sepse=6).
4. **`_find_resumo` por stem.** `_build_index()` passa a indexar `path.stem.lower()`; `_find_resumo('Hepatites Virais')` resolve para o arquivo `Hepatites Virais.md` por match exato de nome (não fuzzy). Verificável: ≥6 dos 8 temas do seed resolvem para um resumo existente por stem.
5. **Craftsmanship gate.** `import sqlite3` permanece **só** em `app/utils/db.py` (migração/seed são CLIs standalone em `tools/`, exceção já prevista em conventions.md). `set_dificuldade` toca **apenas** as 3 colunas novas (grep: nenhum UPDATE em `questoes_*`/`percentual_acertos`/`ultima_revisao`). Segue `db-access-layer.md` (get_connection → cursor → commit → close).

## Scope
- ALTER em `taxonomia_cronograma` via `tools/migrate_dificuldade.py` (idempotente, checa `PRAGMA` antes de cada `ADD COLUMN`).
- `db.set_dificuldade(area, tema, nota, fonte)` + `db.get_dificuldade(area, tema)` (usa `resolve_tema_id`; `dificuldade_at` = `datetime.now().isoformat()`).
- `tools/seed_dificuldade.py` — grava as 8 notas §4.7 via `db.set_dificuldade` (não SQL inline).
- Fix `_build_index` em `get_topic_context.py`: adicionar `index[path.stem.lower()] = str(path)` (stem ganha em colisão — é o identificador mais forte do tema).

## Anti-scope
- `infer_nota()` / `day_plan --difficulty` (Parte 2).
- Qualquer escrita de FSRS, `review_log`, ou edição de skills/contrato/AGENTE (Partes 3-4).
- Schema de "altura de card" (Tier-3, fora do PRD).
- Reindexar ChromaDB (RAG) — `_find_resumo` é o índice em-processo, não o vetorial.

## Technical Decisions
- **3 colunas vs tabela separada.** Colunas em `taxonomia_cronograma` (estado-por-tema já vive lá; join por `(area,tema)` já existe via `resolve_tema_id`). Trade-off: amplia a tabela mas evita nova entidade e novo join.
- **`set_dificuldade` é a única exceção autorizada** à regra "só `insert_questao.py` escreve taxonomia" (PRD §4.5) — confinada a 3 colunas, auditável.
- **Stem sobrescreve frontmatter no índice.** Em colisão (raro), o nome do arquivo vence: é o que a taxonomia usa como `tema`. Mantém fuzzy como fallback final.
- **Seed via helper, não SQL.** Garante o gate de craftsmanship e exercita o roundtrip.

## Applicable Patterns
- `db-access-layer.md` — `get_connection()`, cursor+commit+close, params parametrizados. **Obrigatório.**
- `domain-engine-api.md` — `_find_resumo`/`get_topic_context` é engine; manter assinatura estável.
- CLI tools (`conventions.md §CLI`): argparse, `finally: conn.close()`, print human-readable.

## Risks
- **Regressão no `_find_resumo`** (stem colide com alias intencional). Mitigação: stem por último/precedência; fuzzy permanece como fallback; DoD-4 valida ≥6/8.
- **Migração roda no Cloud.** Mitigação: `ipub.db` é local-only; migração é CLI local, nunca no boot do Streamlit.
- **Índice em-processo cacheado** (index.md tech-debt): seed/teste numa sessão Python nova; não confiar em cache vivo.

## Dependencies
Nenhuma. É a base — implementar primeiro.
