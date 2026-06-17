---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, handoff-contract, estado-contract]
---

# ESTADO — MedHub

*Atualizado: 2026-06-17 (sessão 084) | Ferramenta: Claude Code (Opus 4.8)*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) → [`HANDOFF.md`](HANDOFF.md) (operacional curto) primeiro. Este arquivo é o snapshot **macro** (metas, indicador, marcos). Estrutura normatizada por [`core/contracts/estado-contract.md`](core/contracts/estado-contract.md).

---

## Metas

> **Plano atualizado no `Dashboard EMED 2026` (reconcile s084):** ramp mensal de questões 3.000 (mai) → **17.000 (dez/2026)** [3000·4500·6250·8000·10000·12500·15000·17000]; investimento R$ 2.940 → R$ 4.410 (R$ 210/mês). **Reconcile db↔dashboard: batem por área e no total (3.457 = 3.457, 0 divergência).** *(Supersede a antiga "Meta Final 23.000" — confirmar com o usuário se o stretch de 23k permanece.)*

- **Marco ENAMED (prioridade):** 12.000 questões até **13/09/2026** — ritmo-alvo **~96q/dia** (faltam 8.543). ⚠️ Meta de junho (4.500) não fecha: atrás 1.043.
- **Plano de fim de ano:** 17.000 questões até 12/2026 (dashboard).
- **Custo/Q atual:** **R$ 0,91** (jun/2026, acumulado = investimento ÷ questões), em queda; alvo no fim do plano ≈ R$ 0,26.
- **Indicador Atual:** 3.457 / 12.000 ENAMED (28,8%).
- **Performance Geral:** 80,0% (2.767 acertos / 3.457 questões — `sessoes_bulk`). Fracos no dashboard: **Hepato 57% · Dermato 67% · Cardiologia/Otorrino 68% · Hemato 74% · Pneumo/Nefro/Endocrino/Infecto ~76%**.
- **Contadores:** **46 resumos** em `resumos/` · **278 erros** em `ipub.db` · **~280 cards ativos** (+20 na s084; 196 aposentados) · **0 heurísticos ativos** · **taxonomia `UNIQUE(area,tema)`**

---

## Estado por frente (macro)

- **Volume & Metas:** **3.457 acumuladas (80,0%); +66 na s084** (Nefro 40/31 + SOAP 26/24); ritmo-alvo ~96q/dia p/ 12k em 13-09. Junho (4.500) não fecha (atrás 1.043); foco em não perder setembro. Cluster fraco: Hepato, Dermato, Cardiologia, Otorrino, Hemato.
- **Conteúdo:** **46 resumos.** `Doença Renal Crônica.md` **construído na s084** (stub→padrão-ouro: KDIGO→TRS→DRC×LRA, 30 armadilhas) + `LRA.md` auditado. **Gap real restante:** `Diabetes - Complicações Crônicas`.
- **Erros & Cards:** 278 erros; **~280 cards ativos** (+20 na s084: 9 Nefro + 3 SOAP + 8 andaimes DMO/Hemostasia/Cardio). Pipeline `insert_questao.py` (+ `insert_card_base.py` andaime); taxonomia `UNIQUE(area,tema)`.
- **FSRS:** backlog grande — mas a **curva finalmente comeu na s084 (35/50 revisados)**. `/refrescar` (dormente) + `/revisar` atacam o backlog. **Andaime validado em tempo real:** Hemostasia destravou após 3 cards-base. Clusters frios andaimados: Hemostasia (fatores), Cardiopatias (T4F/shunt).
- **Infraestrutura — NOVA capacidade (s083): gestão da curva de esquecimento** — `review_log` (SSOT do tempo-de-revisão) + radar de dormência (`review_radar.py`) + `/refrescar` (`dormant_refresh.py`, **não toca o FSRS**) + **boot proativo** "Plano do Dia" (`day_plan.py`, AGENTE §2 passo 4) + **autonomia codificada** (AGENTE §1.1) + contrato `core/contracts/forgetting-curve-contract.md`. Mantém: cards de altura graduada (s082), governança de evidência (s076), Camada 2 do `/revisar` (s078). **5 padrões metacognitivos vivos** (+ palpite-abandonado-por-palavra). **Tier-3 (schema de altura) pendente.**

---

## Próximos passos

> **🏃 MODO SPRINT QUESTION-FIRST (s078 → ~13/07/2026):** atrasado → estudo só por **questões + flashcards, SEM apostila corrida**. Exceção produtiva: **refresh dirigido do tema ANTES de cada bloco** (`/revisar` Camada 0 — leitura calibrada ao nível do estudante). Meta **≥100 questões/dia + ≥20 flashcards/dia**. **Não criar resumo completo** de tópico neste período. Detalhe: [[project_sprint_questoes_focado]] e [[cards-altura-graduada]] na memória.

Ver [`ROADMAP.md`](ROADMAP.md). Prioridades guiadas pelo cronograma (SSOT: `Cronograma de Reta Final.xlsx` no Drive):

1. **Abertura da próxima (s085):** revisão temática dos gaps da s084 → re-drill dos 18 cards <4 → 15 restantes da fila FSRS (ver `HANDOFF.md`).
2. **VOLUME (questões):** o gargalo. Bloco 3 (Nefro) **fechado** ✅. Seguir ≥96q/dia com refresh pré-bloco; **alvo nº 1 metacognitivo: bug nº 1c (fato/contexto)**, reincidente na s084.
3. **Gap de resumo restante:** `Diabetes - Complicações Crônicas`.
4. **Pendentes:** Tier-3 (schema de altura), limpeza `[bulk]`/`Geral` da taxonomia, investigar a enumeração do Drive.

> Detalhe operacional e próximo passo imediato: [`HANDOFF.md`](HANDOFF.md). Histórico completo: [`history/INDEX.md`](history/INDEX.md).

---

## Repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao fechar sessão: atualizar `HANDOFF.md` (sempre) e `ESTADO.md` (se o macro mudou) + registrar em `history/`. Ver `AGENTE.md §3`.*
