# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-18 (tarde) -- **s186 (ENGENHARIA, janela 5 / onda 3)**: a fila inteira do `/ai-eng` zerada. **7 commits, harness verde em cada um, suite 811 -> 858.** R2 pousado e **F112 RESOLVIDO** (o operador drenou a previa e confirmou a regua); part-7 (painel) e part-8 (Drive congelado) entregues; **1.9(a)** fechado. 2 achados novos: **F114** e **F115**. 3 cards revisados (as 3 primeiras linhas sob a regua v2); zero questoes.*

> 🔧 **A proxima:** **F115** (spec; o `/ai-eng` deu GO depois do 1.9a) -- comprimento TOTAL do card nao tem gate. 🔴 **O limiar sai dos rotulos do operador (#92 p98 · #96 p99 marcados; #53 p57 nao), reportando precisao sobre as marcas dele -- nunca um numero escolhido.** Depois: **1.10**, que segue **SEM GO** dele.

## > Proximo passo imediato

1. ✅ **R2 ENTREGUE / F112 RESOLVIDO** (`bf7f7e9` + `d97fb32`). Regua nativa (`1 falhou · 2 com esforco · 3 lembrou · 4 sem esforco`), versionada por linha (`fsrs_revlog.regua_versao`, sem backfill: NULL = v1 por declaracao). Gate do operador cumprido pelo ATO -- ele drenou a previa e respondeu que as notas 4 foram "cards faceis", nao habito. Player com relearning `< 3`. **Parametros NAO adotados** (F114): `w3`/`w16` da visao remap sao o default intocado, porque aquela visao tem zero exemplo de Easy. Gatilho do re-fit: quando houver nota 4 v2 em volume que os mova (hoje: 3 linhas).
2. ✅ **part-7 (painel) e part-8 (Drive congelado) ENTREGUES em 18/09.** Painel: https://claude.ai/artifact/QctZqVoJriSviJetF8FYBQ (regenerar no fechamento, mesma url). Drive: planilha declarada abandonada (W1 **suspenso**, nao desligado; ultimo delta +977 preservado) e o sync REMOVIDO do codigo sob snapshot reversivel em `artifacts/snapshot-cronograma-drive-2026-07-26.json`.
3. 🃏 **Cards:** divida **72 atrasados + 31 p/ hoje**, pool 685. 🔺 **3 marcas de reforja novas do player (18/09): #92 e #96 "card longo" (p98 e p99 do baralho -- e o F115), #53 "pergunta composta".** 🔴 **Aula-base D10 de Acido-Base + Potassio ANTES de re-drillar os 6 segurados** (#595 #596 #598 #783 #786 #787). Baralho com acentuacao restaurada (1.796 correcoes) -- **#685 e #689 seguem com erro de portugues irregular** que regra nenhuma pega.
4. 📚 **Questoes (Fase 1, semana 1 = 14 tarefas, 369q; `plano.py --listar --semana 1`):** Prevencao Quaternaria (resumo) -> AMI (resumo) -> MFC extensivo Revisao (50) -> Saude do Idoso T+R (32) -> ... Bulk -> `plano.py --concluir ID --sessao <id>`; erros -> Autopsia.
5. ⚠️ **Acao do operador, pequena:** tirar **RAPS** da fila de "temas sem resumo". O conteudo existe (`## 4. Rede de Atencao Psicossocial (RAPS)` em `Psiquiatria Social e Reforma Psiquiatrica.md`) -- escrever outro produziria duplicado. Foi o F106 invertido.
6. 🗓️ Revisao de status por area (173 linhas) e rebalanceio da semana 3 seguem pendentes.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (44d; **inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7326 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~69.9q/dia (44d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 9 provas + ENAMED real 75. Proximo slot ~10/10 (cadencia de 4 semanas).
- **FSRS:** divida **72 atrasados + 31 p/ hoje** -- pool 685 nunca introduzidos (entram <=90/dia). Regua **v2 em vigor** desde 18/09; revlog misto (3.067 v1 + 3 v2). Parametros seguem DEFAULT por decisao (F114).
- **Conteudo:** 136 resumos. Preventiva: so 3/22 decks pagam aluguel na UERJ.
- **Erros & Cards:** 1041 erros · **1507 cards ativos** · 0 needs_qualitative na fila · taxonomia 302 temas. Reforja 288.
- **Cronograma:** `plano_tarefas` = SSOT, e agora **unica** -- o Drive foi congelado (part-8). W1 **suspenso**, nao desligado (ultimo delta +977). Visao consolidada: o painel.
- **Engenharia:** suite **858**; `auto_check` PASSED; ledger ate **F115** (§6z novo); `app/` nao alcanca mais `tools/` por `sys.path` (1.9a). Divida com o `/ai-eng`: so o **decision brief do R8/F111** (prazo 02/11) e o **1.10** (sem GO).
- **Posicao:** plano semana 1 (fase 1) · 0/14 tarefas da semana feitas [derivado: plano_tarefas]
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** (inscrito) · 📊 **Painel** (regenerar no fechamento, republicar na MESMA url): https://claude.ai/artifact/QctZqVoJriSviJetF8FYBQ

## Ultima sessao -- s185 (2026-09-17/18) -- ENGENHARIA DEDICADA (janela 4)

Detalhe em `history/session_185.md`. 3 filhos Opus 5 na onda 1 (~820k tokens, ~45 min, arquivos disjuntos); ondas 0 e 2 sem filho. **11 commits.** Todo fix nasceu com teste antes do codigo; em 3 casos o teste pegou defeito meu antes do commit. Toda operacao em lote passou pelo rito §10.7 (4 snapshots do banco). FSRS preservado do inicio ao fim (1543 / 3067 / 1543).

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- 🔴 **F113 PARCIAL:** 1.796 correcoes de acentuacao, mas o residuo e **irregular e nao fecha por regra** -- `apendicite`/`artrite`/`abortaria` estao CERTAS sem acento, `arteria`/`bacteria`/`etaria` precisam, e nenhum sufixo distingue. **#685** e **#689** seguem defeituosos. Exige lexico ou olho humano.
- 🔴 **Reportei "875 -> 0" e era FALSO:** medidor e corretor compartilhavam a lista de palavras. Detector independente mediu 897 (60,8%). *Quando o sensor e o remedio nascem do mesmo insumo, o verde nao e evidencia.*
- 🔴 **Eu corrompi 23 cards e reverti:** `-encia` virou verbo em substantivo. **"So-acento" nao e "semanticamente nulo" em portugues.** Pegou-se a olho, nao por gate.
- **F110** sem gate por construcao. **`db.get_db_metrics`** soma campo inflado e nao tem chamador vivo (superficie orfa). **R1:** nada adotado, `app/utils/fsrs.py` sem diff.
- Herdadas e vivas: F100 · F104 · F105 · F87 · F99 · F109 · F111 · G10 · G5 · F89 · F79b · F66 · F64 · eixo C do F81 · F80b.

## Pendencias/observacoes ativas

- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB. 💉 Diretrizes 2026 a conferir: Calendario Vacinal, GINA, ATLS 11 (parcial), SINAN.
- 📡 **Canal com o `/ai-eng` = `SendMessage` entre sessoes locais** (descobrir com `ListAgents`). 🔴 **O endereco MUDA a cada sessao dele** -- em 18/09 ele reiniciou (N=80) e avisou que mensagens ao endereco antigo se perdem. **Sempre responder pelo `from` da mensagem mais recente.** Hook grava as trocas em `history/exchange-log.jsonl`.
- 📬 **Devido a ele no proximo contato (2 itens):** (a) decision brief do **R8/F111** (<=10 linhas: o que muda no dia do operador, o que e reversivel; prazo 02/11); (b) **status do 1.10** -- toda clausula normativa vira CHECK nomeado ou marca literal "nao-verificavel" + data de revisao: **NAO INICIADO**. ⚰️ *O antigo item (b) -- 1.9(a) "NAO INICIADO", smell vivo em `app/utils/db.py:1046` -- morreu em 18/09/2026, no dia em que foi escrito: o 1.9(a) foi ENTREGUE na s186 (`98148fa`), `card_checks` migrou para `app/utils/` e `app/` nao alcanca mais `tools/` por `sys.path`. A linha sobreviveu a propria entrega e contradizia as linhas 2, 4 e 24 deste mesmo arquivo -- **a premissa morta no proprio portador**, a classe que a janela 5 fechou.*
- 🔴 **Erro meu, corrigido em 18/09:** respondi a ele que "1.9a/1.10 ja estavam feitos desde a s177". Estava errado -- **a numeracao diverge**. O `~~1.9~~`/`~~1.10~~` do nosso `§11` (G5 e `check_session_pointer`) nao sao os dele; o handoff dele de 10-09 numera outras duas coisas. **Ao responder item numerado dele, casar por CONTEUDO, nunca por numero** -- os dois inventarios sao independentes.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_185.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
