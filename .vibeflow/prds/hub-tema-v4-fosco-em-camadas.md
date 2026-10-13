# PRD: Hub tema v4 -- fosco em camadas (PS5 GTA VI)

> Generated via discover on 2026-10-13 (s227). Decisões dele por AskUserQuestion no mesmo dia.

## Problem

O hub v3 ("retrowave contido", s225) é uma folha só: toda tela pinta o mesmo fundo `#17132E` e separa as seções por um
filete de 1 px em `#403858` que quase não se vê. Nada fica à frente de nada; o único objeto com moldura no hub inteiro é
o card do player. Nas palavras dele (13/10/2026): *"ainda muito 'chapado' no fundo, sem blocos e divisões, fluidez e
coesão, otimização do espaço"*. A 1280 px a coluna única de 46rem deixa ~60% da tela vazia; a 390 px a Teoria deixa
metade da tela vazia.

A causa é uma decisão anterior levada longe demais: o achado A5 da s225 trocou "caixas preenchidas em série" (uma caixa
por número) por linhas com filete -- e junto foi a superfície de seção, que é o que dá profundidade e agrupa.

Referências dele na raiz do repo (13/10): o controle DualSense GTA VI ("o exemplo que mais se aproxima"), a lata de pins
Vice City e 5 mockups gerados de dashboard. Pedido: manter a riqueza retrowave/95, mas sóbrio e minimalista como uma
plataforma de estudo deve ser.

## Target Audience

Um usuário: ele, médico em preparação (UERJ/MFC 01/11/2026; depois ENAMED/Psiquiatria), lendo **no celular a 390 px,
à noite**, em sessões longas de questões, cards e leitura; no desktop para o Painel e listas longas.

## Proposed Solution

Tema v4 "fosco em camadas", lido do controle:
- **Fundo = o corpo do controle:** preto fosco frio (sai o índigo), com uma **luz atmosférica azul -> roxo** bem fraca
  atrás do topo (marca e abas), como o cromado sob o touchpad. Decidido por ele.
- **Bloco = um degrau acima do fundo:** uma superfície fosca por SEÇÃO, borda de 1 px, e um **fio cromado azul -> roxo
  de 1 px no topo** de cada bloco. Zero glow, zero sombra, zero halo. Decidido por ele ("Fosco em camadas").
- **Regra que concilia com o A5:** um bloco por seção, **nunca uma caixa por número**; dentro do bloco as linhas com
  filete seguem. É o que separa o bento dos mockups da "caixa em série" reprovada na s225.
- **Rosa = os símbolos do controle:** marca, etiquetas, o anel de cards. Ciano segue interação. Branco quente
  ("pêssego") no texto; âmbar segue aviso.
- **Espaço:** no desktop as abas usam uma coluna mais larga com grade (bento de 2-3 colunas no Painel; 2 colunas onde a
  tela tem duas listas). A leitura longa (aula, enunciado) segue numa medida de ~46rem dentro do próprio bloco. A 390 px,
  uma coluna de blocos empilhados.
- **Hoje do Painel:** **dois anéis concêntricos sem soma** -- externo ciano = questões X/76, interno rosa = cards
  X/150, cada um contra a própria meta, os números na legenda; o Ritmo vira barra com a marca dos 80/dia (sem gauge).
  Decidido por ele.

## Success Criteria

- Ele aprova as capturas tela a tela (390 px primeiro, depois 768 e 1280) ANTES de cada publicação.
- Bloco distinguível do fundo à vista (borda do bloco >= 1,6:1 contra o fundo; superfície do bloco visivelmente acima
  dele) -- o "chapado" medido some.
- A 1280 px o Painel ocupa >= 2 colunas; a 390 px nenhuma tela rola na horizontal (`tools/ui_capturas.py` "ok" nas 11
  cenas x 3 larguras), nenhum erro de JS.
- Contraste: texto >= 4,5:1 sobre as três superfícies (fundo, bloco, elevado); corpo >= 7:1; borda de controle >= 3:1.
- Trocar a paleta continua sendo trocar os blocos de cor do `tema.css`; cor literal só lá (os testes de hoje seguem).
- Suíte verde; nenhuma mudança de dado, de texto ou de semântica (a meta única na tela, o hoje do sprint, a cadeia).

## Scope v0

Ele escolheu "tudo, inclusive questão e leitor". Entrega fatiada, nesta ordem, cada fatia conferida e publicada sozinha:
1. **Tokens v4 + casca:** paleta escura e clara v4 no `tema.css` (fundo, bloco, elevado, borda, fio cromado, luz
   atmosférica, branco quente), coluna mais larga no desktop, marca e abas sobre a luz.
2. **Painel em bento:** Hoje (dois anéis), Ritmo (barra com a marca 80/dia), Até 01/11, Por bloco, Revisões 7 dias,
   Plano de hoje, cada um num bloco; grade no desktop.
