# Spec: Telemetria de fila FSRS -- pool x divida (Part 2)

> Gerado via /vibeflow:gen-spec on 2026-07-15 -- de `.vibeflow/prds/auto-suficiencia-card-e-telemetria-fila.md`

## Objective

`day_plan` passa a reportar `pool` (cards nunca-introduzidos) e `divida` (revisao atrasada) como grandezas **distintas e rotuladas** no plano-do-dia e no `--handoff-block`, encerrando a leitura enganosa de "backlog: N novos" como se fosse divida.

## Context

`insert_questao.py` grava `due = datetime.now()` na criacao -> todo card novo nasce "vencido" (630 novos, 100% due-no-passado). O `day_plan._fsrs_counts()` **ja separa** internamente `atrasados` (state>0 + due<now = divida real) de `backlog_novos` (state=0 = pool), mas o `render()`/`render_handoff_block()` rotulam o pool como "Backlog: N novos" -- que o usuario le como divida. Resultado: "22 atrasados + 4 hoje + 425 novos (backlog)" nao faz sentido. E defeito de **rotulo/apresentacao**, nao de mecanismo. Confirmado na sessao 121.

## Definition of Done

1. `python tools/day_plan.py --handoff-block` emite `pool` e `divida` como campos distintos e rotulados (ex.: "vencidos (divida) N -- pool M nunca introduzidos"), sem o termo "backlog" agregando os dois sentidos.
2. O cabecalho do plano-do-dia (`day_plan.py` sem flag, funcao `render`) distingue pool x divida na linha FSRS, e explicita o teto de introducao/dia.
3. As definicoes batem com o db: `divida` = ativos `state>0 AND due<now`; `pool` = ativos `state=0`; teto derivado de `_teto_efetivo`. (Reusa `_fsrs_counts`, sem redefinir contagem.)
4. **Zero write novo:** nenhuma alteracao em `insert_questao`, `fsrs_queue`, no valor de `due`, nem no schema -- a mudanca e so leitura/apresentacao (verificavel: nenhum INSERT/UPDATE novo no diff).
5. **[craftsmanship]** A logica de rotulacao pool/divida, se reusada em `render` e `render_handoff_block`, mora numa funcao/helper testavel (nao duplicada inline); `tools/test_day_plan_telemetria.py` valida pool/divida contra um db-fixture; zero violacao dos Don'ts de `conventions.md`.

## Scope

- `tools/day_plan.py`: ajustar `render_handoff_block()` e `render()` pra rotular pool x divida + teto; helper de rotulacao se houver reuso.
- Teste unitario da distincao pool/divida contra fixture.
- Se o rotulo do bloco numerico for contratual, nota de atualizacao em `handoff-contract.md` (F6).

## Anti-scope

- Mudar `due=now()` na criacao (re-arquitetura do due) -- vira F/spec proprio se o usuario quiser depois.
- Mudar a logica de bucketing do `fsrs_queue` (atrasados/hoje/novos).
- Feature A (check de auto-suficiencia) -- Part 1.
- Streamlit/UI.
- Mudar o `_teto_efetivo` / regime de divida (so exibir).

## Technical Decisions

- **So telemetria (leitura), nao mecanismo.** Menor risco, resolve a dor (contagem mentindo) sem ripple no scheduling. A separacao pool/divida ja existe em `_fsrs_counts`; o trabalho e de rotulo.
- **Definicoes canonicas:** `divida` = `state>0 AND due<now` (ja e o `atrasados`); `pool` = `state=0` (ja e o `backlog_novos`). Manter os nomes internos, mudar so a apresentacao -- ou renomear com cuidado se melhorar a leitura, sem quebrar consumidores.
- **Compat de boot:** o `--handoff-block` alimenta o F6 do HANDOFF e o header alimenta o hook SessionStart. Manter formato legivel e testar o `--handoff-block` pra nao quebrar parsing downstream.

## Applicable Patterns

- **`agent-workflow-protocol.md`** -- o `--handoff-block` (F6) e derivado, nunca digitado a mao; a mudanca preserva essa disciplina.
- **`db-access-layer.md`** -- reusar `_fsrs_counts` (nao abrir contagem nova).

## Risks

- **HANDOFF/ESTADO com "backlog" no texto derivado** -> o F6 auto-gera o bloco; atualizar o gerador propaga. Rodar `auto_check` (F1/F6) pra garantir que nao quebra.
- **Consumidor downstream do formato** (hook SessionStart le o day_plan) -> manter linha legivel; teste do `--handoff-block` cobre o formato.
- **Sobre-engenharia** (mexer no mecanismo) -> anti-scope explicito: v0 e so rotulo.

## Dependencies

Nenhuma. Independente da Part 1.
