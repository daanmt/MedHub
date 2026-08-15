# Spec: consolidacao-part-1 — lista de morte: código

> PRD: `consolidacao-alcancabilidade.md` · Morte aprovada pelo operador; 0 refs provadas (F3 + re-verificação). REGRA: morte = remoção git, NUNCA mover para pasta de archive.

## Objective
O código morto sai do repo: Streamlit inteiro, `reflect.py` (gate anti-decorativo cumprido), auditores/one-shots órfãos e docs absorvidos.

## Definition of Done
1. [ ] `git rm`: `streamlit_app.py` · `app/pages/` (4 .py + `__init__.py`) · `app/utils/styles.py` · `app/engine/summarize_performance.py` · `tools/audit_cards.py` · `tools/reflect.py` · `tools/test_reflect.py` · `docs/AUDITORIA-MECANISMO-CONHECIMENTO-2026-07-12.md` · `artifacts/legacy/HANDOFF_056.md`. `scratch/insert_all.py`: verificar 0 refs (grep) → remover (o dir `scratch/` inteiro se ficar vazio).
2. [ ] `requirements.txt`: saem `streamlit`, `plotly`, `watchdog`; `pandas` FICA (db.py usa).
3. [ ] `pytest.ini`: sai `test_reflect.py` da allowlist; `AGENTE.md §3 passo 5` (que invoca reflect) removido/reescrito em 1 linha.
4. [ ] Pós-remoção: `grep -ri "streamlit\|st\.navigation\|2_estudo\|3_biblioteca\|1_dashboard\|summarize_performance\|reflect\.py" --include="*.py" --include="*.md" --include="*.json"` sobre o repo (exceto history/, .vibeflow/, artifacts/ = registro histórico) → APENAS zero refs vivas; refs em normas vivas encontradas são corrigidas NESTA part (ex.: `gerar-reforco.md:26` cita aba do player; conventions/index do .vibeflow são regenerados na part-5, anotar).
5. [ ] `pytest` verde; contagem nova documentada (base 182 − testes de reflect).
6. [ ] Craftsmanship: nenhum "archive/"; commits atômicos; pt-BR; mensagens citam evidência (0 refs).

## Scope
Os arquivos acima + `requirements.txt` + `pytest.ini` + `AGENTE.md` (§3 passo 5 apenas) + normas vivas com ref direta ao removido.

## Anti-scope
NÃO tocar `app/utils/db.py`/`fsrs*`/engine vivo; NÃO tocar refs a obsidian-notes-rag (part-5); NÃO tocar `.vibeflow/` gerado (part-5 regenera); NÃO deletar nada de filesystem não-versionado (part-7).

## Riscos
`app/utils/parser.py` (legacy, doc diz "kept for backward compat") pode referenciar páginas — verificar; se só o Streamlit o consumia, ele entra na morte TAMBÉM (mesma prova de 0 refs).
