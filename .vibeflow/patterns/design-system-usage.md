---
tags: [design-system, styles, css, streamlit, dark-theme, flat-design]
modules: [app/utils/styles.py, app/pages/]
applies_to: [pages, components]
confidence: inferred
---
# Pattern: Design System Usage

<!-- vibeflow:auto:start -->
## What
Flat dark design system defined in `app/utils/styles.py`. All pages inject global CSS via `inject_styles()`, use color tokens from `COLORS` dict, and compose UI with typed component functions (`metric_card`, `content_card`, `flashcard_front`, `flashcard_back`).

## Where
- `app/utils/styles.py` — token definitions, CSS string, component functions
- `app/pages/*.py` — all 4 pages import and use it
- `streamlit_app.py` — entry point that calls `inject_styles()` globally

## The Pattern

**Import and initialize (top of every page):**
```python
from app.utils.styles import inject_styles, COLORS, metric_card, content_card

st.set_page_config(page_title="...", page_icon="...", layout="wide")
inject_styles()  # Injects GLOBAL_STYLES into Streamlit via st.markdown unsafe
```

**Color tokens — always reference COLORS dict, never hardcode hex:**
```python
COLORS = {
    "background": "#05070A",  # Page background
    "foreground": "#F3F7FC",  # Primary text
    "card": "#11161D",         # Card background
    "secondary": "#0E1116",    # Sidebar background
    "secondary_fg": "#A8B3C2", # Muted text, subtitles
    "muted_fg": "#738093",     # Dimmer text
    "primary": "#2F6BFF",      # Blue accent, CTAs
    "border": "#202A36",       # Card borders
    "border_soft": "#2A3544",  # Softer borders
    "success": "#1FA971",      # Correct, positive delta
    "warning": "#D9A441",      # Armadilha, caution
    "danger": "#D9534F",       # Error, negative delta
}
```

**Metric card (KPI display):**
```python
metric_card("Total de Questões", "2.631",
            delta="↑ 45 esta semana", delta_type="up")
# delta_type="up" → success color; "down" → danger color
```

**Content card (titled block):**
```python
content_card(
    title="Insuficiência Cardíaca",
    content="Paciente masculino, 68 anos...",
    subtitle="Clínica Médica · Cardiologia"
)
```

**Flashcard front:**
```python
flashcard_front(
    category="Cardiologia · ICFEr",
    question=card['frente_pergunta'],
    context=card.get('frente_contexto', '')
)
```

**Flashcard back:**
```python
flashcard_back(
    answer=card['verso_resposta'],
    master_rule=card.get('verso_regra_mestre'),
    trap=card.get('verso_armadilha')
)
```

**Inline HTML card (when component functions don't fit):**
```python
st.markdown(f'''
<div class="medhub-card" style="border-color: {COLORS['border_soft']}">
    <div style="font-size: 1.1rem; font-weight: 500;">{card["frente_pergunta"]}</div>
</div>
''', unsafe_allow_html=True)
```

**Info boxes (medhub-box classes):**
```python
# box-master = navy bg, blue left border (Regra Mestre)
# box-trap = dark amber bg, warning left border (Armadilha)
st.markdown('''
<div class="medhub-box box-master">
    <div class="medhub-box-title" style="color: #7FB8FF;">Regra Mestre</div>
    <div>Betabloqueador deve ser mantido mesmo em IC descompensada leve.</div>
</div>
''', unsafe_allow_html=True)
```

## Rules
- `inject_styles()` always first — before any `st.markdown(html, unsafe_allow_html=True)`
- **No gradients** — `background: linear-gradient(...)` is forbidden
- **No `backdrop-filter`** — forbidden
- **No `box-shadow`** — forbidden (flat design only)
- **Sentence case** — no `text-transform: uppercase` anywhere
- Color references: always `COLORS['key']` in Python, never hardcoded `#2F6BFF`
- FSRS rating buttons use CSS nth-child targeting (column 1=danger, 2=warning, 3=secondary, 4=success) — this is defined in GLOBAL_STYLES, do not override per-page
- `border-radius: 12px` on cards, `10px` on buttons (defined in GLOBAL_STYLES)
- Font: Inter via Google Fonts CDN (already in GLOBAL_STYLES — do not re-import)

## Examples from this codebase

File: `app/utils/styles.py` (lines 1-22) — COLORS dict with all design tokens
File: `app/utils/styles.py` (lines 130-132) — `inject_styles()` function
File: `app/utils/styles.py` (lines 134-149) — `metric_card()` with delta support
File: `app/utils/styles.py` (lines 163-173) — `flashcard_front()` render
File: `app/utils/styles.py` (lines 175-197) — `flashcard_back()` with master rule + trap boxes
File: `app/pages/2_estudo.py` (line 162-164) — inline medhub-card with COLORS reference
<!-- vibeflow:auto:end -->

## Anti-patterns
- Hardcoding color hex values in pages instead of `COLORS['key']` — breaks theme consistency
- Adding `box-shadow` or `gradient` to new components — violates flat design principle
- Calling `st.markdown(html)` before `inject_styles()` — CSS classes won't be defined yet
- Creating new `.medhub-*` CSS classes in page files — all CSS belongs in `styles.py`
