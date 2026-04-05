# Audit Report: medhub-engine-integration

> Data: 2026-04-05
> Spec: `.vibeflow/specs/medhub-engine-integration.md`

**Verdict: PASS**

---

## Testes Automatizados

`pytest` detectado. 4 testes em `tools/test_memory.py` — **4/4 PASS**.

---

## DoD Checklist

- [x] **DoD 1** — `generate_contextual_cards()` retorna `list[dict]` com todos os campos v5 (`frente_contexto`, `frente_pergunta`, `verso_resposta`, `verso_regra_mestre`, `verso_armadilha`). Quando `resumo_content` presente mas `ANTHROPIC_API_KEY` ausente → fallback heurístico ativo, `frente_pergunta` não começa com padrões genéricos. Validação pós-geração em `_llm_generate()` rejeita cards genéricos antes de retornar. Evidence: `app/engine/generate_flashcards.py:165-169` (validação) + verificado via runtime.

- [x] **DoD 2** — `analyze_error(tema, area)` retorna exatamente `{context, resumo_available, can_generate_cards}`. `suggested_cards` ausente. Sem exceção para tema inexistente (`TemaMuitoEstranhoXYZ999` → `resumo_available=False`, `can_generate_cards=False`). Evidence: `app/engine/analyze_error.py:44-56`.

- [x] **DoD 3** — `app/pages/1_dashboard.py` exibe `### Padrões de Fraqueza` (linhas 88-95) somente quando `perf["padroes"]` não vazio. Bloco é `if perf["padroes"]:` sem `else`, sem empty state. Seção completamente ausente quando lista vazia. Evidence: `app/pages/1_dashboard.py:87-95`.

- [x] **DoD 4** — `python tools/review_cli.py --limit 3` termina sem erros (returncode=0). Bug pré-existente corrigido: colunas legadas `f.frente` e `f.verso` removidas do `SELECT_FIELDS` (schema atual não as tem); índices de coluna atualizados. Evidence: `tools/review_cli.py:19-31`.

- [x] **DoD 5** — Nenhum `import sqlite3` nos novos arquivos `app/engine/` (grep retornou vazio). Dashboard usa `inject_styles()` + `content_card()` + `COLORS` de `app.utils.styles`. Evidence: imports em `app/pages/1_dashboard.py:8-9`.

- [x] **DoD 6** — `quality_source='heuristic'` quando sem resumo ou sem API key. `quality_source='contextual'` seria setado (linhas 203-204) após LLM OK. Diferenciação implementada e testada. Evidence: `app/engine/generate_flashcards.py:197-208`.

---

## Pattern Compliance

- [x] **error-insertion-pipeline.md** — `generate_contextual_cards()` retorna schema v5 completo com campos `tipo` (`elo_quebrado` | `armadilha`), `quality_source`, `needs_qualitative`. Armadilha card só criado se `len(armadilha) > 20 and armadilha != "N/A"` — mesma regra de `insert_questao.py`. Evidence: `generate_flashcards.py:80,95`.

- [x] **design-system-usage.md** — Nova seção no dashboard usa `content_card()` de `app.utils.styles`. `inject_styles()` adicionado ao topo do dashboard (necessário para que `.medhub-card` CSS funcione). Sem HTML inline com hex hardcoded no novo bloco. Evidence: `1_dashboard.py:8,12,91-95`.

- [x] **streamlit-page-structure.md** — `inject_styles()` adicionado logo após `st.set_page_config()`. Nova seção usa `st.markdown()` + `unsafe_allow_html=True` via `content_card()`. Sem padrão quebrado. Evidence: `1_dashboard.py:11-12`.

---

## Convention Compliance

Nenhuma violação nova introduzida. Violações pré-existentes (fora do escopo desta spec):
- `app/pages/1_dashboard.py` ainda contém `import sqlite3` legado e `sqlite3.connect()` direto em `get_dashboard_data()` — pré-existente, fora do escopo da spec.

Conformidades verificadas:
- Sem `import sqlite3` em `app/engine/` ✓
- Type hints em todas as funções públicas (`-> list[dict]`, `-> dict`) ✓
- Docstrings com descrição das chaves de retorno ✓
- Try/except com safe defaults em `analyze_error()` ✓
- Fallback gracioso em `generate_contextual_cards()` para API indisponível ✓
- Nomes de arquivo: `snake_case.py` ✓
- LangGraph não ativado em nenhum path ✓

---

## Files alterados

| Arquivo | Ação |
|---|---|
| `app/engine/generate_flashcards.py` | CRIADO |
| `app/engine/analyze_error.py` | CRIADO |
| `app/engine/__init__.py` | EDITADO — exports de 3 para 5 funções |
| `app/pages/1_dashboard.py` | EDITADO — inject_styles + seção Padrões de Fraqueza |
| `tools/review_cli.py` | EDITADO — remoção de colunas legadas frente/verso do SELECT |

Budget: 5 / ≤ 6 arquivos.

---

## Anti-scope verificado

- `tools/insert_questao.py` — não tocado ✓
- LangGraph — não ativado ✓
- Interface conversacional Streamlit — não criada ✓
- Retrieval semântico/MCP — não usado ✓
- Schema `flashcards` — não alterado ✓
