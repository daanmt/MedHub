# Session 099 -- Recalibração de cronograma (11 semanas) + política do simulado + 105q da S11 (20 cards) + resumo de MFC

**Data:** 2026-06-28 (estudo) · fechada em 2026-06-29
**Ferramenta:** Claude Code (Opus 4.8)
**Continuidade:** Sessão 098 (mesmo dia)

---

## O que foi feito

Sessão híbrida (engenharia de estado + estudo por questões). Duas frentes de governança e três blocos de conteúdo da Semana 11.

### 1. Recalibração da reta até o ENAMED
- **Verificação do horizonte:** **77 dias / 11,0 semanas exatas** até 13/09 (28/06->13/09); 13/09 = **semana-calendário 24** da grade (30 sem). **10 simulados pré-ENAMED restantes** (supersede o "11/14" antigo).
- **Decisão estratégica:** fechar **toda a grade de conteúdo (S11->S28 = 6.689q)** dentro dos 77 dias ≈ **87q/dia corridos**; o vão ENAMED->UERJ/USP fica para outro cronograma. Registrado em HANDOFF/ESTADO.
- **Bug de data corrigido:** `day_plan.py` e `performance.py` tinham `+1` no cálculo de dias (78 em vez de 77). Removido -- `dias = (marco - hoje).days` (hoje inclusive, dia da prova exclusivo).

### 2. Política do simulado -- fora do volume
- Decisão: questões de simulado **não contam como "feitas"** (não poluem cronograma/meta). A linha `Simulado` em `sessoes_bulk` persiste só como **ponto da série de predição ENAMED**.
- Mecanismo (1 ponto canônico): `performance.py::AREA_SIMULADO` + filtro `area<>'Simulado'` em `get_totais`/`get_por_area`/`get_questoes_do_mes` (herdado por `day_plan` e `cronograma --gap/--radar`) + `day_plan.q_hoje`. Volume oficial 4.153->4.112.

### 3. Estudo -- Semana 11 (105q em 28/06, 3 blocos)
- **MFC (Preventiva):** 31/27 (87%). 3 erros -> cards 616-618.
- **Doenças Exantemáticas (Rev.):** 41/35 (85%). 6 erros, **todos sarampo** -> cards 619-624.
- **Cirurgia Infantil Pt3 (Rev.):** 33/22 (67%). 11 erros -> cards 625-635 (tema "Cirurgia Infantil").
- **20 cards cunhados no total** (1 por erro, ancorados no elo), todos via `insert_questao.py` (não incrementam `questoes_realizadas`).

### 4. Conteúdo
- **Resumo gold criado:** `resumos/Preventiva/Medicina de Família e Comunidade.md` (a partir do PDF 19 do EMED), calibrado pela engenharia reversa (MCCP 47% -> ferramentas 31% -> PTS -> tipologia). Passou no linter + indexado no RAG.
- **Resumo reforçado:** `Doenças Exantemáticas.md` + 6 armadilhas de sarampo (bloqueio vacinal/PPE/dose zero/recrudescência/PEES) -- cumulativo.

## Padrões de erro identificados
- 🔴 **Enunciado negativo reincidiu 3×** (Exantemáticas Q1 EXCETO + Q3 INCORRETA; Cir. Infantil Q3 ERRADA) -- marca a afirmação VERDADEIRA. Ritual: rotular cada opção V/F e caçar a F.
- 🔴 **Wilms × neuroblastoma** (Cir. Q7, Q10): discriminar por origem (renal×adrenal/cruza-linha-média) + metástase (pulmão×osso/medula) + idade (~5a×<2a).
- 🔴 **Criptorquidia -- direção invertida 2×** (Q2, Q5): palpável->orquidopexia aberta; não palpável->laparoscopia.
- 🔴 **Escroto agudo** (Q1, Q11): torção (súbito/afebril/cremastérico abolido/Prehn−) × apêndice (insidioso/blue dot) × epididimite (febre/disúria/Prehn+).
- **Lacuna de conteúdo focal:** sarampo (bloqueio vacinal/PPE) e Cirurgia Pediátrica (67%, área fria recorrente).
- 2 questões banca-falhas: Cir. Q4 (anulável: hidrocele E hipospádia) e Q6 (gabarito contestado hepatoblastoma×cisto de colédoco).

## Artefatos criados/modificados
- `tools/day_plan.py`, `tools/performance.py` (off-by-one de dias + exclusão de `Simulado` do volume).
- `resumos/Preventiva/Medicina de Família e Comunidade.md` (novo, gold) · `resumos/Pediatria/Doenças Exantemáticas.md` (+armadilhas).
- `sessoes_bulk` (local): 3 linhas s099 (Preventiva 31/27, Pediatria 41/35, Cirurgia 33/22), todas 28/06.
- `questoes_erros` + `flashcards` (local): 20 erros + 20 cards (IDs 616-635).
- `review_log` (local): #53 directed_review de Doenças Exantemáticas.
- HANDOFF.md, ESTADO.md, memória `project_predicao_enamed` (refino s099) atualizados.

## Decisões tomadas
- **Alvo = grade inteira até o ENAMED** (S11->S28, 6.689q, ~87q/dia); vão pós-ENAMED é outro plano.
- **Simulado nunca entra no volume** -- só sinal de predição.
- 33q de Cirurgia reatribuídas a 28/06 (data corrigida no `sessoes_bulk`).

## Próximos passos (29/06)
- **Seguir a S11** (faltam 10 das 13 tarefas): Vulvovaginites, Imunizações, Sepse, Síndromes Hipertensivas, etc. Ritmo-alvo ~88q/dia p/ fechar a grade.
- **FSRS:** 12 cards vencem hoje (os de 28/06 maturando) + backlog -- drenar no `/revisar`.
- **Drill de execução:** ritual V/F no enunciado negativo; re-drill Wilms×neuro e criptorquidia.
- **Pendências de fundo (zeradas no fim da s099):** ✅ 16 cards do simulado s098 cunhados nos temas reais (IDs 636-651); ✅ resumo de Cirurgia Infantil **já existia** (gold) e foi **ampliado** (torção de apêndice, hidronefrose antenatal/neonatal §18.3, parafimose, hipospádia, hepatobiliar); 🗄️ **predição ENAMED ARQUIVADA** por decisão do usuário (simulado permanece só como registro fora do volume + erros->cards).
- Acumulado: **4.217** (clínico; simulado 41 fora do volume). Contadores finais: **400 erros · 422 cards ativos · 53 resumos**.
