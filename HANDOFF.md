# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-03 — conexão Drive + ENAMED + 15 erros Arboviroses + camada de contratos (sessão 075)*

## ▶ Próximo passo imediato (ao retomar)
1. **Criar resumo `Diabetes Mellitus - Complicações Crônicas`** (gap do cronograma; DM2 e Compl. Agudas já existem). Revisão por Questões do bloco DM fecha 15–19/06.
2. **Revisão FSRS diária** via `/revisar` — 14 cards de Arboviroses voltam em 04/06 (sobretudo Febre Amarela básica) + drenar backlog por área fraca.
3. **Boot:** rodar o check de reconcile (`core/contracts/reconcile-contract.md`) — conferir planilha↔db↔ESTADO↔FSRS antes de trabalho novo.

## Estado por frente
- **Volume & Metas:** 3.170/12.000 ENAMED (80,4%); ~86q/dia para o alvo. Planilha conciliada 100% em 03/06.
- **Conteúdo:** Arboviroses turbinado (17 armadilhas, seção vacina FA blindada). Próximo = Diabetes Compl. Crônicas.
- **Erros & Cards:** 226 erros; 15 novos de Arboviroses (s075) + 19 cards qualitativos.
- **FSRS:** fila ativa 332 qualitativos; backlog 307 nunca revisados; 70 heurísticos aposentados (bankruptcy).
- **Infraestrutura:** `core/contracts/` criada (4 contratos); `/revisar` ganhou modo conversacional (auto-rating + lote); HANDOFF+ESTADO split.

## Última sessão — sessão 075
- Google Drive MCP conectado: IDs canônicos registrados (`/importar-planilha`); planilha↔db conciliada (delta +40q Cirurgia; `GO`→Ginecologia, `Obstetricia`→Obstetrícia).
- `/performance`: marco **ENAMED** (12k/13-09) com projeções de ritmo; `META_CUSTO_Q` 0,10→0,20.
- Cronograma do Drive vira guia de prioridades (não persiste no db).
- 15 erros de Arboviroses analisados (3 blocos) → 19 flashcards + resumo turbinado; `/revisar` dos 19 (8×1, 6×2, 2×3, 3×4); cluster fraco = Febre Amarela.
- Camada de estado contract-driven (espelho do `agente-daktus-content`): 4 contratos + HANDOFF + bankruptcy dos 70 cards legados.

## Pendências/observações ativas
- **Push pendente:** muitos commits locais da s075; `main` sem upstream tracking configurado — resolver no go.
- **Erro repetido vigiado:** dose Dengue C (10/1h) vs D (20/20min) — falhou 2-3× em casos embrulhados; card volta amanhã.

---
*Histórico: history/INDEX.md · Snapshot macro: ESTADO.md*
