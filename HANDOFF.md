# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-28 ~16:30 — **s098: simulado dominical (41q, navegador interrompeu) + diagnóstico dos 16 erros + frente de predição ENAMED**. 25/41 = 61%; **10/16 erros foram EXECUÇÃO** (bug nº1 ×6 + conduta ×3 + leitura ×1), só 6 de conteúdo. Volume no slot dedicado `Simulado`. 16 erros persistidos em `tmp/simulado_s098_erros.md` p/ cunhagem. (s097 = curadoria do backlog: 115→98 temas, 409→386 cards.)*

## ▶ Próximo passo imediato — s099 (HOJE)
**A) Adiantar o cronograma (~60-80 questões):** Semana 11 (Med. de Família, Exantemáticas Rev, Cir. Infantil Pt3 Rev, Vulvovaginites, Imunizações, Sepse, Síndromes Hipertensivas). Foco: **ritual anti-vazamento** — integrar o conjunto (o bug nº1 derrubou 6 do simulado).
**B) Cunhar os 16 cards do simulado** — substrato em `tmp/simulado_s098_erros.md` (pipeline limpo, ancorados no elo); priorizar os 6 do bug nº1 + refresh de asma/GINA (2 erros).
**C) Implementar a predição ENAMED** (frente `project_predicao_enamed`): série temporal de % → projeção + IC.

## Simulado / Predição ENAMED (s098 — frente nova)
- Slot `Simulado` em `AREAS_VALIDAS` = volume/desempenho AGREGADO (sinal de condição-de-prova, o mais próximo do ENAMED); erros vinculam aos temas reais (sem dupla contagem). Usuário espelha 1 linha no Quadro Geral do dashboard.
- 1º ponto da série: 41q/61%. A frente projetará a nota ENAMED com IC a partir da evolução.

## Curadoria de cards (s097 — capacidade nova)
- Workflow `.agents/workflows/curar-cards.md` (5 fases). Ferramentas: `normalize_taxonomia.py`, `insert_card_extra.py`, `detect_clones.py`, `recurate` (+`tipo`/+UTF-8), linter (+`orfao_sem_andaime`). Achado: defeito de card é de **autoria** → reforjar ancorado no erro > aposentar.

## Estado por frente
- **Volume & Metas:** **4.153** (4.112 clínico + 41 simulado) / 10.000 (41%). Perf. ~79%. Custo/q acum. R$0,77.
- **Cronograma (SSOT `Cronograma.pdf`):** **Próxima = S11**; calendário nominal S13.
- **Conteúdo:** **52 resumos**. Gaps: `TCE.md`, `Sistemas de Informação em Saúde.md`.
- **Erros & Cards:** **364 erros · 386 cards ativos** (taxonomia 98 temas, áreas canônicas) + **16 erros do simulado pendentes de cunhagem**.

## Pendências ativas
Cunhar 16 cards do simulado. Implementar predição ENAMED. Ratificar contrato Revisão Calibrada. Limpeza pós-curadoria (29 regra-vazia · Cirurgia Infantil). Reescrever `TCE.md`. Áreas fracas: Hepato 57% · Dermato 67% · Cardio 67% · Otorrino 68% · Nefro 70% · Hemato 72%.

---
*Histórico: history/INDEX.md · Macro: ESTADO.md · Erros do simulado: tmp/simulado_s098_erros.md · Curadoria: .agents/workflows/curar-cards.md*
