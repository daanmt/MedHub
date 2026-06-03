# Spec: Onda A · Part 2 — FSRS Fiel à Referência

> Gerado via /vibeflow:gen-spec em 2026-06-03
> PRD: `.vibeflow/prds/agent-first-onda-a-revisao-fsrs.md`
> Split: part 2 de 2 (por limite de DoD). Ver `agent-first-onda-a-part-1.md`.

## Objective

Substituir o scheduler caseiro de `app/utils/fsrs.py` por uma implementação fiel ao FSRS de referência (`py-fsrs` / `fsrs4anki`), preservando o schema `fsrs_cards`/`fsrs_revlog` e a interface `init_card()`/`evaluate()`, para que os intervalos de revisão sejam corretos.

## Context

O `app/utils/fsrs.py` atual (82 linhas) é uma simplificação que o próprio header admite não ser fiel: dificuldade linear, estabilidade exponencial improvisada usando só ~3 dos 17 pesos, `elapsed_days` igual a `scheduled_days` (deveria ser o tempo real desde o último review), e estados Learning/Relearning conflados. Para o uso por repetição espaçada valer a pena, o agendamento precisa seguir o algoritmo de referência. `record_review()` e `tools/review_cli.py` (e, após a part-1, `tools/fsrs_queue.py`) dependem da interface `FSRS().init_card()` / `FSRS().evaluate(card, rating)`.

## Definition of Done

1. `app/utils/fsrs.py` expõe `FSRS` com `init_card()` e `evaluate(card, rating)` retornando um dict com **exatamente as chaves atuais** (`state, stability, difficulty, elapsed_days, scheduled_days, reps, lapses, last_review, due`); `record_review()` e `review_cli.py` funcionam **sem alteração de assinatura**.
2. O cálculo de estabilidade/dificuldade/intervalo segue a referência (`py-fsrs`/`fsrs4anki`), com `request_retention = 0.9`.
3. `elapsed_days` é o tempo real decorrido desde `last_review` (card novo → `0`); não mais espelho de `scheduled_days`.
4. `tools/test_fsrs.py` valida ao menos **5 sequências de rating conhecidas** (ex.: new→Good→Good, new→Again→Good, new→Easy) contra o intervalo/estado esperado da referência, e `python tools/test_fsrs.py` imprime OK com todos passando.
5. Os estados são mapeados fielmente ao py-fsrs (1=Learning, 2=Review, 3=Relearning) + 0=New do MedHub, **sem conflação**: Again num card em Review leva a Relearning (3), distinto do estado inicial. A fase de Learning (passos de minutos) é **intencionalmente bypassada** via `learning_steps=()` — cards graduam direto para Review (intervalos em dias). Justificativa: o `step` do py-fsrs não é persistido pelo schema atual (anti-scope: sem coluna nova); operar o modelo DSR puro evita o "trap de learning" (cards presos em intervalos de minutos) e é fiel ao FSRS. O `relearning_steps` default (1 passo) preserva o estado Relearning.
6. **(Quality gate)** Se `py-fsrs` for adotado, está **pinado** em `requirements.txt`; o schema `fsrs_cards`/`fsrs_revlog` permanece inalterado (nenhuma coluna adicionada/removida); nenhum `import sqlite3` introduzido fora dos lugares autorizados; o `fsrs.py` antigo é substituído (não duplicado).

## Scope

- `app/utils/fsrs.py` (reescrita) — `FSRS` como adapter sobre `py-fsrs` (ou implementação fiel inline), mantendo a interface pública.
- `requirements.txt` (editar) — adicionar `py-fsrs` pinado, se adotado.
- `tools/test_fsrs.py` (novo) — vetores de teste contra a referência.

## Anti-scope

- Mudança de schema (`fsrs_cards`/`fsrs_revlog` ficam idênticos).
- Backfill / reprocessamento do histórico `fsrs_revlog` (audit trail histórico permanece como está).
- Otimização de pesos FSRS a partir do histórico do usuário (FSRS optimizer) — fora desta onda.
- Mudanças em `record_review()` além do necessário para `evaluate()` ler `last_review` do `card_data`.
- Qualquer item da part-1 (CLI/skill de revisão).

## Technical Decisions

- **Adotar `py-fsrs` em vez de reimplementar o algoritmo à mão.** Trade-off: adiciona uma dependência, mas garante fidelidade e manutenção pela própria open-spaced-repetition; reimplementar arrisca repetir o erro do scheduler caseiro. `py-fsrs` é envolvido atrás da interface `init_card()`/`evaluate()` existente — um **adapter**, não um vazamento da API do py-fsrs para `db.py`.
- **Mapeamento de estado.** Converter entre o dict de `fsrs_cards` (colunas planas) e os objetos `Card`/`Rating` do py-fsrs dentro do adapter. `evaluate()` reconstrói o `Card` a partir do `card_data` (incluindo `last_review` para derivar elapsed/retrievability), aplica a `Rating`, e devolve o dict plano.
- **Compatibilidade de valores legados.** Cards existentes têm `stability`/`difficulty` da fórmula antiga; na próxima revisão o py-fsrs assume a partir desses valores armazenados. Faixas são aproximadamente compatíveis (difficulty 1-10, stability em dias); as primeiras revisões recalibram. Sem migração de dados.
- **`request_retention = 0.9`** preserva o alvo de 90% do sistema atual.

## Applicable Patterns

- `fsrs-review-flow.md` — preservar semântica de ratings, escrita dual, e a interface consumida por `record_review()`.
- `db-access-layer.md` — `evaluate()` continua puro (sem I/O de DB); a persistência permanece em `record_review()`.

## Risks

- **API do `py-fsrs` difere do shape esperado** (usa `Scheduler`/`Card`/`Rating`, retorna `ReviewLog`) → encapsular toda a tradução no adapter; cobrir com `test_fsrs.py`.
- **Reescalonamento dos cards existentes** ao trocar a matemática → é melhoria intencional; `fsrs_revlog` histórico continua válido; comunicar que os `due` futuros vão recalibrar.
- **Drift de versão do py-fsrs** → pinar versão em `requirements.txt`.
- **Divergência entre vetores de teste e a versão instalada** → derivar os valores esperados da própria versão pinada; documentar a versão no topo de `test_fsrs.py`.

## Dependencies

Nenhuma dependência técnica rígida da part-1. Recomendação de execução: **part-1 primeiro** (entrega o uso remoto e isola o risco), esta part-2 em seguida.
