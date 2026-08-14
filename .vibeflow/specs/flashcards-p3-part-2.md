# Spec: flashcards-p3-part-2 — banda prioritária no dreno padrão

> De: `.vibeflow/prds/flashcards-p3-fila-proveniencia.md` · 2026-08-14 (ai-eng)
> Dependencies: .vibeflow/specs/flashcards-p3-part-1.md (selection_reason existe no revlog)

## Objective

Card nascido de erro recente entra na frente de novos FIFO no dreno padrão — a reincidência é atacada na fila, não só no `--pre-bloco` opt-in — e todo card servido diz por que veio.

## Definition of Done

1. [ ] `get_cards_by_bucket` ganha bucket `erros_frescos`: cards `state=0` nascidos de erro (questao_id NOT NULL) com criação (`due`) dentro de `JANELA_FRESH_H=48`, cap `CAP_FRESH=8`, ordenados por criação DESC (mais fresco primeiro); constantes módulo-level em `db.py` (sem tabela de política).
2. [ ] Sem duplicata: ids de `erros_frescos` são EXCLUÍDOS do bucket `novos` (teste com card que qualificaria para ambos).
3. [ ] Cada card de cada bucket carrega `selection_reason` ∈ {vencido, fresh_error, agendado, novo} (atrasados→vencido, erros_frescos→fresh_error, hoje→agendado, novos→novo).
4. [ ] `fsrs_queue._ordered_queue` serve na ordem `atrasados → erros_frescos → hoje → novos`; `--next`/`--list` emitem `selection_reason`; `--cluster` continua funcionando (sort estável por bucket).
5. [ ] `get_cards_by_bucket` migra para `ativo_where('f.')` (consumidor de "ativo" que escapou do censo — `nq < 2` sem COALESCE em `db.py:593`); `--pre-bloco`/`get_fresh_error_cards` INTOCADOS.
6. [ ] `tools/test_fila_prioritaria.py`: fixture com 1 vencido + 1 fresco-de-erro + 1 agendado-hoje + 2 novos (1 velho, 1 card-base fresco SEM questao_id) → ordem servida correta; card-base fresco NÃO entra na banda fresh_error (é `novo`); cap respeitado.
7. [ ] Craftsmanship: `pytest` verde; consumidores existentes de `get_cards_by_bucket` (grep) continuam funcionando — chave nova é aditiva.

## Scope
`app/utils/db.py` · `tools/fsrs_queue.py` · `tools/test_fila_prioritaria.py` (novo) · `pytest.ini`. [3+config]

## Anti-scope
NÃO tabela/arquivo de política; NÃO reordenar o FIFO de `novos` (segue `f.id ASC`); NÃO mexer em `day_plan.py` (consome `get_fresh_error_cards`, não o bucket); NÃO limite dinâmico por carga (P4 se a dor aparecer).

## Technical Decisions
- Banda = bucket novo e explícito, NÃO reordenação do bucket `novos`: política nomeada, observável, testável (decisão C.7 do relatório; converge com §22 do anexo GPT).
- `erros_frescos` exige `questao_id NOT NULL`: card-base/andaime fresco não é anti-reincidência — não fura a fila.
- Critério de frescor = `fc.due` (== criação para state=0; contrato já fixado por teste em `get_fresh_error_cards`).

## Applicable Patterns / Risks
- db-access-layer; warn-first (nada bloqueia). Risco: sessão com muitos erros recentes espremer `novos` → cap 8 limita; constante ajustável em 1 linha.
