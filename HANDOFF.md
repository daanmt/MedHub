# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-07 -- S168 (Claude Code / Opus 5): sprint S17-S20 decidido (725q ate 12/09) + aula-base de 13 temas publicada + excecao de 120 cards/dia revogada*

## > Proximo passo imediato

1. 🎯 **Receber as primeiras questoes do sprint.** O usuario vai resolver e trazer. 🔴 Registrar o volume com `registrar_sessao_bulk.py` **ANTES** de processar erros individuais (SSOT volumetrica, AGENTE §6). Depois, analise dos erros -- **1 subagent unico** por lote de ate ~15 erros, nao fan-out.
2. 🔁 **Depois das questoes: 60 cards.** Fila de hoje = 47 (15 atrasados + 14 agendados + **8 erros frescos do S7** + 10 novos); completar ate 60 com novos por prevalencia (`fsrs_queue --list --prevalencia --cluster`). Drillar os 8 frescos cedo. 🔴 Os 10 relearning da s166 (#245, #740, #741, #577, #1381, #736, #313, #706, #709, #1270) so regravam em sessao-calendario nova.
3. 📅 **Pico em 09/09: 34 cards agendados** (carga 07-13/09: 29/16/34/14/22/23/22). Puxar menos novos nesse dia.
4. 📚 **Aula-base do sprint JA ENTREGUE** -- `artifacts/aula-s17.html` ("Sprint S17-20", 13 temas, 331 KB, publicado). Nao refazer aula por bloco; usar o artifact como material de abertura de cada tema. **A secao final `#tarefas` traz as 47 listas do cronograma S17-S20 com link do caderno e contagem por tarefa** (sprint 725q destacado dentro de 1.423q totais) -- e de la que o usuario abre cada bloco.
5. **Ritual de execucao antes de cada bloco** (S7: 8 de 18 erros por execucao; corrigir so isso = ~90%): "qual dado aqui EXCLUI o que eu ia marcar?"; "a pergunta pede X **e** Y?"; enunciado negativo -> rotular cada alternativa V/F. Treinar em BLOCO DE QUESTOES, nao em card.
6. **Reforja pendente (13 da s167 + 18 anteriores):** compostas #175, #1041, #1424, #572, #581; binarias #151, #837; #526, #1112, #258, #910, #527, #513. Anteriores: #792, #4, #1117, 821, 702, 283, 505, 411, 570, 128, 705, 1360, 470, 1415, 1086, 1126. Dedup F67: (GO, Endometriose) -> (Ginecologia, Endometriose).
7. **Inscricao UERJ** fecha 01/10 (Cepuerj, R$ 380). Acao do usuario.
8. 🔬 **Engenharia aberta (ledger §4q):** **F77 NOVO** (`grade.json` nao guarda questoes por tarefa; o contrato manda ratear igual e o rateio erra de 16 a 50q -- a contagem real so existe re-parseando o PDF, S/M). F76 (`--record --reason` sem proveniencia, S), F71 (balanceador x provas.json), F72 (day_plan x snapshot stale), D5, D11; F63/F65-F69 seguem.

## Sprint S17-S20 (decisao do usuario, s168)
- **Mira: S20 completa = 725q ate 12/09.** Pior caso aceito: nao chegar com a S20 inteira. **Piso garantido: S17+S18 = 367q** (61q/dia).
- **24 tarefas verdes**, contagem real extraida do PDF (soma bate com o total em todas as semanas): **S17 172q** (6 tarefas) · **S18 195q** (7) · **S19 244q** (7) · **S20 114q** (4).
- A aula cobre **267 das 725** (37%) e **194 das 367** do piso (53%): Urologia 92q, SUA 65q, Diarreia 63q, Pneumonias Bact. 47q.
- 🔴 **Dois blocos "Revisao por Questoes" drillam frio:** Pre-Natal/Parto/Vitalidade Fetal (36q -- Vitalidade Fetal T e R fora do verde) e IC/HAS (43q -- HAS Revisao fora; cai na Cardiologia, 2a area mais fraca, 68,7%). O de SUS/APS/Etica (59q) esta lastreado.

## Estado por frente
- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (55d). ENAMED 13/09 (6d) termometro: S6 80% -> S7 82%.
- **Volume & Metas:** 6821 / 10400 (perf. ~78.8%). Hoje: 0. Ritmo-alvo ~65.1q/dia (55d p/ UERJ/MFC (prova 01/11)). Setembro: 190q em 6 dias; meta do mes pede ~62/dia.
- **FSRS:** divida 15 atrasados + 14 p/ hoje -- pool 675 nunca introduzidos (entram <=60/dia). **Teto 60 (max. 90 em divida); excecao de 120/dia REVOGADA na s168.**
- **Conteudo:** 128 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 958 erros registrados · 1332 cards ativos · 2 needs_qualitative na fila · taxonomia 274 temas. [derivado: db]
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem) [derivado: preparacao_estado]
- **Prevalencia:** `core/cronograma/prevalencia_enamed.json` (5 de 9 aulas). Pendentes: Ped II, Preventiva II (12/09), **Cirurgia II, CM II** -- e por isso que Urologia e Pneumonias Bact. nao aparecem la; ausencia de dado, nao voto contra.
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**.

