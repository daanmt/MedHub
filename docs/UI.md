---
type: reference
status: active
relates_to: [core/templates/tema.css, core/templates/hub.html, core/templates/player.html, tools/painel.py, core/templates/tema-aula.css]
---

# UI do MedHub -- design system, mapa e achados

> Porta de entrada de qualquer trabalho visual no MedHub. Criado na s225 (13/10/2026), na rodada "refinamento visual,
> design system e simplificação do frontend" pedida pelo operador. Regra que muda aqui muda junto no código e no teste
> que a trava (§7). Memória do harness sobre UI é só ponteiro para este arquivo.

## 1. Direção

**Fosco em camadas (tema v4, s227, 13/10/2026)**: o retrowave do v3 lido do controle DualSense GTA VI que ele trouxe
como referência ("o exemplo que mais se aproxima"): o corpo preto fosco é o fundo; o cromado azul -> violeta é a luz
(atrás do topo) e o fio de 1 px que acende o topo de cada placa, nunca uma superfície; os símbolos rosa são o detalhe
(marca, etiquetas, o anel de cards); o texto é branco quente. Queixa que o v4 resolve, nas palavras dele: *"ainda muito
'chapado' no fundo, sem blocos e divisões, fluidez e coesão, otimização do espaço"*. PRD:
`.vibeflow/prds/hub-tema-v4-fosco-em-camadas.md` (specs `hub-tema-v4-part-1..4`).

**A regra que concilia o v4 com o A5 da s225:** um bloco (`.placa`) por SEÇÃO, nunca uma caixa por número; dentro da
placa, as linhas com filete seguem. Profundidade = degrau de superfície + borda + fio cromado. Sem glow, sem sombra, sem
halo (decisão dele, 13/10: "fosco em camadas"; os mockups com borda neon ficaram de fora).

Princípio que segue do v3 (do brief dele, 13/10/2026): *"a interface deve lembrar Vice City à primeira vista, mas
desaparecer em segundo plano quando o estudante estiver concentrado no conteúdo."*

Prioridade, nesta ordem: (1) clareza e baixa carga cognitiva; (2) legibilidade e acessibilidade; (3) hierarquia e
consistência entre telas; (4) minimalismo funcional; (5) identidade retrowave deliberada e contida; (6) código simples.

Ele lê **no celular (390 px), à noite, entre plantões**. Toda decisão é conferida primeiro a 390 px.

A identidade mora em poucos lugares: a marca (`Med` + `Hub` em ciano, s226), a **linha do horizonte** sob as abas (rosa ->
roxo -> ciano), a **luz** atrás do topo e o **fio cromado** das placas (azul -> violeta), e o roxo do gráfico de previsão
do Painel. O resto é tipografia, superfície, filete e espaço.
⚰️ *13/10/2026 (s227, tema v4): era "a linha do horizonte sob as abas (o único gradiente da UI: rosa -> roxo -> ciano)". O
v4 acrescentou dois gradientes de material (`--luz`, `--cromado`); nenhum deles é cor de dado nem fundo de texto.*

Ele lê no celular, então a 390 px tudo é uma coluna de placas empilhadas; no desktop o shell e o Painel usam a coluna
larga (`--largura`, 72rem) com placas em grade, e a leitura longa (aula, enunciado, card) segue na medida `--wrap`
(46rem).

## 2. Onde mora cada coisa

| Camada | Arquivo | O que tem | Quem recebe |
|---|---|---|---|
| Tokens + base | `core/templates/tema.css` | as duas paletas (escuro padrão, claro por `data-theme="light"`), escalas de espaço, raio e tipo, apelidos legados e das aulas, base comum (fonte, foco, seleção, movimento, o fundo com a luz) e a primitiva `.placa` (s227) | shell do hub, painel, player standalone, leitor de aulas e resumos |
| Casca, Teoria, Listas, leitor | `core/templates/hub.html` (bloco `<style>`, depois de `/* @hub:player-css */`) | abas, Teoria (`qd-*`), Listas e questão (`qz-*`), barra do leitor, assinatura de leitura (`hub-assina*`) | o hub |
| Cards | `core/templates/player.html` (região `@player:css`) | o player FSRS e a tela de fim | o hub (aba Cards) e o standalone do `fsrs_queue.py --build-player` |
| Painel | `tools/painel.py` (constante `CSS`) | o dashboard (Hoje, Ritmo, Até 01/11, Por bloco, Revisões 7 dias), Plano de hoje / Semana, Documentação | `artifacts/painel.html` (iframe no hub) |
| Leitor de aulas e resumos | `core/templates/tema-aula.css` | a camada de leitura sobre o CSS próprio de cada aula (43 em `artifacts/aula-*.html`) e da página de resumo | só o leitor (injetada depois do `tema.css`) |
| Página de resumo | `tools/hub.py` (constante `CSS_RESUMO`) | paleta e estrutura próprias da página de resumo publicada | a página aberta fora do leitor; no leitor o tema vem por cima |
| CSS injetado pelo JS do hub | `core/templates/hub.html`: `painelListas` (selos e "+N" no painel), `pendEstilo` (formulário de pergunta nos documentos), `grifoEstilo` (marca-texto no leitor) | estilos que o hub põe dentro dos iframes | painel e leitor |

Como entra: o `tools/hub.py --build` injeta o `tema.css` no fim do `<style>` do shell (marcador `/* @hub:tema-css */`)
e, junto com o `tema-aula.css`, no leitor (`"@hub:tema-js"`, aplicado no `srcdoc` de cada aula/resumo); o
`tools/painel.py` embute o `tema.css` depois do próprio CSS; o `--build-player` embute antes do `</head>`
(`fsrs_queue.embutir_tema`).

**Regra de casa:** cor literal só no `tema.css`. Componente mora no arquivo da tela, nunca no `tema.css` -- com UMA
exceção declarada (s227): a primitiva `.placa`, usada pelas quatro telas; nenhuma tela a redefine, todas compõem
(`class="placa dash-hoje"`), e o teste trava uma regra só. Trocar a paleta = trocar os dois blocos de cor do `tema.css`,
montar o hub em scratch e conferir (§8) antes de publicar. Dentro do hub, o painel e o leitor rodam em iframe com fundo
TRANSPARENTE (elemento `.hub-quadro` e documento, injetado no `preparar`): a luz é a do shell, sem emenda no topo do
quadro; fora do hub eles pintam o próprio fundo.

## 3. Tokens

Seletores `:root:not([data-theme="light"]),:root[data-theme="dark"]` (escuro) e `:root[data-theme="light"]` (claro), de
especificidade (0,2,0) de propósito: vencem o `@media` escuro que cada aula traz no próprio CSS.

