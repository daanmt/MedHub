# Spec: medhub Fase 0 · Lote 0 — Part 2a: fixture sintético, runtime isolado nos testes e os 4 verdes decorativos

> Gerada: 2026-10-10 | PRD: `.vibeflow/prds/medhub-fase0-preparar-ambiente.md` (ai-eng) | Evidência: `brain/observed-systems/medhub-reforma-2026-10-10/E-testes-harness.md` §Acoplamento a dado vivo (P7), §Suíte
> Parte 2a (de 7) — **fundacional para 2b e 2c**: cria o fixture `db_sintetico`, o marcador `vivo` e a convenção de skip `VIVO:` que elas reusam.
> Repo-alvo: medhub (implement + audit no loop vibeflow dele). Código conferido em leitura @ `6d0239a`.

## Objective

A suíte passa a ter um banco sintético compartilhado e a nunca escrever o runtime real do harness, e os 4 testes que hoje passam sem medir quando falta o `ipub.db` passam a pular com motivo declarado — cada um com um gêmeo hermético que prova que o sensor morde.

## Context

- **Verdes decorativos** (confirmados no código): `tools/test_comprimento_total.py:200-219` e `tools/test_cards_rendimento.py:101-114` fazem `print("[SKIP] ...")` + `return` quando o banco falta ou está vazio; `tools/test_deixis_sem_contexto.py:125-140` faz `if not os.path.exists(dbp): return`; `tools/test_erros_orfaos.py:167-183` passa sem medir porque `check_erros_orfaos()` devolve `None` sem banco (`tools/utils/state_utils.py:276-290`). Num checkout sem `ipub.db` (CI da Fase 1), os quatro saem PASSED sem ter medido nada.
- **Efeito colateral escondido:** `test_comprimento_total` chama `db.cards_ativos_para_predicado()` com o `DB_PATH` real dentro de `try/except`. Se o arquivo não existe, `sqlite3.connect` cria um `ipub.db` vazio na raiz antes de a consulta falhar.
- **Isolamento parcial:** o `conftest.py` raiz já isola por `autouse` `event_log.LOG_PATH`, `manager._HISTORY_DIR` e `manager._ERROR_LOG` ("Escrita nova em caminho global entra aqui"), mas não `ledger_self` nem `state_utils.WATERMARK_PATH`. Teste que exercita `auto_check`/`ledger_self.record` sem `root=` grava em `history/` real (depois da part-1 fora do git, mas ainda é o runtime do operador).
- **Fixture que já existe, espalhado:** 42 arquivos fazem `monkeypatch` de `db.DB_PATH`; o padrão com schema canônico é `tools/test_fuso_unico_leitores.py:48-62` (`init_db.DB_PATH` → `tmp_path`, `init_db.init_db()`, `db.DB_PATH` → tmp, seed por SQL). Não há fixture compartilhado.

**Que fricção esta spec remove — e ela é virtuosa ou viciosa?** Viciosa: verde que não mediu e teste que suja o runtime real. Nenhuma fricção virtuosa é tocada.

## Definition of Done

1. [ ] **Fixture compartilhado.** `conftest.py` expõe o fixture `db_sintetico` (schema de `tools/init_db.py` em `tmp_path`, `db.DB_PATH` e `init_db.DB_PATH` apontados para ele, seed mínimo de 1 linha em `taxonomia_cronograma`, devolve o caminho). `tools/test_harness_hermetico.py::test_db_sintetico_tem_schema_canonico` prova que as tabelas de `init_db` existem e que `db.DB_PATH` aponta para `tmp_path`.
2. [ ] **Runtime real intocado pela suíte.** O `autouse` do `conftest.py` também isola `ledger_self.ROOT_DIR` (nos dois nomes de módulo, `ledger_self` e `tools.ledger_self`, quando importados) e `state_utils.WATERMARK_PATH`. `test_suite_nao_escreve_runtime_real`: dentro de um teste, `ledger_self._paths()` e `state_utils.WATERMARK_PATH` estão sob `tmp_path`, e `ledger_self.record("x", [{"alvo": "a"}])` cria o `.jsonl` em `tmp_path`.
3. [ ] **Marcador `vivo`.** Registrado no `conftest.py` (`pytest_configure` → `config.addinivalue_line("markers", "vivo: ...")`, sem editar o `pytest.ini`). `python -m pytest tools/ -q -m "not vivo"` passa.
4. [ ] **Os 4 pulam com motivo.** As 4 funções acima ganham `@pytest.mark.vivo`, testam a existência do banco **antes** de abrir conexão (nenhum `ipub.db` vazio criado) e, sem ele, chamam `pytest.skip("VIVO: ipub.db ausente -- <o que deixou de ser medido>")`. Nenhum `return` silencioso sobra nelas. `test_vivos_pulam_com_motivo_sem_banco` (em `test_harness_hermetico.py`): para cada uma, com o caminho do banco real monkeypatchado para um arquivo inexistente em `tmp_path`, a chamada levanta `pytest.skip.Exception` com `VIVO` na mensagem, e o arquivo não passa a existir.
5. [ ] **Gêmeo hermético.** Para cada um dos 4 sensores existe ≥ 1 teste não-`vivo` que planta o defeito no `db_sintetico` (ou em fixture sintético equivalente) e vê o sensor acusar. Se já existir, o audit cita o nome; se não, ele é escrito no arquivo do sensor. `python -m pytest tools/ -q -m vivo` coleta as 4 funções e passa na máquina do operador.
6. [ ] **Suíte verde e craftsmanship:** `python -m pytest tools/ -q` passa; nenhuma violação dos Don'ts de `.vibeflow/conventions.md`; os docstrings dos 4 dizem "pula com motivo sem banco" (não "pula" quando retornava); o docstring do `conftest.py` lista os globais isolados.

