---
title: "Part 1 -- Disparo forcado do sync do Drive + ordenacao real das tarefas"
type: spec
status: ready
prd: .vibeflow/prds/boot-cronograma-drive-confiavel.md
ledger: AUDITORIA_MEDHUB.md (F34; residual de F33/W8 + F29)
date: "2026-07-09"
budget: 6 files
---

# Spec Part 1 -- Disparo forcado do sync do Drive + ordenacao real (Ondas C + A)

## Objective

O boot para de apresentar "proximos temas" em silencio sobre um snapshot velho, e passa a ordenar os temas da semana pela ordem real que o usuario mantem no xlsx do Drive -- nao mais pela sequencia congelada do `Cronograma.pdf`.

## Context

O hook `SessionStart` roda headless (sem MCP) e injeta o `day_plan`, que le a conclusao real do Drive de um snapshot em `preparacao_estado.cronograma_conclusao_drive` (gravado por `cronograma.py --sync-drive`, W8/F33). Hoje (09/07) o boot regrediu ao vivo: listou `proximos temas: MFC, Imunizacoes, Apendicite` -- todos ja feitos -- porque nenhum snapshot fresco existia e `_cronograma_hoje` caiu para a ordem do PDF, sinalizando `conclusao_desatualizada=True` de forma fraca demais (so um "(sync: ...)" no fim da linha, em `day_plan.py:671`). Alem disso, o usuario reordena tarefas manualmente no xlsx (a ordem das linhas `DRIVE_TASK_ROWS` dentro da coluna-semana), e o `--sync-drive` ja itera essas linhas em ordem mas descarta a posicao. `AGENTE.md` 2.4 trata o sync como passo *condicional* ("se aparecer o WARNING, buscar"). Esta parte torna a ordem capturavel e o disparo obrigatorio-de-tentativa, sem violar Clausula 1 (SSOT=PDF, sem MCP no boot automatico) nem Clausula 3 (sem cron/daemon) nem Clausula 6 (reconcile nunca BLOCKING).

## Definition of Done

1. `cronograma.py --sync-drive` grava, por task no snapshot `cronograma_conclusao_drive`, um campo `ordem` = posicao da celula (linha de `DRIVE_TASK_ROWS`) dentro da coluna-semana do xlsx; o unico write continua sendo `preparacao_estado` (Clausula 5, verificavel: zero INSERT/UPDATE em taxonomia_cronograma/sessoes_bulk/FSRS/review_log).
2. `day_plan.py::_conclusao_drive` passa a retornar tambem um mapa de ordem por `(semana, tarefa)`; `_cronograma_hoje` ordena `temas`/`temas_material` por essa ordem quando o snapshot e fresco.
3. Sem snapshot fresco (ausente, de dia anterior, ou formato antigo sem `ordem`), o render mantem a ordem do `grade.json` (PDF) e marca `conclusao_desatualizada=True` -- sem crash (acesso via `.get('ordem', ...)`), sem falha silenciosa.
4. `day_plan.py` emite, no topo do bloco de cronograma, um banner de frescor do Drive: data da ultima sync, ou `Drive: STALE (Nd atras)` quando `conclusao_desatualizada`.
5. `AGENTE.md` 2.4 reescrito: quando o snapshot esta velho, o sync do Drive e **acao obrigatoria** -- o agente busca o xlsx via MCP e roda `--sync-drive` ANTES de apresentar "proximos temas"; com MCP indisponivel, apresenta calendario-only com **caveat explicito nomeando o risco de temas-ja-feitos**. (Sem BLOCK.)
6. `reconcile-contract.md` W8 e `cronograma-contract.md` Clausula 5 documentam o campo `ordem` e o disparo obrigatorio-de-tentativa; a filosofia "nunca BLOCKING" (Clausula 6) permanece textual e intacta.
7. (Quality gate) `python -X utf8 tools/auto_check.py --changed` retorna `PASSED` (0 BLOCK); nenhum `import sqlite3` novo fora de `app/utils/db.py`/CLIs standalone (padrao db-access-layer); texto novo em ASCII limpo (AGENTE 4.5: sem setas Unicode, sem `$...$`).

## Scope