| Token | Escuro | Claro | Uso |
|---|---|---|---|
| `--papel` | `#0C0C12` | `#F4F3F8` | fundo da página (o corpo do controle); leva a `--luz` no topo |
| `--card` | `#15151E` | `#FFFFFF` | a placa (superfície de seção); card do player; alternativa; assinatura |
| `--afundado` | `#1E1D2A` | `#ECEAF3` | superfície elevada/selecionada dentro da placa; trilho vazio; badge |
| `--linha` | `#2B2A3A` | `#DFDCE8` | filete interno (linha de lista dentro da placa) |
| `--borda-placa` | `#3A3852` | `#C2BCD4` | borda da placa contra o fundo (>= 1,6:1, s227) |
| `--trilho` | `#312F49` | `#D3CFE1` | trilho vazio de barra e anel sobre a placa (>= 1,35:1, s227) |
| `--linha-forte` | `#6E6A8A` | `#7F7A9C` | borda de controle (campo, botão secundário): >= 3:1 |
| `--tinta` | `#F6EFEA` | `#1A1626` | texto principal (branco quente), títulos, pergunta |
| `--tinta2` | `#BDB7CC` | `#4A4560` | texto secundário, rótulos |
| `--tinta3` | `#948FAA` | `#5F5A78` | metadados |
| `--acento` / `-tinta` / `-fraco` | `#00D9E8` / `#7DE8F0` / `#0E2B36` | `#00737D` / `#005A62` / `#DDF1F4` | ciano: interação |
| `--rosa` / `-fraco` | `#FF4FA3` / `#33172C` | `#C2176F` / `#F8E1EE` | marca e detalhe (os símbolos do controle) |
| `--roxo` / `-tinta` / `-fraco` | `#AA71E8` / `#BE95F0` / `#261C3E` | `#7443B8` / `#5E3596` / `#ECE3F8` | decoração, dado visual, desatenção e chute |
| `--ok` / `-fraco` | `#79D6A5` / `#172A26` | `#1E7348` / `#E2F2E8` | sucesso |
| `--erro` / `-fraco` | `#FF7C87` / `#331B24` | `#B8303E` / `#FBE5E8` | erro (coral) |
| `--aviso` / `-fraco` | `#FFBE72` / `#33261C` | `#8F5200` / `#FAEBD7` | aviso e atraso (âmbar) |
| `--sobre` | `#0C0C12` | `#FFFFFF` | texto sobre preenchimento (botão primário, declaração ligada) |
| `--fc` / `-fraco` / `-tinta` | `#FF5FAE` / `#55204A` / `#FF9ACB` | `#C2176F` / `#F2C2DC` / `#9E0F58` | Flashcards da semana (s228): pico, lavagem dos dias, número; `fc` >= 3:1 e `fc-fraco` >= 1,3:1 contra a placa, `fc-tinta` >= 4,5 como texto (teste do tema) |
| `--qz-grifo` / `-tinta` | `#FFD447` / `#0C0C12` | `#FFE066` / `#1A1626` | marca-texto (literal: o hub lê o valor computado para o leitor) |
| `--cromado` | azul `#2F7BFF` -> violeta `#7A4DFF` -> `#B04FE0`, apagado nas pontas | idem, mais escuros | o fio de 1 px no topo da placa (reflexo, não faixa) |
| `--luz` | duas `radial-gradient` (azul à esquerda, violeta à direita, 20-24%) | idem a 6-7% | a luz atrás do topo (marca e abas) |
| `--horizonte` | rosa -> roxo -> ciano | idem, escuros | a linha sob as abas |

Contraste **medido pelo `tools/test_tema_contraste.py`** (lê os hex do `tema.css`, WCAG 2.x; s227: a tabela deixou de ser
digitada), sobre `papel` / `card` / `afundado`. Escuro: `tinta` 17,1 / 15,9 / 14,6; `tinta2` 10,0 / 9,3 / 8,5; `tinta3`
6,3 / 5,8 / 5,4; `acento` 11,2 / 10,4 / 9,6; `rosa` 6,4 / 6,0 / 5,5; `roxo-tinta` 8,1 / 7,6 / 6,9; `ok` 11,1 / 10,3 / 9,5;
`erro` 7,9 / 7,3 / 6,7; `aviso` 11,9 / 11,1 / 10,2; `linha-forte` 3,8 / 3,5 / 3,2; borda da placa contra o fundo 1,73.
Claro: todos os textos >= 4,7 nas três superfícies (`acento` 4,7 sobre o elevado); `linha-forte` 3,4+; borda da placa
1,66. `--sobre` sobre os preenchimentos: 5,8 (roxo) a 11,9 (aviso) no escuro, 5,6+ no claro. O `roxo` puro como texto
segue proibido (4,9 sobre o elevado escuro): texto roxo usa `--roxo-tinta`.

Apelidos: `--alerta` = `--erro` (nome antigo); `--qz-ok/-duv/-chute` = ok/aviso/roxo-tinta; `--suave` = roxo. As aulas
usam nomes próprios em inglês: `--paper --ink --ink2 --ink3 --line --line2 --sunk --card --on`, `--teal*` (= acento),
`--amber*` (= aviso), `--plum*` (= roxo), `--carmine*` (= erro).

Escalas (em `:root`, valem nos dois temas):
- espaço: `--esp-1` 4 · `--esp-2` 8 · `--esp-3` 12 · `--esp-4` 16 · `--esp-5` 24 · `--esp-6` 32 · `--esp-7` 48 px;
- raio por nível (s227): `--raio-placa` 14 px (a placa) · `--raio` 10 px (cartões e controles) · `--raio-p` 6 px (kbd, grifo, aviso) · `--raio-pilula` (só badge e chip);
- tipo: `--fs-pagina` 1,5rem · `--fs-secao` 1,125rem · `--fs-item` 1rem · `--fs-legenda` .875rem · `--fs-meta` .8125rem ·
  `--fs-numero` 2rem;
- coluna: `--wrap` 46rem = a medida de leitura (~85 caracteres por linha no desktop); `--largura` 72rem = a coluna larga do
  shell e do painel no desktop (s227). Um `.wrap` só por página: o shell troca só a largura do mesmo contêiner.

Tipo: **Atkinson Hyperlegible Next**, uma família só (decisão dele, s224: 0/O e 1/l distintos em dose e corte), com
algarismos tabulares e sem caixa-alta (`text-transform:none` global).

## 4. Semântica das cores

- **Ciano**: navegação ativa (aba, segmento), foco, progresso (barras, trilho atual, o "necessário por dia"), ação
  primária (botão `.primario`), o rótulo "Próxima" do Painel e link. Nunca título nem rótulo.
