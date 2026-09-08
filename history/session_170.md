# Session 170 -- 50 cards + contrato v1.3 do /revisar + auditoria do banco com o /ai-eng

**Data:** 2026-09-08 · **Ferramenta:** Claude Code (Opus 5) · **Co-sessao:** `/ai-eng` (Fable 5.1), janela propria, N=75

---

## 1. Estudo

**Cards: 50 drenados** (fila do dia: 41 agendados + 8 erros frescos + 1 atrasado).
Distribuicao: **21x nota 4 · 8x3 · 6x2 · 15x1 -- retencao 58%**.

| Bucket | n | Retencao |
|---|---|---|
| Blocos 1-5 (agendado/atrasado) | 30 | 63% |
| Cirurgia Infantil (estreia de 07/09 voltando) | 8 | 25% |
| SUA (erros frescos + agendados) | 11 | 73% |
| Diarreia (erro fresco) | 1 | 0% |

**Questoes: 20** (Etica Medica, lista completa, **100%**). Zero erros a analisar. Acumulado **6.936**.

**Vitoria:** a inversao **Wilms x neuroblastoma quebrou** -- 2 cards independentes, os 2 certos, incluindo o que planta "cruza a linha media" como isca. Na s169 foram 2 cards, as 2 vezes errados na mesma direcao. A Revisao Direcionada de ontem pegou.

**SUA: 25% (s169) -> 73% (hoje).** Mesma leitura: o re-ensino completo do dia anterior, com resposta na mesa e uma noite de sono, e o que produziu recall.

## 2. Padroes de erro

