# Plano de Refatoração IPUB — v2.0
> **Para:** Claude Code / Antigravity  
> **Contexto:** A arquitetura Zero-DB está funcionando. Flashcards via LLM estão gerando qualidade. Este plano mapeia o que refatorar, o que polir e o que não tocar.

---

## 1. Estado Atual — O Que Está OK e Não Tocar

| Componente | Status | Observação |
|---|---|---|
| `st.navigation` multipage | ✅ Sólido | Não mexer |
| Resumos por Área (`03_resumos.py`) | ✅ Funcionando | Navegação + modo edição OK |
| Dashboard métricas básicas | ✅ Funcionando | Melhorar gráfico (P2) |
| Arquitetura Zero-DB para UI | ✅ Correta | Persistência via `.md` |
| `flashcard_builder.py` com LLM + cache | ✅ Arquitetura correta | Só polir UI |
| `.streamlit/config.toml` dark theme | ✅ OK | Não mexer |

---

## 2. Problemas Críticos a Resolver

### 2.1 — Bug: `sqlite3` no `03_caderno.py` (P0)
O Gemini introduziu código SQLite na página do Caderno durante o redesign. Remover **qualquer** `import sqlite3` e `conn =` do arquivo `03_caderno.py`. O Caderno lê exclusivamente do `caderno_erros.md`.

### 2.2 — Bug: Parser do `caderno_erros.md` (P0)
A página do Caderno exibe `"O caderno_erros.md não parece conter marcadores H4 padrão"` — o parser busca `####` mas o formato real é diferente. **Antes de qualquer coisa:** inspecionar as primeiras 100 linhas do arquivo e reescrever o regex para o formato real. O Dashboard conta 92 erros, então o parser do dashboard está funcionando; copiar a lógica dele para o caderno.

### 2.3 — Bug: Datas das sessões no Progresso (P1)
Todas as sessões mostram `2026-03-14 00:00:00` — está lendo `mtime` do arquivo em vez de parsear a data do conteúdo. Fix em `utils/parser.py`:
```python
def parse_session_date(content: str) -> datetime | None:
    patterns = [
        r'\*\*Data:\*\*\s*(\d{4}-\d{2}-\d{2})',
        r'\*Data:\s*(\d{4}-\d{2}-\d{2})',
        r'Data:\s*(\d{4}-\d{2}-\d{2})',
    ]
    for pat in patterns:
        m = re.search(pat, content[:500])
        if m:
            return datetime.strptime(m.group(1), '%Y-%m-%d')
    return None
```

### 2.4 — Bug: Sessões recentes no Dashboard desatualizadas (P1)
Mostra `session_011` como mais recente mas hoje é `session_023`. Ordenar por número extraído do nome:
```python
files.sort(key=lambda f: int(re.search(r'(\d+)', f.stem).group(1)), reverse=True)
```

---

## 3. Nova Página: Entry-Point dos Flashcards (`06_flashcards.py`)

### Contexto de uso
O usuário estuda nos ambulatórios, mobile, aguardando aulas. O flashcard precisa de **entry-point dedicado** — não enterrado dentro do Caderno de Erros. A nova página é o destino principal para sessões rápidas de retenção.

### Estrutura da nova página
```
app/pages/06_flashcards.py
```

Adicionar ao `streamlit_app.py`:
```python
pages = {
    "Estudo": [
        st.Page("pages/01_dashboard.py",    title="Dashboard",         icon="🏠"),
        st.Page("pages/06_flashcards.py",   title="Flashcards",        icon="🧠"),  # NOVO
        st.Page("pages/03_caderno.py",      title="Caderno de Erros",  icon="📖"),
        st.Page("pages/02_resumos.py",      title="Resumos",           icon="📚"),
    ],
    "Análise": [
        st.Page("pages/04_progresso.py",    title="Progresso",         icon="📈"),
        st.Page("pages/05_historico.py",    title="Histórico",         icon="🗓️"),
    ],
}
```

### Layout da página `06_flashcards.py`

