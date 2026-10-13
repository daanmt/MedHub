# Auditoria do CSS das aulas (43 arquivos `artifacts/aula-*.html`)

Inventário SOMENTE LEITURA para o refinamento visual da camada de leitura (`core/templates/tema-aula.css`). Gerado em 13/10/2026 01:08 por scripts (parser `html.parser` para o HTML, parser simples de CSS, Edge headless para medir); nenhum arquivo do repositório foi alterado. Convenção: `aulas` = quantas das 43 aulas; `ocorr.` = nº de elementos; fam. = família de template (§4).

## 1. Resumo executivo (o que mais importa para reescrever a camada)

- **Universo**: 43 aulas, 274 classes distintas no corpo (101 usadas por >= 2 aulas, 173 por uma só), 6 famílias de template (§4). Cada aula traz CSS próprio (1 `<style>`, 58 a 141 regras), sem `<body>`/DOCTYPE; o hub embrulha e injeta `tema.css` + `tema-aula.css` DEPOIS do CSS da aula (§13.1).
- **Callouts = 3 significados, todos por token**: `.trap` (31 aulas, 118 elementos) = `border-left:3px solid var(--carmine)` + `background:var(--carmine-wash)`; `.banca` (19, 51) = amber; `.aside` (6, 8) = teal; mais, nas RD, `div.note` (5 aulas, amber) e `.key` (teal). Rótulo `.albl` colorido com `--carmine-ink/--amber-ink/--teal-ink`. As variantes entre aulas são só padding/margem/corpo do texto; a única troca de token é a neuromusculares (`--acc*` no `.aside`). Hoje a camada zera a borda dos 3 primeiros (L4).
- **Diagramas = um só vocabulário**: grade com `gap:1px` sobre `background:var(--line2)` + `border:1px solid var(--line2)` + células `--card`/`--sunk` (`.vs` 35 aulas, `.trig` 21, `.arms` 15, mais `.cmap/.if3/.spec/.cream`); caixas `--card` + `--line2` (`.crit` 37, `.tw` 12, `details.ref` 15, `.synth` 21). Nenhuma cor literal no CSS das aulas fora dos blocos `:root` e nenhum `border-radius` em caixa/callout/grade (§7.1, §8, §9).
- **Tokens**: 21 nomes padrão em 41 aulas; fogem só 2 por PALETA (autópsia, nomes próprios; neuromusculares, `--acc*`) e 4 por variável de layout inline (`--cols`). `--plum*` só existe em 2 aulas. Mapeamento pronto no §8.3.
- **Inline**: 38 atributos `style=` em 10 aulas; só 3 mexem em cor (`color:var(--ink3)`) e nenhum usa cor literal; 5 atributos SVG `stroke="var(...)"` na glomerulopatias.
- **Cabeçalho**: a 390 px o trecho do topo até o 1º degrau ocupa em média EN 738 px, ER 869 px e RS 296 px. As caixas/chips: `nav.nav a` (16 aulas), `nav.rail a` (6 aulas, vira pílula), `.stats` (21 aulas, números em mono), `.ruler/.spec/.tl` (4 aulas). Ver §10.
- **Celular**: nenhuma aula tem rolagem horizontal da página (aula crua, v2.4 e v3, 390 e 704 px). O risco real é o `.tw{overflow:hidden}` da camada: 14 tabelas cortadas em 4 aulas a 390 px, onde a aula crua rolava (L1). Único `position:sticky` = `.rail` (6 aulas, sem efeito no iframe); `white-space:nowrap` em 2 aulas (dossie-uerj, kawasaki). Todas as 58 tabelas estão, nas aulas, em contêiner com `overflow-x:auto` (§11).
- **Coluna de leitura**: só as 13 aulas com `<main>` herdam os 38rem; as outras 30 usam o `.wrap` inteiro (644-664 px a 704 px, ~81-86 car./linha) e a camada ainda troca os 760/780px das aulas por 62rem (L2).
- **Cor do texto**: 22% dos 16838 elementos de texto saem em ciano (`strong` 1331, `span.k` 885, `span.tk` 275, `summary` 239, `span.v` 153); título e rótulo disputam o mesmo ciano/rosa/pêssego, e o `text-transform:none` deixa `letter-spacing` de caixa-alta em 39 aulas (L3, L6, L15; §13.4).
- **Resumo** (`CSS_RESUMO`, 26 regras + 3 blocos de token, tokens `--papel --card --afundado --tinta* --linha --acento*`): recebe as duas camadas por cima (`strong` e `th` ciano, `code/pre` sem mono, corpo 17px). A 704 px o `.wrap` é o do iframe com ou sem a camada; a camada só alarga o resumo se o iframe passar de 736 px (§12).
- **Painel**: recebe a mesma camada (mesma função `carregar`); seletores de tag (`body h2 h3 table th td details summary`) valem para ele também (§13.1).
- **tema.css v3 em curso** (tokens + base) já não tem as regras de aula do v2.4 (`.top h1 text-shadow`, `.aside`, `.dnum`...); o commit BASE (def2fdd) ainda as tem (§13.3). O `--wrap:46rem` (v3) faz o iframe ter <= 704 px: o trilho lateral e o `.body` de 2 colunas nunca aparecem no hub.
- **Reescrita**: o `tema.css` v3 e um `tema-aula.css` novo foram commitados durante a auditoria (b84ce58 design (s225): tema v3 retrowave contido -- tema.css fonte unica (tokens + base); regras de componente voltam aos arquivos das telas). Esta auditoria descreve a camada ANTERIOR (commit BASE def2fdd, a que o pedido descreve, sobre os tokens v3) e o §15 repete as métricas sobre a camada nova no instante do snapshot.

## 2. Estado do repositório e arquivos lidos

O repositório estava sendo alterado em paralelo durante esta auditoria (`core/templates/tema.css` virou v3 'retrowave contido'; `hub.html`, `player.html`, `tools/painel.py`, `docs/UI.md`, `tools/ui_capturas.py` e, no fim, o próprio `tema-aula.css`, commitados depois do commit BASE). BASE desta auditoria: a camada de leitura do commit `def2fdd` (o HEAD quando o pedido foi feito: `tema-aula.css` de 70 linhas + `tema.css` v2.4) medida sobre os tokens do `tema.css` v3 (variante `v3`); o `tema.css` v2.4 do commit BASE aparece como `v24`; a camada reescrita só entra no §15. Os números valem para o snapshot desta tabela; a reprodução está no Apêndice D.

| arquivo | versão | bytes | sha1 (LF) | mtime / origem |
|---|---|---|---|---|
| `core/templates/tema.css` | working tree = v3 (tokens usados na BASE) | 6189 | f5adf7af9025 | 2026-10-13T00:30:03 |
| `core/templates/tema-aula.css` | working tree = camada REESCRITA (só no §15) | 7698 | 7a44c69dc895 | 2026-10-13T00:40:35 |
| `core/templates/tema-aula.css` | commit BASE def2fdd = camada das seções 6-14 | 3899 | 6dc02f9572aa | commit BASE |
| `core/templates/tema.css` | commit BASE def2fdd, v2.4 (variante v24) | 8861 | 972aaa3353c0 | commit BASE |
| `core/templates/hub.html` | working tree | 175954 | 575210fad10c | 2026-10-13T00:40:35 |
| `tools/hub.py` | working tree (CSS_RESUMO) | 119989 | fc9cf6528617 | 2026-10-12T17:53:57 |
| `artifacts/painel.html` | working tree | 47750 | 9ef844373d97 | 2026-10-13T00:46:40 |

Commit BASE = def2fddc7b2e5b0f180cb59be32c6a3557430860 2026-10-12T23:49:38-03:00 backlog (s225): P23 elos em toda . HEAD no momento do snapshot = b84ce58fd04cef57eab5d336773408d4236d9caa 2026-10-13T00:52:57-03:00 design (s225): tema v3 retrowave .
`tema.css`: o commit BASE é o v2.4 (tokens + algumas regras de aula); o working tree é o v3 (só tokens + base). Medido com o v3 e, para comparação, com o v2.4 (§11.3, §13.3).

## 3. Método (resumo)

HTML: `html.parser` (fragmentos sem `<body>`; 0 tags abertas sem fechamento no total das aulas). CSS: parser próprio de blocos aninhados; 'CSS efetivo' = dobra das regras de nível raiz por especificidade e ordem. Medidas: Edge headless com a MESMA montagem do hub (`comTema`/`documentoCompleto`), iframes de 390 e 704 px, Atkinson carregada. Detalhes e limites no Apêndice D.

## 4. Famílias de template

Heurística: sem `.top` = autópsia; nome `rd-*` + `.sec` = RS; `rd-*` + `.degrau` = RG; `.sec` fora de RD = dossiê; `.degrau` + `.rail` = ER; `.degrau` + `nav.nav` = EN. A soma fecha em 43.

| cód. | família | aulas | o que é | aulas |
|---|---|---|---|---|
| EN | escada-nav | 15 | aula-base 'escada' com chips `nav.nav` e `.stats` no cabeçalho, conteúdo direto em `.wrap` (sem `<main>`) | anemias-macrociticas, aorta-cardiomiopatias-pericardio, cronicas-aps-metas, iamcsst, idoso-amg-polifarmacia, imagem-obstetrica, insuficiencia-adrenal, mccp-decisao-compartilhada +7 |
| ER | escada-rail | 6 | aula-base 'escada' com `div.body` (grade) + `nav.rail` lateral + `<main>` | dmg, glomerulopatias, kawasaki, neuromusculares, prevencao-quaternaria, topicos-pediatria |
| RS | RD-sec | 13 | revisão direcionada em seções `.sec`/`.kick`, sem `<main>` | rd-cir-0610, rd-cm-0610, rd-dm-cronicas, rd-go-0610, rd-hemostasia-2, rd-hernias, rd-meningites, rd-neoplasias-tgi +5 |
| RG | RD-degrau | 7 | revisão direcionada em `.degrau` dentro de `<main>` | rd-dii-polipos, rd-hemostasia, rd-hepato, rd-intensiva-sepse, rd-lupus-saf, rd-ventilacao-degrau-0, rd-vias-biliares |
| DO | dossiê | 1 | template próprio (`.sec` + `.mal` + 26 tabelas `.tw`) | dossie-uerj |
| AU | autópsia | 1 | template próprio (sem `.top`, tokens próprios, 89 `details`) | autopsia-uerj-2021 |

## 5. Classes do corpo, por papel

Contagem sobre o HTML do corpo (parser `html.parser`, 43 aulas). `aulas` = quantas das 43 aulas usam; `ocorr.` = nº de elementos; `fam.` = quantas aulas de cada família (legenda no §4). A coluna `classes internas` mostra `aulas/ocorrências` de cada parte.

### 5.1 Cabeçalho (masthead)

| componente | aulas | ocorr. | fam. | classes internas (aulas/ocorr.) | papel |
|---|---|---|---|---|---|
| `header.top` | 42 | 42 | EN15 ER6 RS13 RG7 DO1 | div.wrap 43/43 | a autópsia usa `<header>` sem classe (e sem `.top`) |
| `p.eye` | 42 | 42 | EN15 ER6 RS13 RG7 DO1 |  | linha de contexto acima do h1 (`MedHub - Aula-base - Área - ...`) |
| `h1` | 43 | 43 | EN15 ER6 RS13 RG7 DO1 AU1 |  |  |
| `p.sub` | 42 | 42 | EN15 ER6 RS13 RG7 DO1 |  | subtítulo do cabeçalho (a mesma classe `.sub` também nomeia h3/h4/details em outras partes) |
| `div.stats` > `div.stat` (b + span) | 21 | 21 | EN15 ER3 RG3 | div.stat 21/90 | faixa de números-chave abaixo do subtítulo (cada `.stat` = `b` valor + `span` legenda) |
| `div.spec` / `div.tl` (+ `span.tn`) | 3 | 3 | ER3 | span.tn 3/15 | grade de rótulo+valor no cabeçalho (glomerulopatias: `.spec`; prevenção/tópicos: `.tl`); o `.tv` é o mesmo de `.trig .tv` |
| `div.ruler` (+ `.bar`, `.cols`, `.foot`) | 1 | 1 | ER1 | .bar 2/2; .cols 1/1; .foot 1/1 | régua do tempo do cabeçalho da kawasaki (única) |

### 5.2 Navegação

| componente | aulas | ocorr. | fam. | classes internas (aulas/ocorr.) | papel |
|---|---|---|---|---|---|
| `nav.rail` (+ `p.rlab`, `a > span.rn`) | 6 | 6 | ER6 | p.rlab 6/6; span.rn 6/67 | trilho de degraus; vira fileira de pílulas em <= 920px |
| `nav.nav` (links `a`) | 16 | 16 | EN15 RG1 |  | fileira de chips com borda 1px, raio 2px |
| `div.body` | 6 | 6 | ER6 |  | grade 2 colunas (trilho + main) da família escada-rail |
| `<main>` | 13 | 13 | ER6 RG7 |  | as aulas sem `<main>` escrevem direto em `.wrap` |

### 5.3 Degraus e seções

| componente | aulas | ocorr. | fam. | classes internas (aulas/ocorr.) | papel |
|---|---|---|---|---|---|
| `section.degrau` (+ `.dhead`, `.dnum`, `.dtitle`, `.dstage`) | 28 | 325 | EN15 ER6 RG7 | .dhead 28/325; .dnum 28/325; .dtitle 28/325; .dstage 13/115 | unidade da escada; número + título (o título é `h2` em umas aulas e `h3` em outras; ver L8) |
| `div.ato` (+ `span`, `h2`) | 11 | 37 | EN11 |  | faixa divisória de 'ato' entre grupos de degraus (fundo wash + filete esquerdo 3px) |
| `section.sec` (+ `span.kick`) | 14 | 107 | RS13 DO1 | span.kick 14/107 | seção das RD-sec e do dossiê; `kick` = rótulo acima do h2 |
| `.blk` / `details.blk` (+ `.blks`, `.blks-lede`) | 5 | 38 | RS4 DO1 | .blks 1/1; .blks-lede 1/1 | bloco curto das pílulas / acordeão do dossiê |

### 5.4 Texto

| componente | aulas | ocorr. | fam. | classes internas (aulas/ocorr.) | papel |
|---|---|---|---|---|---|
| `p.lede` | 41 | 357 | EN15 ER6 RS12 RG7 DO1 |  | frase de abertura de cada degrau/seção (itálico nas aulas) |
| `div.prose` (ul/li) | 28 | 298 | EN15 ER6 RG7 |  | lista de pontos do degrau (li 15.4-15.6px) |
| `ul.pt` / `ol.pt` | 14 | 138 | RS13 DO1 |  | lista de pontos das RD-sec e do dossiê |
| `h3.sub` / `h4.sub` | 9 | 37 | ER6 RG3 | h3.sub 2/13; h4.sub 7/24 | sub-título dentro do degrau (a camada só mira `h3.sub`) |
| `.src` (span ou p) | 23 | 219 | EN12 ER1 RS10 | span.src 12/154; p.src 11/65 | fonte da seção (mono 11.5px) ou nota de fonte (12.6px) |
| `p.cap` / `p.hint` | 4 | 7 | ER3 RG1 | p.cap 2/4; p.hint 2/3 | legenda de tabela ('Role a tabela para o lado no celular') |
| `footer` (+ `footer p`) | 22 | 22 | EN15 ER6 RG1 |  | rodapé de fonte/escopo |
| `code` | 32 | 170 | EN15 ER6 RS10 RG1 |  | caminhos de arquivo (resumos/...); 11-12px mono |

### 5.5 Callouts

| componente | aulas | ocorr. | fam. | classes internas (aulas/ocorr.) | papel |
|---|---|---|---|---|---|
| `div.trap` (armadilha) | 31 | 118 | EN13 ER6 RS10 RG2 |  | carmine: filete 3px + wash |
| `div.banca` (como cai na banca) | 19 | 51 | EN15 ER4 |  | amber: filete 3px + wash |
| `div.aside` (nota) | 6 | 8 | ER5 RG1 |  | teal: filete 3px + wash |
| `.albl` (rótulo do callout) | 23 | 157 | EN15 ER6 RG2 | div.albl 22/151; p.albl 1/6 | primeiro filho do callout |
| `div.note` (callout das RD-sec) | 5 | 5 | RS5 |  | amber; `p.note` das sínteses é legenda, não callout |
| `.key` (callout das RD-sec e do dossiê) | 3 | 18 | ER1 RS1 DO1 | p.key 1/12; div.key 2/6 | teal; `.row.key` do kawasaki é linha de tabela |
| `div.star` | 2 | 2 | ER2 |  | caixa neutra (card + borda 1px) com `.albl` cinza |
| `.disc` / `.fonte` (div) | 2 | 8 | EN2 | div.disc 1/7; div.fonte 1/1 | callout teal (uma aula cada: rodapés / vulva-vagina) |
| `span.ff` / `span.fora` / `span.bd` | 5 | 17 | EN3 ER1 DO1 | span.ff 3/10; span.fora 1/2; span.bd 1/5 | etiquetas em linha ('fora da apostila', 'banca-dependente') |

### 5.6 Diagramas e quadros

