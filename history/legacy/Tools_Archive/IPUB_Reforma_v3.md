# Reforma Cirúrgica MedHub — v3.0
> **Para:** Claude Code  
> **Contexto:** O Gemini over-engineered a app. Este plano desfaz a complexidade introduzida e estabelece uma arquitetura mínima e estável.

---

## Diagnóstico do Estado Atual

### Problemas identificados nos screenshots

| # | Problema | Origem |
|---|---|---|
| 1 | `TypeError` em `06_flashcards.py:105` — `id_map[cid]` KeyError | shuffle usa IDs de sessão antiga que não existem no cache atual |
| 2 | Botões "Gerar cards" / "Regenerar" não fazem nada | resultado da função não é atribuído ao session_state + falta `st.rerun()` |
| 3 | Dashboard mostra 1555 acertos / 2434 questões / 63.9% — origem duvidosa | lendo de `progresso.md` com parsing frágil ou do EMED xlsx; precisa validar |
| 4 | "Flashcards e Caderno de Erros" misturados na mesma página | Gemini fundiu as duas páginas numa coisa só |
| 5 | "Hot Topics: 164 cards vencidos" e "Revisão Urgente" — FSRS não implementado | Gemini fingiu FSRS com contagem de todos os cards; é fake |
| 6 | "Sessões Recentes" na dashboard — não tem valor na UI | o usuário explicitamente não quer isso |
| 7 | "Sincronizar com GitHub" na sidebar — não funciona no Streamlit Cloud | operação inválida no ambiente de deploy |

---

## Decisões de Arquitetura

### O que DELETAR completamente

```
❌ Qualquer código FSRS na UI (Hot Topics, Cards Vencidos, Revisão Urgente)
   → FSRS é Fase 2, backend only. Não pertence à UI agora.

❌ "Sessões Recentes" no Dashboard
   → Removido por pedido explícito do usuário.

❌ Registro de desempenho por card (Errei/Difícil/Acertei como log)
   → Os botões ficam para UX de navegação, mas SEM persistência de log.
   → Sem fc_session_log, sem métricas de sessão.

❌ "Sincronizar com GitHub" 
   → Não funciona no Streamlit Cloud. Remover.

❌ Fusão "Flashcards e Caderno de Erros" numa página
   → São páginas separadas, funções separadas.
```

### O que MANTER

```
✅ Flashcard builder via LLM + cache JSON — arquitetura correta
✅ Zero-DB para UI — persistência via .md
✅ Resumos por Área — funcionando
✅ Dark theme
✅ st.navigation multipage
```

---

## Nova Estrutura de Páginas

```
streamlit_app.py
  Estudo:
    🏠 Dashboard        → 01_dashboard.py
    🧠 Flashcards       → 02_flashcards.py   (renomear, era 06)
    📖 Caderno de Erros → 03_caderno.py      (só lista/add erros)
    📚 Resumos          → 04_resumos.py
  Análise:
    📈 Progresso        → 05_progresso.py    (mergeado com histórico)
```

**5 páginas. Sem mais.**

---

## Reformas por Arquivo

---

### 01_dashboard.py — Simplificar

**Remover:**
- Sessões Recentes (bloco inteiro)
- Qualquer referência a FSRS ou "cards vencidos"
- Status do Agente (ESTADO.md) — move para sidebar se quiser

**Manter e corrigir:**
- Métricas de erros (total, por área) — fonte: `caderno_erros.md` via parser
- Gráfico de barras Plotly — já está funcionando
- Fix treemap hovertemplate: `'<b>%{label}</b><br>Erros: %{value}<extra></extra>'`

