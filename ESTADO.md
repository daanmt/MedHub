---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, handoff-contract, estado-contract]
---

# ESTADO — MedHub

*Atualizado: 2026-06-27 01:09 (sessão 093) | Ferramenta: Claude Code (Opus 4.8)*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) → [`HANDOFF.md`](HANDOFF.md) (operacional curto) primeiro. Este arquivo é o snapshot **macro** (metas, indicador, marcos). Estrutura normatizada por [`core/contracts/estado-contract.md`](core/contracts/estado-contract.md).

---

## Metas

> **Plano atualizado no `Dashboard EMED 2026` (reconcile s084):** ramp mensal de questões 3.000 (mai) → **17.000 (dez/2026)** [3000·4500·6250·8000·10000·12500·15000·17000]; investimento R$ 2.940 → R$ 4.410 (R$ 210/mês). **Reconcile db↔dashboard: batem por área e no total (3.457 = 3.457, 0 divergência).** *(Supersede a antiga "Meta Final 23.000" — confirmar com o usuário se o stretch de 23k permanece.)*

- **Marco ENAMED (prioridade):** **meta-prova recalibrada para 10.000** (decisão s093, ultraplan s094) — 12.000 vira **teto/stretch**. ⚙️ **Gatilho de recalibração em S13 (~12/07):** acúmulo ≥5.600 → volta a 12.000; <5.200 → confirma 10.000. Faltam **6.014 p/ 10k em 77 dias** (S11→13/09). **Ritmo: ciclo 3 dias sprint + 1 folga + simulado dominical**, ~90-100q nos dias de conteúdo. **14 simulados × 100q** (1/domingo; **11 pré-ENAMED = 1.100q**, 3 pós rumo a UERJ/USP). ✅ `performance.py` corrigido na s093 (ramp 4.500→17.000; bug fechado).
- **Plano de fim de ano:** 17.000 questões até 12/2026 (dashboard).
- **Custo/Q atual:** **R$ 0,91** (jun/2026, acumulado = investimento ÷ questões), em queda; alvo no fim do plano ≈ R$ 0,26.
- **Indicador Atual:** **3.986** — **40% da meta-prova (10.000)** · 33% do teto (12.000) — **+40 na s093** (T2 Exantemáticas 89% · T3 Cir. Infantil III 86%). Perf. geral 79,8%.
- **Performance Geral:** ~79% (`sessoes_bulk`). Fracos no dashboard: **Hepato 57% · Dermato 67% · Cardiologia/Otorrino 68% · Hemato 74%**. **Gargalo principal = EXECUÇÃO DE PROVA, não conteúdo** — default-to-C, fechamento precoce, **não fechar a conduta** (reconfirmado na s088: acertou o dx, errou a conduta em intussuscepção/ECN/apendicite).
- **Contadores:** **48 resumos** em `resumos/` · **354 erros** em `ipub.db` · **~384 cards ativos** (41 andaimes) · **taxonomia `UNIQUE(area,tema)`**
- **Cronograma (SSOT `Cronograma.pdf`, 28 semanas — 2 de revisão removidas):** Semana 09 ✓. **Semana 10 EM CURSO — 6/11 tasks (147q); faltam 5 (~126q):** Meningites Rev · Diabetes Comp. Crônicas · Distúrbios Ácido-Base · Pneumo Intensiva I · Hepatites Virais. Calendário na S13 (~3 sem atrás). **Frente s094: ultraplan do cronograma comprimido + sistema de sync** (`docs/plans/s094-ultraplan.md`).

---

## Estado por frente (macro)

