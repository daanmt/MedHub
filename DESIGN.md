---
name: MedHub
description: Hub de estudo para a residência (UERJ, 01/11/2026) — tema v4 "fosco em camadas", escuro por padrão, lido no celular à noite.
colors:
  papel: "#0C0C12"
  card: "#15151E"
  afundado: "#1E1D2A"
  linha: "#2B2A3A"
  borda-placa: "#3A3852"
  trilho: "#312F49"
  linha-forte: "#6E6A8A"
  tinta: "#F6EFEA"
  tinta2: "#BDB7CC"
  tinta3: "#948FAA"
  acento: "#00D9E8"
  acento-tinta: "#7DE8F0"
  acento-fraco: "#0E2B36"
  rosa: "#FF4FA3"
  rosa-fraco: "#33172C"
  roxo: "#AA71E8"
  roxo-tinta: "#BE95F0"
  roxo-fraco: "#261C3E"
  amarelo: "#FFD447"
  fc: "#FF5FAE"
  fc-fraco: "#55204A"
  fc-tinta: "#FF9ACB"
  ok: "#79D6A5"
  ok-fraco: "#172A26"
  erro: "#FF7C87"
  erro-fraco: "#331B24"
  aviso: "#FFBE72"
  aviso-fraco: "#33261C"
  sobre: "#0C0C12"
  amber-ink: "#FFD3A0"
  carmine-ink: "#FFB3BA"
  cromado-azul: "#2F7BFF"
  cromado-violeta: "#7A4DFF"
  cromado-magenta: "#B04FE0"
typography:
  numero:
    fontFamily: "Atkinson Hyperlegible Next, ui-sans-serif, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    fontFeature: "tnum"
  pagina:
    fontFamily: "Atkinson Hyperlegible Next, ui-sans-serif, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "1.5rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-.02em"
  secao:
    fontFamily: "Atkinson Hyperlegible Next, ui-sans-serif, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "1.125rem"
    fontWeight: 650
    lineHeight: 1.3
  item:
    fontFamily: "Atkinson Hyperlegible Next, ui-sans-serif, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.35
  corpo:
    fontFamily: "Atkinson Hyperlegible Next, ui-sans-serif, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "clamp(15px, .95rem + .2vw, 17px)"
    fontWeight: 400
    lineHeight: 1.55
    fontFeature: "tnum"
  leitura:
    fontFamily: "Atkinson Hyperlegible Next, ui-sans-serif, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.65
  legenda:
    fontFamily: "Atkinson Hyperlegible Next, ui-sans-serif, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: ".875rem"
    fontWeight: 400
  meta:
    fontFamily: "Atkinson Hyperlegible Next, ui-sans-serif, system-ui, Segoe UI, Roboto, sans-serif"
    fontSize: ".8125rem"
    fontWeight: 650
rounded:
  placa: "14px"
  raio: "10px"
  raio-p: "6px"
  pilula: "999px"
spacing:
  esp-1: "4px"
  esp-2: "8px"
  esp-3: "12px"
  esp-4: "16px"
  esp-5: "24px"
  esp-6: "32px"
  esp-7: "48px"
  wrap: "46rem"
  largura: "72rem"
components:
  placa:
    backgroundColor: "{colors.card}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.placa}"
    padding: "16px"
  placa-desktop:
    backgroundColor: "{colors.card}"
    rounded: "{rounded.placa}"
    padding: "24px"
  botao-primario:
    backgroundColor: "{colors.acento}"
    textColor: "{colors.sobre}"
    rounded: "{rounded.raio}"
    padding: "0 16px"
    height: "44px"
  botao-primario-hover:
    backgroundColor: "{colors.acento-tinta}"
    textColor: "{colors.sobre}"
  botao-ciano:
    backgroundColor: "transparent"
    textColor: "{colors.acento-tinta}"
    rounded: "{rounded.raio}"
    padding: "0 16px"
    height: "44px"
  botao-ciano-hover:
    backgroundColor: "{colors.acento-fraco}"
    textColor: "{colors.acento-tinta}"
  botao-neutro:
    backgroundColor: "transparent"
    textColor: "{colors.tinta}"
    rounded: "{rounded.raio}"
    padding: "10px 16px"
    height: "44px"
  botao-neutro-hover:
    backgroundColor: "{colors.afundado}"
  botao-compacto:
    rounded: "{rounded.raio-p}"
    padding: "4px 12px"
    height: "36px"
  chip-area:
    backgroundColor: "{colors.rosa-fraco}"
    textColor: "{colors.rosa}"
    rounded: "{rounded.pilula}"
    padding: "1px 8px"
  badge:
    backgroundColor: "{colors.afundado}"
    textColor: "{colors.tinta2}"
    rounded: "{rounded.pilula}"
    padding: "1px 8px"
  chip-em-curso:
    backgroundColor: "{colors.aviso-fraco}"
    textColor: "{colors.aviso}"
    rounded: "{rounded.pilula}"
  chip-resolvida:
    backgroundColor: "{colors.ok-fraco}"
    textColor: "{colors.ok}"
    rounded: "{rounded.pilula}"
  card-player:
    backgroundColor: "{colors.afundado}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.placa}"
    padding: "16px"
  tarefa:
    backgroundColor: "{colors.afundado}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.raio}"
    padding: "8px 16px 8px 20px"
  alternativa:
    backgroundColor: "{colors.card}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.raio}"
    padding: "12px"
  aviso:
    backgroundColor: "{colors.aviso-fraco}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.raio-p}"
    padding: "12px 16px"
---

# Design System: MedHub

> Fonte ÚNICA das regras visuais do MedHub (desde 19/10/2026, s231; antes em `docs/UI.md`, criado na s225 em 13/10/2026,
> hoje só ponteiro para cá). Os tokens moram SÓ em `core/templates/tema.css`: o frontmatter acima é o espelho legível
> deles (escuro, o padrão) e, se divergir, vale o `tema.css`. Regra que muda aqui muda junto no código e no teste que a
> trava ("Contratos travados por teste", abaixo). Memória do harness sobre UI é só ponteiro para este arquivo.

## Overview

**Creative North Star: "O Controle Fosco"**

O tema v4, **fosco em camadas** (s227, 13/10/2026), é o retrowave do v3 lido do controle DualSense GTA VI que ele trouxe
como referência ("o exemplo que mais se aproxima"): o corpo preto fosco é o fundo; o cromado azul → violeta é a luz
(atrás do topo) e o fio de 1 px que acende o topo de cada placa, nunca uma superfície; os símbolos rosa são o detalhe
(marca, etiquetas, o anel de cards); o texto é branco quente. Queixa que o v4 resolve, nas palavras dele: *"ainda muito
'chapado' no fundo, sem blocos e divisões, fluidez e coesão, otimização do espaço"*. PRD:
`.vibeflow/prds/hub-tema-v4-fosco-em-camadas.md` (specs `hub-tema-v4-part-1..4`).

Princípio que segue do v3 (brief dele, 13/10/2026): *"a interface deve lembrar Vice City à primeira vista, mas
desaparecer em segundo plano quando o estudante estiver concentrado no conteúdo."* É uma superfície de **operar e ler**
(Painel, Listas, Cards = tarefa; Teoria = leitura): a ambição aparece como precisão e contenção, não como espetáculo.
Prioridade, nesta ordem: (1) clareza e baixa carga cognitiva; (2) legibilidade e acessibilidade; (3) hierarquia e
consistência entre telas; (4) minimalismo funcional; (5) identidade retrowave deliberada e contida; (6) código simples.

Ele lê **no celular (390 px), à noite, entre plantões**. Toda decisão é conferida primeiro a 390 px. A identidade mora em
poucos lugares: a marca (`Med` + `Hub` em ciano, s226), a **linha do horizonte** sob as abas (rosa → roxo → ciano), a
**luz** atrás do topo e o **fio cromado** das placas (azul → violeta), e o roxo do gráfico de previsão do Painel. O resto
é tipografia, superfície, filete e espaço. Rejeições confirmadas por ele: glow, sombra, halo, borda neon (os mockups com
borda neon ficaram de fora em 13/10), caixa-alta, micro-dicas de interação óbvia. Ele muda de ideia rápido: trocar a
paleta é trocar os dois blocos de cor do `tema.css`; nada além disso deve ser preciso.

