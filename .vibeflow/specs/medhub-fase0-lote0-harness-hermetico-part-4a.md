# Spec: medhub Fase 0 · Lote 0 — Part 4a: código morto sai, com alcançabilidade medida

> Gerada: 2026-10-10 | PRD: `.vibeflow/prds/medhub-fase0-preparar-ambiente.md` (ai-eng) | Evidência: `brain/observed-systems/medhub-reforma-2026-10-10/A-identidade-codigo.md` §Tabela de módulos, §Funções mortas, §Morre ou é arquivado
> Parte 4a (de 7). Depois da part-2a (fixture para o teste de schema); na ordem do PRD, depois da part-3.
> Repo-alvo: medhub (implement + audit no loop vibeflow dele). Código conferido em leitura @ `6d0239a`.

## Objective

O código sem chamador e sem norma que o proteja sai do repo, a escrita em tabela inexistente deixa de ser engolida em silêncio, e o instrumento que mede alcançabilidade para de gravar enquanto mede.

## Context

Conferido no código e por `git grep` (2026-10-10):

- **Arquivos sem nenhuma referência:** `core/simulados/micro_temas.py`, `core/simulados/verbo_e.py` (`git grep -w` → 0) e `.streamlit/config.toml` (`git grep -F ".streamlit"` fora de `history/`/`.vibeflow/` → 0; o Streamlit saiu em `47aad80`, 14/08).
- **Cauda morta do `app/utils/db.py`:** 10 funções cuja única ocorrência no repo (fora de `history/`, `.vibeflow/`, `docs/`, `AUDITORIA_MEDHUB.md`) é a própria definição: `get_db_metrics` (`:294`), `get_cronograma` (`:376`), `update_cronograma_status` (`:383`), `get_due_cards_count` (`:391`), `get_caderno_detalhado` (`:445`), `get_erros_resumidos` (`:1004`), `get_bulk_totals_por_area` (`:1048`), `get_erros_por_area` (`:1100`), `registrar_habilidade` (`:1791`), `get_serie_blocos` (`:1830`). `get_semana_conteudo` e `tarefas_com_questoes` são citadas só por testes e **ficam**.
- **Tabela inexistente:** `cronograma_progresso` não existe no `ipub.db` (consulta read-only a `sqlite_master`, 2026-10-10) nem no `tools/init_db.py`. `db.py:379` lê e `db.py:387` escreve nela; `tools/insert_questao.py:413-420` faz `UPDATE cronograma_progresso ...` dentro de `try/except Exception: pass  # tabela opcional — ignorar se não existir`.
- **O instrumento grava:** `tools/reachability_check.py` diz no docstring que "não escreve nada no repo", mas em modo texto chama `ledger_self.record(LEDGER_TAG, achados)` (`:286-290`, `LEDGER_TAG = "reachability"` em `:87`; o próprio CONFIG diz "None desliga o registro"). O `auto_check --all` já registra a mesma tag pelo seu próprio `_ledger_record("reachability", ...)` (`auto_check.py:958`).
- **Divergências com [A], ajustadas aqui:** "19 MORTOS + `tools/_archive` (13)" conta o `_archive` duas vezes (são 6 módulos na árvore + 13 migrações). Dos 6: `tools/calibrate_card_checks.py` e `tools/audit_fsrs.py` estão em `ISENTOS` do `reachability_check.py:75-78` como ferramenta de mão por norma; `tools/backfill_review_log.py` é citado em `core/contracts/forgetting-curve-contract.md`, `AGENTE.md` e `engenharia-cli.md`; `tools/eval/run_eval.py` sustenta o "Baseline reproducible em `tools/eval/REPORT.md`" de `AGENTE.md §6`. E `tools/_archive/migrations/` é prescrito por `.agents/workflows/curar-cards.md:62` ("movem para `tools/_archive/migrations/` após aplicadas"), o que contradiz `AGENTE.md §3.4` ("sem `archive/`"). Todos esses saem só por decisão de contrato (Lote 3) — fora desta parte.

**Que fricção esta spec remove — e ela é virtuosa ou viciosa?** Viciosa: ler e manter código que ninguém chama, e uma escrita que falha calada. Nenhuma fricção virtuosa é tocada.

## Definition of Done

