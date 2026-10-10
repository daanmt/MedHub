# Spec: medhub Fase 0 · Lote 0 — Part 1: hooks e pre-commit não escrevem nem pulam

> Gerada: 2026-10-10 | PRD: `.vibeflow/prds/medhub-fase0-preparar-ambiente.md` (ai-eng) | Evidência: `brain/observed-systems/medhub-reforma-2026-10-10/E-testes-harness.md` §Harness (a)(b), `D1-git-housekeeping.md` §Estado agora
> Parte 1 (de 7) — **keystone**: todas as partes seguintes commitam sob o gatilho e a árvore limpa criados aqui.
> Repo-alvo: medhub (implement + audit no loop vibeflow dele, `AGENTE.md §10.6`). Prompt-pack: `.vibeflow/prompt-packs/medhub-fase0-lote0-harness-hermetico-part-1.md`.
> Código conferido em leitura no medhub @ `6d0239a` (2026-10-10).

## Objective

O boot deixa de regravar o plano do dia já gravado, o pre-commit roda a suíte em todo commit que toca código, dado versionado ou norma (e nunca pula os checks "sempre"), e nenhum arquivo que o harness escreve fica rastreado pelo git.

## Context

**1. Boot escreve no banco vivo.** `tools/hooks/memory_boot.py:72-76` roda `[sys.executable, "tools/day_plan.py"]` sem `--no-persist`. Sem a flag, `tools/day_plan.py:1625-1626` chama `persistir_plano`, que faz `DELETE FROM plano_dia WHERE data = ?` + `INSERT` (`:1309`, `:1313`). Cada abertura de sessão — inclusive depois de `/clear` e em cada sessão do tique — regrava o plano do dia com os defaults, e o próprio `day_plan.py:1620-1624` documenta que regravar com defaults "sobrescreveria a intenção declarada de manhã (`--tempo/--energia`)". A constante `_CMD_DAY_PLAN` (`memory_boot.py:32`) tem `--no-persist`, mas só como texto de dica.

**Divergência com o pedido literal ("`--no-persist` no boot"):** a `telemetria-estudo-part-1` do medhub (`.vibeflow/specs/telemetria-estudo-part-1.md`, DoD 2-3) fez "persistir" o default justamente para gravar o PLANEJADO do dia, que `aderencia()` (`day_plan.py:1509`) cruza com o realizado. O boot é o único writer automático, e as convenções proíbem rodar `day_plan.py` à mão no boot. `--no-persist` em toda abertura mataria a série em silêncio. Decisão: **o boot grava só quando o dia ainda não tem plano**; as aberturas seguintes passam `--no-persist`. Ver Q1 do PRD.

**2. O gate pula.** `tools/auto_check.py:567-571` só classifica `resumos/**.md` e `.py` em `tools/`/`core/`. O check 4 (suíte completa, `:644`) dispara com `tools_to_check or substrato_relevant or fsrs_relevant or selo_relevant`. Se nenhuma flag acende, `:580-589` imprime "Nenhum arquivo crítico... Aprovado!" e faz `return 0` **antes** dos checks que o código chama de "Roda SEMPRE" (`:984` em diante: F38, F89, IMPORT_DANGLING, HISTORY_INTEGRITY, CONTRATO_REVOGADO, SUITES_ORFAS, CLI_ASSINATURA — BLOCK, `:1146-1180` —, consistência, TERMO, cláusulas — BLOCK parcial, `:1228-1268`). Caso real (s216): commit só com `core/hub_quadro.json` + `artifacts/aula-*.html` passou sem `test_hub_quadro`; as 2 falhas apareceram no commit seguinte. Além disso, `tools/utils/git_utils.py:41-50` (`get_staged_files`) usa `--diff-filter=ACMR`: um commit que só **deleta** `tools/x.py` não acende nada — e a part-4a deleta módulos.

**3. O harness suja a árvore no commit.** O `auto_check` chama `_ledger_record(...)` em 23 pontos (ex.: `:687`, `:1003`, `:1173`), que acaba em `tools/ledger_self.py:65-68` (`_append_event`, modo `"a"`) sobre `history/ledger_self.jsonl` — rastreado. `card_watermark_selar` (`auto_check.py:913`; `tools/utils/state_utils.py:66-75`) grava `history/card_watermark.json` — rastreado. Escrito depois do stage, nada disso entra no commit: a árvore fica suja depois de todo commit (D1: `d48de82` "logs append-only que o 89ddd41 não levou"; `ledger_self.jsonl` tocado em 87 commits). O estado derivado `history/ledger_self_state.json` já é ignorado (`.gitignore:63-64`). Quem lê o `.jsonl`: só `validar_jsonl` (`ledger_self.py:197-212`), do disco; `abertos()`/`painel_divida()` leem o state. Ninguém lê o ledger pelo git.