⚰️ *13/10/2026 (s227, tema v4): era "a linha do horizonte sob as abas (o único gradiente da UI: rosa → roxo → ciano)". O
v4 acrescentou dois gradientes de material (`--luz`, `--cromado`); nenhum deles é cor de dado nem fundo de texto.*

**Key Characteristics:**
- Preto fosco frio com uma luz azul/violeta fraca no topo; nada brilha.
- Uma placa por SEÇÃO, nunca uma caixa por número; dentro dela, linhas com filete.
- Profundidade = degrau de superfície + borda + fio cromado de 1 px.
- Cor com papel fixo: ciano = interação, rosa = marca, âmbar = aviso, roxo = dado/decoração.
- Uma família tipográfica (Atkinson Hyperlegible Next), algarismos tabulares, sem caixa-alta.
- Escuro por padrão; claro só por escolha explícita (`data-theme="light"`).
- Celular primeiro: a 390 px tudo é uma coluna de placas empilhadas.

## Colors

Um preto fosco em degraus de índigo quase neutro, texto em branco quente e quatro neons contidos, cada um com um único
papel. Os valores acima são do tema **escuro** (padrão); o **claro** está na tabela abaixo e no sidecar.

Seletores `:root:not([data-theme="light"]),:root[data-theme="dark"]` (escuro) e `:root[data-theme="light"]` (claro), de
especificidade (0,2,0) de propósito: vencem o `@media` escuro que cada aula traz no próprio CSS. O hub ignora
`prefers-color-scheme: light` de propósito (decisão dele, s224: escuro por padrão; achado A17); o claro foi refeito na
mesma semântica.

### Primary
- **Ciano Gatilho** (`acento`; claro `#00737D`): interação. Navegação ativa (aba, segmento), foco, progresso (barras,
  trilho atual, o "necessário por dia"), ação primária (botão `.primario`), o rótulo "Próxima" do Painel e link. Nunca
  título nem rótulo. `acento-tinta` (claro `#005A62`) é o ciano como texto/hover; `acento-fraco` (claro `#DDF1F4`) é a
  lavagem. Na leitura, o termo-chave em negrito é o ÚNICO texto ciano (pedido dele, s224).

### Secondary
- **Rosa Símbolo** (`rosa`; claro `#C2176F`): a marca e o destaque pontual — os símbolos do controle. Etiqueta "nova" na
  Biblioteca, chip de área (`.t-rot`), banca da questão, botão Defeito do card, anel de Cards, grifo padrão. Nunca
  estado. `rosa-fraco` (claro `#F8E1EE`) é a lavagem.
- **Rosa Flashcard** (`fc` / `fc-fraco` / `fc-tinta`; claro `#C2176F` / `#F2C2DC` / `#9E0F58`): paleta própria do bloco
  Flashcards da semana (s228, pedido dele): pico em barra cheia, lavagem dos outros dias, número em destaque. `fc` ≥ 3:1 e
  `fc-fraco` ≥ 1,3:1 contra a placa; `fc-tinta` ≥ 4,5 como texto (teste do tema).

### Tertiary
- **Roxo Cromado** (`roxo`; claro `#7443B8`): decoração e dado visual (gráfico de previsão, anel Até 01/11, Simulados no
  Por bloco, número do degrau das aulas) e os estados chute/desatenção. Como texto, SEMPRE `roxo-tinta` (claro
  `#5E3596`): o `roxo` puro dá 4,9 sobre o elevado escuro e segue proibido como texto. `roxo-fraco` (claro `#ECE3F8`) é a
  lavagem.
- **Amarelo Marca-texto** (`amarelo`; claro `#FFE066`): só a cor amarela do grifo e a faixa da área GO.

### Estados
- **Verde Sucesso** (`ok` / `ok-fraco`; claro `#1E7348` / `#E2F2E8`): sucesso, gabarito, resolvida, em dia.
- **Coral Erro** (`erro` / `erro-fraco`; claro `#B8303E` / `#FBE5E8`): erro, alternativa errada, o que é proibido (`.mal`).
- **Âmbar Aviso** (`aviso` / `aviso-fraco`; claro `#8F5200` / `#FAEBD7`): aviso e atraso, armadilha (no card e na aula),
  Pausar, ritmo abaixo, bloco mais fraco. Atraso é aviso (âmbar), não erro.

### Neutral
- **Corpo do Controle** (`papel`; claro `#F4F3F8`): fundo da página; leva a `--luz` no topo.
- **Placa Fosca** (`card`; claro `#FFFFFF`): a placa (superfície de seção); fundo da alternativa; assinatura.
- **Degrau Elevado** (`afundado`; claro `#ECEAF3`): superfície elevada/selecionada dentro da placa; card do player;
  cartão de tarefa; badge; trilho vazio do trilho de questões.
- **Filete** (`linha`; claro `#DFDCE8`): filete interno (linha de lista dentro da placa); borda de moldura.
- **Borda da Placa** (`borda-placa`; claro `#C2BCD4`): borda da placa contra o fundo (≥ 1,6:1, s227).
- **Trilho** (`trilho`; claro `#D3CFE1`): trilho vazio de barra e anel sobre a placa (≥ 1,35:1, s227; o `afundado` some
  sobre a placa, 1,1:1).
- **Borda de Controle** (`linha-forte`; claro `#7F7A9C`): borda de campo, botão secundário, frente do card: ≥ 3:1.
- **Branco Quente** (`tinta`; claro `#1A1626`): texto principal, títulos, pergunta, resposta, conteúdo ("pêssego" do brief
  = este branco quente).
- **Lavanda** (`tinta2`; claro `#4A4560`): texto secundário, rótulos. **Lavanda Apagada** (`tinta3`; claro `#5F5A78`):
  metadados.
- **Sobre** (`sobre`; claro `#FFFFFF`): texto sobre preenchimento (botão primário, declaração ligada).

### Gradientes de material (não são cor de dado nem fundo de texto)
- `--cromado`: azul → violeta → magenta (stops `cromado-*`; claro `#2F6BE0` / `#6A3FE0` / `#9A3FC8`), apagado nas pontas
  — o fio de 1 px no topo da placa (reflexo, não faixa).
- `--luz`: duas `radial-gradient` (azul à esquerda, violeta à direita, 20–24% no escuro, 6–7% no claro) — a luz atrás do
  topo (marca e abas). Rola com a página.
- `--horizonte`: rosa → roxo → ciano (claro: os mesmos tons escuros do tema claro) — a linha sob as abas.

