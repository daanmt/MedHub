---
type: spec
projeto: MedHub
feature: revisao-calibrada
part: 4
slug: revisao-calibrada-part-4-contrato-skills
status: ready
relates_to:
  - docs/plans/s094-revisao-calibrada-PRD.md
  - .claude/commands/revisar.md
  - .claude/commands/refrescar.md
  - core/contracts/revisao-calibrada-contract.md
  - AGENTE.md
---

# Spec — Revisão Calibrada · Parte 4: Contrato, Skills e AGENTE

> Deriva do PRD §8. Cobre **DoD-3, DoD-4, DoD-7, DoD-10**. Depende das Partes 1-3 (referencia `set_dificuldade`, `infer_nota`, Invariantes A/B).

## Objective
A competência única `/revisar` calibrada por dificuldade fica **documentada e normativa**; `/refrescar` é deprecado como skill autônoma e vira o sub-modo PREPARAR.

## Context
`/revisar` e `/refrescar` são skills markdown separadas que, na prática vivida, se atropelam (PRD §1.1). AGENTE.md §1.2 ainda diz "Calibração pendente". Faltam: o contrato lateral que normatiza escala/degraus/invariantes/`infer_nota`, e a fusão na skill. Partes 1-3 já entregaram o substrato de código (schema, inferência, barreiras).

## Definition of Done
1. **Contrato (DoD-3).** Existe `core/contracts/revisao-calibrada-contract.md` com frontmatter `type: contract / layer: core / status: pending-ratification` e contém (grep): os **4 degraus D10/D8/D5/D2** com faixas de parágrafos, **"Invariante A"** e **"Invariante B"** nomeadas, e o pseudocódigo de `infer_nota()`.
2. **Skill fundida (DoD-4).** `.claude/commands/revisar.md` documenta os sub-modos **PREPARAR** e **DRENAR** e declara **textualmente** que PREPARAR **não** emite `record_review` nem `UPDATE fsrs_cards`, e que PREPARAR **sempre** carimba `review_log` (com `kind` por gatilho).
3. **Deprecação (DoD-4b).** `.claude/commands/refrescar.md` é stub de redirecionamento para `/revisar` (sub-modo PREPARAR) **ou** movido para `history/legacy/` com nota. Nenhuma referência viva restante o trata como skill independente ativa (grep em AGENTE.md §7.3 atualizado).
4. **Degrau mecânico (DoD-7).** O contrato/skill especifica switches **auditáveis por contagem/regex** por degrau: faixas de parágrafos (D10:7-9, D8:5-6, D5:3-4, D2:1-2) + "toda sigla expandida na 1ª ocorrência" (D10/D8). Sem adjetivos subjetivos ("didático"/"excelente") como critério.
5. **AGENTE (DoD-10).** `AGENTE.md §1.2` não contém mais a string "Calibração pendente" e aponta para `core/contracts/revisao-calibrada-contract.md`. AGENTE §6 ganha a decisão "Revisão Calibrada (s096)"; §7.3 reflete a fusão.
6. **Craftsmanship gate.** Contrato segue o template de `core/contracts/` (espelha `reconcile`/`fsrs-management`: Papel, regras normativas, cláusulas). Texto pt-BR. Sem duplicar conteúdo de skill no workflow (contrato §7.2 do AGENTE). Wikilinks/`relates_to` ≤ referências reais.

## Scope
- **CRIAR** `core/contracts/revisao-calibrada-contract.md`: escala 1-10, fontes/precedência (§4.3), regra de divergência (§4.4), mapa nota→degrau (§4.6), fusão em sub-modos, **Invariantes A e B**, pseudocódigo `infer_nota` (§7.3), anti-circularidade (§7.6), degradação graciosa (§7.7), decisões das 6 questões abertas (propostas-semente).
- **EDITAR** `.claude/commands/revisar.md`: enquadrar Camadas 0/1/2 dentro de PREPARAR/DRENAR; adicionar parâmetro `dificuldade` + os dois propósitos (amplo/direcionado); Invariante B (carimbo obrigatório, `kind` por gatilho); apontar `tools/day_plan.py --difficulty` para resolver a nota.
- **EDITAR** `.claude/commands/refrescar.md`: deprecar (stub → `/revisar` PREPARAR).
- **EDITAR** `AGENTE.md`: §1.2 (remover "Calibração pendente" + ponteiro ao contrato), §6 (nova decisão), §7.3 (tabela de skills).

## Anti-scope
- Qualquer código novo (Partes 1-3 já entregaram). Esta parte é **só documentação normativa**.
- Reescrever `forgetting-curve-contract.md` ou `cronograma-contract.md` (apenas referenciar; relação de consumo).
- Gerar aulas-base automaticamente (Tier-3, não-objetivo do PRD).
- Ratificar o contrato (fica `pending-ratification` até o usuário validar em uso).

## Technical Decisions
- **Contrato lateral, não reescrever o PRD.** O PRD vira a fonte; o contrato é a versão normativa enxuta em `core/contracts/` (consistente com `reconcile`/`fsrs-management`). Trade-off: alguma duplicação PRD↔contrato, aceita (PRD = histórico/raciocínio; contrato = norma viva).
- **Stub vs legacy para `/refrescar`.** Stub de redirecionamento (preserva muscle-memory de quem digita `/refrescar`) — melhor que mover para legacy, dado que o comando ainda existe na cabeça do usuário.
- **DoD-7 auditável por proxies mecânicos** (parágrafos/sigla), não por juízo — alinhado ao §0.5 do PRD (conserta "DoD subjetivo").

## Applicable Patterns
- `agent-workflow-protocol.md` — estrutura de skills/contratos; boot/closure.
- Template de `core/contracts/*.md` (frontmatter, cláusulas normativas, Papel).
- `clinical-summary-format.md` **não** se aplica (contrato ≠ resumo); contratos podem usar tabelas.

## Risks
- **Erosão da barreira FSRS na prosa da fusão** (maior risco do PRD). Mitigação: Invariante A textual + o teste da Parte 3 (DoD-8) como respaldo executável.
- **Skill inchada** (revisar.md já é grande). Mitigação: enquadrar Camadas existentes nos sub-modos sem reescrever; delegar a norma ao contrato (não duplicar).
- **Drift contrato↔código** (pseudocódigo `infer_nota` diverge da Parte 2). Mitigação: contrato cita a função como SSOT em `day_plan.py`, não recopia a implementação.

## Dependencies
- `.vibeflow/specs/revisao-calibrada-part-1-fundacao-dados.md`
- `.vibeflow/specs/revisao-calibrada-part-2-inferencia.md`
- `.vibeflow/specs/revisao-calibrada-part-3-barreiras.md`
