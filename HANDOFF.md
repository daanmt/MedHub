# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-10 -- **S176 (ENGENHARIA, janela de reforma remota)**: 6 itens do Tier 0 fechados em 8 commits, suite **452 -> 503**, **0 spawns de subagente**. HEAD `1948457`, main == origin/main.*

> 🔴 **A janela de reforma FECHOU no 0.4.** O `/ai-eng` mandou parar antes do 0.5 (spec em fim de janela = trabalho perdido no meio). **Semana de ENAMED (dom 13/09): questoes, simulados e cards.** A engenharia so recomeca quando o operador abrir outra janela -- e a fila abaixo **NAO se re-deriva**, ja esta ordenada.

## > Proximo passo imediato

1. 🃏 **VOLTAR AO ESTUDO.** Re-drill dos **12 cards nota 1-2 da s175** (so as frentes; **nao gravar FSRS** -- e consolidacao) + fila FSRS do dia (voltam 4 de relearning: #735 #1571 #1270 #1584) + intake novo.
2. ❓ **DUAS PERGUNTAS ABERTAS da s175**, curtas, na abertura: (a) **fork da PAC Q3** -- *"quando voce marcou A, estava afirmando que o pneumococo NAO e o agente mais provavel naquele etilista diabetico, ou marcando a que achou verdadeira?"*; (b) **valores laboratoriais da Uro II Q2** (eram imagem) -- se havia relacao PSA livre/total, o gabarito fecha sem depender do corte NAO-VERIFICAVEL.
3. 🎯 **Simulado 9 (qui) e 10 (sab):** `--area Simulado` direto no CLI; erros analisados no mesmo dia. Domingo: **ENAMED** = termometro.
4. ✅ **Regua de subagent agora e VERSIONADA (F93):** `.claude/commands/analisar-questao.md §0 Orquestracao`, 10 clausulas. Ate ~8 erros o principal analisa SOZINHO; cutoff = **WebSearch direto**; um subagente so por lote; **nunca cadeia**; `model` explicito; custo (tokens+min) no selo.
5. 📚 **Backlog de conteudo:** 6 temas do Simulado 8 sem resumo (Doenca Hemorroidaria, Lesoes Hepaticas Focais, Abdome Agudo Obstrutivo, Farmacodermias, Esquistossomose, Liquido Amniotico) + s172 (Disturbios Resp. Neonatais, Infeccoes Congenitas, cerclagem). **Medida nova:** `cobertura_conhecimento.py` conta **395 PDFs / 135 .md / 327 orfaos** -- e so `/extrair-pdf` alcanca esse CLI (F16).

## Fila de engenharia -- ORDEM SELADA, o boot NAO re-deriva. Inventario: `docs/MEMORIA-AUDITORIA.md §11`

- ⚰️ **FEITO na s176:** 0.0 (F93+F90) · Tier 3 (8 triados: 5 fechados, 3 parciais) · 0.1 (F80b) · 0.1b (F91) · 0.2 (B1/F81) · 0.3 (B2) · 0.4 (B4/F77+F77b).
- 🔜 **Tier 0 restante, nesta ordem:** **0.5 B3 (F35** -- reconcile planilha x db **reporta, nao bloqueia, com a IDADE da planilha)** -> **0.6 F89** (`AREAS_VALIDAS` unica + fail-loud nos 3 writers de taxonomia + WARN no auto_check) -> **0.7 promotes x3** (contrato do calendario de provas F71 · contrato da zona canonica LOCAL F80 · `reason_servido` como campo do F81/F76).
- 🔜 **Tier 1:** 1.1 F79b -> 1.2 F64 -> 1.3 F66 -> 1.4 F42 -> 1.5 F7 -> 1.6 F39 -> 1.7 D5 -> 1.8 varredura unica **+ o (ii') do F90** (termos revogados DERIVADOS do ledger, matando a enumeracao manual) -> 1.9 sem data. **1.10 e CANDIDATO, aguardando GO do OPERADOR:** toda clausula normativa de skill/`AGENTE.md` tem um CHECK nomeado **ou** a marca literal "nao-verificavel" -- 100% medido por script.
- 🧑‍⚖️ **Decisoes empilhadas do OPERADOR:** (a) **`python tools/reforja.py --backfill --apply`** -- 9 linhas ja declaradas em dry-run, esperando ele; (b) **RODADA 3 do `normalize_taxonomia`** (`docs/DRYRUN-F65-F67-2026-09-09.md §4`); (c) **17 cards em overflow no 14/09**; (d) **backfill UTC->local** do historico; (e) **`--new-limit` x pool de 647** (e sobre VAZAO, nao meta); (f) os de sempre: apagao do `/graphify`, planilha ainda e fonte? (F35), regua de "card bom" (F87), F62/F55/F37.

## Estado por frente

- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (52d). ENAMED 13/09 (**3d**) termometro.
- **Volume & Metas:** **7126** / 10400 (perf. ~79.0%). Ritmo-alvo ~63.0q/dia.
- **FSRS:** divida 0 atrasados + 4 p/ hoje -- pool **671** nunca introduzidos (entram <=60/dia).
- **Conteudo:** 136 resumos. **Cobertura medida: 327 temas com PDF e sem `.md`.**
- **Erros & Cards:** **1002** erros · **1419** cards ativos · taxonomia **288** temas.
- **Engenharia:** suite **503** · `auto_check --changed` PASSED · ledger **95 ids** · 2 hotfix docs `verified` + 3 audits `PASS` ainda **nao consolidados** (`audit --consolidate-hotfixes`).
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem). Sprint "S20 ate 12/09" da s168 esta **morto**.
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario).

