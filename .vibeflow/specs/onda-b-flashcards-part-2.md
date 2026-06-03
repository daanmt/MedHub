# Spec: Onda B · Part 2 — Persistência de N Cards Atômicos + UPDATE in-place

> Gerado via /vibeflow:gen-spec em 2026-06-03
> PRD: `.vibeflow/prds/onda-b-flashcards-metacognitivos.md`
> Split: part 2 de 3. Ver part-1 (contrato), part-3 (backfill).

## Objective

Dar à camada de persistência a capacidade de gravar **N cards atômicos** por erro (em vez da estrutura fixa elo+armadilha) e de **atualizar cards existentes preservando o `card_id`** (logo o estado FSRS), habilitando go-forward atômico e backfill sem perder histórico.

## Context

`insert_questao.py` hoje gera estrutura fixa: 1 card `elo_quebrado` + (se `armadilha`>20) 1 card `armadilha`. A régua (part-1) pede cards atômicos de conteúdo cujo número varia por erro (ex.: #211 → "agentes de úlcera" + "agentes de corrimento"). E não existe caminho para reescrever um card legado sem deletar/recriar — o que zeraria `fsrs_cards`/`fsrs_revlog` daquele card. Ambas as lacunas bloqueiam a Onda B.

## Definition of Done

1. `insert_questao.py` aceita `--cards-file <path.json>`: uma lista de cards atômicos, cada um com `tipo, frente_contexto, frente_pergunta, verso_resposta, verso_regra_mestre, verso_armadilha`. Quando fornecido, substitui a geração fixa elo+armadilha; cada card vira `quality_source='qualitative'`, `needs_qualitative=0`, com `fsrs_cards` inicializado.
2. Sem `--cards-file`, o comportamento atual de `insert_questao.py` permanece **inalterado** (retrocompatível).
3. `app/utils/db.py` ganha `update_flashcard_fields(card_id, fields)`: atualiza os campos v5 de um card existente por `card_id`, sem tocar em `fsrs_cards`/`fsrs_revlog`, marcando `quality_source='qualitative'`, `needs_qualitative=0` e incrementando `card_version`.
4. O JSON é lido como UTF-8 (suporta acentuação/marcadores clínicos), contornando o limite de aspas/unicode do PowerShell que afeta args inline.
5. **(Quality gate)** `update_flashcard_fields` segue o pattern `db-access-layer` (`get_connection`→cursor→`commit`→`close`, params parametrizados, sem f-string em SQL); `insert_questao.py` mantém `import sqlite3` como CLI standalone autorizado; schema da tabela `flashcards` **inalterado** (`tipo` continua TEXT livre).
6. Teste manual documentado: inserir um erro com `--cards-file` de 2 cards atômicos cria 2 linhas em `flashcards` + 2 em `fsrs_cards`; `update_flashcard_fields` num card real altera os campos e preserva a linha de `fsrs_cards` (verificado com captura+restauração, sem alteração líquida).

## Scope

- `tools/insert_questao.py` (editar) — adicionar `--cards-file`; ramo de N cards atômicos; preservar caminho legado.
- `app/utils/db.py` (editar) — adicionar `update_flashcard_fields(card_id, fields)`.

## Anti-scope

- A régua de conteúdo dos cards (é a part-1).
- O loop de backfill e a aposentadoria de `regenerate_cards*.py` (é a part-3).
- FSRS fiel (Onda A part-2).
- Mudança de schema (`tipo` permanece TEXT; nenhuma coluna nova).
- Geração heurística (não estender `_invert_elo_to_question`; ele será aposentado na part-3).

## Technical Decisions

- **`--cards-file` (JSON em arquivo), não `--cards` inline.** O agente escreve o JSON em arquivo e passa o path. Trade-off: um arquivo temporário a mais, mas elimina o inferno de quoting/unicode do PowerShell (já alertado em `analisar-questao.md`) e expressa 1..N cards uniformemente.
- **UPDATE in-place preserva `card_id`** (decisão da open question do PRD): manter o estado FSRS do card legado é preferível a aposentar+recriar (que zeraria stability/difficulty/histórico). `card_version` é incrementado para rastrear a linhagem.
- **`tipo` livre.** Cards atômicos de conteúdo usam `tipo='conteudo'` (ou o tipo que o JSON trouxer); `tipo` é TEXT, sem migração.
- **Retrocompatibilidade total** do caminho sem `--cards-file` — não quebra o uso atual nem a part-1 enquanto a régua amadurece.

## Applicable Patterns

- `error-insertion-pipeline.md` — preservar a transação atômica (taxonomia → questao → cards → fsrs_cards → métricas, commit único).
- `db-access-layer.md` — `update_flashcard_fields` no padrão de escrita; params parametrizados.

## Risks

- **Quebrar o caminho legado de `insert_questao`** ao ramificar → DoD #2 + teste; manter o ramo antigo intacto, só adicionar o novo.
- **JSON malformado vindo do agente** → validar campos mínimos (`frente_pergunta`, `verso_resposta`) e falhar com mensagem clara, sem corromper a transação.
- **`update_flashcard_fields` tocar FSRS por engano** → DoD #3/#6 exigem preservação verificada de `fsrs_cards`.

## Dependencies

- `.vibeflow/specs/onda-b-flashcards-part-1.md` (a régua define o conteúdo que esta persistência grava; recomenda-se part-1 auditada antes).
