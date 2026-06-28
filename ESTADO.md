---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, handoff-contract, estado-contract]
---

# ESTADO — MedHub

*Atualizado: 2026-06-28 ~02:30 (sessão 096) | Ferramenta: Claude Code (Opus 4.8)*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) → [`HANDOFF.md`](HANDOFF.md) (operacional curto) primeiro. Este arquivo é o snapshot **macro** (metas, indicador, marcos). Estrutura normatizada por [`core/contracts/estado-contract.md`](core/contracts/estado-contract.md).

---

## Metas

> **Plano atualizado no `Dashboard EMED 2026` (reconcile s084):** ramp mensal de questões 3.000 (mai) → **17.000 (dez/2026)** [3000·4500·6250·8000·10000·12500·15000·17000]; investimento R$ 2.940 → R$ 4.410 (R$ 210/mês). **Reconcile db↔dashboard: batem por área e no total (3.457 = 3.457, 0 divergência).** *(Supersede a antiga "Meta Final 23.000" — confirmar com o usuário se o stretch de 23k permanece.)*

- **Marco ENAMED (prioridade):** **meta-prova recalibrada para 10.000** (decisão s093, ultraplan s094) — 12.000 vira **teto/stretch**. ⚙️ **Gatilho de recalibração em S13 (~12/07):** acúmulo ≥5.600 → volta a 12.000; <5.200 → confirma 10.000. Faltam **5.888 p/ 10k em ~77 dias** (S11→13/09). **Ritmo: ciclo 3 dias sprint + 1 folga + simulado dominical**, ~90-100q nos dias de conteúdo. **14 simulados × 100q** (1/domingo; **11 pré-ENAMED = 1.100q**, 3 pós rumo a UERJ/USP). ✅ `performance.py` corrigido na s093 (ramp 4.500→17.000; bug fechado).
- **Plano de fim de ano:** 17.000 questões até 12/2026 (dashboard).
- **Custo/Q atual:** **R$ 0,91** (jun/2026, acumulado = investimento ÷ questões), em queda; alvo no fim do plano ≈ R$ 0,26.
- **Indicador Atual:** **4.112** — **41% da meta-prova (10.000)** · 34% do teto (12.000). **s096 = engenharia + revisão (sem questões novas):** implementou o **PRD de Revisão Calibrada** (4 partes, 63 testes) + revisou **32 cards** (drenou os 31 vencidos) + criou o resumo gold de **ectópica**. Perf. geral 79,5%. Meta jun 4.500: déficit 388 em 3 dias (~129/dia).
- **Performance Geral:** ~79% (`sessoes_bulk`). Fracos no dashboard: **Hepato 57% · Dermato 67% · Cardiologia/Otorrino 68% · Hemato 74%**. **Gargalo principal = EXECUÇÃO DE PROVA, não conteúdo** — default-to-C, fechamento precoce, **não fechar a conduta** (reconfirmado na s094: pé diabético 4/4 erros no eixo cirúrgico-vascular; exame lido por dado parcial — LCR → PaCO₂). Exceção s094: **lacuna de conteúdo real** em Ácido-Base (26%, tema de iniciante destravado via aula).
- **Contadores:** **52 resumos** em `resumos/` (+ectópica gold) · **364 erros** em `ipub.db` · **~408 cards ativos** (#609 último; #104 aposentado) · **taxonomia `UNIQUE(area,tema)` + colunas `dificuldade*`**
- **Cronograma (SSOT `Cronograma.pdf`):** **sync F1-F4 LIVE (s095)** — derivador `tools/cronograma.py` + `core/cronograma/grade.json` (30 sem · 352 tasks · 10218q). Semana 10 ✓ FECHADA. **Próxima = Semana 11** (conteúdo); calendário nominal S13 (~2 sem atrás). Frente **PRD de Revisão Calibrada** — **IMPLEMENTADO na s096** (4 partes; contrato `core/contracts/revisao-calibrada-contract.md`; 63 testes verdes).

---

## Estado por frente (macro)

- **Volume & Metas:** **4.112 / 10.000 meta-prova (41%)** [teto 12.000]; **+126 na s094** (fecha a Semana 10). Perf. geral **79,4%**. Cluster fraco (volume + %): Hepato, Dermato, Otorrino; **0q: Ortopedia, Oftalmo**. **Gargalo nº1 = execução de prova** (bug nº1: não fechar a conduta / exame lido por dado parcial); exceção s094 = lacuna real de conteúdo em Ácido-Base (26%, tema de iniciante).
- **Conteúdo:** **51 resumos** (+4 na s094: Diabetes Comp. Crônicas, Distúrbios Ácido-Base, Pneumo Intensiva, Hepatites Virais — os 2 de Nefro/Pneumo no novo **registro onboarding fundacional**). **Gaps:** reescrever `TCE.md` + `Sistemas de Informação em Saúde.md`; ectópica/icterícia neonatal (só andaime). PDFs EMED p/ aula-base mantidos (gitignored).
- **Erros & Cards:** **364 erros; ~410 cards ativos (41 andaimes)** (#609 último). **21 flashcards da s094 forjados na s095** (#589-609, 5 temas, eixo bug nº1). Pipeline `insert_questao.py` (+ `insert_card_base.py` andaime); taxonomia `UNIQUE(area,tema)`. Backlog FSRS: #554-609 + vencidos.
- **FSRS:** backlog grande — mas a **curva finalmente comeu na s084 (35/50 revisados)**. `/refrescar` (dormente) + `/revisar` atacam o backlog. **Andaime validado em tempo real:** Hemostasia destravou após 3 cards-base. Clusters frios andaimados: Hemostasia (fatores), Cardiopatias (T4F/shunt).
- **Infraestrutura — NOVA capacidade (s083): gestão da curva de esquecimento** — `review_log` (SSOT do tempo-de-revisão) + radar de dormência (`review_radar.py`) + `/refrescar` (`dormant_refresh.py`, **não toca o FSRS**) + **boot proativo** "Plano do Dia" (`day_plan.py`, AGENTE §2 passo 4) + **autonomia codificada** (AGENTE §1.1) + contrato `core/contracts/forgetting-curve-contract.md`. Mantém: cards de altura graduada (s082), governança de evidência (s076), Camada 2 do `/revisar` (s078). **5 padrões metacognitivos vivos** (+ palpite-abandonado-por-palavra). **Tier-3 (schema de altura) pendente.** **🆕 s094 — 2 frentes de método (aprovadas, a implementar):** (1) **Revisão Calibrada** (PRD `docs/plans/s094-revisao-calibrada-PRD.md`) — escala 1-10 calibra a descompressão, **aglutina `/revisar` + `/refrescar`**, integra cronograma + `/performance`; memória `project_revisao_calibrada`; (2) **Registro onboarding fundacional** p/ temas de iniciante; memória `feedback_registro_onboarding_iniciante`. **🆕 s095 — sync do cronograma LIVE (F1-F4):** derivador único `tools/cronograma.py` (read-only) + `core/cronograma/grade.json` versionado + `--radar` (cobertura × performance) + `day_plan.py` lê a grade (conteúdo×calendário, 2 ritmos) + contrato `core/contracts/cronograma-contract.md` + skill `/cronograma` + reconcile W5-W7. **🆕 s096 — Revisão Calibrada IMPLEMENTADA (frente A):** schema `dificuldade*` + `db.set/get_dificuldade` + `infer_nota()` (`day_plan --difficulty`, read-only) + fusão `/revisar` (sub-modos PREPARAR/DRENAR, Invariantes A/B) + `/refrescar` deprecado + contrato `revisao-calibrada-contract.md` (pending-ratification) + 4 specs vibeflow + **63 testes verdes**; `_find_resumo` corrigido (indexa stem). **Política de cards: teto 30/dia (agendados + 15 backlog)** (`feedback_politica_cards_diaria`). Modelo FSRS auditado: agendados (119, têm due) × novos (290, pilha sem due, entram por `--new-limit`).

---

## Próximos passos

> **🏃 MODO SPRINT QUESTION-FIRST (s078 → ~13/07/2026):** atrasado → estudo só por **questões + flashcards, SEM apostila corrida**. Exceção produtiva: **refresh dirigido do tema ANTES de cada bloco** (`/revisar` Camada 0 — leitura calibrada ao nível do estudante). Meta **≥100 questões/dia + ≥20 flashcards/dia**. **Não criar resumo completo** de tópico neste período. Detalhe: [[project_sprint_questoes_focado]] e [[cards-altura-graduada]] na memória.

Ver [`ROADMAP.md`](ROADMAP.md). Prioridades guiadas pelo cronograma (SSOT: `Cronograma de Reta Final.xlsx` no Drive):

1. **Abertura da próxima:** começa com **flashcards** (17 cards operacionais da s086 vencem cedo no FSRS) → **≥100 questões**. Aula-base + refresh Camada 0 antes de cada bloco.
2. **PRIORIDADE ESTRATÉGICA — execução de prova:** o gargalo migrou de conteúdo para processo de resolução. Treinar o **ritual anti-vazamento** (default-to-C + fechamento precoce) via [`PLAYBOOK_EXECUCAO_PROVA.md`](PLAYBOOK_EXECUCAO_PROVA.md). Maior alavanca da preparação. (bug nº 1c segue ativo; default-to-C é o novo sub-padrão dominante.)
3. **Aulas-base = CONTRATO** (AGENTE §1.2): cunhar aula "escada de degraus" antes de cada bloco novo; calibrar descompressão para pontos operacionais que a banca cobra.
4. **Gaps de resumo:** `Diabetes - Complicações Crônicas`; candidatos: ectópica, icterícia neonatal (só andaime). PDFs do EMED agora MANTIDOS (gitignored) p/ RAG — GO/Gastro/Dermato/Pediatria despejados.
5. **Revisão Calibrada — IMPLEMENTADA (s096):** schema + `infer_nota` + fusão `/revisar` + contrato + 63 testes. Resta **ratificar o contrato** após o 1º uso real e **integrar `day_plan --difficulty`** na abertura de task do boot. **Pendentes:** Tier-3 (schema de altura), limpeza `[bulk]`/`Geral` da taxonomia, re-drill dos bug-nº1 (#70 reincidiu na s096), sessão dedicada de Cirurgia, integrar `/schedule` no calendário.

> Detalhe operacional e próximo passo imediato: [`HANDOFF.md`](HANDOFF.md). Histórico completo: [`history/INDEX.md`](history/INDEX.md).

---

## Repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao fechar sessão: atualizar `HANDOFF.md` (sempre) e `ESTADO.md` (se o macro mudou) + registrar em `history/`. Ver `AGENTE.md §3`.*