```python
import streamlit as st
from utils.parser import parse_caderno_erros, read_md
from utils.flashcard_builder import load_or_generate_flashcards
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
CADERNO_PATH = ROOT / "caderno_erros.md"

st.set_page_config(layout="centered")  # flashcard = tela centrada, não wide

# ── Header ──────────────────────────────────────────────────────────────────
st.title("🧠 Flashcards")

# ── Filtros de sessão (sidebar) ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Configurar sessão")
    
    entries = parse_caderno_erros(read_md(CADERNO_PATH))
    areas = sorted(set(e.get('area', '') for e in entries if e.get('area')))
    
    area_filtro = st.multiselect("Área", options=areas, default=areas)
    tipo_filtro = st.multiselect(
        "Tipo de card",
        options=["elo_quebrado", "armadilha"],
        default=["elo_quebrado", "armadilha"],
        format_func=lambda x: {"elo_quebrado": "🔗 Elo Quebrado", "armadilha": "⚠️ Armadilha"}[x]
    )
    embaralhar = st.toggle("Embaralhar", value=True)
    
    st.divider()
    st.caption("Gerenciamento")
    if st.button("➕ Gerar cards para novos erros", use_container_width=True):
        with st.spinner("Gerando via LLM..."):
            all_cards = load_or_generate_flashcards(entries, force_regen=False)
        st.success(f"{len(all_cards)} cards disponíveis.")
    
    if st.button("🔄 Regenerar todos (LLM)", use_container_width=True):
        with st.spinner("Gerando todos os cards..."):
            all_cards = load_or_generate_flashcards(entries, force_regen=True)
        st.success("Regeneração completa.")

# ── Carrega e filtra flashcards ──────────────────────────────────────────────
entries = parse_caderno_erros(read_md(CADERNO_PATH))
all_cards = load_or_generate_flashcards(entries)

filtered = [
    c for c in all_cards
    if c.get('area') in area_filtro
    and c.get('tipo') in tipo_filtro
]

if embaralhar and 'fc_shuffled' not in st.session_state:
    import random
    st.session_state.fc_shuffled = random.sample(filtered, len(filtered))
    filtered = st.session_state.fc_shuffled

if not filtered:
    st.info("Nenhum flashcard para os filtros selecionados.")
    st.stop()

# ── Estado da sessão ─────────────────────────────────────────────────────────
if 'fc_idx' not in st.session_state:
    st.session_state.fc_idx = 0
if 'fc_verso' not in st.session_state:
    st.session_state.fc_verso = False
if 'fc_session_log' not in st.session_state:
    st.session_state.fc_session_log = []  # lista de {card_id, resultado}

idx = min(st.session_state.fc_idx, len(filtered) - 1)
card = filtered[idx]
total = len(filtered)

# ── Progresso e meta ─────────────────────────────────────────────────────────
acertos = sum(1 for l in st.session_state.fc_session_log if l['resultado'] == 'acertou')
revistos = len(st.session_state.fc_session_log)

col_meta1, col_meta2, col_meta3 = st.columns(3)
col_meta1.metric("Card", f"{idx + 1} / {total}")
col_meta2.metric("Acertos na sessão", acertos)
col_meta3.metric("Taxa", f"{int(acertos/revistos*100)}%" if revistos else "—")

st.progress((idx + 1) / total)

# ── Breadcrumb ────────────────────────────────────────────────────────────────
tipo_label = {"elo_quebrado": "🔗 Elo Quebrado", "armadilha": "⚠️ Armadilha"}.get(card['tipo'], "📋")
st.caption(f"{card.get('area','')} › {card.get('tema','')}  ·  {tipo_label}  ·  Erro #{card.get('erro_origem','')}")

st.divider()

# ── FRENTE ───────────────────────────────────────────────────────────────────
if not st.session_state.fc_verso:
    if card.get('frente_contexto'):
        st.markdown(f"*{card['frente_contexto']}*")
        st.markdown("")  # espaçamento

    st.markdown(f"### {card['frente_pergunta']}")

    st.markdown("")
    if st.button("Revelar Resposta →", use_container_width=True, type="primary"):
        st.session_state.fc_verso = True
        st.rerun()

# ── VERSO ─────────────────────────────────────────────────────────────────────
else:
    # Resposta direta
    st.markdown(f"### {card['verso_resposta']}")
    st.markdown("")

    # Regra Mestre
    if card.get('verso_regra_mestre'):
        st.info(f"🧠 **Regra Mestre:** {card['verso_regra_mestre']}")

    # Gatilho/Armadilha
    if card.get('verso_armadilha'):
        st.warning(f"⚠️ **Gatilho do Examinador:** {card['verso_armadilha']}")

    st.markdown("")
    st.markdown("**Como foi?**")
    col1, col2, col3 = st.columns(3)

    def _advance(resultado: str):
        st.session_state.fc_session_log.append({
            'card_id': card['id'],
            'erro_origem': card.get('erro_origem'),
            'resultado': resultado,
        })
        st.session_state.fc_idx += 1
        st.session_state.fc_verso = False
        if st.session_state.fc_idx >= total:
            st.session_state.fc_idx = 0
            st.session_state.fc_shuffled = None  # reembaralha na próxima
        st.rerun()

    with col1:
        if st.button("❌ Errei / Revisar", use_container_width=True):
            _advance('errou')
    with col2:
        if st.button("😅 Difícil", use_container_width=True):
            _advance('dificil')
    with col3:
        if st.button("✅ Acertei", use_container_width=True):
            _advance('acertou')
```

