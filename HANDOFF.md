# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-22 (~23h) -- **s192 (ENGENHARIA)**: MedHub HUB v0 no ar -- UMA pagina fixada com as abas Cards / Aulas / Painel (linha 3); o rito inteiro republica nela (F90, contrato `revisao-calibrada` v1.7). A parte 2 (gravacao das notas do hub) ficou PENDENTE com gate no rito. A s193 abre pela parte 2 e depois pelo que ele traz (listas + drill no hub).*
> 🏠 **MedHub HUB (1 artifact, fixado): https://claude.ai/artifact/3RksMfkzNWYSQD7D6JXNEr** -- abas Cards / Aulas / Painel. Republicar SEMPRE nesta URL (rito: `/revisar` "DRENAR no player"; `registrar-sessao` §6); `artifact-deleted` = recriar completo e REPORTAR aqui.

> 🔴 **ABRIR A s193 POR AQUI:** (0) **PARTE 2 do hub ANTES de gravar qualquer nota do hub** -- spec `.vibeflow/specs/medhub-hub-v0-part-2.md` (relogio da revisao = ts da nota, idempotencia exata, quarentena); parcial em `tmp/medhub-hub-v0-part-2-wip.patch`; depois `/vibeflow:audit` das partes 1-3. (a) `ArtifactData list` em `sessoes/2026-09-22h/notas` NO HUB -- notas ficam la ate a parte 2 (gate: nao gravar, nao trocar o lote, nao podar). (b) Feedback das listas bloco a bloco: `registrar_sessao_bulk` -> `plano.py --concluir` -> `/analisar-questao` com o racional DELE.

> 🔒 **O SELO:** `python tools/selo.py` -- tabela DERIVADA, nunca digitada. Ledger ate **F128** (F127/F128 DECLARADOS, aguardam triagem do `/ai-eng`); 2 GATE do operador seguem (F87, F111).

## > Proximo passo imediato

