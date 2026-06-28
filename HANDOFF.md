# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-27 22:17 — **s094: fecha a Semana 10 (5 tasks restantes; 11/11) + 4 resumos + frente Revisão Calibrada (PRD)**. Dia 27/06 = **126q/87 (69%)**: Meningites Rev 50/35 · Ácido-Base 19/5 · Pneumo Int. 15/12 · Diabetes Comp.Crônicas 17/13 · Hepatites 25/22. **S10 FECHADA (273q).** 4 resumos novos (2 no registro "onboarding fundacional"). Acumulado **4.112 (41% da meta-prova 10k).***

## ▶ Próximo passo imediato — s095
**A) Cunhar os flashcards do dia** (Meningites + Ácido-Base + Pneumo + Diabetes + Hepatites — combinado p/ s095; ainda não cunhados).
**B) Semana 11** do cronograma (S10 fechada → avança).
**C) Engenharia — F1 do sync** (`tools/cronograma.py` + `core/cronograma/grade.json`, ainda inexistentes): agora também **desbloqueia o PRD de Revisão Calibrada** → F2 radar → F3 day_plan → F4 contrato. Integrar `/schedule` no calendário (pedido s093).
**D) FSRS:** drenar #554-588 + vencidos (`/revisar`).

## Frentes novas (s094 — aprovadas, a implementar)
- **Revisão Calibrada** (`docs/plans/s094-revisao-calibrada-PRD.md`): escala de dificuldade do tema **1-10** calibra a descompressão (10=onboarding, ref. resumo DM; comprime se fácil/quente/baixa-prevalência); **aglutina `/revisar` + `/refrescar`** numa competência única (exercícios=ampla / flashcards=direcionada; refresh não toca FSRS); integra cronograma + `/performance` (área fraca → nota maior → mais descomprimido). 6 questões abertas APROVADAS. Memória `project_revisao_calibrada`.
- **Registro onboarding fundacional**: temas onde o usuário é iniciante — sigla na 1ª aparição, cada nuance/parâmetro explicado, foco vida médica (aplicado a Ácido-Base + Pneumo). Memória `feedback_registro_onboarding_iniciante`.

## Plano da sprint (s093)
**Meta-prova 10.000 + gatilho S13 (~12/07):** ≥5.600 → 12k; <5.200 → 10k. **Ritmo 3+1 + simulado dominical** (~90-100q/dia ON); **14 simulados × 100q** (11 pré-ENAMED).

## Estado por frente
- **Volume & Metas:** **4.112 / 10.000 meta-prova (41%)** [teto 12k]. Perf. geral **79,4%**. Fracos = gaps de volume (Hepato · Otorrino · Dermato; 0q: Ortopedia, Oftalmo). Dia puxado p/ baixo por Ácido-Base 26% (tema NOVO de iniciante, destravado via aula).
- **Cronograma (SSOT `Cronograma.pdf`, 28 sem):** **S10 FECHADA — 11/11 tasks (273q).** Próxima = **S11**. Calendário na S13; conteúdo na S10 (~3 sem atrás). Grade: `scratchpad/crono_dados.json`.
- **Conteúdo:** **51 resumos** (+4 na s094: Diabetes Comp.Crônicas, Ácido-Base, Pneumo Int., Hepatites; 2 em registro onboarding). Gaps: reescrever `TCE.md` + `Sistemas de Informação em Saúde.md`; ectópica.
- **Erros & Cards:** 359 erros · ~389 cards (#588 último). **Flashcards do dia PENDENTES (s095).** FSRS: backlog #554-588 + vencidos.

## Última sessão de questões — s094 (estudo+registro 27/06)
- 5 blocos / **126q/87 (69%)**. **Eixo = bug nº1 / "não fechar a verificação/conduta"**: LCR por dado parcial (glicorraquia relativa) migrou p/ a PaCO₂ (Ácido-Base); pé diabético = **4/4 erros** no eixo cirúrgico-vascular (foco infeccioso>exame; revascularizar antes de amputar); HBV ocupacional/pós-exposição. 2 não-erros em Meningites (gabaritos ruins).

## Pendências ativas
- Gaps de cobertura de aula (candidatos a card/andaime): **pé diabético cirúrgico-vascular**; **HBV ocupacional/pós-exposição**.
- Carry-over s093: sessão dedicada de Cirurgia; integrar `/schedule` na gestão de calendário.

---
*Histórico: history/INDEX.md · Macro: ESTADO.md · Planos: docs/plans/s094-revisao-calibrada-PRD.md · s094-ultraplan.md*
