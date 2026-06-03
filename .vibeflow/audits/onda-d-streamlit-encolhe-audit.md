# Audit Report: Onda D — Streamlit Encolhe (Dashboard + Biblioteca + Caderno)

> Auditado em 2026-06-03 (sessão 074) contra `.vibeflow/specs/onda-d-streamlit-encolhe.md`
> Testes: `pytest` (4/4 passed) + `python tools/test_fsrs.py` (14/14 OK)

**Verdict: PASS**

### Test Suite

- `python -m pytest` → **4 passed** (`tools/test_memory.py`: persistence, cross_thread, search, consolidation), 0.43s
- `python tools/test_fsrs.py` (script standalone, não coletado pelo pytest) → **14 asserts OK**, incluindo paridade de stability com py-fsrs de referência
- `py_compile` OK em todos os arquivos tocados (`2_estudo.py`, `styles.py`, `db.py`, `streamlit_app.py`)

### DoD Checklist

- [x] **1. `2_estudo.py` vira Caderno de Erros read-only, sem `import sqlite3`, lendo via `db.py`** — reescrita completa (174 → 47 linhas). FSRS Player removido; única fonte de dados é `get_caderno_detalhado()` via `app.utils.db`; banner `st.info` aponta para `/revisar` (revisão conversacional). Zero `sqlite3`, zero `DB_PATH`, zero fallback SQL cru.
- [x] **2. `db.py::get_caderno_detalhado(area=None)`** — `app/utils/db.py:91`. Retorna DataFrame com `id, area, tema, titulo, elo, caso, explicacao, armadilha` (aliases sobre `habilidades_sequenciais`, `o_que_faltou`, `explicacao_correta`, `armadilha_prova`); filtro opcional por área via parâmetro bound (`WHERE t.area = ?`). `get_caderno_erros()` permanece intacta (`db.py:47`).
- [x] **3. `get_next_due_card()` removida** — substituída no mesmo ponto do arquivo; grep em `app/` + `tools/` confirma 0 referências remanescentes. Bug latente (`SELECT f.frente, f.verso` sobre colunas inexistentes) eliminado.
- [x] **4. `flashcard_front`/`flashcard_back` removidos de `styles.py`** — 0 callers antes da remoção (grep); docstring do módulo atualizado (componentes agora: `metric_card`, `content_card`).
- [x] **5. `streamlit_app.py` reflete o novo papel** — `st.Page(..., title="Caderno de Erros", icon="📓")` (antes: "Caderno & Retenção FSRS" 🧠). A página em si instrui o uso de `/revisar` para revisão espaçada.
- [x] **6. Quality** — nenhum `import sqlite3` em `2_estudo.py`; `sqlite3` remanescente apenas onde autorizado (`db.py`, `app/memory/*`, CLIs em `tools/`, `1_dashboard.py` — anti-scope explícito desta onda); sem referências órfãs a `get_next_due_card`/`flashcard_front`/`flashcard_back`; `py_compile` OK.

### Pattern Compliance

- [x] `db-access-layer.md` — página consome função tipada de `db.py` que retorna DataFrame; leitura parametrizada (`pd.read_sql(..., params=...)`, nunca interpolação); `conn.close()` explícito. O anti-pattern documentado ("`import sqlite3` in a Streamlit page — found in `2_estudo.py` tab1") foi **eliminado na fonte**.
- [x] `streamlit-page-structure.md` — `st.set_page_config` → `inject_styles()` primeiro; filtro `st.multiselect("Filtrar Especialidade", ..., placeholder="Todas", key="filt_cad")`; lista em `st.expander` com `st.caption` breadcrumb (`area › tema`); `st.success` para explicação, `st.warning` para armadilha, `st.error` para falha fatal; `@st.cache_data(ttl=60)` no load de DB; strings em pt-BR. **Desvio justificado:** página não usa mais `st.tabs()` — virou seção única (o player que justificava a segunda tab foi removido pela spec).
- [x] `design-system-usage.md` — `inject_styles()` antes de qualquer HTML; cor inline única é `#A8B3C2` (= `COLORS['secondary_fg']`, mesmo padrão de subtitle das demais páginas); componentes mortos removidos sem órfãos; zero gradients/shadows.

### Convention Violations

Nenhuma.

### Staleness em `.vibeflow/` (follow-up, não bloqueia)

Os pattern docs ficaram desatualizados em relação a esta onda (conteúdo dentro de marcadores auto — corrigir via `/vibeflow:analyze` ou `/vibeflow:teach`, não à mão):

- `design-system-usage.md` — ainda documenta `flashcard_front`/`flashcard_back` como componentes ativos.
- `streamlit-page-structure.md` — ainda descreve `2_estudo.py` como "caderno + FSRS player" com tabs, e referencia `4_simulados.py` (inexistente).
- `db-access-layer.md` — anti-pattern cita o `sqlite3` do `2_estudo.py` tab1 (agora resolvido; `1_dashboard.py` segue sendo o único caso pendente, fora do scope desta onda).
