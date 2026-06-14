# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-14 — s082 (revisão de Cardiopatias Congênitas + evolução "cards de altura graduada"). Diagnóstico: o tema NÃO era "zero" — o resumo existe e é gold; o gap era **grounding do estudante**. Construída a infra de andaime de pré-requisito. **Próximo: VOLUME (questões — gargalo real, 2 dias a 0) + drillar a escada de cardiopatia conforme o FSRS trouxer.***

## ▶ Próximo passo imediato — abertura de amanhã
1. **Questões — o gargalo de verdade.** Duas sessões seguidas a 0 (s081 grounding, s082 construção). Scrum master cobra o piso (≥100/dia; ritmo-alvo ENAMED ~94/dia). **Refresh pré-bloco** (`/revisar` Camada 0) antes do bloco da área escolhida.
2. **Drillar a escada de Cardiopatias Congênitas** conforme o FSRS vence: HCE (base c441 + alvos c94/c95/c96) volta **amanhã**; mecanismos (c443-445) e os base 439/440/442 em ~2 dias. Escada base→mecanismo→topo já no banco (tema 121).
3. **Re-testar os 4 refeitos da s081** (ainda não revisados): 428 (HIT), 68 (iSGLT-2), 74 (Cushing), 82 (TXA).
4. **Decisão Tier-3 pendente:** formalizar altura no schema (ordinal + `prereq_de` + fila auto-ordenada base→topo). Hoje a altura vive no campo `tipo` (sem schema change).

## Estado por frente
- **Volume & Metas:** 3.316/12.000 ENAMED (79,9%) — **inalterado** (0 questões). Junho (meta 8.000) já não fecha; foco = ~94q/dia p/ não perder 13/09. Custo/q alto (R$ 0,95) — diluir com volume.
- **Conteúdo:** 45 resumos. **`Cardiopatias Congênitas.md` é gold e completo** — a s081 errou ao chamá-lo de "tema zero a criar". Sem gap de material aqui. Gap real: `Diabetes - Complicações Crônicas`.
- **Erros & Cards:** 255 erros; **+8 cards de andaime** no tema 121 (5 `base` ids 438-442; 3 `mecanismo` ids 443-445). ~246 cards ativos.
- **FSRS:** s082 drillou os **12 cards-alvo** de cardiopatia (2 vistos + 10 estreias) + os 8 de andaime. Distribuição honesta; **HCE foi o buraco** (re-ensinado, volta amanhã).
- **Infraestrutura:** NOVA capacidade **cards de altura graduada** — `tools/insert_card_base.py` + `/revisar` Camada 0 (refresh + compressão calibrada) + decisão AGENTE §6 + régua em `estilo-flashcard.md`. Ver [[cards-altura-graduada]] na memória.

## Última sessão — sessão 082 (revisão + evolução de método)
- Drill de Cardiopatias Congênitas (12 cards-alvo). Achado: tema não-dominado por **falta de grounding**, não de material (resumo gold já existia; HANDOFF da s081 estava factualmente errado).
- Co-desenho com o usuário da evolução **"altura graduada"**: cards `base → mecanismo → nuance → topo`; andaime gerado quando um **cluster** cai; propagação local; compressão calibrada ao nível do estudante. Princípios de `ai-eng`.
- Construído: CLI `insert_card_base.py` (Tier-1, sem schema change) + 8 cards de andaime + docs (estilo-flashcard, revisar Camada 0, AGENTE §6/§7.4) + memória.
- Gap fino do estudante nomeado: **causalidade/mecanismo, não fato** — o degrau `mecanismo` é o de maior rendimento.

## Pendências/observações ativas
- **VOLUME é o gargalo.** Duas sessões a 0 questões — priorizar amanhã.
- **Tier-3:** schema formal de altura (ordinal + `prereq_de` + fila auto-ordenada base→topo). Espera OK do usuário.
- **Aplicar altura graduada a outros temas frios** (Hemato, LRA) conforme clusters caírem na revisão.
- **4 padrões metacognitivos vivos:** ancoragem nº/fármaco, enunciado negativo, fato-no-contexto-errado — todos = "parar antes de completar a verificação".

---
*Histórico: history/INDEX.md · Snapshot macro: ESTADO.md*
