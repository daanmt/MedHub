# Spec: flashcards-integridade-part-2 — trava técnica em record_review (Invariante C)

> De: `.vibeflow/prds/flashcards-integridade-geracao.md` · Gerado 2026-08-14 (ai-eng)
> Ordem: 2ª de 6. Sem dependências (independente da part-1).

## Objective

Re-record da mesma revisão passa a ser tecnicamente impossível: `record_review` ganha lock otimista com rowcount, revlog só grava quando o estado gravou, e revisão de card sem linha FSRS deixa de se perder silenciosamente.

## Context

`db.py::record_review` (`:302-354`) faz blind write: `UPDATE fsrs_cards SET ... WHERE card_id=?` sem condição sobre o estado lido; `fsrs_revlog` não tem dedup. Duas chamadas sobre o mesmo estado → 2 linhas de log, a última sobrescreve a primeira. Incidente registrado (card 403, s108); o contrato `revisao-calibrada-contract.md` Invariante C proíbe re-record **sem trava técnica**. Bug adjacente confirmado: se `df.empty` (card sem linha em `fsrs_cards`), o UPDATE atinge 0 linhas e a revisão se perde do estado — só o revlog registra (hoje inalcançável na prática: 0 cards sem linha FSRS, verificado 2026-08-14; mas o caminho existe). `fsrs_revlog.last_elapsed_days` nunca é populado (`:343-350`) — coluna sempre-NULL.

## Definition of Done

1. [ ] `record_review` refatorado em leitura + aplicação testável: o UPDATE carrega `WHERE card_id = ? AND COALESCE(last_review,'') = COALESCE(?,'')` com o `last_review` **lido**; `rowcount == 0` → `conn.rollback()` + `ConcurrentReviewError` (exceção nova em `db.py`), e **nenhuma** linha entra no `fsrs_revlog` (teste conta revlog antes/depois).
2. [ ] Teste determinístico da corrida: aplicar duas vezes com o mesmo estado lido → 1ª passa, 2ª levanta `ConcurrentReviewError`; estado final = resultado da 1ª; revlog tem exatamente 1 linha nova.
3. [ ] `df.empty` → INSERT da linha em `fsrs_cards` (em vez de UPDATE fantasma); corrida no INSERT (linha já criada por outro processo) falha alto por PK — teste do caminho INSERT.
4. [ ] `fsrs_revlog.last_elapsed_days` populado com o `elapsed_days` do estado anterior (NULL só quando primeira revisão) — teste.
5. [ ] `fsrs_queue.py` captura `ConcurrentReviewError`, reporta `[ERRO] rating nao gravado (estado mudou desde a leitura)` e NÃO regrava (fail-safe, sem retry — PRD open question 2, v0).
6. [ ] Craftsmanship: `pytest` verde (incl. `test_fsrs.py` intacto — o adapter FSRS não muda); comportamento observável de `record_review` em fluxo normal idêntico (mesma assinatura, mesmo retorno `new_metrics`); load balancer intocado; padrão db-access-layer respeitado.

## Scope

- `app/utils/db.py` — `record_review` (lock + upsert + last_elapsed_days + exceção `ConcurrentReviewError`); refactor mínimo p/ testabilidade (ex.: `_aplicar_review(conn, card_data, rating)` interna que o público chama após ler).
- `tools/fsrs_queue.py` — tratamento da exceção no ponto de gravação.
- `tools/test_record_review.py` — novo (fixture tmp SQLite com DDL real; monkeypatch `DB_PATH`).

## Anti-scope

- NÃO adicionar UNIQUE/constraint no revlog (resolução de segundo do `review_time` tornaria revisões rápidas legítimas indistinguíveis; o lock otimista é o mecanismo primário).
- NÃO mudar o algoritmo FSRS, `learning_steps`, balanceamento ou a assinatura pública.
- NÃO implementar retry/interatividade no `fsrs_queue` — reportar e seguir.
- NÃO tocar `record_cache_review`/tabelas de cache (fora do subsistema auditado).

## Technical Decisions

- **Lock otimista sobre `last_review` lido** > token de sessão/lock de banco: zero schema novo, 1 cláusula WHERE, cobre exatamente o incidente (single-user, corridas raras). Limite documentado: se surgir concorrência real multi-processo, revisitar.
- **COALESCE(...,'')** para comparar NULL de forma estável entre str/None (primeira revisão tem `last_review` NULL).
- **INSERT no caso empty** em vez de silêncio: perder revisão de estado é o pior modo de falha (invisível). PK de `fsrs_cards` (card_id) faz a corrida do INSERT falhar alto de graça.
- **Transação única já existe** (uma conexão, commit no fim) — a mudança é condicionar o INSERT do revlog ao sucesso do UPDATE, não criar transação nova.

## Applicable Patterns

- `patterns/db-access-layer.md` — read-write com cursor, commit antes de close, params `?`.
- Convenções: exceção com nome claro, mensagem pt-BR acionável no CLI.

## Risks

- **R1**: algum caller de `record_review` além de `fsrs_queue` não tratar a exceção → mitigação: grep de callers no repo durante implement; os que existirem ganham tratamento mínimo (report + não regravar).
- **R2**: `last_review` armazenado com formato de string diferente do lido (str vs datetime) quebrar a igualdade do WHERE → mitigação: comparar exatamente o valor cru lido do banco (sem parse), teste cobre 2ª revisão real (last_review não-NULL).
