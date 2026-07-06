# Audit Report: pipeline-conhecimento-part-1 (Cobertura / F16a)

**Verdict: PASS**

> Auditado 2026-07-06. Spec: `.vibeflow/specs/pipeline-conhecimento-part-1.md`.
> Tests: 41 passed (era 36; +5 de test_cobertura). Critical Gate: limpo.

### DoD Checklist
- [x] **1 — Totais + lista de orfaos ordenada + semana destacada.**
  `tools/cobertura_conhecimento.py` (`main`/`render`/`priorizar`). Execucao real:
  `PDFs 333, .md 61, Cobertos 35 (31 exato/4 fuzzy), Orfaos 298`; restantes ordenados por
  volume (Trauma Abdominal e Pelvico vol=352 no topo). Numeros batem com o censo real
  (333 PDFs; 62 .md - 1 INDEX.md = 61 SSOT).
- [x] **2 — Match tolerante + fuzzy.** `normaliza_stem` remove prefixo numerico EMED, acento
  (NFKD), case e pontuacao; `parear` usa exato + `SequenceMatcher` (COBERTO>=0.90,
  REVISAR>=0.75). Testes `test_par_divergente_reconhecido` (PDF "12 - Apendicite Aguda" x
  .md "Apendicite Aguda" -> coberto) e `test_nao_par_mantido_orfao` (Meckel sem par -> orfao).
- [x] **3 — Semana corrente sem .md destacada.** `render` emite secao propria
  "Temas da SEMANA CORRENTE (S12)". Semana alvo = posicao SSOT de conteudo
  (`db.get_semana_conteudo`, S12) com fallback ao calendario (`cronograma.semana_corrente`) --
  alinhado a "reusa cronograma.py/preparacao_estado (posicao SSOT)" da spec.
- [x] **4 — Teste dos 3 casos, pytest verde.** `tools/test_cobertura.py`: normalizacao,
  par divergente, nao-par, ordenacao por rendimento, read de taxonomia em db temp.
  `pytest tools/test_cobertura.py` = 5 passed.
- [x] **5 — Craftsmanship.** CLI sem `import sqlite3` (le via `db.get_taxonomia_rendimento`);
  argparse + `--dir` default `resumos` + `sys.path.insert` + exit 0/1 (padrao de `tools/`);
  so stdlib (unicodedata/difflib/re); ASCII limpo (verificado por grep de nao-ASCII;
  a fixture acentuada usa `chr(0x00e1)` para manter o fonte ASCII).
- [x] **6 — Read-only.** CLI apenas varre nomes (`rglob`) e imprime; nenhum create/move/delete.
  A funcao nova em `db.py` e um `SELECT` puro.

### Pattern Compliance
- [x] **db-access-layer** — `get_taxonomia_rendimento` segue `get_connection()` -> `pd.read_sql`
  -> `conn.close()` (`app/utils/db.py`); query parametrizada nao aplicavel (sem input externo);
  CLI nao usa sqlite3, consome a funcao. Confinamento respeitado.
- [x] **CLI tools (conventions.md)** — argparse, exit codes, saida legivel, default `--dir`.
  DB path via `os.path.dirname` nao se aplica (CLI nao abre DB direto -- delega a `db.py`).
- [x] **Reuso cronograma.py** — usa `load_grade`/`get_semana`/`semana_corrente` + posicao SSOT;
  nao reimplementa deteccao de semana.

### Convention Violations
Nenhuma.

### Critical Gate
Clean — no destructive operations detected.
- `app/utils/db.py` +17: adicao de `SELECT` read-only (nenhum DROP/DELETE/TRUNCATE/ALTER).
- `pytest.ini` +1/-1: allowlist de teste.
- `tools/cobertura_conhecimento.py`, `tools/test_cobertura.py`: sem exec dinamico, sem
  mass-delete, sem secret hardcoded. `CREATE TABLE`/`INSERT` do teste sao em db temporario.

### Budget
4 / <=6 arquivos: cria `cobertura_conhecimento.py`, `test_cobertura.py`; modifica `db.py`
(+1 funcao read-only), `pytest.ini` (+1 entrada na allowlist).

### Anti-scope
Respeitado: sem autoria de `.md`, sem WARN no `auto_check`, sem indexar PDF (Parte 2),
sem coluna nova de schema, sem deletar/mover arquivo.

### Nota de decisao (registrada)
Semana alvo do relatorio = **posicao SSOT de conteudo** (S12, `get_semana_conteudo`), nao o
calendario (S15, `semana_corrente`). A spec nomeia "preparacao_estado (posicao SSOT do ciclo
2)" nas Decisoes tecnicas; usar o calendario destacaria temas ~3 semanas a frente de onde o
operador esta. Fallback ao calendario preservado quando a posicao SSOT nao esta registrada.
