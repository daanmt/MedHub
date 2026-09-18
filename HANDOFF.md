# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-18 (madrugada) -- **s185 (ENGENHARIA DEDICADA, janela 4)**: ondas 0, 1 e 2 fechadas. **11 commits, harness verde em cada um, suite 714 -> 811.** 8 achados fechados (F102 F107 F103 F101 F98 F37 + F106 RETRATADO + F113 parcial), R1 entregue com os numeros do R2, PRD part-4 e part-6 entregues, riders R3-R6 commitados. **Operador decidiu R2 = (b) e destravou o part-8.** Zero questoes e zero cards hoje (sessao de engenharia).*

> 🔧 **Onda 3 e a proxima:** spec do **R2** (regua nova). 🔴 **Nao pousa sem mostrar a tela do player ao operador antes** -- muda o que ele le todo dia. Depois: **part-7** (painel) e **part-8** (congelar Drive, agora liberado).

## > Proximo passo imediato

1. 🔧 **R2 -- spec sob a opcao (b)** (decidida pelo operador em 17/09): regua nativa do FSRS (`1 falhou · 2 lembrou com esforco · 3 lembrou · 4 sem esforco`). Escopo no ledger **F112**: remap historico versionado **so na ENTRADA do Optimizer** (revlog imutavel), adaptador lendo `core/fsrs_params.json` com fallback default + versao da regua, `record_review` gravando a versao, **F9** (override de nota ja gravada) no mesmo caminho unico, **paridade como gate**. Baseline ja escrita: `tools/test_fsrs_blackout_curto.py::test_baseline_do_R2_intervalo_por_nota` -- quando o R2 pousar esse teste MUDA, e o diff dele e a evidencia. Riders de schema abertos: gravar `review_duration_ms` quando o player medir; **meta de retencao FICA em 0,90** ate haver duracao real.
2. 🧩 **part-7 (painel)** -> **part-8 (congelar Drive)**. O part-8 foi **destravado em 17/09** (o operador confirmou que nao reordena mais o xlsx a mao): remover `cronograma.py --sync-drive` **sob snapshot reversivel** (export + chave), nunca delecao seca.
3. 🃏 **Cards:** divida **75 atrasados + 31 p/ hoje**, pool 685. 🔴 **Aula-base D10 de Acido-Base + Potassio ANTES de re-drillar os 6 segurados** (#595 #596 #598 #783 #786 #787). Baralho com acentuacao restaurada (1.796 correcoes) -- **#685 e #689 seguem com erro de portugues irregular** que regra nenhuma pega.
4. 📚 **Questoes (Fase 1, semana 1 = 14 tarefas, 369q; `plano.py --listar --semana 1`):** Prevencao Quaternaria (resumo) -> AMI (resumo) -> MFC extensivo Revisao (50) -> Saude do Idoso T+R (32) -> ... Bulk -> `plano.py --concluir ID --sessao <id>`; erros -> Autopsia.
5. ⚠️ **Acao do operador, pequena:** tirar **RAPS** da fila de "temas sem resumo". O conteudo existe (`## 4. Rede de Atencao Psicossocial (RAPS)` em `Psiquiatria Social e Reforma Psiquiatrica.md`) -- escrever outro produziria duplicado. Foi o F106 invertido.
6. 🗓️ Revisao de status por area (173 linhas) e rebalanceio da semana 3 seguem pendentes.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (44d; **inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7326 / 10400 (perf. ~79.1%). Hoje: 0. Ritmo-alvo ~69.9q/dia (44d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 9 provas + ENAMED real 75. Proximo slot ~10/10 (cadencia de 4 semanas).
- **FSRS:** divida **75 atrasados + 31 p/ hoje** -- pool 685 nunca introduzidos (entram <=90/dia). 🔴 **F112 decidido: regua vai para a opcao (b) no R2.** Parametros seguem DEFAULT -- o R1 mediu, nada foi adotado.
- **Conteudo:** 136 resumos. Preventiva: so 3/22 decks pagam aluguel na UERJ.
- **Erros & Cards:** 1041 erros · **1507 cards ativos** · 0 needs_qualitative na fila · taxonomia 302 temas. Reforja 288.
- **Cronograma:** `plano_tarefas` = SSOT. **O boot le o plano** (part-4): o banner "Drive desatualizado" morreu depois de 42 dias abrindo toda sessao.
- **Engenharia:** suite **811**; `auto_check` PASSED; ledger ate F113 (§6y); indice de status **F1-F113 completo** (§3 + §3b novo).
- **Posicao:** plano semana 1 (fase 1) · 0/14 tarefas da semana feitas [derivado: plano_tarefas]
- **Datas:** fim da grade 09/10 · **UERJ 01/11** (inscrito).

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
- 📬 **Devido a ele no proximo contato (3 itens):** (a) decision brief do **R8/F111** (<=10 linhas: o que muda no dia do operador, o que e reversivel; prazo 02/11); (b) **status do 1.9(a)** -- refactor `db.py -> tools/card_checks` por `__file__`, por spec, raio > 7 writers: **NAO INICIADO**, o smell segue em `app/utils/db.py:1046`; (c) **status do 1.10** -- toda clausula normativa vira CHECK nomeado ou marca literal "nao-verificavel" + data de revisao: **NAO INICIADO**, e depende de **GO do operador**.
- 🔴 **Erro meu, corrigido em 18/09:** respondi a ele que "1.9a/1.10 ja estavam feitos desde a s177". Estava errado -- **a numeracao diverge**. O `~~1.9~~`/`~~1.10~~` do nosso `§11` (G5 e `check_session_pointer`) nao sao os dele; o handoff dele de 10-09 numera outras duas coisas. **Ao responder item numerado dele, casar por CONTEUDO, nunca por numero** -- os dois inventarios sao independentes.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_185.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
