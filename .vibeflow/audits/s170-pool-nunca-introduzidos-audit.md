# Auditoria READ-ONLY do pool de cards nunca introduzidos (`fsrs_cards.state = 0`)

Data: 2026-09-08 · Repo `C:\Users\daanm\medhub` · db `ipub.db` aberto sempre em
`file:...?mode=ro` (URI read-only) — **zero escrita**, zero edição de arquivo do repo.

## 0. Universo e definições

| conjunto | definição SQL | n |
|---|---|---|
| ativos | `COALESCE(f.needs_qualitative,0) < 2` (`app/utils/db.py:ATIVO_WHERE`) | **1353** |
| **POOL** | ativos `JOIN fsrs_cards fc ON fc.card_id=f.id WHERE fc.state = 0` | **657** |
| **RODADO** | idem, `fc.state != 0` (state 2 = 683, state 3 = 13) | **696** |

Nota de saneamento: `fsrs_cards` tem 782 linhas com `state=0`, mas **125 delas já estão
aposentadas** (`needs_qualitative = 2`) e portanto não entram na fila. O pool real é 657 —
bate com o "~665" do enunciado. Nenhum card `state=0` tem `reps > 0`
(`select count(*) from fsrs_cards where state=0 and reps>0` → `0`), então "nunca
introduzido" é literal.

Scripts usados (todos em scratch, nenhum no repo):
`audit_pool.py`, `f81_repro.py`, `clones_pool.py`, `generica.py`, `triagem.py`,
`versao.py`, `lote.py`, `exemplos.py`, `sub.py`. Todos rodados com `python -X utf8`.
Ferramentas do repo consumidas por import, não reimplementadas:
`tools.card_checks` (6 predicados + `_norm_tokens`/`_maior_run_comum`),
`tools.audit_card_atomicity.checar_front/checar_verso`,
`tools.card_self_sufficiency.run_checks(cards=[...])` (aceita cards injetados),
`tools/detect_clones.py` (CLI, saída parseada).

---

## 1. Estratificação: taxa de defeito por predicado, POOL x RODADO

Comando: `python -X utf8 scratchpad/audit_pool.py`

| predicado | fonte | POOL n | POOL % | ROD n | ROD % | ratio POOL/ROD |
|---|---|---:|---:|---:|---:|---:|
| `campo_vazio` (fp/vr vazios) | `validar_card` | 0 | 0,0% | 0 | 0,0% | — |
| `checar_encoding` | card_checks | 2 | 0,3% | 0 | 0,0% | ∞ |
| `checar_pergunta_template` | card_checks | 0 | 0,0% | 0 | 0,0% | — |
| `checar_resposta_embutida` | card_checks | 1 | 0,2% | 1 | 0,1% | 1,06 |
| `checar_multi_parte` | card_checks | **52** | **7,9%** | 32 | 4,6% | **1,72** |
| `checar_negativo_orfao` | card_checks | **18** | **2,7%** | 8 | 1,1% | **2,38** |
| `checar_contexto_artefato` | card_checks | 0 | 0,0% | 0 | 0,0% | — |
| `checar_front` (duplo-ask) | atomicity | **69** | **10,5%** | 57 | 8,2% | 1,28 |
| `checar_verso` (multifato) | atomicity | 75 | 11,4% | **118** | **17,0%** | **0,67** |
| `opcao-anaforico` | self_sufficiency | 4 | 0,6% | 2 | 0,3% | 2,12 |
| `deitico` | self_sufficiency | 3 | 0,5% | 1 | 0,1% | **3,18** |
| `pct-fake` | self_sufficiency | 0 | 0,0% | 0 | 0,0% | — |
| **F81 eixo A** (containment ≥0,70) | novo | 14 | 2,1% | 12 | 1,7% | 1,24 |
| **F81 eixo B** (Por que + negado, estrito) | novo | 2 | 0,3% | 3 | 0,4% | 0,71 |
| F81 eixo B (regex ampla) | novo | 9 | 1,4% | 16 | 2,3% | 0,60 |

