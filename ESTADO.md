---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, handoff-contract, estado-contract]
---

# ESTADO — MedHub

*Atualizado: 2026-06-11 (sessão 078) | Ferramenta: Claude Code (Fable 5)*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) → [`HANDOFF.md`](HANDOFF.md) (operacional curto) primeiro. Este arquivo é o snapshot **macro** (metas, indicador, marcos). Estrutura normatizada por [`core/contracts/estado-contract.md`](core/contracts/estado-contract.md).

---

## Metas

- **Marco ENAMED (prioridade):** 12.000 questões até 13/09/2026 — ritmo alvo ~86q/dia (projeções no `/performance`)
- **Marco ENARE:** 17.000 questões até 10/2026 (Custo/Q: R$ 0,24)
- **Meta Final:** 23.000 questões até 12/2026 (Custo/Q: R$ 0,20)
- **Indicador Atual:** 3.244 / 12.000 ENAMED — faltam ~8.756 q
- **Performance Geral:** 80,2% (2.601 acertos / 3.244 questões — `sessoes_bulk`; +34q/27a de CAD/EHH na s076)
- **Contadores:** 45 resumos em `resumos/` · 234 erros em `ipub.db` · **216 cards qualitativos ativos (195 aposentados)** · **0 heurísticos ativos** · **0 duplicatas** (dedup estrutural s078: 109 pares v1/v2 por `questao_id`)

---

## Estado por frente (macro)

- **Volume & Metas:** 3.210 acumuladas (80,2%). Planilha Drive conciliada (delta +40q Cirurgia + 40q Infecto/Arboviroses; áreas normalizadas). Cluster fraco confirmado: Cardiologia, Hepato, Dermato, FA.
- **Conteúdo:** 45 resumos. Arboviroses turbinado (17 armadilhas). **Gap ativo do cronograma:** `Diabetes Mellitus - Complicações Crônicas`.
- **Erros & Cards:** 233 erros estruturados (+7 CAD/EHH). Pipeline `/analisar-questao` → `insert_questao.py` operante.
- **FSRS:** **216 cards qualitativos ativos**; fila 100% qualitativa. **Backlog de 44 cards drenado (s078)** (24×4, 5×3, 7×2, 8×1). **Dedup estrutural (s078): 109 pares duplicados v1/v2 aposentados** (chave `questao_id`; bug de pipeline criava 2 cards por questão). 195 aposentados no total (70 bankruptcy + 16 s077 + 109 s078). Contrato `/revisar` evoluído: flip + relearning intra-sessão (s077) + **Camada 2 — Revisão Direcionada de fechamento (s078)**. **Pendente:** 7 pares divergentes flagados p/ revisão manual (cards conflitantes, não-duplicatas).
- **Infraestrutura:** camada de contratos `core/contracts/`. **Governança de evidência (s076):** `evidence-governance.md` + `/pesquisar-evidencia` + subagente `evidence-researcher` + `pubmedmcp` — auditoria de afirmação clínica (BR>INT>consenso + lente da banca). Google Drive MCP vinculado. **`insert_questao.py` corrigido (s077):** não gera mais card heurístico extra no caminho qualitativo. **Contrato `/revisar` Camada 2 (s078):** ao fechar sessão, revisão direcionada de volta ao resumo do tema com gap (o card é a sonda, o resumo é a fonte) — diagnostica cobre/raso/inchado, expande/comprime a matéria. Verdict s078: 0 deficiência de material nos temas revisados.
- **Dívida de dados (RESOLVIDA s077):** os ~291 cards `[bulk]` foram re-categorizados para área/tema corretos ("[bulk] Cirurgia" 216→0; Cirurgia real 57, Pediatria 65, Endocrino 35). O filtro por área e o "due por área" voltam a ser confiáveis.

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
