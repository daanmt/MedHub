# Session 074 — Pivot Agent-First: retomada e fechamento da Onda D + commits das Ondas A-D
**Data:** 2026-06-03
**Ferramenta:** Claude Code (Opus 4.8)
**Continuidade:** Sessão 073 (e sessão interrompida que implementou Ondas A-C + metade da Onda D)

---

## O que foi feito

- **Diagnóstico da interrupção:** a sessão anterior caiu no meio da Onda D (Streamlit Encolhe). `db.py` estava pronto (`get_caderno_detalhado` criada, `get_next_due_card` removida), mas `2_estudo.py`, `styles.py` e `streamlit_app.py` estavam intocados e não havia audit.
- **Onda D completada:**
  - `app/pages/2_estudo.py` reescrito (174 → 47 linhas): FSRS Player removido, vira **Caderno de Erros read-only** sem `import sqlite3`, lendo via `get_caderno_detalhado()` com `@st.cache_data(ttl=60)`; banner aponta para `/revisar`.
  - `styles.py`: `flashcard_front`/`flashcard_back` removidos (0 callers) + docstring atualizado.
  - `streamlit_app.py`: página 2 renomeada "Caderno de Erros" 📓 (antes "Caderno & Retenção FSRS" 🧠).
- **Audit da Onda D: PASS** (`.vibeflow/audits/onda-d-streamlit-encolhe-audit.md`) — 6/6 DoD, 3/3 patterns, pytest 4/4 + `test_fsrs.py` 14/14, zero violações de convenção.
- **Decision log:** entrada 2026-06-03 em `.vibeflow/decisions.md` (player removido em favor da revisão conversacional; pitfall de staleness nos pattern docs).
- **Commits atômicos por onda** do trabalho acumulado A-D (staging por hunk em `db.py`, que cruzava 3 ondas) + push.

## Artefatos criados/modificados

- `app/pages/2_estudo.py` (reescrita), `app/utils/styles.py`, `streamlit_app.py`, `app/utils/db.py`
- `.vibeflow/audits/onda-d-streamlit-encolhe-audit.md` (novo), `.vibeflow/decisions.md`
- Commits das Ondas A-C herdadas: `app/utils/fsrs.py` (adapter py-fsrs), `tools/fsrs_queue.py`, `tools/test_fsrs.py`, `tools/cards_regen_queue.py`, `tools/importar_sessoes.py`, skills `/revisar`, `/estilo-flashcard`, `/importar-planilha`, aposentadoria de `regenerate_cards{,_llm}.py`

## Decisões tomadas

- **Remover o FSRS Player, não consertá-lo** — a revisão conversacional (`/revisar`) o superou; Streamlit fica só com Dashboard + Caderno + Biblioteca (conforme spec da Onda D).
- `.claude/settings.local.json` permanece fora dos commits (decisão da sessão 073: PR separado).

## Extensão pós-encerramento (mesma data)

- **Google Drive MCP oficial vinculado (OAuth ok, restart pendente).** Não existe MCP oficial específico para Sheets; o acesso a planilhas é via o connector claude.ai Google Drive. Skill `/importar-planilha` adaptada: pré-requisito atualizado + seção "Planilhas canônicas" (registro de nome/ID a preencher na primeira sessão com acesso). As planilhas são a fonte primária de performance/desempenho e uma delas é o **cronograma** (conciliação com `taxonomia_cronograma`; CLI de persistência a definir na primeira importação real).

## Próximos passos

- **Após restart:** registrar nome/ID das planilhas canônicas em `/importar-planilha` e fazer a primeira leitura via Drive MCP (volume/desempenho + cronograma).
- Regenerar pattern docs stale via `/vibeflow:analyze` (`design-system-usage`, `streamlit-page-structure`, `db-access-layer` ainda referenciam o player e `flashcard_front/back`).
- Onda E (se planejada) ou prioridades do ESTADO: pipeline RAG inverso, busca semântica na Biblioteca.
- `1_dashboard.py` ainda usa `sqlite3` cru — anti-scope da Onda D, candidato a onda futura.
