# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-04 — s076: CAD/EHH + 87 cards regenerados + camada de evidência. **Próximo: retomar `/revisar` (parados em 20/30).***

## ▶ Próximo passo imediato (ao retomar) — RETOMAR `/revisar`
1. **Continuar a revisão de onde paramos (estávamos em 20/30).** Fila ≈ **17 cards**: 7 que caíram hoje (re-fixar) + 10 novos de outras áreas (Cirurgia 6, Infecto 2, Obstetrícia 1, Pneumo 1). Modo: lotes de 5, auto-rating, **micro-resumo ao errar** (feedback s076 — ativo).
2. **Focar os clusters fracos de 04/06:** ⚠️ **PALS/arritmias pediátricas** (taqui sinusal × TSV × bradicardia→adrenalina), ⚠️ **Febre Amarela** (4/5 caíram: vetores, vírus, Faget, viremia), ⚠️ **dengue = extravasamento** (não sangramento). Cards que voltaram p/ hoje: #1, #5, #389, #396, #401, #403, #404.
3. **Evidência agora LIVE:** `pubmedmcp` conecta neste boot → usar `/pesquisar-evidencia` se um card for banca-dependente/contestável (ex.: colestase SBP×INT, metas SBD×ADA).
4. **Antes:** check de reconcile rápido (`core/contracts/reconcile-contract.md`).

## Estado por frente
- **Volume & Metas:** 3.244/12.000 ENAMED (80,2%); ~86q/dia para o alvo (13-09). Planilha não reconciliada nesta sessão (sem novo lançamento no Drive).
- **Conteúdo:** 45 resumos. `Compl. Agudas` turbinado (+4 armadilhas CAD/EHH). **Gap ativo:** `Diabetes - Complicações Crônicas`.
- **Erros & Cards:** 233 erros (+7 CAD/EHH); 338 cards qualitativos.
- **FSRS:** **fila 100% qualitativa — 0 heurísticos** (87 órfãos regenerados em 4 ondas). Backlog state=0 segue a drenar. Watched Dengue C/D **resolvido**.
- **Infraestrutura:** `cards_regen_queue.py` critério corrigido; `estilo-flashcard.md §Backfill` reativada. **Nova camada: governança de evidência** (`core/contracts/evidence-governance.md` + `/pesquisar-evidencia` + subagente `evidence-researcher` + `pubmedmcp`). `pubmedmcp` conecta no **próximo boot** (restart do Claude Code).

## Última sessão — sessão 076
- CAD/EHH: 34q/27a registradas (3.244); 7 erros → 7 cards qualitativos (406-412) + resumo turbinado; 4/7 erros foram sobre armadilhas já documentadas (gargalo = aplicação/leitura, não conhecimento).
- **87 cards heurísticos órfãos regenerados qualitativamente** (4 ondas, `update_flashcard_fields`, FSRS preservado) + 1 duplicata (#276) aposentada → 0 heurísticos ativos.
- Causa-raiz do slip-through achada e corrigida (filtro órfão da bankruptcy s075).
- `/revisar` 20 cards: **fantasma Dengue C/D caiu** ✅; pontos fracos novos = arritmias pediátricas (PALS) + Febre Amarela (4/5 caíram).
- **Camada de governança de evidência** portada/adaptada do irmão (contrato + skill `/pesquisar-evidencia` + subagente + `pubmedmcp`): hierarquia BR>INT>consenso + lente da banca + veredito `DESATUALIZADO` (banca×evidência → 🔴 banca-dependente).

## Pendências/observações ativas
- **Demanda em espera (despriorizada p/ a revisão):** re-fil dos temas `[bulk]` — ~80 cards mal-rotulados sob "[bulk] Cirurgia" (cardiopatias/iSGLT-2/HbA1c/epidemiologia/GO); migração one-shot backup-first → corrige o "Cirurgia due" inflado.
- **Erro repetido vigiado:** dengue = **extravasamento plasmático**, não sangramento (#396); arritmias pediátricas (sinusal × TSV × bradicardia). Git: tudo pushed até `d3706cb`.

---
*Histórico: history/INDEX.md · Snapshot macro: ESTADO.md*
