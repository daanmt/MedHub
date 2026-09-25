# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-24 (~22h45) -- **s195 (ESTUDO + ENGENHARIA)**, encerrada pelo operador ("vou conferir as aulas e na proxima sessao te trago o feedback"): lote `2026-09-24a` drenado (90 cards: 72 notas gravadas, 18 defeitos; as 90 do hospital se perderam num reload -- F130), hub **Version 5** (aba Aulas = quadro POR SEMANAS do plano; aulas concluidas arquivadas), player com espelho local das notas, fila retendo card com defeito marcado (F132), export de vespera honesto (`--para`, F131). Fila de 25/09 (60 cards) ja no ar. Backend MANUAL (decisao dele).*
> 🏠 **MedHub HUB (1 artifact, fixado): https://claude.ai/artifact/3RksMfkzNWYSQD7D6JXNEr** -- abas Painel / Aulas / Cards. Republicar SEMPRE nesta URL (rito: `/hub-backend`, `/revisar` "DRENAR no player", `registrar-sessao` §6); `artifact-deleted` = recriar completo (capabilities de 3 regras, abaixo) e REPORTAR aqui. **Lote vivo `2026-09-26a`** = colecao `sessoes/2026-09-26a/notas` (56 cards, fila de vespera exportada 25/09 ~18h com `--para 2026-09-26`; teto novo 100/150; 13 retidos por marca de reforja nova). (o `sessao` nao e a data de hoje; trocou o lote, troca aqui). Colecoes `2026-09-22h` (220) e `2026-09-24a` (90) PODADAS no fechamento (releitura = 0 novas nas duas). Aulas Pediatria e DMG ja em TOPICOS; ele vai trazer o feedback.

> 🔴 **ABRIR A s196 POR AQUI -- 1o ATO:** quando ele disser que drenou o `2026-09-25a`, UM tique do `/hub-backend` (`--precisa-publicar` -> gravar -> fila no SALDO do dia -> publish -> `--confirmar` -> linha 3 daqui). Backend e MANUAL desde a s195 ("manual, por hora"): sem `/loop`, tique so quando ele avisa. Saldo do dia zerado e ele vai drenar de manha sem o PC = fila de vespera com `--export-player --para <amanha> --sessao <amanha>a` (nunca `--limit`). Capabilities do hub (so o agente principal passa, e so se recriar): `{db: {rules: [{path: "", read: "view", write: "admin"}, {path: "sessoes", write: "interact"}, {path: "quadro", write: "interact"}]}}`.

> 🔒 **O SELO:** `python tools/selo.py` -- tabela DERIVADA, nunca digitada. Ledger ate **F132** (F130/F131/F132 RESOLVIDOS na s195; F129 PARCIAL; F127/F128 DECLARADOS); 2 GATE do operador seguem (F87, F111).

## > Proximo passo imediato

