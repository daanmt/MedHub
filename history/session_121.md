# Session 121 — Drenagem FSRS + auditoria de cards + engenharia vibeflow (linter de auto-suficiencia + telemetria de fila) + reforja de 27 cards

**Data:** 2026-07-15
**Ferramenta:** Claude Code (Opus 4.8)
**Continuidade:** Sessão 120 (S13 conversacional)
**Natureza:** mista — estudo (drenagem FSRS) + engenharia (2 features vibeflow) + curadoria (reforja de cards)

---

## O que foi feito

**1. Drenagem FSRS conversacional (dívida vencida → 0):**
- Drenados os **26 vencidos** (22 atrasados + 4 hoje) em 5 blocos de 5. Distribuição: 17x nota 4 · 6x nota 3 · 1x nota 2 · 2x nota 1.
- Furos: #238 (AAST renal — lesão vascular = grau IV), #251 (IGIV só hemólise isoimune), #19 (asma: pior parâmetro manda — faceta do bug nº1). Re-drill mnemônico dos 3 (não tocou FSRS) — reproduzidos a frio.
- Feedback do usuário: **agente decide a nota e grava direto, sem pausa de confirmação** (usuário corrige se quiser). Ajuste da janela de override do /revisar.

**2. Auditoria ampla do baralho (pergunta do usuário "como estão os cards afinal?"):**
- Estado: 596 ativos = **425 pool** (state=0, nunca introduzidos) + 171 em revisão + 0 dívida. 66 de 105 temas com card nunca drilados. Pool concentrado: Cirurgia 82, Pediatria 57, GO 78. Idade: 235 de junho (exhaust do sprint question-first), 155 de julho.
- Achado-chave: o pool é **dívida de consolidação** sobre temas JÁ estudados, não temas futuros. **Imunizações (mais fraca, D10) tem 18 cards parados no pool.**
- Meta-achado: o linter sintático era **cego ao semântico** (99,6% OK), o que deixou passar os cards criptográficos.

**3. Engenharia vibeflow (discover → gen-spec → implement → audit, 2 features):**
- **Part 1 — `tools/card_self_sufficiency.py`:** check WARN de auto-suficiência no `auto_check` (bloco 8, warn-first), 3 anti-padrões (opção-anafórico / deítico / pct-fake). 14 testes. **Audit PASS.** Descobriu ~30% de falso-positivo nos regex crus do audit (prosa clínica reusa "opção/alternativa/acima") → **apertado com guarda de contexto anafórico** (aprovado pelo usuário): 36 achados ruidosos → 24 reais.
- **Part 2 — telemetria de fila no `day_plan`:** `telemetria_fila()` separa **pool** (nunca introduzidos) de **dívida** (vencidos), matando o rótulo enganoso "backlog". `render`/`render_handoff_block` + linha de sinais do recomendador. 3 testes. **Audit PASS.**

**4. M1 — reforja de conteúdo (curadoria, fora do pipeline de código):**
- **27 cards reforjados** via `recurate_cards.py` (backup + dry-run sempre; card_version++, FSRS preservado): 5 do piloto SUS (811-815) + 22 do worklist do linter.
- Opção-anafórico → recall clínico direto + armadilhas-meta ("rotular V/F") trocadas pelo distrator clínico real. Deítico → vinhetas destravadas do "neste caso". #813 (equidade×igualdade) resolvido com a nuance honesta. #243 ganhou a 2ª metade que faltava (ABO).
- **Linter pós-reforja: 0 achados — corpus auto-suficiente.** Zero regressão sintática.

## Estratégia definida — "matar os cards" (M1-M4)

- **M1 (feito):** reforjar os não-auto-suficientes antes de introduzir.
- **M2:** intake priorizado **fraco-primeiro** (não FIFO) — Imunizações 18 primeiro (casado com a task **Imunizações-Revisão da S13**), depois clusters de Cirurgia/GO.
- **M3:** cadência ~20 novos/dia via `/revisar DRENAR --new-limit 20 --area <fraca>` (celular). Pool 425 → ~3-4 semanas.
- **M4:** estancar o crescimento — card fresco entra em ≤2 dias (não vira pool de junho).
- **Princípio (validado pelo usuário):** card entra colado no tema sendo estudado.

## Artefatos criados/modificados

- **Novos (código):** `tools/card_self_sufficiency.py`, `tools/test_card_self_sufficiency.py`, `tools/test_day_plan_telemetria.py`.
- **Modificados (código):** `tools/auto_check.py` (bloco 8 + wire da suíte telemetria), `tools/day_plan.py` (`telemetria_fila` + relabel pool×dívida).
- **Vibeflow:** PRD + 2 specs + 2 audits (PASS) em `.vibeflow/`; pitfall do regex em `decisions.md`.
- **Cards (ipub.db, local):** 27 reforjados (811-815, 5, 42, 52, 120, 155, 159, 175, 185, 229, 243, 253, 413, 682, 694, 743, 746, 750, 791, 800, 809, 824, 825). FSRS: 26 vencidos gravados.

## Decisões tomadas

- **Regex de linter semântico over-matcheia prosa clínica** → apertar com guarda de contexto anafórico; rodar contra o corpus real ANTES de fechar a severidade (registrado em `decisions.md`).
- **/revisar: agente grava a nota direto, sem pausa de confirmação** (usuário corrige se quiser).
- **due-at-creation NÃO é bug, é telemetria enganosa** — v0 conserta o rótulo (pool×dívida), sem cirurgia no `due` (F próprio se o usuário quiser depois).
- **Reforja > aposentar** confirmado (curar-cards): 27 cards com erro rico devolvidos ao elo, 0 aposentados.

## Próximo passo

M2: liberar intake das 18 de Imunizações (limpas), casado com a task Imunizações-Revisão D10 da S13 (aula → questões → drenar as 18 no mesmo dia = loop fechado).
