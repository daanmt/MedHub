# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-26 (~16h40 local, s201 SELADA) -- **s201 (Opus 5.5, observada pelo /ai-eng)**: a ordem do veredito da s200 FECHADA (F133-F136 + #2-#9) e o pedido do operador: **aba Listas dividida em Questoes | Simulados** -- as provas UERJ 2021-2026 entram por PDF (`tools/prova_pdf.py`, tudo ou nada) e 5 simulados pendentes (417q) estao no hub. **F137**: a suite fazia backup REAL e a rotacao apagou os pontos de retorno do dia (corrigido; dano irreversivel declarado).*
> 🏠 **MedHub HUB (1 artifact, fixado): https://claude.ai/artifact/3RksMfkzNWYSQD7D6JXNEr** -- abas Painel / Aulas / Cards / **Listas** (Questoes | Simulados) (Version 33). Republicar SEMPRE nesta URL (rito: `/hub-backend`, `/revisar` "DRENAR no player", `registrar-sessao` §6); `artifact-deleted` = recriar completo (capabilities de 3 regras, abaixo) e REPORTAR aqui. **Lote vivo `2026-09-26b`** = colecao `sessoes/2026-09-26b/notas` (51 cards, 11 gravados; 11/51 no db em 26/09 16h, vespera exportada 25/09 ~21h depois da revisao de portugues; o `2026-09-26a` (56) ele ja drenou na noite de 25/09). (o `sessao` nao e a data de hoje; trocou o lote, troca aqui). Colecoes `2026-09-22h` (220) e `2026-09-24a` (90) PODADAS no fechamento (releitura = 0 novas nas duas). Aulas Pediatria e DMG ja em TOPICOS; ele vai trazer o feedback.

> 📝 **SIMULADO DA VEZ = UERJ 2021 (60q, ~3 h) NO HUB:** aba Listas -> Simulados (o painel tem o atalho "resolver no hub"). Depois: 2022 (S3), 2024 (S4), 2025 (S5, 97q -- 3 anuladas fora), 2026 (S6). ⚰️ *Bancada EMED https://claude.ai/artifact/Q2Cojm89D9JwRyBYmCD5Db = historico da captura pelo Chrome, revogada em 26/09 (F135)*; entrada agora = PDF. 🔒 Conteudo so no `ipub.db` e nas colecoes `read admin` do hub; nunca no git.

> 🔒 **O SELO:** `python tools/selo.py` -- tabela DERIVADA, nunca digitada. Ledger ate **F137** (F133-F137 RESOLVIDOS na s201; F129 PARCIAL; F127/F128 DECLARADOS); 2 GATE do operador seguem (F87, F111).

> 🔴 **ABRIR A s202 POR AQUI (o /ai-eng monitora; decisoes dele no `history/exchange-log.jsonl`, 26/09 ~16h35, dir=in):** (0) **golden EMED** sob as decisoes (a) e (b) do /ai-eng -- re-export da lista Saude do Idoso com "Ver solucao" aberta; perfil EMED PROPRIO no `tools/prova_pdf.py` que CORTA comentario/estatistica no parser (propriedade = o predicado da purga (e)); golden = contagem + predicados + sha256 do PDF, NENHUM texto EMED no git, skip sem o PDF; gabarito por `emed_id` do banco so como conferencia da t3; discursiva sai DECLARADA por numero e a contagem fecha em 3: achadas (31) = ingeridas (30) + declaradas (1) = `--expect` confirmado por ele. Amostra sem gabarito na raiz: `idoso pt1.pdf`/`idoso pt2.pdf` (gitignored). **Operador (26/09 ~16h40): contagem 31 CONFIRMADA; e objecao a (a): re-exportar com "Ver solucao" aberta traz o comentario do professor para o PDF -- "voltamos ao problema inicial, de precisar scrapar o emed, sem violar direitos autorais".** A FONTE DO GABARITO sem o comentario do professor e bifurcacao ABERTA (dele + /ai-eng) antes de qualquer parser. (1) **F137 parte 2**: writer destrutivo recusa sem o fixado do proprio inicio, `--desfixar ID --motivo` com rastro, sha256 no F-item. (2) (ii) advisories lote5/lote6. (3) UX: "ficou entre A e C e D" com 3 letras. (4) **Simulado UERJ 2021 feito no hub com a sessao fechada = `--registrar` idempotente na abertura** (rito do simulado em `/banco-emed` passo 3: UMA linha `--area Simulado` com os blocos na observacao).

## > Proximo passo imediato

