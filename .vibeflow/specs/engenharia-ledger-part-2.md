# Spec: Engenharia Ledger — Part 2: Fila e Plano (F3 + F4)

> Gerada via /vibeflow:gen-spec em 2026-07-05, a partir de `.vibeflow/prds/engenharia-ledger-f1-f13.md` (Onda 2)

## Objetivo

A fila FSRS entrega cards clusterizados por tema (fim do re-agrupamento manual) e o plano do dia expõe a dívida de atrasados com teto dinâmico — a política de drenagem decidida pelo operador (2026-07-05) vira comportamento derivado, não improviso de sessão.

## Contexto

`fsrs_queue._ordered_queue` achata os buckets (atrasados→hoje→novos) intercalando temas; na s108 o agente re-agrupou 43 cards à mão e a contagem manual errou 3 vezes. Os campos `area`/`tema` já vêm de `db.get_cards_by_bucket` — a clusterização é ordenação local, zero mudança de query. Sobre dívida: 44 agendados excediam o teto de 30/dia antes de qualquer card novo; sem política explícita, teto e backlog se contradizem para sempre.

## Definition of Done

1. [ ] `python tools/fsrs_queue.py --list --cluster` preserva a prioridade de bucket e, dentro de cada bucket, ordena por `(area, tema)` com cards do mesmo tema contíguos; determinístico (mesma entrada → mesma saída).
2. [ ] Sem `--cluster`, a saída é idêntica à atual (regressão zero — comparar JSON antes/depois com a mesma fila).
3. [ ] `python tools/day_plan.py --review-plan` emite os clusters do dia (area, tema, contagem por bucket, total) e a soma dos totais bate com `fsrs_queue.py --list` na mesma execução.
4. [ ] `day_plan.py` (render e `--json`) expõe `divida_atrasados` e `teto_efetivo`. Política teto dinâmico: `teto_base = 30`; regime de dívida quando `atrasados > teto_base`; `teto_efetivo = min(teto_base + atrasados, 2 * teto_base)`; fora do regime, `teto_efetivo = teto_base`. Parâmetros como constantes nomeadas.
5. [ ] Política documentada em `core/contracts/fsrs-management-contract.md` (seção nova, ASCII limpo, marcada com a data da decisão do operador).
6. [ ] Craftsmanship: day_plan permanece read-only; nenhum `import sqlite3` novo; argparse com help claro para as flags novas; zero violações dos Don'ts de `conventions.md`.

## Escopo

- `tools/fsrs_queue.py` — flag `--cluster` (ordenação secundária estável dentro do bucket).
- `tools/day_plan.py` — flag `--review-plan` + campos `divida_atrasados`/`teto_efetivo` no build/render.
- `core/contracts/fsrs-management-contract.md` — seção "Política de teto dinâmico".

Budget: 3 arquivos (≤6 OK).

## Anti-escopo

- Não mudar `db.get_cards_by_bucket` nem qualquer SQL — a ordenação é em Python, no CLI.
- Não mudar a ordem default (sem flag) — o contrato de `/revisar` referencia a assinatura atual.
- Não implementar drenagem automática (o teto dinâmico INFORMA; quem drena é a sessão de revisão conduzida pelo agente).
- Não implementar "modo mutirão" nem alternativas descartadas pelo operador.
- Não tocar o contrato de `/revisar` (Onda 3) — a menção ao `--cluster` no fluxo entra lá se necessário.

## Decisões Técnicas

1. **Ordenação estável em Python** (`sorted(key=(area, tema))` por bucket): preserva a sub-ordem por `due` dentro do mesmo tema (sort estável). Trade-off: perde-se a ordem global por due dentro do bucket, mas o bucket inteiro é drenado na sessão — o custo é nulo e o ganho pedagógico é o objetivo do F3.
2. **`--review-plan` deriva de `get_cards_by_bucket` uma vez** e agrega em Python — mesma fonte da fila real, impossível divergir (a classe de erro de contagem manual morre por construção).
3. **Fórmula do teto com cap 2×**: linear até o cap evita tanto o teto furado todo dia quanto pico de burnout; constantes nomeadas (`TETO_BASE`, `CAP_MULTIPLICADOR`) para ajuste barato. Proposta do PRD (questão aberta 1) — o operador valida na revisão desta entrega.
4. **Dívida = `atrasados` (não inclui `hoje`)**: "hoje" é carga normal, não dívida; alinha com a leitura do F4 no ledger.

## Patterns Aplicáveis

- `db-access-layer.md` — consumo via funções existentes de `db.py`; pós-processamento em Python, não SQL.
- `fsrs-review-flow.md` — filtro `needs_qualitative < 2` e semântica de buckets intocados.

## Riscos

- **Alguma automação depender da ordem default** e alguém ligar `--cluster` por padrão no futuro → mitigação: flag opt-in, default intocado (DoD 2), documentado no help.
- **Teto dinâmico mal calibrado** (sobe demais em dívida grande) → mitigação: cap 2× + constantes nomeadas + validação do operador na revisão; a política vive num contrato editável, não hardcoded espalhado.
- **Cards sem `area`/`tema` (LEFT JOIN pode dar None)** → mitigação: ordenar com fallback `("", "")` no fim do bucket; caso aparece no teste com fila real.

## Dependencies

- `.vibeflow/specs/engenharia-ledger-part-1.md` (toca `day_plan.py` primeiro; evita conflito e o `--handoff-block` já estabelece o padrão de flag derivada).