| componente | aulas | ocorr. | fam. | classes internas (aulas/ocorr.) | papel |
|---|---|---|---|---|---|
| `div.vs` (+ `.a`, `.b`) | 35 | 85 | EN12 ER5 RS10 RG7 DO1 | .a 35/84; .b 35/86 | comparação em 2 colunas; `.a` carmine, `.b` teal |
| `div.cmap` / `div.if3` / `div.cream` / `div.branches` | 2 | 5 | ER2 |  | quadros específicos de poucas aulas (ver coluna `aulas`) |
| `div.trig` (+ `.tk`, `.tv`) | 21 | 21 | EN15 ER6 | span.tk 21/301; span.tv 21/306 | gatilhos da síntese (grade 1px) |
| `div.arms` > `div.arm` (+ `span.dot`) | 15 | 15 | ER6 RS3 RG6 | div.arm 15/110; span.dot 15/110 | lista de armadilhas com bolinha carmine |
| `section.synth` (+ `h2`, `p.note`) | 21 | 36 | EN15 ER6 | p.note 16/30 | síntese de fim da aula |
| `section.synth.arm` (+ `ol.armas`) | 13 | 13 | EN13 | ol.armas 12/12; ol.arml 1/1 | síntese de armadilhas (classe `arm` num `<section>`) |
| `div.crit` (+ `.row`, `.k`, `.v`, `.hd`, `.c3`/`.c4`) | 37 | 190 | EN15 ER6 RS9 RG7 | .row 37/1043; .k 38/1395; .v 38/1409; .hd 18/98; .c3 15/54; .c4 2/5 | grade de critérios (CSS grid, não `<table>`) |
| `div.tw` / `div.tblw` (+ `<table>`) | 15 | 65 | ER3 RS5 RG6 DO1 | div.tw 12/57; div.tblw 3/8 | contêiner de tabela com rolagem lateral |
| `details.ref` (+ `.refbody`, `.row`) | 15 | 36 | EN9 ER5 RG1 | .refbody 14/35 | referência densa recolhida |
| `div.flow` (+ `.node`, `.arrow`) | 4 | 9 | EN1 ER3 |  | fluxo; 4 implementações diferentes |
| `div.grade` (+ `.gr`, `.gh`, `.gk`, `.gc`) | 4 | 20 | EN4 | .gr 4/118; .gh 4/20; .gk 4/98; .gc 4/211 | tabela por grid com `--cols` inline |
| `div.trilho-box` > `ol.trilho` | 7 | 7 | EN7 | ol.trilho 7/7 | trilha de passos com círculos numerados |
| `ol.passo` / `ol.passos` | 5 | 5 | EN5 |  | passos numerados |
| `ol.chain` / `ul.chain` / `ol.cadeia` | 4 | 48 | EN3 AU1 |  | cadeias causais |
| `ul.elos` / `ol.elos` | 4 | 4 | RG4 |  | elos quebrados (RD-degrau) |
| `ul.miss` (onde tropeçou) | 13 | 13 | RS13 | .n 24/109 | lista numerada dos erros do dia (RD-sec) |
| `div.qs` > `div.q` (+ `.tag`, `details`) | 16 | 16 | RS13 RG3 | div.q 16/157; .tag 14/221 | perguntas de teste agora (RD) |
| `div.qa` / `div.tgrp` | 4 | 52 | RG4 | p.qq 4/36 | pergunta/resposta e grupo de teste (RD-degrau) |
| `span.v.mal` | 12 | 48 | EN12 |  | célula-valor de `.crit .row` destacada em carmine-ink 600 (EN) |
| `div.mals` > `div.mal` | 1 | 7 | DO1 | div.mal 1/53 | linhas 'o que errou' do dossiê |
| `div.ext` (+ `.fk`, `.fv`, `.tot`) | 7 | 9 | EN6 ER1 | .fk 7/42; .fv 7/42; .tot 6/8 | faixa de fatos-chave em grid (valor grande + legenda); na dmg `.ext` é callout âmbar |

## 6. Callouts: como o CSS da própria aula os pinta

Método: dobra das regras de nível raiz (sem `@media`) de cada aula por especificidade e ordem, só nas aulas que USAM a classe no corpo. Coluna `css` = em quantas dessas aulas a regra existe. `(n/m)` = só n de m aulas declaram a propriedade; `a (n) / b (m)` = o valor varia, com o nº de aulas de cada variante (nomes quando <= 2).

**`.trap` (armadilha de prova)** -- 31 aulas, 118 elementos (EN13 ER6 RS10 RG2)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.trap` | 31/31 | background:var(--carmine-wash); border-left:3px solid var(--carmine); color:var(--ink) (10/31); font-size:15.2px (10/31); padding: 13px 16px (14) / 12px 16px (10) / 15px 18px (4) / 14px 17px (3) |
| texto | `.trap p` | 21/31 | color:var(--ink) (21/31); font-size: 15px (13) / 15.2px (4) / 15.3px (4); line-height: 1.55 (14) / 1.6 (4) / 1.58 (2) [glomerulopatias, kawasaki] / 1.56 (1) [neuromusculares] |
| rótulo | `.trap .albl` | 21/31 | display:flex (4/31); color:var(--carmine-ink) (21/31); font:700 10.5px "Source Sans 3" (4/31); letter-spacing:.1em (4/31); text-transform:uppercase (4/31) |

**`.banca` (como cai na prova)** -- 19 aulas, 51 elementos (EN15 ER4)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.banca` | 19/19 | background:var(--amber-wash); border-left:3px solid var(--amber); padding: 13px 16px (16) / 14px 17px (2) [glomerulopatias, kawasaki] / 15px 18px (1) [topicos-pediatria] |
| texto | `.banca p` | 19/19 | color:var(--ink); font-size: 15px (15) / 15.2px (3) / 15.3px (1) [topicos-pediatria] |
| rótulo | `.banca .albl` | 18/19 | color:var(--amber-ink) (18/19); font:700 10.5px "Source Sans 3" (1/19); letter-spacing:.1em (1/19); text-transform:uppercase (1/19) |

