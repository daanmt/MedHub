# Audit Report: pipeline-conhecimento-part-4 (Residuos / F27 + F28)

**Verdict: PASS**

> Auditado 2026-07-06. Spec: `.vibeflow/specs/pipeline-conhecimento-part-4.md`.
> Tests: 50 passed (+2 de exit-code em test_batch_insert). Paridade command<->skill: OK.
> auto_check --staged: PASSED. Critical Gate: limpo.

### DoD Checklist
- [x] **1 — F27 exit code simetrico.** `tools/insert_questao.py` (modo single) agora faz
  `ok = insert_questao(...)` + `sys.exit(0 if ok else 1)` (linha ~387/409), simetrico ao modo
  `--errors-file` (linha 374). Falha (`insert_questao` -> False no caminho own_conn) -> exit 1;
  sucesso -> exit 0.
- [x] **2 — Sem regressao de chamadores.** Grep de invocacoes (`.claude/`, `.agents/`, `tools/`,
  `AGENTE.md`) mostra que todas sao `python tools/insert_questao.py ...` agent-driven em docs;
  nenhum hook/script le `$?` nem depende do exit 0 em falha. `auto_check --staged` = PASSED.
- [x] **3 — Teste do exit code single.** `test_single_exit_ok` (entrada valida -> returncode 0)
  e `test_single_exit_fail` (`--cards-file` invalido -> insert_questao False -> returncode 1),
  ambos via `subprocess` em sandbox hermetico (`_sandbox_cli`: copia do script standalone +
  `ipub.db` temp; db real nunca tocado). `test_batch_insert` = 8 passed.
- [x] **4 — F28 doc.** `.claude/commands/analisar-questao.md` (secao 9) ganha tabela
  arg -> coluna deixando explicito: `--faltou` -> `o_que_faltou` (coluna CANONICA do elo),
  `--habilidades` -> `habilidades_sequenciais`, `--erro` -> `tipo_erro`, e `--elo` -> NENHUMA
  coluna (alimenta so o matcher F25 `checar_reincidencia`). Nota "nao criar coluna `elo`".
  Espelho `.agents/skills/source-command-analisar-questao/SKILL.md` regenerado.
- [x] **5 — Craftsmanship + paridade.** Nenhum schema alterado; `sync_skills --check` = OK;
  a mudanca F27 nao altera o comportamento de sucesso nem a saida legivel (so acrescenta o
  `sys.exit`); `import sqlite3` de insert_questao permanece exceção autorizada (CLI standalone).

### Pattern Compliance
- [x] **error-insertion-pipeline** — o contrato de exit code do CLI passa a ser consistente
  (single == batch); pipeline insert_questao + flashcards inalterado.
- [x] **CLI tools (conventions.md)** — retorno bool -> exit code; sucesso 0 / falha 1.
- [x] **sync_skills (paridade)** — command canonico editado + espelho regenerado e verificado.

### Convention Violations
Nenhuma.

### Critical Gate
Clean — no destructive operations detected.
- `tools/insert_questao.py`: adiciona `ok =` + `sys.exit(0 if ok else 1)`. Sem DROP/DELETE/
  TRUNCATE novos; o `ALTER TABLE ... ADD COLUMN status` e PRE-EXISTENTE (ADD, nao DROP).
- `tools/test_batch_insert.py`: `subprocess` + `shutil.rmtree(<tempdir>)` escopado ao sandbox;
  `CREATE TABLE` do `_db_temp` e pre-existente. Nenhum keyword de mass-delete.
- `analisar-questao.md`, `SKILL.md`: documentacao.

### Budget
4 / <=6 arquivos: modifica `insert_questao.py` (exit code), `test_batch_insert.py` (+2 testes),
`analisar-questao.md` (doc F28); regenera `SKILL.md`.

### Anti-scope
Respeitado: sem coluna nova (F28 = documentacao; `status` segue a unica mudanca de schema do
ciclo 2); `--elo` permanece (consumido pelo matcher F25); `insert_questao`/`insert_batch` nao
refatorados (so o exit code do single mudou); comportamento de sucesso e saida legivel intactos.