## Scope

- `conftest.py`: fixture `db_sintetico`; `autouse` estendido (ledger/watermark); registro do marcador `vivo`.
- `tools/test_harness_hermetico.py` (criado na part-1): + os 3 testes nomeados nos DoD 1, 2 e 4.
- `tools/test_comprimento_total.py`, `tools/test_cards_rendimento.py`, `tools/test_deixis_sem_contexto.py`, `tools/test_erros_orfaos.py`: marcador, guarda de existência, skip com motivo, gêmeo hermético se faltar. Para viabilizar o DoD 4, cada um expõe o caminho do banco real numa constante de módulo (ex.: `REAL_DB = ROOT / "ipub.db"`).

**Budget: 6 arquivos.**

## Anti-scope

- **Fronteiras:** design no ai-eng, implementação no medhub; nenhum escreve no repo do outro.
- **Nada que mude conteúdo clínico, FSRS ou o hub publicado.** Os predicados (`card_checks.checar_*`, `cards_rendimento.medir`, `check_erros_orfaos`) não mudam — só os testes.
- Não mudar números de corte nem a janela d..d+1 do F38 (`CONHECIDOS` em `test_erros_orfaos` fica como está; a churn dele é decisão de sensor, não de harness).
- Não migrar os 42 arquivos que já fazem `monkeypatch` de `db.DB_PATH` para o fixture novo.
- Não editar `pytest.ini` (o marcador vai pelo `conftest.py`); não adicionar `addopts` que tire `vivo` do default (a suíte do selo continua a mesma; a lane hermética é `-m "not vivo"`, e quem a adota como default é a Fase 1/CI).
- Os demais acoplados → part-2b e part-2c.

## Technical Decisions

1. **Marcador + skip com prefixo `VIVO:`** em vez de mover os testes para fora da suíte. A suíte do operador continua medindo o dado vivo (o valor de sensor fica), e a CI da Fase 1 ganha uma lane hermética por `-m "not vivo"` sem reescrita. Custo: dois modos para lembrar; mitigação: o motivo do skip nomeia o que não foi medido.
2. **Marcador registrado no `conftest.py`**, não no `pytest.ini`, para caber no budget e evitar `PytestUnknownMarkWarning` sem tocar a allowlist.
3. **Guarda antes da conexão:** `if not REAL_DB.is_file(): pytest.skip(...)` antes de qualquer `connect`, porque `sqlite3.connect` cria arquivo vazio.
4. **`ledger_self` tem dois nomes de módulo** (`state_utils` faz `sys.path.insert(tools)` + `from ledger_self import record`; testes importam `tools.ledger_self`). O isolamento patcha os dois quando presentes em `sys.modules` (mesma técnica do `conftest` para `event_log`).

## Applicable Patterns

- `conftest.py` existente (`_event_log_isolado`): `try/except` por global, comentário com o incidente que motivou cada isolamento.
- `tools/test_fuso_unico_leitores.py:48-62`: banco canônico via `init_db` em `tmp_path` + seed por SQL.
- Convenção de hotfix do medhub: `reproduction: synthetic` é a regra; suíte que escreve no banco de produção é defeito (F49/F96).
- `.vibeflow/patterns/warn-first-check.md` item 3: "sem dados → silêncio" vale para sensor; para **teste**, a regra é skip declarado.

## Risks

- **"O skip esconde regressão real."** → O motivo do skip diz o que não foi medido; `-m vivo` continua rodando na máquina do operador; o gêmeo hermético roda em qualquer lugar.
- **"O fixture autouse quebra teste que dependia do ledger real."** → Nenhum teste deveria depender; se algum quebrar, é achado (teste acoplado ao runtime) e o audit lista.
- **"`init_db` muda e o fixture diverge."** → O fixture chama `init_db.init_db()`, não copia DDL.
- **"Dois agentes no mesmo `conftest.py`."** → `AGENTE.md §10.1`: reler antes de editar.

## Dependencies

- `.vibeflow/specs/medhub-fase0-lote0-harness-hermetico-part-1.md` (cria `tools/test_harness_hermetico.py` e o gatilho que faz estes commits rodarem a suíte).