- **Volume & Metas:** **3.946 / 12.000 ENAMED (32,9%); +107 na s092** (modo volume Semana 10); ritmo-alvo **~102q/dia** p/ 12k em 13-09. **Meta junho 4.500: faltam 554.** Cluster fraco: Hepato 57%, Dermato 67%, Cardiologia/Otorrino 68%, Hemato 72%. **Gargalo nº1 = execução de prova** (s091); s092 evidenciou também **lacunas de conteúdo fino** em temas de revisão (DO, DIU).
- **Conteúdo:** **48 resumos** (+Planej. Familiar, +Exantemáticas na s086). **Gaps:** `Diabetes - Complicações Crônicas`; ectópica/icterícia neonatal (só andaime). PDFs EMED p/ aula-base: GO restante, Gastro, Dermato, Pediatria.
- **Erros & Cards:** **354 erros; ~384 cards ativos (41 andaimes).** Pipeline `insert_questao.py` (+ `insert_card_base.py` andaime); taxonomia `UNIQUE(area,tema)`. Fila FSRS: vencida zerada na s091; backlog de novos + 30 novos das s091/s092 (#554-583).
- **FSRS:** backlog grande — mas a **curva finalmente comeu na s084 (35/50 revisados)**. `/refrescar` (dormente) + `/revisar` atacam o backlog. **Andaime validado em tempo real:** Hemostasia destravou após 3 cards-base. Clusters frios andaimados: Hemostasia (fatores), Cardiopatias (T4F/shunt).
- **Infraestrutura — NOVA capacidade (s083): gestão da curva de esquecimento** — `review_log` (SSOT do tempo-de-revisão) + radar de dormência (`review_radar.py`) + `/refrescar` (`dormant_refresh.py`, **não toca o FSRS**) + **boot proativo** "Plano do Dia" (`day_plan.py`, AGENTE §2 passo 4) + **autonomia codificada** (AGENTE §1.1) + contrato `core/contracts/forgetting-curve-contract.md`. Mantém: cards de altura graduada (s082), governança de evidência (s076), Camada 2 do `/revisar` (s078). **5 padrões metacognitivos vivos** (+ palpite-abandonado-por-palavra). **Tier-3 (schema de altura) pendente.**

---

## Próximos passos

> **🏃 MODO SPRINT QUESTION-FIRST (s078 → ~13/07/2026):** atrasado → estudo só por **questões + flashcards, SEM apostila corrida**. Exceção produtiva: **refresh dirigido do tema ANTES de cada bloco** (`/revisar` Camada 0 — leitura calibrada ao nível do estudante). Meta **≥100 questões/dia + ≥20 flashcards/dia**. **Não criar resumo completo** de tópico neste período. Detalhe: [[project_sprint_questoes_focado]] e [[cards-altura-graduada]] na memória.

Ver [`ROADMAP.md`](ROADMAP.md). Prioridades guiadas pelo cronograma (SSOT: `Cronograma de Reta Final.xlsx` no Drive):

1. **Abertura da próxima:** começa com **flashcards** (17 cards operacionais da s086 vencem cedo no FSRS) → **≥100 questões**. Aula-base + refresh Camada 0 antes de cada bloco.
2. **PRIORIDADE ESTRATÉGICA — execução de prova:** o gargalo migrou de conteúdo para processo de resolução. Treinar o **ritual anti-vazamento** (default-to-C + fechamento precoce) via [`PLAYBOOK_EXECUCAO_PROVA.md`](PLAYBOOK_EXECUCAO_PROVA.md). Maior alavanca da preparação. (bug nº 1c segue ativo; default-to-C é o novo sub-padrão dominante.)
3. **Aulas-base = CONTRATO** (AGENTE §1.2): cunhar aula "escada de degraus" antes de cada bloco novo; calibrar descompressão para pontos operacionais que a banca cobra.
4. **Gaps de resumo:** `Diabetes - Complicações Crônicas`; candidatos: ectópica, icterícia neonatal (só andaime). PDFs do EMED agora MANTIDOS (gitignored) p/ RAG — GO/Gastro/Dermato/Pediatria despejados.
5. **Pendentes:** 🐛 corrigir o ramp de metas do `performance.py` (junho 4.500 / dez 17.000, pós-s084); Tier-3 (schema de altura), limpeza `[bulk]`/`Geral` da taxonomia, enumeração do Drive, re-drill dos 1 (426, 435, 84, 78, 70, 104).

> Detalhe operacional e próximo passo imediato: [`HANDOFF.md`](HANDOFF.md). Histórico completo: [`history/INDEX.md`](history/INDEX.md).

---

## Repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao fechar sessão: atualizar `HANDOFF.md` (sempre) e `ESTADO.md` (se o macro mudou) + registrar em `history/`. Ver `AGENTE.md §3`.*
