---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, handoff-contract, estado-contract]
---

# ESTADO — MedHub

*Atualizado: 2026-06-04 (sessão 076) | Ferramenta: Claude Code (Opus 4.8)*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) → [`HANDOFF.md`](HANDOFF.md) (operacional curto) primeiro. Este arquivo é o snapshot **macro** (metas, indicador, marcos). Estrutura normatizada por [`core/contracts/estado-contract.md`](core/contracts/estado-contract.md).

---

## Metas

- **Marco ENAMED (prioridade):** 12.000 questões até 13/09/2026 — ritmo alvo ~86q/dia (projeções no `/performance`)
- **Marco ENARE:** 17.000 questões até 10/2026 (Custo/Q: R$ 0,24)
- **Meta Final:** 23.000 questões até 12/2026 (Custo/Q: R$ 0,20)
- **Indicador Atual:** 3.244 / 12.000 ENAMED — faltam ~8.756 q
- **Performance Geral:** 80,2% (2.601 acertos / 3.244 questões — `sessoes_bulk`; +34q/27a de CAD/EHH na s076)
- **Contadores:** 45 resumos em `resumos/` · 233 erros em `ipub.db` · 338 cards qualitativos ativos (71 aposentados) · **0 heurísticos ativos**

---

## Estado por frente (macro)

- **Volume & Metas:** 3.210 acumuladas (80,2%). Planilha Drive conciliada (delta +40q Cirurgia + 40q Infecto/Arboviroses; áreas normalizadas). Cluster fraco confirmado: Cardiologia, Hepato, Dermato, FA.
- **Conteúdo:** 45 resumos. Arboviroses turbinado (17 armadilhas). **Gap ativo do cronograma:** `Diabetes Mellitus - Complicações Crônicas`.
- **Erros & Cards:** 233 erros estruturados (+7 CAD/EHH). Pipeline `/analisar-questao` → `insert_questao.py` operante.
- **FSRS:** 338 cards qualitativos; **fila 100% qualitativa — 0 heurísticos** (os 87 órfãos da bankruptcy s075 foram regenerados em 4 ondas na s076). Backlog state=0 segue a drenar por área fraca. 71 aposentados (70 bankruptcy + 1 duplicata).
- **Infraestrutura:** camada de contratos `core/contracts/`. `cards_regen_queue.py` critério corrigido. **Governança de evidência (s076):** `evidence-governance.md` + `/pesquisar-evidencia` + subagente `evidence-researcher` + `pubmedmcp` — auditoria de afirmação clínica (BR>INT>consenso + lente da banca), adaptada do irmão. Google Drive MCP vinculado.
- **Dívida de dados (nova):** temas `[bulk] *` são lata de lixo de rotulagem — ~80 cards mal-filiados (cardiopatias/iSGLT-2/HbA1c/epidemiologia/GO sob "[bulk] Cirurgia"); inflam o "Cirurgia due" e distorcem o filtro por área. Re-fil pendente.

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
