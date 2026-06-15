# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-15 — s083. **Zero de questões quebrado (75q)** + construída ponta-a-ponta a **capacidade de gestão da curva de esquecimento (F1-F6)**: radar de dormência, `/refrescar`, boot proativo, dedup da taxonomia, contrato. **Próximo: estrear o boot proativo + fechar o bloco 3 (Nefro, 40q pendente).***

## ▶ Próximo passo imediato — abertura de amanhã
1. **Estrear o boot proativo (§2 passo 4):** rodar `python tools/day_plan.py` e **liderar com o plano decidido** (não menu). Hoje aponta: refrescar Icterícia e Sepse Neonatal (60d), volume 3391 (faltam ~94q/dia), FSRS 27+14+167.
2. **1º `/refrescar` real** — `dormant_refresh.py --pick` → narrar inline → `--stamp`. Não toca o FSRS.
3. **Fechar o Bloco 3 — Nefro (DRC + LRA, 40q)** que ficou pendente (micro-refresh de DRC já entregue na s083). VOLUME segue o gargalo (~94q/dia p/ 13/09).
4. Re-testar os 4 refeitos da s081 (428/68/74/82) + escada de Cardiopatias via FSRS.

## Estado por frente
- **Volume & Metas:** 3.391/12.000 ENAMED (28,3%) — **+75 hoje** (zero quebrado após 3 sessões). Junho (8.000) não fecha; foco = ~94q/dia p/ 13/09. Bloco 3 (Nefro 40q) pendente.
- **Conteúdo:** 45 resumos. **`DITC.md` +§4 DMTC** (anti-U1-RNP, hierarquia de frequência) + 2 armadilhas. Gap real ativo: `Diabetes - Complicações Crônicas` e `Doença Renal Crônica` (stub).
- **Erros & Cards:** **+14 cards** na s083 (13 GO ids 446-458 + 1 DITC 459); ~260 ativos. 6 padrões metacognitivos em GO (gestante perdida 2×, ancoragem, regra-idade, ATA, palpite-abandonado, 2016×2025 banca-dependente).
- **FSRS:** backlog grande (167 novos + 41 vencidos) — quase nada revisado (curva não alimentada). `/revisar` cumpre o piso de cards/dia.
- **Infraestrutura — NOVA capacidade (F1-F6):** curva de esquecimento — `review_log` (SSOT tempo-revisão) + `/refrescar`/`dormant_refresh.py` + `review_radar.py` + boot proativo `day_plan.py` + **taxonomia deduplicada (126→86, `UNIQUE(area,tema)`)** + backfill (47 temas) + `core/contracts/forgetting-curve-contract.md` + **autonomia AGENTE §1.1**. Ver [[project_curva_esquecimento]].

## Última sessão — sessão 083
- Estudo: GO 54/41 (76%) + DITC 21/20 (95%) = 75/61 (81%); 14 cards; `DITC.md` ganhou DMTC. Bloco 3 Nefro não rodado.
- Feature F1-F6 planejada (3 Explore + 1 Plan agent, verificada contra o db) e executada+verificada: F4 destrutivo com backup-first/dry-run; 0 órfãos, filhos preservados, integrity ok.
- Drive "Extensivo EMED": acesso por ID ok, mas **enumeração por parentId falha** (não é só propagação) — investigar share. Apostilas = fonte; sugestões de flashcard ≠ cards automáticos.

## Pendências/observações ativas
- **Bloco 3 (Nefro, 40q)** pendente — fechar primeiro.
- **Tier-3** (schema formal de altura de card) e **limpeza `[bulk]`/`Geral`** da taxonomia seguem pendentes (fora de escopo do forgetting-curve v1).
- Drive: descobrir por que a árvore não enumera (tipo de compartilhamento).
- 4 padrões metacognitivos vivos + o 5º (palpite-abandonado-por-palavra) observado na s083.

---
*Histórico: history/INDEX.md · Snapshot macro: ESTADO.md · Curva: core/contracts/forgetting-curve-contract.md*