1. 📚 **Ele traz questoes + cards.** Listas em aberto (panorama S2, 21 tarefas/511q; 3 atrasadas da S1): DMG #26 (19q) · Topicos em Pediatria #96 (18q) · Raciocinio diagnostico #877 (aula -- riscar no quadro do hub conclui por `plano.py --concluir 877 --leitura`). Bloco a bloco: `registrar_sessao_bulk --tarefa` -> `plano.py --concluir` -> `/analisar-questao` com o racional DELE (perguntar se acertou no chute: `incerteza`). Fim de semana = **UERJ 2021** (60q).
2. 🧠 **Revisao Direcionada pendente:** lote de 24/09 (72 notas: 51 x nota 4, 8 x nota 1). Nota 1 = as 5 hernias novas #1720/#1723/#1729/#1730/#1731 (relearning legitimo, voltam 25/09 -- ele elogiou os cards), Nefro #598 (4o 1 seguido: Acido-Base) e #827, #1456. Cluster Nefro segue: aula-base D10 de Acido-Base + Potassio ANTES de re-drillar (#595/#685/#783/#787 deram 4 em 24h -- e curto prazo, nao consolidacao).
3. 🃏 **REFORJA = proxima frente de conteudo (F129/F132):** 63 cards RETIDOS da fila por marca humana aberta (56 do player + 6 de sessao/ledger) -- nao voltam ate a marca fechar. Padroes DELE: pergunta composta/dupla, circular, aberta/ampla, card longo/contexto longo, portugues. Regua nova = os cards de hernia #1729-#1733 (contexto 1 frase, 1 pergunta, verso 15-150 chars). Reforjar > aposentar; `reforja.py --fechar` so com o predicado limpo. Acento (~749) segue para o `/ai-eng`.
4. 📊 **Ritmo e o alarme real:** 17,9 q/dia (7d) x 77,6 necessarios ate 01/11 (painel). Cobertura > refinamento.
5. ✂️ **Contrato novo (24/09): TUDO MAIS CURTO -- e aulas em TOPICOS.** Pediatria e DMG ja reescritas (`aula-base.md` §5); Raciocinio diagnostico (#877) ainda no formato antigo: reescrever antes de ele ler. Palavras dele: cards, aulas, analises e reports "muito longos... carga cognitiva". Card: frente = 1 pergunta, verso 1-2 linhas, regra/armadilha 1 frase; aula: degrau de 2-4 frases; chat: o dado primeiro. Memoria `feedback_conteudo_curto_carga_cognitiva`.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (**inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7451 / 10400 (perf. ~78.8%). Hoje: 25. Ritmo do marco de volume ~75.6q/dia (39d p/ UERJ/MFC (prova 01/11)). [derivado: day_plan --handoff-block]
- **Simulados:** 10 provas + ENAMED real 75. **UERJ 2023 = 58** (solidas 44/60). Sequencia: ~~2023~~ -> 2021 -> 2022 -> 2024 -> 2025 -> 2026.
- **FSRS:** divida 49 atrasados + 34 p/ hoje -- pool 730 nunca introduzidos (entram <=90/dia). [derivado] 23/09: 159 revisoes gravadas (teto 90 -> saldo 0). Regua v2; parametros DEFAULT (F114). O export corta no SALDO do dia desde a s194.
- **Conteudo:** 135 resumos em resumos/. [derivado: glob] Hernias/DMG/Topicos em Pediatria sem `.md` (armadilhas vivem nos cards e nas aulas do hub).
- **Erros & Cards:** 1087 erros registrados · 1569 cards ativos · 0 needs_qualitative na fila · taxonomia 318 temas. [derivado: db]
- **Cronograma:** `plano_tarefas` = SSOT; Fase 1 GERADA por `tools/trilha.py`. #38 Hernias FEITA (sb 131, 25q/21). 🔴 A linha "Posicao" do `--handoff-block` ainda diz "semana 1" (semana por POSICAO no plano, o defeito que a auditoria achou no painel e que o painel V4 ja corrigiu); a semana de calendario e a **S2** (21-27/09) -- `plano.py --panorama` manda.
- **Posicao:** plano semana 1 (fase 1) · 2/5 tarefas da semana feitas · cota ~103q/dia ate 27/09 · Fase 1 ~82.5q/dia [derivado: plano_tarefas -- ver a ressalva acima]
- **Engenharia:** suite **1074** coletados; hub V4 (painel pelo leitor do panorama, quadro `core/hub_quadro.json`, `hub.py --precisa-publicar`, timer ativo, tela de fim com agenda); `/hub-backend` + `plano.py --concluir --leitura`.
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** · 🩻 Raio-X UERJ (foto de 18/09): https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc

## Ultima sessao -- s194 (2026-09-23) -- ESTUDO + ENGENHARIA: hub gravado, Hernias, hub V4 e backend

Detalhe em `history/session_194.md`. (1) Lote de 220 gravado (170 notas, 0 quarentena) e defeitos triados -> F129; armadilhas da Autopsia (#1721-1728) refeitas. (2) Hernias #38 21/25 (solidas 18): 4 erros + 3 incertezas; cards #1729-1733. (3) Hub V3 -> V4: abas Painel/Aulas/Cards, timer ativo, painel auditado (semana/saldo/ritmo), quadro de aulas. (4) Botao "Pedir mais cards" barrado pelo classificador ("Create Unsafe Agents") -> `/hub-backend` em `/loop` (decisao dele). (5) Export no saldo do dia; `--concluir --leitura`.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- 🔴 **Backend so vale com PC acordado e sessao aberta;** latencia = intervalo do `/loop`. Tique barrado pelo classificador ou pedindo aprovacao = para e relata, nunca contorna. Nunca testado ainda em `/loop` real (so 1 tique a mao).
- 🔴 **O mapa UERJ erra rotulo (F128)**; recalibrar a trilha so pelo acerto ACUMULADO, a partir da 3a prova UERJ (regra do `/ai-eng`, s189).
- **F113 PARCIAL** (+ F129), **F110** sem gate, **F78**/**F2** DECLARADOS. Pasta travada `.claude/worktrees/agent-acda9b545d40f697d` (sobra da s194; o `reachability_check` ja a ignora) -- remover so com OK dele (`git worktree remove --force`). Patch do botao em `tmp/patch_s194_pedido_cards.diff` (fora do git).
- 🏠 **O owner passa por cima das regras do `db`** (conta compartilhada): a fronteira real e o writer. Poda de `sessoes/2026-09-22h` (220 docs) pendente: releitura = 0 novas, 0 quarentena -> pode podar no proximo fechamento de cards.

## Pendencias/observacoes ativas

- 🔴 **Instrucao para o OPERADOR fora das 8 primeiras linhas deste arquivo nao e instrucao, e arquivo.**
- 🔴 **Commit com subagente em paralelo:** `git add` so dos proprios paths; commit barrado -> `git restore --staged` so dos seus (s194: um filho levou o log da sessao junto no commit dele).
- 🔴 **Brief de subagente com conteudo clinico se escreve COM acentos**; regex sempre em string RAW; patch longo = arquivo no scratchpad.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_194.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md * Selo: `python tools/selo.py`*
