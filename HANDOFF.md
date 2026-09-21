# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-21 (~00h40) -- **s190 (ESTUDO + 1 fatia de engenharia)**: simulado **UERJ 2023 = 58/100** (39 chutes), Autopsia das 56 questoes publicada, trilha ajustada com OK dele, boot passou a entregar o PANORAMA (F126). A proxima sessao (s191) e de ESTUDO: cards, questoes e revisao do simulado.*

> 🔒 **O SELO:** `python tools/selo.py` -- tabela DERIVADA, nunca digitada. Ledger ate **F128** (F127/F128 DECLARADOS, aguardam triagem do `/ai-eng`); 2 GATE do operador seguem (F87, F111).

## > Proximo passo imediato

1. 🔴 **ELE TRAZ O RACIONAL dos erros da UERJ 2023 -- 21 perguntas, 1 linha cada** (texto completo na secao "Perguntas em aberto" da Autopsia e em `artifacts/autopsia-2026-09-20.json`, campo `pergunta_ao_aluno`). Resumo:
   - **CM:** Q8 calculou o GASA (2,0-1,3=0,7)? por que circulou a amilase 80? · Q9 Janeway/Roth disseram algo? · Q11 por que TB e nao criptococo (circulou glicorraquia "normal")? · Q13 massa cistica = vesicula ou figado? · Q14 febre 38,8 + borramento perirrenal mudaram o plano? · Q16 RM pelo nistagmo ou por nao lembrar que Dix-Hallpike e o exame?
   - **CIR:** Q30 o que "NAO obstruido" mudou na flora? · Q36 por que celula T antes do neutrofilo (a C estava com "?")?
   - **GO:** Q43 que estadio FIGO deu a "6 cm limitada ao colo"? · Q45 o "desejo de gestar" entrou no filtro? · Q47 considerou origem endometrial do AGC? · Q50 hesitou entre menopausa materna e idade > 30? · Q51 calculou a subida do beta (145->554 em 72h) x zona discriminatoria? · Q56 eliminou A e B por principio antes de chutar? · Q57 como foi de confusao+ataxia+nistagmo a miastenia? · Q58 classificou a desaceleracao antes de escolher a causa?
   - **PED:** Q73 cipro por esquema antigo ou por nao lembrar o PCDT? · Q74 leu "nega antibiotico ha 2 meses"? · Q77 descartou a A (antibiotico contraindicado) por que?
   - **MFC:** Q91 "mimetizar" = doenca que ACOMPANHA ou que PRODUZ o quadro? · Q99 calculou o IMC (118/4 = 29,5) antes de marcar "obesidade"?
2. 🔴 **So DEPOIS do racional: persistir.** `insert_questao.py` por erro (42) + `habilidades.py --add` para os 14 chutes certos; triar os 81 cards CANDIDATOS da Autopsia pelo teste de regenerabilidade (nenhum foi cunhado). Ate la o `auto_check` avisa F38 para 2026-09-20 (42 erros em `sessoes_bulk.id=130`, zero linhas em `questoes_erros`) -- divida DECLARADA, nao surpresa.
3. 📚 **Estudo, na ordem do boot (panorama):** atrasadas da S1 -- Hernias #38 (25q, aula-base ANTES: 2 chutes na prova) · DMG #26 (19q) · aula de raciocinio diagnostico #877 (Q97 errada no chute) · Topicos em Pediatria #96 (18q). S2 (21-27/09) = 474q + 62 atrasadas; fim de semana = **UERJ 2021** (60q). Tema de chute = aula-base ANTES da lista. REMIT/cicatrizacao #530 e o maior cluster da prova (Q26, 29, 31, 35, 36).
4. 🃏 **Cards:** divida **153 atrasados + 25 p/ hoje**, pool 690, teto 90. Aula-base D10 de Acido-Base + Potassio antes de re-drillar #595 #596 #598 #783 #786 #787.
5. 🔺 **Pedir a ele:** 2 cadernos **UERJ 2017-2020** no banco do EMED (S7, #1798/#1799, sem link) e, quando a semana chegar, cadernos pelo filtro do tema para as tarefas `sem_lista`/`caderno` do panorama.
6. 🔴 **Recalibrar a trilha NAO e reflexo de UMA prova (regra do `/ai-eng`, s189):** peso de bloco so pelo acerto ACUMULADO, a partir da 3a prova UERJ; na 1a recalibracao legitima entram JUNTO as faixas de prevalencia e a correcao do mapa (F128). O contraste CIR 8 x MFC 16 e candidato forte -- conferir na UERJ 2021. O que foi feito na s190 NAO e recalibracao: sao 6 linhas na camada manual (`trilha/custom.json`, com `racional`), abaixo.

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
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** · 🩺 **Autopsia UERJ 2023**: https://claude.ai/artifact/XLCeFfczezCANirt5ykdvP · 📊 Painel: https://claude.ai/artifact/QctZqVoJriSviJetF8FYBQ · 🩻 Raio-X UERJ (foto de 18/09): https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc

## Ultima sessao -- s190 (2026-09-20/21) -- UERJ 2023 = 58 e a Autopsia; o boot vira panorama

Detalhe em `history/session_190.md`. (1) Overview pedido por ele virou feature: `plano.py --panorama` + hook de boot sem o corte de 8 linhas (F126, `442d924`). (2) Ele deu **autonomia total de git** (commit + push sem pedir). (3) Video de analise da UERJ absorvido e cruzado com o nosso mapa (concorda no grupo, diverge no tema; ignora TB/Infecto). (4) Simulado: PDF anotado a tinta lido por vetor + pixel + olho; 56 -> 58 com Q32/Q56 declaradas depois; reconferido por 3 lentes quando ele duvidou do numero. (5) Autopsia: fan-out de 5 filhos Opus (regra do Simulado), 56 questoes, 43 de base ausente, 3 contestaveis (Q16, Q73, Q77). (6) Trilha ajustada como TROCA.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- 🔴 **A Autopsia e LEITURA, nao registro:** 0 erros da UERJ 2023 em `questoes_erros`, 0 cards cunhados; os vereditos de elo dos erros sem chute estao `pendente` ate o racional. Das 56 fontes, so 5 foram ABERTAS na sessao (as outras sao referencia canonica, rotuladas na pagina).
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
