---
name: "source-command-refrescar"
description: "[DEPRECADO] Fundido em /revisar como o sub-modo PREPARAR (Revisão Calibrada, s096). Stub de redirecionamento — o re-ensino de tema dormente agora abre dentro de /revisar, com a descompressão calibrada pela nota 1-10."
---

# source-command-refrescar

Use this skill when the user asks to run the migrated source command `refrescar`.

## Command Template

# Skill: Refrescar — DEPRECADA (fundida em /revisar)

> **`/refrescar` foi fundido em `/revisar` como o sub-modo PREPARAR** (Revisão Calibrada, s096). Não é mais uma competência autônoma.
> Norma: [`core/contracts/revisao-calibrada-contract.md`](../../core/contracts/revisao-calibrada-contract.md). Protocolo operacional: [`revisar.md`](revisar.md) §PREPARAR.

## O que mudou

- O re-ensino narrativo de tema dormente é agora o **sub-modo PREPARAR** de `/revisar`, com a descompressão **calibrada pela nota 1-10** (antes: sempre descomprimia num ponto fixo).
- O CLI permanece `tools/dormant_refresh.py` (`--pick`/`--context`/`--stamp`), agora com **`--kind {dormant_refresh,directed_review}`** (Invariante B — todo PREPARAR carimba `review_log`, qualquer que seja o gatilho).
- A fronteira dura permanece: **PREPARAR não toca o FSRS** (Invariante A).

## Compatibilidade

Invocar `/refrescar [tema]` continua válido como atalho → abre `/revisar` no sub-modo PREPARAR (gatilho de dormência → `kind='dormant_refresh'`). Para a operação completa (incluindo a transição para DRENAR e a calibração por nota), ver `revisar.md` §PREPARAR/DRENAR.