### Marca-texto (grifo)
Pinta só o FUNDO (lavagem `--grifo-*` a 32%; 26% no claro, 70% no amarelo do claro) e o texto mantém a cor
(`color:inherit`) — s227, part-6, pedido dele: "poderia apenas manter a cor do texto e mudar o fundo dele". Três cores:
**rosa (padrão), ciano ou amarelo**, a ativa lembrada no aparelho (`medhub.grifo`, `data-grifo` no `:root`). Desde a s228
(pedido dele: "alterando apenas a cor dos próximos grifos, e não todos [...] um botão único, que quando clicamos ele
expande em cascata com as 3 opções"): a cor ativa vale só para os PRÓXIMOS grifos. Cada grifo guarda a cor com que
nasceu (`cor` no registro de `analises/grifos/itens/<slug>`, gravada só quando não é rosa; grifo antigo sem `cor` segue
rosa), é pintado por `mark.hub-grifo[data-cor]` e nunca muda quando a ativa troca; grifos de cores diferentes não se
fundem. `--qz-grifo` / `--qz-grifo-tinta` ficam como token porque o hub lê o valor computado para o leitor.
⚰️ *s227 (part 6): "uma cor ativa vale para todos os grifos", 3 botões no topo do hub; o leitor aberto repintava.*
⚰️ *13/10/2026 (s227): era "**Amarelo**: marca-texto (grifo)", com o texto escuro sobre o amarelo cheio.*

### Escalas de estado
- A declaração dos elos (`Sim / Incerteza / Desatenção / Não`) e a nota do card (`1 falhei / 2 com esforço / 3 lembrei
  / 4 sem esforço`) seguem a mesma escala: ok, aviso, roxo, erro / erro, aviso, ok, acento.
- Certeza da questão: sólida = ciano, dúvida = âmbar, chute = roxo.
- Área do Cronograma (`--area` por `data-area`): CM ciano, CIR rosa, MFC verde, PED roxo, GO amarelo, Simulado âmbar, RD
  lavanda (`roxo-tinta`).

### Contraste (medido, não digitado)
Medido pelo `tools/test_tema_contraste.py` (lê os hex do `tema.css`, WCAG 2.x; s227: a tabela deixou de ser digitada),
sobre `papel` / `card` / `afundado`. Escuro: `tinta` 17,1 / 15,9 / 14,6; `tinta2` 10,0 / 9,3 / 8,5; `tinta3` 6,3 / 5,8
/ 5,4; `acento` 11,2 / 10,4 / 9,6; `rosa` 6,4 / 6,0 / 5,5; `roxo-tinta` 8,1 / 7,6 / 6,9; `ok` 11,1 / 10,3 / 9,5; `erro`
7,9 / 7,3 / 6,7; `aviso` 11,9 / 11,1 / 10,2; `linha-forte` 3,8 / 3,5 / 3,2; borda da placa contra o fundo 1,73. Claro:
todos os textos ≥ 4,7 nas três superfícies (`acento` 4,7 sobre o elevado); `linha-forte` 3,4+; borda da placa 1,66.
`--sobre` sobre os preenchimentos: 5,8 (roxo) a 11,9 (aviso) no escuro, 5,6+ no claro. Pisos travados: texto ≥ 4,5 nas
3 superfícies, `tinta` ≥ 7, controle ≥ 3, borda da placa ≥ 1,6, `--sobre` ≥ 4,5.

### Apelidos
Legados (hub e player): `--alerta` = `--erro` (nome antigo); `--qz-ok/-duv/-chute` = ok/aviso/roxo-tinta; `--suave` =
roxo. As aulas usam nomes próprios em inglês: `--paper --ink --ink2 --ink3 --line --line2 --sunk --card --on`, `--teal*`
(= acento), `--amber*` (= aviso; `amber-ink` literal), `--plum*` (= roxo), `--carmine*` (= erro; `carmine-ink` literal).

### Named Rules
**The Cor Literal Rule.** Cor literal só no `tema.css`. Player, painel, hub e leitor usam `var(--token)`; o teste trava
cor literal no player, no painel e na tela revelada.

**The Um Papel por Cor Rule.** Ciano interage, rosa assina, âmbar avisa, roxo decora e mede. Rosa nunca é estado; ciano
nunca é título nem rótulo; roxo puro nunca é texto.

**The Nunca Só Cor Rule.** Estado nunca só por cor: gabarito `✓`, errada `✗`, chute `?`, resolvida `✓`, "abaixo do
necessário" por extenso, declaração com o nome do estado no botão, chip de área com o nome.

## Typography

**Família única:** Atkinson Hyperlegible Next (com `ui-sans-serif, system-ui, "Segoe UI", Roboto, sans-serif`).

**Character:** uma família só (decisão dele, s224: 0/O e 1/l distintos em dose e corte), aplicada com `!important`
porque as aulas declaram a fonte em atalhos `font:`; algarismos tabulares em tudo; sem caixa-alta (`text-transform:none`
global — os rótulos em maiúsculas das aulas e do player viram texto comum). Hierarquia por tamanho e peso, nunca por cor
(achado A4: títulos em ciano foram removidos).

### Hierarchy
- **Número** (700, `--fs-numero` 2rem): métrica de destaque. Nos anéis, o % central (30 px no SVG, algarismos
  proporcionais) e um único número branco por anel.
- **Página** (700, `--fs-pagina` 1,5rem, 1,2, −.02em): título da tela/topo do player. Marca do hub: 700, 1,375rem,
  −.01em (A22). Manchete da aula: `clamp(30px, 6.4vw, 44px)` 700.
- **Seção** (650, `--fs-secao` 1,125rem): título de seção; número destacado do anel (`.an-val b`). Título da placa no
  Painel usa `--fs-item` 650.
- **Item** (600, `--fs-item` 1rem, 1,35): título de linha de lista e de cartão em `tinta`. Pergunta do card: 700,
  `clamp(1.2rem, 1.05rem + .6vw, 1.5rem)`, 1,3; resposta: 600, 1,125rem, 1,45.
- **Corpo** (400, `clamp(15px, .95rem + .2vw, 17px)`, 1,55): hub e player. **Leitura** (17 px, 1,65): aulas e resumos
  no leitor, numa medida de ~85 caracteres (`--wrap`).
- **Legenda** (`--fs-legenda` .875rem): rótulos, botões compactos de ação, valores sob o anel.
- **Meta** (`--fs-meta` .8125rem, 650 em chips): metadado em `tinta3`, chips, rótulo "Próxima".
- Negrito (`strong`): 650.

### Named Rules
**The Sem Caixa-Alta Rule.** `text-transform:none` em tudo, inclusive no CSS das aulas. Ênfase por peso e tamanho.

**The Número Único Rule.** Nenhum número soma unidades diferentes (o "226" dos mockups somava questões com cards e ficou
de fora); uma métrica = um número.

## Layout

**Celular primeiro.** A 390 px tudo é uma coluna de placas empilhadas; no desktop o shell e o Painel usam a coluna larga
(`--largura`, 72rem) com placas em grade, e a leitura longa (aula, enunciado, card) segue na medida `--wrap` (46rem, ~85
caracteres por linha no desktop; A14: a coluna de 58rem dava ~110). Na medida `--wrap` ficam só o card, o leitor e a
questão aberta (`#aba-cards,#hub-leitor,#qz-player`). Um `.wrap` só por página: o shell troca só a largura do mesmo
contêiner.

**Espaço** (múltiplos de 4, em `:root`, valem nos dois temas): `--esp-1` 4 · `--esp-2` 8 · `--esp-3` 12 · `--esp-4` 16 ·
`--esp-5` 24 · `--esp-6` 32 · `--esp-7` 48 px. Vão entre placas da grade: `--esp-4`.

**Pontos de quebra observados:** placa e cartão de tarefa mudam a 520/521 px (padding 16 → 24; tarefa empilha meta / tema
/ ação abaixo de 520); anéis do Hoje 2 × 2 a 390 e 4 em linha a partir de 600 px de iframe; legenda ao lado do anel a
partir de 26rem (`@container`); Painel em duas colunas a partir de 760 px de iframe (Por bloco | Flashcards da semana,
mesma altura); Teoria lado a lado a partir de 900 px (`align-items:start`); leitor com trilho lateral até 920 px.

**Largura (regra dele, reprovada duas vezes quando quebrou):** UM `max-width` no contêiner (`.wrap`) e todos os filhos
herdam 100% dele. Nunca `max-width` por elemento (parágrafo, lede, lista) ao lado de quadro com fundo ou borda: as bordas
direitas fazem zigue-zague. Exceção: manchete sem caixa (`.top h1`). O `max-width` aparece no máximo 2 vezes na página do
player e na do painel; nenhum no `tema.css`.

**Celular:** nada `sticky`/`fixed`, nada `nowrap` (texto longo quebra); item de grade com `min-width:0` (`.qd-tema`,
`.qz-cadeia li`, placas); alvo de toque de 44 px (abas, botões, linhas; o trilho de questões tem 10 px visíveis e 26 px
de toque; dias da lista em linhas de 44 px). Nenhuma rolagem horizontal (medida pelo `ui_capturas.py`).

**Iframes:** dentro do hub, o painel e o leitor rodam em iframe com fundo TRANSPARENTE (elemento `.hub-quadro` e
documento, injetado no `preparar`): a luz é a do shell, sem emenda no topo do quadro; fora do hub eles pintam o próprio
fundo.

### Named Rules
**The Um Wrap Rule.** Um contêiner com `max-width`; os filhos herdam. Bordas direitas alinhadas sempre.

**The 390 Primeiro Rule.** Toda decisão é conferida primeiro a 390 px, à noite, no tema escuro.

## Elevation & Depth

Sem sombra, sem glow, sem halo, sem `text-shadow` (decisão dele, 13/10: "fosco em camadas"; `--sombra:none` nos dois
temas; A10 tirou o brilho do título da aula e o gradiente das barras). A profundidade vem de três coisas: **degrau de
superfície** (`papel` → `card` → `afundado`), **borda** (`borda-placa` ≥ 1,6:1 contra o fundo; `linha-forte` ≥ 3:1 nos
controles) e o **fio cromado** de 1 px no topo de cada placa (`::before`, recuado do raio nas pontas, apagado nas pontas
como um reflexo). Atrás do topo, a `--luz` dá a sensação de material sob uma lâmpada. Elevado = um degrau acima da
placa: card do player, cartão de tarefa, badge. Dentro do leitor, `--paper` = a cor da placa e `--card` = o elevado,
para nenhuma caixa interna ter a cor da placa.

O único `box-shadow` em uso é estrutural, não de profundidade: `inset` para a marca de "revisar depois" no trilho (base
âmbar de 3 px) e para o contorno do segmento ligado.

### Named Rules
**The Fosco Rule.** Profundidade = degrau + borda + fio cromado. Nada brilha; neon nunca no corpo do texto.

**The Cromado É Luz Rule.** O azul → violeta é reflexo (1 px) ou luz de fundo, nunca uma superfície, faixa ou
preenchimento.

## Shapes

Cantos suaves com raio por nível (s227): `--raio-placa` 14 px (a placa, o card do player) > `--raio` 10 px (cartões e
controles: botão, alternativa, campo, segmento, cartão de tarefa) > `--raio-p` 6 px (kbd, grifo, aviso, botões compactos
do topo do card) > `--raio-pilula` (só badge e chip). Controles nunca em pílula (A8: a declaração e Questões/Simulados
saíram do formato reservado a badge). Filetes de 1 px (`linha`) separam linhas dentro da placa; seções do card e
callouts usam filete à esquerda (2–3 px) em vez de caixa. O trilho de questões usa segmentos de 2 px de raio. Barras
de progresso: 6–10 px, pontas em pílula, preenchimento sólido. Anéis: SVG, traço 10, ponta arredondada.

## Components

Caráter: **foscos e diretos** — objetos de toque grandes (44 px), contorno honesto, ciano só onde se age. Componente
mora no arquivo da tela, nunca no `tema.css` — com UMA exceção declarada (s227): a primitiva `.placa`.

### Placa (signature)
Primitiva `.placa` do `tema.css`, usada pelas quatro telas: `card` + borda 1 px `borda-placa` + raio de placa + fio
cromado de 1 px no topo; padding 16 px no celular, 24 px acima de 520 px; `min-width:0`; sem sombra. Nenhuma tela a
redefine: todas compõem (`class="placa dash-hoje"`), e o teste trava uma regra só. Uma placa por seção, título dentro,
linhas com filete por dentro e sem filete na última; nunca uma placa por número. **Questão (part 4):** placa do enunciado
(meta, texto, figuras) e placa do resultado (veredito, cadeia, análise, rodapé); alternativas, certeza e botões no fundo,
com a moldura própria; no fim, métricas, por bloco, Elos e revisão, uma placa cada. **Leitor:** o iframe numa placa sem
padding (a aula tem o próprio; com 16 px a coluna perderia 32 px a 390) e a assinatura na placa de baixo, da mesma
largura (`.hub-assina.placa{margin-inline:0}` vence o alinhamento R9).

### Buttons
- **Forma:** raio de controle (10 px), 44 px de altura, 650.
- **Primário** (`.primario`, `.hub-btn-prim`, `.t-btn-prim`): ciano cheio com texto `sobre` (Resolver, Responder,
  Próxima, Virar, Abrir lista, Tentar de novo). Hover: `acento-tinta` (ou `brightness(1.08)` no player).
- **Secundário temático** (`.hub-btn`, `.t-btn`, s229): contorno ciano, fundo transparente, texto `acento-tinta`; hover
  com lavagem `acento-fraco`; desabilitado em `linha-forte` + `tinta3`. É o "Abrir aula", "Abrir resumo", "Abrir
  documento", "Todas as listas", o voltar do leitor, "Anterior" e "Pular" — o desenho do "Responder" em contorno.
- **Neutro** (botão base do player): contorno `linha-forte`, fundo transparente, texto `tinta`; hover `afundado`;
  `:active` desce 1 px; desabilitado a 45%.
- **Fantasma** (`.fantasma`): tracejado, `tinta2`, tamanho de legenda.
- **Compacto** (`.topo-acoes`, Cards, s229): 36 px, raio pequeno, tamanho meta — Virar (ciano, `.primario`) | Pausar
  (âmbar) | Defeito do card (rosa; hover/aberto em lavagem rosa), numa linha no bloco de cima.
- **Foco:** contorno 2 px `acento`, deslocado 2 px (3 px no player; 3 px de foco na linha da Teoria).

### Chips e badges
- **Badge** (área `.qd-bl`, objetivo `.qz-obj`): pílula, `afundado` + `tinta2`; "Próxima" em ciano (lavagem
  `acento-fraco` + `acento-tinta`).
- **Chip de área** (`.t-rot` no Painel, "nova"/"novas" na Biblioteca): `rosa-fraco` + `rosa` (s226, pedido dele). Banca
  da questão em rosa, tema em ciano.
- **Chip de estado** (`.qz-chip`, `qzChip`): só fora do normal — "pronta" não tem chip (A21); em curso = aviso com
  respondidas/total (espelho do aparelho); resolvida = ok + `✓`.
- **Motivo do card** (`.reason`): pílula `card` + `tinta2`.

### Cards / Containers
- **Linha de lista** (Teoria `.qd-bloco`, Listas `.qz-lista button`, revisão `.qz-rev`, por bloco `.qz-porobj li`,
  cadeia `.qz-cadeia li`): sem fundo e sem caixa própria, DENTRO da placa da seção; filete de baixo (`linha`); título 600
  em `tinta`, meta em `tinta3`.
- **Moldura** (card do player, alternativa da questão, campo, assinatura de leitura): só o que é objeto de toque ou o
  foco da tela; `card` + `linha` + raio de controle; sem sombra.
- **Barra do Cronograma / cartão de tarefa** (`li.tarefa`, s229 rodadas 3–4): o item de backlog das três abas (Painel,
  Teoria, Listas). Barra horizontal na largura toda, empilhada no dia (estilo Google Calendar sem horas): faixa de 4 px à
  esquerda + fundo tingido pela grande área (`color-mix` 9% de `--area` sobre `afundado`), borda `linha`, raio de
  controle; no topo o chip da área e a contagem (`.t-n`), o tema, e os botões à direita (no celular, embaixo). A Próxima
  = rótulo "Próxima" + borda ciano. Assinada/concluída: a 72% com o estado em verde; ao vivo, sai do Cronograma.
  Roteamento: o Painel mostra **Resolver** (primário: `data-hub-tarefa` abre a aba Listas JÁ na lista) + **Abrir aula**
  (contorno: o leitor já na aula); fora do hub, "Abrir lista" (primário); a Teoria só Abrir aula / Abrir resumo / Abrir
  documento (`.hub-btn`); as Listas só Resolver (a resolvida, "Rever"; visual, o toque é da linha). A tarefa que uma aula
  CUMPRE (`tarefa_id` no quadro) mostra o título da aula. A RD não assinada é um cartão com o estado num span só
  (`.t-rd-st`), que o hub reescreve ao vivo pela MESMA fonte do "assinado" (`quadro/<slug>` ou `doc_<slug>`); o build
  também lê o `doc_<slug>` (`painel.PEND_ESTADO`). ⚰️ a linha inteira como alvo com a seta "›" (P21).
- **Card do player** (`.card.placa`): a placa ELEVADA (`afundado`) com a borda de controle (`linha-forte`; ciano no
  hover da frente), na medida `--wrap`, logo abaixo da placa do topo; os botões ficam fora dela. Tocar no card vira (o
  mesmo `virar()` do botão e do Espaço; seleção de texto não vira); a frente leva cursor de toque. Contra o "chapado":
  pergunta em 700 e maior, o motivo como pílula, o contexto com filete, e o verso abre como o DEGRAU de baixo da mesma
  placa (`card`, de borda a borda, filete `borda-placa` em cima), nunca caixa dentro do card. Pergunta > resposta >
  regra/armadilha > assunto.
- **Secções do card** (`.bloco` regra-mestre, `.bloco.alerta` armadilha): filete à esquerda (neutro / âmbar), nunca
  caixa dentro do card.
- **Métricas** (`.qz-tiles`, `.fim-grade`, `.fig`): uma faixa entre dois filetes, número 700 + rótulo `tinta3`; sem uma
  caixa por número (A5).
- **Aviso** (`.hub-aviso`, `.aviso` no player): filete âmbar de 3 px + lavagem âmbar, raio pequeno; `.aviso.forte`
  (banco fora) com borda inteira.

### Inputs / controles da questão
- **Alternativa** (`.qz-alt`): moldura `card` + `linha` + raio de controle; letra em `tinta3`; marcada = borda ciano +
  lavagem; gabarito = ok + `✓`; errada = erro + `✗`; riscada = tachado de 2 px em `tinta3`; " · por quê" quando há
  porquê fechado.
- **Segmentado** (Questões/Simulados `.qz-modo`, certeza `.qz-seg`, declaração `.qz-decl`): raio de controle, contorno
  `linha-forte`, 48 px; ligado = cor do estado + lavagem + contorno interno.
- **Trilho de questões** (`.qz-trilho i`): 10 px visíveis, 26 px de toque; respondida = `linha-forte`, atual = ciano,
  marcada para revisar = base âmbar (`flag`), vazia = `afundado` (A7).
- **Campo**: moldura, borda `linha-forte` (A9: a borda a 1,6:1 era invisível).

### Navigation
- **Abas** (`.hub-aba`): quatro iguais (Painel | Teoria | Listas | Cards), rótulo curto, 44 px, texto 600 `tinta3`
  (hover `tinta`); a ativa em `tinta` com uma barra de 2 px que é o TRECHO do horizonte sob ela (`background-size:400%`,
  posição por `nth-child`; s226, pedido dele); o filete de baixo é o próprio horizonte (75%).
- **Marca** (`.hub-marca`): "Med" em `tinta` + "Hub" em ciano, 1,375rem, sob a luz.
- **Barra do leitor**: título à esquerda; à direita o botão único do grifo (`#hub-grifo-btn`, amostra da cor ativa +
  "Grifo", 44 px, `aria-expanded`) — só no leitor da Teoria e na barra da questão (`#qz-grifo`); tocar abre as 3 cores
  em cascata (lista vertical sob o botão, atraso de 60 ms por opção, `aria-pressed` + contorno ciano na ativa); escolher,
  tocar fora ou Esc fecha. Nas questões sem o seletor o grifo fica no rosa padrão.

### Anéis do Hoje (signature, Painel v4.1)
Uma placa "Hoje, terça 13/10" com 4 anéis (`.an4`; SVG inline, viewBox 120, traço 10, `pathLength=100`, % no centro,
rótulo + valor + uma linha abaixo; trilho `--trilho`, 0% = só o trilho): **Questões** (`acento`, contra o `q_hoje` das
LISTAS — s231, 19/10, decisão dele: o simulado é unidade à parte, "+ simulado (100 q)" em `.an-sim` sob o valor; dia só de
simulado, "X de 97 no simulado"; o `data-conta` da âncora diz ao hub o que o "+K" soma; sem sprint, o alvo da meta), **Cards** (`rosa`, contra o teto, com "Ir para os cards"), **Ritmo em 7 dias** (`aviso` abaixo
/ `ok` em dia, sempre com o texto; `data-bloco="ritmo"`; "23,5 em 14 dias · 78,4% de acerto"), **Até 01/11** (`roxo`:
feito contra a meta + um 2º arco, roxo a 50%, por baixo, até o que o sprint entrega; a meta 10.000 só aqui). O número do
valor é UM só, branco, publicado + o que ele fez desde o publish (o "+K" ciano morreu; `title` diz o K); o
`b[data-vivo]` fica na legenda e o anel no valor publicado.

### Barras de dado
- **Progresso** (painel `.bl-barra`, player `.barra`, `.dist-barra`): 6–10 px, trilho `--trilho`, preenchimento sólido
  ciano.
- **Por bloco** (`.bl`): nome · barra de acerto 0–100% · % · feitas/total; o de menor acerto em âmbar com o rótulo "mais
  fraco"; Simulados na última linha em `roxo` (s228; era neutra); `title` em cada linha = dica ao passar o mouse.
- **Flashcards da semana** (ex-"Revisões nos próximos 7 dias"; s228–s229): paleta `--fc*`; total da semana no cabeçalho
  (`.ag-total`, número em `fc-tinta`); barra EMPILHADA por dia — embaixo, em `fc-fraco`, os já agendados (o PICO em
  `fc` cheio com o número em destaque e "(pico da semana)" na dica); em cima, em ciano, os que ENTRARAM pela última
  sessão (cards com `last_review` no dia do `review_time` mais recente do `fsrs_revlog`, `painel._agenda_com_sessao`); o
  total em cima e "+k" pequeno em ciano; linha de base `linha-forte`; a dica diz os dois.
- HTML/CSS puro (o painel não carrega lib); forma e cor do dado pela skill `dataviz`, dentro dos tokens.

### Leitura resiliente (comportamento)
`assinarResiliente(consulta, onDados, opts)` no `hub.html` (listas, quadro da Teoria, questões/respostas/análises da
lista aberta, notas do lote): `consulta(db)` monta a referência sobre o `db` recebido (1ª tentativa = `opts.db`; da 2ª em
diante e no "Tentar de novo", conexão nova por `claude.use("db")`, avisada em `opts.aoReconectar` — o `QZ.db`); erro =
`console.warn("[hub] leitura <coleção> falhou", código, tentativa)` + nova assinatura em 1/2/4 s com "Carregando…";
esgotadas, a mensagem + botão `.primario` **Tentar de novo** (`htmlRetentar`); reabrir a aba com ela morta reassina; um
estado por assinatura, nunca 2 ouvintes. Aba nova lê por ela.

## Do's and Don'ts

### Do:
- **Do** usar uma `.placa` por SEÇÃO e linhas com filete (`linha`) dentro dela; compor (`class="placa x"`), nunca redefinir.
- **Do** pôr cor literal só no `core/templates/tema.css`; trocar a paleta trocando os dois blocos de cor (escuro e claro).
- **Do** usar ciano (`acento`) só para interação: navegação ativa, foco, progresso, ação primária, link.
- **Do** dizer o estado em texto ou símbolo além da cor (`✓ ✗ ?`, "abaixo do necessário", "mais fraco").
- **Do** dar 44 px de alvo de toque a todo controle (36 px só nos três compactos do topo do card).
- **Do** usar `roxo-tinta` quando o roxo for texto.
- **Do** conferir a tela a 390 px primeiro e no tema escuro, com `python tools/ui_capturas.py`, antes de publicar.
- **Do** manter um só `.wrap` (`max-width`) por página e todos os filhos a 100% dele.
- **Do** deixar só a mecânica e o botão: mensagem de erro com a ação de recuperar ("Toque para reenviar") fica.

### Don't:
- **Don't** usar sombra, glow, halo, `text-shadow` ou borda neon; a profundidade é degrau + borda + fio cromado.
- **Don't** fazer uma caixa por número (tiles, métricas, cadeia em caixas, regra-mestre como caixa dentro do card).
- **Don't** usar o cromado ou a luz como superfície, faixa, cor de dado ou fundo de texto.
- **Don't** usar rosa como estado, ciano como título/rótulo, nem roxo puro como texto.
- **Don't** usar caixa-alta, outra família tipográfica ou algarismos não tabulares em métricas.
- **Don't** usar `sticky`, `fixed` ou `nowrap`; nem `max-width` por elemento ao lado de quadro com borda.
- **Don't** pôr controle em pílula (pílula é só badge e chip).
- **Don't** explicar o gesto que o controle já mostra ("toque no card para virar", "toque numa questão para ver...",
  "· toque para ampliar", a legenda da certeza) — regra dele, s229, 15/10: *"pode todos esses pequenos excessos. basta a
  mecânica e o botão que já existe"*.