---

## 4. Polimento da UI dos Flashcards

### Problemas visuais visíveis nos screenshots

**Problema 1 — Verso: texto da resposta muito grande**
O `verso_resposta` está sendo renderizado como `### heading`, deixando fonte enorme. Reduzir para markdown normal com bold:
```python
# ❌ Atual
st.markdown(f"### {card['verso_resposta']}")

# ✅ Correto
st.markdown(card['verso_resposta'])  # LLM já formata com **negrito** onde necessário
```

**Problema 2 — Caixas "Regra Mestre" e "Armadilha" com background escuro demais**
Os `st.info()` e `st.warning()` do Streamlit dark mode ficam opacos demais. Alternativa com CSS customizado:
```python
# No início de 06_flashcards.py, após imports:
st.markdown("""
<style>
/* Caixas de destaque mais leves no dark mode */
.stAlert {
    border-radius: 8px;
    border-left-width: 4px;
}
/* Remove padding excessivo da frente/verso */
.block-container { max-width: 800px; }
</style>
""", unsafe_allow_html=True)
```

**Problema 3 — Frente: contexto e pergunta sem hierarquia visual clara**
O contexto está em itálico (bom), mas a pergunta precisa de separação visual:
```python
# Frente com hierarquia clara
if card.get('frente_contexto'):
    st.markdown(
        f'<p style="color: var(--text-color); opacity: 0.65; font-style: italic; '
        f'margin-bottom: 1rem;">{card["frente_contexto"]}</p>',
        unsafe_allow_html=True
    )

# Pergunta em destaque — sem heading, mas com tamanho e peso adequados
st.markdown(
    f'<p style="font-size: 1.3rem; font-weight: 600; line-height: 1.5;">'
    f'{card["frente_pergunta"]}</p>',
    unsafe_allow_html=True
)
```

**Problema 4 — Caption "ELO QUEBRADO · MODO RETENÇÃO" em ALL CAPS**
Streamlit não converte para maiúsculas automaticamente — o código está forçando upper(). Remover o `.upper()` e deixar em sentence case.

---

## 5. Polimento do `03_caderno.py`

### Remover SQLite (P0)
Localizar e remover todo código com:
- `import sqlite3`
- `conn = sqlite3.connect(...)`
- `conn.row_factory`
- Qualquer `cursor.execute(...)` ou `conn.commit()`

### Reativar listagem de erros (P0 — depende do fix do parser)
Após corrigir o parser, a listagem precisa:
```python
# Filtros na sidebar
areas = sorted(set(e.get('area','') for e in entries))
area_sel = st.multiselect("Área", areas)
busca = st.text_input("Buscar", placeholder="palavra-chave...")

# Aplicar filtros
filtered = entries
if area_sel:
    filtered = [e for e in filtered if e.get('area') in area_sel]
if busca:
    filtered = [e for e in filtered
                if busca.lower() in str(e).lower()]

# Renderizar
for entry in filtered:
    with st.expander(f"Erro #{entry['numero']} — {entry.get('area','')} › {entry.get('tema','')}"):
        st.markdown(f"**Elo Quebrado:** {entry.get('elo_quebrado','')}")
        st.markdown(f"**Regra Mestre:** {entry.get('conceito_de_ouro','')}")
        if entry.get('armadilha_examinador'):
            st.warning(f"⚠️ {entry['armadilha_examinador']}")
```

