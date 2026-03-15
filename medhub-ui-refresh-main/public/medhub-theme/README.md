# MedHub Theme Files

## Como usar

### 1. Tema Streamlit (`config.toml`)
Copie para `.streamlit/config.toml` no seu projeto.

### 2. CSS customizado (`medhub_style.css`)
Copie para a raiz do projeto e injete com:

```python
from medhub_theme.inject_css import apply
apply()  # chamar no início do app
```

Ou inline:
```python
with open("medhub_style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
```

### 3. Plotly theme (`plotly_theme.py`)
```python
from medhub_theme.plotly_theme import apply_medhub_theme, MEDHUB_BAR_COLORS

fig = px.bar(df, x="area", y="acertos", color_discrete_sequence=MEDHUB_BAR_COLORS)
apply_medhub_theme(fig, title="Aproveitamento por Disciplina")
st.plotly_chart(fig, use_container_width=True)
```

### Classes CSS para flashcards
Use via `st.markdown(... unsafe_allow_html=True)`:
- `.regra-mestre` — caixa azul para regras
- `.armadilha` — caixa âmbar para armadilhas
- `.fsrs-novamente`, `.fsrs-dificil`, `.fsrs-bom`, `.fsrs-facil` — botões de rating
