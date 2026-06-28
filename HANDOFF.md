# HANDOFF.md — ESTADO OPERACIONAL CURTO
*Atualizado: 2026-06-28 ~16:00 — **s097: curadoria completa do backlog de flashcards (5 fases) + saneamento da taxonomia**. Disparada pelo feedback na revisão ("cards horríveis, sem contexto"). Taxonomia **115→98 temas** (áreas 100% canônicas); backlog **409→386 cards ativos** (29 fundidos + 37 reforjados no elo + 6 atomizados; 335 já ok). 2 workflows multi-agente (triagem 20 + cunhagem 10). Sem questões novas (engenharia). Acumulado **4.112 (41%)**.*

## ▶ Próximo passo imediato — s098
**A) Simulado de domingo (PENDENTE):** usuário fez offline; traz as **erradas** → analisar (elo metacognitivo) + cunhar cards (5 princípios, ancorados no erro).
**B) Semana 11 (estudo):** questões (foco execução de prova). Temas: Med. de Família, Exantemáticas (Rev), Cir. Infantil Pt3 (Rev), Vulvovaginites, Imunizações, Sepse, Síndromes Hipertensivas.
**C) Limpeza pós-curadoria:** 29 cards `ok` com regra-mestre vazia (passe rápido `recurate`); Cirurgia Infantil (26 cards fragmentados → mapear às partes EMED); `[bulk]` com questões (reclassificar = eixo de volume).

## Curadoria de cards (s097 — nova capacidade)
- **Workflow repetível:** `.agents/workflows/curar-cards.md` (5 fases). Régua = `/estilo-flashcard`.
- **Ferramentas:** `normalize_taxonomia.py` (saneia além do dedup), `insert_card_extra.py` (card extra em questao_id existente), `detect_clones.py` (near-dup por tema), `recurate_cards.py` (+`tipo`/+UTF-8), `audit_flashcard_quality.py` (+sinal `orfao_sem_andaime`).
- **Achado-mestre:** defeito de card é de **AUTORIA** (gerador não valida; linter cego ao semântico). Cura = **reforjar ancorado no erro**, não aposentar. O linter complementa o olho, não substitui (validado no par #528 TB × #531 viral).

## Revisão Calibrada / FSRS (s096)
- `/revisar` = PREPARAR (FSRS read-only, carimba `review_log`) + DRENAR (escreve FSRS). Contrato `revisao-calibrada-contract.md` **(ratificar após 1º uso real)**. Política de cards: teto 30/dia (agendados + 15 backlog).

## Estado por frente
- **Volume & Metas:** **4.112 / 10.000 (41%)** [teto 12k]. Perf. ~79,5%. Meta jun 4.500: déficit 388 (3 dias). Custo/q acum. R$0,77 · mês R$0,22.
- **Cronograma (SSOT `Cronograma.pdf`):** **Próxima = S11**; calendário nominal S13. `grade.json` em dia.
- **Conteúdo:** **52 resumos**. Gaps: reescrever `TCE.md` + `Sistemas de Informação em Saúde.md`.
- **Erros & Cards:** **364 erros · 386 cards ativos** (taxonomia **98 temas**, `UNIQUE(area,tema)`). FSRS backlog: vencidos + ~290 novos.

## Pendências ativas
Ratificar contrato Revisão Calibrada. Limpeza pós-curadoria (29 regra-vazia · Cirurgia Infantil · `[bulk]` c/ questões). Reescrever `TCE.md`. Re-drill bugs nº1. Sessão Cirurgia + integrar `/schedule`. Áreas fracas: Dermato 67% · Cardio 67% · Otorrino 68% · Nefro 70% · Hemato 72%.

---
*Histórico: history/INDEX.md · Macro: ESTADO.md · Curadoria: .agents/workflows/curar-cards.md*