- 🔴 **O no do fluxograma nao e lido -- 5o dia, e sobreviveu a 2 explicacoes no MESMO dia.** No card #1536 ("qual dado decide clinico x cirurgico no SUA agudo") respondeu "imagem"; expliquei; no redrill respondeu "relacao com a cavidade" (a resposta da miomectomia, arrastada do item anterior). E acertou o #1538 (a conduta: curetagem). **Tem o destino decorado e nao tem a regra de decisao** -- por isso o padrao sobrevive a acertar questoes. Agora sao **5 areas**.
- 🔴 **Repeticao exata do erro de ontem em 24h:** #1530, "reagiu ao leite" -> APLV. Substancia redutora nas fezes e teste de ACUCAR; aponta ma-absorcao de carboidrato e AFASTA a via alergica.
- 🔴 **Eixo clozapina x carbamazepina: 5o encontro** (#335 25/06, #847 17/08, card #560 em 07/09 e hoje). Nas 2 vezes que arriscou, marcou carbamazepina; nas 2 ultimas, "nao lembro". O resumo cobre o ponto com clareza (`Dependencia Quimica.md:58` e `:85`) -- nao e falta de material, e alca de recuperacao que nao engata.
- **Billings:** 2 tentativas, as 2 descrevendo o sintotermico. Decoreba invertida, nao ausente.
- **Perseveracao:** respondeu "adenomiose" em 2 cards seguidos (#1542 certo, #1543 errado).

## 3. Mudanca de contrato -- `/revisar` v1.3 (decisao do usuario)

O usuario **nao leu** o bloco de PREPARAR entregue antes de Cirurgia Infantil e respondeu os 8 cards a frio: *"muito ruim, denso e confuso. Noto bastante confusao entre os conceitos de 'refrescar', 'preparar', 'revisao direcionada' e 'aula-base'. Proponho integrar tudo na revisao direcionada ao final."*

- ⚰️ **Sub-modo PREPARAR REVOGADO** + **Camada 0** + **Camada 1** (micro-resumo na virada). Lapide com 3 motivos em `revisar.md`, para impedir re-derivacao.
- ⚰️ **Invariante D revogado** (sem aquecimento pre-drill nao ha o que isolar).
- **Invariante F (novo):** silencio no meio do DRENAR -- verso + nota + tally, zero prosa, **inclusive para 1-2**. Excecao unica: **defeito de CARD**.
- **Invariante B realocado:** quem carimba `review_log` agora e a Revisao Direcionada.
- A sessao passa a ter **2 fases**: DRENAR -> REVISAO DIRECIONADA (unica superficie de ensino, sobre notas 1-2).
- 🔴 **`/aula-base` NAO afetada** -- e pre-QUESTOES, nao pre-cards, e tem eficacia medida (Meningites 53% -> 75%). Explicitado nos 3 portadores.

Contrato `revisao-calibrada-contract.md` para **v1.3**, Clausula 11. Portadores: `revisar.md`, `refrescar.md`, `AGENTE.md` §6 e §7.3, os 2 espelhos via `sync_skills`.

🔴 **Erro meu, corrigido no mesmo dia:** afirmei que 100 cards estavam "dentro da politica de sprint ate 13/09". O sprint de 120/dia foi **revogado pelo usuario em 07/09** (lapide no `fsrs-management-contract`). Teto real: **60/dia**, 90 so em regime de divida. A memoria estava 1 sessao atras do contrato e eu nao reli o portador -- a memoria virou ponteiro.

## 4. Auditoria do banco (3 subagentes, read-only, a pedido do usuario)

**Reforja (Sonnet):** a fila de reforja **nao existe como estado** -- e 100% prosa acumulativa em `HANDOFF`/`history`/`AUDITORIA`. O unico CLI queryable (`cards_regen_queue.py:49`) filtra `quality_source='heuristic'`, populacao **aposentada na s075**: cego por desenho a 100% do que cai no drill, ha ~95 sessoes. 6 reincidentes confirmados por `card_version` (#321 em v2 com o texto do defeito IDENTICO; #792 v1 nunca editado); **23 cards da fila corrente em v1 = confirmadamente nunca reforjados**. Passivo ~37.

**Pool `state=0` (Opus):** hipotese do usuario **refutada na media, confirmada no eixo que importa**. 21,9% (144/657) com achado x **25,3% (176/696) no rodado** -- o pool nao e lixo. Mas a media mente: a inversao vem de UM predicado de verso; em **todo** eixo de frente o pool perde, e no like-for-like v1xv1 e **1,34x pior**; eixo A do F81 **2,0x**; contexto vazio **49% x 18%**. **Lote 600-799 = 20,1% do pool carrega 41,5% do defeito de frente** (backfill retroativo; contraprova: faixa 900-999, datas sobrepostas, e a mais limpa). Baldes: APOSENTAR 4 · REFORJAR-frente 102 · REFORJAR-so-verso 41 · OK 510.

**Graphify (Sonnet):** 36 commits de defasagem, `resumos/` 0 de 136 indexados, **zero leitor mecanico**, 880k tokens em 2 regeneracoes. Veredito **MORRE** -- **operador NAO aprovou o apagao**; fica de pe.

Relatorios crus em `.vibeflow/audits/s170-*` (entraram no repo porque a citacao original apontava para o scratch da sessao -- inalcancavel para qualquer outro, achado G2).

## 5. Engenharia entregue (9 commits)

| Commit | O que |
|---|---|
| `5b1f682` | contrato v1.3 -- PREPARAR revogado |
| `c7efc23` | `AGENTE.md §10.6-8` -- protocolo com o `/ai-eng` |
| `c4ce1db` | **hotfix**: reforja deixa rastro (evento `reforja` nos 2 writers, pos-commit) |
| `d2026a1` | **ratchet de nao-crescimento do verso**, BLOCK nos 2 writers |
| `06634b6` | ratchet indisponivel RECUSA a escrita (fail-loud, nao fail-open) |
| `64a8a9a` | `ESTADO.md` contradizia a si mesmo em 2 eixos (G4) |
| `d9ecbbe` | 3 relatorios de auditoria entram no repo (G2) |
| `3b034a5` | ledger de trocas agente<->agente + hook `PostToolUse` |

**395 testes** (eram 376). Suites novas: `test_reforja_event_log`, `test_ratchet_verso`.

## 6. Achados de engenharia

- **F81** (novo no ledger): `frente_contexto` desalinhado da `frente_pergunta`, 3 eixos -- A: 26 cards com containment >=0,70; B: 10 "Por que X nao pode Y"; C: contrafactual, **declarado como nao verificavel por gate**. `card_checks` compara frente x verso e **nunca** compara contexto x pergunta. **Achado do usuario no drill, nao do gate** -- 3o consecutivo (F79, F79b, F81).
- **Justificativa orfa** (classe nova, nomeada aqui): comentario cuja premissa outra frente removeu, ainda governando codigo. `db.py:765` justifica um fail-open com *"o app nao pode quebrar sem tools/"* -- esse app era a UI Streamlit, **removida**. Medido: **N=1 governando**, N=2 claim envelhecido, 1 lapide legitima. Discriminador: *"a premissa esta no caminho de decisao?"* -- sem ele a assinatura de grep nasce 3-em-4 falsa.
- **Claim de contagem/mecanismo envelhece (D67 estendido):** 4 casos no dia, dos 2 lados. Eu afirmei "o check nao bloqueia" sem seguir o consumidor; o `/ai-eng` afirmou "6 suites orfas" sem o grep (o F43 checa a uniao de 3 registros -- refutado por medicao) e "5 writers" (sao 7); e a constante `LEDGER` morta no script dele. Regra: **descrever um registro exige ler o registro atual, nao o lembrado.**
- **DEFERIDO:** `recurate_cards.validar()` recebe `permitir_atomicidade` e **nunca usa** -- a politica mora no `main()`, logo chamador programatico passava livre por toda a atomicidade.

## 7. Aberto para a proxima sessao

1. 📄 **Dossie do `/ai-eng`** em `C:\Users\daanm\ai-eng\brain\observed-systems\medhub-dossier-2026-09-08.md` (141 linhas) -> **ler inteiro**, copiar para `docs/MEMORIA-AUDITORIA.md`, ponteiro de 1 linha no HANDOFF + citacao no workflow de engenharia. Pedido dele: divergencia na §3 ou §7 contra o repo -> corrigir na copia e mandar a linha.
2. 🔢 **Os 4 achados de hoje sem F-id** (G2): hotfix do event_log, ratchet, fail-loud, justificativa orfa.
3. 🛠️ **Fila acordada e nao executada:** spec F81 (+pergunta generica como CONJUNCAO, 7 writers), spec da fila de reforja com lifecycle (`reforja_marks`, nunca coluna booleana), check de idade N=6, dry-run do lote 600-799.
4. ⏳ **Decisoes do operador:** apagao do graphify (nao aprovado), contexto obrigatorio em card novo (49% do pool nasce sem).
5. 🃏 **Reforja:** 6 cards de hoje (#243, #561, #582, #321, #365, #792) + o passivo de ~37.

## 8. Reencontro com o `/ai-eng` apos o reinicio

Ambas as sessoes reiniciam com contexto limpo. Protocolo combinado: **o endereco do canal muda, o nome reaparece no `ListAgents`**. Quem bootar primeiro manda 1 linha de presenca; o outro responde com "o que ja foi decidido" a partir do ledger. Do lado dele: `python tools/exchange_log.py --report 25 --full` (22 registros, texto integral dos 2 sentidos). Do lado daqui o ledger nasceu hoje e tem 2 registros -- **a memoria da troca de hoje esta do lado dele**, e o handoff de retomada dele fica em `brain/interactions/2026-09-08-handoff-canal-medhub-continuidade.md`.

---
*Anterior: `session_169.md` · Macro: `ESTADO.md` · Ledger: `AUDITORIA_MEDHUB.md` · Trocas: `history/exchange-log.jsonl`*
