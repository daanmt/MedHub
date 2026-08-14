# Spec: flashcards-p3-part-1 — proveniência no revlog (card_version + selection_reason)

> De: `.vibeflow/prds/flashcards-p3-fila-proveniencia.md` · 2026-08-14 (ai-eng)
> Ordem: 1ª de 4 — DELIBERADAMENTE antes da onda de curadoria: reforja sem estas colunas fica imensurável para sempre. Sem dependências novas (base: ciclo parts 1-6 auditado).

## Objective

Toda revisão passa a registrar **qual versão do card o usuário viu** e **por que o card foi servido** — o revlog vira fonte de avaliação do gerador.

## Definition of Done

1. [ ] `db._ensure_revlog_columns(conn)`: ALTER idempotente adiciona `card_version INTEGER` e `selection_reason TEXT` a `fsrs_revlog` (padrão `_ensure_status_column`); chamado em `record_review` (não na fábrica — custo por conexão desnecessário).
2. [ ] `record_review(flashcard_id, rating, selection_reason=None)`: captura `card_version` atual do flashcard no ATO do record (JOIN/SELECT) e grava ambos no INSERT do revlog; `selection_reason` NULL quando não informado. Assinatura retro-compatível (chamadas antigas seguem válidas).
3. [ ] Teste pós-reforja: card v1 revisado → revlog v1; `card_version` vira 2 (UPDATE) → nova revisão → revlog v2 (é a pergunta "v2 > v1?" respondível).
4. [ ] `fsrs_queue --record` aceita `--reason {vencido,fresh_error,agendado,novo,pre_bloco}` opcional e repassa; sem a flag, grava NULL (teste do CLI via monkeypatch de argv OU teste da função db — o CLI é wiring fino).
5. [ ] Revlog antigo intacto: NENHUM backfill (colunas ficam NULL no histórico — proveniência começa agora); lock otimista/upsert da part-2 anterior preservados (testes existentes passam sem edição).
6. [ ] Craftsmanship: `pytest` verde; padrão db-access-layer; pt-BR.

## Scope
`app/utils/db.py` · `tools/fsrs_queue.py` · `tools/test_record_review.py` (estender). [3 arquivos]

## Anti-scope
NÃO backfill; NÃO mudar shape de retorno de `record_review`; NÃO tocar o balanceador; NÃO capturar version por parâmetro (fonte = banco no ato, à prova de chamador desatualizado).

## Technical Decisions
- `card_version` lido do banco no record (não passado pelo chamador): single-user, a versão vista == versão corrente no ato; elimina drift de chamador. Limite: reforja no meio de uma revisão aberta registraria a nova — aceito e documentado (janela de segundos, single-user).
- ALTER em `record_review` e não em `get_connection`: só o caminho de escrita paga o custo.

## Applicable Patterns / Risks
- db-access-layer; convenções CLI. Risco R1: fixtures antigas de revlog sem as colunas → o ALTER idempotente roda no record antes do INSERT, cobrindo fixtures também.