1. [ ] **Alcançabilidade antes e depois.** `python tools/reachability_check.py --json` rodado antes da primeira remoção e depois da última; as duas saídas ficam no scratch da sessão e o audit cita as contagens; o conjunto de órfãos depois ⊆ antes (nada novo ficou órfão). Limite declarado: `core/` não é alvo do sensor (`ALVOS = tools/*.py, app/**/*.py`), então as remoções de `core/simulados/` não mexem na contagem.
2. [ ] **Instrumento read-only.** `LEDGER_TAG = None` em `tools/reachability_check.py`; `tools/test_reachability.py::test_modo_texto_nao_grava_ledger` roda `RC.main()` em modo texto sobre o repo sintético do arquivo com `ledger_self.record` substituído por uma função que falha se chamada, e o retorno é 0. O docstring ("não escreve nada no repo") passa a ser verdade.
3. [ ] **Remoções com raio conferido** (`AGENTE.md §10.4`): para cada item, `git grep -n -F <nome>` no repo inteiro antes de remover, saída colada no audit; removidos `core/simulados/micro_temas.py`, `core/simulados/verbo_e.py`, `.streamlit/config.toml` e as 10 funções do `db.py` listadas acima.
4. [ ] **Escrita em tabela inexistente é teste.** Novo `tools/test_schema_escrita.py::test_toda_tabela_escrita_existe_no_schema`, escrito e visto VERMELHO antes do fix (acusa `cronograma_progresso`): todo nome de tabela depois de `INSERT [OR …] INTO`, `UPDATE` e `DELETE FROM` em literais de string de `app/**/*.py` e `tools/*.py` (sem `test_*` e sem `_archive`) existe no schema do `init_db.init_db()` em `tmp_path` **ou** tem `CREATE TABLE IF NOT EXISTS` nas mesmas fontes (DDL lazy, ex. `plano_dia`). Nomes com `{`/`%` (dinâmicos) ficam de fora — limite declarado no docstring.
5. [ ] **O bloco engolido sai:** `tools/insert_questao.py:413-420` (o `try/except: pass` sobre `cronograma_progresso`) é removido; o teste do DoD 4 fica verde.
6. [ ] **Suíte e FSRS verdes:** `python -m pytest tools/ -q` passa; como o commit toca `app/utils/db.py`, o pre-commit roda também `test_fsrs_balance.py` (check 2, BLOCK) — verde.
7. [ ] **Craftsmanship:** nenhuma violação dos Don'ts de `.vibeflow/conventions.md` (em `app/`, `sqlite3` continua só no `db.py`); `test_schema_escrita.py` entra no `python_files` do `pytest.ini` com parágrafo; nenhuma função viva do `db.py` muda de comportamento.

## Scope

Editados/criados: `tools/reachability_check.py`, `tools/test_reachability.py`, `app/utils/db.py` (só remoções), `tools/insert_questao.py` (só o bloco `:413-420`), `tools/test_schema_escrita.py` (novo), `pytest.ini`. **Budget: 6 arquivos + 3 deleções de arquivo** sem referenciador (listadas no DoD 3).

## Anti-scope

- **Fronteiras:** design no ai-eng, implementação no medhub.
- **Nada que mude conteúdo clínico, FSRS ou o hub publicado.** No `db.py` só saem as 10 funções sem referência; nada em `record_review`, `get_cards_by_bucket`, `carga_agendada` ou writers.
- Não remover `tools/calibrate_card_checks.py`, `tools/audit_fsrs.py`, `tools/backfill_review_log.py`, `tools/eval/`, `tools/_archive/` nem os `?` de [A] (`listas`, `preparacao`, `emed_flashcards`, RAG, memória) — Lote 3 (contratos) ou Lote 5 (RAG).
- Não mexer em `requirements.txt` (deps mortas e PyMuPDF não declarado) — Lote 3/Fase 1.
- Não tocar `README.md` (descreve o sistema de agosto; reescrita é Lote 3).
- Não regenerar a tabela do `AGENTE.md §7.4`.

## Technical Decisions

1. **Remover só o que não tem norma por cima.** Módulo citado em contrato, skill ou `ISENTOS` sai só depois que a norma muda (3 passos de revogação, `AGENTE.md §10.10`), e isso é Lote 3. O preço é deixar ~2,2k linhas para depois; o ganho é não abrir revogação de cláusula dentro de uma parte de housekeeping.
2. **Teste de schema por regex sobre as fontes** em vez de rodar cada writer: barato e pega a classe inteira (escrita em tabela que não existe), não só o caso. Limite declarado: SQL montado dinamicamente.
3. **`LEDGER_TAG = None`** em vez de remover o bloco: usa o interruptor que o CONFIG já documenta, e o registro continua pelo `auto_check --all`.

## Applicable Patterns

- `tools/test_reachability.py:21-75` (`_repo`): repo sintético em tmp para o sensor; `test_warn_first_exit_zero` (`:153-163`) mostra como trocar `RC.ROOT_DIR` e `sys.argv`.
- Fixture `db_sintetico` da part-2a, ou `init_db` em `tmp_path` como em `tools/test_fuso_unico_leitores.py:48-62`.
- `tools/test_plano_dia.py::test_calendario_e_snapshot_do_drive_sairam_do_codigo`: teste-lápide de código removido (modelo, se o implementador quiser travar a volta das funções).
- `AGENTE.md §10.4`: deletar é ato com raio — `grep` no repo e nos portadores de regra antes.

## Risks

- **"Uma função 'morta' era chamada por string ou por `python -c` numa skill."** → DoD 3: `git grep` sobre o repo inteiro (inclui `.claude/commands` e `.agents/`) antes de remover; o audit cola a saída.
- **"O teste de schema acusa falso positivo."** → Nome dinâmico fica de fora; DDL lazy conta; se aparecer outro caso legítimo, o audit lista e a lista de exceções nasce declarada (vazia hoje).
- **"`db.py` é o arquivo mais mexido (52 commits desde 01/07) e o tique commita em paralelo."** → `AGENTE.md §10.1`: reler antes de editar; só remoções.

## Dependencies

- `.vibeflow/specs/medhub-fase0-lote0-harness-hermetico-part-2a.md` (fixture de banco sintético).