**Sobre as métricas 1555/2434/63.9%:**
Verificar de onde vêm. Se vierem do `progresso.md`:
```python
# utils/parser.py — parse_progresso_metrics()
# Extrair apenas: total_questoes, total_acertos, pct_acertos
# Se o parsing for instável (regex frágil em texto livre), REMOVER as métricas
# É melhor não mostrar do que mostrar dado errado.
```
Se não houver fonte confiável para esses números agora, substituir por:
```python
# Mostrar só o que vem do caderno_erros.md (fonte confiável):
st.metric("Total de Erros Registrados", len(entries))
# + gráfico por área
# Nada mais.
```

---

### 02_flashcards.py — Reescrever do zero (limpo)

**O bug do crash:**
```python
# ❌ BUG ATUAL: shuffle por IDs guardados no session_state
# Quando o cache é regenerado, os IDs mudam e o id_map não bate
filtered = [id_map[cid] for cid in st.session_state.fc_shuffled_ids if ...]
#                         ↑ KeyError quando IDs do cache antigo não existem mais

# ✅ FIX: shuffle por índices, não por IDs
# E sempre reconstruir a lista a partir do cache atual
```

**Código limpo e funcional:**

```python
import streamlit as st
import random
from pathlib import Path
from utils.parser import parse_caderno_erros, read_md
from utils.flashcard_builder import load_or_generate_flashcards

ROOT = Path(__file__).parent.parent.parent
CADERNO_PATH = ROOT / "caderno_erros.md"

st.set_page_config(layout="centered")
st.title("🧠 Flashcards")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Filtros")
    entries = parse_caderno_erros(read_md(str(CADERNO_PATH)))
    all_cards = load_or_generate_flashcards(entries)

    areas_disponiveis = sorted(set(c.get('area', '') for c in all_cards if c.get('area')))
    area_sel = st.multiselect("Área", areas_disponiveis, default=areas_disponiveis)
    embaralhar = st.toggle("Embaralhar", value=True)

    st.divider()
    st.markdown("### Inteligência")
    if st.button("➕ Gerar cards novos", use_container_width=True):
        # Limpa cache do Streamlit para forçar recarga
        st.cache_data.clear()
        with st.spinner("Gerando via LLM..."):
            new_cards = load_or_generate_flashcards(entries, force_regen=False)
        st.success(f"{len(new_cards)} cards disponíveis.")
        # Reseta estado da sessão para evitar KeyError com IDs antigos
        for key in ['fc_idx', 'fc_verso', 'fc_order']:
            st.session_state.pop(key, None)
        st.rerun()

    if st.button("🔄 Regenerar todos", use_container_width=True):
        st.cache_data.clear()
        with st.spinner("Regenerando todos via LLM..."):
            new_cards = load_or_generate_flashcards(entries, force_regen=True)
        st.success("Regeneração completa.")
        for key in ['fc_idx', 'fc_verso', 'fc_order']:
            st.session_state.pop(key, None)
        st.rerun()

# ── Filtra cards ──────────────────────────────────────────────────────────────
filtered = [c for c in all_cards if c.get('area') in area_sel]

if not filtered:
    st.info("Nenhum flashcard para os filtros selecionados.")
    st.stop()

# ── Ordem dos cards (índices — nunca IDs) ─────────────────────────────────────
# Recria a ordem apenas quando necessário (primeira vez ou após reset)
if 'fc_order' not in st.session_state or len(st.session_state.fc_order) != len(filtered):
    order = list(range(len(filtered)))
    if embaralhar:
        random.shuffle(order)
    st.session_state.fc_order = order
    st.session_state.fc_idx = 0
    st.session_state.fc_verso = False

if 'fc_idx' not in st.session_state:
    st.session_state.fc_idx = 0
if 'fc_verso' not in st.session_state:
    st.session_state.fc_verso = False

# Garante que idx nunca ultrapassa o tamanho
total = len(filtered)
idx = st.session_state.fc_idx % total
card = filtered[st.session_state.fc_order[idx]]

# ── Progresso ─────────────────────────────────────────────────────────────────
st.caption(f"{card.get('area','')} › {card.get('tema','')}  ·  Erro #{card.get('erro_origem','')}")
st.progress((idx + 1) / total, text=f"Card {idx + 1} de {total}")

st.divider()

# ── FRENTE ────────────────────────────────────────────────────────────────────
if not st.session_state.fc_verso:
    if card.get('frente_contexto'):
        st.markdown(
            f'<p style="opacity:0.6; font-style:italic; margin-bottom:1.2rem">'
            f'{card["frente_contexto"]}</p>',
            unsafe_allow_html=True
        )
    st.markdown(
        f'<p style="font-size:1.25rem; font-weight:600; line-height:1.5; margin-bottom:1.5rem">'
        f'{card["frente_pergunta"]}</p>',
        unsafe_allow_html=True
    )
    if st.button("Revelar Resposta →", use_container_width=True, type="primary"):
        st.session_state.fc_verso = True
        st.rerun()

# ── VERSO ─────────────────────────────────────────────────────────────────────
else:
    st.markdown(card.get('verso_resposta', ''))

    if card.get('verso_regra_mestre'):
        st.info(f"🧠 **Regra Mestre:** {card['verso_regra_mestre']}")

    if card.get('verso_armadilha'):
        st.warning(f"⚠️ **Gatilho:** {card['verso_armadilha']}")

    st.divider()

    # Botões de navegação (sem log de desempenho)
    col1, col2, col3 = st.columns(3)

    def _next():
        st.session_state.fc_idx = (st.session_state.fc_idx + 1) % total
        st.session_state.fc_verso = False
        st.rerun()

    with col1:
        if st.button("← Voltar", use_container_width=True):
            st.session_state.fc_idx = max(0, st.session_state.fc_idx - 1)
            st.session_state.fc_verso = False
            st.rerun()
    with col2:
        if st.button("Próximo →", use_container_width=True, type="primary"):
            _next()
    with col3:
        if st.button("⏭ Pular", use_container_width=True):
            _next()
```