- `tools/cronograma.py`: `diff_drive`/`sync_drive` anexam `ordem` por task (a posicao da celula casada dentro da lista da coluna-semana; ja disponivel no loop de `_parse_conclusao_xlsx`).
- `tools/day_plan.py`: `_conclusao_drive` retorna o mapa de ordem; `_cronograma_hoje` usa-o para ordenar; banner de frescor no render do bloco de cronograma.
- `AGENTE.md`: reescrever o passo de sync do 2.4 (condicional -> obrigatorio-de-tentativa + fallback com caveat).
- `core/contracts/cronograma-contract.md`: Clausula 5 documenta a chave estendida.
- `core/contracts/reconcile-contract.md`: W8 refinado.
- `tools/test_autonomia_hooks.py` (ou suite de cronograma): fixture de snapshot fresco com `ordem` fora da sequencia do PDF -> assert ordem respeitada; snapshot velho/sem-`ordem` -> assert fallback PDF + `conclusao_desatualizada`.

## Anti-scope

- **Sem automacao do fetch do Drive** (cron/daemon/credencial de servico/cache local) -- viola Clausula 1/3. O `--sync-drive` continua disparado pelo agente interativo.
- **Sem reescrever `grade.json`** a partir do xlsx -- a ordem vive so no snapshot `preparacao_estado`, sobreposta em memoria.
- **Sem BLOCK** de boot por snapshot velho -- so banner + protocolo obrigatorio-de-tentativa.
- **F30/F31 (integridade de rotulo) e higiene de estado** ficam nas Parts 2 e 3.
- Sem alinhamento fino `questoes_por_lista[i] <-> tasks[i]` (rateio igual, fora de escopo do contrato).

## Technical Decisions

- **Ordem = indice de linha do xlsx.** A reordenacao manual do usuario e a ordem das linhas `DRIVE_TASK_ROWS` dentro da coluna-semana; capturar `row` (ou o indice ordinal da celula na lista da coluna) e o sinal direto, sem heuristica. Trade-off: se o usuario reordena *entre* semanas (mover task de coluna), isso ja e captado porque `semana` = coluna; a ordem intra-semana e o `row`.
- **Estender a chave existente, nao criar irma.** Adicionar `ordem` ao dict de task de `cronograma_conclusao_drive` mantem um unico read no `_conclusao_drive` (vs. dois snapshots a reconciliar). Compat retro: leitura via `.get('ordem')` -> fallback quando ausente.
- **Banner via `atualizado_em`.** O frescor ja e computado (`_conclusao_drive` compara `atualizado_em[:10]` com hoje); o banner so promove esse sinal de rodape a cabecalho.
- **Disparo e protocolo, nao codigo.** O `day_plan.py` (CLI Python, headless-safe) nao pode chamar MCP; entao a obrigatoriedade vive no `AGENTE.md` (o agente interativo executa) + o banner que torna o estado velho impossivel de ignorar. Isso respeita Clausula 1 por construcao.

## Applicable Patterns

- `db-access-layer.md`: o snapshot le/grava so via `db.get_preparacao`/`db.set_preparacao`; `cronograma.py`/`day_plan.py` sao CLIs standalone (excecao autorizada), nunca `import sqlite3` novo em outra camada.
- `agent-workflow-protocol.md`: o passo de sync do boot (AGENTE 2.4) segue o protocolo de boot proativo (oferece/executa, degrada gracioso).

## Risks

- **Estrutura do xlsx muda** -> `_parse_conclusao_xlsx` ja aborta com erro claro (valida a linha de datas); a captura de `ordem` herda essa guarda.
- **Snapshot antigo sem `ordem`** apos deploy -> mitigado por `.get('ordem', <fallback ordinal do grade>)`; teste cobre.
- **Banner ruidoso** -> manter em uma linha; so aparece STALE quando `conclusao_desatualizada`.
- **Falso "obrigatorio" em sessao headless** -> o AGENTE 2.4 preve explicitamente o fallback calendario-only-com-caveat quando o MCP nao esta disponivel; nunca trava.

## Dependencies

Nenhuma (primeira parte). Parts 2 e 3 dependem desta (compartilham `day_plan.py`).