Agregados:

- **card com ≥1 achado (qualquer predicado): POOL 144/657 = 21,9% · RODADO 176/696 = 25,3%.**
- card com ERRO de write-gate (campo vazio / encoding / template / resposta embutida):
  POOL 3 (0,5%) · RODADO 1 (0,1%).
- contexto vazio: **POOL 322/657 = 49,0% · RODADO 125/696 = 18,0%.**

### Leitura — a resposta à pergunta central

**Não. O pool NÃO está inflado por lixo de autoria.** Em agregado ele é *ligeiramente mais
limpo* que o corpus já rodado (21,9% x 25,3%), e o defeito irrecuperável é praticamente
inexistente (3 ERROs de gate em 657 cards = 0,5%).

Mas a média esconde duas coisas, e as duas importam:

1. **A inversão vem de um único predicado, e ele é de VERSO.** `resposta-multifato`
   (`checar_verso`) é 17,0% no rodado x 11,4% no pool. É o único eixo em que o rodado perde.
   Tirando ele, o pool perde em TODOS os eixos de FRENTE: multi-parte 1,72x,
   negativo-órfão 2,38x, deítico 3,18x, opção-anafórico 2,12x, duplo-ask 1,28x.
   **Defeito-FRENTE: POOL 106/657 = 16,1% · RODADO 12,3% em v1.**

2. **A comparação bruta é injusta com o pool — e por isso subestima o problema.**
   O rodado já passou por reforja: 111 cards em `card_version=3`, 47 em v4, 11 em v5, 3 em v6.
   O pool é 528/657 = **80% em `card_version=1`, nunca tocado.** Comparando like-for-like
   (só v1):

   | | n | ≥1 achado | defeito-FRENTE |
   |---|---:|---:|---:|
   | POOL v1 | 528 | 24,1% | **16,5%** |
   | RODADO v1 | 350 | 25,4% | **12,3%** |

   Ou seja: o pool a v1 tem **1,34x mais defeito de frente** que os cards v1 que já foram
   introduzidos. E o rodado v4 (o mais reforjado) tem 46,8% de achados — quase todos
   `atom_verso` (20/47) — evidência de que **a reforja engorda o verso**: cada rodada de
   reescrita adiciona frase e estoura os 220 chars de `LIMITE_CHARS`
   (`tools/audit_card_atomicity.py:105`).

---

## 2. F81 aplicado ao pool

Reprodução da varredura do ledger antes de estratificar (`f81_repro.py`):
906 cards ativos com contexto+pergunta preenchidos (F81 diz 904 — delta de 2, provavelmente
`IS NOT NULL` x `.strip()`), **26 cards no eixo A (2,9%)** — bate exatamente.
Containment dos cards que o usuário flagrou: #321 = 0,467 · #243 = 0,095 · #365 = 0,200 ·
#792 = 0,000 — os quatro valores conferem com o texto de `AUDITORIA_MEDHUB.md:1475`.
Casos extremos também conferem: #673 = 1,000 · #525 = 0,900 · #664 = 0,875.
Definição usada: `containment = |tokens(contexto) ∩ tokens(pergunta)| / |tokens(contexto)|`,
sobre `card_checks._norm_tokens`.

**Denominador correto para o eixo A/B é só quem tem contexto** (POOL 335, RODADO 571):

| eixo | POOL | RODADO |
|---|---|---|
| A — contexto redundante (≥0,70) | **14 / 335 = 4,2%** | 12 / 571 = 2,1% |
| B — `^Por que` + negado estrito (`não pode/deve/entra`) | 2 / 335 = 0,6% | 3 / 571 = 0,5% |
| B — regex ampla (`^Por que` + qualquer `não <verbo>`) | 9 / 335 = 2,7% | 16 / 571 = 2,8% |

**Normalizado, o eixo A é 2,0x pior no pool.** É o achado F81 mais acionável aqui: o pool
tem metade dos cards SEM contexto nenhum (49%) e, entre os que têm, o dobro de contexto que
não faz trabalho.

