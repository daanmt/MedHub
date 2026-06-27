# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-27 01:09 — **s093: avança a Semana 10 (T2+T3) + ULTRAPLAN s094 do cronograma**. Dia de estudo 26/06 = **147q** nas 6 primeiras tasks da S10 (s092 107 + s093 40). T2 Exantemáticas 18/16 + T3 Cir. Infantil III 22/19 = 40q/87,5% (s093). 5 cards (#584-588) + 2 resumos. Reconcile de drift fechado. `performance.py` corrigido. **Meta recalibrada: 10.000 + gatilho S13.** Acumulado **3.986 (40% da meta-prova).***

## ▶ Próximo passo imediato — s094
**A) Estudo — matar o RESTO da Semana 10** (faltam 5 das 11 tasks, ~126q), nesta ordem:
1. **Meningites (Revisão)** ← começar aqui (revisão → aula comprimida).
2. Diabetes Mellitus - Complicações Crônicas (Teoria) — *gap de resumo: criar*.
3. Distúrbios Ácido-Base (Teoria).
4. Pneumologia Intensiva (Teoria I).
5. **Hepatites Virais (Teoria)** — 🔴 ataca **Hepato** (área mais fraca). Teoria nova → aula descomprimida.

**B) Engenharia — Fase 1 do sync** (`docs/plans/s094-ultraplan.md`): `tools/cronograma.py` + `core/cronograma/grade.json` (funde os scripts do scratch; `AREA_PDF_TO_CANON`; subcomandos). → F2 radar → F3 day_plan → F4 contrato. **Integrar `/schedule` (routines)** ao sistema p/ gestão proativa do calendário (metas diárias/semanais/mensais, tema do dia, gatilhos) — pedido s093.

**C) Análise — Sessão dedicada de Cirurgia:** varrer o eixo cirúrgico (resumos + PDFs Ortop/Otorrino/outros na pasta) → avaliar ajustes no cronograma.

**D) FSRS:** drenar #554-588 + vencidos (`/revisar`).

## Plano da sprint (decidido s093)
- **Meta-prova 10.000 + gatilho S13 (~12/07):** ≥5.600 → volta a 12k; <5.200 → confirma 10k. (Routine `/schedule` criada p/ lembrar.)
- **Ritmo: 3 dias sprint + 1 folga + simulado dominical** (~90-100q nos dias ON → ~10k no ENAMED).
- **14 simulados × 100q** (1/domingo; 11 pré-ENAMED = 1.100q) — volume extra + hábito + cobre órfãs no mix.
- **Arritmia (FA/Flutter/PCR) antecipada → ~S18-S21.** Fonte cronograma = PDF v1.0.

## Estado por frente
- **Volume & Metas:** **3.986 / 10.000 meta-prova (40%)** [teto 12k]. Cronograma S11-S28 = 6.689q/222 tasks (1,62× compressão até ENAMED 13/09). Ritmo real ~31/dia (média jun) → alvo ~90-100/dia nos dias ON. Fracos = gaps de **volume** (Hepato 14q · Otorrino 19q · Dermato 24q; 0q: Ortopedia, Oftalmo).
- **Cronograma (SSOT `Cronograma.pdf`, 28 sem):** **S10 EM CURSO — 6/11 tasks (147q); faltam 5 (~126q).** Calendário na S13; conteúdo na S10 (~3 sem atrás). S11 só após fechar a S10. Grade em `scratchpad/crono_dados.json`.
- **Conteúdo:** 48 resumos. Gaps: Diabetes Comp. Crônicas (criar p/ S10), ectópica; reescrever `TCE.md` e `Sistemas de Informação em Saúde.md`.
- **Erros & Cards:** 359 erros · ~389 cards (5 novos s093). FSRS: backlog #554-588 + vencidos.

## Última sessão de questões — s093 (estudo 26/06; registrada 27/06 01:09)
- T2 Exantemáticas + T3 Cir. Infantil III = **40q/87,5%**. Eixo = **bug nº1** (veneno na cauda Q1/Q5 + ancoragem em achado isolado Q3/Q4 + enunciado negativo Q2 = 4ª reincidência).

## Pendências ativas
- Ultraplan s094 (`docs/plans/s094-ultraplan.md`) → F1-F4 + sessão Cirurgia + integrar `/schedule` na gestão de calendário.
- ⚠️ **Convenção nova (s093): registros de sessão levam DATA + HORA** (evita o borrão que inflou "26/06" com a s091). Atualizar `registrar-sessao.md`.
- Limpeza de rótulos sujos `sessoes_bulk` (`GO`/`Obstetrícia` mojibake) = fork destrutivo (normalizar só na leitura — W4).

---
*Histórico: history/INDEX.md · Macro: ESTADO.md · Plano da frente: docs/plans/s094-ultraplan.md*
