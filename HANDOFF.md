# HANDOFF.md -- ESTADO OPERACIONAL CURTO
*Atualizado: 2026-09-10 -- S175 (Claude Code / Opus 5 1M, sessao de ESTUDO, dia cheio): **76 cards drenados + 90 questoes registradas (75 acertos, 83,3%) + 15 erros analisados**. Volume 7036 -> **7126** (estava congelado desde 08/09). Tres achados de mecanismo: **F90, F91 (ALTA), F92**. Feedback duro do usuario sobre **uso de subagents** -- regra reescrita.*

> 🔴 **Engenharia so em sessao DEDICADA, contexto limpo dos dois lados.** A sessao autorizada em 09/09 **aconteceu (s174)**; a proxima e o **bloco B** (specs F81 + fila de reforja), GO ja dado, **so quando o operador abrir outra janela**. Janela de estudo nao toca engenharia. Semana de **ENAMED (dom 13/09)**: questoes, simulados e cards. **Ler `history/session_173.md §5`** -- a semana esta decidida pelo usuario.

## > Proximo passo imediato

1. ❓ **DUAS PERGUNTAS ABERTAS ao usuario, curtas, na abertura:** (a) **fork da PAC Q3** -- *"quando voce marcou A, estava afirmando que o pneumococo NAO e o agente mais provavel naquele etilista diabetico, ou estava marcando a que achou verdadeira?"* Se rota (iii), resgatar o card cortado "fator de risco nao destrona o agente mais comum"; se rota (i), e o padrao de enunciado negativo e o remedio e ritual, nao conteudo. (b) **valores laboratoriais da Uro II Q2** (eram imagem, nao transcritos) -- se havia relacao PSA livre/total, o gabarito fecha sem depender do corte NAO-VERIFICAVEL.
2. 🔴 **NOVA REGUA DE SUBAGENT (feedback duro da s175, ja gravado):** **ate ~8 erros o agente principal analisa SOZINHO**; verificacao de cutoff = **WebSearch direto**, nunca `evidence-researcher`; subagente so acima de ~8 e **um so**; **nunca subagente que sumona subagente**. Custo que gerou a regra: 3 spawns, ~673k tokens e ~66 min para 15 erros -- e 2 afirmacoes de subagente **rejeitadas por re-medicao**.
3. 🃏 **Re-drill dos 12 cards nota 1-2 da s175** na abertura da proxima sessao de cards (so as frentes; **nao gravar FSRS** -- e consolidacao). Fila de 10/09 **zerada**; voltam 4 de relearning (#735 #1571 #1270 #1584) + o intake novo. Para o alvo de ~100/dia falta abrir o `--new-limit` (default 10) contra o pool de **671** -- **decisao do operador**, e agora e sobre **VAZAO**, nao meta: o card #1320, cunhado ha 24 dias para um erro que ele repetiu em 09/09, **nunca foi servido**.
4. 🎯 **Simulado 9 (qui) e 10 (sab):** `--area Simulado` direto no CLI; erros analisados no mesmo dia. Domingo: **ENAMED** = termometro.
5. 📚 **Backlog de conteudo:** 6 temas do Simulado 8 sem resumo (Doenca Hemorroidaria, Lesoes Hepaticas Focais, Abdome Agudo Obstrutivo, Farmacodermias, Esquistossomose, Liquido Amniotico) + s172 (Disturbios Resp. Neonatais, Infeccoes Congenitas, cerclagem).
6. 🧑‍⚖️ **Decisoes empilhadas do OPERADOR (o `/ai-eng` leva numa rodada so; ninguem decide por ele):** (a) **RODADA 3 do `normalize_taxonomia`** -- `docs/DRYRUN-F65-F67-2026-09-09.md` §4: 10 grupos duplicados (fundir?), 35 cards e 201 erros presos em `[bulk]` (tema real de cada um); (b) **17 cards em overflow no dia 14/09** (#321 #558 #788 #1187 #245 #706 #381 #823 #1479 #1159 #707 #553 #709 #419 #486 #632 #463) -- mover a mao para antes da prova ou deixar; (c) **backfill UTC->local** do historico de `review_time`/`data_registro`/`reviewed_at` (shift constante -3h; dry-run + COUNT por linhas que mudam de dia) -- sim/nao; (d) os de sempre: apagao do `/graphify`, contexto obrigatorio em card novo, F62/F55/F37, planilha ainda e fonte? (F35), **regua de "card bom" (F87)**.

## Fila de engenharia (proxima sessao DEDICADA; protocolo `AGENTE.md §10.6-8`, D71) -- ORDEM SELADA pelo `/ai-eng` em 09/09 (fechamento do ciclo A): o boot da proxima janela NAO re-deriva
0. **Inventario COMPLETO da divida = `docs/MEMORIA-AUDITORIA.md §11`** (4 tiers, pedido do operador: "resolver progressivamente"). Abrir a janela com o **Tier 3** (30 min: re-medir e marcar os 8 achados sem status F16-F20 F27 F28 F32), depois o Tier 0 abaixo.
1. **F80b como hotfix, PRIMEIRO** (mesma costura do F80 do lado do LEITOR): `get_cards_by_bucket`/`get_fresh_error_cards` comparam `fc.due` local com `datetime('now')` UTC -- fila mente 3h em 48h. Remedio: leitor unico de "agora" = `db.agora()`; varredura estrutural que falha nomeando o arquivo se um SELECT ainda usar `datetime('now')`. Teste = instante congelado as 22h local, card `due` 23h NAO pode aparecer como vencido.
2. **B1 -> B2 -> B4 (se <=1h) -> B3** (GO de 08-09/09): B1 spec **F81** (predicado contexto x pergunta; DoD por CADA um dos 7 writers; fixtures #1568/#1574 no 1o predicado; contador de gate-miss com classe lendo **`fsrs_revlog.reason_servido`** do F76) -> B2 spec **fila de reforja como estado** (`reforja_marks` lifecycle; #792 3x, #321) -> B4 F77/F77b -> B3 F35 (reporta, nao bloqueia, **com a IDADE da planilha**).
3. **F89 depois do B1:** o MECANISMO (`AREAS_VALIDAS` unica + fail-loud nos 3 writers de taxonomia + WARN no auto_check) e engenharia e nao depende do operador; a LISTA e conteudo dele (RODADA 3). Escrever a spec contra a lista atual; a RODADA 3 muda a lista, nao o mecanismo.
4. **Promote dos 3 stubs** (`.vibeflow/audits/2026-09-09-hotfix-consolidation.md`) = GO, loop local: contrato do calendario de provas (F71) · contrato da zona canonica LOCAL (F80) · `reason_servido` como campo do F81 (F76).
5. **Smell declarado, sem data:** `app/utils/db.py` importa `tools/card_checks.py` por `__file__`; mover = spec.
6. **F90 (s175; entra no FIM -- nao reordeno lista selada; = `§11` item 1.19):** `revisar.md` tem 2 clausulas **revogadas sem lapide** que o agente obedeceu em uso real (passo 4 "justificativa em 1 linha" x Invariante F; "lote de 3/5/6" x a regua 10-15 da s130/s152) + o preview P3 orfao do override passivo. 🔴 **E gate-miss, nao so drift:** o `CONTRATO_REVOGADO` (`auto_check.py:100-119`) mira `revisar.md` **nominalmente** e imprimiu `PASSED` com o defeito em curso -- seu `_TERMOS_REVOGADOS` tem **3 entradas** e o comentario do codigo promete *"ninguem enumera a mao"*, mas enumera. Remedio em 2 metades: (i) lapidar as clausulas; **(ii) cadastrar os termos + dar ritual de alimentacao ao registro** -- sem (ii) o gate segue cego para a proxima revogacao. Barato (2 arquivos).

## Estado por frente

- **Norte:** 🎯 **UERJ/MFC 01/11/2026** (52d). ENAMED 13/09 (**3d**) termometro.
- **Volume & Metas:** **7126** / 10400 (perf. ~79.0%). Ritmo-alvo ~63.0q/dia (52d p/ UERJ/MFC (prova 01/11)).
- **FSRS:** divida 0 atrasados + 4 p/ hoje -- pool **671** nunca introduzidos (entram <=60/dia). **76 drenados na s175.**
- **Conteudo:** 136 resumos em resumos/. [derivado: glob]
- **Erros & Cards:** **1002** erros registrados · **1419** cards ativos · 2 needs_qualitative na fila · taxonomia **288** temas. [derivado: db]
- **Posicao:** conteudo S17 (nominal S24, atraso 7 sem) [derivado: preparacao_estado]. Sprint "S20 ate 12/09" da s168 esta **morto**.
- **Datas:** ENAMED 13/09 · fim da grade 25/10 · **UERJ 01/11**. Inscricao UERJ fecha **01/10** (acao do usuario).

## Ultima sessao -- s175 (2026-09-10, dia cheio) -- ESTUDO (76 cards + 90 questoes + 15 erros)

**Tarde -- 4 listas de 09/09 registradas de uma vez** (Diarreia 41/34 · Uro I 20/17 · PAC I 16/13 · Uro II 13/11 = **90/75, 83,3%**). Volume destravado: 7036 -> **7126**. **15 erros analisados -> 4 elos que reincidem, 24 cards, 7 cortes por regenerabilidade.**
🔴 **Achado clinico do dia, confirmado no banco:** o erro #997 (Uro I) e o de Uro II Q2 tem **a MESMA prescricao marcada** (alfa-bloqueador + 5-ARI), em duas perguntas diferentes, no mesmo dia. Formulacao correta: **"a prescricao da HPB e o output default quando aparece uma prostata"** -- nao "trata antes de investigar", que so cobre um dos casos. Em Uro II Q2 os dois cortes (I-PSS 8 e 20) **ja estavam escritos no resumo dele**: e "sabia mas nao aplicou".
**Fato no contexto errado (1c) foi a assinatura do dia -- 5 ocorrencias, em 3 escalas:** molecula (norfloxacina), framework decisorio (criterios de HPB no CaP) e motivo da consulta. Mais a reincidencia exata em 2 dias do erro #963 (Diarreia Q3), onde ele corrigiu a 1a metade e repetiu a 2a identica.
**Resumos editados:** `Pediatria/Diarreia.md` (nova §7.5 acido-base/potassio, buraco que causou 3 dos 7 erros), `Cirurgia/Urologia.md` (F92 + §1.4/§1.5/§2.6), `Clinica Medica/Infectologia/Pneumonias Bacterianas.md` (nova §5.10 eosinofilias, §5 "associacao NAO e frequencia", §6, §8.2, nova §8.6 vacina).

---

### Manha -- drenagem da fila FSRS (76 cards, fila zerada)
**52x nota 4 - 9x3 - 3x2 - 12x1.** 🔴 **A separacao que salvou o diagnostico:** 6 das 12 notas 1 eram **cards NOVOS** (1a exposicao) -- nos **66 ja vistos, so 6** notas 1-2 (~91% funcional). *Nota 1 em card `state=0` e linha de base, nao sinal.* 🔴 **Correcao do usuario (virou F90):** prosa em card nota 3-4, lote de 6 e `<sub>` HTML no terminal -- *"Voce deu o boot direito, mestre?"*. O boot estava certo; o `revisar.md` carrega 2 clausulas revogadas sem lapide. **Revisao Direcionada** em 6 eixos + 2 curtos; `Cirurgia Infantil.md` cobria os 6 pontos -> nenhuma edicao. `review_log` 143-150; notas F18c gravadas. **F71 em acao:** #238 declarou OVERFLOW em vez de silenciar. Detalhe em `history/session_175.md`.

## Padroes de erro ativos (re-medidos na s175, leitura de drill de 76 cards)
- 🔴 **Fato no contexto errado** -- **2x no mesmo drill** (pancreatite: a resposta de "TC precoce subestima" reaplicada na pergunta de "por que USG primeiro"). Ritual: *"a pergunta e sobre etiologia, gravidade ou complicacao?"* · 🔴 **Armadilha literal do card e o que ele marca** (dreno na apendicectomia) · 🔴 **Enunciado lido pela metade** ("quantas doses AINDA exige" respondido com o total do esquema -- em Imunizacoes, 2a maior area de erro) · 🔴 **Ancoragem no achado saliente** (padrao-mestre). ✅ **clozapina x carbamazepina fechado no 5o encontro.**

## Pendencias/observacoes ativas
- 📄 Manual de Gestacao de Alto Risco (MS 2022) > 10 MB: baixar uma vez resolve beta-hCG e cortes da PE.
- 🃏 Reforja: **#792 (3a marcacao)**, **#582/#583 compostas (confirmadas em uso na s175** -- ele respondeu so a 1a metade das duas), **#1568 NOVO** (frente pede achado "ausente" e o que ele "afastaria" -- falta o *se estivesse presente*; fixture do F81), #243, #561, #321 (rated 4, defeito intacto) + passivo ~37 -- vira fila mecanica no B2.
- 🔬 Ledger: **abertos (13 F + 7 so-ESTADO + 2 D):** F35 F36 F42 F72 F77 F77b F78 F79b F81 F87 F89 **F90 F91(ALTA)** · F63-F69 · D5 D11. **Fechados:** F71 F76 F80 F85 F88 (s174) · **F92** (s175).
- 📡 **Handoff de engenharia entregue ao `/ai-eng` N=78** em `docs/HANDOFF-ENG-2026-09-10.md` (blob `db82fc3`). **3 bifurcacoes esperando ordem dele:** (6.1) a regua de subagent vira portador versionado? (6.2) F91 em que Tier? (6.3) F90 remedio em 2 metades juntas? Tier 3/0/1 seguem em **ZERO** -- gate de janela de estudo, desvio conforme.
- 💉 Diretrizes a conferir: Calendario Vacinal 2026, GINA 2026, ATLS 11 (parcial), SINAN 2026.
- ⚠️ Drive 45d sem sync (F72); Dashboard EMED 6.288 x db 7.036 -- db e a fonte fiel (F35: planilha ainda e fonte? -> operador).
- 📚 **Frente MFC (Gusso + Duncan)** abre 14/09; rescope da grade pro formato UERJ.

---
*Historico: history/INDEX.md * Macro: ESTADO.md * Sessao: history/session_175.md * Trocas: history/exchange-log.jsonl * Auditoria: docs/MEMORIA-AUDITORIA.md*
