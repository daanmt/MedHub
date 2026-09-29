# Spec: rotação do ledger -- part 3 (portadores e rito)

## Objetivo

A norma diz onde o achado nasce, onde ele vai morar quando fecha e em que momento sai da frente.

## Contexto

`AGENTE.md` 10.9 descreve o ledger como um arquivo só. `README.md` idem. `revisao-calibrada-contract.md:131` cita o ledger por número de linha. O rito de fechamento não tem passo de rotação. `/engenharia-cli` documenta o `selo.py` sem as flags novas (o check D5 bloqueia flag sem skill).

## Que fricção esta spec remove -- e ela é virtuosa ou viciosa?

Remove norma que descreve um sistema que deixou de existir: **viciosa**.

## Definition of Done

1. `AGENTE.md`: 3 (fechamento) ganha a rotação; 10 descreve o par de arquivos e a regra "antes de escrever achado novo, buscar o mecanismo nos dois".
2. `.claude/commands/engenharia-cli.md` documenta `--rotacionar`, `--apply`, `--expect`, `--onde`; `sync_skills --check` sai 0 e o check D5 passa.
3. `.agents/workflows/registrar-sessao.md` tem o passo de rotação no selo.
4. `README.md` e `docs/MEMORIA-AUDITORIA.md` descrevem o par; o índice manual fica datado como retrato.
5. `revisao-calibrada-contract.md:131` cita o F-id, sem número de linha.
6. Suíte completa verde, `auto_check --changed` PASSED e `selo.py` fechando.

## Escopo

- `AGENTE.md`, `README.md`, `docs/MEMORIA-AUDITORIA.md`
- `.claude/commands/engenharia-cli.md` (espelho gerado), `.agents/workflows/registrar-sessao.md`
- `core/contracts/revisao-calibrada-contract.md`

## Anti-escopo

- Reindexar F114-F142 no índice manual.
- Citações por número de linha dentro de `docs/MEMORIA-AUDITORIA.md` e de `history/`: são retrato datado.

## Decisões técnicas

- **A busca antes de escrever achado novo vira regra escrita** (gate-miss da s204: F140 x F32). Sem gate: nada lê a intenção de escrever. Declarado como não-verificável, com data.

## Dependencies

- `.vibeflow/specs/ledger-rotacao-part-1.md`
- `.vibeflow/specs/ledger-rotacao-part-2.md`
