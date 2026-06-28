---
type: contract
layer: core
status: canonical
version: 1.0
relates_to: [fsrs-management-contract, reconcile-contract, AGENTE]
---

# Contrato de Gestão da Curva de Esquecimento (Forgetting Curve)
**Versão 1.0 | 2026-06-15 (sessão 083) — primeira instância**

> Documento normativo. Governa a gestão ativa da curva de esquecimento **no nível do TEMA** — o ritual diário de refresh de tema dormente, o registro de tempo-de-revisão (`review_log`) e o boot proativo. Complementa o FSRS (nível card, `fsrs-management-contract.md`); **não o substitui nem o toca**. Referenciado por: `AGENTE.md` (§1.1, §2 passo 4, §6), `.claude/commands/refrescar.md`.

---

## Papel

O FSRS agenda a revisão **de cada card**. Mas o estudante esquece **temas inteiros** que não vê há semanas — e passa a errar coisas simples (memória dormente). Faltava (a) a visão de dormência **por tema**, (b) um re-ensino narrativo que reidrate o tema (não só sondar cards) e (c) uma base fiel de "há quanto tempo não revejo X". Este contrato normatiza essa camada, **sem perturbar a fila FSRS**.

---

## Vocabulário

- **Dormência:** `dias_sem_revisar` de um tema = hoje − `max(review_log, fsrs_cards.last_review, taxonomia.ultima_revisao)`. Limiar `DORMENTE_DIAS = 21`.
- **Score de dormência:** `dias + (1−retrievability)·30 + vencidos·2` (retrievability ≈ `0.9^(dias/stability)`). Maior = mais frio. Calculado por `tools/review_radar.py`.
- **Refresh dormente:** re-ensino narrativo de 1 tema/dia, menos comprimido. ≠ `/revisar` (card-a-card).

---

## Fonte de seleção — radar

`tools/review_radar.py` (read-only) é o radar canônico: ranqueia temas por dormência cruzando `taxonomia_cronograma` × `flashcards` ativos × `fsrs_cards` × `review_log`. `--json` emite o ranking. O tema do dia sai do topo, filtrado por: **tem cards ativos**, não é `[bulk]`/`Geral`, **não foi refrescado na janela anti-repetição**.

---

## Refresh dormente diário (`/refrescar`)

Operado por `.claude/commands/refrescar.md` + `tools/dormant_refresh.py` (`--pick`/`--context`/`--stamp`).

- **Forma:** prosa clínica reconstrutiva (3-6 parágrafos) — mecanismo → conduta → armadilha + "o elo que você costuma quebrar aqui". Densidade Gold Standard (AGENTE §4), sem tabelas. Substrato: `app.engine.get_topic_context` (resumo + erros + RAG + weak_areas), com fallback de resumo por nome de arquivo.
- 🔴 **Fronteira dura — NÃO toca o FSRS:** nunca chama `record_review`/`insert_questao`/`insert_card_base`; não cunha card; não grava rating. O único write é `--stamp` → `review_log` (`kind=dormant_refresh`). A fila FSRS (`fsrs-management-contract.md`) permanece intacta.

---

## Timestamp de revisão (`review_log`)

- **SSOT** = tabela `review_log` (em `ipub.db`, local-only): `tema_id, resumo_path, kind, source, note, reviewed_at`. `kind ∈ {dormant_refresh, directed_review, resumo_read, backfill}`. Escrita única via `db.log_review`.
- **Leitura unificada:** `db.get_theme_last_review` une `review_log` + `fsrs_cards.last_review` + `taxonomia.ultima_revisao` (a mais recente vence).
- **Backfill (`tools/backfill_review_log.py`):** semeia 1 linha por tema a partir do **sinal real mais forte** (fsrs → taxonomia). **Nunca `CURRENT_TIMESTAMP`** — não falsifica a curva. Idempotente.
- **Espelho no frontmatter (`ultima_revisao`):** opcional, derivado do SSOT, escrito **organicamente** quando o agente toca o resumo. Sem migração em massa.

---

## Rotação por todos os temas

A janela anti-repetição (`dormant_refresh.REPETITION_WINDOW_DAYS`, default 7 dias) garante que, ao longo do tempo, **todos os temas com cards** passem pelo refresh — construindo a base fiel de tempo-desde-revisão. **Métrica de saúde:** % de temas com `review_log` (`kind=dormant_refresh`) nos últimos K dias, crescente.

---

## Boot proativo — Plano do Dia

`AGENTE.md §2 passo 4`: após o reconcile, `tools/day_plan.py` compõe (read-only) dormência × volume (vs ~94q/dia ENAMED) × fila FSRS × **cronograma**; o agente **lidera com um plano decidido** + propõe o passo. Consome (não duplica) o report FSRS que `reconcile`/`fsrs-management` já exigem no boot.

A **4ª fonte (cronograma, s095)** entra via `import cronograma` (não reparseia o PDF): `day_plan` mostra semana de **conteúdo** (ponteiro `Próxima = SNN`) vs nominal por data, temas previstos e **dois ritmos-alvo** (terminar a grade vs meta-prova). Governado por `cronograma-contract.md`; read-only, zero write no db.

---

## Autonomia

O agente decide o próximo passo e executa (AGENTE §1.1). Pausa só em fork real / **operação destrutiva sobre SSOT** / fronteira de PR / BLOCKING do reconcile. A dedup da taxonomia (s083) é o exemplo canônico de "pausa destrutiva": backup → dry-run → apply.

---

## Invariante anti-poluição

Identidade do tema = `(area, tema)`, com `UNIQUE INDEX ux_taxonomia_area_tema`. `insert_questao.py` e `insert_card_base.py` resolvem por `(area, tema)`. A s083 colapsou 22 grupos duplicados via `tools/dedup_taxonomia.py` (merge MAX — `taxonomia.questoes_realizadas` é legado, **não** o SSOT de volume, que é `sessoes_bulk`).

---

## Fora de escopo (v1.0)

- Schema formal de **altura de card** (ordinal + `prereq_de`) — Tier-3 já pendente (AGENTE §6 "Cards de altura graduada").
- Rotação **agendada** (cron) e UI da curva de esquecimento.
- Limpeza das linhas `[bulk]`/`Geral` da taxonomia (não quebram nada; item separado).

---

## Changelog

- **v1.0 (2026-06-15, s083):** primeira instância. F1 `review_log` + helpers `db.py`; F2 `/refrescar` + `dormant_refresh.py`; F3 boot proativo + `day_plan.py`; F4 dedup + `UNIQUE(area,tema)`; F5 backfill. Adaptado dos princípios de `ai-eng` (grounding) + do irmão `agente-daktus-content` (contract-driven).