3. **Teoria, Listas e Cards em blocos:** cada seção um bloco (RDs, Biblioteca; Hoje, Próximos dias, Fora do sprint,
   Resolvidas; o player e a tela de fim), linhas por dentro; grade de 2 colunas no desktop onde houver duas listas.
4. **Questão e leitor:** a tela da questão (enunciado, alternativas, veredito, cadeia, fim) e o leitor de aulas/resumos
   (pela camada `tema-aula.css`, a moldura da aula como bloco, callouts e a `figure.fig-an` da anima no mesmo idioma).
   🔴 **Interação idêntica** (mesmos botões, ordem, teclas, gravação). 🔴 **Guarda do simulado:** esta fatia só vai ao ar
   se conferida até **qui 15/10 à noite**; senão, depois do simulado UERJ 2024 (**dom 18/10**).

Regra de publicação (A18): nunca com uma lista aberta; fora do bloco de estudo dele; build e capturas em scratch antes.

## Anti-scope

- Glow, halo, `text-shadow`, `box-shadow` como profundidade, gradiente animado, neon nas bordas (os mockups 5_41PM e
  5_43PM(1) ficam de fora por decisão dele).
- Gauge semicircular; qualquer número que some questões com cards (o "226").
- Conteúdo novo: o card "Diagnostic Intel IA", métricas novas, textos novos, "As planned"; mudar a semântica do Painel
  (meta única na tela, `cronograma-contract` v1.7) ou a fonte de qualquer número.
- Reescrever o HTML das 43 aulas (só a camada `tema-aula.css`); pendências L2/L4/L6/L9-L15 do leitor além do que a
  camada nova resolver de graça.
- Mudar a interação da questão ou do player (fluxo, atalhos, gravação, ordem dos blocos).
- Fonte nova, ícones, ilustrações decorativas, imagens das referências no hub.
- A página de resumo fora do leitor (`CSS_RESUMO`, A16) e a saída do artifact para ambiente próprio (pós-01/11).
- `sticky`/`fixed`/`nowrap` (contratos de celular seguem).

## Technical Context

- **Mapa das camadas** (`docs/UI.md` §2): tokens e base em `core/templates/tema.css`; casca, Teoria, Listas e questão no
  `<style>` do `core/templates/hub.html`; Cards em `core/templates/player.html` (`@player:css`); Painel na constante
  `CSS` de `tools/painel.py` (servido em iframe no hub); leitor em `core/templates/tema-aula.css`. O `hub.py --build`
  injeta o tema no shell e no `srcdoc` do leitor; o `painel.py` embute o tema; o `--build-player` também.
- **Contratos travados por teste** (`docs/UI.md` §7): um `.wrap` só, sem sticky/nowrap, 44 px, `min-width:0`, cor
  literal só no `tema.css`, `max-width` no máximo 2x no player e no painel, painel sem jargão (inclusive comentários do
  `tema.css`, que viaja embutido). A coluna mais larga muda `--wrap` (ou cria um segundo token só para a medida de
  leitura) -- o spec decide sem quebrar a regra de largura dele ("UM max-width no contêiner, filhos herdam 100%").
- **Painel em iframe:** a luz atmosférica do shell não atravessa o `body` do iframe; o spec decide (fundo transparente
  no iframe ou a luz repetida no próprio painel).
- **Anéis e barra:** SVG inline/CSS puro (o painel não carrega lib), forma e cor pela skill `dataviz` dentro dos tokens,
  `role=img` + `aria-label` com os números.
- **Conferência:** `python tools/ui_capturas.py` (11 cenas x 390/768/1280, banco falso, Edge headless) antes de cada
  publicação; fotos "antes" em `tmp/ui_capturas/s227_antes/`. Implementação com a skill `frontend-design`.
- **Ponto de partida da paleta** (o spec mede contraste e fecha): fundo ~`#0C0C12`, bloco ~`#15151E`, elevado
  ~`#1D1C28`, borda do bloco ~`#2A2838`, fio cromado azul `#3B6CFF` -> violeta `#8A4DFF`, texto branco quente
  ~`#F6EFEA`; ciano `#00D9E8`, rosa `#FF4FA3`, roxo `#AA71E8`, âmbar `#FFBE72`, verde `#79D6A5`, coral `#FF7C87` mantidos.
- **Registro:** `docs/UI.md` (§1 direção, §3 tokens, §5 componentes "Bloco", §10 A5 com a regra nova, §11 histórico v4);
  ⚰️ a frase "o único gradiente da UI" e o "sem caixa" das métricas viram lápide com data e motivo (§10.10).

## Open Questions

None. (Decididas por ele: superfície, fundo, anéis, escopo. Decididas pelo agente, com veto dele: coluna larga no
desktop, branco quente como "pêssego", ordem das fatias e a guarda do simulado.)
