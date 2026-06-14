---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, handoff-contract, estado-contract]
---

# ESTADO — MedHub

*Atualizado: 2026-06-14 (sessão 082) | Ferramenta: Claude Code (Opus 4.8)*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) → [`HANDOFF.md`](HANDOFF.md) (operacional curto) primeiro. Este arquivo é o snapshot **macro** (metas, indicador, marcos). Estrutura normatizada por [`core/contracts/estado-contract.md`](core/contracts/estado-contract.md).

---

## Metas

- **Marco ENAMED (prioridade):** 12.000 questões até 13/09/2026 — ritmo alvo ~94q/dia (projeções no `/performance`)
- **Marco ENARE:** 17.000 questões até 10/2026 (Custo/Q: R$ 0,24)
- **Meta Final:** 23.000 questões até 12/2026 (Custo/Q: R$ 0,20)
- **Indicador Atual:** 3.316 / 12.000 ENAMED — faltam ~8.684 q
- **Performance Geral:** 79,9% (2.651 acertos / 3.316 questões — `sessoes_bulk`)
- **Contadores:** 45 resumos em `resumos/` · 255 erros em `ipub.db` · **~246 cards qualitativos ativos** (+8 cards de andaime na s082; 196 aposentados) · **0 heurísticos ativos** · **0 duplicatas**

---

## Estado por frente (macro)

- **Volume & Metas:** 3.316 acumuladas (79,9%); ritmo-alvo ~94q/dia p/ 12k em 13-09. **Duas sessões seguidas a 0 questões (s081-082)** — o gargalo é volume. Meta de junho (8.000) já não fecha; foco em não perder setembro. Cluster fraco: Cardiologia, Hepato, Dermato, FA, Hemostasia.
- **Conteúdo:** 45 resumos. **`Cardiopatias Congênitas.md` é gold e completo** — a s081 errou ao registrá-lo como "tema zero a criar"; não há gap de material. **Gap real ativo:** `Diabetes - Complicações Crônicas`.
- **Erros & Cards:** 255 erros; **~246 cards ativos** (+8 de andaime no tema 121: 5 `base`, 3 `mecanismo`). Pipeline `insert_questao.py` + curadoria `recurate_cards.py` + **novo `insert_card_base.py`** (cards de andaime).
- **FSRS:** s082 drillou os 12 cards-alvo de Cardiopatias Congênitas + 8 de andaime. HCE foi o buraco (re-ensinado). Pontos fracos persistentes: Hemato, cardiopatia (em consolidação via escada).
- **Infraestrutura:** camada de contratos `core/contracts/`. **NOVA capacidade (s082): cards de altura graduada** — flashcards têm altura (`base→mecanismo→nuance→topo`, campo `tipo`); andaime de pré-requisito (`insert_card_base.py`) destrava tema frio quando um **cluster** cai; compressão calibrada no refresh pré-bloco (`/revisar` Camada 0); decisão AGENTE §6, régua em `estilo-flashcard.md`. **Schema formal de altura = Tier-3 pendente.** Governança de evidência (s076) e Camada 2 do `/revisar` (s078) ativas. **4 padrões metacognitivos vivos:** ancoragem nº/fármaco, enunciado negativo, fato-no-contexto-errado.

---

## Próximos passos

> **🏃 MODO SPRINT QUESTION-FIRST (s078 → ~13/07/2026):** atrasado → estudo só por **questões + flashcards, SEM apostila corrida**. Exceção produtiva: **refresh dirigido do tema ANTES de cada bloco** (`/revisar` Camada 0 — leitura calibrada ao nível do estudante). Meta **≥100 questões/dia + ≥20 flashcards/dia**. **Não criar resumo completo** de tópico neste período. Detalhe: [[project_sprint_questoes_focado]] e [[cards-altura-graduada]] na memória.

Ver [`ROADMAP.md`](ROADMAP.md). Prioridades guiadas pelo cronograma (SSOT: `Cronograma de Reta Final.xlsx` no Drive):

1. **VOLUME (questões):** o gargalo. Recuperar o ritmo ≥94q/dia, com refresh pré-bloco da área.
2. **Drenar a escada de Cardiopatias Congênitas** via FSRS (base/mecanismo/topo já no banco) + **aplicar altura graduada a outros temas frios** (Hemato, LRA) conforme clusters caírem.
3. **Diabetes - Complicações Crônicas:** criar o resumo (gap real).
4. **Tier-3:** decidir o schema formal de altura (ordinal + `prereq_de` + fila auto-ordenada base→topo).

> Detalhe operacional e próximo passo imediato: [`HANDOFF.md`](HANDOFF.md). Histórico completo: [`history/INDEX.md`](history/INDEX.md).

---

## Repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao fechar sessão: atualizar `HANDOFF.md` (sempre) e `ESTADO.md` (se o macro mudou) + registrar em `history/`. Ver `AGENTE.md §3`.*
