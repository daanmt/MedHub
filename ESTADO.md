---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, handoff-contract, estado-contract]
---

# ESTADO — MedHub

*Atualizado: 2026-06-03 (sessão 075) | Ferramenta: Claude Code (Opus 4.8)*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) → [`HANDOFF.md`](HANDOFF.md) (operacional curto) primeiro. Este arquivo é o snapshot **macro** (metas, indicador, marcos). Estrutura normatizada por [`core/contracts/estado-contract.md`](core/contracts/estado-contract.md).

---

## Metas

- **Marco ENAMED (prioridade):** 12.000 questões até 13/09/2026 — ritmo alvo ~86q/dia (projeções no `/performance`)
- **Marco ENARE:** 17.000 questões até 10/2026 (Custo/Q: R$ 0,24)
- **Meta Final:** 23.000 questões até 12/2026 (Custo/Q: R$ 0,20)
- **Indicador Atual:** 3.170 / 12.000 ENAMED — faltam ~8.830 q
- **Performance Geral:** 80,4% (2.549 acertos / 3.170 questões — `sessoes_bulk`, conciliada com planilha Drive em 03/06)
- **Contadores:** 45 resumos em `resumos/` · 226 erros em `ipub.db` · 332 cards qualitativos ativos (70 legados aposentados)

---

## Estado por frente (macro)

- **Volume & Metas:** 3.170 acumuladas (80,4%). Planilha Drive conciliada (delta +40q Cirurgia importado; áreas normalizadas). Cluster fraco confirmado: Cardiologia, Hepato, Dermato, FA.
- **Conteúdo:** 45 resumos. Arboviroses turbinado (17 armadilhas). **Gap ativo do cronograma:** `Diabetes Mellitus - Complicações Crônicas`.
- **Erros & Cards:** 226 erros estruturados. Pipeline `/analisar-questao` → `insert_questao.py` operante.
- **FSRS:** 332 cards qualitativos; backlog 307 nunca revisados (drenar por área fraca — ver `fsrs-management-contract.md`). 70 heurísticos aposentados (bankruptcy s075).
- **Infraestrutura:** camada de contratos `core/contracts/` (estado, handoff, reconcile, fsrs). Google Drive MCP vinculado (IDs canônicos em `/importar-planilha`).

---

## Próximos passos

Ver [`ROADMAP.md`](ROADMAP.md). Prioridades guiadas pelo cronograma (SSOT: `Cronograma de Reta Final.xlsx` no Drive):

1. **Diabetes - Complicações Crônicas:** criar o resumo (gap; DM2 e Compl. Agudas já existem). Revisão por Questões do bloco DM fecha 15–19/06.
2. **Arboviroses:** Revisão por Questões (com Meningites e Sepse) na semana 22–26/06.
3. **Drenar backlog FSRS** por área fraca (307 cards) + revisão diária via `/revisar`.
4. **Meta volumétrica:** ENAMED 12k até 13/09 (~86q/dia) — priorizar Revisão por Questões.
5. **Pipeline RAG inverso** e **busca semântica na Biblioteca** (backlog técnico).

> Detalhe operacional e próximo passo imediato: [`HANDOFF.md`](HANDOFF.md). Histórico completo: [`history/INDEX.md`](history/INDEX.md).

---

## Repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao fechar sessão: atualizar `HANDOFF.md` (sempre) e `ESTADO.md` (se o macro mudou) + registrar em `history/`. Ver `AGENTE.md §3`.*
