# Spec: Onda D — Streamlit Encolhe (Dashboard + Biblioteca + Caderno)

> Gerado via /vibeflow:gen-spec em 2026-06-03
> ROADMAP.md Linha Evolutiva 8 (MedHub Agent-First)

## Objective

Encolher o Streamlit para o que exige UI real — Dashboard, Biblioteca e um Caderno de Erros read-only — removendo o FSRS Player (superado pela revisão conversacional `/revisar`) e o código morto associado.

## Context

Com a Onda A, a revisão de flashcards virou conversacional (`/revisar` + `fsrs_queue.py`), funcional remotamente. O FSRS Player do Streamlit (`2_estudo.py` tab2) ficou redundante, ainda carrega bugs (closure captura card errado; `fc_idx % total` mascara overflow) e viola a convenção `db.py`-only (`sqlite3` cru). Além disso, `db.py::get_next_due_card()` é código morto (0 callers) e quebrado (faz `SELECT f.frente, f.verso` — colunas removidas), e `styles.py::flashcard_front/back` não têm callers. A visão do usuário: Streamlit = dashboard de performance + checagem rápida de resumo.

## Definition of Done

1. `app/pages/2_estudo.py` não contém mais o FSRS Player: vira um **Caderno de Erros read-only** (consulta), sem `import sqlite3`, lendo via uma função de `db.py`.
2. `db.py` ganha `get_caderno_detalhado(area=None)` retornando `id, area, tema, titulo, elo, caso, explicacao, armadilha` (colunas que a página de consulta usa), com filtro opcional por área; `get_caderno_erros()` existente permanece intacto.
3. `db.py::get_next_due_card()` é **removido** (código morto + bug de colunas inexistentes); nenhum caller resta.
4. `styles.py::flashcard_front` e `flashcard_back` são **removidos** (0 callers); o docstring do módulo é atualizado.
5. `streamlit_app.py` reflete o novo papel da página (título "Caderno de Erros", sem "Retenção FSRS"); a página aponta o usuário para `/revisar` (revisão conversacional) em vez do player.
6. **(Quality)** Nenhum `import sqlite3` em `app/pages/2_estudo.py`; sem referências órfãs aos símbolos removidos (`get_next_due_card`, `flashcard_front/back`) em `app/`/`tools/`; `py_compile` OK em todos os arquivos tocados.

## Scope

- `app/pages/2_estudo.py` (reescrita) — Caderno de Erros read-only via `db.py`.
- `app/utils/db.py` (editar) — adicionar `get_caderno_detalhado`; remover `get_next_due_card`.
- `app/utils/styles.py` (editar) — remover `flashcard_front`/`flashcard_back` + atualizar docstring.
- `streamlit_app.py` (editar) — título/ícone da página 2.

## Anti-scope

- Dashboard (`1_dashboard.py`) e Biblioteca (`3_biblioteca.py`) — mantidos como estão (são a face desejada). Não refatorar o `sqlite3` do dashboard nesta onda.
- FSRS, geração de cards, ingestão MCP.
- Mudança de schema.
- Reescrever `get_caderno_erros()` (manter intacto para não quebrar callers).

## Technical Decisions

- **Remover o player, não consertá-lo.** A revisão conversacional o superou; consertar bugs de algo descontinuado é desperdício. O Caderno read-only permanece porque é consulta rápida útil.
- **Nova função `get_caderno_detalhado` em vez de estender `get_caderno_erros`** — evita risco a callers existentes; a página passa a respeitar `db.py`-only (sem `sqlite3`).
- **Remover `get_next_due_card` agora** — é o bug latente do ROADMAP, sem callers; mantê-lo só perpetua confusão.

## Applicable Patterns

- `db-access-layer.md` — página consome `db.py`; sem `sqlite3` em página.
- `streamlit-page-structure.md` — `inject_styles()`, `st.multiselect(placeholder="Todas")`, expanders.
- `design-system-usage.md` — usar componentes/COLORS; remover componentes mortos.

## Risks

- **Remover `get_caderno_erros` por engano** → manter intacto; só adicionar a função nova.
- **Página quebrar sem o player** → fluxo de revisão migrou para `/revisar`; a página passa a indicar isso explicitamente.
- **Caller oculto de `get_next_due_card`/`flashcard_*`** → grep confirma 0 antes de remover (DoD #6).

## Dependencies

Nenhuma. (A revisão conversacional da Onda A part-1 já substitui o player.)
