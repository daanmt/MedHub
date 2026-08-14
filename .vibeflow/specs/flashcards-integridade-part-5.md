# Spec: flashcards-integridade-part-5 — view canônica de ativo, detectores no batch e calibração

> De: `.vibeflow/prds/flashcards-integridade-geracao.md` · Gerado 2026-08-14 (ai-eng)
> Ordem: 5ª de 6. Dependencies:
> - .vibeflow/specs/flashcards-integridade-part-1.md (definição de ativo já corrigida na regen queue)
> - .vibeflow/specs/flashcards-integridade-part-3.md (predicados existem)

## Objective

"Card ativo" vira uma definição única (VIEW `flashcards_ativos`), os detectores cross-field entram na auditoria batch, os 3 sinais excluídos voltam ao agregado, `audit_card_atomicity` ganha suíte própria — e o recall do conjunto é **medido** contra os 68 do incidente (meta ≥ 66/68).

## Context

3 definições divergentes de ativo em 5 arquivos (§6.5.2 do handoff; a 4ª divergência está no próprio handoff — denominadores 1209 vs 978). `audit_flashcard_quality.py:164` exclui `needs_qual`/`regra_vazia`/`structured_null` do "TOTAL COM ≥1 SINAL" e do `--export`. `audit_card_atomicity.py` está no harness automático sem suíte própria. Nenhum detector batch é relacional. Fixture real de calibração: 68 cards `questao_id BETWEEN 781 AND 814` (todos nq=2, confirmado 2026-08-14).

## Definition of Done

1. [ ] `db.py` cria `CREATE VIEW IF NOT EXISTS flashcards_ativos AS SELECT * FROM flashcards WHERE COALESCE(needs_qualitative,0) < 2` via `_ensure_views()` chamado em `get_connection()`; helper `ativos()` disponível; teste de equivalência: contagem da view == contagem da expressão inline na fixture.
2. [ ] `audit_flashcard_quality.py`, `audit_card_atomicity.py` e `card_self_sufficiency.py` usam a view (ou a expressão canônica via constante única importada, para conexões `mode=ro` que antecedem a criação da view) — zero SQL inline novo com `needs_qualitative` divergente; contagens pré/pós-migração impressas no primeiro run e idênticas (fixture).
3. [ ] Os 3 sinais excluídos voltam ao agregado e ao `--export` de `audit_flashcard_quality.py` (continuam discriminados individualmente); teste: card com `regra_vazia` conta no total.
4. [ ] Detectores cross-field de `card_checks` expostos no batch de `audit_flashcard_quality.py` (join com `questoes_erros` para `titulo`/`alternativa_marcada`; predicados em Python, SQL simples) — novos sinais aparecem no relatório e no export com tag própria.
5. [ ] `tools/test_audit_card_atomicity.py` existe: casos do docstring (falsos-positivos conhecidos) + 1 caso por regra ativa — o detector que está no harness deixa de ser não-testado.
6. [ ] `tools/calibrate_card_checks.py` (novo, read-only `mode=ro`, execução manual): roda os predicados sobre `questao_id BETWEEN 781 AND 814` do banco real, imprime recall X/68 por predicado e agregado, grava resultado no `ledger_self.jsonl` (fingerprint `calibracao|card_checks`). Meta ≥ 66/68; se < meta, ajustar thresholds de `resposta_embutida` (part-3) e re-medir ANTES do commit final do ciclo — o número medido entra na mensagem de commit.
7. [ ] Craftsmanship: `pytest` verde; nenhum teste depende do `ipub.db` real (calibração é script manual, não CI); padrão warn-first (sinais novos no batch são WARN/INFO, não mudam exit-code); pt-BR.

## Scope

- `app/utils/db.py` — `_ensure_views()` + `ativos()` + constante `ATIVO_WHERE` exportável.
- `tools/audit_flashcard_quality.py` — agregado + cross-field batch + view.
- `tools/audit_card_atomicity.py`, `tools/card_self_sufficiency.py` — definição canônica.
- `tools/test_audit_card_atomicity.py`, `tools/calibrate_card_checks.py` — novos.

## Anti-scope

- NÃO endurecer nenhum sinal batch para BLOCK (warn-first; endurecimento = decisão posterior com base real).
- NÃO reescrever a lógica interna dos sinais existentes de `audit_flashcard_quality` — só agregação/definição de ativo/adição dos cross-field.
- NÃO commitar nenhum output com texto clínico (o calibrador imprime IDs e contagens, nunca conteúdo de card).
- NÃO tocar `init_db.py` (view garantida por `_ensure_views`; drift do init registrado como pendência).

## Technical Decisions

- **VIEW + constante**: conexões rw (via fábrica) garantem a view; CLIs `mode=ro` usam a constante `ATIVO_WHERE` importada de `db.py` — uma fonte, duas formas, zero risco de CREATE em conexão read-only.
- **Predicados em Python sobre fetch simples** (não SQL complexo): mantém a regra num lugar só (`card_checks`), testável puro; o volume (1.3k cards) torna o custo irrelevante.
- **Calibração fora do CI**: banco fora do git é a restrição-mestre do PRD; o número vive no ledger (memória de achado com ciclo de vida), não em teste que quebraria em outro clone.

## Applicable Patterns

- `patterns/warn-first-check.md` (sinais novos WARN; ledger), `patterns/db-access-layer.md`.

## Risks

- **R1**: recall < 66/68 na 1ª medição → mitigação prevista no DoD 6: ajustar threshold e re-medir; se um padrão do incidente for indetectável estruturalmente, documentar qual e por quê no ledger (honestidade > meta).
- **R2**: view quebrar consumidor com SELECT posicional → mitigação: view é `SELECT *` da mesma tabela; testes de equivalência de contagem + pytest inteiro.
