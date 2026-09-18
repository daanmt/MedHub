# Session 186 -- Janela de engenharia 5: a onda 3 e a fila zerada

**Data:** 2026-09-18 (manha -> tarde)
**Ferramenta:** Claude Code / Opus 5 (1M context)
**Tipo:** ENGENHARIA
**Custo:** ZERO subagentes. O principal fez tudo -- a regua do F93 nao foi acionada porque nenhum
lote passou do limiar. 8 commits, harness verde em cada um, suite **811 -> 858**.
**Estudo:** 3 cards revisados (as 3 primeiras linhas sob a regua v2), zero questoes.

---

## Placar

| frente | desfecho |
|---|---|
| **R2 / F112** | ✅ **RESOLVIDO** -- regua nativa, versionada por linha; gate do operador cumprido |
| **part-7** | ✅ painel gerado do banco, publicado, regenerado 2x na mesma URL |
| **part-8** | ✅ Drive congelado sob snapshot reversivel; W1 suspenso, nao desligado |
| **1.9(a)** | ✅ `app/` deixou de alcancar `tools/` por cirurgia de `sys.path` |
| **F114** | 🆕 MITIGADO com fronteira declarada |
| **F115** | 🆕 ABERTO (spec; GO do `/ai-eng` dado depois do 1.9a) |
| **1.10** | ⏸️ sem GO do operador -- nao entrou |

Fila do `/ai-eng` (janela 5): **zerada**. Divida restante com ele: o decision brief do R8/F111
(prazo 02/11) e o 1.10.

---

## O que esta sessao aprendeu (vale mais que os fixes)

### 1. O gate do operador foi cumprido por ATO, nao por tela

A condicao que ele pos para o R2 era *"nao pousa sem eu ver a tela do player"*. Publiquei uma
previa de 6 cards -- e ele **drenou**, devolvendo 3 notas e 3 marcas de defeito. As tres notas
foram **4**, e sob a regua v2 o 4 e o degrau raro ("sem esforco"), entao perguntei diretamente sob
qual regua ele tinha dado. Resposta: *"a regua foi minha memoria mesmo. achei cards faceis."*

Isso fechou o gate melhor do que a tela fecharia. Ver a tela prova que o rotulo mudou; **dar nota
sob a regua nova prova que a MAO mudou**. A pergunta valeu o turno que custou -- sem ela, tres 4
seguidos seriam indistinguiveis de habito da regua velha, e eu teria selado um F112 falso.

🔴 **Regra derivada:** quando o sinal e ambiguo entre "funcionou" e "habito", **perguntar o
racional** e mais barato que medir mais. Irma direta da regra da s179 (*racional declarado vence
racional inferido*), agora aplicada ao operador testando uma mudanca minha, nao a um erro dele.

### 2. A prova do R2 saiu do dado real, e ela so existiu porque o versionamento existia

As 3 notas viraram as **3 primeiras linhas v2** do `fsrs_revlog` (3.067 -> 3.070, gravadas por
`--record-lote --apply --expect 3` com COUNT-ASSERT). O revlog ficou **misto**, que e exatamente o
caso que o R2 existe para tratar, e a traducao respeitou a linha:

```
visao nativa sobre o revlog real misto (3.067 v1 + 3 v2):
  nota 4 -> 3 linhas      (so as v2 -- "sem esforco" de verdade)
  nota 3 -> 1613 linhas   (as notas 4 da v1, que significavam "cravou")
```

Sem o versionamento, as **1.613 notas 4 antigas teriam sido relidas HOJE como "sem esforco"**. O
defeito que o F112 nomeia teria voltado pela porta dos fundos -- desta vez **inserido por nos**, na
mesma sessao que o consertou, e sem deixar rastro.

### 3. F114 -- parametro sem dado que o identifique e default com carimbo de medido

Fui medir quanto a adocao dos parametros do R1 mudaria o agendamento real e o numero da nota 4 nao
fechava (o "sem esforco" agendando igual ao "lembrou"). O diff indice a indice explicou:

```
python -X utf8 -c "<diff: Scheduler().parameters x core/fsrs_params.json::visoes.remap.parametros>"
  w3   8.295600 == 8.295600   <-- INTOCADO
  w16  1.872900 == 1.872900   <-- INTOCADO
  (os outros 19 se moveram; na visao `cru`, onde ha 1.613 notas 4, os dois TAMBEM se movem)
```

`w3` e `w16` governam o Easy. O mapa do R1 manda `4 -> 3`, entao a visao `remap` tem **zero
exemplo de Easy** e o otimizador nunca teve gradiente nesses eixos. Eles nao convergiram: **nunca
foram tocados** -- e o JSON versionado apresentava os 21 numeros em pe de igualdade.

