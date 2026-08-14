# Spec: flashcards-integridade-part-6 — watermark de dado no harness

> De: `.vibeflow/prds/flashcards-integridade-geracao.md` · Gerado 2026-08-14 (ai-eng)
> Ordem: 6ª de 6. Dependencies:
> - .vibeflow/specs/flashcards-integridade-part-5.md (checks batch completos, que o gatilho dispara)

## Objective

O harness deixa de ser cego ao dado: `auto_check` dispara os checks de card quando **o banco** mudou desde a última corrida — mesmo com zero arquivos staged relevantes.

## Context

`auto_check.py:239-244` define `card_relevant` por arquivo **staged no git**; cards vivem no `ipub.db`, fora do git. O próprio comentário do código admite a limitação. Foi a 3ª causa independente do incidente dos 68 (§6.5.2 item 3) e é o furo arquitetural mais profundo apontado pelo handoff: **o dado não tem gate; só o código que o produz tem**. Família do set-diff recomendado ao daktus-hub: timestamp/arquivo não detecta mudança de dado.

## Definition of Done

1. [ ] `auto_check` persiste watermark `(MAX(flashcards.id), COUNT(*), MAX(card_version))` em `history/card_watermark.json`; em qualquer modo (`--staged`/`--changed`/`--all`), watermark divergente do arquivo → `card_relevant = True` (além do gatilho por arquivo, que permanece).
2. [ ] Watermark é atualizado **só após** os checks de card rodarem (corrida interrompida não avança o marco — teste).
3. [ ] Sensor defensivo (padrão warn-first): `ipub.db` ausente/ilegível → WARN visível `[WARN] CARD_WATERMARK: banco inacessivel` e checks de card rodam mesmo assim (fail-open para detecção, nunca silêncio que mascare sensor quebrado); arquivo de watermark corrompido → WARN + tratado como "mudou".
4. [ ] Teste `tools/test_auto_check_watermark.py`: fixture db + watermark tmp; (a) watermark igual → não dispara por dado; (b) INSERT de card → dispara; (c) reforja (`card_version++` sem INSERT) → dispara; (d) arquivo corrompido → dispara com WARN.
5. [ ] Craftsmanship: `pytest` verde; lógica do watermark em função própria testável (não inline no `main`); leitura do banco `mode=ro`; WARN não altera exit-code (warn-first); pt-BR.

## Scope

- `tools/auto_check.py` — função `card_watermark()` + integração no cálculo de `card_relevant` + persistência.
- `tools/test_auto_check_watermark.py` — novo.

## Anti-scope

- NÃO transformar checks de card em BLOCK (seguem WARN — endurecimento é decisão posterior).
- NÃO estender o watermark a outras tabelas neste ciclo (padrão fica pronto para replicar; escopo é o subsistema de flashcards).
- NÃO rodar os checks a cada comando fora do fluxo do auto_check (custo do hook é orçamento do harness do MedHub).

## Technical Decisions

- **Tripla (max_id, count, max_version)** cobre os 3 vetores de mudança: insert (max_id/count), delete (count), reforja in-place (max_version). Timestamp foi rejeitado: não pega UPDATE nem delete (mesma lição do watermark Notion do daktus-hub).
- **`history/`** como destino: padrão do repo para estado de harness (`ledger_self.jsonl` vive lá).
- **Fail-open com WARN** quando o sensor falha: para um *detector* (não um gate de escrita), rodar a mais é barato; silenciar é exatamente o modo de falha que este ciclo inteiro corrige.

## Applicable Patterns

- `patterns/warn-first-check.md` — integralmente (regra em módulo, WARN, ledger, sensor defensivo).

## Risks

- **R1**: hooks do MedHub rodarem auto_check com working dir inesperado e não acharem `history/` → mitigação: paths resolvidos a partir de `__file__` como o resto do arquivo já faz.
- **R2**: `MAX(card_version)` não capturar reforja que não incrementa versão (bug do no-op da part-4) → mitigação: part-4 elimina o no-op; ordem das specs garante.
