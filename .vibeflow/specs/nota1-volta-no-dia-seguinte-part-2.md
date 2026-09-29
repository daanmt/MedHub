# Spec: nota 1 volta no dia seguinte -- part 2 (novos do lote = saldo do teto)

> Origem: F140, pergunta 3. Decisão do operador (28/09/2026): *"saldo por teto, que deve passar a 100 cards/dia."*

## Objetivo

O lote do player passa a trazer cards novos até encher o saldo do teto do dia, em vez de 10 fixos.

## Contexto

`tools/fsrs_queue.py --export-player` chama `_ordered_queue(new_limit=args.new_limit)` com default 10 e depois corta o lote no saldo (`teto_do_dia`). Em 28/09 o saldo era 53 e o lote saiu com 13: o gargalo era o `--new-limit`, não o teto. O teto já é 100 por dia (`day_plan.TETO_BASE`), até 150 em regime de dívida.

## Que fricção esta spec remove -- e ela é virtuosa ou viciosa?

Remove o pedido manual de `--new-limit N` a cada lote: **viciosa** (o operador já tem um freio, o teto). Nenhuma fricção virtuosa é tocada.

## Definition of Done

1. `tools/test_fsrs_queue_player.py::test_export_sem_new_limit_enche_o_saldo_com_novos` escrito ANTES e visto vermelho: com 3 vencidos, 80 novos no pool e consumo 47, o lote sai com 53 cards (3 + 50).
2. `test_new_limit_explicito_vence_o_saldo`: `--new-limit 5` entrega 5 novos.
3. `test_fila_do_chat_segue_com_10_novos`: `--list` e `--next` sem a flag continuam com 10.
4. Conferência read-only contra o banco real: export com `--out` no scratch entrega `total` = saldo do dia.
5. A docstring do módulo lista os 4 buckets na ordem que a função usa.
6. Suíte completa verde e `auto_check --changed` PASSED; nenhuma violação dos Don'ts.

## Escopo

- `tools/fsrs_queue.py`: `--new-limit` sem default no parser; no `--export-player`, ausente = saldo do lote; nos demais caminhos, ausente = 10. Função pura para a escolha.
- `tools/test_fsrs_queue_player.py`.

## Anti-escopo

- Mudar o teto, o regime de dívida ou o contador de consumo (F142).
- Mudar a ordem dos buckets.
- Trocar o lote que está no ar.
- Skills e contratos: part 3.

## Decisões técnicas

- **Duas passadas.** O saldo depende só dos vencidos, que não dependem de `new_limit`: mede-se o saldo com 0 novos e pede-se a fila de novo com `new_limit = saldo`. O corte do lote no saldo continua igual.
- **`--limit` explícito** segue mandando no tamanho do lote; sem `--new-limit`, os novos enchem esse limite.
- **Fila do chat fica em 10.** A decisão dele foi sobre o lote; o `/revisar` conversacional é fallback e drena em blocos de 10 a 15.

## Padrões aplicáveis

- `patterns/db-access-layer.md`: a fila segue lendo por `db.get_cards_by_bucket`.

## Riscos

- **Carga do dia seguinte.** Projeção da auditoria: +40 novos hoje dão cerca de +17 revisões amanhã. O teto de 100 por dia absorve: vencido tem prioridade sobre novo, então a entrada de novos se regula sozinha.
- **`--prevalencia`** puxa o pool inteiro e corta em Python: o corte tem de usar o mesmo `new_limit` resolvido.

## Dependencies

- `.vibeflow/specs/nota1-volta-no-dia-seguinte-part-1.md`