**O achado inverteu a recomendacao.** Eu teria recomendado adotar (o ganho de -0,0129 no hold-out
era real). Medido no baralho (830 cards em Review): nota 2 cairia de **24d -> 8d** -- o ganho do
F112 virando comportamento -- mas nota 4 cairia de **70d -> 50d**, colapsando em cima do 3.
Recomendei **nao adotar**, o `/ai-eng` deu GO, e o gatilho do re-fit ficou escrito: quando a visao
v2 tiver nota 4 em volume que mova `w3`/`w16` para fora do default. O sensor ja existe -- e o mesmo
diff que achou o F114.

### 4. Um teste estava VERDE sem testar nada, e so apareceu porque a refatoracao o tocou

No 1.9(a), `test_ratchet_indisponivel_nao_bloqueia_edicao_que_nao_toca_o_verso` simulava
indisponibilidade do gate com `sys.modules["audit_card_atomicity"] = None`. Depois da inversao de
dependencia esse nome **deixou de ser consultado por `db`** -- o teste continuava passando sobre um
envenenamento **inerte**.

Os dois irmaos dele nasceram VERMELHOS, que e o comportamento certo: acusaram a mudanca de
contrato. O terceiro nao acusou nada porque nao media nada. **Verde decorativo e pior que vermelho**
-- a primeira linha do proprio `pytest.ini` deste repo ja avisa disso, e mesmo assim passou.

Os tres foram reescritos para provar a garantia NOVA (dois em subprocesso, afirmando que
`import app.utils.db` FALHA com o gate quebrado) e o terceiro ficou **invertido**: prova que a
simulacao antiga e inerte, e cai se alguem reintroduzir o import por nome.

### 5. O `CONTRATO_REVOGADO` achou 9 linhas que eu nao tinha lapidado

No part-8, depois de declarar a revogacao e lapidar as duas skills, o gate acusou `ESTADO.md`,
`HANDOFF.md`, 3 linhas do `cronograma-contract`, 2 do `reconcile-contract` e 2 da docstring do
`day_plan` ainda prescrevendo `--sync-drive` / `Realizada?` / `cronograma_conclusao_drive`.

Tratei por **natureza, nao em bloco**: prescricao viva foi reescrita (o `ESTADO` mandava ler a
conclusao do Dashboard; o `day_plan` afirmava que o sync "segue vivo"); registro historico de
changelog ganhou `⚰️` e **ficou**, porque apagar destruiria a evidencia (§10.2).

🔧 **Forma do gate, medida e agora escrita:** ele casa por **LINHA**, e em `.py` **nao ha isencao
por secao** -- um paragrafo que abre com `⚰️` nao protege as linhas seguintes. Foi preciso por a
marca em cada linha que nomeia o morto. Nao e defeito, e limite; so nao estava registrado.

### 6. F115 -- o olho do operador achou o que nenhum gate pega

Drenando a previa, ele marcou "card longo" em **#92** e **#96** sem ver numero nenhum. Medido sobre
os 1.507 ativos (mediana **562** chars, p90 **880**):

```
  card#96   1130 chars  percentil 99,2%   <-- marcado a olho
  card#92   1059 chars  percentil 98,0%   <-- marcado a olho
  card#53    597 chars  percentil 57,1%   (marcado, mas por OUTRO defeito: "pergunta composta")
```

Ele marcou **os dois extremos do lote, ambos no topo 2% do baralho**, e nao marcou por comprimento
o de percentil 57. Existe `LIMITE_CHARS = 220`, mas mede o **verso** e so roda **na reforja**: um
card nasce com 1.130 chars espalhados por contexto+pergunta+verso sem estourar nada.

Classe: **gate-miss por ESCOPO DE ALVO** -- o sensor existe, mede a coisa vizinha, e o painel fica
verde. O `/ai-eng` classificou como **N+1 do Reachability-Debt ja promovido**, forma "sem escopo",
que com F98/F113/F115 ganha tres eixos medidos: **intencao · consulta · alvo**.

---

## Erros meus nesta sessao

1. 🔴 **Quase perdi um arquivo.** Um script meu chamou `write_text` e o encode falhou **depois** do
   open: `.claude/commands/importar-planilha.md` ficou com **0 bytes**. Recuperei do git na hora e
   refiz validando os bytes **antes** de tocar no alvo. Nada se perdeu, mas foi sorte de estar
   versionado -- `write_text` trunca antes de escrever, e a validacao tem que vir primeiro.
2. 🔴 **Escrevi uma segunda copia do vocabulario de area.** No part-7 montei um `mapa_area_bloco`
   proprio, derivado de `plano_tarefas`, antes de perceber que **`db.bloco_de` ja existia**. Isso e
   o F89 cometido por mim, na sessao em que estou fechando achados dessa familia. Apaguei; as tres
   cestas passaram a sair de `db.bloco_de`, `areas.AREAS_AGREGADAS` e `areas.area_valida`.
3. Dois defeitos na pagina do painel achados **a olho, nao por gate** (`<b>` aninhado; `url_lista`
   com caminho LOCAL virando `<a href>` que morreria publicado). Viraram teste.

