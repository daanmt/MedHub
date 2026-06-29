# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-29 — **s099: recalibração da reta (11 sem) + política do simulado fora do volume + 105q da S11 (20 cards) + resumo gold de MFC**. 77 dias/11,0 sem até 13/09 (=S24-calendário); decisão: fechar a grade S11→S28 (6.689q) até o ENAMED ≈ 87q/dia. Estudo 28/06: MFC 31/27, Exantemáticas 41/35, Cir. Infantil Pt3 33/22 → 20 erros = 20 cards (616-635). 🔴 enunciado negativo reincidiu 3×; Wilms×neuro + criptorquidia (direção) + escroto agudo. (s098 = simulado 41q/61%, 16 erros pendentes.)*

## ▶ Próximo passo imediato — s100 (29/06)
**A) Seguir a S11** (faltam 10 das 13 tarefas: Vulvovaginites, Imunizações, Sepse, Síndromes Hipertensivas, etc.). Ritmo-alvo **~88q/dia** p/ fechar a grade. Refresh pré-bloco antes de cada tema.
**B) Drenar o FSRS** — 12 cards vencem hoje (os de 28/06) + backlog; `/revisar`. Re-drill dirigido: **enunciado negativo** (ritual V/F), **Wilms×neuro**, **criptorquidia (direção)**.
**C) Pendências de fundo:** ✅ zeradas no fim da s099 — 16 cards do simulado cunhados (636-651); resumo de Cirurgia Infantil já existia (ampliado com Pt3); predição ENAMED **arquivada** (decisão do usuário).

## Simulado (predição ENAMED ARQUIVADA — s099)
- 🗄️ **A frente de predição da nota ENAMED foi ARQUIVADA (s099, decisão do usuário)** — não implementar série temporal/IC. Memória `project_predicao_enamed` marcada como parada.
- **O que PERMANECE vivo:** slot `Simulado` em `AREAS_VALIDAS` registra simulados; **simulado NÃO conta como volume**; os **erros de simulado viram flashcards** nos temas reais (sem dupla contagem). Usuário espelha 1 linha no Quadro Geral do dashboard.
- **Simulados restantes: 10** (1/domingo, 05/07→06/09). 1º (e único) registrado: 41q/61%.
- **Mecanismo "fora do volume":** `performance.py::AREA_SIMULADO` + filtro `area<>'Simulado'` em `get_totais`/`get_por_area`/`get_questoes_do_mes` (herdado por `day_plan` e `cronograma`) + `day_plan.q_hoje`. Erros via `insert_questao.py` (não mexe em `questoes_realizadas`).

## 🎯 Decisão estratégica de cronograma (s099) — fechar a grade INTEIRA até o ENAMED
- 13/09 cai na **semana-calendário 24** da grade (30 sem; S1 = 30/03). Conteúdo está em **S11**. **Decisão do usuário:** comprimir TODO o conteúdo restante (S11→S28, S29/S30 = revisão 0q) **dentro dos 77 dias** até a prova; acelerar questões se preciso.
- **Falta de conteúdo: 6.689q (S11→S28)** → ritmo p/ fechar a grade ≈ **87q/dia corridos** (`day_plan`: "terminar a grade ~86.9/dia"). Acima do ritmo da meta-prova 10k (~76/dia), abaixo do teto 12k (~102/dia).
- **Vão ENAMED→UERJ/USP** será tocado por OUTRO cronograma / talvez só simulados. Prioridade absoluta = grade até 13/09.

## Curadoria de cards (s097 — capacidade nova)
- Workflow `.agents/workflows/curar-cards.md` (5 fases). Ferramentas: `normalize_taxonomia.py`, `insert_card_extra.py`, `detect_clones.py`, `recurate` (+`tipo`/+UTF-8), linter (+`orfao_sem_andaime`). Achado: defeito de card é de **autoria** → reforjar ancorado no erro > aposentar.

## Estado por frente
- **Volume & Metas:** **4.217** / 10.000 (42%) [+105 s099: 31 MFC + 41 Exantemáticas + 33 Cir. Infantil Pt3]. Perf. ~79%. Custo/q acum. R$0,77. **Simulado NÃO entra no volume (decisão s099)** — os 41q viram só ponto da série de predição; agregações de `performance.py`/`day_plan`/`cronograma` excluem `area='Simulado'`.
- **Cronograma (SSOT `Cronograma.pdf`):** **Próxima = S11**; calendário nominal S13 (13/09 = S24-calendário). **Alvo s099: fechar S11→S28 (6.689q) até 13/09 ≈ 87q/dia corridos.**
- **Conteúdo:** **53 resumos** (+1 s099: `Medicina de Família e Comunidade.md`, gold, indexado no RAG). Gaps: `TCE.md`, `Sistemas de Informação em Saúde.md`.
- **Erros & Cards:** **400 erros · 422 cards ativos** (taxonomia 98 temas, áreas canônicas). Os 16 cards do simulado s098 já cunhados (IDs 636-651, nos temas reais).
- **MFC (s099):** 31q/27a (87%); 3 erros cunhados (IDs 616-618). Cluster = lacuna em MCCP (ordem + nº de componentes). Q2 = estruturas familiares (banca-dependente).
- **Exantemáticas Rev. (s099):** 41q/35a (85%); 6 erros cunhados (IDs 619-624), **TODOS sarampo** = lacuna de conteúdo focal em **bloqueio vacinal/PPE** (dose zero, vacina×IG por idade/imunidade, bloqueio na suspeita, recrudescência 2018, PEES tardia). Armadilhas somadas ao resumo. 🔴 **Enunciado negativo reincidiu 2× (Q1/Q3)** — execução, não só conteúdo.
- **Cir. Infantil Pt3 Rev. (s099):** 33q/22a (67%); 11 erros cunhados (IDs 625-635, tema "Cirurgia Infantil"). Clusters: **criptorquidia** (palpável→orquidopexia / não palpável→laparoscopia), **escroto agudo** (torção testicular×apêndice×epididimite), **Wilms×neuroblastoma** (origem+metástase / idade), **hidronefrose fetal-neonatal** (unilateral→aguardar / grau3-4→renograma diurético), parafimose. 🔴 enunciado negativo reincidiu (Q3). Resumo `Cirurgia Infantil.md` (já existia, gold) **ampliado** com torção de apêndice, hidronefrose antenatal/neonatal §18.3, parafimose, hipospádia e hepatobiliar.

## Pendências ativas
Ratificar contrato Revisão Calibrada. Limpeza pós-curadoria (29 regra-vazia · Cirurgia Infantil). Reescrever `TCE.md` + `Sistemas de Informação em Saúde.md`. Áreas fracas: Hepato 57% · Dermato 67% · Cardio 67% · Otorrino 68% · Nefro 70% · Hemato 72%. *(s099 zerou: 16 cards do simulado ✅, resumo Cir. Infantil ✅, predição ENAMED 🗄️ arquivada.)*

---
*Histórico: history/INDEX.md · Macro: ESTADO.md · Erros do simulado: tmp/simulado_s098_erros.md · Curadoria: .agents/workflows/curar-cards.md*
