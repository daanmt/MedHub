---
description: "[DEPRECADO] Fundido em /revisar. Desde a s170 o re-ensino de tema dormente acontece na Revisão Direcionada de FECHAMENTO da sessão de cards, não antes do drill. Stub de redirecionamento."
type: skill
layer: commands
status: deprecated
---

# Skill: Refrescar — DEPRECADA (fundida em /revisar)

> **`/refrescar` foi fundido em `/revisar`.** Não é mais uma competência autônoma.
> Norma: [`core/contracts/revisao-calibrada-contract.md`](../../core/contracts/revisao-calibrada-contract.md). Protocolo operacional: [`revisar.md`](revisar.md) §Fechamento.

## O que mudou

- **s096:** o re-ensino narrativo de tema dormente virou o antigo sub-modo **PREPARAR** de `/revisar`, entregue **antes** de drillar, com descompressão calibrada pela nota 1-10.
- ⚰️ **s170:** o **PREPARAR morreu** (lápide em [`revisar.md`](revisar.md)). O re-ensino migrou inteiro para a **Revisão Direcionada de FECHAMENTO** — depois do drill, ancorado nos temas que caíram em nota **1 e 2**. Motivo: o aquecimento pré-drill não era lido, e o ensino pós-drill mira o gap que o próprio drill acabou de provar que existe.
- O CLI permanece `tools/dormant_refresh.py` (`--pick`/`--context`/`--stamp`), com **`--kind {dormant_refresh,directed_review}`** (Invariante B — toda Revisão Direcionada carimba `review_log`, qualquer que seja o gatilho).
- A fronteira dura permanece: **o ensino não toca o FSRS** (Invariante A).

## Compatibilidade

Invocar `/refrescar [tema]` continua válido como atalho -> o tema entra na fila da **Revisão Direcionada de fechamento** de `/revisar` (gatilho de dormência -> `kind='dormant_refresh'`). Para a operação completa, ver [`revisar.md`](revisar.md) §Fechamento.