---

## O desvio de spec do part-7 (medido antes de codar)

A spec mandava tirar o progresso por bloco do elo `sessoes_bulk.tarefa_id` (part-6). Medi antes:
o backfill casa **1 de 126 sessoes** (37 ambiguas, 78 sem match). Um painel alimentado so pelo elo
mostraria **~0 questoes feitas em TODO bloco** para um operador que fez 7.326 -- verde falso ao
contrario, e ele leria o painel novo como "nao andei nada".

Duas camadas, rotuladas na tela: **VOLUME** por area (cobre tudo, reconcilia exato em 7.326) e
**ELO** por tarefa (`q_feitas_por_elo`, cobertura declarada). `Simulado` (931q, 12,7%) fica fora
dos blocos porque `areas.AREAS_AGREGADAS` ja o marca como agregado -- dobrado em CM pelo fallback
do `bloco_de`, inflaria o bloco em um oitavo. Area fantasma do F89 (`GO`, 85q) ganha linha nomeada
em vez de virar CM por fallback silencioso.

**Fronteira declarada, nao estimada:** a spec pedia projecao ate ENAMED 2027. A data nao existe em
SSOT nenhum (`core/provas.json` vai ate 01/11/2026; `performance.MARCOS` nao a tem). A pagina DIZ
isso e pede o cadastro, em vez de projetar de uma data inventada (§10.8).

---

## Numeros da janela

- **Commits:** 8 (`bf7f7e9` `d97fb32` `3ae877c` `62b01e1` `fbec41a` `300919f` `98148fa` `b801a8b`)
- **Suite:** 811 -> **858** (4 testes do parser do Drive saem, 1 guarda entra; +26 da regua, +22 do painel)
- **Subagentes:** **0** -- nenhum lote passou o limiar do F93
- **Migracao de schema:** `fsrs_revlog.regua_versao` sob o rito §10.7 (backup
  `ipub_backup_20260918_114258.db`, COUNT-ASSERT escrito antes: colunas 14 -> 15, 3 tabelas
  inalteradas, 3067/3067 com a coluna NULL)
- **Remocao reversivel:** 111 linhas fora de `cronograma.py`; snapshot de 52.802 chars exportado
  com sha256 **antes** da remocao
- **Refatoracao 1.9a:** 21 arquivos, raio medido antes de mover (15 importadores de `card_checks`,
  apenas 1 em `app/`)
- **FSRS preservado:** 1543 cards / 1543 fsrs_cards o tempo todo; revlog 3067 -> 3070 (as 3
  revisoes reais do operador)

---

## Fronteiras declaradas (nao ler verde de gate como limpeza)

- **F114 mitigado, nao resolvido.** O gate de `regua_do_fit` barra *adotar sob a regua errada*. Ele
  **nao** detecta "parametro que o fit nao identificou" no caso geral -- isso exigiria medir
  cobertura por eixo no corpus, e nao existe. Ate la, a nao-adocao e a unica garantia.
- **F115 aberto.** O limiar **nao foi escolhido**: sai dos rotulos do operador (#92 p98 · #96 p99
  marcados; #53 p57 nao), reportando **precisao sobre as marcas dele**. Comprimento e proxy, nao
  defeito -- vinheta longa pode ser load-bearing (#284/F81 e o precedente), entao o predicado
  sinaliza CANDIDATO e nunca BLOCK sem triagem humana.
- **F113 segue PARCIAL** -- #685 e #689 intocados; o residuo e irregular e nao fecha por regra.
- **Elo do part-6 cobre 1 de 126 sessoes.** O painel declara isso na tela. Fechar exige decidir as
  37 ambiguas a mao -- trabalho do operador, nao meu.
- **Orcamento da Fase 1 aparece 0/2.760 no painel, e e verdade:** ele conta so volume VINCULADO a
  tarefa. O aviso ao lado explica.
- Herdadas e vivas: F100 · F104 · F105 · F87 · F99 · F109 · F111 · G10 · G5 · F89 · F79b · F66 ·
  F64 · eixo C do F81 · F80b.

---

## Rito e higiene

- `HANDOFF.md` rotacionado (`b801a8b`); numeros derivados por `day_plan --handoff-block` (F6).
- `ESTADO.md` atualizado: o macro mudou em tres pontos (Drive congelado, painel como superficie
  nova, regua v2 em vigor).
- Duas memorias do harness ganharam **cabecalho de supersessao** em vez de sumir
  (`project_cronograma_dual_ssot`, `project_planilhas_google_drive`) -- quem recall-a amanha precisa
  saber que o mundo mudou, nao encontrar silencio.
- Scratch de `tmp/` da sessao removido (§3.4). Os specs cumpridos FICAM, como as parts anteriores.
- Artifact vivo: **Painel MedHub** (`QctZqVoJriSviJetF8FYBQ`, v2). A previa do player era
  descartavel e foi apagada pelo operador.
