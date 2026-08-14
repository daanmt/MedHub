# Spec: flashcards-integridade-part-4 — gate nos writers restantes + fim do no-op disfarçado

> De: `.vibeflow/prds/flashcards-integridade-geracao.md` · Gerado 2026-08-14 (ai-eng)
> Ordem: 4ª de 6. Dependencies:
> - .vibeflow/specs/flashcards-integridade-part-3.md (card_checks existe)

## Objective

Os 3 writers restantes (`insert_card_base`, `insert_card_extra`, `recurate_cards`) passam pelo mesmo gate de `card_checks`, e `recurate_cards` deixa de registrar reforja bem-sucedida que não alterou nada.

## Context

`insert_card_base.py` e `recurate_cards.py` gravam por default sem nenhuma validação; `insert_card_extra.py` valida presença mínima mas não estilo/encoding. `recurate_cards.py:72-83`: item sem nenhum campo de `FIELD_MAP` ainda executa UPDATE, incrementa `card_version` e grava `quality_source='qualitative'` — no-op disfarçado de reforja. Pré-auditoria §6.5.1 confirmada no terreno.

## Definition of Done

1. [ ] `insert_card_base.py`: cada card passa por `validar_card` antes do INSERT; erro → aborta com todas as violações, 0 linhas gravadas (teste); PRAGMA foreign_keys ligado na conexão própria.
2. [ ] `insert_card_extra.py`: idem (gate antes do INSERT; PRAGMA na conexão própria; dry-run default preservado).
3. [ ] `recurate_cards.py`: item sem nenhum campo válido de `FIELD_MAP` → **erro por item** (não UPDATE, não `card_version++`, não flip de `quality_source`), lote reporta itens rejeitados; itens válidos passam por `validar_card`; PRAGMA na conexão.
4. [ ] Teste por writer em `tools/test_writer_gates.py`: card com template/encoding proibido rejeitado; card válido gravado; caso no-op do recurate coberto com fixture (card_version não muda).
5. [ ] Craftsmanship: `pytest` verde; defaults de CLI **inalterados** (base grava por default, extra é dry-run — mudança de convenção é anti-scope); pt-BR; conexões fechadas em `finally`.

## Scope

- `tools/insert_card_base.py`, `tools/insert_card_extra.py`, `tools/recurate_cards.py` — gate + PRAGMA.
- `tools/test_writer_gates.py` — novo.

## Anti-scope

- NÃO unificar os defaults de dry-run entre CLIs (mudaria contratos que os workflows do agente usam; inconsistência registrada para decisão do lado MedHub).
- NÃO refatorar a duplicação de `get_or_create_tema`/INSERT fsrs_cards neste ciclo (registrada; risco de regressão > ganho agora).
- NÃO mudar assinaturas/flags existentes.

## Technical Decisions

- **Gate no ponto de escrita de cada CLI** (não wrapper comum de conexão): os 3 têm fluxos distintos; a biblioteca é o comum, o wiring é local e pequeno (~5 linhas por writer).
- **Erro por item em lote** (recurate): rejeitar o lote inteiro por 1 item ruim viraria ping-pong; rejeitar o item e reportar preserva o padrão do repo (relatar tudo de uma vez) sem gravar lixo.

## Applicable Patterns

- `patterns/warn-first-check.md`, `patterns/db-access-layer.md`, convenções de CLI (argparse, stdout humano, return bool).

## Risks

- **R1**: workflow existente que alimenta `recurate_cards` com itens propositalmente vazios (improvável) quebraria → mitigação: mensagem de erro lista exatamente os campos aceitos; comportamento anterior era bug confirmado pela pré-auditoria do próprio MedHub.