**O que mudou em relação ao código quebrado:**
- Shuffle por **índices** em `fc_order`, nunca por IDs → elimina o KeyError
- Reset explícito de `fc_order` ao gerar/regenerar cards → sem estado stale
- Removido `fc_session_log` completamente
- Removidos botões Errei/Difícil/Acertei (sem backend FSRS, não fazem nada útil)
- Substituídos por ← Voltar / Próximo → / ⏭ Pular

---

### 03_caderno.py — Separar dos flashcards, simplificar

**Remover:**
- Tudo que for FSRS ("Hot Topics", "Cards Vencidos", "Revisão Urgente")
- "Explorador de Lacunas" (se for apenas renome do caderno)
- Qualquer `import sqlite3`

**Estrutura limpa:**
```python
st.title("📖 Caderno de Erros")
st.caption(f"{len(entries)} erros registrados")

# Sidebar: filtros
with st.sidebar:
    areas = sorted(set(e.get('area','') for e in entries if e.get('area')))
    area_sel = st.multiselect("Filtrar por área", areas)
    busca = st.text_input("Buscar", placeholder="palavra-chave...")

# Aplicar filtros
filtered = entries
if area_sel:
    filtered = [e for e in filtered if e.get('area') in area_sel]
if busca:
    filtered = [e for e in filtered if busca.lower() in str(e).lower()]

# Exibir erros
for e in filtered:
    label = f"Erro #{e.get('numero','')} — {e.get('area','')} › {e.get('tema','')}"
    with st.expander(label):
        if e.get('elo_quebrado'):
            st.markdown(f"**Elo Quebrado:** {e['elo_quebrado']}")
        if e.get('conceito_de_ouro') or e.get('regra_mestre'):
            st.info(f"🧠 {e.get('conceito_de_ouro') or e.get('regra_mestre')}")
        if e.get('armadilha_examinador'):
            st.warning(f"⚠️ {e['armadilha_examinador']}")

# Form de novo erro (collapsible)
with st.expander("➕ Registrar novo erro", expanded=False):
    with st.form("novo_erro"):
        # campos...
        submitted = st.form_submit_button("Salvar")
        if submitted:
            # append no caderno_erros.md
            ...
```