**`.aside` (nota)** -- 6 aulas, 8 elementos (ER5 RG1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.aside` | 6/6 | background: var(--teal-wash) (5) / var(--acc-wash) (1) [neuromusculares]; border-left: 3px solid var(--teal) (5) / 3px solid var(--acc) (1) [neuromusculares]; padding: 14px 17px (3) / 15px 18px (2) [dmg, topicos-pediatria] / 13px 16px (1) [neuromusculares] |
| texto | `.aside p` | 6/6 | color:var(--ink); font-size: 15.2px (4) / 15.3px (2) [dmg, topicos-pediatria] |
| rótulo | `.aside .albl` | 5/6 | color: var(--teal-ink) (4) / var(--acc-ink) (1) [neuromusculares]; font:700 10.5px "Source Sans 3" (2/6); letter-spacing:.1em (2/6); text-transform:uppercase (2/6) |

**`div.note` (RD-sec)** -- 5 aulas, 5 elementos (RS5)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.note` | 5/5 | background:var(--amber-wash); border-left:3px solid var(--amber); color:var(--ink); font-size:14.8px; padding:12px 16px |

**`.key` (RD-sec, dossiê)** -- 2 aulas, 13 elementos (RS1 DO1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.key` | 2/2 | background:var(--teal-wash); border-left:3px solid var(--teal); color:var(--ink); font-size:15.2px; padding:12px 16px |

**`.star`** -- 2 aulas, 2 elementos (ER2)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.star` | 2/2 | background:var(--card); border:1px solid var(--line2); padding:14px 18px |
| texto | `.star p` | 2/2 | color:var(--ink); font-size:15.3px; font-weight:560 |
| rótulo | `.star .albl` | 2/2 | color:var(--ink3); font:700 10.5px "Source Sans 3"; letter-spacing:.1em; text-transform:uppercase |

**`.disc` (rodapés)** -- 1 aula, 7 elementos (EN1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.disc` | 1/1 | background:var(--teal-wash); border-left:3px solid var(--teal); padding:13px 16px |
| rótulo | `.disc .albl` | 1/1 | color:var(--teal-ink) |

**`.fonte` (vulva / dossiê)** -- 1 aula, 1 elemento (EN1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.fonte` | 1/1 | background:var(--teal-wash); border-left:3px solid var(--teal); padding:13px 16px |
| rótulo | `.fonte .albl` | 1/1 | color:var(--teal-ink) |

**`.ext` quando é callout (dmg)** -- 1 aula, 1 elemento (ER1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa (só dmg) | `.ext` | 1/1 | background:var(--amber-wash); border-left:3px solid var(--amber); padding:14px 18px |

**`.ato` (faixa de ato)** -- 11 aulas, 37 elementos (EN11)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.ato` | 11/11 | background: var(--teal-wash) (10) / var(--plum-wash) (1) [vulva-vagina-anatomia]; border-left: 3px solid var(--teal) (10) / 3px solid var(--plum) (1) [vulva-vagina-anatomia]; padding:14px 16px |
| rótulo | `.ato span` | 11/11 | display:block; color: var(--teal-ink) (10) / var(--plum-ink) (1) [vulva-vagina-anatomia]; font:700 10.5px "Source Sans 3"; letter-spacing:.12em; text-transform:uppercase |
| título | `.ato h2` | 11/11 | font-size: clamp(21px,4vw,28px) (8) / clamp(22px,4vw,28px) (3) |

**`span.ff` (fora da apostila)** -- 3 aulas, 10 elementos (EN3)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| etiqueta | `.ff` | 3/3 | display:inline-block; border:1px solid var(--amber); border-radius:2px; color:var(--amber-ink); font:600 10.5px/1.5 "Source Sans 3"; padding:0 4px; vertical-align:1px |

**`span.fora` (kawasaki)** -- 1 aula, 2 elementos (ER1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| etiqueta | `.fora` | 1/1 | background:var(--amber-wash); border-radius:2px; color:var(--amber-ink); font:600 11px "IBM Plex Mono"; padding:1px 5px; white-space:nowrap |

**`span.bd` (dossiê)** -- 1 aula, 5 elementos (DO1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| etiqueta | `.bd` | 1/1 | display:inline-block; background:var(--amber-wash); border-radius:3px; color:var(--amber-ink); font:600 10.5px/1.5 "Source Sans 3"; letter-spacing:.06em; text-transform:uppercase; padding:0 6px |

Notas: (a) `.trap .albl::before` desenha uma bolinha carmine 7px em 6 aulas (as de rótulo em caixa-alta); (b) `.albl` é `<div>` em 22 aulas e `<p>` em 1 (glomerulopatias); (c) em 25 aulas algum seletor `.albl` usa `text-transform:uppercase` (com `letter-spacing` de .1em).

## 7. Diagramas, quadros e estrutura: como o CSS da própria aula os pinta

Mesmo método do §6 (CSS efetivo de nível raiz, só nas aulas que usam o componente no corpo). Variações de `@media` (colapso para 1 coluna em <= 640px etc.) ficam fora desta tabela; ver §11.

**`.vs` (comparação)** -- 35 aulas (EN12 ER5 RS10 RG7 DO1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| grade | `.vs` | 35/35 | display:grid; background:var(--line2); border:1px solid var(--line2) |
| célula | `.vs>div` | 35/35 | background:var(--card); padding: 13px 15px (16) / 12px 14px (12) / 14px 16px (7); min-width:0 (33/35) |
| título `.a` | `.vs .a h[345]\|.vs>.a h[345]` | 35/35 | color: var(--carmine-ink) (34) / var(--teal-ink) (1) [kawasaki] |
| título `.b` | `.vs .b h[345]\|.vs>.b h[345]` | 35/35 | color: var(--teal-ink) (34) / var(--carmine-ink) (1) [kawasaki] |
| título genérico | `.vs h[345]` | 35/35 | color:var(--ink3) (21/35); font: 700 11.5px "Source Sans 3" (24) / 700 12px "Source Sans 3" (9) / 700 14px "Source Sans 3" (2) [glomerulopatias, kawasaki]; letter-spacing: .04em (22) / .05em (11); text-transform:uppercase (33/35) |
| itens | `.vs li` | 35/35 | color:var(--ink2); font-size: 14.5px (22) / 14.4px (12) / 14.2px (1) [kawasaki]; line-height: 1.5 (29) / 1.55 (6) |

**`.trig` (gatilhos)** -- 21 aulas (EN15 ER6)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| grade | `.trig` | 21/21 | display:grid; background:var(--line2); border:1px solid var(--line2) |
| célula | `.trig div\|.trig>div` | 21/21 | background:var(--sunk); padding: 10px 13px (12) / 13px 15px (4) / 11px 13px (3) / 12px 14px (2) [kawasaki, neuromusculares] |
| chave `.tk` | `.trig .tk` | 21/21 | display:block; color: var(--teal-ink) (19) / var(--acc-ink) (1) [neuromusculares] / var(--plum-ink) (1) [vulva-vagina-anatomia]; font: 700 11px "IBM Plex Mono" (18) / 600 12px "IBM Plex Mono" (1) [kawasaki] / 600 13.5px/1.35 "Source Sans 3" (1) [neuromusculares] / 700 12px "IBM Plex Mono" (1) [glomerulopatias] |
| valor `.tv` | `.trig .tv` | 21/21 | color:var(--ink2); font-size: 13.8px (17) / 13.6px (3) / 14px (1) [kawasaki] |

**`.arms` / `.arm` (armadilhas)** -- 15 aulas (ER6 RS3 RG6)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| lista | `.arms` | 15/15 | display:flex; background:var(--line2); border:1px solid var(--line2) |
| item | `.arm` | 15/15 | display:flex; background:var(--card); padding: 13px 16px (8) / 15px 18px (6) / 14px 17px (1) [glomerulopatias] |
| bolinha | `.arm .dot\|.dot` | 15/15 | background:var(--carmine); border-radius:50% |
| texto | `.arm p\|.arm span:last-child` | 15/15 | color:var(--ink2); font-size:15px |

**`section.synth`** -- 21 aulas (EN15 ER6)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.synth` | 21/21 | background:var(--card); border:1px solid var(--line2); padding: 20px 16px (12) / 26px 22px (3) / 32px 30px (3) / 28px 26px (2) [kawasaki, neuromusculares] +1 |
| título | `.synth h2` | 21/21 | font-size:23px |
| legenda `.note` | `.synth .note` | 15/21 | color:var(--ink3) (15/21); font-size:14px (15/21) |

**`section.synth.arm`** -- 13 aulas (EN13)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.synth.arm` | 13/13 | border-left:3px solid var(--carmine) |
| lista | `ol.armas\|.armas` | 12/13 | margin:0 (12/13) |
| item | `ol.armas li\|.armas li` | 12/13 | color:var(--ink2) (12/13); font-size:15px (12/13); line-height:1.5 (12/13) |
| marcador | `ol.armas li::marker\|.armas li::marker` | 0/13 | - |

**`.crit` (grade de critérios)** -- 37 aulas (EN15 ER6 RS9 RG7)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| grade | `.crit` | 37/37 | background:var(--card) (28/37); border:1px solid var(--line2) |
| linha | `.crit .row` | 37/37 | display:grid; font-size: 14.2px (15) / 14.6px (10) / 14.3px (8) / 14.4px (4); padding: 10px 14px (15) / 9px 13px (15) / 11px 15px (6) / 9px 14px (1) [rd-ventilacao-degrau-0] |
| chave `.k` | `.crit .k\|.crit .row .k` | 37/37 | color: var(--teal-ink) (35) / var(--acc-ink) (1) [neuromusculares] / var(--plum-ink) (1) [vulva-vagina-anatomia]; font-weight: 600 (36) / 700 (1) [glomerulopatias] |
| valor `.v` | `.crit .v\|.crit .row .v` | 37/37 | color:var(--ink2) |
| linha de cabeçalho | `.crit .row.h\|.crit.hd .row:first-child\|.crit .hd` | 23/37 | background:var(--sunk) (23/37); color:var(--ink3) (6/37); font-size: 12px (6) / 13px (1) [kawasaki]; font-weight:600 (6/37); letter-spacing:.04em (6/37); text-transform:uppercase (6/37) |
| `.v.mal` | `.crit .mal\|.mal\|.v.mal` | 12/37 | color:var(--carmine-ink) (12/37); font-weight:600 (12/37) |

**`.tw` / `<table>`** -- 12 aulas (ER3 RS5 RG3 DO1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| contêiner | `.tw` | 12/12 | background:var(--card) (9/12); border:1px solid var(--line2) (9/12); overflow-x:auto |
| tabela | `.tw table\|table` | 9/12 | font-size: 14.4px (6) / 14px (2) [glomerulopatias, kawasaki] / 13.8px (1) [neuromusculares]; min-width: 560px (1) [glomerulopatias] / 620px (1) [kawasaki] / 640px (1) [neuromusculares]; width:100% (9/12); border-collapse:collapse (9/12) |
| `th` | `.tw th\|th\|.tw thead th\|thead th` | 9/12 | background:var(--sunk) (9/12); border-top:0 (3/12); color: var(--ink3) (7) / var(--ink) (1) [neuromusculares] / var(--ink2) (1) [glomerulopatias]; font:600 11.5px "Source Sans 3" (6/12); font-size: 13px (2) [kawasaki, neuromusculares] / 12.8px (1) [glomerulopatias]; font-weight: 600 (2) [kawasaki, neuromusculares] / 700 (1) [glomerulopatias]; letter-spacing:.05em (6/12); text-transform:uppercase (6/12); padding: 9px 12px (6) / 9px 11px (3) |
| `td` | `.tw td\|td` | 9/12 | border-top:1px solid var(--line) (9/12); color:var(--ink2) (9/12); padding: 9px 12px (6) / 9px 11px (3) |
| `td.hi` | `td.hi\|.tw .hi` | 6/12 | background:var(--acc-wash) (1/12); color:var(--teal-ink) (5/12); font-weight:600 (5/12) |

**`.tblw` (RD-degrau)** -- 3 aulas (RG3)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| contêiner | `.tblw` | 3/3 | border:1px solid var(--line2); overflow-x:auto |
| tabela | `table.t` | 3/3 | font-size:14.2px; min-width:520px |
| `th` | `table.t th` | 3/3 | background:var(--sunk); border-top:0; color:var(--ink3); font:600 12px "Source Sans 3"; letter-spacing:.04em; text-transform:uppercase; padding:10px 12px |

**`details.ref`** -- 15 aulas (EN9 ER5 RG1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `details.ref` | 15/15 | background:var(--card); border:1px solid var(--line2) |
| summary | `details.ref>summary` | 15/15 | display:flex; color: var(--teal-ink) (13) / var(--acc-ink) (1) [neuromusculares] / var(--plum-ink) (1) [vulva-vagina-anatomia]; font: 600 13.5px "Source Sans 3" (12) / 600 14px "Source Sans 3" (3); padding: 12px 16px (8) / 11px 14px (5) / 11px 15px (2) [kawasaki, neuromusculares] |
| corpo | `details.ref .refbody` | 14/15 | padding: 0 14px 12px (4) / 0 16px 16px (4) / 0 14px 14px (2) [mccp-decisao-compartilhada, rastreamento-programas-br] / 0 15px 14px (2) [kawasaki, neuromusculares] +1 |
| linha | `details.ref .row` | 5/15 | display:grid (5/15); border-top:1px solid var(--line) (5/15); font-size: 13.8px (4) / 14px (1) [kawasaki]; padding:8px 0 (5/15) |
| `.k` | `details.ref .k` | 5/15 | color:var(--ink) (5/15); font-weight:600 (5/15) |
| `.v` | `details.ref .v` | 5/15 | color:var(--ink2) (5/15) |

**`.stats` / `.stat`** -- 21 aulas (EN15 ER3 RG3)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| faixa | `.stats` | 21/21 | display:flex; gap: 18px (12) / 22px (6) / 20px (3) |
| número `b` | `.stat b` | 21/21 | color: var(--teal-ink) (20) / var(--plum-ink) (1) [vulva-vagina-anatomia]; font: 600 21px/1 "IBM Plex Mono" (12) / 600 24px/1 "IBM Plex Mono" (6) / 600 22px/1 "IBM Plex Mono" (3) |
| legenda `span` | `.stat span` | 21/21 | color:var(--ink3); font-size:11.5px; letter-spacing:.02em (6/21) |

**`.nav` (chips)** -- 16 aulas (EN15 RG1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| contêiner | `.nav` | 16/16 | display:flex; padding: 20px 0 4px (15) / 18px 0 0 (1) [rd-ventilacao-degrau-0]; gap:6px |
| link | `.nav a` | 16/16 | border:1px solid var(--line2); border-radius:2px; color:var(--ink2); font-size:13px; padding:4px 9px |

**`.rail` (trilho lateral)** -- 6 aulas (ER6)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| contêiner | `.rail` | 6/6 | display:flex; position:sticky; gap:1px |
| rótulo `.rlab` | `.rail .rlab` | 6/6 | color:var(--ink3); font: 600 10.5px/1 "Source Sans 3" (3) / 600 12.5px/1 "Source Sans 3" (1) [neuromusculares] / 600 12px/1 "Source Sans 3" (1) [glomerulopatias] / 600 13px/1 "Source Sans 3" (1) [kawasaki]; letter-spacing:.1em (3/6); text-transform:uppercase (3/6) |
| link | `.rail a` | 6/6 | display:grid; border-left:2px solid transparent; color:var(--ink3); font-size: 13.3px (5) / 13.5px (1) [kawasaki]; padding: 7px 0 (3) / 7px 0 7px 10px (2) [glomerulopatias, kawasaki] / 6px 0 6px 10px (1) [neuromusculares]; grid-template-columns: 20px 1fr (5) / 22px minmax(0,1fr) (1) [neuromusculares] |
| link ativo | `.rail a.on` | 6/6 | color: var(--teal-ink) (5) / var(--acc-ink) (1) [neuromusculares]; font-weight:600 |
| `.rn` | `.rail a .rn` | 6/6 | color:var(--ink3); font:600 11px "IBM Plex Mono" |

**`.degrau`** -- 28 aulas (EN15 ER6 RG7)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| seção | `.degrau` | 28/28 | border-bottom:1px solid var(--line); padding: 30px 0 (12) / 44px 0 (6) / 34px 0 (4) / 36px 0 (3) +2 |
| cabeça | `.dhead` | 28/28 | display:flex; gap: 13px (12) / 16px (8) / 14px (7) / 15px (1) [neuromusculares]; align-items:flex-start |
| número `.dnum` | `.dnum` | 28/28 | display:flex; border: 1.5px solid var(--teal) (26) / 1.5px solid var(--acc) (1) [neuromusculares] / 1.5px solid var(--plum) (1) [vulva-vagina-anatomia]; border-radius:50%; color: var(--teal-ink) (26) / var(--acc-ink) (1) [neuromusculares] / var(--plum-ink) (1) [vulva-vagina-anatomia]; font: 600 14px "IBM Plex Mono" (12) / 600 15px "IBM Plex Mono" (7) / 600 17px "IBM Plex Mono" (7) / 600 16px "IBM Plex Mono" (2) [kawasaki, neuromusculares]; width: 38px (12) / 40px (7) / 44px (7) / 42px (2) [kawasaki, neuromusculares]; height: 38px (12) / 40px (7) / 44px (7) / 42px (2) [kawasaki, neuromusculares] |
| etapa `.dstage` | `.dtitle .dstage\|.dstage` | 13/28 | color:var(--ink3) (13/28); font: 600 11px "Source Sans 3" (10) / 600 12.5px "Source Sans 3" (2) [glomerulopatias, neuromusculares] / 600 13px "Source Sans 3" (1) [kawasaki]; letter-spacing:.1em (10/28); text-transform:uppercase (10/28) |
| título | `.dtitle h2\|.dtitle h3\|.degrau h2` | 28/28 | font-size: clamp(19px,3.4vw,24px) (15) / clamp(21px,2.6vw,27px) (9) / clamp(20px,2.6vw,25px) (4) |

**`.sec` / `.kick` (RD-sec, dossiê)** -- 14 aulas (RS13 DO1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| seção | `.sec` | 14/14 | border-bottom:1px solid var(--line); padding:34px 0 |
| `.kick` | `.kick` | 14/14 | display:block; color:var(--ink3); font:600 11px "Source Sans 3"; letter-spacing:.1em; text-transform:uppercase |
| título | `.sec h2` | 14/14 | font-size:clamp(21px,3.2vw,26px) |

**`.lede` / `.prose` / `.pt`** -- 41 aulas (EN15 ER6 RS12 RG7 DO1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| `.lede` | `.lede` | 41/41 | color:var(--ink2); font-size: 16px (15) / 16.3px (13) / 16.5px (13); font-style:italic; line-height: 1.6 (21) / 1.55 (19) / 1.58 (1) [neuromusculares]; margin: 0 0 14px (28) / 0 0 20px (6) / 0 0 16px (5) / 0 0 18px (2) [glomerulopatias, kawasaki] |
| `.prose li` | `.prose li\|.prose ul li` | 28/41 | color:var(--ink2) (28/41); font-size: 15.4px (15) / 15.6px (13); line-height: 1.55 (19) / 1.6 (8) / 1.58 (1) [neuromusculares] |
| `ul.pt li` | `ul.pt li\|.pt li` | 13/41 | color:var(--ink2) (13/41); font-size:15.6px (13/41); line-height:1.58 (13/41) |
| sub-título `h4.sub` | `h4.sub\|.prose h4` | 7/41 | color:var(--ink) (7/41); font-size: 14px (6) / 14.5px (1) [kawasaki]; font-weight:600 (7/41); letter-spacing:.01em (6/41); margin: 26px 0 10px (6) / 24px 0 10px (1) [kawasaki] |
| sub-título `h3.sub` | `h3.sub` | 2/41 | color:var(--ink) (2/41); font:600 15px/1.3 "Source Sans 3" (1/41); font-size:15px (1/41); font-weight:700 (1/41); margin: 24px 0 9px (1) [neuromusculares] / 28px 0 10px (1) [glomerulopatias] |

**`.eye` / `.top h1` / `.top .sub`** -- 42 aulas (EN15 ER6 RS13 RG7 DO1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| `.top` | `.top` | 42/42 | border-bottom:1px solid var(--line2); padding: 44px 0 26px (17) / 36px 0 22px (12) / 52px 0 30px (6) / 46px 0 26px (3) +2 |
| `.eye` | `.eye` | 42/42 | color: var(--teal-ink) (40) / var(--acc-ink) (1) [neuromusculares] / var(--plum-ink) (1) [vulva-vagina-anatomia]; font: 600 11px/1.3 "Source Sans 3" (33) / 600 11px/1 "Source Sans 3" (6) / 600 13px/1.3 "Source Sans 3" (3); letter-spacing: .14em (24) / .12em (15); text-transform:uppercase (39/42); margin: 0 0 14px (21) / 0 0 13px (14) / 0 0 15px (6) / 0 0 12px (1) [kawasaki] |
| `.top h1` | `.top h1` | 42/42 | font-size: clamp(28px,5vw,42px) (14) / clamp(28px,6vw,44px) (12) / clamp(32px,5vw,50px) (8) / clamp(28px,5vw,44px) (3) +3; font-weight:680; max-width: 18ch (6) / 20ch (5) / 16ch (1) [dmg] |
| `.top .sub` | `.top .sub\|.sub` | 42/42 | color:var(--ink2); font-size: clamp(16px,2.2vw,17.5px) (14) / 16.5px (12) / 18px (6) / clamp(16px,2.2vw,18px) (4) +2; line-height: 1.6 (23) / 1.55 (19); max-width: 66ch (6) / 64ch (3) |

**`.grade` (tabela por grid)** -- 4 aulas (EN4)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| tabela | `.grade` | 4/4 | background:var(--card); border:1px solid var(--line2) |
| linha | `.grade .gr` | 4/4 | display:grid; padding:10px 13px |
| chave `.gk` | `.grade .gk` | 4/4 | color:var(--teal-ink); font-size:14.8px; font-weight:600 |
| célula `.gc` | `.grade .gc` | 4/4 | color:var(--ink2); font-size:14px |
| linha quente | `.grade .gr.hot .gk` | 4/4 | color:var(--carmine-ink) |

**`.ext` (fatos-chave)** -- 7 aulas (EN6 ER1)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| grade | `.ext` | 7/7 | display:grid (6/7); background: var(--line2) (6) / var(--amber-wash) (1) [dmg]; border:1px solid var(--line2) (6/7); border-left:3px solid var(--amber) (1/7); padding:14px 18px (1/7) |
| célula | `.ext>div` | 6/7 | background:var(--card) (6/7); padding:13px 14px (6/7) |
| valor `.fv` | `.ext .fv` | 6/7 | color:var(--teal-ink) (6/7); font:600 17px/1.25 Fraunces,Georgia,serif (6/7) |
| legenda `.fk` | `.ext .fk` | 6/7 | color:var(--ink2) (6/7); font-size:14px (6/7) |
| total | `.ext .tot .fv` | 6/7 | color:var(--carmine-ink) (6/7) |

**`.trilho` (trilha de passos)** -- 7 aulas (EN7)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| caixa | `.trilho-box` | 7/7 | background:var(--card); border:1px solid var(--line2); padding:16px 14px 10px |
| círculo `.n` | `.trilho .n` | 7/7 | display:flex; background:var(--card); border:1.5px solid var(--teal); border-radius:50%; color:var(--teal-ink); font: 600 12px "IBM Plex Mono" (5) / 600 10px "IBM Plex Mono" (1) [imagem-obstetrica] / 600 13px "IBM Plex Mono" (1) [tireoide-nodulo-cancer]; width:30px; height:30px |
| título `b` | `.trilho b` | 7/7 | color:var(--ink); font-size:15px; font-weight:600 |
| legenda `small` | `.trilho small` | 7/7 | color:var(--ink3); font-size:13px |

**`ol.passo`** -- 3 aulas (EN3)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| lista | `ol.passo` | 3/3 | background:var(--card); border:1px solid var(--line2); padding:0 |
| item | `ol.passo li` | 3/3 | display:grid; color:var(--ink2); font-size:14.4px; padding:10px 13px |

**`.elos`** -- 4 aulas (RG4)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| lista | `.elos` | 4/4 | background:var(--card) (1/4); border:1px solid var(--line2); padding:0 |
| item | `.elos li` | 4/4 | display:grid; color:var(--ink2); font-size: 15.3px (3) / 15.2px (1) [rd-ventilacao-degrau-0]; padding:11px 14px |
| número `.n` | `.elos .n` | 4/4 | color: var(--carmine-ink) (3) / var(--teal-ink) (1) [rd-ventilacao-degrau-0]; font:600 12px "IBM Plex Mono" |

**`.flow` (4 implementações)** -- 4 aulas (EN1 ER3)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| contêiner | `.flow` | 4/4 | display: flex (3) / grid (1) [dmg]; background:var(--line2) (1/4); border:1px solid var(--line2) (1/4) |
| nó | `.flow .node\|.flow>div` | 2/4 | background:var(--card) (2/4); border:1px solid var(--line2) (1/4); color:var(--ink2) (1/4); font-size:14.4px (1/4); padding: 11px 14px (1) [kawasaki] / 13px 14px (1) [dmg] |
| seta | `.flow .arrow` | 1/4 | background:var(--teal) (1/4); width:2px (1/4); height:18px (1/4) |

**quadros de 1 aula: `.cream`, `.ruler`, `.cmap`, `.if3`, `.spec`** -- 2 aulas (ER2)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| `.cream` (kawasaki) | `.cream` | 1/2 | display:grid (1/2); background:var(--line2) (1/2); border:1px solid var(--line2) (1/2) |
| `.cream>div` | `.cream>div` | 1/2 | background:var(--card) (1/2); padding:13px 15px (1/2) |
| `.ruler` (kawasaki) | `.ruler` | 1/2 | background:var(--card) (1/2); border:1px solid var(--line2) (1/2) |
| `.cmap` (glomerulopatias) | `.cmap` | 1/2 | display:grid (1/2); background:var(--line2) (1/2); border:1px solid var(--line2) (1/2) |
| `.if3` (glomerulopatias) | `.if3` | 1/2 | display:grid (1/2); background:var(--line2) (1/2); border:1px solid var(--line2) (1/2) |
| `.spec` (glomerulopatias) | `.spec` | 1/2 | display:grid (1/2); background:var(--line2) (1/2); border:1px solid var(--line2) (1/2) |

**RD: `.miss` / `.q` / `.qs` / `.blk`** -- 13 aulas (RS13)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| `.miss` | `.miss` | 13/13 | background:var(--card); border:1px solid var(--line2); padding:0 |
| `.miss li` | `.miss li` | 13/13 | color:var(--ink2); font-size:15.3px; padding:11px 14px |
| `.miss .n` | `.miss .n` | 13/13 | color:var(--carmine-ink); font:600 12px "IBM Plex Mono" |

**RD: `.q` (teste agora)** -- 16 aulas (RS13 RG3)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| `.q` | `.q` | 16/16 | background:var(--card); border:1px solid var(--line2) (13/16); padding: 13px 15px (13) / 14px 16px (3) |
| `.q .tag` | `.q .tag` | 13/16 | display:block (13/16); color:var(--teal-ink) (13/16); font:600 10.5px "IBM Plex Mono" (13/16); letter-spacing:.04em (13/16) |
| `.q p` | `.q p` | 16/16 | color:var(--ink); font-size: 15.4px (13) / 15.3px (3); font-weight:500 (13/16) |

**RD: `.qs`** -- 16 aulas (RS13 RG3)

| parte | seletor | css | pintura efetiva (aula) |
|---|---|---|---|
| `.qs` | `.qs` | 16/16 | display:flex; background:var(--line2) (3/16); border:1px solid var(--line2) (3/16); gap: 10px (13) / 1px (3) |

### 7.1 Raios de borda declarados pelas aulas (`border-radius`)

Caixas, callouts e grades das aulas (`.trap .banca .aside .vs .crit .tw .trig .arms .synth details.ref`) não declaram raio (cantos retos). Raios aparecem só em elementos pequenos (círculos 50%, `code`/`.nav a` 2px) e nos formulários e cartões da autópsia (6px). Lista completa por seletor (31 seletores):

| seletor | aulas | valores (aulas) |
|---|---|---|
| `.dnum` | 28 | 50% (28) |
| `code` | 25 | 2px (25) |
| `.nav a` | 16 | 2px (16) |
| `.arm .dot` | 15 | 50% (15) |
| `.synth.arm h2::before` | 13 | 50% (13) |
| `.src code` | 10 | 2px (10) |
| `.trilho .n` | 7 | 50% (7) |
| `.rail a` | 6 | 2px (5), 3px (1) |
| `.trap .albl::before` | 6 | 50% (6) |
| `.ff` | 4 | 2px (4) |
| `ol.passo li::before` | 4 | 50% (4) |
| `details.pend-opc` | 2 | 6px (2) |
| `form.pend` | 2 | 6px (2) |
| `form.pend [data-pend-retorno]` | 2 | 4px (2) |
| `form.pend button` | 2 | 6px (2) |
| `form.pend textarea` | 2 | 6px (2) |
| `.alts li` | 1 | 4px (1) |
| `.bd` | 1 | 3px (1) |
| `.busca` | 1 | 6px (1) |
| `.c` | 1 | 3px (1) |
| `.card` | 1 | 6px (1) |
| `.chip` | 1 | 999px (1) |
| `.f.perg` | 1 | 6px (1) |
| `.fora` | 1 | 2px (1) |
| `.fx` | 1 | 3px (1) |
| `.nota-box` | 1 | 6px (1) |
| `.pill` | 1 | 999px (1) |
| `.tile` | 1 | 6px (1) |
| `details.q` | 1 | 6px (1) |
| `details.sub` | 1 | 6px (1) |
| `mark` | 1 | 2px (1) |

## 8. Tokens (variáveis CSS)

43 das 43 aulas declaram os tokens do mesmo jeito: `:root{...}` (claro) + `@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){...}}` + `:root[data-theme="dark"]{...}`. O `tema.css` injetado depois redefine os mesmos nomes com seletores (0,2,0) e vence por ordem. Os nomes em inglês são apelidos no `tema.css` v3 em curso (`--teal` = `--acento` etc.).

### 8.1 Nomes padrão (21) e o que o tema v3 faz com eles

| token | aulas que definem | aulas que usam | usos (CSS+inline) | papel na aula | tema v3 escuro (alias -> valor) | tema v3 claro |
|---|---|---|---|---|---|---|
| `--paper` | 42 | 42 | 49 | fundo da página | var(--papel) -> #17132E | #F7F5FB |
| `--card` | 42 | 42 | 247 | superfície (caixas, células) | #211C3A | #FFFFFF |
| `--sunk` | 42 | 39 | 111 | superfície afundada (cabeçalho de tabela, chips) | var(--afundado) -> #29233F | #EFEBF7 |
| `--ink` | 43 | 43 | 356 | texto principal | var(--tinta) -> #F8F5F2 | #1C1733 |
| `--ink2` | 42 | 42 | 407 | texto secundário | var(--tinta2) -> #B8B3CC | #4B4466 |
| `--ink3` | 42 | 42 | 278 | metadado / rótulo | var(--tinta3) -> #9C96B6 | #625B7E |
| `--line` | 42 | 42 | 150 | filete suave | var(--linha) -> #403858 | #DCD5E8 |
| `--line2` | 42 | 42 | 500 | filete forte / gap de grade | var(--linha-forte) -> #776E99 | #8E87AD |
| `--teal` | 41 | 41 | 177 | acento (aside, dnum, rail ativo, link) | var(--acento) -> #00D9E8 | #00737D |
| `--teal-ink` | 41 | 41 | 377 | texto sobre/junto do acento (rótulos, chaves, números) | var(--acento-tinta) -> #7DE8F0 | #005A62 |
| `--teal-wash` | 41 | 41 | 54 | lavagem do acento (aside, ato) | var(--acento-fraco) -> #13334C | #DDF1F4 |
| `--carmine` | 42 | 41 | 100 | alerta (trap, bolinha das armadilhas) | var(--erro) -> #FF7C87 | #B8303E |
| `--carmine-ink` | 42 | 42 | 148 | texto de alerta | #FFB3BA | #962632 |
| `--carmine-wash` | 42 | 36 | 41 | lavagem de alerta (trap) | var(--erro-fraco) -> #3C243C | #FBE5E8 |
| `--amber` | 42 | 35 | 45 | aviso (banca, note) | var(--aviso) -> #FFBE72 | #8F5200 |
| `--amber-ink` | 42 | 26 | 37 | texto de aviso | #FFD3A0 | #7A4500 |
| `--amber-wash` | 42 | 35 | 37 | lavagem de aviso (banca) | var(--aviso-fraco) -> #3C2E39 | #FAEBD7 |
| `--plum` | 2 | 2 | 5 | variante roxa (só vulva-vagina e glomerulopatias) | var(--roxo) -> #AA71E8 | #7443B8 |
| `--plum-ink` | 2 | 2 | 10 | texto roxo | var(--roxo-tinta) -> #BE95F0 | #5E3596 |
| `--plum-wash` | 2 | 1 | 1 | lavagem roxa | var(--roxo-fraco) -> #2F224C | #ECE3F8 |
| `--on` | 27 | 1 | 2 | texto sobre preenchimento | var(--sobre) -> #17132E | #FFFFFF |

### 8.2 Aulas que fogem do padrão

| aula | fam. | define fora do padrão de 21 | usa mas o tema NÃO define (não é recolorido) |
|---|---|---|---|
| anemias-macrociticas | EN | --cols | --cols |
| autopsia-uerj-2021 | AU | --accent, --accent-ink, --accent-soft, --bg, --body, --display, --ink-2, --marcada, --marcada-soft, --mark, --mono, --muted, --rule, --rule-2, --surface, --surface-2, --warn, --warn-soft | --accent, --accent-ink, --accent-soft, --bg, --body, --display, --ink-2, --marcada, --marcada-soft, --mark, --mono, --muted, --rule, --rule-2, --surface, --surface-2, --warn, --warn-soft |
| dmg | ER | --sh | - |
| iamcsst | EN | --cols | --cols |
| insuficiencia-adrenal | EN | --cols | --cols |
| neuromusculares | ER | --acc, --acc-ink, --acc-wash, --i | --acc, --acc-ink, --acc-wash, --i |
| oncohemato-cronicas | EN | --cols | --cols |
| prevencao-quaternaria | ER | --sh | - |
| rd-hemostasia | RG | --sh | - |
| rd-lupus-saf | RG | --sh | - |
| rd-vias-biliares | RG | --sh | - |
| topicos-pediatria | ER | --sh | - |

- `--plum*` só é definido (e usado) por 2 aulas: glomerulopatias, vulva-vagina-anatomia; nas outras 41 o nome não existe e o tema v3 o define como `--roxo*`.
- Aulas com pelo menos um token que o tema não conhece: 6 (anemias-macrociticas, autopsia-uerj-2021, iamcsst, insuficiencia-adrenal, neuromusculares, oncohemato-cronicas).
- `--on` não é definido por 16 aulas e só é USADO em 1 (rd-ventilacao-degrau-0).
- Tipografia declarada pelas aulas (nº de aulas): Source Sans 3 (43), IBM Plex Mono (43), Fraunces (42), Barlow Semi Condensed (1). A camada as anula com `*{font-family:var(--fonte)!important}`; o hub remove os `<link>` do Google Fonts de cada aula e injeta o da Atkinson.

### 8.3 Mapeamento necessário para recolorir os dois outliers (a camada pode declarar os apelidos, não precisa editar a aula)

| aula | nome da aula | usos | alvo no tema v3 | valor escuro | papel |
|---|---|---|---|---|---|
| autópsia | `--bg` | 4 | `--papel` | #17132E | fundo da página |
| autópsia | `--surface` | 7 | `--card` | #211C3A | caixas |
| autópsia | `--surface-2` | 3 | `--afundado` | #29233F | caixas internas |
| autópsia | `--ink` | 6 | `--tinta` | #F8F5F2 | (já usa o nome padrão) |
| autópsia | `--ink-2` | 8 | `--tinta2` | #B8B3CC | texto secundário |
| autópsia | `--muted` | 17 | `--tinta3` | #9C96B6 | metadado |
| autópsia | `--rule` | 12 | `--linha` | #403858 | filete |
| autópsia | `--rule-2` | 5 | `--linha-forte` | #776E99 | filete forte / borda de controle |
| autópsia | `--accent` | 6 | `--acento` | #00D9E8 | acento (links, seleção) |
| autópsia | `--accent-ink` | 4 | `--acento-tinta` | #7DE8F0 | texto de acento |
| autópsia | `--accent-soft` | 3 | `--acento-fraco` | #13334C | lavagem do acento (alt. certa) |
| autópsia | `--marcada` | 6 | `--erro` | #FF7C87 | errou |
| autópsia | `--marcada-soft` | 1 | `--erro-fraco` | #3C243C | lavagem de erro (alt. marcada) |
| autópsia | `--warn` | 3 | `--aviso` | #FFBE72 | dúvida / chute certo |
| autópsia | `--warn-soft` | 2 | `--aviso-fraco` | #3C2E39 | lavagem de aviso |
| autópsia | `--mark` | 1 | `--amarelo` | #FFD447 | marca-texto `mark`: a aula usa rgba translúcido (alfa .34-.38); `--amarelo`/`--qz-grifo` são sólidos, usar com alfa |
| autópsia | `--display` | 3 | `--fonte` | var(--fonte) (Atkinson) | família de títulos |
| autópsia | `--body` | 2 | `--fonte` | var(--fonte) (Atkinson) | família do corpo |
| autópsia | `--mono` | 7 | `--fonte` | var(--fonte) (Atkinson) | mono (o tema anula) |
| neuromusculares | `--acc` | 6 | `--acento` | #00D9E8 | acento da aula (indigo #3B4F9A claro / #9DB0F0 escuro) |
| neuromusculares | `--acc-ink` | 11 | `--acento-tinta` | #7DE8F0 | texto de acento |
| neuromusculares | `--acc-wash` | 3 | `--acento-fraco` | #13334C | lavagem do acento |

- Variáveis inline: `--cols` (grid de 20 `div.grade`: anemias, iamcsst, insuficiencia-adrenal, oncohemato) e `--i` (6 `li` da neuromusculares); `--sh` é definida por 6 aulas e nunca usada. Nenhuma das três é do tema.

## 9. Estilos inline com cor, fundo ou borda no corpo

Aulas com algum `style="..."` ou atributo de cor SVG (as demais 0 em tudo): 10 de 43.
Total de atributos `style`: 38, dos quais com cor/fundo/borda: 3 (em 3 aulas). Cores literais (hex/rgb/hsl/nome) nos `style=`: 0. Cores literais no CSS das aulas fora dos blocos `:root`: 0.

| aula | fam. | atributos style | com cor/fundo/borda | atributos SVG fill/stroke com valor |
|---|---|---|---|---|
| anemias-macrociticas | EN | 3 | 0 | 0 |
| dmg | ER | 3 | 1 | 0 |
| glomerulopatias | ER | 1 | 0 | 5 |
| iamcsst | EN | 8 | 0 | 0 |
| insuficiencia-adrenal | EN | 3 | 0 | 0 |
| neuromusculares | ER | 6 | 0 | 0 |
| oncohemato-cronicas | EN | 6 | 0 | 0 |
| prevencao-quaternaria | ER | 3 | 1 | 0 |
| rd-ventilacao-degrau-0 | RG | 1 | 0 | 0 |
| topicos-pediatria | ER | 4 | 1 | 0 |

Exemplos (todos os que existem; só 3 são `style=` de cor, os outros 2 são atributos de apresentação SVG):

| aula | elemento | atributo |
|---|---|---|
| dmg | p | `style="font-size:14px;color:var(--ink3);margin:0 0 4px;max-width:72ch"` |
| prevencao-quaternaria | p | `style="font-size:14px;color:var(--ink3);margin:0 0 4px;max-width:72ch"` |
| topicos-pediatria | p | `style="font-size:14px;color:var(--ink3);margin:0 0 4px;max-width:72ch"` |
| glomerulopatias | circle | `stroke="var(--line2)"` |
| glomerulopatias | path | `stroke="var(--plum)"` |

Todas as propriedades inline, por contagem: `--var` 26, `font-size` 6, `margin` 5, `margin-top` 4, `margin-bottom` 3, `color` 3, `max-width` 3.

## 10. Cabeçalho típico (do `.top` até o primeiro bloco de conteúdo)

**anemias-macrociticas** -- família EN (15 aulas): chips `nav.nav` + faixa `.stats`

```
header.top
  p.eye  "MedHub / Aula-base / Clínica Médica / Hematologia / ..."
  h1  "Anemias macrocíticas: quando o núcleo não acompanha"
  p.sub  "Hemácia grande nasce de um núcleo que atrasa. A mega..."
  div.stats
    div.stat
      b  "78%"
      span  "das questões: megaloblástica"
    (... e mais 4 iguais a div.stat)
nav.nav
  a  "Régua"
  (... e mais 13 iguais a a)
```

**kawasaki** -- família ER (6 aulas): régua/`spec` no cabeçalho + `div.body` com `nav.rail`

```
header.top
  p.eye  "Aula-base de Pediatria, antes da lista #651 (30 ques..."
  h1  "Doença de Kawasaki: a corrida do décimo dia"
  p.sub  "Uma vasculite que se diagnostica pela clínica e se t..."
  div.ruler
    div.bar
      span  "D1"
      span  "D5"
      span.hot  "D10"
      span  "sem 2-3 em diante"
    div.cols
      div
        b  "Febre começa"
        p  "Dia 1 de febre = dia 1 da doença. Exantema perineal ..."
      (... e mais 3 iguais a div)
    div.foot  "Tudo o que vem depois nesta aula se pendura nesta ré..."
div.body
  nav#rail.rail
    p.rlab  "A escada"
    a
      span.rn  "0"
      span  "O que é"
    (... e mais 10 iguais a a)
  main
```

**rd-hernias** -- família RS (13 aulas): só eye + h1 + sub

```
header.top
  p.eye  "Revisão direcionada / Hérnias da parede abdominal / ..."
  h1  "Quando a hérnia dói, a pergunta é uma só: há sinal d..."
  p.sub  "10 de 21. Dos 11 erros, 3 foram na mesma decisão (en..."
```

### 10.1 Caixas, bordas e pílulas no cabeçalho, medido no Edge (tema v3 + camada) a 390 px

`altura` = distância do topo do `.top` até o 1º degrau/seção/ato (o que a pessoa rola antes de ler a 1ª frase de conteúdo). `caixas` = elementos da zona com borda visível ou fundo; `pílulas` = caixas com raio >= 12px e altura <= 48px.

| aula | fam. | altura px | caixas | pílulas | caixas mais comuns |
|---|---|---|---|---|---|
| anemias-macrociticas | EN | 646 | 14 | 0 | a x14 |
| aorta-cardiomiopatias-pericardio | EN | 620 | 10 | 0 | a x10 |
| autopsia-uerj-2021 | AU | 382 | 5 | 0 | div.tile x4, header x1 |
| cronicas-aps-metas | EN | 936 | 16 | 5 | a x10, span.n x5, div.trilho-box x1 |
| dmg | ER | 680 | 13 | 13 | a x13 |
| dossie-uerj | DO | 410 | 0 | 0 |  |
| glomerulopatias | ER | 886 | 13 | 7 | a x7, div.spec x1, div.s-aua x1 |
| iamcsst | EN | 620 | 16 | 0 | a x16 |
| idoso-amg-polifarmacia | EN | 982 | 24 | 4 | a x19, span.n x4, div.trilho-box x1 |
| imagem-obstetrica | EN | 955 | 19 | 3 | a x15, span.n x3, div.trilho-box x1 |
| insuficiencia-adrenal | EN | 643 | 13 | 0 | a x13 |
| kawasaki | ER | 1100 | 16 | 11 | a x11, div x3, div.ruler x1 |
| mccp-decisao-compartilhada | EN | 908 | 15 | 3 | a x11, span.n x3, div.trilho-box x1 |
| neuromusculares | ER | 1033 | 20 | 14 | a x14, li x5, ol.axis x1 |
| oncohemato-cronicas | EN | 682 | 14 | 0 | a x14 |
| prevencao-quaternaria | ER | 756 | 9 | 9 | a x9 |
| rastreamento-programas-br | EN | 881 | 16 | 3 | a x12, span.n x3, div.trilho-box x1 |
| rd-cir-0610 | RS | 281 | 0 | 0 |  |
| rd-cm-0610 | RS | 335 | 0 | 0 |  |
| rd-dii-polipos | RG | 269 | 0 | 0 |  |
| rd-dm-cronicas | RS | 326 | 0 | 0 |  |
| rd-go-0610 | RS | 281 | 0 | 0 |  |
| rd-hemostasia-2 | RS | 263 | 0 | 0 |  |
| rd-hemostasia | RG | 357 | 0 | 0 |  |
| rd-hepato | RG | 269 | 0 | 0 |  |
| rd-hernias | RS | 362 | 0 | 0 |  |
| rd-intensiva-sepse | RG | 269 | 0 | 0 |  |
| rd-lupus-saf | RG | 330 | 0 | 0 |  |
| rd-meningites | RS | 281 | 0 | 0 |  |
| rd-neoplasias-tgi | RS | 299 | 0 | 0 |  |
| rd-ortopedia-cirurgia | RS | 317 | 0 | 0 |  |
| rd-ped-0610 | RS | 290 | 0 | 0 |  |
| rd-pediatria | RS | 290 | 0 | 0 |  |
| rd-pilulas-0510 | RS | 281 | 0 | 0 |  |
| rd-pilulas | RS | 254 | 0 | 0 |  |
| rd-ventilacao-degrau-0 | RG | 392 | 7 | 0 | a x7 |
| rd-vias-biliares | RG | 280 | 0 | 0 |  |
| remit-cicatrizacao | EN | 540 | 10 | 0 | a x10 |
| rodapes-retorno-alto | EN | 606 | 9 | 0 | a x9 |
| tb-360 | EN | 895 | 21 | 4 | a x16, span.n x4, div.trilho-box x1 |
| tireoide-nodulo-cancer | EN | 612 | 11 | 0 | a x11 |
| topicos-pediatria | ER | 759 | 13 | 13 | a x13 |
| vulva-vagina-anatomia | EN | 550 | 13 | 0 | a x13 |

| fam. | aulas | altura min-max px | altura média px | caixas min-max | pílulas min-max |
|---|---|---|---|---|---|
| EN | 15 | 540-982 | 738 | 9-24 | 0-5 |
| ER | 6 | 680-1100 | 869 | 9-20 | 7-14 |
| RS | 13 | 254-362 | 296 | 0-0 | 0-0 |
| RG | 7 | 269-392 | 309 | 0-7 | 0-0 |
| DO | 1 | 410-410 | 410 | 0-0 | 0-0 |
| AU | 1 | 382-382 | 382 | 5-5 | 0-0 |

Onde ficam os chips/pílulas hoje:

- `nav.nav a` (16 aulas: EN15 RG1): chips com borda 1px `--line2`, raio 2px, 13px, em fileira com quebra. A camada NÃO os toca (nenhum seletor `.nav`).
- `nav.rail a` (6 aulas, ER6): link de texto com filete esquerdo no desktop; a camada o transforma em pílula (`border-radius:999px; background:--sunk`) abaixo de 920px. Como o iframe do leitor tem <= 704 px, a fileira de pílulas é SEMPRE a que aparece no hub (medido: `.body` com 1 coluna e `.rail` `position:static`).
- `.stats .stat` (21 aulas): número em mono (Plex Mono, tamanhos do §7) + legenda pequena; sem caixa.
- Etiquetas em linha: `span.ff` (borda âmbar 1px), `span.fora` (wash âmbar mono), `span.bd`, `span.c` (chips numéricos da glomerulopatias), `.chain .c` (caixas da idoso).

## 11. Riscos para celular (390 px)

### 11.1 Estático (CSS das aulas)

| propriedade | seletor | aulas | fam. |
|---|---|---|---|
| `white-space:nowrap` | `td.nw` | dossie-uerj | DO1 |
| `white-space:nowrap` | `td.num` | dossie-uerj | DO1 |
| `white-space:nowrap` | `.ar` | dossie-uerj | DO1 |
| `white-space:nowrap` | `.fora` | kawasaki | ER1 |
| `position:sticky` | `.rail`  | dmg, glomerulopatias, kawasaki, neuromusculares, prevencao-quaternaria, topicos-pediatria | ER6 |

Elementos afetados no corpo: dossiê `td.nw`/`td.num` = 186 células e `.ar` = 62; kawasaki `.fora` = 2. `.rail{position:sticky}` (6 aulas) volta a `static` em <= 920px (e em `(hover:none)` na dmg); dentro do iframe do hub (largura <= 704 px, altura = conteúdo) o sticky não tem efeito nem no desktop.

Larguras fixas >= 300px no CSS das aulas (todas são `min-width` de `<table>`, e todas as tabelas estão dentro de `.tw`/`.tblw`, ver §11.2):

| seletor | declaração | @media | aulas |
|---|---|---|---|
| `table.t` | `min-width:520px` | - | rd-hemostasia, rd-lupus-saf, rd-vias-biliares |
| `table` | `min-width:560px` | - | glomerulopatias |
| `table.w7` | `min-width:700px` | - | glomerulopatias |
| `.tw table` | `min-width:620px` | - | kawasaki |
| `.tw table` | `min-width:640px` | - | neuromusculares |
| `.tw.w8 table` | `min-width:780px` | - | neuromusculares |

Colunas de grid com trilhas fixas em px somando >= 100px (as maiores; a 1a coluna fixa é o ponto de pressão em 390 px; medido: nenhuma estoura a 390 px, §11.3):

| seletor | grid-template-columns | @media | aulas |
|---|---|---|---|
| `.crit .row` | `150px minmax(0,1fr)` | - | 19 aulas |
| `.crit .row` | `150px minmax(0,1fr)` | @media (min-width:560px) | 12 aulas |
| `.crit.c3 .row` | `130px minmax(0,1fr) minmax(0,1fr)` | @media (min-width:560px) | 12 aulas |
| `.crit .row` | `180px 1fr` | - | 6 aulas |
| `details.ref .row` | `150px 1fr` | - | 6 aulas |
| `.crit.c3 .row` | `150px 1fr 1fr` | - | 5 aulas |
| `.body` | `210px minmax(0,1fr)` | - | 3 aulas |
| `.body` | `220px minmax(0,1fr)` | - | 3 aulas |
| `.crit.c3 .row` | `110px minmax(0,1fr) minmax(0,1fr)` | - | 2 aulas |
| `.crit.c4 .row` | `104px repeat(3,minmax(0,1fr))` | - | 2 aulas |
| `details.ref .row` | `150px minmax(0,1fr)` | @media (min-width:560px) | 2 aulas |
| `.crit .row` | `170px minmax(0,1fr)` | - | 1 aula |
| `.crit.c3 .row` | `118px minmax(0,1fr) minmax(0,1fr)` | - | 1 aula |
| `.crit.c3 .row` | `120px minmax(0,1fr) minmax(0,1fr)` | - | 1 aula |

### 11.2 Tabelas `<table>` e seus contêineres de rolagem

Tabelas no corpo: 58, em 12 aulas; dentro de contêiner com `overflow-x:auto` nas aulas (`.tw`/`.tblw`): 58; sem contêiner: 0.

| aula | fam. | tabelas | em `.tw` | em `.tblw` | sem contêiner |
|---|---|---|---|---|---|
| dossie-uerj | DO | 26 | 26 | 0 | 0 |
| glomerulopatias | ER | 6 | 6 | 0 | 0 |
| kawasaki | ER | 1 | 1 | 0 | 0 |
| neuromusculares | ER | 3 | 3 | 0 | 0 |
| rd-hemostasia | RG | 2 | 0 | 2 | 0 |
| rd-lupus-saf | RG | 3 | 0 | 3 | 0 |
| rd-meningites | RS | 1 | 1 | 0 | 0 |
| rd-neoplasias-tgi | RS | 2 | 2 | 0 | 0 |
| rd-ortopedia-cirurgia | RS | 5 | 5 | 0 | 0 |
| rd-pediatria | RS | 3 | 3 | 0 | 0 |
| rd-pilulas | RS | 3 | 3 | 0 | 0 |
| rd-vias-biliares | RG | 3 | 0 | 3 | 0 |

### 11.3 Medido no Edge headless (largura do iframe 390 e 704; aula crua, tokens v3 + camada BASE, tema v2.4 + camada BASE)

| configuração | largura | aulas com rolagem horizontal da PÁGINA | aulas com elemento fora da borda (fora de contêiner) | contêineres com rolagem lateral (auto) | contêineres CORTADOS (overflow:hidden) |
|---|---|---|---|---|---|
| aula crua (sem camada) | 390 | 0 | 0 | 21 (7 aulas) | 0 (0 aulas) |
| aula crua (sem camada) | 704 | 0 | 0 | 4 (2 aulas) | 0 (0 aulas) |
| tokens v3 + camada BASE (def2fdd) | 390 | 0 | 0 | 8 (3 aulas) | 14 (4 aulas) |
| tokens v3 + camada BASE (def2fdd) | 704 | 0 | 0 | 0 (0 aulas) | 6 (3 aulas) |
| tema.css v2.4 + camada BASE (def2fdd, como publicado) | 390 | 0 | 0 | 8 (3 aulas) | 14 (4 aulas) |
| tema.css v2.4 + camada BASE (def2fdd, como publicado) | 704 | 0 | 0 | 0 (0 aulas) | 6 (3 aulas) |

Contêineres cortados (base: tokens v3 + camada BASE). `rolam na crua` = contêineres `div.tw*` da aula crua, na mesma largura, com `overflow-x:auto` e conteúdo maior que a caixa:

| largura | aula | contêiner | conteúdo px | caixa px | escondido px | rolam na crua (nesta aula) |
|---|---|---|---|---|---|---|
| 390 | dossie-uerj | `div.tw` | 347 | 324 | 23 | 3 |
| 390 | dossie-uerj | `div.tw` | 377 | 324 | 53 | 3 |
| 390 | dossie-uerj | `div.tw` | 349 | 324 | 25 | 3 |
| 390 | dossie-uerj | `div.tw` | 339 | 324 | 15 | 3 |
| 390 | glomerulopatias | `div.tw` | 560 | 356 | 204 | 6 |
| 390 | glomerulopatias | `div.tw` | 700 | 356 | 344 | 6 |
| 390 | glomerulopatias | `div.tw` | 560 | 356 | 204 | 6 |
| 390 | glomerulopatias | `div.tw` | 700 | 356 | 344 | 6 |
| 390 | glomerulopatias | `div.tw` | 560 | 322 | 238 | 6 |
| 390 | glomerulopatias | `div.tw` | 560 | 356 | 204 | 6 |
| 390 | kawasaki | `div.tw` | 620 | 356 | 264 | 1 |
| 390 | neuromusculares | `div.tw.w8` | 780 | 356 | 424 | 3 |
| 390 | neuromusculares | `div.tw` | 640 | 356 | 284 | 3 |
| 390 | neuromusculares | `div.tw.w8` | 780 | 356 | 424 | 3 |
| 704 | glomerulopatias | `div.tw` | 700 | 606 | 94 | 2 |
| 704 | glomerulopatias | `div.tw` | 700 | 606 | 94 | 2 |
| 704 | kawasaki | `div.tw` | 620 | 606 | 14 | 0 |
| 704 | neuromusculares | `div.tw.w8` | 780 | 606 | 174 | 2 |
| 704 | neuromusculares | `div.tw` | 640 | 606 | 34 | 2 |
| 704 | neuromusculares | `div.tw.w8` | 780 | 606 | 174 | 2 |

## 12. CSS dos resumos: constante `CSS_RESUMO` em `tools/hub.py`

Onde: `tools/hub.py` linhas 1684-1724 (constante) e função `pagina_resumo` logo abaixo; cada resumo vira uma página `resumos/resumo-<nome>.html` = `<main class="wrap">` + `<p class="rs-olho">` + o corpo de `md_para_html`. Registrados em `core/hub_resumos.json`: 31 de 136 `.md` em `resumos/`. No leitor o resumo recebe as DUAS camadas por cima (`tema.css` + `tema-aula.css`), como as aulas.

**Tokens** (nomes em português, os MESMOS do `tema.css`; 3 blocos: claro `:root`, `@media (prefers-color-scheme:dark)` e `:root[data-theme="dark"]`): `--acento`, `--acento-fraco`, `--afundado`, `--card`, `--linha`, `--papel`, `--tinta`, `--tinta2`, `--tinta3`.
Todos os 9 nomes existem no tema v3 e são redefinidos por ele (seletor (0,2,0), depois do CSS do resumo), então no leitor o resumo já sai na paleta nova; a paleta própria só aparece fora do leitor (A16 do `docs/UI.md`).

**Componentes** (tag/classe -> declarações). HTML gerado: `h1..h6`, `p`, `ul/ol > li (> div)`, `strong/em/code/a`, `blockquote`, `hr`, `div.cod > pre > code`, `div.tab > table`, `p.rs-olho`.

| seletor | declarações |
|---|---|
| `*` | box-sizing:border-box |
| `html,body` | margin:0; padding:0 |
| `body` | background:var(--papel); color:var(--tinta); font:16px/1.6 ui-sans-serif,system-ui,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; -webkit-text-size-adjust:100%; overflow-wrap:break-word |
| `.wrap` | max-width:46rem; margin:0 auto; padding:18px 16px 40px; min-width:0 |
| `.rs-olho` | margin:0 0 6px; font-size:.8rem; font-weight:650; color:var(--acento) |
| `h1` | font-size:clamp(1.4rem,1.15rem + 1.2vw,1.9rem); line-height:1.2; margin:0 0 18px; letter-spacing:-.01em; text-wrap:balance |
| `h2` | font-size:1.18rem; line-height:1.3; margin:28px 0 10px |
| `h3` | font-size:1.04rem; line-height:1.35; margin:22px 0 8px |
| `h4,h5,h6` | font-size:1rem; line-height:1.4; margin:18px 0 6px; color:var(--tinta2) |
| `p` | margin:0 0 12px |
| `ul,ol` | margin:0 0 12px; padding-left:1.3em |
| `li` | margin:4px 0 |
| `li>ul,li>ol` | margin:4px 0 0 |
| `strong` | font-weight:650 |
| `a` | color:var(--acento); font-weight:600; text-underline-offset:2px |
| `code` | font:.88em ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; background:var(--afundado); border-radius:4px; padding:1px 5px |
| `blockquote` | margin:0 0 14px; padding:10px 14px; border-left:3px solid var(--acento); background:var(--acento-fraco); border-radius:0 8px 8px 0 |
| `blockquote>:last-child` | margin-bottom:0 |
| `hr` | border:0; border-top:1px solid var(--linha); margin:22px 0 |
| `.cod,.tab` | margin:0 0 14px; border:1px solid var(--linha); border-radius:8px; background:var(--card) |
| `.tab` | overflow-x:auto |
| `.cod pre` | margin:0; padding:10px 12px; overflow-x:auto; tab-size:4; font:.82em/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace |
| `.cod code` | background:none; padding:0; font-size:1em |
| `.tab table` | border-collapse:collapse; min-width:100%; font-size:.92em |
| `.tab th,.tab td` | border-bottom:1px solid var(--linha); padding:8px 10px; text-align:left; vertical-align:top; min-width:7rem |
| `.tab th` | background:var(--afundado); font-weight:650 |

**Medido** (resumo-amostra com os mesmos elementos, no Edge; aula crua = só `CSS_RESUMO`, v3 = com as duas camadas):

| largura | configuração | .wrap | corpo: fonte / caracteres por linha | h1: tamanho / peso | strong | a | família do `pre` | .tab overflow-x |
|---|---|---|---|---|---|---|---|---|
| 390 | só CSS_RESUMO | 390px (max 736px) | 16px / ~46 car. | 23.08px / 700 | #EDEFF3 | #4FD0B3 | ui-monospace, SFMono-Regular, Menl | auto |
| 390 | CSS_RESUMO + tema v3 + camada | 390px (max 992px) | 17px / ~44 car. | 23.08px / 650 | #7DE8F0 | #00D9E8 | "Atkinson Hyperlegible Next", ui-s | auto |
| 704 | só CSS_RESUMO | 704px (max 736px) | 16px / ~86 car. | 26.848px / 700 | #EDEFF3 | #4FD0B3 | ui-monospace, SFMono-Regular, Menl | auto |
| 704 | CSS_RESUMO + tema v3 + camada | 704px (max 992px) | 17px / ~81 car. | 26.848px / 650 | #7DE8F0 | #00D9E8 | "Atkinson Hyperlegible Next", ui-s | auto |

## 13. O que as camadas do tema fazem com as aulas (base: camada commitada)

Arquivos lidos (snapshot desta auditoria; `tema.css` estava sendo reescrito em paralelo, v3 -- por isso os dois estados):

Arquivos e versões lidos: tabela do §2. As linhas de `tema-aula.css` citadas no §14 são as do arquivo do commit BASE (def2fdd).

### 13.1 Como as camadas entram

- `core/templates/hub.html` (`comTema`/`documentoCompleto`): remove os `<link>` do Google Fonts da aula, anexa `<link>` da Atkinson + `<style id="medhub-tema">` com `tema.css` + `tema-aula.css` NO FIM do documento (depois do `<style>` da aula) e embrulha em `<!DOCTYPE html>` + viewport. Mesma função (`carregar`) para o leitor (aulas e resumos) E para o Painel (`artifacts/painel.html`): a camada de leitura também chega ao Painel.
- Cascata: seletores da camada têm especificidade de (0,0,1) a (0,4,0) e vencem a aula por ORDEM quando empatam; perdem para qualquer seletor mais específico da aula (`.trap .albl`, `.crit .row .v`, `.synth.arm`, `ul.pt li`, `h4.sub`...). O `tema.css` usa (0,2,0) nos blocos de token para vencer os blocos escuros das aulas.
- Largura do iframe do leitor: a do `.wrap` do hub. `--wrap:46rem` no tema v3 em curso => iframe de ate 704 px no desktop (736 - 2x16); no commit BASE o `--wrap` nem existe no `tema.css` (o `.wrap` do hub fica sem teto). Medido aqui a 390 e 704 px.
- Painel: classes do painel que a camada de leitura também mira: `.sub` (1), `.wrap` (1); tags: `body` (1), `details` (3), `h2` (5), `h3` (4), `summary` (3), `table` (1), `td` (18), `th` (10), `thead` (1). Reescrever seletores de tag (`body`, `h1-h4`, `table`, `th/td`, `code`, `strong`, `footer`) muda o Painel junto.

### 13.2 `core/templates/tema-aula.css` do commit BASE def2fdd (sha1 6dc02f95), a camada de leitura: seletor -> o que faz -> quantas aulas -> quem vence (medido a 704 px sobre os tokens v3)

`aulas` = aulas com ao menos um elemento que casa o seletor (consulta `querySelectorAll` no DOM real das 43 aulas); `elem.` = total de elementos. `não vence` = declarações em que a regra da própria aula ganha, por elementos (calculado por cascata no navegador: especificidade + ordem + !important).

| seletor | declarações | aulas | elem. | efeito | não vence |
|---|---|---|---|---|---|
| `body` | `font-size:17px; line-height:1.62` | 43 | 43 | corpo 17px/1.62 (as aulas usam 15.4-17px/1.5-1.6; o resumo 16px/1.6) | - |
| `.wrap` | `max-width:62rem; padding:0 20px 96px` | 43 | 43 | coluna 62rem + padding 20px; vence os `max-width` próprios das aulas (760/780/820/1180px, §14 L2) e os 46rem do resumo. No iframe do hub o `.wrap` ocupa a largura toda do iframe | - |
| `@media(max-width:640px) .wrap` | `padding:0 16px 72px` | 43 | 43 | padding lateral 16px no celular | - |
| `h1,h2,h3,h4` | `font-weight:650; letter-spacing:-.015em; line-height:1.2; color:var(--ink)` | 43 | 732 | títulos 650, tracking -.015em, cor --ink (branco); perde para `.vs h3/h4`, `.tgrp h3`, `.blk h3`, `h4.sub` etc. | font-weight: 170/732 -> aula: .vs h3 {font} (30), details.blk h3 {font} (25); outra regra da camada: .top h1 {font-weight} (42), h3.sub {font-weight} (13); letter-spacing: 148/732 -> aula: .vs h3 {letter-spacing} (30), details.blk h3 {letter-spacing} (25); outra regra da camada: .top h1 {letter-spacing} (42); line-height: 90/732 -> aula: .vs h3 {font} (30), details.blk h3 {font} (25); color: 129/732 -> aula: h4.sub {color} (24), .vs .a h3 {color} (20); outra regra da camada: h3.sub {color} (13) |
| `.top` | `padding:36px 0 24px; border-bottom:0` | 42 | 42 | cabeçalho com padding menor e SEM filete inferior | - |
| `.eye` | `font-weight:500; font-size:14px; color:var(--ink3); margin:0 0 10px` | 42 | 42 | linha de contexto 14px/500 em --ink3 (o tema zera a caixa-alta, mas o letter-spacing da aula fica) | - |
| `.top h1` | `font-size:clamp(30px,6.4vw,46px); font-weight:700; letter-spacing:-.025em; max-width:20ch; margin-bottom:12px` | 42 | 42 | h1 clamp(30,6.4vw,46)px/700, até 20ch | - |
| `.top .sub` | `font-size:17px; color:var(--ink2); max-width:60ch` | 42 | 42 | subtítulo 17px em --ink2, até 60ch | - |
| `.spec` | `display:grid; gap:0 28px; background:none; border:0; border-top:1px solid var(--line2); margin-top:22px` | 1 | 1 | grade `.spec` da glomerulopatias sem caixa, só filetes | - |
| `.spec div` | `background:none; padding:12px 0; border-top:0; border-bottom:1px solid var(--line)` | 1 | 5 | células do `.spec` sem fundo, filete inferior | border-top: 5/5 -> outra regra da camada: .spec div[class] {border-top} (5) |
| `.spec div[class]` | `border-top:0` | 1 | 5 | zera o filete superior das células com classe | - |
| `.spec .tn` | `font-size:15px; font-weight:650` | 1 | 5 | rótulo 15px/650 | - |
| `.spec .tv` | `font-size:14px; color:var(--ink2)` | 1 | 5 | valor 14px --ink2 | - |
| `.body` | `grid-template-columns:11rem minmax(0,38rem); gap:52px; padding-top:28px` | 6 | 6 | grade 11rem + 38rem (só a família ER). Nunca ativa no hub: o iframe tem <= 704px e a regra de 920px a derruba para 1 coluna | - |
| `main` | `max-width:38rem` | 13 | 13 | ÚNICO limite de coluna de leitura: 38rem, e só nas aulas que têm `<main>` (ER e RG) | - |
| `@media(max-width:920px) .body` | `grid-template-columns:minmax(0,1fr); gap:20px` | 6 | 6 | 1 coluna e gap 20px (sempre ativa no hub) | - |
| `.rail .rlab` | `font-weight:600; color:var(--ink3); font-size:13px` | 6 | 6 | rótulo do trilho 13px/600 --ink3 | - |
| `.rail a` | `font-size:14.5px; border-left:0; padding:6px 0 6px 12px; box-shadow:inset 1px 0 0 var(--line2)` | 6 | 67 | link do trilho 14.5px, sem filete esquerdo, com régua inset 1px | - |
| `.rail a:hover` | `color:var(--ink)` | 6 | 67 | hover em --ink | - |
| `.rail a.on` | `box-shadow:inset 2px 0 0 var(--teal); color:var(--ink); font-weight:600` | 0 | 0 | ativo: régua inset 2px --teal (o `.on` é posto por JS da aula) | - |
| `.rail a .rn` | `color:var(--ink3)` | 6 | 67 | número do degrau em --ink3 | - |
| `@media(max-width:920px) .rail a` | `padding:5px 12px; border:0; border-radius:999px; background:var(--sunk); box-shadow:none; color:var(--ink2)` | 6 | 67 | PÍLULA: raio 999px, fundo --sunk (sempre ativa no hub) | - |
| `@media(max-width:920px) .rail a.on` | `background:var(--teal-wash); color:var(--teal-ink); box-shadow:none` | 0 | 0 | pílula ativa em teal-wash/teal-ink | - |
| `.degrau` | `padding:34px 0; border-bottom:1px solid var(--line)` | 28 | 325 | degrau com padding 34px e filete inferior | padding: 9/325 -> aula: .degrau:first-child {padding-top} (9); border-bottom: 7/325 -> aula: .degrau:last-of-type {border-bottom} (7) |
| `.dhead` | `gap:14px; align-items:flex-start` | 28 | 325 | cabeça do degrau gap 14px, alinhada ao topo | - |
| `.dnum` | `width:auto; height:auto; min-width:36px; border:0; border-radius:0; display:block; font-size:42px; font-weight:300; line-height:.9; margin-top:4px; letter-spacing:-.04em; color:var(--suave)` | 28 | 325 | número do degrau vira texto 42px/300, sem círculo, cor --suave (roxo) | font-size: 7/325 -> aula: .dnum.r {font-size} (7) |
| `.dtitle .dstage` | `font-weight:500; font-size:13.5px; color:var(--ink3)` | 13 | 115 | etapa 13.5px/500 --ink3 | - |
| `.dtitle h2` | `font-size:clamp(21px,4.2vw,27px)` | 13 | 115 | título do degrau clamp(21,4.2vw,27)px; NÃO cobre `.dtitle h3` (família EN, L8) | - |
| `.lede` | `font-style:normal; font-size:17px; color:var(--ink2); margin-bottom:16px` | 41 | 357 | sem itálico, 17px --ink2 | margin-bottom: 2/357 -> aula: .synth .lede {margin-bottom} (2) |
| `.prose li` | `font-size:16.5px; line-height:1.62; color:var(--ink2)` | 28 | 1002 | item 16.5px/1.62 --ink2 | - |
| `h3.sub` | `font-size:16px; font-weight:650; margin:28px 0 8px` | 2 | 13 | sub-título 16px/650 (não cobre `h4.sub`) | - |
| `.trap,.banca,.aside` | `border:0; border-radius:12px; padding:14px 16px; margin:20px 0` | 33 | 177 | ZERA a borda (filete esquerdo 3px some), raio 12px, padding 14x16, margin 20 | margin: 1/177 -> aula: details.ref .banca {margin} (1) |
| `.albl` | `font-weight:650; font-size:13.5px` | 23 | 157 | rótulo 13.5px/650 (perde para `.trap .albl{font:...}` das aulas que o declaram em caixa-alta) | font-weight: 25/157 -> aula: .trap .albl {font} (15), .banca .albl {font} (4); font-size: 31/157 -> aula: .trap .albl {font} (15), .banca .albl {font} (4); outra regra da camada: .banca p {font-size} (2), .trap p {font-size} (2) |
| `.trap p,.banca p,.aside p` | `font-size:16px; line-height:1.58` | 23 | 163 | texto do callout 16px/1.58 | - |
| `.vs,.cmap,.if3,.trig,.arms,.crit,.tw,details.ref` | `border:1px solid var(--line); border-radius:12px; overflow:hidden` | 42 | 507 | borda 1px --line, raio 12px e OVERFLOW:HIDDEN (corta a rolagem lateral de `.tw`) | border: 1/507 -> aula: details.ref .crit {border-left} (1) |
| `.vs,.cmap,.if3,.trig,.arms` | `gap:1px; background:var(--line)` | 40 | 224 | gap 1px sobre fundo --line (as divisórias da grade) | - |
| `.vs>div,.cmap>div,.if3>div,.arm` | `background:var(--card)` | 39 | 299 | células em --card | background: 13/299 -> outra regra da camada: .synth {background} (13) |
| `.trig div` | `background:var(--sunk)` | 21 | 291 | células de gatilho em --sunk | - |
| `.cmap .k3,.cmap .k34,.cmap .kn` | `border-top-width:2px` | 1 | 3 | borda superior 2px (glomerulopatias) | - |
| `table` | `font-size:15px` | 12 | 58 | tabela 15px | font-size: 12/58 -> aula: table.t {font-size} (8), .tw table {font-size} (4) |
| `thead th` | `background:var(--sunk); color:var(--acento-tinta); font-weight:650; font-size:13.5px` | 4 | 120 | cabeçalho de tabela --sunk, 13.5px/650, cor ciano claro | background: 20/120 -> aula: .tw thead th {background} (20); color: 20/120 -> aula: .tw thead th {color} (20); font-weight: 20/120 -> aula: .tw thead th {font-weight} (20); font-size: 20/120 -> aula: .tw thead th {font-size} (20) |
| `th,td` | `padding:10px 12px` | 12 | 1227 | células 10x12 | padding: 266/1227 -> aula: .tw td {padding} (121), table.t td {padding} (66) |
| `.c` | `border-radius:6px` | 3 | 19 | raio 6px nos chips numéricos | - |
| `.flow span` | `border-radius:8px; border-color:var(--line); font-size:15px` | 3 | 44 | caixas do fluxo raio 8px, 15px | font-size: 36/44 -> aula: .flow .fv {font-size} (18), .flow .fk {font-size} (18) |
| `details.ref>summary` | `font-weight:600; color:var(--ink)` | 15 | 36 | summary 600 --ink | - |
| `.synth` | `border:0; background:var(--sunk); border-radius:16px` | 21 | 36 | síntese sem borda, fundo --sunk, raio 16px (perde o filete esquerdo para `.synth.arm`) | border: 13/36 -> aula: .synth.arm {border-left} (13) |
| `.synth h2` | `font-size:24px` | 21 | 36 | título da síntese 24px | - |
| `code` | `background:var(--sunk); border-radius:4px; font-size:.9em` | 32 | 170 | código em --sunk, raio 4px, .9em | background: 51/170 -> aula: .src code {background} (51); border-radius: 51/170 -> aula: .src code {border-radius} (51); font-size: 51/170 -> aula: .src code {font-size} (51) |
| `footer` | `border-top:1px solid var(--line)` | 22 | 22 | rodapé com filete superior | - |
| `strong` | `color:var(--acento-tinta)` | 42 | 1651 | TODO negrito em ciano claro (--acento-tinta); perde para `.prose li strong`, `.arm p strong`, `.crit .row .v strong` etc. | color: 320/1651 -> aula: .prose li strong {color} (203), .arm p strong {color} (55) |
| `h3.sub` | `color:var(--acento-tinta)` | 2 | 13 | sub-título em ciano claro | - |
| `.dtitle .dstage` | `color:var(--acento-tinta)` | 13 | 115 | etapa do degrau em ciano claro | - |
| `.rail .rlab` | `color:var(--acento-tinta)` | 6 | 6 | rótulo do trilho em ciano claro | - |
| `.crit.hd .row:first-child>*` | `color:var(--acento-tinta)` | 18 | 258 | linha de cabeçalho das tabelas em div em ciano claro | color: 13/258 -> aula: .crit.hd .row:first-child .v {color} (7), .crit.hd .row:first-child .k {color} (6) |

Diferenças entre 390 e 704 px (só regras que dependem de `@media`): `.wrap` padding n/ganha 43/43 (704) vs 43/0 (390); `.wrap` padding so em 390.

### 13.3 `core/templates/tema.css` v3 (em curso): o que ainda atinge aulas

O v3 só tem tokens + base. Regras com efeito nas aulas:

| seletor | declarações | aulas | efeito |
|---|---|---|---|
| `*` | `font-family:var(--fonte)!important; font-variant-numeric:tabular-nums; text-transform:none!important` | 43 | uma família só: anula Fraunces/Plex/Barlow e o MONO de `code`, `pre`, `.mn`, `.src`, `.tk`, `.stat b` etc.; `text-transform:none` desliga a caixa-alta em 40 aulas que a declaram, mas o `letter-spacing` das mesmas regras continua (ver §14 L3) |
| `body` | `background:var(--papel); color:var(--tinta); -webkit-font-smoothing:antialiased` | 43 | fundo e cor; sozinho NÃO recolore autópsia/neuromusculares (nomes próprios) |
| `strong` | `font-weight:650` | 42 | negrito 650 (a cor vem da camada de leitura) |
| `:focus-visible`, `::selection` | contorno ciano 2px; seleção ciano | 43 | foco e seleção |
| `@media (prefers-reduced-motion)` `*` | `animation:none!important; transition:none!important` | 43 | sem animação |

Regras de aula que o `tema.css` tinha no commit BASE (v2.4) e o v3 REMOVEU (continuam em `def2fdd`/`730d884`): 

| seletor (v2.4) | declarações | aulas que casam |
|---|---|---|
| `.fig` | `background:transparent; border-top:1px solid var(--linha); border-radius:0; padding:10px 0` | 1 |
| `.card` | `box-shadow:none` | 1 |
| `.dnum` | `color:var(--acento)` | 28 |
| `.top h1` | `text-shadow:0 0 28px rgba(0,240,255,.22)` | 42 |
| `.aside` | `background:var(--acento-fraco)` | 6 |
| `.aside .albl` | `color:var(--acento-tinta)` | 6 |
| `thead th` | `color:var(--acento-tinta)` | 4 |

Notas: `.top h1{text-shadow}` era o brilho do título (42 aulas); `.dnum{color:var(--acento)}` do v2.4 já era anulada pelo `.dnum{color:var(--suave)}` da camada de leitura (que vem depois); `.card{box-shadow:none}` e `.fig*` atingiam só a autópsia (`.card`) e a imagem-obstetrica/(`figure.fig`).

### 13.4 Censo de cor do texto hoje (tema v3 + camada, 704 px)

Cada elemento com texto próprio nas 43 aulas (16838 elementos), pela cor computada. Mostra QUAIS seletores pintam texto de cada cor (não só o que a camada declara). Os 'seletores' são tag.classe do elemento que contém o texto; cada aula contribui com seus 10 maiores.

| cor | token | elementos | % | aulas | seletores que mais a usam |
|---|---|---|---|---|---|
| #B8B3CC | --tinta2 (lavanda) | 6010 | 35.7% | 42 | `li` 2284, `span.v` 1169, `td` 497, `p.lede` 356, `span.tv` 304, `p` 276, `span.gc` 205, `a` 200 |
| #7DE8F0 | --acento-tinta (ciano claro) | 3775 | 22.4% | 42 | `strong` 1331, `span.k` 885, `span.tk` 275, `summary` 239, `span.v` 153, `span.tag` 127, `span.dstage` 115, `b` 106 |
| #F8F5F2 | --tinta (branco) | 3179 | 18.9% | 43 | `p` 541, `strong` 320, `h2` 297, `td` 250, `h3` 243, `b` 216, `mark` 115, `q` 115 |
| #9C96B6 | --tinta3 (lavanda escura) | 1245 | 7.4% | 42 | `code` 170, `span` 159, `span.d` 157, `span.src` 154, `span.kick` 107, `p` 74, `span.rn` 67, `p.src` 61 |
| #9AA6A1 | - | 1093 | 6.5% | 1 | `p.k` 358, `span.nota` 176, `span.muted` 129, `b` 74, `span.at` 74, `span` 66, `p.muted` 48, `span.qm` 44 |
| #FFB3BA | carmine-ink (rosa claro) | 503 | 3.0% | 42 | `b` 130, `div.albl` 85, `span.n` 79, `h5` 62, `span.mn` 53, `span.gk` 31, `h3` 20, `span.fv` 11 |
| #AA71E8 | --roxo | 325 | 1.9% | 28 | `span.dnum` 312, `span.dnum.r` 7, `div.dnum` 6 |
| #6FD3AA | - | 170 | 1.0% | 1 | `a` 86, `span.tag` 43, `span.pill` 41 |
| #C2CBC6 | - | 130 | 0.8% | 1 | `summary` 44, `blockquote.trecho` 35, `blockquote` 25, `button.chip` 9, `b` 5, `span.num` 5, `h3` 5, `p.ctx` 1 |
| #FFD3A0 | amber-ink (pêssego) | 106 | 0.6% | 22 | `div.albl` 50, `span.fx` 28, `span.ff` 10, `span.bd` 5, `p.src.out` 4, `p.albl` 2, `span.fora` 2, `span.bn` 2 |
| #BE95F0 | --roxo-tinta | 75 | 0.4% | 2 | `span.k` 47, `span.tk` 14, `b` 4, `i` 4, `h4` 3, `span` 3 |
| #14181A | - | 68 | 0.4% | 1 | `button` 66, `button.chip.on` 2 |
| #BCC9F6 | - | 67 | 0.4% | 1 | `span.k` 27, `th` 21, `span.tk` 12, `span.ak` 6, `div.albl` 1 |
| #D9776B | - | 50 | 0.3% | 1 | `span.tag` 26, `span.res` 24 |

## 14. Achados para a reescrita da camada de leitura

Todos medidos neste snapshot (tokens do tema v3 + camada de leitura do commit BASE def2fdd, Edge headless, iframe de 704 px = hub no desktop com `--wrap:46rem`; 390 px = celular). Ids `L1..` são provisórios (o `docs/UI.md` reserva A19-A24 para o leitor).

| id | achado | evidência (medida) | ação possível |
|---|---|---|---|
| L1 | `.tw` perde a rolagem lateral e a tabela é CORTADA | tema-aula.css:48 `.vs,.cmap,.if3,.trig,.arms,.crit,.tw,details.ref{overflow:hidden}` vence o `.tw{overflow-x:auto}` de 20 aulas (mesma especificidade, vem depois). 390 px: 14 tabelas cortadas em 4 aulas (dossie-uerj, glomerulopatias, kawasaki, neuromusculares), até 424 px escondidos; 704 px: 6 tabelas em 3 aulas. Na aula crua as mesmas tabelas rolavam (13 contêineres `.tw` com `overflow-x:auto` a 390 px). 3 aulas ainda mandam 'role/deslize a tabela para o lado' (glomerulopatias, kawasaki, neuromusculares). | tirar `.tw` da lista do `overflow:hidden` (ou `.tw{overflow-x:auto}` depois). `.tblw` (3 aulas RD-degrau) já rola porque a camada não o cita |
| L2 | Coluna de leitura: só `main` tem teto (38rem), e 30 aulas não têm `<main>` | a camada manda `.wrap{max-width:62rem}` (vence os 760px (21 aulas), 780px (15 aulas), 1180px (6 aulas), 820px (1 aulas) das aulas e os 46rem do resumo) e só `main{max-width:38rem}` limita o texto. A 704 px: 13 aulas com `<main>` -> texto 608 px (~74 car./linha); 30 aulas sem `<main>` -> texto 644-664 px (~81-86 car./linha); as mesmas aulas cruas tinham ~85-88. A 390 px: ~44-45 car. em todas. Resumo (`CSS_RESUMO`, `<main class="wrap">`): coluna de 704 px e ~86 car./linha cru -> 704 px e ~81 com a camada (o `main{38rem}` perde para o `.wrap{62rem}` no mesmo elemento). Se o iframe for mais largo que o `--wrap` (commit BASE do hub, sem `--wrap`; medido a 1000 px): texto das aulas sem `<main>` de ~94-100 car./linha (crua) para ~116-124 (camada); das com `<main>` ~89-93 -> ~74. | limitar o texto no próprio `.wrap` (ou `.wrap>*`), não em `main`; hoje só 13/43 aulas respeitam os 38rem do contrato do UI.md |
| L3 | Caixa-alta desligada, espaçamento de letras mantido | `tema.css` tem `text-transform:none!important`; as aulas declaram `letter-spacing:.04em-.14em` junto com o `uppercase` e a camada não o zera. Medido (1º elemento de cada aula): `.eye` 39 aulas (1.68-1.96 px a 14px); `.kick` 14 aulas (1.10 px a 11px); `.dtitle .dstage` 10 aulas (1.35 px a 13.5px); `.rail .rlab` 3 aulas (1.30 px a 13px); `.trap .albl` 18 aulas (1.05-1.35 px a 10.5px/13.5px); `.banca .albl` 16 aulas (1.05-1.35 px a 10.5px/13.5px); `.aside .albl` 3 aulas (1.05-1.35 px a 10.5px/13.5px); `.vs .a h3/h5` 33 aulas (0.46-0.57 px a 11.5px/12px); `.vs .b h3/h5` 33 aulas (0.46-0.57 px a 11.5px/12px); `th` 9 aulas (0.48-0.68 px a 11.5px/12px/13.5px); `.q .tag` 13 aulas (0.42 px a 10.5px). Aulas afetadas em ao menos um rótulo: 39 de 43. | `letter-spacing:0` nos rótulos (`.eye .kick .dstage .rlab .albl th .tk .tag` e `h3/h5` de `.vs`) |
| L4 | Callouts sem critério único: `trap/banca/aside` viram lavagem sem filete; os outros mantêm filete 3px e cantos retos | tema-aula.css:44 (`.trap,.banca,.aside{border:0;border-radius:12px}`) só cita 3 classes; `.key`, `div.note`, `.ato`, `.disc`, `.fonte`, `.ext`(dmg) e `.synth.arm` ficam como a aula os pintou. Medido (fundo, filete esquerdo, raio; nº de aulas): .trap: #3C243C, sem filete, raio 12px (31); .banca: #3C2E39, sem filete, raio 12px (19); .aside: #13334C, sem filete, raio 12px (5) / #232B45, sem filete, raio 12px (1); .key: #13334C, 3px #00D9E8, raio 0px (2); div.note: #3C2E39, 3px #FFBE72, raio 0px (5); .ato: #13334C, 3px #00D9E8, raio 0px (10) / #2F224C, 3px #AA71E8, raio 0px (1); .disc: #13334C, 3px #00D9E8, raio 0px (1); .fonte: #13334C, 3px #00D9E8, raio 0px (1); .ext(dmg): #3C2E39, 3px #FFBE72, raio 0px (1); .synth.arm: #29233F, 3px #FF7C87, raio 16px (13); .star: #211C3A, 1px #776E99, raio 0px (2). O rótulo `.albl` fica em carmine-ink/amber-ink/teal-ink (rosa claro / pêssego / ciano claro) e a camada perde o tamanho em 31 de 157 rótulos. | uma regra por significado (armadilha / banca / nota) cobrindo TODOS os alias e `.albl` com seletor (0,2,0) |
| L5 | `strong` ciano em 81% dos casos, com exceções por descendente | tema-aula.css:66 `strong{color:var(--acento-tinta)}` pinta 1331 de 1651 `<strong>` (42 aulas) de ciano claro; os outros 320 seguem a aula (`--ink`, branco) por seletores como `.prose li strong {color}` (203), `.arm p strong {color}` (55), `.crit .row .v strong {color}` (37). No resumo todo `strong` também fica ciano. | decidir se o termo-chave é ciano (contrato do UI.md) e então igualar a especificidade para todos |
| L6 | `h3/h4/h5` servem de título E de rótulo: a regra de título não manda neles | pais de `h3` (337): `.dtitle` 210, `.blk` 33, `.a` 20, `.b` 20, `.degrau` 17; de `h5` (137): `.b` 64, `.a` 62, `div` 5; de `h4` (48): `.degrau` 21, `.prose` 17, `div` 3. A regra `h1,h2,h3,h4{color:--ink}` perde a cor em 129 de 732 elementos para `h4.sub {color}`, `.vs .a h3 {color}`, `.vs .b h3 {color}`, `.tgrp h3 {color}`. | rótulo por CLASSE do contêiner (`.vs :is(h3,h4,h5)`, `.tgrp h3`, `.blk h3`, `.cream h5`, `.cmap h4`, `.if3 h4`) em lavanda; título por posição (`.dtitle > *`) |
| L7 | `h4.sub` fora da regra de sub-título | a camada só tem `h3.sub` (13 elementos em 2 aulas: glomerulopatias, neuromusculares); `h4.sub` são 24 elementos em 7 aulas (dmg, kawasaki, prevencao-quaternaria, rd-hemostasia, rd-lupus-saf, rd-vias-biliares, topicos-pediatria) e ficam 14px/600 branco, enquanto `h3.sub` fica 16px ciano claro. | `:is(h3,h4).sub` |
| L8 | Título do degrau é `h2` em 13 aulas e `h3` em 15 | a camada dimensiona só `.dtitle h2` (clamp 21-27px; aulas: ER6 RG7); os `.dtitle h3` (aulas: EN15) ficam com o tamanho da própria aula. | `.dtitle :is(h2,h3)` |
| L9 | Dois outliers de paleta não são recoloridos | autópsia (18 tokens próprios: `--bg --surface --ink-2 --muted --rule --accent --marcada --warn ...`) e neuromusculares (`--acc/--acc-ink/--acc-wash`, indigo). Medido: `.aside` da neuromusculares fica #232B45 (nas outras `#13334C`), `.q` da autópsia fica #1C2224 com filete #D9776B sobre o fundo do tema (`#17132E`). | declarar os apelidos na camada (tabela do §8.3) com seletor (0,2,0) |
| L10 | Chips e pílulas do cabeçalho | `nav.nav a` (16 aulas, 7-24 caixas na zona do cabeçalho, borda 1px, raio 2px) não é tocado pela camada; `nav.rail a` vira pílula 999px nas 6 aulas ER porque o iframe (<= 704 px) está sempre abaixo de 920px (o trilho lateral nunca aparece no hub). Altura do cabeçalho até o 1º bloco a 390 px (média; min-max): EN 738 px (540-982), ER 869 px (680-1100), RS 296 px (254-362). | decidir o destino de `.nav`, `.rail` e `.stats` (são as únicas caixas/chips do cabeçalho) |
| L11 | Monoespaçada anulada por `*{font-family:...!important}` | 43 aulas declaram mono (`code`, `.dnum`, `.rn`, `.stat b`, `.tk`, `.src`, `.fora`, `.q .tag`...); 170 `<code>` em 32 aulas. No resumo-amostra o `pre` computa `"Atkinson Hyperlegible Next", ui-sans-serif, sys` (cru: monoespaçada). Blocos `.cod pre` alinhados por espaços perdem o alinhamento. | exceção `code,pre,.cod *{font-family:var(--fonte-mono)}` (token novo) ou aceitar |
| L12 | A camada de leitura também chega ao Painel | `carregar()` do hub.html aplica `documentoCompleto` ao leitor E ao painel; ver §13.1 (tags `body h2 h3 table th td details summary` e `.wrap/.sub`). | seletores de tag da camada afetam o painel; escopar por classe do leitor ou aceitar |
| L13 | `section.synth.arm` mantém filete carmine e cantos curvos | `.synth{border:0;border-radius:16px;background:--sunk}` perde a borda esquerda para `.synth.arm{border-left:3px solid var(--carmine)}` em 13 de 36 sínteses (13 aulas, EN13): fica um filete reto sobre canto de 16px. | incluir `.synth.arm` na regra ou zerar a borda |
| L14 | Tabelas: a camada perde para `.tw td/.tw th/table.t` | `th,td{padding:10px 12px}` perde em 266 de 1227 células; `table{font-size:15px}` perde em 12 de 58 tabelas; `thead th` perde fundo/cor/peso/tamanho em 20 de 120 `th` (`.tw thead th`). | aceitar a tabela da aula ou subir a especificidade (`.tw table`, `.tblw table`) |
| L15 | O texto ciano não é só o termo-chave | censo (§13.4): 3780 de 16838 elementos de texto (22%) saem em ciano; branco 3179 (19%); lavanda (--tinta2/--tinta3) 7255 (43%). Quem pinta ciano: `strong` 1331, `span.k` 885, `span.tk` 275, `summary` 239, `span.v` 153, `span.tag` 127, `span.dstage` 115, `b` 106. | ciano só no negrito do termo-chave: `.crit .k`, `.tk`, `.dstage`, `.rail .rlab`, `th`, `.eye`... passam a lavanda por seletor da camada |

## 15. Verificação rápida da camada reescrita (`tema-aula.css` do working tree / commit seguinte ao BASE)

Durante a auditoria o `tema-aula.css` foi reescrito e commitado (b84ce58 design (s225): tema v3 retrowave contido -- tema.css fonte unica (tokens + base); regras de componente voltam aos arquivos das telas). As seções 6-14 descrevem a camada ANTERIOR (commit BASE def2fdd, sha1 `6dc02f95`), que é a que o pedido descreve. Aqui as mesmas medidas foram repetidas sobre o arquivo do working tree (`tema.css` v3 + `tema-aula.css` sha1 `7a44c69d`, snapshot 2026-10-13T01:05:49): coluna `BASE` = camada anterior sobre os tokens v3; coluna `camada nova` = a reescrita. O arquivo continuava sendo editado; confira o sha1 antes de usar.

| métrica | BASE (camada anterior + tokens v3) | camada nova (working tree) |
|---|---|---|
| contêineres CORTADOS (overflow-x:hidden com conteúdo maior), 390 px | 14 em 4 aulas | 14 em 4 aulas |
| contêineres CORTADOS, 704 px | 6 em 3 aulas | 6 em 3 aulas |
| aulas com rolagem horizontal da página (390 / 704) | 0 / 0 | 0 / 0 |
| aulas com elemento fora da borda (390 / 704) | 0 / 0 | 0 / 0 |
| .wrap max-width computado | 992px (43) | 736px (37), 992px (6) |
| caracteres/linha a 704 px: com `<main>` (13 aulas) / sem (30) | 74-74 / 81-86 | 74-74 / 81-86 |
| caracteres/linha a 390 px | 44-45 | 44-45 |
| aulas com letter-spacing residual em `.eye` | 39 | 0 |
| aulas com letter-spacing residual em `.kick` | 14 | 14 |
| aulas com letter-spacing residual em `.trap .albl` | 18 | 4 |
| aulas com letter-spacing residual em `th` | 9 | 8 |
| callout .trap (fundo, filete esquerdo, raio) | #3C243C, sem filete, raio 12px (31) | #3C2E39, filete 3px #FFBE72, raio 0px 6px 6px 0px (31) |
| callout .banca (fundo, filete esquerdo, raio) | #3C2E39, sem filete, raio 12px (19) | #2F224C, filete 3px #AA71E8, raio 0px 6px 6px 0px (19) |
| callout .aside (fundo, filete esquerdo, raio) | #13334C, sem filete, raio 12px (5); #232B45, sem filete, raio 12px (1) | #29233F, filete 3px #776E99, raio 0px 6px 6px 0px (6) |
| callout .key (RS/DO) (fundo, filete esquerdo, raio) | #13334C, filete 3px #00D9E8, raio 0px (2) | #13334C, filete 3px #00D9E8, raio 0px (2) |
| callout div.note (fundo, filete esquerdo, raio) | #3C2E39, filete 3px #FFBE72, raio 0px (5) | #3C2E39, filete 3px #FFBE72, raio 0px (5) |
| callout .ato (fundo, filete esquerdo, raio) | #13334C, filete 3px #00D9E8, raio 0px (10); #2F224C, filete 3px #AA71E8, raio 0px (1) | sem fundo, sem filete, raio 0px (11) |
| callout .synth.arm (fundo, filete esquerdo, raio) | #29233F, filete 3px #FF7C87, raio 16px (13) | #29233F, filete 3px #FFBE72, raio 10px (13) |
| `strong` cor tamanho/peso | #7DE8F0 16.5px/650 (16); #7DE8F0 15.6px/650 (9); #F8F5F2 16.5px/650 (6) | #7DE8F0 16.5px/650 (22); #7DE8F0 15.6px/650 (9); #7DE8F0 14.6px/650 (4) |
| `.crit .k` cor tamanho/peso | #7DE8F0 11.5px/600 (13); #7DE8F0 14.6px/600 (10); #7DE8F0 14.3px/600 (5) | #B8B3CC 11.5px/650 (13); #F8F5F2 14.6px/600 (10); #7DE8F0 14.3px/600 (5) |
| `.dnum` cor tamanho/peso | #AA71E8 42px/300 (27); #AA71E8 13px/300 (1) | #BE95F0 42px/300 (27); #BE95F0 13px/300 (1) |
| `.eye` cor tamanho/peso | #9C96B6 14px/500 (42) | #9C96B6 14px/500 (42) |
| `h4.sub` cor tamanho/peso | #F8F5F2 14px/600 (6); #F8F5F2 14.5px/600 (1) | #F8F5F2 14px/600 (6); #F8F5F2 14.5px/600 (1) |
| `h3.sub` cor tamanho/peso | #7DE8F0 16px/650 (2) | #F8F5F2 16px/650 (2) |
| `.trap .albl` cor tamanho/peso | #FFB3BA 13.5px/650 (16); #FFB3BA 10.5px/700 (4); #FFB3BA 16px/650 (1) | #FFBE72 13.5px/650 (16); #FFBE72 10.5px/700 (4); #FFBE72 16px/650 (1) |
| texto em ciano / lavanda / branco (de 16838 elementos) | 22% / 43% / 19% | 16% / 46% / 22% |
| altura média do cabeçalho a 390 px (EN / ER / RS) | 738 / 869 / 296 | 779 / 888 / 294 |
| caixas/bordas na zona do cabeçalho, média (EN / ER) | 14.7 / 14.0 | 14.7 / 14.0 |
| resumo-amostra: `pre` / `strong` | "Atkinson Hyperlegible / #7DE8F0 | "Atkinson Hyperlegible / #7DE8F0 |

## Apêndice A. Matriz por aula

`wrap` = `max-width` do `.wrap` na própria aula; `deg/sec` = nº de `.degrau` (ou `.sec`); `cab.390` = altura do cabeçalho a 390 px com a camada; `car.704` = caracteres por linha aproximados do 1º parágrafo a 704 px com a camada.

| aula | fam. | KB | regras CSS | wrap | main | deg/sec | trap | banca | aside | tabelas | style= | tokens extras | cab.390 | car.704 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| anemias-macrociticas | EN | 39 | 125 | 780px | - | 13 | 4 | 2 | 0 | 0 | 3 | --cols | 646 | 81 |
| aorta-cardiomiopatias-pericardio | EN | 56 | 92 | 780px | - | 26 | 14 | 4 | 0 | 0 | 0 | - | 620 | 81 |
| autopsia-uerj-2021 | AU | 292 | 121 | 820px | - | 0 | 0 | 0 | 0 | 0 | 0 | --accent, --accent-ink, --accent-soft, --bg, --body, --display, --ink-2, --marcada, --marcada-soft, --mark, --mono, --muted, --rule, --rule-2, --surface, --surface-2, --warn, --warn-soft | 382 | 81 |
| cronicas-aps-metas | EN | 46 | 118 | 780px | - | 12 | 3 | 2 | 0 | 0 | 0 | - | 936 | 81 |
| dmg | ER | 46 | 130 | 1180px | sim | 11 | 6 | 0 | 2 | 0 | 3 | --sh | 680 | 74 |
| dossie-uerj | DO | 107 | 78 | 760px | - | 12 | 0 | 0 | 0 | 26 | 0 | - | 410 | 81 |
| glomerulopatias | ER | 39 | 138 | 1180px | sim | 6 | 2 | 2 | 2 | 6 | 1 | - | 886 | 74 |
| iamcsst | EN | 45 | 125 | 780px | - | 14 | 2 | 5 | 0 | 0 | 8 | --cols | 620 | 81 |
| idoso-amg-polifarmacia | EN | 58 | 130 | 780px | - | 17 | 5 | 6 | 0 | 0 | 0 | - | 982 | 81 |
| imagem-obstetrica | EN | 78 | 141 | 780px | - | 13 | 4 | 1 | 0 | 0 | 0 | - | 955 | 81 |
| insuficiencia-adrenal | EN | 34 | 125 | 780px | - | 11 | 3 | 2 | 0 | 0 | 3 | --cols | 643 | 81 |
| kawasaki | ER | 43 | 140 | 1180px | sim | 10 | 1 | 1 | 1 | 1 | 0 | - | 1100 | 74 |
| mccp-decisao-compartilhada | EN | 34 | 118 | 780px | - | 9 | 5 | 1 | 0 | 0 | 0 | - | 908 | 81 |
| neuromusculares | ER | 48 | 113 | 1180px | sim | 13 | 3 | 2 | 1 | 3 | 6 | --acc, --acc-ink, --acc-wash, --i | 1033 | 74 |
| oncohemato-cronicas | EN | 42 | 125 | 780px | - | 14 | 2 | 1 | 0 | 0 | 6 | --cols | 682 | 81 |
| prevencao-quaternaria | ER | 28 | 123 | 1180px | sim | 7 | 2 | 0 | 0 | 0 | 3 | --sh | 756 | 74 |
| rastreamento-programas-br | EN | 39 | 118 | 780px | - | 10 | 2 | 3 | 0 | 0 | 0 | - | 881 | 81 |
| rd-cir-0610 | RS | 15 | 67 | 760px | - | 5 | 4 | 0 | 0 | 0 | 0 | - | 281 | 81 |
| rd-cm-0610 | RS | 16 | 67 | 760px | - | 6 | 7 | 0 | 0 | 0 | 0 | - | 335 | 81 |
| rd-dii-polipos | RG | 15 | 67 | 760px | sim | 9 | 0 | 0 | 0 | 0 | 0 | - | 269 | 74 |
| rd-dm-cronicas | RS | 15 | 67 | 760px | - | 8 | 3 | 0 | 0 | 0 | 0 | - | 326 | 81 |
| rd-go-0610 | RS | 11 | 67 | 760px | - | 4 | 2 | 0 | 0 | 0 | 0 | - | 281 | 81 |
| rd-hemostasia-2 | RS | 12 | 67 | 760px | - | 5 | 3 | 0 | 0 | 0 | 0 | - | 263 | 81 |
| rd-hemostasia | RG | 21 | 123 | 760px | sim | 7 | 1 | 0 | 0 | 2 | 0 | --sh | 357 | 74 |
| rd-hepato | RG | 19 | 67 | 760px | sim | 10 | 0 | 0 | 0 | 0 | 0 | - | 269 | 74 |
| rd-hernias | RS | 22 | 97 | 760px | - | 7 | 3 | 0 | 0 | 0 | 0 | - | 362 | 81 |
| rd-intensiva-sepse | RG | 16 | 67 | 760px | sim | 9 | 0 | 0 | 0 | 0 | 0 | - | 269 | 74 |
| rd-lupus-saf | RG | 20 | 123 | 760px | sim | 7 | 0 | 0 | 0 | 3 | 0 | --sh | 330 | 74 |
| rd-meningites | RS | 16 | 67 | 760px | - | 8 | 2 | 0 | 0 | 1 | 0 | - | 281 | 81 |
| rd-neoplasias-tgi | RS | 17 | 67 | 760px | - | 8 | 3 | 0 | 0 | 2 | 0 | - | 299 | 81 |
| rd-ortopedia-cirurgia | RS | 17 | 58 | 760px | - | 9 | 0 | 0 | 0 | 5 | 0 | - | 317 | 81 |
| rd-ped-0610 | RS | 12 | 67 | 760px | - | 5 | 3 | 0 | 0 | 0 | 0 | - | 290 | 81 |
| rd-pediatria | RS | 16 | 58 | 760px | - | 9 | 0 | 0 | 0 | 3 | 0 | - | 290 | 81 |
| rd-pilulas-0510 | RS | 20 | 67 | 760px | - | 9 | 1 | 0 | 0 | 0 | 0 | - | 281 | 86 |
| rd-pilulas | RS | 19 | 58 | 760px | - | 12 | 0 | 0 | 0 | 3 | 0 | - | 254 | 81 |
| rd-ventilacao-degrau-0 | RG | 25 | 104 | 760px | sim | 7 | 1 | 0 | 1 | 0 | 1 | - | 392 | 74 |
| rd-vias-biliares | RG | 23 | 123 | 760px | sim | 8 | 0 | 0 | 0 | 3 | 0 | --sh | 280 | 74 |
| remit-cicatrizacao | EN | 41 | 95 | 780px | - | 17 | 9 | 5 | 0 | 0 | 0 | - | 540 | 81 |
| rodapes-retorno-alto | EN | 46 | 113 | 780px | - | 7 | 7 | 2 | 0 | 0 | 0 | - | 606 | 81 |
| tb-360 | EN | 57 | 122 | 780px | - | 20 | 5 | 3 | 0 | 0 | 0 | - | 895 | 81 |
| tireoide-nodulo-cancer | EN | 41 | 129 | 780px | - | 14 | 0 | 2 | 0 | 0 | 0 | - | 612 | 81 |
| topicos-pediatria | ER | 52 | 123 | 1180px | sim | 11 | 6 | 4 | 1 | 0 | 4 | --sh | 759 | 74 |
| vulva-vagina-anatomia | EN | 40 | 99 | 780px | - | 13 | 0 | 3 | 0 | 0 | 0 | - | 550 | 81 |

## Apêndice B. Todas as classes usadas por 2 ou mais aulas (101), por papel

| papel | classe | aulas | ocorr. | tags | fam. | nota |
|---|---|---|---|---|---|---|
| layout | `.wrap` | 43 | 43 | div 43 | EN15 ER6 RS13 RG7 DO1 AU1 | contêiner único da página (`div.wrap`) |
| layout | `.body` | 6 | 6 | div 6 | ER6 | `div.body` grade trilho+main |
| cabeçalho | `.eye` | 42 | 42 | p 42 | EN15 ER6 RS13 RG7 DO1 | `p.eye` |
| cabeçalho | `.top` | 42 | 42 | header 42 | EN15 ER6 RS13 RG7 DO1 | `header.top` |
| cabeçalho | `.stat` | 21 | 90 | div 90 | EN15 ER3 RG3 | um número-chave (`b` + `span`) |
| cabeçalho | `.stats` | 21 | 21 | div 21 | EN15 ER3 RG3 | faixa de números-chave |
| cabeçalho | `.tn` | 3 | 15 | span 15 | ER3 | rótulo no `.spec`/`.tl` |
| cabeçalho | `.bar` | 2 | 2 | div 2 | ER1 RG1 | barra da régua (kawasaki) / barra de `.stack` (RD) |
| cabeçalho | `.tl` | 2 | 2 | div 2 | ER2 | grade do cabeçalho (prevenção, tópicos) |
| navegação | `.nav` | 16 | 16 | nav 16 | EN15 RG1 | `nav.nav` chips de âncora |
| navegação | `.rail` | 6 | 6 | nav 6 | ER6 | trilho lateral |
| navegação | `.rlab` | 6 | 6 | p 6 | ER6 | rótulo do trilho |
| navegação | `.rn` | 6 | 67 | span 67 | ER6 | número no link do trilho |
| degrau | `.degrau` | 28 | 325 | section 325 | EN15 ER6 RG7 | `section.degrau` |
| degrau | `.dhead` | 28 | 325 | div 325 | EN15 ER6 RG7 | cabeça do degrau |
| degrau | `.dnum` | 28 | 325 | span 319, div 6 | EN15 ER6 RG7 | número do degrau |
| degrau | `.dtitle` | 28 | 325 | div 325 | EN15 ER6 RG7 | título + etapa |
| degrau | `.kick` | 14 | 107 | span 107 | RS13 DO1 | rótulo acima do h2 (RD-sec) |
| degrau | `.sec` | 14 | 107 | section 107 | RS13 DO1 | `section.sec` |
| degrau | `.dstage` | 13 | 115 | span 115 | ER6 RG7 | etapa ('Degrau 2 - diagnóstico') |
| degrau | `.ato` | 11 | 37 | div 37 | EN11 | faixa de ato |
| degrau | `.blk` | 5 | 38 | div 33, details 5 | RS4 DO1 | bloco curto (RD-sec) / acordeão (dossiê) |
| texto | `.sub` | 43 | 123 | details 44, p 42, h4 24 | EN15 ER6 RS13 RG7 DO1 AU1 | `p.sub` no cabeçalho (42); `h3.sub` 13 e `h4.sub` 24 (sub-títulos); `details.sub` 44 (autópsia) |
| texto | `.lede` | 41 | 357 | p 357 | EN15 ER6 RS12 RG7 DO1 | frase de abertura de cada degrau/seção |
| texto | `.prose` | 28 | 298 | div 298 | EN15 ER6 RG7 | bloco de pontos do degrau |
| texto | `.src` | 23 | 219 | span 154, p 65 | EN12 ER1 RS10 | fonte da seção |
| texto | `.pt` | 14 | 138 | ul 131, ol 7 | RS13 DO1 | `ul.pt` lista de pontos (RD-sec/dossiê) |
| texto | `.cap` | 3 | 5 | p 4, span 1 | EN1 ER1 RG1 | legenda de tabela/cadeia |
| texto | `.mn` | 3 | 74 | span 74 | ER2 DO1 | número em mono (`span.mn`) |
| texto | `.ar` | 2 | 68 | span 68 | EN1 DO1 | seta '->' em item de lista |
| texto | `.hint` | 2 | 3 | p 3 | ER2 | dica 'role a tabela' |
| callout | `.trap` | 31 | 118 | div 118 | EN13 ER6 RS10 RG2 | armadilha (carmine) |
| callout | `.albl` | 23 | 157 | div 151, p 6 | EN15 ER6 RG2 | rótulo do callout |
| callout | `.note` | 20 | 35 | p 30, div 5 | EN15 RS5 | `div.note` (amber, RD-sec) ou `p.note` (legenda da síntese) |
| callout | `.banca` | 19 | 51 | div 51 | EN15 ER4 | como cai na banca (amber) |
| callout | `.aside` | 6 | 8 | div 8 | ER5 RG1 | nota (teal) |
| callout | `.ff` | 3 | 10 | span 10 | EN3 | etiqueta em linha 'fora da apostila' |
| callout | `.key` | 3 | 18 | p 12, div 6 | ER1 RS1 DO1 | `div/p.key` (teal, RD-sec e dossiê); `div.row.key` na kawasaki é linha de tabela |
| callout | `.fonte` | 2 | 2 | p 1, div 1 | EN1 DO1 | `div.fonte` (vulva) / `p.fonte` (cabeçalho do dossiê) |
| callout | `.star` | 2 | 2 | div 2 | ER2 | caixa neutra com rótulo cinza |
| callout | `.warn` | 2 | 14 | span 13, div 1 | ER1 AU1 | `pill.warn` (autópsia) / `flow.warn` (dmg) |
| diagrama | `.k` | 38 | 1395 | span 1032, p 358, div 5 | EN15 ER6 RS9 RG7 AU1 | chave: linhas de `.crit`, `details.ref .row`, `.tile` (autópsia) |
| diagrama | `.v` | 38 | 1409 | span 1400, div 5, p 4 | EN15 ER6 RS9 RG7 AU1 | valor da mesma linha |
| diagrama | `.crit` | 37 | 190 | div 190 | EN15 ER6 RS9 RG7 | grade de critérios (CSS grid) |
| diagrama | `.row` | 37 | 1043 | div 1043 | EN15 ER6 RS9 RG7 | linha de `.crit`/`details.ref` |
| diagrama | `.vs` | 36 | 186 | p 101, div 85 | EN12 ER5 RS10 RG7 DO1 AU1 | comparação em 2 colunas |
| diagrama | `.a` | 35 | 84 | div 84 | EN12 ER5 RS10 RG7 DO1 | lado A do `.vs` (carmine) |
| diagrama | `.b` | 35 | 86 | div 86 | EN12 ER5 RS10 RG7 DO1 | lado B do `.vs` (teal) |
| diagrama | `.arm` | 28 | 123 | div 110, section 13 | EN13 ER6 RS3 RG6 | `div.arm` = item de armadilha; `section.arm` = síntese de armadilhas |
| diagrama | `.n` | 24 | 109 | span 109 | EN7 RS13 RG4 | número do item (`.miss .n`, `.trilho .n`, `.elos .n`, `.rail .rn` é outra classe) |
| diagrama | `.synth` | 21 | 36 | section 36 | EN15 ER6 | síntese |
| diagrama | `.tk` | 21 | 301 | span 301 | EN15 ER6 | chave do gatilho |
| diagrama | `.trig` | 21 | 21 | div 21 | EN15 ER6 | grade de gatilhos |
| diagrama | `.tv` | 21 | 306 | span 306 | EN15 ER6 | valor do gatilho (`.trig .tv`; `.spec .tv`/`.tl .tv` no cabeçalho) |
| diagrama | `.hd` | 18 | 98 | div 98 | EN14 ER3 RG1 | modificador `.crit.hd`: 1ª linha é cabeçalho |
| diagrama | `.arms` | 15 | 15 | div 15 | ER6 RS3 RG6 | lista de armadilhas |
| diagrama | `.c3` | 15 | 54 | div 53, span 1 | EN11 ER3 RG1 | modificador `.crit.c3`: 3 colunas |
| diagrama | `.dot` | 15 | 110 | span 110 | ER6 RS3 RG6 | bolinha carmine do item |
| diagrama | `.ref` | 15 | 36 | details 36 | EN9 ER5 RG1 | `details.ref` |
| diagrama | `.refbody` | 14 | 35 | div 35 | EN9 ER5 | corpo do `details.ref` |
| diagrama | `.d` | 13 | 161 | span 161 | EN12 AU1 | referência de degrau ('D2') mono em `ol.armas li`; `.leit .d` na autópsia |
| diagrama | `.mal` | 13 | 101 | div 53, span 48 | EN12 DO1 | `span.v.mal`: célula-valor em carmine-ink 600 (EN); `div.mal` do dossiê |
| diagrama | `.miss` | 13 | 13 | ul 13 | RS13 | `ul.miss` onde tropeçou |
| diagrama | `.armas` | 12 | 12 | ol 12 | EN12 | `ol.armas`: lista numerada de armadilhas da síntese |
| diagrama | `.t` | 10 | 35 | span 27, table 8 | EN7 RG3 | `span.t` texto do passo; `table.t` (RD) |
| diagrama | `.ext` | 7 | 9 | div 9 | EN6 ER1 | faixa de fatos-chave em grid (7 aulas); na dmg é callout |
| diagrama | `.fk` | 7 | 42 | span 42 | EN6 ER1 | legenda do fato |
| diagrama | `.fv` | 7 | 42 | span 42 | EN6 ER1 | valor do fato |
| diagrama | `.trilho-box` | 7 | 7 | div 7 | EN7 | caixa da trilha |
| diagrama | `.trilho` | 7 | 7 | ol 7 | EN7 | `ol.trilho` passos |
| diagrama | `.tot` | 6 | 8 | div 8 | EN6 | fato-total (cor carmine) |
| diagrama | `.hot` | 5 | 32 | div 31, span 1 | EN4 ER1 | linha/célula quente (`.gr.hot`, `.bar span.hot`) |
| diagrama | `.elos` | 4 | 4 | ul 4 | RG4 | lista de elos (RD-degrau) |
| diagrama | `.flow` | 4 | 9 | div 9 | EN1 ER3 | fluxo (4 implementações) |
| diagrama | `.gc` | 4 | 211 | span 211 | EN4 | célula do `.grade` |
| diagrama | `.gh` | 4 | 20 | div 20 | EN4 | cabeçalho do `.grade` |
| diagrama | `.gk` | 4 | 98 | span 98 | EN4 | chave do `.grade` |
| diagrama | `.gr` | 4 | 118 | div 118 | EN4 | linha do `.grade` |
| diagrama | `.grade` | 4 | 20 | div 20 | EN4 | tabela por grid + `--cols` inline |
| diagrama | `.c` | 3 | 19 | span 19 | EN1 ER1 AU1 | chip numérico (`span.c`) / caixa de `.chain .c` / contador `.leit .c` na autópsia |
| diagrama | `.chain` | 3 | 4 | ol 3, ul 1 | EN3 | cadeia causal |
| diagrama | `.passo` | 3 | 3 | ol 3 | EN3 | `ol.passo` passos |
| diagrama | `.c4` | 2 | 5 | div 5 | EN2 | modificador `.crit.c4`: 4 colunas |
| diagrama | `.passos` | 2 | 2 | ol 2 | EN2 | `ol.passos` passos |
| tabela | `.tw` | 12 | 57 | div 57 | ER3 RS5 RG3 DO1 | contêiner de tabela com rolagem |
| tabela | `.hi` | 6 | 18 | td 18 | ER1 RS5 | `td.hi` célula destacada |
| tabela | `.num` | 3 | 195 | td 181, span 9, p 4 | ER1 DO1 AU1 | `td.num` numérico; `p.v.num` na autópsia |
| tabela | `.tblw` | 3 | 8 | div 8 | RG3 | contêiner de tabela (RD-degrau) |
| tabela | `.grp` | 2 | 9 | tr 5, h3 4 | ER1 RG1 | linha/título de grupo |
| RD | `.q` | 17 | 201 | div 157, details 44 | RS13 RG3 AU1 | `div.q` pergunta (RD); `details.q` na autópsia |
| RD | `.qs` | 16 | 16 | div 16 | RS13 RG3 | lista de perguntas |
| RD | `.tag` | 14 | 221 | span 221 | RS13 AU1 | `.q .tag` etiqueta mono; `li.elo .tag` na autópsia |
| RD | `.qa` | 4 | 36 | div 36 | RG4 | pergunta+resposta |
| RD | `.qq` | 4 | 36 | p 36 | RG4 | texto da pergunta do `.qa` |
| RD | `.ql` | 3 | 30 | span 30 | RG3 | rótulo 'Elo n' do `.q` |
| RD | `.tgrp` | 3 | 16 | div 16 | RG3 | grupo de teste |
| injetado | `.pend-item` | 2 | 24 | li 24 | RS1 AU1 | item do formulário |
| injetado | `.pend-lista` | 2 | 3 | ol 3 | RS1 AU1 | lista |
| injetado | `.pend-pe` | 2 | 68 | div 68 | RS1 AU1 | rodapé do formulário |
| injetado | `.pend-q` | 2 | 24 | p 24 | RS1 AU1 | enunciado da pergunta |
| injetado | `.pend` | 2 | 68 | form 68 | RS1 AU1 | formulário de pergunta (`form.pend`) já no HTML |

## Apêndice C. Classes exclusivas de uma aula (173 no total)

| aula | fam. | nº | classes |
|---|---|---|---|
| autopsia-uerj-2021 | AU | 48 | `.alts`, `.at`, `.blocos`, `.busca`, `.cadeia`, `.card`, `.certa`, `.chip`, `.conta`, `.cortado`, `.ctx`, `.elo`, `.enun`, `.f`, `.fila`, `.filtros`, `.fr`, `.grupo`, `.leit`, `.linha`, `.lista-q`, `.marc`, `.muted`, `.nota`, `.nota-box`, `.obrig`, `.on`, `.pend-coment`, `.pend-conta`, `.pend-opc`, `.pend-opc-tit`, `.perg`, `.pill`, `.qb`, `.qm`, `.qn`, `.qt`, `.qtema`, `.r-anulada`, `.r-chute-certo`, `.r-duvida-certa`, `.r-errou`, `.res`, `.risc`, `.tile` +3 |
| dossie-uerj | DO | 12 | `.bd`, `.blks`, `.blks-lede`, `.gesto`, `.in`, `.mais`, `.mal-h`, `.mals`, `.nw`, `.onde`, `.rt`, `.sg` |
| glomerulopatias | ER | 15 | `.c34`, `.cmap`, `.cn`, `.if3`, `.k3`, `.k34`, `.kn`, `.s-aua`, `.s-cron`, `.s-gnrp`, `.s-nefri`, `.s-nefro`, `.spec`, `.w7`, `.why` |
| iamcsst | EN | 1 | `.e4` |
| idoso-amg-polifarmacia | EN | 1 | `.x` |
| imagem-obstetrica | EN | 42 | `.fig`, `.mgrid`, `.mini`, `.minis`, `.sv-action`, `.sv-alert`, `.sv-amb`, `.sv-axis`, `.sv-back`, `.sv-bad`, `.sv-band`, `.sv-circ`, `.sv-dash`, `.sv-dot-c`, `.sv-fetus`, `.sv-fhr`, `.sv-font-b`, `.sv-font-l`, `.sv-grid`, `.sv-head`, `.sv-hodge`, `.sv-hodge0`, `.sv-ink`, `.sv-lead`, `.sv-pelvis`, `.sv-rot`, `.sv-rot-h`, `.sv-skull`, `.sv-spine`, `.sv-strip`, `.sv-t`, `.sv-ta`, `.sv-tb`, `.sv-tc`, `.sv-tm`, `.sv-trend`, `.sv-trend2`, `.sv-tri`, `.sv-tt`, `.sv-uc`, `.sv-uterus`, `.sv-wall` |
| kawasaki | ER | 15 | `.arrow`, `.bh`, `.br`, `.branches`, `.cols`, `.cream`, `.fever`, `.foot`, `.fora`, `.h`, `.lt`, `.node`, `.red`, `.ruler`, `.start` |
| neuromusculares | ER | 7 | `.ak`, `.an`, `.av`, `.axis`, `.fx`, `.out`, `.w8` |
| rd-ventilacao-degrau-0 | RG | 14 | `.b-dp`, `.b-pk`, `.b-pl`, `.brk`, `.brow`, `.eq`, `.s-ela`, `.s-peep`, `.s-res`, `.seg`, `.stack`, `.t1`, `.t2`, `.t3` |
| remit-cicatrizacao | EN | 3 | `.dir`, `.dn`, `.up` |
| rodapes-retorno-alto | EN | 2 | `.disc`, `.r` |
| tb-360 | EN | 5 | `.esc`, `.escada`, `.g`, `.neg`, `.p` |
| tireoide-nodulo-cancer | EN | 7 | `.beth`, `.bn`, `.cd`, `.nm`, `.r2`, `.r3`, `.rk` |
| vulva-vagina-anatomia | EN | 1 | `.arml` |

## Apêndice D. Método e como reproduzir

Nada no repositório foi alterado. Os scripts vivem no scratchpad da sessão (`C:/Users/daanm/AppData/Local/Temp/claude/C--Users-daanm-medhub/9cb414e8-6bd6-439e-b351-7d1ab0d4db70/scratchpad/`); este `.md` é gerado por `gen_md.py` a partir deles. Rodar de novo: `python -B -X utf8 run_all.py` e depois `python -B -X utf8 gen_md.py` (com `serve.py` ligado em 127.0.0.1:8765).

- `common.py`: parser de HTML por `html.parser` (`BodyParser`: tag, classes, pai, texto; todas as aulas fecham todas as tags) e parser simples de CSS (blocos aninhados, `@media`; regex só para CSS); dobra de regras por especificidade/ordem (`fold`, `rules_matching`) para o 'CSS efetivo' de cada componente (ignora `@media`, pseudo-elementos e regras de ancestral).
- `build_harness.py`: replica o injetor do hub (`comTema`/`documentoCompleto` de `core/templates/hub.html`) em 4 variantes por aula: `v3` (BASE: `tema.css` v3 do working tree + `tema-aula.css` do commit def2fdd), `v24` (os dois do commit BASE def2fdd), `wip` (os dois do working tree = camada reescrita, só para o §15) e `raw` (sem camada). Mais uma página-amostra de resumo montada com o `CSS_RESUMO` real (extraído por `ast`, sem importar `tools/hub.py`).
- `harness/m.html`, `casc.html`, `sel.html` + `run_edge.py`: Edge headless (`msedge --headless=new --virtual-time-budget --dump-dom`) lendo o harness servido por `serve.py` (http.server sem cache em 127.0.0.1) em iframes de 390 px, 704 px e 1000 px (largura útil real, sem barra de rolagem). `m.html` mede overflow, contêineres cortados, estilos computados de ~100 sondas, censo de cor do texto e a zona do cabeçalho; `casc.html` calcula, por elemento, QUEM vence cada declaração da camada (aula x camada, especificidade + ordem + !important, `matchMedia` real); `sel.html` conta os elementos que cada seletor das camadas casa em cada aula.
- `run_all.py`: refaz tudo (snapshot dos arquivos de tema + `git show def2fdd:`, harness, medições Edge; poucos minutos). A Atkinson é carregada do Google Fonts (a máquina estava online; confirmado `FontFace.status == loaded` nas faces latinas).
- Limites: 'CSS efetivo' dos §6-7 olha só regras de nível raiz; `a.on` do trilho é posto por JS e não foi observado; a largura de texto usa o 1º `.lede`/`li`/`p` de cada aula (aproximação por largura média de caractere); tema claro não medido; o Edge headless reporta `prefers-color-scheme:dark`, por isso a página crua do resumo aparece na paleta escura do `CSS_RESUMO`; a camada do working tree (§15) é um alvo móvel.