1. 🏠 **(s192) Hub no ar, ele aprovou ("simplesmente excelente") e definiu como PADRAO:** nada de player, painel ou aula como artifact avulso -- tudo e arquivo do hub, republicado na URL da linha 3. Lote `2026-09-22h` = 220 cards (210 vencidos + 10 novos). Pendentes: parte 2 (item 0 acima) e a parte 4 (sessao nova rodando o rito; drill de >= 20 no celular abrindo 1 aula no meio; 2 fechamentos).
2. 📚 **Ele leu (ou esta lendo) as 4 aulas-base D10 das atrasadas da S1 (22/09)** e faz as listas na sequencia: Hernias #38 (25q) · DMG #26 (19q) · Raciocinio diagnostico #877 (aula, sem lista -- `--concluir` quando ele confirmar a leitura) · Topicos em Pediatria #96 (18q). **Ele traz o feedback esmiucado por lista** (como pensou, chute ou nao) -> bloco a bloco: `registrar_sessao_bulk` -> `plano.py --concluir` -> `/analisar-questao` por erro. Depois: S2 (21-27/09) = 474q + 62 atrasadas; fim de semana = **UERJ 2021** (60q). REMIT/cicatrizacao #530 e o maior cluster da prova (Q26, 29, 31, 35, 36).
3. 🃏 **Os artifacts avulsos de 22/09 estao SUPERADOS pelo hub:** player P8qiJD3ACcofhfnkJaYU8Y (a unica nota, card #92, ja gravada) e as 4 aulas -- ele os apaga SO DEPOIS de abrir 1 aula pelo hub no celular (ordem do `/ai-eng`). Card **#92** = conteudo clinico INVERTIDO (vinheta de CoAo critica, cianose diferencial atribuida a TGA): marcado para reforja. Aula-base D10 de Acido-Base + Potassio antes de re-drillar #595 #596 #598 #783 #786 #787.
4. 🔺 **Pedir a ele:** 2 cadernos **UERJ 2017-2020** no banco do EMED (S7, #1798/#1799, sem link) e, quando a semana chegar, cadernos pelo filtro do tema para as tarefas `sem_lista`/`caderno` do panorama.
5. 🔴 **Recalibrar a trilha NAO e reflexo de UMA prova (regra do `/ai-eng`, s189):** peso de bloco so pelo acerto ACUMULADO, a partir da 3a prova UERJ; na 1a recalibracao legitima entram JUNTO as faixas de prevalencia e a correcao do mapa (F128). O contraste CIR 8 x MFC 16 e candidato forte -- conferir na UERJ 2021. O que foi feito na s190 NAO e recalibracao: sao 6 linhas na camada manual (`trilha/custom.json`, com `racional`), abaixo.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (**inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7426 / 10400 (perf. ~78.8%). Hoje: 0. Ritmo do marco de volume ~74.3q/dia (40d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 10 provas + ENAMED real 75. **UERJ 2023 = 58** (CM 13 · CIR 8 · GO 10 · PED 11 · MFC 16; solidas 44/60 = 73%; chutes 14/40 ~ acaso -- Q77 virou chute declarado em 22/09). Leitura: COBERTURA, nao raciocinio (5/21 racionais = bug de execucao); CIR = ciencia basica de Sabiston (15 chutes). Sequencia: ~~2023~~ -> 2021 -> 2022 -> 2024 -> 2025 -> 2026.
- **FSRS:** divida 178 atrasados + 24 p/ hoje -- pool 742 nunca introduzidos (entram <=90/dia). Regua **v2** desde 18/09. Parametros seguem DEFAULT (F114). Lote do hub `2026-09-22h` (220) no ar; notas do hub NAO sao gravadas antes da parte 2.
- **Conteudo:** 135 resumos em resumos/. [derivado: glob] `Neurologia/TCE.md` reescrito (F104) -- pendente de validacao clinica dele. 8 temas novos SEM resumo (item 1). Hernias e Topicos em Pediatria tambem sem `.md`: as armadilhas dessas aulas vivem so no artifact (fronteira de SSOT da skill `/aula-base`).
- **Erros & Cards:** 1083 erros registrados · 1564 cards ativos · 0 needs_qualitative na fila · taxonomia 317 temas. [derivado: db] Reforja **308 abertas**.
- **Cronograma:** `plano_tarefas` = SSOT; Fase 1 GERADA por `tools/trilha.py` (119 overrides, **34 da camada manual**). **Ajuste da s190 (OK dele em 21/09):** ENTRAM SCA/IAMCSST #777 (S3, aula-base + filtro) · pre-natal/parto/vitalidade fetal #22 (S4, 36q) · disturbios hipertensivos #325 (S6, 56q) · aleitamento/neonatal #354 (S5, 43q); SAEM para a S9 a 3a lista de DMG #51 e RPMO #749 (o TETO de 25% recusou somar: GO iria a 28,0% -- virou troca; GO fechou em 24,6%); MCCP e abordagem familiar viram REFRESH CURTO. Fase 1 = 3242q pendentes.
- **Engenharia:** suite **986**; `auto_check` PASSED; **boot = panorama** (`plano.py --panorama` + Plano do Dia inteiro; contrato de 5 secoes no hook, `test_boot_entrega_o_panorama`). Item 1.10: 127 orfas (catraca).
- **Posicao:** plano semana 1 (fase 1) · 1/5 tarefas da semana feitas · cota ~90q/dia ate 27/09 · Fase 1 ~81.0q/dia [derivado: plano_tarefas]
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** · 🩺 **Autopsia UERJ 2023 (v2, elos fechados 22/09)**: https://claude.ai/artifact/GjpAqF9HVTTDVRUZLkutyf (⚰️ a URL antiga XLCeFfczezCANirt5ykdvP ficou stale) · 🃏📚📊 **Cards, aulas-base e painel = abas do HUB** (linha 3). ⚰️ *Avulsos de 22/09, superados pelo hub:* player P8qiJD3ACcofhfnkJaYU8Y (a unica nota, card #92, ja gravada) e as 4 aulas (Vezrca1J, RCPurGRw, DtEYHEok, RtopChfq) -- ele apaga as aulas avulsas SO DEPOIS de abrir 1 aula pelo hub no celular (ordem do `/ai-eng`) · 🩻 Raio-X UERJ (foto de 18/09): https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc

## Ultima sessao -- s192 (2026-09-22, ~19h30-23h) -- ENGENHARIA: MedHub HUB v0

Detalhe em `history/session_192.md`. (1) 1o ato: a nota do player de 22/09 gravada + #92 para reforja. (2) PRD sem discover + 4 specs. (3) Parte 1 `c299eb4` (hub.py + hub.html, 26 testes). (4) Parte 3 `d42a0af` (rito F90, contrato v1.7, 1o publish com regras de `db`; DoD 7 provada). (5) Parte 2 interrompida (o filho quebrou o `record_review` no meio): parado, parcial salvo, gate no rito. Suite 986.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- ⚰️ *(fechada em 22/09, s191)* A Autopsia deixou de ser so leitura: 42 erros registrados, 52 cards cunhados, 21 elos fechados pelo racional. **Sobrevive:** das 56 fontes, so 5 foram ABERTAS (as outras sao referencia canonica, rotuladas na pagina); Q16/Q73/Q77 seguem CONTESTAVEIS e foram registradas SEM `status banca-divergente` (a lacuna do aluno e real; os cards ensinam o consenso, nao o gabarito); o teste F38 ganhou a instancia 20/09 declarada (mesmo precedente do ENAMED 13/09).
- 🔴 **O mapa UERJ erra rotulo (F128):** Q8/2023 esta como Tuberculose e e sindrome nefrotica; a prevalencia de TB (13) inclui essa. Consumir em faixas; corrigir JUNTO da 1a recalibracao.
- 🔴 **O piso/teto da trilha e conferido na regua do PROPRIO gerador**; a entrada e snapshot de 18/09 (progresso posterior muda status, nunca prioridade). Overrides manuais NAO passam pelo `cap_listas` semanal: S5 ficou com 720q.
- 🔴 **Duas autoridades que sobraram:** `--mover` fora da Fase 1 e `plano_custom.json` x trilha -- decisao unica, depois de 02/11 (`/ai-eng`).
- **F113 PARCIAL** (#689), **F110** sem gate, **F78**/**F2** DECLARADOS. Backlog de engenharia (depois de 02/11): F122, F127 (`--corrigir` no registrar), redesenho do `--mover`, terminal da reserva, F111, fatia 6.
- 🏠 ⚰️ *(entregue como v0 na s192)* **MedHub HUB:** o que segue aberto e so a parte 2 (gravacao) e a parte 4 (medicao). v1a = RD como arquivo derivado de `history/` (antes de 01/11); v1b = colecao `comandos` + `/loop` (depois de 01/11). 🔴 **O owner passa por cima das regras do `db`** (conta compartilhada): a fronteira real e o writer.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB. 💉 Diretrizes 2026 a conferir: Calendario Vacinal, GINA, ATLS 11 (parcial), SINAN.
- 🔴 **Ao responder item numerado do `/ai-eng`, casar por CONTEUDO, nunca por numero.** 📡 Canal = `SendMessage` entre sessoes locais (`ListAgents`); responder pelo `from` da mensagem mais recente.
- 🔴 **Brief de subagente com conteudo clinico se escreve COM acentos** (4 de 5 filhos imitaram o brief sem acento, s190) e o insumo se valida ANTES do spawn. Regex sempre em string RAW; script de patch longo = arquivo no scratchpad, nunca heredoc com acento (o Git Bash corrompe).

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_190.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md * Selo: `python tools/selo.py`*
