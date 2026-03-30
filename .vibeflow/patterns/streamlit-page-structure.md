---
tags: [streamlit, ui, pages, tabs, components, layout]
modules: [app/pages/, app/utils/styles.py]
applies_to: [pages, components]
confidence: inferred
---
# Pattern: Streamlit Page Structure

<!-- vibeflow:auto:start -->
## What
Standard anatomy of a MedHub Streamlit page: config → inject_styles → tabs → per-tab logic with DB queries, filters, and cards. Pages use `st.tabs()` for top-level sections, `st.expander()` for list items, `st.multiselect()` for filters.

## Where
- `app/pages/1_dashboard.py` — KPI metrics + charts
- `app/pages/2_estudo.py` — caderno de erros + FSRS player
- `app/pages/3_biblioteca.py` — resumos browser + PDF index
- `app/pages/4_simulados.py` — AI-generated MCQs

## The Pattern

**Page header (required):**
```python
import streamlit as st
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from app.utils.styles import inject_styles, COLORS, metric_card

st.set_page_config(page_title="Nome da Página", page_icon="📋", layout="wide")
inject_styles()  # MUST be called before any st.markdown with HTML
```

**Top-level structure (tabs):**
```python
tab1, tab2 = st.tabs(["📖 Nome Tab 1", "🧠 Nome Tab 2"])

with tab1:
    # subtitle in secondary color
    st.markdown('<p style="color: #A8B3C2;">Descrição da tab.</p>', unsafe_allow_html=True)
    # ... content ...

with tab2:
    # ... content ...
```

**Filter pattern:**
```python
# Multiselect specialty filter — always before the list
areas = sorted(df['area'].unique())
filtro_area = st.multiselect("Filtrar Especialidade", areas, placeholder="Todas", key="filt_cad")
f_df = df[df['area'].isin(filtro_area)] if filtro_area else df
```

**Error list with expanders:**
```python
for _, r in f_df.iterrows():
    with st.expander(f"Erro #{r['id']} · {r['titulo']}"):
        st.caption(f"{r['area']} › {r['tema']}")
        if r['elo_quebrado'] and r['elo_quebrado'] != 'N/A':
            st.markdown(f"**🔗 Elo Quebrado:** {r['elo_quebrado']}")
        if r['explicacao_correta'] and r['explicacao_correta'] != 'N/A':
            st.success(f"{r['explicacao_correta']}")
        if r['armadilha_prova'] and r['armadilha_prova'] != 'N/A':
            st.warning(f"**Armadilha:** {r['armadilha_prova']}")
```

**Metric display (dashboard):**
```python
col1, col2, col3 = st.columns(3)
with col1:
    metric_card("Total de Questões", f"{metrics['total_questoes']:,}",
                delta="↑ 45 esta semana", delta_type="up")
```

**Cached DB load inside page:**
```python
@st.cache_data(ttl=60)
def load_flashcards():
    # ... query ...
    return list_of_dicts

cards = load_flashcards()
# User action clears cache:
if st.button("🔄 Sincronizar"):
    st.cache_data.clear()
    st.rerun()
```

**DB path in pages (legacy pattern — prefer db.py functions):**
```python
import os as _os
DB_PATH = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(
    _os.path.abspath(__file__)))), 'ipub.db')
```

## Rules
- `inject_styles()` is the first call after `st.set_page_config` — always
- `st.tabs()` for major sections — not nested st.columns at top level
- Specialty filter: `st.multiselect(..., placeholder="Todas", key="filt_<unique>")` — unique key per page
- `@st.cache_data(ttl=60)` on all DB-loading functions inside pages
- `st.cache_data.clear()` + `st.rerun()` after any write action
- Inline HTML with `unsafe_allow_html=True` for cards that need custom styling
- `st.success()` for correct answers/explanations, `st.warning()` for armadilhas, `st.error()` for fatal errors
- `st.caption()` for breadcrumb metadata (area › tema)
- All user-facing strings in pt-BR

## Examples from this codebase

File: `app/pages/2_estudo.py` (lines 1-71) — tab1 structure with config, inject_styles, tabs, filter, expander list

File: `app/pages/2_estudo.py` (lines 73-185) — tab2 FSRS player with cache, session state, progress bar, columns
<!-- vibeflow:auto:end -->

## Anti-patterns
- Calling `st.markdown(html, unsafe_allow_html=True)` before `inject_styles()` — CSS classes won't be defined
- Using `st.radio()` for specialty filters — `st.multiselect` is the standard
- Creating unique DB connections per row in a loop — query once, iterate the DataFrame
- Skipping `key=` parameter on widgets that appear in multiple tabs — causes Streamlit DuplicateWidgetID errors
