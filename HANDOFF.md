# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-07 -- S169 (Claude Code / Opus 5): 95 questoes (87,4%), 10 erros analisados, 60 cards drenados (divida FSRS zerada), 12 resumos tocados (10 novos/expandidos), substrato PubMed trocado, F78/F79/F79b/F80 no ledger*

## > Proximo passo imediato

1. 🔁 **Cards de 08/09: 41 agendados** -- destes, **23 sao os erros desta sessao voltando** (17 nota-1 + 6 nota-2). Drillar cedo; e a fila mais valiosa da semana.
2. 📚 **Questoes: seguir o sprint S17-S20.** Faltam ~630 das 725 (95 feitas em 07/09). Ritmo-alvo ~63,3q/dia p/ UERJ.
3. 🎯 **Revisao Direcionada JA ENTREGUE na s169** em 3 eixos (SUA/PALM-COEIN + manejo do sangramento · o paciente etilista, 16 erros do historico · inversao Wilms x neuroblastoma). Nao repetir; usar como material de abertura.

## Mix de cards 08-13/09 (decisao do usuario, s169)
**Regra: agendado + intake DIRIGIDO. Nao puxar volume indiscriminado.**
- **Carga agendada:** 41 (08) · 39 (09) · 20 (10) · 23 (11) · 24 (12) · 23 (13) = **170 em 6 dias**, media 28/dia. **Atrasados: 1.**
- **08-09/09:** so o agendado (41/39). Sao os relearning desta sessao + estreia de Cirurgia Infantil; nao somar novos.
- **10-13/09:** usar a folga com **intake dirigido a Cirurgia Infantil** (~40-50 cards no total, nao os 190 que a folga permitiria). Justificativa: fraqueza nº 1 (30 erros) + 9 de 10 cards do tema cairam na estreia de 07/09 = cluster com fundacao ausente. Puxar com `fsrs_queue --list --prevalencia --cluster`.
- 🔴 **Por que NAO puxar os 190 disponiveis:** estreia rendeu **22% de retencao** na s169. Volume indiscriminado vira nota 1 e infla a fila em 10 dias. Teto 60/dia segue valendo (CAP 1,5x = 90).
- ⚠️ **ENAMED 13/09 nao pede taper** -- e termometro desde a s159, o CRM e automatico. A prova decisiva e UERJ 01/11.

## Estado por frente
- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (55d). ENAMED 13/09 (6d) termometro.
- **Volume & Metas:** 6916 / 10400 (perf. ~78.9%). Hoje: 95. Ritmo-alvo ~63.3q/dia (55d p/ UERJ/MFC (prova 01/11)).
- **FSRS:** divida 0 atrasados + 1 p/ hoje -- pool 665 nunca introduzidos (entram <=60/dia).
- **Conteudo:** 136 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 970 erros registrados · 1353 cards ativos · 2 needs_qualitative na fila · taxonomia 275 temas. [derivado: db]
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem) [derivado: preparacao_estado]
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**.

## Ultima sessao -- s169 (2026-09-07): 95 QUESTOES + 60 CARDS + 10 RESUMOS DO SPRINT
**Questoes (95, 87,4%):** Diarreia 22q/86,4% · SUA 23q/69,6% · APS 50q/**96,0%**. 10 erros analisados e persistidos (#961-#972), 21 cards cunhados (#1526-#1546).
**Resumos:** 10 cunhados/expandidos por subagentes Sonnet em paralelo (Urologia 470 linhas, Pneumonias na Infancia, Diarreia, Tumores Anexiais, Etica Medica 37->364, DM na Gestacao 44->258, Pneumonias Bacterianas, HAS Parte 1, HAS Parte 3, Vitalidade Fetal) -- **cobertura escrita do sprint de ~30% para 100% dos temas**. Estadiamento FIGO preenchido com fonte auditada.
**Cards (60 drenados):** atrasados 87% · hoje 79% · **erros frescos 25%** · novos 22%. Retencao sem estreia 70%.
**Engenharia:** substrato `canonico` da governanca de evidencia trocado (`pubmedmcp` morto -> plugin `pubmed@life-sciences`), contrato v1.1; check 6 `[SPEC]` no linter de resumos + suite nova; `doc_drift` aceita server de plugin.

## Padroes de erro confirmados na s169
- 🔴 **O no do fluxograma nao e lido -- 3 disparos no mesmo dia.** SUA agudo: PA/FC medidas **APOS** o volume decidem clinico x cirurgico. Errou na prova (medroxiprogesterona) e no card (acido tranexamico), nas duas ficando no trilho clinico com paciente que ja falhou nele. Mesma habilidade de #947 (TC antes da via aerea, Trauma) e da fraqueza nº 3 (Sindromes Hipertensivas). **3 areas.**
- 🔴 **Achado saliente sequestra o diagnostico -- 4 disparos.** Disenteria->Salmonella; leite->APLV; macula rubra->malignidade; "cruza a linha media"->neuroblastoma. O dado que EXCLUI estava no enunciado nas 4.
- 🔴 **Inversao cristalizada Wilms x neuroblastoma:** 2 cards independentes, as 2 vezes respondeu neuroblastoma, as 2 vezes era Wilms. Regua: origem renal + hematuria + bom estado geral + metastase PULMONAR = Wilms.
- 🔴 **Carbamazepina marcada como "a proibida" na SAA pela 3a vez** (#335 25/06, #847 17/08, card #560 hoje). Ela e 2a linha VALIDA; as proibidas sao clozapina e clorpromazina (baixam o limiar convulsivo).
- **Pergunta composta:** parou na 1a metade em #1424, #610, #582, #583.

## Pendencias/observacoes ativas
- 🃏 **Reforja: 7 cards da s169** -- compostas #419, #1424, #582, #583 · binarias #1381, #1359 · **#367 inrespondivel** (dexis com contexto vazio) · #365 (frente embute a premissa). Somar aos 13 da s167 + 18 anteriores.
- 📚 **Frente MFC (Gusso + Duncan)** abre 14/09; rescope da grade pro formato UERJ. A fila de cards cai para ~10/dia a partir do 14, o que abre o espaco.
- 🔬 **Engenharia aberta (ledger):** **F80** (writers discordam de fuso: revlog/erros em UTC, bulk em local -- ja produziu conclusao errada em subagente), **F79b** (`card_self_sufficiency` cego a dexis+contexto vazio), **F78** (extracao de PDF perde figura em silencio, e a figura que sobrevive pode estar desatualizada), F79 RESOLVIDO. Antigos: F76, F71, F72, D5, D11, F63, F65-F69.
- 💉 Diretrizes a conferir nos resumos: Calendario Vacinal 2026, GINA 2026, Reanimacao SBP 2026, ATLS 11 (parcial), SINAN 2026. **SBC 2025 ja incorporada** (HAS Parte 1).
- 🔴 **Lacunas honestas dos resumos novos:** O-RADS, torcao anexial e massa anexial na gestante (Tumores Anexiais); PSI/PORT, criterios IDSA/ATS, criterios de Light, PAV/PAH (Pneumonias Bacterianas, fora do escopo do livro); telemedicina e escala de penalidades do CEM (Etica); contracepcao pos-parto (DMG). Declaradas, nao inventadas.
- ⚠️ Drive 43d sem sync (F72): a ordem confiavel e a lista verde homologada na s168.
- 📅 **Inscricao UERJ** fecha 01/10 (Cepuerj, R$ 380). Acao do usuario.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_169.md*
