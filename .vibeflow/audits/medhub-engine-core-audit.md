# Audit Report: medhub-engine-core

> Data: 2026-04-05
> Spec: `.vibeflow/specs/medhub-engine-core.md`

**Verdict: PASS**

---

## Testes Automatizados

`pytest` detectado. 4 testes em `tools/test_memory.py` — **4/4 PASS**.

---

## DoD Checklist

- [x] **DoD 1** — `app/engine/__init__.py` exporta `get_topic_context`, `get_review_queue`, `summarize_performance` via `__all__`. Verificado por assertion em runtime.

- [x] **DoD 2** — Todas as 3 funções têm: type hints em parâmetros e retorno (`-> dict`), docstrings com descrição completa das chaves do dict retornado. Retorno sempre `dict`. Verificado por `__annotations__` e `__doc__`.

- [x] **DoD 3** — `get_topic_context("Cardiologia")` retornou `{'resumo_path': 'resumos/Clínica Médica/Cardiologia/Insuficiência Cardíaca.md', 'resumo_content': <str>, 'erros_recentes': [], 'cards_ativos': 0, 'weak_areas': [...]}`. Com tema inexistente: todas as chaves presentes, valores seguros (`None`, `[]`, `0`). Nenhuma exceção em qualquer path.

- [x] **DoD 4** — `get_review_queue()` retornou `{'atrasados': [5 cards], 'hoje': [], 'novos': [10 cards]}`. Cada card contém `card_id`, `frente_pergunta`, `verso_resposta`, `due`. Verificado por assertion em todos os items de todos os buckets.

- [x] **DoD 5** — `summarize_performance()` retornou `{'total_erros': 181, 'taxa_acerto': 78.2, 'padroes': [41 items]}`. Tipos corretos (`int`, `float`, `list[dict]`). LangGraph não ativado. Com `medhub_memory.db` ausente: retornaria `padroes: []` silenciosamente (try/except amplo).

- [x] **DoD 6** — Grep de `import sqlite3` em `app/engine/*.py` → zero resultados. Todas as queries passam por `app.utils.db`.

- [x] **DoD 7** — `python -c "from app.engine import get_topic_context, get_review_queue, summarize_performance; print('OK')"` → `OK`.

---

## Pattern Compliance

- [x] **db-access-layer.md** — Engine não importa `sqlite3`. As duas novas funções em `db.py` (`get_erros_por_tema`, `get_cards_by_bucket`) seguem o padrão `conn = get_connection()` → `pd.read_sql(..., conn, params=(...))` → `conn.close()`. Retornam `list[dict]` e `dict[str, list[dict]]` (não raw rows). Evidence: `db.py` linhas 167-255.

- [x] **error-insertion-pipeline.md** — `get_erros_por_tema` consulta `questoes_erros JOIN taxonomia_cronograma` usando os campos corretos do schema (`tipo_erro`, `habilidades_sequenciais`, `armadilha_prova`, `explicacao_correta`). Evidence: `db.py:get_erros_por_tema`.

---

## Convention Compliance

- Naming: `app/engine/` com arquivos `snake_case.py` ✓
- Retornos tipados: `dict`, `list[dict]` — nunca raw rows ✓
- Try/except com safe defaults em cada fonte independente ✓
- Sem LangGraph activation em nenhum path ✓
- Sem `import sqlite3` fora de `app/utils/db.py` ✓

---

## Files alterados

| Arquivo | Ação |
|---|---|
| `app/engine/__init__.py` | CRIADO |
| `app/engine/get_topic_context.py` | CRIADO |
| `app/engine/get_review_queue.py` | CRIADO |
| `app/engine/summarize_performance.py` | CRIADO |
| `app/utils/db.py` | EDITADO — `get_erros_por_tema()` e `get_cards_by_bucket()` adicionadas |

Budget: 5 / ≤ 6 arquivos.