## Ultima sessao -- s168 (2026-09-07): SPRINT DECIDIDO + AULA DE 13 TEMAS
**Planejamento:** mix 07-13/09 fechado (cards a 60, tardes as questoes). Precificacao da grade S17-S20 -- achado **F77**: `grade.json` so guarda o total da semana e o contrato manda ratear igual; a contagem por tarefa saiu de re-parsear o PDF e bate exatamente (293/380/449/301). Anomalia da APS 0q **resolvida**: a linha esta riscada no xlsx do usuario, os dois sinais concordam. Escopo verde homologado em 3 iteracoes (minhas 2 leituras de cor erraram; o usuario mandou as listas em texto).
**Aula-base:** `artifacts/aula-s17.html` de 4 -> **13 temas**, `<title>` "Sprint S17-20", 310 KB, mesma URL. Cunhada por **1 subagent fable** com brief travado (editar no lugar, nao publicar, preservar as 4 secoes originais, 1 unico `max-width`, ASCII limpo); verificacao independente antes de publicar passou em todos os eixos. **Alvo prioritario entregue:** tabela discriminadora **ENTRADA x ALOCACAO COMPARADA x COMPLETUDE** para o SUS (4a fraqueza persistente, 19 erros -- era falta de discriminador, nao de conteudo).
**Higiene:** excecao do sprint de 120 cards/dia revogada 6 dias antes do prazo, com lapide no `fsrs-management-contract` + `ESTADO.md` corrigido. Sem mudanca de codigo. `auto_check --changed` PASSED.
**Zero questoes e zero cards** -- a sessao foi planejamento + aula + contrato.

## Pendencias/observacoes ativas
- 📚 **Frente MFC (Gusso + Duncan)** -- abre 14/09. Rescope da grade pro formato UERJ em 14/09. A fila de cards cai para ~10/dia a partir do 14, o que abre o espaco.
- 🔴 **Lacunas honestas do artifact** (declaradas no rodape dele): estadios FIGO do CA de ovario, 10 grupos de Robson, minimo de servicos do Decreto 7.508 e a tabela SBC 2025 sairam como **figura** nos PDFs e nao extrairam -- conferir na lista se cair.
- 💉 Diretrizes novas a conferir nos resumos: Calendario Vacinal 2026 (Q89), GINA 2026 (Q79), Reanimacao SBP 2026, Dislipidemia 2025, ATLS 11 (parcial), SINAN 2026 (F69).
- ⚠️ Drive 43d sem sync (F72): a ordem confiavel e a lista verde que o usuario homologou na s168, nao a do `day_plan`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_168.md*
