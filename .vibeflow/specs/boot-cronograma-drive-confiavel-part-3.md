---
title: "Part 3 -- Higiene de estado: contador derivado, ESTADO nao-diario, ponteiro de abertos"
type: spec
status: ready
prd: .vibeflow/prds/boot-cronograma-drive-confiavel.md
ledger: AUDITORIA_MEDHUB.md (risco 5 da auditoria de boot)
date: "2026-07-09"
budget: 6 files
---

# Spec Part 3 -- Higiene da camada de estado (Onda D)

## Objective

Os numeros que o boot le como verdade-macro deixam de ser digitados a mao (fim do contador de resumos divergente), e a linha macro do `ESTADO` para de virar diario de sessoes -- "derive, nao mantenha a mao".

## Context

A camada de estado que o boot le drifta a mao. O `ESTADO.md` traz o contador de resumos como **63** (linha 25) e **61** (linha 33) no mesmo arquivo; a linha "Indicador Atual" acumula narrativa de s096..s114 num paragrafo-corrido, contra o `estado-contract` ("nao e diario de sessoes"); e o bloco de abertos do `HANDOFF` lista F21/F30 mas **omite F31** (que tem instancia viva hoje). O padrao ja provado no F6 -- numeros derivados via `day_plan.py --handoff-block` em vez de digitados -- resolve a classe, mas nao cobre o contador de resumos.

## Definition of Done

1. `day_plan.py --handoff-block` passa a emitir o **contador de resumos derivado** (contagem de `resumos/**/*.md`); o bloco numerico do `HANDOFF` consome esse valor (nao mais digitado).
2. `ESTADO.md`: a linha "Indicador Atual" e enxugada para o snapshot macro corrente (contador unico e consistente; a narrativa por-sessao permanece em `history/`), conforme `estado-contract`.
3. `HANDOFF.md`: o bloco de abertos inclui F31 e reflete os abertos reais do ledger (F21/F30/F31).
4. `estado-contract.md` reforca operacionalmente a regra "linha Indicador nao e diario de sessoes" (uma frase normativa referenciavel).
5. (Quality gate) `python -X utf8 tools/auto_check.py --changed` retorna `PASSED`; ASCII limpo; nenhum numero macro que ja seja derivavel por `--handoff-block` (volume, FSRS, backlog, agora contador de resumos) fica digitado a mao no HANDOFF.

## Scope

- `tools/day_plan.py`: `render_handoff_block` (linha ~618) deriva e inclui a contagem de `resumos/**/*.md`.
- `ESTADO.md`: enxugar a linha "Indicador Atual"; unificar o contador de resumos.
- `HANDOFF.md`: corrigir o ponteiro de abertos (incluir F31).
- `core/contracts/estado-contract.md`: uma clausula/frase reforcando "Indicador nao e diario".
- (Opcional, se barato) WARN no `auto_check` quando o contador digitado no HANDOFF diverge do derivado -- so se couber no budget sem estourar; caso contrario, fica como nota para uma sessao futura.

## Anti-scope

- **Nao reescrever o `ESTADO` inteiro** -- so a linha Indicador e o contador. A reforma completa do ESTADO e fora de escopo.
- **Nao tocar** metas/indicador de volume/FSRS (ja derivados por `--handoff-block`; F6).
- **Nao fabricar** `history/session_NNN` retroativos (proibido por convencao).
- **Nao mexer** em cronograma/Drive (Part 1) nem integridade de rotulo (Part 2).

## Technical Decisions

- **Contagem via glob simples** de `resumos/**/*.md` (mesmo padrao que o linter `audit_resumos.py` ja usa para varrer o corpus) -- fonte unica, sem cache a driftar. Excluir stubs? Nao: contar `.md` reais como o linter conta, para o numero bater com a auditoria.
- **Enxugar, nao apagar a historia.** A narrativa de sessao sai do ESTADO e vive em `history/` (ja e o SSOT de sessoes); o ESTADO fica com o snapshot macro corrente, como o contrato manda.
- **F31 no ponteiro** e uma correcao textual pontual do HANDOFF -- alinha o ledger (abertos reais) com o que o boot injeta.

## Applicable Patterns

- `agent-workflow-protocol.md`: `--handoff-block` como fonte derivada do bloco numerico do HANDOFF (o texto qualitativo continua manual; so numeros viram derivados).

## Risks

- **Contagem divergente do linter** (se usar um glob diferente do `audit_resumos.py`) -> usar o mesmo padrao de varredura para garantir 1 numero.
- **Enxugar demais o ESTADO** e perder contexto macro util -> preservar o snapshot corrente (metas, indicador, marcos); so remover o acumulo por-sessao que ja esta em `history/`.

## Dependencies

- `.vibeflow/specs/boot-cronograma-drive-confiavel-part-1.md` (compartilha `day_plan.py`; implementar a Part 1 primeiro). Independente da Part 2 (funcoes distintas em `day_plan.py`).