Eixo B estrito no pool = **#1216, #1375**. Nota: **#1375 é o falso-positivo que o próprio
F81 nomeia como card legítimo** (`AUDITORIA_MEDHUB.md:1473`, daptomicina no VRE). Sobra
**1 card real** no pool sob o critério estrito. Com a regex ampla sobem 9 (#774, #936, #946,
#1216, #1252, #1330, #1372, #1375, #1411), mas a triagem humana continua obrigatória —
o eixo B tem falso-positivo estrutural, como o ledger já registra.

Eixo B na minha regex ampla dá **11** no corpus inteiro contra os **10** do F81 (ids
291, 321, 365, 396, 410, 946, 1041, 1216, 1375, 1411, 1537). Não reproduzi o corte exato do
ledger — reporto o delta em vez de inventar o número.

Eixo C (contrafactual, ex. #792) **não foi medido** — é semântico, como o F81 determina.

---

## 3. Clones

`python -X utf8 tools/detect_clones.py --limiar 0.72` → **6 pares** em 1353 cards ativos,
256 temas. Classificados por state (`clones_pool.py`):

| classe | 0,72 | 0,60 |
|---|---:|---:|
| POOL ~ RODADO (card novo duplicando consolidado) | **2** | 11 |
| POOL ~ POOL | 3 | 6 |
| RODADO ~ RODADO | 1 | 3 |

Pares POOL~RODADO no limiar oficial:
- `0,82 [Ginecologia/Vulvovaginites] #746(s0) ~ #1444(s2)`
- `0,73 [Preventiva/Sistemas de Informação] #902(s0) ~ #372(s2)`

`detect_clones.py` só compara **dentro do mesmo tema** (`by_tema` em
`tools/detect_clones.py:44`). Varri POOL x RODADO **cross-tema** com o mesmo
`SequenceMatcher ≥ 0,72` e achei **1 par adicional**:
- `0,89 #1014(pool, Cirurgia Infantil) ~ #244(rodado, Icterícia e Sepse Neonatal)` —
  "Qual a causa mais comum de colestase neonatal cirúrgica (extra-hepática)?"

**Total: 3 cards do pool são near-duplicates de cards já em revisão (#746, #902, #1014) =
0,46% do pool.** Clone não é fonte de inflação.

**Achado colateral, mais grave que os clones:** `frente+verso` idênticos = **0 grupos**, mas
**`frente_pergunta` idêntica = 10 grupos / 49 cards**. São stems genéricos:

```
['#32','#37','#38','#432','#436','#446','#449','#452','#453','#529','#543','#1501(s0)'] :: "qual a conduta?"
['#97','#427','#458','#625','#716(s0)','#724(s0)','#744','#747','#957(s0)']              :: "qual o diagnóstico?"
['#120','#783(s0)','#799(s0)','#805(s0)','#1504(s0)','#1512(s0)','#1520(s0)']            :: "qual o diagnostico mais provavel?"
['#406','#528','#531','#594(s0)','#1487(s0)']                                            :: "qual a principal hipotese diagnostica?"
```

Isso **não** é clone (os versos diferem) — é a classe inversa do eixo A do F81: a **pergunta
não carrega informação nenhuma** e toda a discriminação mora no contexto. Nenhum predicado
existente pega. Frequência: `pergunta-generica` (regex de stem + ≤7 tokens) = **26/657 = 4,0%
no pool** x 52/696 = 7,5% no rodado — logo é padrão do corpus, **não** inflação do pool, e
todos os 26 do pool têm contexto preenchido (0 sem contexto). Não sobe para balde nenhum,
mas merece linha própria no ledger como classe nomeada.

---

## 4. Triagem acionável — 3 baldes (657 cards)

`scratchpad/triagem.json` tem as listas completas de ids.

| balde | n | % do pool |
|---|---:|---:|
| **APOSENTAR** | **4** | 0,6% |
| **REFORJAR — frente** | **102** | 15,5% |
| REFORJAR — só verso (multifato) | 41 | 6,2% |
| **OK** | **510** | 77,6% |

Critério de balde (explícito, para poder ser contestado):
- APOSENTAR = `resposta_embutida` OU `pergunta_template` OU clone de card já rodado
  (SequenceMatcher ≥ 0,72) OU (`negativo_orfao` **e** `opcao_anaforico` juntos → irrespondível).
- REFORJAR-frente = qualquer de `f81_A`, `f81_B`, `multi_parte`, `atom_front`,
  `negativo_orfao`, `deitico`, `opcao_anaforico`, `encoding`, `contexto_artefato`.
- REFORJAR-verso = só `atom_verso` disparou (defeito de verso, separado por honestidade:
  é o único eixo em que o pool é MELHOR que o rodado, logo não é inflação do pool).
- OK = nenhum predicado dispara.

Checagem: `negativo_orfao AND opcao_anaforico` = **0 cards** no pool. Nenhum card do pool é
irrespondível pelos dois critérios simultâneos.

### 4.1 APOSENTAR — os 4 (lista completa, não amostra)

| card | predicado | texto ofensor |
|---|---|---|
| **#696** [CM/Síndrome do Olho Vermelho] q=447 | `resposta-embutida (titulo do erro, run>=6)` | pergunta: *"Segundo o gabarito das bancas (não a epidemiologia pediátrica real), qual é a causa mais comum de exoftalmia unilateral?"* — a frente repete o título da questão-mãe |
| **#746** [GO/Vulvovaginites] q=494 | clone de #1444 (s2), sim=0,82 | *"Quais os agentes mais comuns da vaginite aeróbia?"* |
| **#902** [Preventiva/SIS] q=206 | clone de #372 (s2), sim=0,73 | *"Com que periodicidade se notifica a doenca de Chagas AGUDA?"* |
| **#1014** [Cir/Cirurgia Infantil] q=468 | clone cross-tema de #244 (s2), sim=0,89 | *"Qual a causa mais comum de colestase neonatal cirúrgica (extra-hepática)?"* |

### 4.2 REFORJAR-frente — sub-baldes (card pode contar em mais de um)

`atom_front` 69 · `multi_parte` 52 · `negativo_orfao` 18 · `f81_A` 14 ·
`opcao_anaforico` 4 · `deitico` 3 · `encoding` 2 · `f81_B` 2.

Sub-tipos de `atom_front`: `duplo-ask/conectivo` 55 · `duplo-ask/segundo-nucleo` 10 ·
`duplo-ask/duas-interrogacoes` 4.

**15 mais claros** (ordem: eixo A por containment desc, depois irrespondíveis, depois duplo-ask):

| # | predicado | linha ofensora |
|---|---|---|
| **#988** | f81-A cont **1,00** | ctx `Cardiopatias congênitas canal-dependentes.` — a pergunta repete "ambas cardiopatias congênitas canal-dependentes" |
| **#1273** | f81-A cont **1,00** | ctx `Choque hemorrágico refratário por fratura pélvica instável, com FAST negativo.` — pergunta abre com a mesma frase inteira |
| **#605** | f81-A 0,89 | ctx `Pe diabetico com necrose e doenca arterial periferica (isquemia).` |
| **#664** | f81-A 0,88 | ctx `Gestante convulsionando por eclampsia; **pergunta a PRIMEIRA medida**.` — artefato de pipeline dentro do campo (já citado em F81) |
| **#1275** | f81-A 0,86 | ctx `Triagem laboratorial de doadores de sangue no Brasil.` |
| **#1280** | f81-A 0,85 | ctx `Síndrome da veia cava superior em tabagista de longa data, com massa mediastinal.` |
| **#599** | f81-A 0,78 + multi-parte + duplo-ask | *"...esconde um deficit corporal, **e como isso muda a conduta?**"* — 2 critérios de acerto |
| **#662** | f81-A 0,75 | *"hCG que sobe/plateia pos-molar (ou invasao miometrial): **diagnostico e conduta?**"* |
| **#1253** | f81-A 0,75 | ctx `Publicidade médica em mídias digitais, sob a Resolução CFM 2.336/2023.` — pergunta recita a resolução de novo |
| **#1277** | f81-A 0,75 | ctx `Criança pequena, assintomática, contactante domiciliar de tuberculose bacilífera.` |
| **#1278** | opção-anafórico | *"Por que solicitar **'apenas PPD, inicialmente'** está errado..."* — cita alternativa que não está no card |
| **#1268** | deítico | *"**Numa alternativa** sobre conduta em abdome agudo perfurativo, que tipo de palavra dentro da própria descrição..."* — card sobre a prova, não sobre medicina |
| **#977** | opção-anafórico | *"Por que a imunizacao passiva **nao serve** para erradicar uma doenca?"* + contexto vazio |
| **#620** | duas interrogações | *"O bloqueio vacinal do sarampo só é feito após confirmação do caso? **E quem é o alvo?**"* |
| **#682** | duas interrogações | *"...qual teste de Coombs e positivo? **E qual o efeito da transfusao de hemacias normais sobre o VCM...?**"* |

Menções honrosas do mesmo balde (todas com o texto conferido):
#647 (`Qual delineamento é mais eficiente para uma DOENÇA rara e qual para uma EXPOSIÇÃO rara?` — duplo critério + seta Unicode no `verso_armadilha`),
#617 (seta Unicode, `checar_encoding`), #639, #641, #646, #877, #1372, #1362.

**Falso-positivo já mapeado, NÃO reforjar:** #1375 (daptomicina/VRE) cai em `negativo_orfao`
e `f81_B` mas o ledger F81 o declara card legítimo. Idem a classe "card discriminador" do
`duplo-ask` (`tools/audit_card_atomicity.py:33-43`) — os 55 `duplo-ask/conectivo` precisam do
desempate "conte os CRITÉRIOS DE ACERTO, não as entidades" antes de virar fila.

### 4.3 OK — 510 cards (amostra 15)

#327, #329, #333, #335, #337, #339, #341, #343, #345, #347, #349, #351, #357, #359, #375.
Exemplos: `#335 Que achado simples do exame permite concluir, sem exames complementares, que
as vias aéreas e a respiração estão adequadas?` · `#375 No diagnóstico diferencial entre
cancro mole e LGV, o que o número de orifícios de fistulização do bubão discrimina?`
Todos com pergunta de critério único e alvo explícito.

---

## 5. Concentração: os defeitos NÃO estão espalhados

Denominador: os 106 cards do pool com defeito-FRENTE (APOSENTAR + REFORJAR-frente).

### 5.1 Por faixa de id (lote de cunhagem) — o achado mais forte

| faixa de card_id | defeito-frente | taxa |
|---|---:|---:|
| 300-399 | 0/15 | 0,0% |
| 500-599 | 2/13 | 15,4% |
| **600-699** | **28/75** | **37,3%** |
| **700-799** | **16/57** | **28,1%** |
| 800-899 | 12/72 | 16,7% |
| 900-999 | 4/86 | 4,7% |
| 1000-1099 | 4/39 | 10,3% |
| 1100-1199 | 3/45 | 6,7% |
| 1200-1299 | 13/89 | 14,6% |
| 1300-1399 | 14/78 | 17,9% |
| 1400-1499 | 6/57 | 10,5% |
| 1500-1599 | 1/31 | 3,2% |

**A faixa 600-799 tem 132 cards (20,1% do pool) e carrega 44/106 = 41,5% de todo o defeito
de frente do pool.** Taxa 33,3% contra 11,6% no resto.

Caracterização do lote 600-699 (`lote.py`): 75 cards, **71 em `card_version=1`**, 68
questões-mãe distintas com `questao_id` de 37 a 448 e `data_registro` de **2026-03-14 a
2026-07-03** — ou seja, é um **backfill retroativo**: cards cunhados de uma vez sobre um
histórico de erros de ~4 meses, não a cunhagem incremental do dia. Predicados que disparam
no lote: `atom_verso` 33, `atom_front` 22, `multi_parte` 18, `f81_A` 4, `encoding` 2,
`negativo_orfao` 2, `resposta_embutida` 1. Temas mais representados: Síndromes Hipertensivas
da Gestação (10), Síndrome do Olho Vermelho (10), Anemias Hemolíticas (9), Doenças
Exantemáticas (7).

O lote 700-799 tem o mesmo perfil (qid 461-547, 2026-07-04..07-12): `atom_verso` 19,
`atom_front` 15, `multi_parte` 12, `negativo_orfao` 4.

Contraprova de que é lote e não deriva temporal: a faixa 900-999 (86 cards, qid 50-574,
datas sobrepostas com o lote ruim) tem 4,7% de defeito — a **mais limpa** do pool.

### 5.2 Lotes por `questao_id` (mesma questão-mãe, ≥2 cards defeituosos)

- `q#365` → **3/4** defeituosos: #604, #605, #606 (Pé diabético; os três com contexto que a
  pergunta reengole)
- `q#812` → **2/2**: #1275, #1276 (Segurança Transfusional — 100% do lote)
- `q#813` → **2/2**: #1277, #1278 (ILTB — 100% do lote)
- `q#363` → 2/5: #596, #599 · `q#608` → 2/4: #892, #893

### 5.3 Por área / tema (só temas com ≥5 cards no pool)

Área: Otorrino 33,3% (2/6) · Psiquiatria 30,8% (4/13) · **Endocrino 30,0% (9/30)** ·
Clínica Médica 27,3% (6/22) · **Preventiva 26,3% (10/38)** · Reumato 26,3% (5/19) ·
Obstetrícia 20,6% (7/34) · Pediatria 17,6% (15/85) · Pneumo 15,2% (5/33) ·
Cirurgia 14,6% (14/96).

Tema: Colecistite/Colangite 50,0% (4/8) · Doenças Exantemáticas 44,4% (4/9) ·
**DM Complicações Crônicas 41,7% (5/12)** · SVCS 40% (2/5) · Distúrbios Ácido-Base 40% (2/5) ·
DM2 40% (2/5) · LES 33,3% (4/12) · Anemias Hemolíticas 33,3% (3/9).

---

## 6. Predicados que NÃO rodaram / limites declarados

- **F81 eixo C (contrafactual)** — não medido, por instrução e por natureza (semântico).
- **`checar_distrator`** — é predicado por QUESTÃO, não por card; exige o conjunto de cards
  derivados de cada `questao_id` e o campo `alternativa_marcada`. Fora do escopo "por card"
  desta estratificação; não rodei, não estimei.
- **`tools/audit_flashcard_quality.py`** — não rodado: os predicados que ele expõe já estão
  cobertos por `card_checks` (é a biblioteca única declarada no cabeçalho do próprio
  `card_checks.py`). Rodá-lo produziria dupla contagem, não informação nova.
- **`detect_clones.py`** só compara dentro do tema; a varredura cross-tema POOL x RODADO foi
  feita com o mesmo `SequenceMatcher` e o mesmo limiar 0,72, pré-filtrada por Jaccard ≥ 0,45.
- **Eixo B do F81**: minha regex ampla dá 11 no corpus contra os 10 do ledger. Delta reportado,
  não reconciliado.
- Todos os predicados são regex/estatísticos: **classificam sintaxe, não clínica.** Os 510
  "OK" são "OK para o harness", não "OK auditados por leitura".

---

## 7. Conclusão em uma frase

O pool de 657 cards nunca introduzidos **não é lixo de autoria** — 77,6% passa limpo em todos
os predicados existentes e só 0,6% (4 cards) é irrecuperável; mas **é sistematicamente pior
que o corpus rodado no eixo da FRENTE** (16,5% x 12,3% comparando v1 com v1), com o defeito
concentrado num backfill identificável (cards #600-799, 20% do pool carregando 41,5% do
defeito) — logo o remédio não é encolher a fila, é **reforjar 102 frentes, com prioridade no
lote 600-799**, e aposentar 4.