**Que fricção esta spec remove — e ela é virtuosa ou viciosa?** Remove fricção **viciosa** (automatizar): o boot que apaga a intenção declarada do dia, o commit que sai "Aprovado!" sem suíte e o resíduo de log que suja a árvore a cada commit. Nenhuma fricção virtuosa (recall, nota honesta, triagem humana de card) é tocada.

## Definition of Done

Testes 1–4 vivem no arquivo novo `tools/test_harness_hermetico.py`, escritos **antes** do fix e vistos vermelhos (`AGENTE.md §10.6`).

1. [ ] **Boot grava no máximo uma vez por dia.** `test_boot_nao_regrava_plano_do_dia`: com um `ipub.db` sintético em `tmp_path` cuja `plano_dia` tem linha de `date.today().isoformat()`, o argv que o hook passa ao `subprocess.run` do day_plan contém `--no-persist`; sem linha de hoje, não contém; com banco ausente ou sem a tabela, contém (dúvida = não gravar).
2. [ ] **Gatilho por prefixo, não por extensão.** `test_gatilho_da_suite_por_prefixo` sobre a função pura nova `auto_check.dispara_suite_por_caminho(arquivos)`: `True` para `core/hub_quadro.json`, `core/templates/hub.html`, `artifacts/aula-rd-x.html`, `app/utils/areas.py`, `.claude/commands/revisar.md`, `.agents/workflows/curar-cards.md`, `tools/x.py`, `pytest.ini`, `conftest.py`, `requirements.txt`; `False` para `history/session_223.md`, `.vibeflow/specs/x.md`, `docs/x.md`, `resumos/GO/X.md`, `ROADMAP.md` e `[]`.
3. [ ] **O `main()` usa o gatilho, conta deleções e nunca pula os "sempre".** `test_staged_core_json_roda_a_suite` (in-process; `run_command`, `get_staged_files`, o leitor de deleções staged, `_ledger_record` e `card_watermark_*` monkeypatchados no módulo `auto_check`): staged = `["core/hub_quadro.json"]` → `run_command` recebe `[sys.executable, "-m", "pytest", "tools/", "-q"]`; só a deleção staged de `tools/x.py` → idem; staged = `["docs/x.md"]` → a suíte **não** roda, a saída não contém `Nenhum arquivo crítico` e o relatório final lista `Assinatura canonica de CLI (D5)` e `Clausula normativa com terminal (1.10)`.
4. [ ] **Runtime do harness fora do git.** `test_runtime_do_harness_fora_do_git`: para os dois caminhos de `ledger_self._paths()` e para `state_utils.WATERMARK_PATH`, `git ls-files --error-unmatch -- <p>` sai ≠ 0 **e** `git check-ignore -q -- <p>` sai 0 (mesmo padrão de `tools/test_emed_api.py:400-402`). `history/ledger_self.jsonl` e `history/card_watermark.json` saem do índice com `git rm --cached` (o conteúdo fica no disco).
5. [ ] **Verificação contra o artefato real** (read-only, colada no audit): (a) logo depois do commit desta parte, `git status --porcelain` não lista `history/ledger_self.jsonl` nem `history/card_watermark.json`; (b) num dia que já tem plano, `SELECT COUNT(*), MAX(criado_em) FROM plano_dia WHERE data = date('now','localtime')` (conexão `mode=ro`) devolve o mesmo par antes e depois de `python tools/hooks/memory_boot.py`.
6. [ ] **Suíte completa verde:** `python -m pytest tools/ -q` passa; o número (1509 + os novos) é o que o pre-commit mede no commit do selo (F136), nunca digitado.
7. [ ] **Craftsmanship:** nenhuma violação dos Don'ts de `.vibeflow/conventions.md`; `test_harness_hermetico.py` entra no `python_files` do `pytest.ini` com parágrafo de justificativa no formato dos vizinhos; todo texto que descrevia o mecanismo antigo passa a dizer a verdade (`ledger_self.py:5-9` "versionado" → local; `.gitignore:63`; o comentário do gatilho do check 4 em `auto_check.py:636-643`; o "Roda SEMPRE" passa a ser verdade); o limite do teste 4 está declarado no docstring ("prova os 3 caminhos conhecidos; não prova que não exista um 4º escritor — o DoD 5a cobre isso empiricamente").

