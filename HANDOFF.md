# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-21 (~00h40) -- **s190 (ESTUDO + 1 fatia de engenharia)**: simulado **UERJ 2023 = 58/100** (39 chutes), Autopsia das 56 questoes publicada, trilha ajustada com OK dele, boot passou a entregar o PANORAMA (F126). A proxima sessao (s191) e de ESTUDO: cards, questoes e revisao do simulado.*

> 🔒 **O SELO:** `python tools/selo.py` -- tabela DERIVADA, nunca digitada. Ledger ate **F128** (F127/F128 DECLARADOS, aguardam triagem do `/ai-eng`); 2 GATE do operador seguem (F87, F111).

## > Proximo passo imediato

1. ✅ **(s191, 22/09) Racional das 21 recebido e PERSISTIDO:** 42 erros em `questoes_erros` (ids 1044-1085) + 52 cards; 14 chutes certos = `incerteza` no ledger; Q77 reclassificada como chute (39 -> 40). Autopsia corrigida em **URL nova** (abaixo). Leitura: 5/21 sao bug de execucao (Q11, Q30, Q74, Q99 discriminador visto e nao convertido; Q36 palavra-gatilho), 16/21 cobertura. 8 temas novos SEM resumo (Glomerulopatias, Vertigem, Videolaparoscopia, REMIT, Tumores de Partes Moles, Violencia Sexual/Aborto Legal, Tubo Neural, Prevencao Quaternaria) -- candidatos a `.md` quando a semana chegar.
2. 📚 **Ele esta lendo as 4 aulas-base D10 das atrasadas da S1 (publicadas 22/09)** e depois faz as listas: Hernias #38 (25q) · DMG #26 (19q) · Raciocinio diagnostico #877 (aula, sem lista -- marcar feita quando ler) · Topicos em Pediatria #96 (18q). **Ele traz as erradas de cada lista** -> `/analisar-questao` + `registrar_sessao_bulk` por bloco. Depois: S2 (21-27/09) = 474q + 62 atrasadas; fim de semana = **UERJ 2021** (60q). REMIT/cicatrizacao #530 e o maior cluster da prova (Q26, 29, 31, 35, 36).
3. 🃏 **Player de 22/09 com os 202 vencidos (pedido dele; teto 90 sobrescrito pelo operador)** -- ele faz ao longo do dia. Fechamento: `ArtifactData list sessoes/2026-09-22/notas` -> `tmp/player_2026-09-22_notas.json` -> `fsrs_queue.py --record-lote ... --lote tmp/player_2026-09-22.json` dry-run -> `--apply --expect N` -> Revisao Direcionada sobre as notas 1-2. Pool 690 + 52 novos. Aula-base D10 de Acido-Base + Potassio antes de re-drillar #595 #596 #598 #783 #786 #787.
4. 🔺 **Pedir a ele:** 2 cadernos **UERJ 2017-2020** no banco do EMED (S7, #1798/#1799, sem link) e, quando a semana chegar, cadernos pelo filtro do tema para as tarefas `sem_lista`/`caderno` do panorama.
5. 🔴 **Recalibrar a trilha NAO e reflexo de UMA prova (regra do `/ai-eng`, s189):** peso de bloco so pelo acerto ACUMULADO, a partir da 3a prova UERJ; na 1a recalibracao legitima entram JUNTO as faixas de prevalencia e a correcao do mapa (F128). O contraste CIR 8 x MFC 16 e candidato forte -- conferir na UERJ 2021. O que foi feito na s190 NAO e recalibracao: sao 6 linhas na camada manual (`trilha/custom.json`, com `racional`), abaixo.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (**inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7426 / 10400 (perf. ~78.8%). Hoje: 0. Ritmo do marco de volume ~72.5q/dia (41d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 10 provas + ENAMED real 75. **UERJ 2023 = 58** (CM 13 · CIR 8 · GO 10 · PED 11 · MFC 16; solidas 44/61 = 72%; chutes 14/39 ~ acaso). Leitura: COBERTURA, nao raciocinio; CIR = ciencia basica de Sabiston (15 chutes). Sequencia: ~~2023~~ -> 2021 -> 2022 -> 2024 -> 2025 -> 2026.
- **FSRS:** divida 153 atrasados + 25 p/ hoje -- pool 690 nunca introduzidos (entram <=90/dia). Regua **v2** desde 18/09. Parametros seguem DEFAULT (F114).
- **Conteudo:** 135 resumos em resumos/. [derivado: glob] `Neurologia/TCE.md` reescrito (F104) -- pendente de validacao clinica dele.
- **Erros & Cards:** 1041 erros registrados · 1512 cards ativos · 0 needs_qualitative na fila · taxonomia 302 temas. [derivado: db] Reforja **308 abertas**.
- **Cronograma:** `plano_tarefas` = SSOT; Fase 1 GERADA por `tools/trilha.py` (119 overrides, **34 da camada manual**). **Ajuste da s190 (OK dele em 21/09):** ENTRAM SCA/IAMCSST #777 (S3, aula-base + filtro) · pre-natal/parto/vitalidade fetal #22 (S4, 36q) · disturbios hipertensivos #325 (S6, 56q) · aleitamento/neonatal #354 (S5, 43q); SAEM para a S9 a 3a lista de DMG #51 e RPMO #749 (o TETO de 25% recusou somar: GO iria a 28,0% -- virou troca; GO fechou em 24,6%); MCCP e abordagem familiar viram REFRESH CURTO. Fase 1 = 3242q pendentes.
- **Engenharia:** suite **960**; `auto_check` PASSED; **boot = panorama** (`plano.py --panorama` + Plano do Dia inteiro; contrato de 5 secoes no hook, `test_boot_entrega_o_panorama`). Item 1.10: 127 orfas (catraca).
- **Posicao:** plano semana 1 (fase 1) · 1/5 tarefas da semana feitas · cota ~77q/dia ate 27/09 · Fase 1 ~79.1q/dia [derivado: plano_tarefas]
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** · 🩺 **Autopsia UERJ 2023 (v2, elos fechados 22/09)**: https://claude.ai/artifact/GjpAqF9HVTTDVRUZLkutyf (⚰️ a URL antiga XLCeFfczezCANirt5ykdvP ficou stale) · 🃏 Player 22/09 (202 cards): https://claude.ai/artifact/P8qiJD3ACcofhfnkJaYU8Y · 📚 Aulas-base 22/09: Hernias https://claude.ai/artifact/Vezrca1JEyMdYF2gtwpSxv · DMG https://claude.ai/artifact/RCPurGRw8DnRiMinuDN4ga · Raciocinio dx https://claude.ai/artifact/DtEYHEokhcZgpFoWJYBXY4 · Topicos Ped https://claude.ai/artifact/RtopChfqqcPPWvZmArfuUA · 📊 Painel: https://claude.ai/artifact/QctZqVoJriSviJetF8FYBQ · 🩻 Raio-X UERJ (foto de 18/09): https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc

## Ultima sessao -- s190 (2026-09-20/21) -- UERJ 2023 = 58 e a Autopsia; o boot vira panorama

Detalhe em `history/session_190.md`. (1) Overview pedido por ele virou feature: `plano.py --panorama` + hook de boot sem o corte de 8 linhas (F126, `442d924`). (2) Ele deu **autonomia total de git** (commit + push sem pedir). (3) Video de analise da UERJ absorvido e cruzado com o nosso mapa (concorda no grupo, diverge no tema; ignora TB/Infecto). (4) Simulado: PDF anotado a tinta lido por vetor + pixel + olho; 56 -> 58 com Q32/Q56 declaradas depois; reconferido por 3 lentes quando ele duvidou do numero. (5) Autopsia: fan-out de 5 filhos Opus (regra do Simulado), 56 questoes, 43 de base ausente, 3 contestaveis (Q16, Q73, Q77). (6) Trilha ajustada como TROCA.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- ⚰️ *(fechada em 22/09, s191)* A Autopsia deixou de ser so leitura: 42 erros registrados, 52 cards cunhados, 21 elos fechados pelo racional. **Sobrevive:** das 56 fontes, so 5 foram ABERTAS (as outras sao referencia canonica, rotuladas na pagina); Q16/Q73/Q77 seguem CONTESTAVEIS e foram registradas SEM `status banca-divergente` (a lacuna do aluno e real; os cards ensinam o consenso, nao o gabarito); o teste F38 ganhou a instancia 20/09 declarada (mesmo precedente do ENAMED 13/09).
- 🔴 **O mapa UERJ erra rotulo (F128):** Q8/2023 esta como Tuberculose e e sindrome nefrotica; a prevalencia de TB (13) inclui essa. Consumir em faixas; corrigir JUNTO da 1a recalibracao.
- 🔴 **O piso/teto da trilha e conferido na regua do PROPRIO gerador**; a entrada e snapshot de 18/09 (progresso posterior muda status, nunca prioridade). Overrides manuais NAO passam pelo `cap_listas` semanal: S5 ficou com 720q.
- 🔴 **Duas autoridades que sobraram:** `--mover` fora da Fase 1 e `plano_custom.json` x trilha -- decisao unica, depois de 02/11 (`/ai-eng`).
- **F113 PARCIAL** (#689), **F110** sem gate, **F78**/**F2** DECLARADOS. Backlog de engenharia (depois de 02/11): F122, F127 (`--corrigir` no registrar), redesenho do `--mover`, terminal da reserva, F111, fatia 6.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB. 💉 Diretrizes 2026 a conferir: Calendario Vacinal, GINA, ATLS 11 (parcial), SINAN.
- 🔴 **Ao responder item numerado do `/ai-eng`, casar por CONTEUDO, nunca por numero.** 📡 Canal = `SendMessage` entre sessoes locais (`ListAgents`); responder pelo `from` da mensagem mais recente.
- 🔴 **Brief de subagente com conteudo clinico se escreve COM acentos** (4 de 5 filhos imitaram o brief sem acento, s190) e o insumo se valida ANTES do spawn. Regex sempre em string RAW; script de patch longo = arquivo no scratchpad, nunca heredoc com acento (o Git Bash corrompe).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_190.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md * Selo: `python tools/selo.py`*