- **Rosa**: a marca e destaque pontual (`nova` na Biblioteca). Nunca estado.
- **Roxo**: decoração e dado visual (gráfico de previsão, número do degrau das aulas) e os estados chute/desatenção.
- **Marca-texto (grifo), s227 (part-6, pedido dele: "poderia apenas manter a cor do texto e mudar o fundo dele"):** pinta
  só o FUNDO (lavagem `--grifo-*` a 32%; 70% no amarelo do claro) e o texto mantém a cor (`color:inherit`). Uma cor
  ativa: **rosa (padrão), ciano ou amarelo**, lembrada no aparelho (`medhub.grifo`).
  **s228 (pedido dele: "alterando apenas a cor dos próximos grifos, e não todos, mas sobretudo em um botão que apareça só
  dentro do bloco de teoria, e que seja um botão único, que quando clicamos ele expande em cascata com as 3 opções"):**
  a cor ativa vale só para os PRÓXIMOS grifos. Cada grifo do leitor guarda a cor com que nasceu (`cor` no registro de
  `analises/grifos/itens/<slug>`, gravada só quando não é rosa; grifo salvo antes, sem `cor`, segue rosa), é pintado
  por `mark.hub-grifo[data-cor]` e nunca muda quando a ativa troca; grifos de cores diferentes não se fundem. O seletor
  é UM botão (`#hub-grifo-btn`, amostra da ativa + "Grifo", 44 px, `aria-expanded`) na barra do leitor da Teoria, à
  direita do título -- saiu do topo e não aparece em outra tela; tocar abre as 3 cores em cascata (lista vertical sob o
  botão, atraso de 60 ms por opção, `aria-pressed` + contorno ciano na ativa); escolher, tocar fora ou Esc fecha. Nas
  questões (sem o seletor) o grifo fica no rosa padrão (`--grifo-rosa`), sem cor no dado.
  ⚰️ *s227 (part 6): "uma cor ativa vale para todos os grifos", 3 botões no topo do hub; o leitor aberto repintava.*
  ⚰️ *13/10/2026 (s227): era "**Amarelo**: marca-texto (grifo)", com o texto escuro sobre o amarelo cheio.*
- **Verde / coral / âmbar**: sucesso, erro, aviso. Atraso é aviso (âmbar), não erro.
- **Branco suave**: pergunta, resposta, títulos, conteúdo. **Lavanda**: secundário e metadado.
- Estado nunca só por cor: gabarito `✓`, errada `✗`, chute `?`, resolvida `✓`, "abaixo do necessário" por extenso,
  declaração com o nome do estado no botão.
- A declaração dos elos (`Sim / Incerteza / Desatenção / Não`) e a nota do card (`1 falhei / 2 com esforço /
  3 lembrei / 4 sem esforço`) seguem a mesma escala: ok, aviso, roxo, erro / erro, aviso, ok, acento.

## 5. Componentes

| Padrão | Onde | Forma |
|---|---|---|
| Placa (s227) | uma por seção em todas as telas (parts 1-4 do tema v4) | primitiva `.placa` do `tema.css`: `--card` + borda 1 px `--borda-placa` + `--raio-placa` + fio cromado de 1 px no topo (`::before`, apagado nas pontas); padding 16 px no celular, 24 px acima de 520 px; sem sombra; a tela compõe, nunca redefine; dentro dela, as linhas com filete; nunca uma placa por número. **Questão (part 4):** placa do enunciado (meta, texto, figuras) e placa do resultado (veredito, cadeia, análise, rodapé); alternativas, certeza e botões no fundo, com a moldura própria; no fim, métricas, por bloco, Elos e revisão, uma placa cada. **Leitor:** o iframe numa placa sem padding (a aula tem o próprio; com 16 px a coluna perderia 32 px a 390) e a assinatura na placa de baixo, da mesma largura (`.hub-assina.placa{margin-inline:0}` vence o alinhamento R9) |
| Linha de lista | Teoria (`.qd-bloco`), Listas (`.qz-lista button`), Painel (`.tarefa`), revisão (`.qz-rev`), por bloco (`.qz-porobj li`), cadeia (`.qz-cadeia li`) | sem fundo e sem caixa própria, DENTRO da placa da seção (v4); filete de baixo (`--linha`); título 600 em `tinta`, meta em `tinta3` |
| Moldura | card do player, alternativa da questão, campo, assinatura de leitura | só o que é objeto de toque ou o foco da tela; `--card` + `--linha` + `--raio`; sem sombra |
| Badge | área (`.qd-bl`), objetivo (`.qz-obj`), "Próxima"; no Painel `.t-rot` | pílula, `--afundado` + `tinta2` (o "Próxima" em ciano); no Painel `.t-rot` em `--rosa-fraco` + `--rosa`, como o "novas" da Biblioteca (s226, pedido dele) |
| Chip de estado | lista (`.qz-chip`, `qzChip`) | só fora do normal: "pronta" não tem chip; em curso = aviso com respondidas/total (espelho do aparelho); resolvida = ok + `✓` |
| Botão | global (`player.html`) | secundário: contorno `--linha-forte`, fundo transparente; `.primario`: ciano com texto `--sobre`; `.fantasma`: tracejado; 44 px de altura |
| Segmentado | Questões/Simulados (`.qz-modo`), certeza (`.qz-seg`), declaração (`.qz-decl`) | raio de controle; ligado = cor do estado + lavagem |
| Abas | `.hub-aba` | texto; ativa em `tinta` com uma barra de 2 px que é o TRECHO do horizonte sob ela (`background-size:400%`, posição por `nth-child`; s226, pedido dele); o filete de baixo é o horizonte |
| Dashboard | topo do Painel (`section.dash`, `data-bloco="dia"`; Ritmo e Por bloco com o `data-bloco` deles por dentro, `.dash-sec`) | s226: Hoje · Ritmo · Até 01/11 · Por bloco · Revisões 7 dias, cada parte sob um filete; tiles = um número por tile (`.fracao b`), barra fina e rótulo curto `tinta3` (`.kpi-r`), sem caixa e **sem `p.nota`**; com sprint o único por-dia é o do sprint (`q_hoje` no tile, real 7 d contra a `capacidade_q` no Ritmo) e a meta aparece uma vez, como alvo da **barra de projeção** (`.proj-barra`: feito ciano · cumprindo o sprint lavagem ciano com contorno · fora do sprint `--linha` tracejado em `--tinta3`, 2 px de fundo entre trechos, `role=img` com os números no `aria-label`); **Por bloco** em linhas (`.bl`: nome · barra de acerto 0-100% · % · feitas/total), o de menor acerto em âmbar com o rótulo "mais fraco", Simulados na última linha (s228: barra em `--roxo`, o token do anel Até 01/11; era neutra); `title` em cada linha e trecho = dica ao passar o mouse; HTML/CSS puro (o painel não carrega lib) **v4 (s227, tema v4 part-2):** a `section.dash` é a GRADE de cinco `.placa` (Hoje · Ritmo · Até 01/11 · Por bloco · Revisões), uma coluna e, com o iframe a partir de 760 px, duas (Hoje | Ritmo, Até 01/11 em `1 / -1`, Por bloco | Revisões), vão `--esp-4`, o mesmo até as placas do Plano de hoje e da Documentação; sem filete entre seções. **Hoje** = dois anéis concêntricos em SVG inline (viewBox 120, traço 10, `pathLength=100`): externo `--acento` = questões / `q_hoje` (sem sprint, o alvo da meta), interno `--rosa` = cards / teto, trilho `--trilho`, 0% = só o trilho, centro = o dia; nenhum número soma as duas unidades (o '226' dos mockups ficou de fora); legenda com 'X de Y' + `kpi-r` + 'Ir para os cards', ao lado do anel a partir de 26rem (`@container`); o `b[data-vivo]` fica na legenda e o anel no valor publicado. **Ritmo** = barra `.rb` do real 7 d contra UMA marca (`--tinta`, '80/dia'; sem sprint, o necessário por dia), escala 1,25x o maior, âmbar abaixo / verde em dia; sem gauge. **v4.1 (s227, part-5, pedido dele: "o 'Painel' ainda está muito disperso. Esses 4 blocos deveriam aparecer junto no topo, através desses anéis com percentual"):** o topo é UMA placa "Hoje, terça 13/10" com 4 anéis (`.an4`, % no centro, rótulo + valor + uma linha abaixo): Questões (`--acento`, contra o `q_hoje`), Cards (`--rosa`, contra o teto, com 'Ir para os cards'), Ritmo em 7 dias (`--aviso` abaixo / `--ok` em dia, sempre com o texto; `data-bloco="ritmo"` no anel; '23,5 em 14 dias · 78,4% de acerto'), Até 01/11 (`--roxo`: feito contra a meta + um 2º arco, roxo a 50%, até o que o sprint entrega; a meta 10.000 só aqui); 2 x 2 a 390, 4 em linha a partir de 600 px de iframe. Abaixo, Por bloco | **Flashcards da semana** (ex-'Revisões nos próximos 7 dias'), lado a lado a partir de 760 px, mesma altura. **s228 (pedido dele: "melhorar a estética do bloco de flashcards da semana, até com liberdade para rever a paleta"):** paleta própria `--fc*` (a família rosa do anel de Cards; era roxo): o total da semana no cabeçalho (`.ag-total`, número em `--fc-tinta`), os dias em lavagem `--fc-fraco`, o PICO em barra cheia `--fc` com o número em destaque e "(pico da semana)" na dica, linha de base `--linha-forte` sob as barras. A barra de projeção e a barra do Ritmo saíram (`cronograma-contract` v1.8). |
| Métricas | fim da lista (`.qz-tiles`), fim do lote (`.fim-grade`), Ritmo (`.fig`) | uma faixa entre dois filetes, número 700 + rótulo `tinta3`; sem uma caixa por número |
| Aviso | `.hub-aviso`, `.aviso` (player) | filete âmbar de 3 px + lavagem âmbar; `.aviso.forte` (banco fora) com borda inteira |
| Trilho | `.qz-trilho i` | 10 px visíveis, 26 px de toque; respondida = `--linha-forte`, atual = ciano, marcada para revisar = base âmbar (`flag`), vazia = `--afundado` |
| Barra de progresso | painel (`.bl-barra`; o `.rb` do Ritmo virou anel na s227), player (`.barra`, `.dist-barra`) | 6-10 px, trilho `--trilho` (s227: o `--afundado` some sobre a placa, 1,1:1; o `--trilho` dá 1,4:1), preenchimento sólido ciano |
| Leitura resiliente | `assinarResiliente(consulta, onDados, opts)` no `hub.html`: listas, quadro da Teoria, questões/respostas/análises da lista aberta, notas do lote | `consulta(db)` monta a referência sobre o `db` recebido (1ª tentativa = `opts.db`; da 2ª em diante e no "Tentar de novo", conexão nova por `claude.use("db")`, avisada em `opts.aoReconectar` -- o `QZ.db`); erro = `console.warn("[hub] leitura <coleção> falhou", código, tentativa)` + nova assinatura em 1/2/4 s com "Carregando…"; esgotadas, a mensagem + botão `.primario` **Tentar de novo** (`htmlRetentar`); reabrir a aba com ela morta reassina; um estado por assinatura, nunca 2 ouvintes. Aba nova lê por ela |
| Secções do card | `.bloco` (regra-mestre), `.bloco.alerta` (armadilha) | filete à esquerda (neutro / âmbar), nunca caixa dentro do card |

## 6. Telas: o que cada uma prioriza

- **Painel**: responde, nesta ordem, o que fazer hoje (Hoje), quanto avancei (Ritmo, Blocos) e o que vem depois.
  Desde a s226 (painel-dashboard-sprint part-1) Hoje + Ritmo + Até 01/11 + Por bloco + Revisões nos próximos 7 dias são
  UM dashboard no topo (§5); desde a s227 (part-5) ele é uma placa com 4 anéis + Por bloco | Flashcards da semana. O Plano de hoje vem logo abaixo, como a lista do que fazer.
  Com o sprint gravado (s226, `plano.agenda_sprint`, a fonte única do "hoje" do Painel, da aba Listas e do boot), o
  bloco das tarefas é **Plano de hoje** (título; o bloco do topo segue "Hoje") (as tarefas do dia, a que rolou de um dia passado sem rótulo de atraso, o total de
  questões, "+ N cards" que faltam da dose do dia e a RD não assinada mais antiga, a linha inteira abrindo o leitor;
  sem o estado do quadro (`tmp/hub_db/quadro`), nenhuma RD: o Painel nunca afirma "não assinada" no escuro)
  + **Próximos dias** (um dia por linha, "qua 14/10 · 2 listas · 72 q", recolhido) + **Fora do sprint · N**
  (recolhido, agrupado pelo motivo). Sem "Semana", "Atrasadas", "Desta semana" nem "Até a prova". Sem sprint
  (`dia_plano` todo NULL), a semana antiga: o subtítulo "Atrasadas · N" em âmbar, uma vez, nunca por linha. Nos
  dois, a 1ª tarefa leva só o rótulo "Próxima", `li.tarefa.proxima`, o mesmo controle das outras. Na Semana, a tarefa com questões no
  hub é UM alvo (`a.t-alvo` com `data-hub-aba`: a linha inteira abre a lista); a aula ligada fica fora dele, pequena
  ("aula"). Fora do hub (lista externa, PDF), a coluna de ação de antes. O Ritmo fica logo abaixo de Hoje (pedido
  dele, s221).
- **Teoria** (s226, consulta): no topo, **Revisões direcionadas · N** (as RDs não assinadas, da mais antiga para a
  mais nova, a linha inteira abrindo o leitor; a assinada some ao vivo e fica só na Biblioteca); abaixo, a Biblioteca
  por área e disciplina com toda aula, resumo e RD. Sem semana, sem "Atrasadas" e sem contagem de questões.
- **Listas** (s226): na ordem do Plano de hoje, pelo `<script id="hub-sprint">` (`hub.dados_sprint` =
  `plano.agenda_sprint`): **Hoje** (aberto) + **Próximos dias** (um grupo por data, recolhido) + **Fora do sprint · N**
  (recolhido, com o motivo; a lista aberta de tarefa sem dia cai aqui como "sem dia no plano"); resolvidas recolhidas
  no fim. Sem sprint (`hub-sprint` = `null`), as semanas antigas. **Simulados** na sua sub-aba, com a data do sprint
  ("dom 25/10"; o do dia, "hoje").
- **Listas e simulados** (s227, part 4: barra e trilho no fundo, com a largura do corpo, `--wrap`; só wrappers e classes, nenhum id nem gesto mudou, travado por `test_ids_botoes_e_ordem_da_questao_e_do_leitor_nao_mudaram`): o trilho é navegação; a questão revelada tem no máximo 3 blocos (alternativas com o porquê,
  veredito, cadeia com a declaração); a tela de fim mostra a faixa de métricas, o por bloco, o bloco Elos e a revisão.
- **Leitor de aulas**: uma coluna só (`.wrap` de 46rem; a aula antiga com trilho lateral usa o `main` de 38rem);
  títulos brancos, rótulos lavanda; termo-chave em negrito ciano claro (pedido dele, s224: o único texto ciano da
  leitura); callouts por significado (§9).

**Largura (regra dele, reprovada duas vezes quando quebrou):** UM `max-width` no contêiner (`.wrap`) e todos os
filhos herdam 100% dele. Nunca `max-width` por elemento (parágrafo, lede, lista) ao lado de quadro com fundo ou
borda: as bordas direitas fazem zigue-zague. Exceção: manchete sem caixa (`.top h1`).
- **Cards**: o topo (título, 'N de 150 hoje', fila, relógio, pausar, barra, tally) é uma placa; o card é a placa
  elevada (`.card.placa`, `--afundado`) logo abaixo, na medida `--wrap`; os botões ficam fora dela; a tela de fim do lote
  numa placa (s227, part 3). Pergunta > resposta > regra/armadilha > assunto.
  **s228 (pedido dele):** o "Defeito do card D" fica logo abaixo da barra, à direita do tally, no estilo do
  Pausar/Retomar (`.pausa`, `aria-expanded`), e as opções abrem dentro da placa do topo (o registro `defeito` + `motivo`
  não mudou). Tocar no card vira (o mesmo `virar()` do botão e do Espaço; seleção de texto não vira); a frente
  (`.card.frente`) leva cursor de toque, a dica "toque no card para virar" e a borda de controle (`--linha-forte`,
  ciano no hover). Contra o "chapado": pergunta em 700 e maior, o motivo como pílula, o contexto com filete, e o verso
  abre como o DEGRAU de baixo da mesma placa (`--card`, de borda a borda, filete `--borda-placa` em cima), nunca caixa
  dentro do card; resposta em 600.
- **Teoria, Listas e Cards em placas (s227, tema v4 part 3):** uma placa por seção, título dentro, linhas com filete por
  dentro e sem filete na última. Teoria = RDs | Biblioteca (`.qd` em grade; lado a lado a partir de 900 px,
  `align-items:start`). Listas = seletor + legenda (`.qz-cabeca`) fora das placas; Hoje | Próximos dias + Fora do sprint +
  Outras listas (os dias são linhas de 44 px) | Resolvidas; no desktop (`qz-duas`) Próximos ocupa a coluna 2 nas duas
  linhas e Resolvidas sobe para baixo de Hoje; Simulados = provas | resolvidos (`qz-sim`, só com os dois). Na medida
  `--wrap` ficam só o card, o leitor e a questão aberta (`#aba-cards,#hub-leitor,#qz-player`).

## 7. Contratos travados por teste

| Contrato | Teste |
|---|---|
| nada `sticky`/`fixed`, nada `nowrap`, um `.wrap` só | `test_hub.py::test_celular_sem_sticky_sem_nowrap_e_um_wrap_so`, `test_painel.py::test_celular_sem_sticky_sem_nowrap_e_grid_item_encolhe`, `test_hub_render.py::test_forma_da_tela_revelada` |
| abas com rótulo curto e 44 px; `.qd-tema` com `min-width:0` | `test_hub.py::test_abas_curtas_e_com_alvo_de_toque` |
| tela revelada sem cor literal; 44 px nos botões; `.qz-cadeia li` com `min-width:0` | `test_hub_render.py::test_forma_da_tela_revelada` |
| contraste do tema nos dois blocos (texto >= 4,5 nas 3 superfícies, `tinta` >= 7, controle >= 3, borda da placa >= 1,6, `--sobre` >= 4,5); `.placa` com uma regra só, sem sombra nem brilho, sem `max-width` no `tema.css` | `test_tema_contraste.py` (s227) |
| shell v4: luz no `body`, `.hub-quadro` e documento do quadro transparentes, coluna larga, um `.wrap` | `test_hub.py::test_tema_v4_luz_no_shell_e_quadros_transparentes` (s227) |
| Painel v4.1: topo com 4 anéis (Questões, Cards, Ritmo contra o sprint, Até 01/11 com o 2º arco do sprint), Por bloco e Flashcards da semana em placas | `test_painel.py::test_topo_quatro_aneis`, `test_ate_01_11_anel_com_projecao_do_sprint`, `test_ritmo_anel_contra_o_sprint_com_a_cor_e_o_texto`, `test_flashcards_da_semana_renomeado`, `test_dashboard_em_placas_e_a_grade` (s227; os de dois anéis e da barra do Ritmo viraram ⚰️) |
| questão, fim e leitor em placas; ids, botões, `data-*` e ordem da questão e do leitor congelados | `test_hub_render.py::test_questao_fim_e_leitor_em_placas`, `test_ids_botoes_e_ordem_da_questao_e_do_leitor_nao_mudaram` (s227) |
| Teoria, Listas e Cards em placas, grade de 2 colunas no desktop, standalone do player com a placa | `test_hub_quadro.py::test_teoria_em_duas_placas_lado_a_lado_no_desktop`, `test_hub_render.py::test_listas_em_placas_e_a_grade_de_duas_colunas_no_desktop`, `test_cards_topo_e_card_em_placas_e_o_standalone_leva_a_placa` (s227) |
| player e painel sem cor literal (a cor mora no `tema.css`); tema escuro/claro presente na página pronta | `test_fsrs_queue_player.py::test_template_real_e_injetavel_e_tem_wrap_unico`, `test_painel.py::test_html_obedece_o_contrato_de_render` |
| standalone do player recebe o tema | `test_fsrs_queue_player.py::test_embutir_tema_entra_antes_do_head_e_e_idempotente` |
| linha da Teoria acessível (foco de 3 px, sem-aula sem cara de botão) | `test_hub_quadro.py::test_p21_cartao_alvo_e_acessivel_e_o_sem_aula_nao_parece_botao` |
| Painel com sprint: Plano de hoje / Próximos dias / Fora do sprint, sem semana nem atraso; sem sprint, a semana antiga; sem estado do quadro, nenhuma RD | `test_painel.py::test_painel_sprint_sem_semana`, `test_hoje_do_sprint_soma_os_cards_do_dia_e_a_rd_nao_assinada`, `test_sem_sprint_o_painel_mostra_a_semana_antiga`, `test_sem_estado_do_quadro_o_painel_nao_afirma_rd_nao_assinada` |
| Teoria sem semana: backlog de RDs no topo + Biblioteca; a assinada some do backlog ao vivo | `test_hub_quadro.py::test_teoria_sem_semanas_com_o_backlog_de_rds_e_a_biblioteca`, `test_backlog_de_rds_da_mais_antiga_e_a_assinada_so_na_biblioteca`, `test_hub_render.py::test_rd_assinada_some_do_backlog_e_perde_a_etiqueta_na_biblioteca` |
| Listas = o mesmo "hoje" do Painel (Hoje / Próximos dias / Fora do sprint); simulado com a data | `test_hub_render.py::test_listas_e_painel_mesmo_hoje`, `test_listas_agrupam_por_hoje_proximos_dias_e_fora_do_sprint`, `test_simulado_leva_a_data_do_sprint`, `test_sem_hub_sprint_as_listas_caem_nas_semanas` |
| dashboard: com sprint o tile de Questões = `q_hoje` do sprint e o Ritmo contra a `capacidade_q`, sem "por dia até a prova", meta 1x; sem sprint, a meta; projeção com os 3 números; Por bloco em linhas com "mais fraco"; nenhum `p.nota` no dashboard; o `q_hoje` do tile = o do boot | `test_painel.py::test_dashboard_questoes_usa_o_q_hoje_do_sprint`, `test_dashboard_sem_sprint_volta_a_meta`, `test_barra_de_projecao_feito_sprint_meta`, `test_por_bloco_em_linhas_com_barra_e_o_mais_fraco_rotulado`, `test_plano_dia.py::test_boot_painel_listas_mesmo_hoje` |
| painel sem jargão de bastidor (inclusive nos comentários do `tema.css`, que viaja embutido) | `test_painel.py::test_html_sem_jargao` |
| leituras das abas pela assinatura resiliente (retentativa, botão, 1 ouvinte); chip só fora do normal; marca 1,375rem | `test_hub_render.py::test_listas_se_recuperam_da_falha_de_leitura`, `test_botao_tentar_de_novo_reassina`, `test_leituras_das_abas_passam_pela_assinatura_resiliente`, `test_chip_da_lista_so_fora_do_normal` |
| a retentativa pede conexão nova ao banco (e o `QZ.db` passa a ser ela) | `test_hub_render.py::test_retentativa_pede_conexao_nova` |
| o `max-width` aparece no máximo 2 vezes na página do player e na do painel | os dois testes de contrato acima |

## 8. Como conferir (obrigatório antes de publicar tela nova)

Regra da casa: tela nova do hub só publica conferida em navegador real, a 390 px. Caminho:
1. `python tools/painel.py --html` e `python tools/hub.py --build --lote <lote vivo> --publicado <listagem> --quadro-estado tmp/hub_db`.
2. Capturas com banco falso no Edge headless, a 390, 768 e 1280 px: `python tools/ui_capturas.py` (11 cenas: painel,
   teoria, listas, simulados, questao, revelada, fim, cards, verso, aula, resumo; mede rolagem horizontal e erro de JS;
   assinatura e limites em `/engenharia-cli`). Saída em `tmp/ui_capturas/<data>/`. O seed vem dos dumps locais do db do hub em `tmp/` (conteúdo do EMED: nunca no git).
3. Ler as capturas (ferramenta Read) e conferir: hierarquia, rolagem horizontal, estados e contraste.
4. Rodar as suítes `tools/test_hub*.py tools/test_painel.py tools/test_fsrs_queue_player.py`.

## 9. Leitor de aulas (`tema-aula.css`)

Inventário completo das 43 aulas (s225, medido com parser + Edge): `docs/research/2026-10-13-05-ui-auditoria-aulas.md`
(6 famílias de classe: EN15 com `.nav`/`.stats` sem `<main>`, ER6 com `.rail` + `main`, RS13, RG7, dossiê, autópsia). Achados
L1-L15 (§14 de lá; medidos na camada ANTIGA, def2fdd) e o estado na camada v3:
- **L1** `.tw` cortada pelo `overflow:hidden` (até 424 px a 390): **resolvido** (hub v105; a tabela rola na caixa).
- **L3** espaçamento de caixa-alta nos rótulos: **resolvido** nos rótulos citados (`.eye .kick .dstage .rlab .albl th .tag .tk`, `h3/h5` de `.vs`).
- **L5** negrito ciano com exceções por descendente: **resolvido** (mesma especificidade das aulas).
- **L7** `h4.sub` e **L8** `.dtitle h3`: **resolvidos**.
- **L4** callouts sem critério único: **resolvido na v4** (s227: `.key`, `div.note`, `.disc`, `.fonte`, `.star` viraram nota neutra; trap = âmbar, banca = roxo); resta o `.ext` da `dmg`.
- **Referências no fim (s227, part-7, pedido dele: "remover todos os 'Fonte:...' espalhados pelo texto, e concentrá-los
  ao final, tal como um artigo"):** no leitor, a "Fonte:" com cara de referência sai do texto (`ehReferencia`, pura; a
  "Fonte:" clínica, como a do sangramento no TCE, fica). Referência externa vira lista numerada no fim
  (`section.hub-refs`, título "Referências") com um sobrescrito ciano no lugar; base interna (`ehBaseInterna`: resumo do
  MedHub, verso de card, PDF/apostila do curso) vai para "Base deste documento", sem número. O bloco que sai deixa um
  marcador vazio (os grifos não mudam de índice). A aula nova traz `sup.ref`, `section.refs` e `p.base` (`aula-base`
  §6), com a mesma regra no `tema-aula.css`; a aula na fonte não muda (migra na reforma com a /anima). Alcance medido
  em 13/10: 116 "Fonte:" em 36 aulas e 8 resumos; nas aulas publicadas, quase tudo é base interna (a troca por diretriz
  é o trabalho seguinte).
- **v4 (s227, part 4):** no leitor, `--paper` = a cor da placa e `--card` = o elevado, para nenhuma caixa interna ter a cor da placa; `figure.fig-an` com fundo da placa e `--borda-placa`; `.trilho-box` sem moldura; `ol.esc` das RDs como lista. Conferido a 390 nos dois temas (RD com figura `rd-cir-1310`, ER `kawasaki`, EN `tb-360`). O `ui_harness.html` ganhou `?tema=light|dark` e `?doc=aulas/x.html` (o `ui_capturas.py` ainda não tem flag para eles).
- **L6** h3/h4/h5 como rótulo dentro de `.vs .tgrp .blk .cmap .if3`: **pendente**.
- **L9** outliers de paleta (autópsia: 18 tokens próprios; neuromusculares: `--acc*`): **pendente** (mapeamento no §8.3 do inventário).
- **L2, L10-L15**: **pendentes** (ver o inventário).

**Figura de mecanismo na aula (s226, painel-dashboard-sprint part-2, teste nas 5 RDs da UERJ 2022):** `figure.fig-an`
no CSS da própria aula -- moldura `--card` + `--line2` (cabeçalho "Fig n · esquema" à esquerda e o título à direita),
SVG inline com `viewBox` e `max-width:26rem` dentro da moldura, `role="img"` + `aria-label` com o que a figura diz,
legenda curta + o número da referência (s227: sem "Fonte:" na legenda; as fontes vão para as Referências no fim, `aula-base` §6).
Cor só pelos apelidos das aulas (`--teal*`, `--amber*`, `--plum*`, `--ink*`,
`--line2`, `--sunk`, `--card`): herda o claro e o escuro do leitor. Nenhum fato que a seção não diga; dado ilustrativo
declarado na própria figura. Conferida a 390/768 nos dois temas com o mesmo esqueleto do `documentoCompleto` do leitor.
⚰️ *13/10/2026 (s227): era "legenda curta + `Fonte:` = a fonte da seção". Motivo: pedido dele de concentrar as fontes no fim, como num artigo.*

## 10. Achados da varredura s225 (13/10/2026)

| # | Achado | Onde | Estado |
|---|---|---|---|
| A1 | Três paletas sobrepostas: tokens claros/escuros antigos (verde-água) no `player.html`, uma cópia no `painel.py` e o `tema.css` por cima | player, painel, tema | **resolvido**: paleta só no `tema.css`; player e painel só estrutura; o standalone embute o tema; teste trava cor literal |
| A2 | O `tema.css` misturava regras do hub, do painel, do player e das aulas, sobrescrevendo a regra-base por especificidade (duas definições por componente) | `tema.css` | **resolvido**: cada regra voltou ao arquivo da tela; o `tema.css` tem só tokens e base |
| A3 | Rosa servia de alerta e de identidade; `--alerta` servia erro e aviso | todas | **resolvido**: rosa = marca; erro = coral; aviso = âmbar; `--alerta` é apelido de `--erro` |
| A4 | Títulos, rótulos e cabeçalhos todos em ciano (v2.4) | hub, painel, aulas | **resolvido**: títulos em branco, hierarquia por tamanho e peso; ciano só na interação |
| A5 | Caixas preenchidas em série: tiles do fim, por bloco, revisão com faixa lateral, cadeia em caixas centralizadas, regra-mestre e armadilha como caixas dentro do card, números do Ritmo, fim do lote | hub, player, painel | **resolvido**: linhas com filete; métricas numa faixa; cadeia alinhada à esquerda e numerada. **s227:** a superfície de SEÇÃO voltou (A24) -- a regra é uma placa por seção, nunca uma caixa por número |
| A6 | Estado só por cor: gabarito/errada, revisão certa/errada/chute, ritmo abaixo, lista recém-concluída | hub, painel | **resolvido**: `✓ ✗ ?` e "abaixo do necessário" por extenso |
| A7 | Trilho com todos os segmentos no mesmo brilho; "revisar depois" invisível nele; alvo de 14 px | Listas | **resolvido**: respondida, atual, marcada e vazia distintas; classe `flag` no JS; 26 px de toque |
| A8 | Controles em pílula (declaração, Questões/Simulados) com o formato reservado a badge | Listas | **resolvido**: raio de controle |
| A9 | Borda de campo e de botão a 1,6:1 (invisível) | hub, player | **resolvido**: `--linha-forte` (3,2 a 3,8:1) |
| A10 | Brilho no título da aula e gradiente nas barras de progresso | tema, painel, player | **resolvido**: barras sólidas; sem `text-shadow` |
| A11 | Vermelho literal `#b3261e` no erro do formulário de pergunta dentro dos documentos (ilegível no escuro) | `hub.html` (`pendEstilo`) | **resolvido**: `var(--erro, #b3261e)` |
| A12 | O kit de conferência visual (banco falso, montagem do site, capturas) existia só em `tmp/` (gitignorado) | `tmp/design`, `tmp/alca_s213` | **resolvido**: `tools/ui_capturas.py` + `core/templates/ui_harness.html` (11 cenas, rolagem horizontal medida; §8) |
| A13 | `.qz-lista button` (0,1,1) vencia `.qz-rev` (0,1,0) e espremia a revisão em 2 colunas | `hub.html` | **resolvido**: `.qz-lista .qz-rev` |
| A14 | Coluna de 58rem: ~110 caracteres por linha no desktop | `--wrap` | **resolvido**: 46rem |
| A15 | O "próximo passo" não existia como elemento no Painel | painel | **resolvido**: a 1ª tarefa da Semana leva "Próxima" e a ação como botão primário |
| A16 | Página de resumo publicada tem paleta própria (verde-água antigo) para quando abre fora do leitor | `hub.py` `CSS_RESUMO` | **pendente** (baixo impacto: no leitor o tema vem por cima; mudar republica 31 resumos) |
| A17 | Tema claro só por `data-theme="light"`; o hub ignora `prefers-color-scheme: light` de propósito | `tema.css` | **decisão dele** (s224: escuro por padrão); o claro foi refeito na mesma semântica |
| A18 | Aba que não carrega ("Não consegui ler as listas"): a assinatura de `listas` (e a do quadro da Teoria) é feita uma vez só e não tenta de novo depois de uma falha | `hub.html` `iniciarQuestoes` | **resolvido** (s226, part-1): `assinarResiliente` (1/2/4 s + Tentar de novo) e log no console com o código para medir o gatilho real |
| A19 | Cards: o Painel conta o saldo do dia (X de 150) e a aba Cards o lote no ar (3/100), que é de 10/10 (backend manual) | `painel.py`, `player.html`, `/hub-backend` | **pendente**: mesmo PRD (decisão dele: contador do dia + fila diária) |
| A20 | Semana do Painel: "resolver no hub"/"abrir aula" repetidos por linha, "da semana N" em cada atrasada, a Próxima com controle de outro tipo | `painel.py` | **pendente**: mesmo PRD (linha clicável, aviso uma vez) |
| A21 | Listas: chip "pronta" repetido em toda linha (informação nula) | `hub.html` `qzItem` | **resolvido** (s226, part-1): `qzChip` |
| A22 | Marca "MedHub" pequena no topo | `hub.html` `.hub-marca` | **resolvido** (s226, part-1): 1,375rem; "Hub" passou a ciano na s226 (pedido dele) |
| A24 | "Chapado": toda tela uma folha só no mesmo fundo, seções separadas por filete de 1,3:1 que quase não se vê; nada à frente de nada; a 1280 px a coluna de 46rem deixa ~60% vazio | todas | **em curso** (s227, tema v4): fundo preto + placa por seção (borda 1,7:1 + fio cromado), coluna larga no desktop; parts 2-4 aplicam por tela |
| A23 | Sem o espelho local `medhub.respostas.<lista>`, o 1º snapshot de `questoes` chega antes do de `respostas` e a Q1 aparece como nova mesmo respondida (lido no código pelo subagente, não medido) | `hub.html` | **pendente**: mesmo PRD (família do A18) |

## 11. Histórico de decisões

- **Tema v4 "fosco em camadas" (13/10, s227)**: pedido dele com 7 referências na raiz (controle DualSense GTA VI, pins
  Vice City, 5 mockups): *"manter a 'riqueza' do retrowave/95', mas deve ser sóbrio e minimalista como uma plataforma de
  estudos deve ser [...] predomínio de tom escuro, rosa nos detalhes, azul/roxo para dar profundidade, branco/pêssego"*.
  Decididas por ele no /discover: placa fosca com fio cromado (sem glow), fundo preto frio com luz azul/roxa no topo, dois
  anéis sem soma no Hoje (o "226" dos mockups somava questões com cards), v0 inteira. Decididas pelo agente: coluna larga
  no desktop, "pêssego" = o branco quente do texto, entrega em 4 parts e a guarda do simulado (a part 4, tela da questão,
  só vai ao ar conferida até qui 15/10; senão, dom 18/10). Part 1 (`c633422`): tokens, luz, placa, casca. Parts 2 e 3
  (subagentes em paralelo, arquivos disjuntos): Painel em bento com os dois anéis; Teoria, Listas e Cards em placas.
  Decisões dos subagentes que ele pode reverter: Simulados com provas | resolvidos lado a lado; a tela de fim do lote de
  cards numa placa. Part 4 (questão e leitor): JS idêntico ao de antes, só classes e wrappers; alternativas mantidas com
  a moldura própria (não elevadas) pela segurança do simulado de 17/10. Riscos declarados: duas placas somem por `:has()`
  (Elos sem cadeia; o leitor sem aula carregada) -- sem `:has`, uma placa vazia, nenhum gesto muda; a 390 o enunciado
  ficou 34 px mais estreito.

- **Dashboard do Painel (13/10, s226, painel-dashboard-sprint part-1)**: pedido dele ("integre estes dois blocos [...] com a modalidade de dashboard [...] e resolva as divergências entre metas"): Hoje + Ritmo + Por bloco viram um dashboard no topo (forma e cor pela skill `dataviz`, dentro dos tokens); com sprint, o único por-dia da tela é o do sprint ("0 de 76", não "0 de ~115"; o Ritmo contra 80/dia; "114,9 por dia até a prova" sai) e a meta 10.000 aparece uma vez, na barra de projeção (7.817 -> 9.306 -> 10.000, fora do sprint 997 q); a `<table>` do Por bloco virou linhas com barra de acerto. Regra s203 suspensa para a tela: `cronograma-contract` v1.7.
- **s226 (13/10, tarde):** pedido dele com prints: "Hub" no azul da paleta; a barra da aba ativa acompanha o degradê; as tags do Painel com a cor das de Teoria (o "novas"), "Próxima" segue ciano; fora as legendas em prosa (Teoria, frase do Ritmo, "Fora da tabela"). O dashboard que integra Hoje + Ritmo + Por bloco e a meta única na tela vão para o PRD `painel-dashboard-sprint`.

- **v1 (12/10/2026, s224)**: escuro índigo sobre preto, Atkinson, cartões viram linhas -- *"prefiro tema escuro / modo
  noite, pode ser assim por default"* (commit `1d71743`).
- **v2 Vice City (12/10)**: fundo Ocean Night `#0B0F2B`, acento ciano -- *"essa paleta me parece melhor"* (`95d4a38`).
- **v2.1-v2.3 (12/10)**: rosa crescente em ação, títulos, seleção e grifo.
- **v2.4 (12/10, noite)**: *"agora temos muito rosa; preferia a UI com mais ciano"*: ciano em tudo, rosa só alerta (`730d884`).
- **v3 retrowave contido (13/10, s225)**: o brief dele (paleta de referência `#17132E #211C3A #29233F #403858`, ciano
  `#00D9E8`, rosa `#FF4FA3`, roxo `#AA71E8`, amarelo `#FFD447`, verde `#79D6A5`, coral `#FF7C87`, âmbar `#FFBE72`) com
  semântica fixa por cor, hierarquia por tipo e menos caixas. Este arquivo nasce aqui.
- **Semana do Painel no padrão da Teoria (13/10, s226, P21)**: a linha inteira abre a lista no hub ("resolver no
  hub" saiu), a aula vira ação pequena fora do alvo, o atraso sobe para o subtítulo "Atrasadas · N" ("da semana N"
  saiu da linha) e a "Próxima" perde o botão cheio, fica só o rótulo. Travas: `test_painel.py::
  test_semana_linha_inteira_abre_a_lista`, `test_atrasadas_sob_subtitulo_unico`, `test_proxima_so_pelo_rotulo_sem_botao_cheio`.

- **Abas que se recuperam sozinhas (13/10, s226, part-1, A18/A21/A22)**: leitura de Listas, Teoria e lista aberta pela
  assinatura resiliente (1/2/4 s, depois "Tentar de novo"); o chip "pronta" saiu (em curso mostra respondidas/total);
  marca em 1,375rem. O banco falso do `ui_harness.html` ganhou `?leitura=1x|0` (falha de leitura de coleção).
- **A retentativa pede conexão nova (13/10, s226, sprint-final-uerj part-1)**: a v108 publicada com a página aberta
  deixou Listas em "Não consegui ler as listas" até ele sair do artifact e voltar -- as 3 tentativas reusavam o `db`
  morto. Da 2ª tentativa em diante a assinatura pede `claude.use("db")` de novo e a consulta recebe o `db` novo
  (`consulta(db)`); `QZ.db` acompanha. O harness ganhou `?leitura=conexao` (a 1ª conexão falha em toda leitura).

Ele muda de ideia rápido: trocar paleta é trocar os dois blocos de cor do `tema.css`; nada além disso deve ser preciso.