## Scope

- `tools/hooks/memory_boot.py`: helper `_plano_de_hoje_existe(db_path=None) -> bool` (sqlite `mode=ro` via URI, mesmo padrão de `state_utils.card_watermark_atual`) e montagem do argv do day_plan (`--no-persist` quando já há plano de hoje ou quando a consulta falha). O resto do hook não muda.
- `tools/auto_check.py`: (i) função pura `dispara_suite_por_caminho(arquivos)` ao lado de `dispara_suite_por_selo` (`:381`); (ii) leitor das deleções staged (`--diff-filter=D`, reaproveitando `git_utils._git_files`), cujas entradas entram só no gatilho da suíte, não na classificação de arquivos a auditar; (iii) condição do check 4 = condição atual **ou** `dispara_suite_por_caminho(staged + deletados)`; (iv) o early-return vira uma linha verdadeira ("suíte não exigida para este recorte") e o fluxo segue para os checks "sempre".
- `.gitignore`: + `history/ledger_self.jsonl` e `history/card_watermark.json`, comentário da linha 63 corrigido; `git rm --cached` dos dois, no mesmo commit.
- `tools/ledger_self.py`: só o docstring (linhas 5-9).
- `tools/test_harness_hermetico.py` (novo) e `pytest.ini` (allowlist + parágrafo).

**Budget: 6 arquivos editados/criados** (os 6 acima) **+ 2 des-rastreados** por `git rm --cached` (índice; o conteúdo não é editado).

## Anti-scope

- **Fronteiras:** esta spec decide o mecanismo; o código é do medhub. O implementador não escreve no ai-eng; o ai-eng não escreve no medhub.
- **Nada que mude conteúdo clínico, FSRS** (`app/utils/fsrs*.py`, `record_review`, `fsrs_revlog`) **ou o hub publicado** (`core/templates/*`, Artifact).
- `tools/day_plan.py` não muda (nem flag nova, nem `persistir_plano`): a decisão mora no hook.
- Severidade de check nenhum muda (BLOCK/WARN) — catraca e CLI check são a part-3.
- `tools/reachability_check.py` (grava no ledger em modo texto) → part-4a. Com o ledger fora do git, a escrita dele deixa de sujar a árvore.
- Isolamento do ledger/watermark **dentro** da suíte (conftest) → part-2a.
- Logs de sessão (`history/exchange-log.jsonl`, `history/generation_log.jsonl`) → Lote 4/Fase 1.
- `core.hooksPath`/hook versionado e CI → Fase 1.
- Reescrever o histórico do git; mexer em `selo.py`, `setup_hooks.py` ou no conteúdo do hook instalado.

## Technical Decisions

