# Audit Report: Orquestracao da Preparacao -- Part 3 (Pre-bloco + reincidencia)

> Auditado em 2026-07-06. Spec: `.vibeflow/specs/orquestracao-preparacao-part-3.md`.
> Dependencia part-2: audit PASS confirmado. Testes rodados de forma independente.

**Verdict: PASS**

### DoD Checklist

- [x] 1. `--pre-bloco TEMA` como 4a acao mutuamente exclusiva; so state-0 frescos do tema; fila sem a flag byte-identica -- branch novo isolado no main; `test_pre_bloco_cli` (JSON valido, bucket='pre-bloco') + `test_list_sem_flag_regressao`; smoke real: 10 cards frescos de Apendicite (727-736 da s109).
- [x] 2. Rating via caminho unico -- o pre-bloco NAO cria caminho de escrita; --record/record_review intocados (delegacao preservada, docstring do proprio CLI).
- [x] 3. Matcher pos-insert com tokens normalizados + limiar; WARN informativo, exit inalterado -- `checar_reincidencia` roda POS-commit dentro de try/except; `test_matcher_nunca_bloqueia` (inclusive com multiplos hits).
- [x] 4. Fixture caso real s109 dispara apontando o card 730; negativo nao dispara -- `test_reincidencia_caso_real_s109` (elo Q4 vs verso do 730) e `test_reincidencia_negativo_nao_dispara` (vancomicina/sepse no mesmo tema).
- [x] 5. Craftsmanship -- constantes nomeadas no topo (LIMIAR_OVERLAP, STOPWORDS); `_tokens` pura e testada; SQL do matcher dentro do insert_questao (excecao standalone autorizada); ASCII; pytest 30 passed; standalone verde; --cluster/--list/--next sem regressao.

### Pattern Compliance

- [x] `error-insertion-pipeline.md` -- transacao original intocada; matcher e extensao pos-commit read-only.
- [x] `fsrs-review-flow.md` / `db-access-layer.md` -- pre-bloco delega a `db.get_fresh_error_cards` (part-2); zero sqlite3 novo no fsrs_queue.
- [x] Precedente `--cluster` (F3) -- opt-in byte-identico replicado.

### Critical Gate

Clean -- diff aditivo, sem operacoes destrutivas.

### Notas / achados laterais (para o ledger, nao bloqueiam)

1. **`--elo` (arg required) nao e persistido em coluna propria de `questoes_erros`** -- descoberto na verificacao: o INSERT grava habilidades/faltou/armadilha, e o elo era passado e IGNORADO. O matcher F25 agora e o primeiro consumidor real do arg. Candidato a achado de ledger (persistir o elo ou documentar que ele vive nos cards).
2. pytest emite 8 warnings pre-existentes (DeprecationWarning do adapter datetime do sqlite3 no Python 3.12, vindo de `INSERT INTO fsrs_cards ... datetime.now()` -- comportamento antigo do pipeline, fora do escopo desta part). Candidato a polimento futuro.

**Ready to ship.** Proximo: part-4 (errors-file + status anulada), que consome o matcher por item do lote.