## Ultima sessao -- s176 (2026-09-10, noite) -- ENGENHARIA

**Permit do operador, verbatim: "Fila inteira, sem parar"** -- dado **CONTRA** a recomendacao do `/ai-eng` e a minha (as duas propunham so os 2 hotfixes antes do ENAMED). Decisao dele; a ressalva fica no registro. Detalhe integral em `history/session_176.md`.
**O fio do dia:** os 6 itens sao a mesma doenca em superficies diferentes -- **o mecanismo existe, esta certo, e nao alcanca**. Duas formas novas da serie *Reachability-Debt*, medidas: **sem perimetro** (o F80 cobria writers e nao leitores; os 2 caminhos de reforja nao chamavam `validar_card`) e **sem consulta/ponteiro/escopo** (Tier 3).
🔴 **Caso-sintese, o F90:** o gate `CONTRATO_REVOGADO` mira `revisar.md` **nominalmente** e imprimiu `PASSED` com 3 prescricoes revogadas em vigor, porque seu registro tinha 3 termos enumerados a mao sob um comentario que prometia *"ninguem enumera a mao"*. Virou regra: **`AGENTE.md §10 item 10` -- revogar tem TRES passos (declarar -> lapidar -> cadastrar), os tres no mesmo commit.**
**Dois achados que so apareceram porque o teste veio ANTES do codigo:** o **segundo silenciador** no `get_topic_context` (consertar so o `rag.py` daria um fix que parece certo e nao muda o caminho real) e os **writers de reforja sem `validar_card`**.
**Uma bifurcacao real:** os fixtures que a ordem mandava usar no 0.2 pontuavam **0.056/0.091** -- o chao da distribuicao. Parei em vez de afrouxar a metrica; o `/ai-eng` decidiu 3 predicados nomeados.

## Fronteiras DECLARADAS (nao ler verde de gate como limpeza)

- **Eixo C do F81** (vinheta que trabalha CONTRA a pergunta, semantico) nao alcancavel por regex -- **#792 e sentinela**: se um predicado passar a pega-lo, a leitura e *"atualize a declaracao"*, **nunca "regressao"**.
- **Faixa 0.55-0.79** do contexto-redundante: **14 cards** com redundancia real fora do corte 0.8, ate o passivo de 12 zerar.
- **"Passivo ~37" de reforja NAO migrado** -- existe o numero, nao existe a lista.
- **Contador de gate-miss** so passa a informar com **>= 300** revisoes na janela (hoje **76**, contra **2642** fora dela).
- **Sitios gemeos do F80b em `tools/`** (`audit_fsrs.py`, `variancia.py`) deferidos por teto de hotfix; a varredura declara o proprio escopo (`app/`) na docstring.

## Pendencias/observacoes ativas

- 🃏 **Reforja virou estado consultavel:** `python tools/reforja.py --fila` e a **unica cifra citavel** do passivo. Numero escrito a mao vira claim que envelhece. Fechar marca **re-roda o predicado** e recusa se ele ainda acusar.
- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB: baixar uma vez resolve beta-hCG e cortes da PE.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial), SINAN 2026.
- ⚠️ Drive 45d sem sync (F72); Dashboard EMED 6.288 x db 7.126 -- db e a fonte fiel (F35 -> operador).
- 📚 **Frente MFC (Gusso + Duncan)** abre 14/09; rescope da grade pro formato UERJ.
- 📡 Canal com o `/ai-eng` N=78 em `history/exchange-log.jsonl` (`python tools/exchange_log.py --report 4 --full`). Portador dele: `C:/Users/daanm/ai-eng/brain/interactions/2026-09-10-handoff-medhub-reforma-subagents.md`.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_176.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