1. 🗄️ **Banco de questoes (s201):** 12 listas EMED + **5 simulados UERJ** (t1793 2021, t1794 2022, t892 2024, t891 2025, t890 2026) no hub; **resolvidas: t96, t26**; em v2 (cadeia): t26 t40 t49 t96. Mapa de fragilidade: `emed_banco.py --status --por-objetivo`. Divergentes a conferir: t49 Q10/Q20 · t68 Q1/Q13 · t100 Q8/Q18/Q29/Q34 · t61 Q11 · t651 Q20. Sem resumo local de Hernias. Erro 1092 com `o_que_faltou` pre-racional (a analise do hub manda, #4).
2. 📊 **Aba Analise do hub:** PRD `.vibeflow/prds/hub-aba-analise.md` -- a cadeia v2 + `analises/*` + `--por-objetivo` ja sao o insumo (mapa de fragilidade por objetivo, acumulado entre listas). gen-spec -> implementar.
3. 📚 **Estudo:** semana 2 fecha 27/09: **UERJ 2021 no hub** (a da vez), #49 Hernias, #40 DMG, #100 Pediatria. Aula #877 pronta no hub. Nota de UX a mostrar a ele: a leitura diz "ficou entre A e C e D" com 3 letras.
4. 🃏 **Cards:** fila `2026-09-26b` (51, 11 gravados na s200) no ar; cards novos #1749-1756 entram pela fila. Marcas humanas abertas = 0. Duvidas clinicas da reforja em `tmp/reforja_s196/duvidas_*.json` e na s196 (#1113, #1176, #373, #65, #55) -> `/pesquisar-evidencia` quando houver folga. Resumo `[GIN] CA de Mama.md` ainda diz supraclavicular ipsilateral = estadio IV (errado; AJCC 8 = N3c).
5. 📊 **Ritmo e o alarme real:** 17,9 q/dia (7d) x 79,7 necessarios ate 01/11. Cobertura > refinamento.

## Estado por frente

- **Norte:** 🎯 Psiquiatria/IPUB via ENAMED 2027 (corte 940, alvo 95%). Plano B: UERJ/MFC 01/11/2026 (**inscrito**). Hibrido: Fase 1 = RF rescopada ate 01/11; Fase 2 = extensivo S21-S48.
- **Volume & Metas:** 7488 / 10400 (perf. ~78.8%). Hoje: 37. Ritmo do marco de volume ~80.9q/dia (36d p/ UERJ/MFC (prova 01/11)).
- **Simulados:** 10 provas + ENAMED real 75. **UERJ 2023 = 58** (solidas 44/60). Sequencia: ~~2023~~ -> 2021 -> 2022 -> 2024 -> 2025 -> 2026.
- **FSRS:** divida 2 atrasados + 30 p/ hoje -- pool 717 nunca introduzidos (entram <=100/dia).
- **Conteudo:** 135 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** 1094 erros registrados · 1589 cards ativos · 0 needs_qualitative na fila · taxonomia 320 temas. [derivado: db]
- **Cronograma:** `plano_tarefas` = SSOT; Fase 1 GERADA por `tools/trilha.py`. #38 Hernias FEITA (sb 131, 25q/21). 🔴 A linha "Posicao" do `--handoff-block` ainda diz "semana 1" (semana por POSICAO no plano, o defeito que a auditoria achou no painel e que o painel V4 ja corrigiu); a semana de calendario e a **S2** (21-27/09) -- `plano.py --panorama` manda.
- **Posicao:** plano semana 1 (fase 1) · 4/5 tarefas da semana feitas · cota ~237q/dia ate 27/09 · Fase 1 ~88.3q/dia [derivado: plano_tarefas] -- a semana de calendario e a S2 (`plano.py --panorama` manda)
- **Engenharia:** suite **1174** (s201, medida pelo pre-commit -- F136); caminho PDF `tools/prova_pdf.py`; Solucao v2 em cadeia + `core/objetivos.json` + estados no brief; `test_hub_render.py` (goldens); `backup_db` com argparse e rotacao pelo nome (F137); teto 100/150; hub V4 + aba Listas Questoes | Simulados; `/hub-backend` + `plano.py --concluir --leitura`.
- **Datas & links:** fim da grade 09/10 · **UERJ 01/11** · 🩻 Raio-X UERJ (foto de 18/09): https://claude.ai/artifact/1tCT3CqnSR3Wb2kSRqcESc

## Ultima sessao -- s201 (2026-09-26, sabado) -- ordem do /ai-eng fechada, caminho PDF, Listas = Questoes | Simulados, F137

Detalhe em `history/session_201.md`. Commits `e0e1ea1` (ledger), `3217bff` (F133/F134), `93308ff` (F136 aberto + gates), `cc30c57` (#5), `42b7bfe` (#6), `6b33f94` (#7/#8/#4/#9), `0661b2b` (F136), `d2e2bcf` (PDF + Simulados + F135), `1f42d9d` (F137), `ecdbe32` (atalho resolver no hub). Hub Version 33. Nenhum subagente. Dano do F137: sumiram os backups `143813` (antes do apagamento (e)) e `140307` (antes da reforja da s200).

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- 🔴 **Backend so vale com PC acordado e sessao aberta;** latencia = intervalo do `/loop`. Tique barrado pelo classificador ou pedindo aprovacao = para e relata, nunca contorna. Nunca testado ainda em `/loop` real (so 1 tique a mao).
- 🔴 **O mapa UERJ erra rotulo (F128)**; recalibrar a trilha so pelo acerto ACUMULADO, a partir da 3a prova UERJ (regra do `/ai-eng`, s189).
- **F113 PARCIAL** (+ F129), **F110** sem gate, **F78**/**F2** DECLARADOS. ⚰️ Worktrees orfaos (`agent-acda...` da s194 e `wt187`) REMOVIDOS na s201 com OK dele (remove + prune + branch), junto do residual do conteudo do professor em `tmp/`. Patch do botao em `tmp/patch_s194_pedido_cards.diff` (fora do git).
- 🏠 **O owner passa por cima das regras do `db`** (conta compartilhada): a fronteira real e o writer. Poda de `sessoes/2026-09-22h` (220 docs) pendente: releitura = 0 novas, 0 quarentena -> pode podar no proximo fechamento de cards.

## Pendencias/observacoes ativas

- 🔴 **Instrucao para o OPERADOR fora das 8 primeiras linhas deste arquivo nao e instrucao, e arquivo.**
- 🔴 **Commit com subagente em paralelo:** `git add` so dos proprios paths; commit barrado -> `git restore --staged` so dos seus (s194: um filho levou o log da sessao junto no commit dele).
- 🔴 **Brief de subagente com conteudo clinico se escreve COM acentos**; regex sempre em string RAW; patch longo = arquivo no scratchpad.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_201.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md * Selo: `python tools/selo.py`*
