# Spec: Pipeline de Conhecimento -- Parte 4: Residuos do Ciclo 2 (Onda 4 / F27 + F28)

> Derivado de `.vibeflow/prds/pipeline-conhecimento.md` (Onda 4). Encoding ASCII (AGENTE 4.5).
> Parte 4 de 4. Totalmente independente das demais -- carona/limpeza.

## Objetivo

Fechar dois residuos do ciclo 2: o modo single de `insert_questao` passa a refletir falha no
exit code (F27), e o campo canonico do elo (`o_que_faltou`) fica documentado no workflow de
analise (F28) -- sem nenhuma mudanca de schema.

## Contexto

- **F27:** `tools/insert_questao.py` no modo `--errors-file` faz `sys.exit(0 if ok else 1)`
  (linha 372-374), mas o modo SINGLE (linha 385) chama `insert_questao(...)` SEM capturar o
  retorno nem chamar `sys.exit` -- entao o script sai 0 mesmo quando `insert_questao` retorna
  `False`. A docstring/contrato promete exit 1 em falha. Um hook/chamador que confie no exit
  code do modo single hoje recebe sinal errado.
- **F28:** o arg `--elo` (opcional no parser, linha 343) nao tem coluna propria em
  `questoes_erros`; o campo canonico de fato e `o_que_faltou`. Isso nao esta documentado em
  lugar nenhum, e o `--elo` permanece porque e consumido pelo matcher de reincidencia (F25).

## Definition of Done

Binarios (pass/fail):

1. **F27:** o modo single de `insert_questao.py` captura o retorno de `insert_questao(...)` e
   faz `sys.exit(0 if ok else 1)`; falha -> exit 1, sucesso -> exit 0. Simetrico ao modo
   batch.
2. **F27 -- sem regressao de chamadores.** `grep` das invocacoes de `insert_questao.py`
   (skills, workflows, hooks, `.claude/`, `tools/`) confirma que nenhum chamador depende do
   exit 0 atual em falha; se algum depende, e ajustado ou documentado. `auto_check` verde.
3. **F27 -- teste.** Teste (novo ou em `tools/test_batch_insert.py`) exercita o modo single:
   entrada que faz `insert_questao` retornar `False` -> processo sai com codigo 1; entrada
   valida -> exit 0.
4. **F28:** o workflow `analisar-questao` (`.claude/commands/analisar-questao.md` e/ou
   `.agents/workflows/analisar-questoes.md`) documenta que o campo canonico do elo e
   `o_que_faltou`; o `--elo` permanece (consumido pelo matcher F25), SEM coluna nova.
5. **Craftsmanship + paridade:** nenhum schema alterado; se a doc F28 tocar um
   `.claude/commands/*.md` espelhado, `python tools/sync_skills.py --check` passa; ASCII
   limpo; a mudanca F27 nao altera o comportamento de sucesso nem a saida legivel existente.

## Escopo

- `tools/insert_questao.py`: capturar `ok = insert_questao(...)` no modo single + `sys.exit(0
  if ok else 1)`.
- Teste do exit code do modo single (em `tools/test_batch_insert.py` ou novo
  `tools/test_insert_exit.py`).
- Doc F28 no workflow de analise: `.claude/commands/analisar-questao.md` (fonte canonica) e,
  se existir, `.agents/workflows/analisar-questoes.md`. Regenerar espelho se aplicavel.

## Anti-escopo

- **Coluna nova de schema** -- F28 e resolvido por DOCUMENTACAO; a unica mudanca de schema do
  ciclo 2 (`status`) permanece a unica.
- **Remover o arg `--elo`** -- ele fica; e consumido pelo matcher de reincidencia F25.
- **Refatorar `insert_questao`/`insert_batch`** -- so o exit code do single muda.
- **Mudar o comportamento de sucesso** ou a saida legivel do CLI.

## Decisoes tecnicas

- **Espelhar exatamente o batch:** `ok = insert_questao(...)` seguido de `sys.exit(0 if ok
  else 1)`. `insert_questao` ja retorna `bool` (convencao de CLIs em conventions.md). Mudanca
  minima, simetrica, sem novo fluxo.
- **Grep de chamadores ANTES de mudar** (DoD #2). O parecer do PRD pede conferir se algum
  hook/chamador depende do exit 0 atual. Provavel que nenhum dependa (falha silenciosa e o
  bug), mas a verificacao e barata e evita quebrar um pre-commit/CI.
- **F28 e documentacao pura.** O `--elo` alimenta o matcher F25; `o_que_faltou` e a coluna
  real. Documentar o mapeamento no workflow evita que uma sessao futura crie coluna
  redundante ou trate `--elo` como persistido.

## Applicable patterns

- `patterns/error-insertion-pipeline.md` -- pipeline `insert_questao` + flashcards; contrato
  de exit code do CLI.
- Convencao "CLI tools": retorno bool, exit codes, `finally: conn.close()`.
- `tools/sync_skills.py --check` para paridade, se a doc F28 tocar command espelhado.

## Riscos

- **Um hook silenciosamente dependia do exit 0 em falha.** Mitigacao: DoD #2 (grep +
  auto_check) e justamente o gate; se achado, decidir explicitamente (ajustar o chamador,
  nao reverter o fix).
- **Doc F28 no arquivo errado** (editar so o workflow e nao o command espelhado, ou
  vice-versa). Mitigacao: identificar a fonte canonica vs espelho (sync_skills) e rodar
  `--check`.
