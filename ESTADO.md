---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, handoff-contract, estado-contract]
---

# ESTADO — MedHub

*Atualizado: 2026-06-15 (sessão 083) | Ferramenta: Claude Code (Opus 4.8)*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) → [`HANDOFF.md`](HANDOFF.md) (operacional curto) primeiro. Este arquivo é o snapshot **macro** (metas, indicador, marcos). Estrutura normatizada por [`core/contracts/estado-contract.md`](core/contracts/estado-contract.md).

---

## Metas

- **Marco ENAMED (prioridade):** 12.000 questões até 13/09/2026 — ritmo alvo ~94q/dia (projeções no `/performance`)
- **Marco ENARE:** 17.000 questões até 10/2026 (Custo/Q: R$ 0,24)
- **Meta Final:** 23.000 questões até 12/2026 (Custo/Q: R$ 0,20)
- **Indicador Atual:** 3.391 / 12.000 ENAMED — faltam ~8.609 q
- **Performance Geral:** 80,0% (2.712 acertos / 3.391 questões — `sessoes_bulk`)
- **Contadores:** 45 resumos em `resumos/` · 267 erros em `ipub.db` · **~260 cards qualitativos ativos** (+14 na s083; 196 aposentados) · **0 heurísticos ativos** · **taxonomia deduplicada (126→86, `UNIQUE(area,tema)`)**

---

## Estado por frente (macro)

- **Volume & Metas:** 3.391 acumuladas (80,0%); **+75 na s083 (zero quebrado após 3 sessões a 0)**; ritmo-alvo ~94q/dia p/ 12k em 13-09. Junho (8.000) não fecha; foco em não perder setembro. Cluster fraco: Hepato, Dermato, Cardiologia, Otorrino, Hemato.
- **Conteúdo:** 45 resumos. `DITC.md` ganhou **§4 DMTC** na s083. **Gaps reais ativos:** `Diabetes - Complicações Crônicas` e `Doença Renal Crônica` (stub de 9 linhas, exposto na s083).
- **Erros & Cards:** 267 erros; **~260 cards ativos** (+14 na s083: 13 GO + 1 DITC). Pipeline `insert_questao.py` (+ `insert_card_base.py` andaime); **taxonomia deduplicada** (126→86, `UNIQUE(area,tema)`).
- **FSRS:** backlog grande (~167 novos + ~41 vencidos) — a curva quase não é alimentada (`revisados≈0`). O **refresh dormente** (`/refrescar`) e o `/revisar` atacam isso. Fracos persistentes: Hemato, cardiopatia.
- **Infraestrutura — NOVA capacidade (s083): gestão da curva de esquecimento** — `review_log` (SSOT do tempo-de-revisão) + radar de dormência (`review_radar.py`) + `/refrescar` (`dormant_refresh.py`, **não toca o FSRS**) + **boot proativo** "Plano do Dia" (`day_plan.py`, AGENTE §2 passo 4) + **autonomia codificada** (AGENTE §1.1) + contrato `core/contracts/forgetting-curve-contract.md`. Mantém: cards de altura graduada (s082), governança de evidência (s076), Camada 2 do `/revisar` (s078). **5 padrões metacognitivos vivos** (+ palpite-abandonado-por-palavra). **Tier-3 (schema de altura) pendente.**

---

## Próximos passos

> **🏃 MODO SPRINT QUESTION-FIRST (s078 → ~13/07/2026):** atrasado → estudo só por **questões + flashcards, SEM apostila corrida**. Exceção produtiva: **refresh dirigido do tema ANTES de cada bloco** (`/revisar` Camada 0 — leitura calibrada ao nível do estudante). Meta **≥100 questões/dia + ≥20 flashcards/dia**. **Não criar resumo completo** de tópico neste período. Detalhe: [[project_sprint_questoes_focado]] e [[cards-altura-graduada]] na memória.

Ver [`ROADMAP.md`](ROADMAP.md). Prioridades guiadas pelo cronograma (SSOT: `Cronograma de Reta Final.xlsx` no Drive):

1. **VOLUME (questões):** o gargalo. Fechar o **Bloco 3 (Nefro, 40q) pendente**; ritmo ≥94q/dia com refresh pré-bloco.
2. **Estrear o boot proativo** (`day_plan.py`, §2 passo 4) + o **refresh dormente diário** (`/refrescar`) — começar a alimentar a curva (FSRS backlog grande).
3. **Gaps de resumo:** `Doença Renal Crônica` (stub) e `Diabetes - Complicações Crônicas`.
4. **Pendentes:** Tier-3 (schema de altura), limpeza `[bulk]`/`Geral` da taxonomia, investigar a enumeração do Drive.

> Detalhe operacional e próximo passo imediato: [`HANDOFF.md`](HANDOFF.md). Histórico completo: [`history/INDEX.md`](history/INDEX.md).

---

## Repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao fechar sessão: atualizar `HANDOFF.md` (sempre) e `ESTADO.md` (se o macro mudou) + registrar em `history/`. Ver `AGENTE.md §3`.*