---

## 6. Polimento do `01_dashboard.py`

### Gráfico de barras → Plotly (P2)
```python
import plotly.express as px

fig = px.bar(
    df_area.sort_values('erros'),
    x='erros', y='area',
    orientation='h',
    template='plotly_dark',
    color_discrete_sequence=['#378ADD'],
    labels={'erros': 'Erros', 'area': 'Área'},
)
fig.update_layout(
    margin=dict(l=0, r=20, t=0, b=0),
    showlegend=False,
    height=280,
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
)
fig.update_traces(hovertemplate='%{y}: %{x} erros<extra></extra>')
st.plotly_chart(fig, use_container_width=True)
```

### Fix treemap tooltip (P0 — 5 minutos)
```python
fig_tree.update_traces(
    hovertemplate='<b>%{label}</b><br>Erros: %{value}<extra></extra>'
)
```

---

## 7. Arquitetura Final dos Arquivos

```
IPUB/
├── streamlit_app.py              ← adicionar 06_flashcards na navegação
│
├── app/
│   ├── pages/
│   │   ├── 01_dashboard.py       ← fix treemap tooltip + migrar bar para plotly
│   │   ├── 02_resumos.py         ← não mexer
│   │   ├── 03_caderno.py         ← remover SQLite + fix parser + filtros
│   │   ├── 04_progresso.py       ← fix datas sessões
│   │   ├── 05_historico.py       ← fix ordenação sessões
│   │   └── 06_flashcards.py      ← NOVO: entry-point dedicado
│   │
│   └── utils/
│       ├── parser.py             ← fix regex caderno + parse_session_date()
│       ├── file_io.py            ← não mexer
│       └── flashcard_builder.py  ← não mexer (arquitetura correta)
│
└── flashcards_cache.json         ← gerado automaticamente, adicionar ao .gitignore
```

---

## 8. Ordem de Execução para o Claude Code

### Sprint 1 — Fixes críticos (fazer primeiro, ~30 min)
1. **`03_caderno.py`:** remover todo código SQLite
2. Inspecionar `caderno_erros.md` (`head -100 caderno_erros.md`) → reescrever parser
3. **`04_progresso.py`:** fix treemap `hovertemplate`
4. **`utils/parser.py`:** `parse_session_date()` lendo data do conteúdo do arquivo

### Sprint 2 — Nova página flashcards (~45 min)
5. Criar `app/pages/06_flashcards.py` com o código acima
6. Adicionar à navegação em `streamlit_app.py`
7. Testar filtros de área + embaralhar + log de sessão
8. Testar botão "Gerar cards para novos erros"

### Sprint 3 — Polimento UI (~30 min)
9. Fix hierarquia visual frente/verso (remover `###` do verso_resposta)
10. Fix `caption` ALL CAPS → sentence case
11. Fix CSS das caixas Regra Mestre / Armadilha
12. **`01_dashboard.py`:** migrar bar chart para Plotly + fix ordenação sessões recentes

### Sprint 4 — Caderno funcional (~20 min)
13. **`03_caderno.py`:** adicionar filtros de área + busca por texto
14. Validar formulário "Novo Erro" ainda funciona após remoção do SQLite

---

## 9. O Que NÃO Fazer Nessa Refatoração

- **Não implementar SQLite** em nenhuma página da UI — isso é Fase 2 do roadmap, exclusivo para backend FSRS
- **Não refatorar `02_resumos.py`** — está funcionando perfeitamente
- **Não mexer no `.streamlit/config.toml`** — tema dark está correto
- **Não migrar `flashcard_builder.py`** para SQLite — cache JSON é suficiente e correto
- **Não adicionar autenticação** — app é local/single-user por design

---

## 10. Contexto de Uso — Lembrete para o Claude Code

O sistema tem **dois ambientes distintos**:

| Ambiente | Ferramenta | Uso |
|---|---|---|
| **IDE (profundo)** | Antigravity + Claude Code | Analisar questões, criar resumos, registrar erros, rodar workflows `.agents/` |
| **UI Mobile (ambulatório)** | Streamlit | Flashcards durante espera, consulta rápida de resumos, checar dashboard |

A UI **não substitui** o agente — ela serve uma necessidade específica de mobilidade e revisão ativa. Qualquer feature que faz sentido só na IDE não pertence à UI.