- **Don't** pôr legenda em prosa que repete o dado (Teoria, frase do Ritmo, "Fora da tabela", `p.nota` no dashboard,
  legenda de instrução das Listas).
- **Don't** somar unidades diferentes num número só.
- **Don't** usar jargão de bastidor no painel, inclusive nos comentários do `tema.css` (viaja embutido).

## Telas e processo

### Onde mora cada coisa

| Camada | Arquivo | O que tem | Quem recebe |
|---|---|---|---|
| Tokens + base | `core/templates/tema.css` | as duas paletas (escuro padrão, claro por `data-theme="light"`), escalas de espaço, raio e tipo, apelidos legados e das aulas, base comum (fonte, foco, seleção, movimento, o fundo com a luz) e a primitiva `.placa` (s227) | shell do hub, painel, player standalone, leitor de aulas e resumos |
| Casca, Teoria, Listas, leitor | `core/templates/hub.html` (bloco `<style>`, depois de `/* @hub:player-css */`) | abas, Teoria (`qd-*`), Listas e questão (`qz-*`), barra do leitor, assinatura de leitura (`hub-assina*`) | o hub |
| Cards | `core/templates/player.html` (região `@player:css`) | o player FSRS e a tela de fim | o hub (aba Cards) e o standalone do `fsrs_queue.py --build-player` |
| Painel | `tools/painel.py` (constante `CSS`) | o dashboard (anéis do Hoje, Por bloco, Flashcards da semana) e o Cronograma (s229: a Documentação foi para a Teoria) | `artifacts/painel.html` (iframe no hub) |
| Leitor de aulas e resumos | `core/templates/tema-aula.css` | a camada de leitura sobre o CSS próprio de cada aula (43 em `artifacts/aula-*.html`) e da página de resumo | só o leitor (injetada depois do `tema.css`) |
| Página de resumo | `tools/hub.py` (constante `CSS_RESUMO`) | paleta e estrutura próprias da página de resumo publicada | a página aberta fora do leitor; no leitor o tema vem por cima |
| CSS injetado pelo JS do hub | `core/templates/hub.html`: `painelListas` (selos e "+N" no painel), `pendEstilo` (formulário de pergunta nos documentos), `grifoEstilo` (marca-texto no leitor) | estilos que o hub põe dentro dos iframes | painel e leitor |

