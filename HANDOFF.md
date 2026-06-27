# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-27 — **s093: fecha a Semana 10 (T2+T3) + ULTRAPLAN s094 do cronograma**. T2 Exantemáticas 18/16 + T3 Cir. Infantil III 22/19 = **40q/87,5%**. 5 cards (#584-588) + 2 resumos turbinados. Reconcile de drift fechado (6q na Pediatria T13; db = fonte fiel). `performance.py` corrigido. **Meta recalibrada: 10.000 + gatilho S13.** Acumulado **3.986 (40% da meta-prova).***

## ▶ Próximo passo imediato — s094
**Frente principal: implementar a Fase 1 do ultraplan** (`docs/plans/s094-ultraplan.md`; forks já decididos):
1. **F1 — `tools/cronograma.py` + `core/cronograma/grade.json`** (versionado): fundir os scripts do scratch (`crono_extract.py`+`cronograma_grade.py`); `AREA_PDF_TO_CANON`; subcomandos `--rebuild/--check/--json/--gap/--radar`. Validar S10=273q. → **F2 radar** → **F3 day_plan** (boot puxa semana+ritmos) → **F4 contrato** `cronograma-contract.md`.
2. **🆕 Sessão dedicada de Cirurgia:** varrer o eixo cirúrgico (resumos + PDFs Ortop/Otorrino/outros na pasta) → avaliar ajustes no cronograma.
3. **Conteúdo S11 (começa 29/06):** Med. de Família e Comunidade (Teoria I) + 12 tasks (412q). Calibrar aula por tipo.
4. **FSRS:** drenar #554-588 + vencidos (`/revisar`).

## Plano da sprint (decidido s093)
- **Meta-prova 10.000 + gatilho S13 (~12/07):** acúmulo ≥5.600 → 12k; <5.200 → confirma 10k. 12k = teto.
- **Ritmo: 3 dias sprint + 1 folga + simulado dominical** (~90-100q nos dias ON → ~10k no ENAMED).
- **14 simulados × 100q** (1/domingo; 11 pré-ENAMED = 1.100q) — volume extra + hábito + cobre órfãs no mix.
- **Arritmia (FA/Flutter/PCR) antecipada → ~S18-S21.** Órfãs (Oftalmo/Otorrino/Dermato/Ortop): via simulados, sem bloco dedicado. Fonte cronograma = PDF v1.0.

## Estado por frente
- **Volume & Metas:** **3.986 / 10.000 meta-prova (40%)** [teto 12k]. Cronograma S11-S28 = **6.689q/222 tasks** (1,62× compressão até ENAMED 13/09). Ritmo real junho ~31/dia → alvo ~90-100/dia nos dias ON. Fracos = gaps de **volume** (Hepato 14q · Otorrino 19q · Dermato 24q; 0q: Ortopedia, Oftalmo).
- **Cronograma (SSOT `Cronograma.pdf`, 28 sem):** S10 ✓. **S11 começa 29/06.** Calendário na S13; conteúdo na S10 (~3 sem atrás). Grade em `scratchpad/crono_dados.json`.
- **Conteúdo:** 48 resumos. Gaps: ectópica; reescrever `TCE.md` e `Sistemas de Informação em Saúde.md`.
- **Erros & Cards:** **359 erros · ~389 cards** (5 novos s093). FSRS: backlog #554-588 + vencidos.

## Última sessão de questões — s093 (27/06)
- T2 Exantemáticas + T3 Cir. Infantil III = **40q/87,5%**. Eixo = **bug nº1** (veneno na cauda Q1/Q5 + ancoragem em achado isolado Q3/Q4 + enunciado negativo Q2 = 4ª reincidência). Conteúdo intacto; gargalo é leitura/execução.

## Pendências ativas
- Ultraplan s094 (`docs/plans/s094-ultraplan.md`) → implementar F1-F4 + sessão de Cirurgia.
- Limpeza de rótulos sujos `sessoes_bulk` (`GO`/`Obstetrícia` mojibake) = fork destrutivo (normalizar só na leitura por ora — W4).
- Reescrever `Sistemas de Informação em Saúde.md` + `TCE.md`; resumo de ectópica.

---
*Histórico: history/INDEX.md · Macro: ESTADO.md · Plano da frente: docs/plans/s094-ultraplan.md*
