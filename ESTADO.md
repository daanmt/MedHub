---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, handoff-contract, estado-contract]
---

# ESTADO — MedHub

*Atualizado: 2026-06-13 (sessão 081) | Ferramenta: Claude Code (Fable 5)*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) → [`HANDOFF.md`](HANDOFF.md) (operacional curto) primeiro. Este arquivo é o snapshot **macro** (metas, indicador, marcos). Estrutura normatizada por [`core/contracts/estado-contract.md`](core/contracts/estado-contract.md).

---

## Metas

- **Marco ENAMED (prioridade):** 12.000 questões até 13/09/2026 — ritmo alvo ~93q/dia (projeções no `/performance`)
- **Marco ENARE:** 17.000 questões até 10/2026 (Custo/Q: R$ 0,24)
- **Meta Final:** 23.000 questões até 12/2026 (Custo/Q: R$ 0,20)
- **Indicador Atual:** 3.316 / 12.000 ENAMED — faltam ~8.684 q
- **Performance Geral:** 79,9% (2.651 acertos / 3.316 questões — `sessoes_bulk`; +72q nas s079-080: LRA 77%, Hemostasia 62%)
- **Contadores:** 45 resumos em `resumos/` · 255 erros em `ipub.db` · **238 cards qualitativos ativos (196 aposentados)** · **0 heurísticos ativos** · **0 duplicatas**

---

## Estado por frente (macro)

- **Volume & Metas:** 3.316 acumuladas (79,9%); ritmo-alvo ~93q/dia p/ 12k em 13-09. Planilha não reconciliada nas s079-080. Cluster fraco: Cardiologia, Hepato, Dermato, FA, **Hemostasia (62%)**.
- **Conteúdo:** 45 resumos; **`Hemostasia.md` expandido (s081)** — coagulopatias adquiridas (hipotermia/tríade letal, vit. K, PTT/SHU), HNF (IIa+Xa), PTI criança×adulto, +7 armadilhas. **Gaps ativos:** resumo de **Cardiopatia Congênita** (tema dos cards travados) e `Diabetes - Complicações Crônicas`.
- **Erros & Cards:** 255 erros; **238 cards qualitativos ativos** (c92 aposentado na curadoria s081). Pipeline `insert_questao.py` operante; **nova rotina de curadoria `recurate_cards.py`** (refaz cards in-place por id, preserva FSRS).
- **FSRS:** 238 ativos; **49 reviews na s081** (pós-pausa de ~2-3 meses). Cardiopatia congênita segurada até ter resumo de base. Pontos fracos: Hemato (vWD/FVIII, PTI, coagulopatias adquiridas), cardiopatia congênita (tema zero).
- **Infraestrutura:** camada de contratos `core/contracts/`. **Governança de evidência (s076):** `evidence-governance.md` + `/pesquisar-evidencia` + subagente `evidence-researcher` + `pubmedmcp`. **Contrato `/revisar` Camada 2 (s078):** ao fechar sessão, revisão direcionada de volta ao resumo do tema com gap. **3 padrões metacognitivos nomeados (s079-080):** ancoragem no número (PTI reincidiu), ancoragem no fármaco, enunciado negativo. **Curadoria de cards (s081):** `tools/recurate_cards.py` (refaz in-place). **4º padrão metacognitivo:** "fato verdadeiro no contexto errado" (Pringle/beta2/GLP-1).

---

## Próximos passos

> **🏃 MODO SPRINT QUESTION-FIRST (s078 → ~13/07/2026):** atrasado no cronograma → estudo só por **questões + flashcards, SEM leitura de apostila** corrida. Exceção produtiva: **revisão direcionada do resumo ANTES de cada bloco** (reonboarding sintético do tema, a "última chance" antes de avançar). Meta **≥100 questões/dia + ≥20 flashcards/dia** (100/dia > ritmo-alvo ENAMED de ~93/dia → recupera o gap). **Não criar resumo completo por tópico** neste período. Detalhe: [[project-sprint-questoes-focado]] na memória.

Ver [`ROADMAP.md`](ROADMAP.md). Prioridades guiadas pelo cronograma (SSOT: `Cronograma de Reta Final.xlsx` no Drive):

1. **Cardiopatia Congênita:** criar o resumo de base (tema não-dominado) + drillar os 12 cards travados. Depois, **cards + questões (ambos)**. Detalhe operacional no `HANDOFF.md`.
2. **Diabetes - Complicações Crônicas:** criar o resumo (gap; DM2 e Compl. Agudas já existem).
3. **Drenar backlog FSRS** por área fraca + revisão diária via `/revisar`.
4. **Meta volumétrica:** ENAMED 12k até 13/09 (~93q/dia) — priorizar Revisão por Questões.

> Detalhe operacional e próximo passo imediato: [`HANDOFF.md`](HANDOFF.md). Histórico completo: [`history/INDEX.md`](history/INDEX.md).

---

## Repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao fechar sessão: atualizar `HANDOFF.md` (sempre) e `ESTADO.md` (se o macro mudou) + registrar em `history/`. Ver `AGENTE.md §3`.*