Como entra: o `tools/hub.py --build` injeta o `tema.css` no fim do `<style>` do shell (marcador `/* @hub:tema-css */`) e,
junto com o `tema-aula.css`, no leitor (`"@hub:tema-js"`, aplicado no `srcdoc` de cada aula/resumo); o `tools/painel.py`
embute o `tema.css` depois do próprio CSS; o `--build-player` embute antes do `</head>` (`fsrs_queue.embutir_tema`).
Trocar a paleta = trocar os dois blocos de cor do `tema.css`, montar o hub em scratch e conferir (abaixo) antes de
publicar.

### Telas: o que cada uma prioriza

- **Painel**: responde, nesta ordem, o que fazer hoje, quanto avancei e o que vem depois. No celular (abaixo de 760 px de
  iframe), o 1º filho da grade é a Próxima (`.dash-prox`: o MESMO cartão `li.tarefa.proxima` do Cronograma, mesmos botões e
  `data-tarefa`; feita ao vivo, some) — s231, 19/10, decisão dele, do P0 do critique ("a próxima ação enterrada a 390 px");
  no desktop ela não aparece (o pedido era o celular; lá fica a ordem da s227, anéis no topo). Depois, a placa dos 4 anéis
  (s227 part-5, pedido dele: *"o 'Painel' ainda está muito disperso. Esses 4 blocos deveriam aparecer junto no topo,
  através desses anéis com percentual"*); abaixo, Por bloco | Flashcards da semana. A `section.dash` é a grade das
  placas, uma coluna e, a partir de 760 px de iframe, duas; vão `--esp-4`, o mesmo até as placas de baixo; sem filete
  entre seções. Com sprint, o único por-dia da tela é o do sprint (`q_hoje`; s231: no anel, no Cronograma e no Hoje das
  Listas o número é o das LISTAS — o mesmo nos três — e o simulado vem a parte, "+ simulado (100 q)") e a meta
  10.000 aparece uma vez (no anel Até 01/11); sem sprint, a meta. A barra de projeção e a barra do Ritmo saíram
  (`cronograma-contract` v1.8). ⚰️ *s226: dashboard Hoje · Ritmo · Até 01/11 · Por bloco · Revisões 7 dias em tiles, com
  barra de projeção (feito ciano · cumprindo o sprint lavagem ciano · fora do sprint `linha` tracejado); s227 part-2: dois
  anéis concêntricos (questões externo, cards interno).*
- **Painel, Cronograma** (s229, pedido dele em 15/10; ex-"Plano de hoje" + "Próximos dias", depois "Roadmap"): Hoje
  (`section.rm-dia.hoje`, título "Hoje · qua 15/10" em ciano + a contagem) e cada dia seguinte, TODOS abertos (nenhum
  `<details>`); Fora do sprint · N segue recolhido, agrupado pelo motivo. Cada tarefa é a barra do Cronograma
  (Components). Com o sprint gravado (`plano.agenda_sprint`, a fonte única do "hoje" do Painel, da aba Listas e do boot):
  as tarefas do dia, a que rolou de um dia passado sem rótulo de atraso, o total de questões, "+ N cards" que faltam da
  dose do dia e a RD não assinada mais antiga; sem o estado do quadro (`tmp/hub_db/quadro`), nenhuma RD: o Painel nunca
  afirma "não assinada" no escuro. Sem "Semana", "Atrasadas", "Desta semana" nem "Até a prova". Sem sprint (`dia_plano`
  todo NULL), a semana antiga: o subtítulo "Atrasadas · N" em âmbar, uma vez, nunca por linha. A 1ª tarefa leva só o
  rótulo "Próxima" (`li.tarefa.proxima`), o mesmo controle das outras. No Cronograma o assinado/concluído SAI (RD lida,
  tarefa cuja aula que a cumpre foi lida — `data-cumpre` —, lista resolvida), no build e ao vivo.
- **Teoria** (s226; s229): a Biblioteca por área e disciplina com toda aula, resumo e RD; "Revisões direcionadas" é o
  eixo `RD` da Biblioteca (o 1º; as disciplinas por dentro; a RD não assinada da mais antiga para a mais nova; a assinada
  some ao vivo do backlog e fica só na Biblioteca); as análises (Dossiê UERJ, Autópsia UERJ 2021...) moram no eixo
  **Documentação** (`hub.EIXO_DOC`, área `DOC`, disciplina "Análises"). A RD e a análise não feitas levam "nova" até ele
  ABRIR o item no leitor (visto por aparelho, `localStorage["medhub.vistos"]`, try/catch). Na Biblioteca o feito segue
  riscado e esmaecido. Sem semana, sem "Atrasadas" e sem contagem de questões. Placas: RDs | Biblioteca (`.qd` em grade;
  lado a lado a partir de 900 px).
- **Listas** (s226): na ordem do Cronograma, pelo `<script id="hub-sprint">` (`hub.dados_sprint` =
  `plano.agenda_sprint`): **Hoje** (aberto) + **Próximos dias** (um grupo por data, recolhido) + **Fora do sprint · N**
  (recolhido, com o motivo; a lista aberta de tarefa sem dia cai aqui como "sem dia no plano"); resolvidas recolhidas no
  fim. Sem sprint (`hub-sprint` = `null`), as semanas antigas. **Simulados** na sua sub-aba, com a data do sprint ("dom
  25/10"; o do dia, "hoje"). Placas: seletor (`.qz-cabeca`) fora das placas; Hoje | Próximos dias + Fora do sprint +
  Outras listas | Resolvidas; no desktop (`qz-duas`) Próximos ocupa a coluna 2 nas duas linhas e Resolvidas sobe para
  baixo de Hoje; Simulados = provas | resolvidos (`qz-sim`, só com os dois).
- **Questão** (s229, pedido dele em 15/10): lista SEMPRE em modo estudo, simulado SEMPRE em prova — sem seletor;
  "Revisar depois" só no simulado (`#qz-marca`; na lista a resposta grava `flag: false`); o grifo guarda a cor (`[ini,
  fim, cor]`, sem cor = rosa; a cor nova corta a antiga); título numa linha, Grifo e tempo lado a lado em bloquinhos;
  botões "‹ Anterior · Responder · Pular ›" centralizados. Barra e trilho no fundo, com a largura do corpo (`--wrap`). O
  trilho é navegação; a questão revelada tem no máximo 3 blocos (alternativas com o porquê, veredito, cadeia com a
  declaração); a tela de fim mostra a faixa de métricas, o por bloco, o bloco Elos e a revisão. Riscos declarados da
  part 4: duas placas somem por `:has()` (Elos sem cadeia; o leitor sem aula carregada) — sem `:has`, uma placa vazia.
- **Cards**: o topo (título, "N de 150 hoje", fila, relógio, os três controles, barra, tally) é uma placa; as opções do
  Defeito abrem logo abaixo, dentro dela (o registro `defeito` + `motivo` não mudou); o card é a placa elevada logo
  abaixo; a tela de fim do lote numa placa (s227, part 3).
- **Leitor de aulas**: uma coluna só (`.wrap` de 46rem; a aula antiga com trilho lateral usa o `main` de 38rem); títulos
  brancos, rótulos e fontes lavanda; termo-chave em negrito ciano claro (o único texto ciano da leitura); callouts por
  significado, sempre filete + lavagem: armadilha = âmbar (como no card), banca = roxo, nota neutra (`.key`, `div.note`,
  `.disc`, `.fonte`, `.star`); o que é errado ou proibido (`.mal`) = coral; numerais e marcos decorativos = roxo; números-
  chave do tema em branco e grandes com rótulo lavanda (destaque por tamanho, não por neon).

### Leitor de aulas (`tema-aula.css`)

Inventário das 43 aulas (s225, medido com parser + Edge): `docs/research/2026-10-13-05-ui-auditoria-aulas.md` (6 famílias
de classe: EN15 com `.nav`/`.stats` sem `<main>`, ER6 com `.rail` + `main`, RS13, RG7, dossiê, autópsia). A camada só
ajusta, nunca reescreve aula. Achados L1–L15 (§14 de lá) e o estado:
- **L1** `.tw` cortada pelo `overflow:hidden`: **resolvido** (hub v105; a tabela rola na caixa).
- **L3** espaçamento de caixa-alta nos rótulos: **resolvido** (`.eye .kick .dstage .rlab .albl th .tag .tk`, `h3/h5` de `.vs`).
- **L5** negrito ciano com exceções por descendente: **resolvido**. **L7** `h4.sub` e **L8** `.dtitle h3`: **resolvidos**.
- **L4** callouts sem critério único: **resolvido na v4**; resta o `.ext` da `dmg`.
- **L6** h3/h4/h5 como rótulo dentro de `.vs .tgrp .blk .cmap .if3`: **pendente**.
- **L9** outliers de paleta (autópsia: 18 tokens próprios; neuromusculares: `--acc*`): **pendente** (§8.3 do inventário).
- **L2, L10–L15**: **pendentes** (ver o inventário).
- **Referências no fim** (s227, part-7, pedido dele: "remover todos os 'Fonte:...' espalhados pelo texto, e concentrá-los
  ao final, tal como um artigo"): no leitor, a "Fonte:" com cara de referência sai do texto (`ehReferencia`; a "Fonte:"
  clínica, como a do sangramento no TCE, fica). Referência externa vira lista numerada no fim (`section.hub-refs`,
  "Referências") com um sobrescrito ciano no lugar; base interna (`ehBaseInterna`: resumo do MedHub, verso de card,
  PDF/apostila do curso) vai para "Base deste documento", sem número. O bloco que sai deixa um marcador vazio (os grifos
  não mudam de índice). A aula nova traz `sup.ref`, `section.refs` e `p.base` (`aula-base` §6). Alcance medido em 13/10:
  116 "Fonte:" em 36 aulas e 8 resumos.
- **v4 (s227, part 4):** `figure.fig-an` com fundo da placa e `borda-placa`; `.trilho-box` sem moldura; `ol.esc` das RDs
  como lista. Conferido a 390 nos dois temas. O `ui_harness.html` tem `?tema=light|dark` e `?doc=aulas/x.html` (o
  `ui_capturas.py` ainda não tem flag para eles).
- **Figura de mecanismo** (s226): `figure.fig-an` no CSS da própria aula — moldura `--card` + `--line2` (cabeçalho "Fig
  n · esquema" à esquerda e o título à direita), SVG inline com `viewBox` e `max-width:26rem` dentro da moldura,
  `role="img"` + `aria-label` com o que a figura diz, legenda curta + o número da referência (sem "Fonte:"). Cor só pelos
  apelidos das aulas (`--teal*`, `--amber*`, `--plum*`, `--ink*`, `--line2`, `--sunk`, `--card`). Nenhum fato que a
  seção não diga; dado ilustrativo declarado na própria figura. Conferida a 390/768 nos dois temas.

### Contratos travados por teste

| Contrato | Teste |
|---|---|
| nada `sticky`/`fixed`, nada `nowrap`, um `.wrap` só | `test_hub.py::test_celular_sem_sticky_sem_nowrap_e_um_wrap_so`, `test_painel.py::test_celular_sem_sticky_sem_nowrap_e_grid_item_encolhe`, `test_hub_render.py::test_forma_da_tela_revelada` |
| abas com rótulo curto e 44 px; `.qd-tema` com `min-width:0` | `test_hub.py::test_abas_curtas_e_com_alvo_de_toque` |
| tela revelada sem cor literal; 44 px nos botões; `.qz-cadeia li` com `min-width:0` | `test_hub_render.py::test_forma_da_tela_revelada` |
| contraste do tema nos dois blocos; `.placa` com uma regra só, sem sombra nem brilho, sem `max-width` no `tema.css` | `test_tema_contraste.py` |
| shell v4: luz no `body`, `.hub-quadro` e documento do quadro transparentes, coluna larga, um `.wrap` | `test_hub.py::test_tema_v4_luz_no_shell_e_quadros_transparentes` |
| Painel v4.1: 4 anéis, Por bloco e Flashcards da semana em placas | `test_painel.py::test_topo_quatro_aneis`, `test_ate_01_11_anel_com_projecao_do_sprint`, `test_ritmo_anel_contra_o_sprint_com_a_cor_e_o_texto`, `test_flashcards_da_semana_renomeado`, `test_dashboard_em_placas_e_a_grade` |
| questão, fim e leitor em placas; ids, botões, `data-*` e ordem congelados | `test_hub_render.py::test_questao_fim_e_leitor_em_placas`, `test_ids_botoes_e_ordem_da_questao_e_do_leitor_nao_mudaram` |
| Teoria, Listas e Cards em placas, grade de 2 colunas no desktop, standalone do player com a placa | `test_hub_quadro.py::test_teoria_em_duas_placas_lado_a_lado_no_desktop`, `test_hub_render.py::test_listas_em_placas_e_a_grade_de_duas_colunas_no_desktop`, `test_cards_topo_e_card_em_placas_e_o_standalone_leva_a_placa` |
| player e painel sem cor literal; tema escuro/claro presente na página pronta | `test_fsrs_queue_player.py::test_template_real_e_injetavel_e_tem_wrap_unico`, `test_painel.py::test_html_obedece_o_contrato_de_render` |
| standalone do player recebe o tema | `test_fsrs_queue_player.py::test_embutir_tema_entra_antes_do_head_e_e_idempotente` |
| linha da Teoria acessível (foco de 3 px, sem-aula sem cara de botão) | `test_hub_quadro.py::test_p21_cartao_alvo_e_acessivel_e_o_sem_aula_nao_parece_botao` |
| Cronograma com sprint; sem sprint, a semana antiga; sem estado do quadro, nenhuma RD; RD lida pelo `doc_<slug>` sai; cartão com Resolver / Abrir aula | `test_painel.py::test_rd_lida_pela_assinatura_doc_sai_do_hoje`, `test_cartao_da_tarefa_tem_resolver_e_abrir_aula`, `test_hub_pendencias.py::test_rd_assinada_no_painel_troca_o_estado_e_nunca_soma_um_segundo_rotulo` |
| Painel com sprint (s226, base) | `test_painel.py::test_painel_sprint_sem_semana`, `test_hoje_do_sprint_soma_os_cards_do_dia_e_a_rd_nao_assinada`, `test_sem_sprint_o_painel_mostra_a_semana_antiga`, `test_sem_estado_do_quadro_o_painel_nao_afirma_rd_nao_assinada` |
| Teoria sem semana; a RD assinada some do backlog ao vivo | `test_hub_quadro.py::test_teoria_sem_semanas_com_o_backlog_de_rds_e_a_biblioteca`, `test_backlog_de_rds_da_mais_antiga_e_a_assinada_so_na_biblioteca`, `test_hub_render.py::test_rd_assinada_some_do_backlog_e_perde_a_etiqueta_na_biblioteca` |
| Listas = o mesmo "hoje" do Painel; simulado com a data | `test_hub_render.py::test_listas_e_painel_mesmo_hoje`, `test_listas_agrupam_por_hoje_proximos_dias_e_fora_do_sprint`, `test_simulado_leva_a_data_do_sprint`, `test_sem_hub_sprint_as_listas_caem_nas_semanas` |
| dashboard: `q_hoje` do sprint, meta 1x, Por bloco com "mais fraco", nenhum `p.nota`, o `q_hoje` = o do boot | `test_painel.py::test_dashboard_questoes_usa_o_q_hoje_do_sprint`, `test_dashboard_sem_sprint_volta_a_meta`, `test_barra_de_projecao_feito_sprint_meta`, `test_por_bloco_em_linhas_com_barra_e_o_mais_fraco_rotulado`, `test_plano_dia.py::test_boot_painel_listas_mesmo_hoje` |
| s231: Próxima no topo no celular; carga do dia = listas, simulado à parte (anel, Cronograma, Listas › Hoje, "+K") | `test_painel.py::test_proxima_no_topo_do_painel_so_no_celular`, `test_carga_do_dia_listas_num_denominador_e_o_simulado_a_parte`, `test_anel_de_questoes_no_dia_so_de_simulado`, `test_hub_render.py::test_listas_hoje_soma_as_listas_e_o_simulado_a_parte`, `test_ao_vivo_o_anel_de_questoes_conta_listas_e_simulado_a_parte` |
| painel sem jargão de bastidor (inclusive nos comentários do `tema.css`) | `test_painel.py::test_html_sem_jargao` |
| leituras pela assinatura resiliente; chip só fora do normal; marca 1,375rem | `test_hub_render.py::test_listas_se_recuperam_da_falha_de_leitura`, `test_botao_tentar_de_novo_reassina`, `test_leituras_das_abas_passam_pela_assinatura_resiliente`, `test_chip_da_lista_so_fora_do_normal` |
| a retentativa pede conexão nova ao banco | `test_hub_render.py::test_retentativa_pede_conexao_nova` |
| `max-width` no máximo 2 vezes na página do player e na do painel | os dois testes de contrato acima |

### Como conferir (obrigatório antes de publicar tela nova)

Regra da casa: tela nova do hub só publica conferida em navegador real, a 390 px.
1. `python tools/painel.py --html` e `python tools/hub.py --build --lote <lote vivo> --publicado <listagem> --quadro-estado tmp/hub_db`.
2. Capturas com banco falso no Edge headless, a 390, 768 e 1280 px: `python tools/ui_capturas.py` (11 cenas: painel,
   teoria, listas, simulados, questao, revelada, fim, cards, verso, aula, resumo; mede rolagem horizontal e erro de JS;
   assinatura e limites em `/engenharia-cli`). Saída em `tmp/ui_capturas/<data>/`. O seed vem dos dumps locais do db do
   hub em `tmp/` (conteúdo do EMED: nunca no git). O banco falso (`core/templates/ui_harness.html`) aceita
   `?leitura=1x|0|conexao`, `?tema=light|dark` e `?doc=aulas/x.html`.
3. Ler as capturas (ferramenta Read) e conferir: hierarquia, rolagem horizontal, estados e contraste.
4. Rodar as suítes `tools/test_hub*.py tools/test_painel.py tools/test_fsrs_queue_player.py tools/test_tema_contraste.py`.

### Achados abertos da varredura s225

Resolvidos (detalhe no git de `docs/UI.md` e em `tmp/UI_md_antes_s231.md`): A1–A15, A18, A21, A22; A24 ("chapado") em
curso pelo tema v4. Abertos:
- **A16** página de resumo publicada com paleta própria (verde-água antigo) fora do leitor (`hub.py` `CSS_RESUMO`):
  baixo impacto; mudar republica 31 resumos.
- **A17** claro só por `data-theme="light"`: decisão dele (s224).
- **A19** Cards: o Painel conta o saldo do dia (X de 150) e a aba Cards o lote no ar: mesmo PRD (contador do dia + fila
  diária).
- **A20** Semana antiga do Painel com ações repetidas por linha: mesmo PRD.
- **A23** sem o espelho local `medhub.respostas.<lista>`, a Q1 pode aparecer como nova mesmo respondida (lido no código,
  não medido): mesmo PRD (família do A18).

### Histórico de decisões

- **Front s229 (15/10)**: pedido dele, item a item — Roadmap/Cronograma no Painel (dias abertos, barras, Resolver / Abrir
  aula); a Documentação no eixo próprio da Biblioteca; "nova" some ao abrir; número único branco nos anéis; lista =
  estudo, simulado = prova, sem seletor; "Revisar depois" só no simulado; grifo de 3 cores nas Listas; banca rosa, tema
  ciano; botões secundários no desenho do "Responder"; Virar | Pausar (âmbar) | Defeito (rosa) no topo dos Cards; sem
  micro-dica de interação; rodada 4 (*"UM design compartilhado entre Painel, Teoria e Listas"*): a barra do Cronograma é
  o item de backlog das três abas. ⚰️ P21 (a linha inteira como alvo, com "›") e "a Próxima sem botão cheio" (s226).
- **Tema v4 "fosco em camadas" (13/10, s227)**: pedido dele com 7 referências na raiz (controle DualSense GTA VI, pins
  Vice City, 5 mockups): *"manter a 'riqueza' do retrowave/95', mas deve ser sóbrio e minimalista como uma plataforma de
  estudos deve ser [...] predomínio de tom escuro, rosa nos detalhes, azul/roxo para dar profundidade, branco/pêssego"*.
  Decididas por ele: placa fosca com fio cromado (sem glow), fundo preto frio com luz azul/roxa no topo, anéis sem soma.
  Decididas pelo agente (ele pode reverter): coluna larga no desktop, "pêssego" = o branco quente do texto, Simulados com
  provas | resolvidos lado a lado, a tela de fim do lote numa placa, alternativas com a moldura própria (não elevadas)
  pela segurança do simulado de 17/10. v3 (retrowave contido, índigo) no git: commit `c40c9f2`.
- **Dashboard do Painel (13/10, s226)**: pedido dele (*"integre estes dois blocos [...] com a modalidade de dashboard
  [...] e resolva as divergências entre metas"*); forma e cor pela skill `dataviz`; regra s203 suspensa para a tela
  (`cronograma-contract` v1.7). Na mesma tarde: "Hub" no azul da paleta; a barra da aba ativa acompanha o degradê; tags
  do Painel com a cor das da Teoria; fora as legendas em prosa.
- **v1 (12/10, s224)**: escuro índigo sobre preto, Atkinson, cartões viram linhas — *"prefiro tema escuro / modo noite,
  pode ser assim por default"* (`1d71743`). **v2 Vice City (12/10)**: fundo `#0B0F2B`, acento ciano (`95d4a38`).
  **v2.1–v2.3**: rosa crescente. **v2.4**: *"agora temos muito rosa; preferia a UI com mais ciano"* (`730d884`). **v3
  retrowave contido (13/10, s225)**: paleta de referência `#17132E #211C3A #29233F #403858`, semântica fixa por cor,
  hierarquia por tipo e menos caixas.
- **Abas que se recuperam sozinhas (13/10, s226)** e **a retentativa pede conexão nova** (a v108 publicada com a página
  aberta deixou Listas em "Não consegui ler as listas": as 3 tentativas reusavam o `db` morto).
