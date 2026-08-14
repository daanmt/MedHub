# Spec: flashcards-p3-part-4 — eventos de geração/reincidência + eficácia + fim do bypass

> De: `.vibeflow/prds/flashcards-p3-fila-proveniencia.md` · 2026-08-14 (ai-eng)
> Dependencies: .vibeflow/specs/flashcards-p3-part-1.md (colunas de proveniência existem p/ a eficácia ler)

## Objective

A geração deixa evento persistido, a reincidência vira métrica de 1ª classe consultável, a eficácia de aprendizado ganha script read-only — e o último caminho de escrita sem gate (`update_flashcard_fields`) fecha.

## Definition of Done

1. [ ] `tools/event_log.py` (novo, ~40 ln): `registrar(tipo, dados)` → append em `history/generation_log.jsonl` ({ts, tipo, **dados}); NUNCA levanta exceção (falha → WARN no stdout); leitura `eventos(tipo=None)` p/ consumo do efficacy.
2. [ ] `insert_questao`: insert com cards → evento `generation` {questao_id, n_cards, avisos}; hit F25 → evento `reincidencia` {questao_id, hits}; falha de log não derruba insert (teste com path de log inválido). Decisão registrada: `ledger_self.record` NÃO serve p/ eventos (opened/resolved auto-resolveria o passado).
3. [ ] `db.update_flashcard_fields` ganha gate ERRO-level sobre campos presentes (encoding + template + embutida, mesmos predicados parciais do recurate): violação → `ValueError` (chamador `apply_reforja` já valida antes — dupla camada barata); `card_checks` indisponível → WARN e segue (degradação anunciada, nunca silêncio). Fecha o bypass documentado na docstring da regen queue.
4. [ ] `tools/learning_efficacy.py` (novo, read-only `mode=ro`): rates 1-4 por `tipo × card_version × quality_source × selection_reason` (revlog novo; linhas antigas NULL agrupadas como `pre-P3`) + reincidência: questões com evento `reincidencia` APÓS já terem card cunhado / questões cardadas. Saída humana + `--json`. Gate anti-decorativo documentado no docstring: 3 ciclos sem alterar decisão → remover.
5. [ ] Testes: `tools/test_event_log_efficacy.py` — evento gravado/lido; insert gera generation (fixture db); update_flashcard_fields rejeita template e aceita válido; efficacy agrega fixture mínima de revlog.
6. [ ] Craftsmanship: `pytest` verde; JSONL fora do git? — `history/` é versionado no repo (ledger_self.jsonl é): generation_log.jsonl SEGUE versionado (eventos não carregam conteúdo clínico — só ids/contagens; teste garante ausência de campos de texto).
7. [ ] `pytest.ini` allowlist atualizado.

## Scope
`tools/event_log.py`✚ · `tools/insert_questao.py` · `app/utils/db.py` · `tools/learning_efficacy.py`✚ · `tools/test_event_log_efficacy.py`✚ · `pytest.ini`. [5+config]

## Anti-scope
NÃO gravar texto clínico em evento (só ids/contagens/tags); NÃO dashboard; NÃO tocar `ledger_self` (ferramenta certa p/ ACHADOS com ciclo de vida, não p/ eventos); NÃO retro-derivar reincidência do histórico (começa agora).

## Technical Decisions
- JSONL dedicado > ledger: eventos são fatos imutáveis; o ledger resolve/reabre — semânticas incompatíveis (correção consciente do C.8.1 do relatório).
- Gate no `update_flashcard_fields` com import lazy de `card_checks` (tools/ → sys.path no corpo): camada app não pode quebrar se tools/ ausente (Streamlit Cloud) — degrada com WARN.

## Applicable Patterns / Risks
- warn-first; db-access-layer. Risco: dupla validação (apply_reforja + db) divergir → ambas consomem os MESMOS predicados de card_checks; teste de não-regressão do apply_reforja segue passando.
