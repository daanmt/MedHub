# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-04 — CAD/EHH + regeneração dos 87 cards órfãos + /revisar (sessão 076)*

## ▶ Próximo passo imediato (ao retomar)
1. **Re-fil dos temas `[bulk]`** (nova demanda da s076): ~80 cards mal-rotulados sob "[bulk] Cirurgia" (cardiopatias, iSGLT-2, HbA1c, epidemiologia, GO). Migração one-shot, backup-first → corrige o "Cirurgia due" inflado e o filtro por área do `/revisar`.
2. **Drenar fila FSRS:** 15 cards restantes da fila de 04/06 + 4 que voltam hoje (rating 1: bradicardia/adrenalina, taqui sinusal, incubação FA, extravasamento dengue) + novos por área fraca.
3. **Boot:** rodar o check de reconcile (`core/contracts/reconcile-contract.md`).

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
- **Push pendente:** commits locais s075 + s076; `main` sem upstream tracking — resolver no go.
- **Erro repetido vigiado (novo):** dengue — eixo de gravidade é **extravasamento plasmático**, não sangramento (#396 falhou); arritmias pediátricas (sinus vs TSV vs bradicardia).

---
*Histórico: history/INDEX.md · Snapshot macro: ESTADO.md*