---

### 05_progresso.py — Merge com histórico, remover FSRS fake

**Remover:**
- Qualquer UI de FSRS
- "Cards vencidos" / "Revisão urgente"

**Manter:**
- Gráfico distribuição de erros por área (pizza + treemap — fix hovertemplate)
- Gráfico sessões por dia (barras, lendo de `history/`)
- Tabela de sessões recentes (apenas as 10 mais recentes, sem "registrar sessão" pelo app)

---

## Checklist de execução para o Claude Code

### Fase 1 — Limpeza (fazer primeiro, ~20 min)

```
[ ] 1. Inspecionar caderno_erros.md: head -200 caderno_erros.md
        → identificar formato real das entradas
        → reescrever parser em utils/parser.py

[ ] 2. Remover de 03_caderno.py:
        - import sqlite3 e qualquer uso de conn/cursor
        - bloco "Hot Topics" / FSRS
        - bloco "Explorador de Lacunas" (se for apenas wrapper do caderno)

[ ] 3. Fix 01_dashboard.py:
        - remover bloco "Sessões Recentes"
        - fix treemap hovertemplate
        - validar origem dos dados 1555/2434 — se parser frágil, remover métricas

[ ] 4. Fix 05_progresso.py:
        - remover FSRS fake
        - fix hovertemplate do treemap (mesmo fix do dashboard)
```

### Fase 2 — Reescrita do flashcard (~30 min)

```
[ ] 5. Deletar o código atual de 06_flashcards.py (ou renomear para 02_flashcards.py)
        e implementar o código limpo desta spec (seção acima)

[ ] 6. Atualizar streamlit_app.py:
        pages = {
            "Estudo": [
                st.Page("app/pages/01_dashboard.py",   title="Dashboard",        icon="🏠"),
                st.Page("app/pages/02_flashcards.py",  title="Flashcards",       icon="🧠"),
                st.Page("app/pages/03_caderno.py",     title="Caderno de Erros", icon="📖"),
                st.Page("app/pages/04_resumos.py",     title="Resumos",          icon="📚"),
            ],
            "Análise": [
                st.Page("app/pages/05_progresso.py",   title="Progresso",        icon="📈"),
            ],
        }
```

### Fase 3 — Validação (~10 min)

```
[ ] 7. Testar 06_flashcards.py (novo): navegar 10 cards, trocar área, embaralhar
[ ] 8. Testar botão "Gerar cards novos" → deve mostrar spinner + success + rerun
[ ] 9. Testar botão "Regenerar todos" → mesmo comportamento
[ ] 10. Confirmar que Caderno mostra a lista de erros (não mais vazia)
[ ] 11. Confirmar que Dashboard não tem mais "Sessões Recentes"
```

---

## Regras para o Claude Code nessa sessão

1. **Não implementar FSRS** — nenhum código de agendamento, nenhum cálculo de estabilidade/dificuldade, nenhuma UI de "revisão urgente"

2. **Não adicionar SQLite** em nenhuma página do app Streamlit

3. **Não adicionar "registro de sessão"** — o usuário não quer isso na UI

4. **Não adicionar "Sincronizar com GitHub"** — não funciona no Streamlit Cloud

5. **Antes de modificar qualquer parser**, inspecionar o arquivo fonte (`head -200 caderno_erros.md`) e confirmar o formato real

6. **Se um dado não tem fonte confiável, não exibir** — melhor não mostrar do que mostrar errado

7. **Cada página tem uma função, uma só:**
   - Dashboard → visão geral dos erros
   - Flashcards → estudar ativamente
   - Caderno → consultar e registrar erros
   - Resumos → ler conteúdo clínico
   - Progresso → analítica histórica