1. **Boot grava uma vez por dia** em vez de `--no-persist` sempre. Ganho: a série planejado × real continua viva e a intenção declarada (`day_plan.py --tempo/--energia`, rodado pelo agente quando o operador declara) não é mais sobrescrita por aberturas seguintes. Custo: o boot ainda escreve uma vez por dia no banco vivo (escrita de processo, sem conteúdo clínico). <!-- TODO(operador, Q1 do PRD): manter a gravacao do 1o boot do dia? default implementado = sim -->
2. **Dúvida = não gravar.** Banco ausente, tabela ausente ou erro na consulta → `--no-persist`. Um boot nunca escreve quando não consegue verificar.
3. **"Hoje" do hook = `date.today()`**, o mesmo de `day_plan.build()` (`day_plan.py:894`). Se o `build()` passar a usar o dia lógico (`app/utils/relogio.py`), o hook tem de acompanhar — comentário no helper apontando a linha.
4. **Gatilho por prefixo de diretório** (`tools/`, `app/`, `core/`, `artifacts/`, `.claude/`, `.agents/`) + arquivos de config (`pytest.ini`, `conftest.py`, `requirements.txt`), qualquer extensão, em vez de acrescentar extensões à lista. Custo: ~210 s de suíte nesses commits (o commit do tique já paga, porque toca `HANDOFF.md`). Limite declarado: commits só de `resumos/`, `docs/`, `.vibeflow/`, `history/` ou docs de raiz (fora `HANDOFF.md`) não rodam a suíte, embora `test_consistencia_registros` leia `.vibeflow/`/`docs/` e `test_audit_resumos`/`test_autonomia_hooks` leiam 5 resumos reais — esses só mordem no próximo commit que dispare a suíte. Fecha na Fase 1 (CI).
5. **Deleção conta para o gatilho.** O leitor de deletados alimenta só `dispara_suite_por_caminho`; a auditoria de arquivos (linter de resumos, `tools_to_check`) continua sobre ACMR, como hoje.
6. **Sem early-return.** Os checks "sempre" passam a rodar em todo commit (custo: segundos). A frase "Nenhum arquivo crítico... Aprovado!" sai, porque mentia sobre o que não tinha rodado.
7. **Runtime do harness fora do git** (des-rastrear) em vez de "não gravar no `--staged`". A alternativa deixaria o `.jsonl` rastreado e sujo pelas rodadas `--changed` do agente — a classe continuaria. Custo: a trilha **futura** do ledger deixa de ser versionada; a passada fica no histórico; cópia fora da máquina é o Lote 4.
8. **Como se testa o commit.** Rodar o hook real dentro da suíte recursa (o hook roda a suíte, que roda o teste, que commita). Por isso: `main()` in-process com `run_command` substituído (DoD 3) + invariante do git em subprocess (DoD 4) + verificação do commit real (DoD 5a). É um desvio declarado do pedido "teste em subprocess de um commit".

## Applicable Patterns

- `.vibeflow/patterns/warn-first-check.md`: a regra mora numa função pura testável; o `auto_check` só orquestra.
- `tools/test_selo_suite.py:18-21`: teste da função pura de gatilho (`dispara_suite_por_selo`).
- `tools/test_plano_dia.py:328-337` (`_hook_de_boot()`): carregar o hook por caminho com `importlib`.
- `tools/test_fuso_unico_leitores.py:48-62`: banco sintético em `tmp_path`.
- `tools/test_emed_api.py:400-402`: invariante "está no `.gitignore`" por `git check-ignore -q`.
- `tools/utils/state_utils.py:31-47` (`card_watermark_atual`): leitura `sqlite3` `mode=ro` por URI dentro de `tools/`.
- Convenções do medhub: teste novo no `python_files`; `tools/` pode abrir conexão própria; `AGENTE.md §10.1` (reler o arquivo no disco antes de editar `.gitignore`/`pytest.ini`).

## Risks

- **"A série de aderência sumiu."** → Decisão 1 + o caso "sem linha de hoje → grava" no DoD 1.
- **"O dia do hook não é o dia do plano."** → Decisão 3; o teste usa `date.today()`, o mesmo que `build()`.
- **"O commit ficou lento."** → `run_command` já imprime o tempo por bloco; se a espera incomodar, o `/ai-eng` decide (ALTERA) — fora desta parte.
- **"O primeiro commit só de docs foi bloqueado."** → Esperado se houver BLOCK latente (26/29 eram "sempre" no comentário). Medido em 10/10: `cli_signature_check` 0 órfãs; cláusulas BLOCK só para `gate_inexistente`/`nv_sem_data`, 0 hoje (`test_repo_real_sem_anotacao_mentirosa`). Se aparecer, é achado, não regressão.
- **"O teste in-process gravou no ledger real."** → Monkeypatch de `auto_check._ledger_record` e `auto_check.card_watermark_selar` (são os nomes importados no módulo). Os sensores "sempre" rodam de verdade sobre o repo, em leitura; `painel_divida` só lê.
- **"Dois agentes no mesmo `.gitignore`."** → `§10.1`: reler antes de editar; `.gitignore` e `git rm --cached` no mesmo commit.
- **"O `.jsonl` des-rastreado parou de ser escrito."** → Não para: continua sendo apendado no disco; só sai do índice.

## References

- `brain/observed-systems/medhub-reforma-2026-10-10/E-testes-harness.md` (ai-eng): tabela de flags `auto_check.py:495-585`, 29 checks, efeitos colaterais.
- `brain/observed-systems/medhub-reforma-2026-10-10/D1-git-housekeeping.md` (ai-eng): `d48de82`, contagem de commits que tocam os logs.
- medhub: `.vibeflow/specs/telemetria-estudo-part-1.md` (persistir o planejado é o default por desenho).
