# Spec: hub-tema-v4 -- part 1: tokens v4, luz atmosférica, placa e casca

> PRD: `.vibeflow/prds/hub-tema-v4-fosco-em-camadas.md` (fatia 1). Gerada em 13/10/2026 (s227).
> Publica JUNTO com a part 2 (o Painel é a 1a tela que ele vê; paleta nova sem o bento seria um passo pela metade).

## Objetivo

O hub inteiro troca o índigo chapado pelo preto fosco frio com luz azul -> roxo no topo, e ganha a primitiva de
superfície (`.placa`) que as próximas parts usam para dar um bloco a cada seção.

## Contexto

Hoje `core/templates/tema.css` (v3) pinta tudo de `#17132E` e o único gradiente é o `--horizonte` sob as abas. O PRD
decidiu (ele, 13/10): fosco em camadas, fundo preto frio + luz atmosférica, zero glow. Fotos "antes":
`tmp/ui_capturas/s227_antes/`.

## Definition of Done

1. Antes de escrever, carregar as skills `frontend-design` e `artifact-design` (ferramenta Skill) e seguir a direção
   dentro deste spec (nada de cor fora do `tema.css`; nada de glow, `box-shadow`, `text-shadow`).
2. `tema.css` v4: blocos escuro e claro com as três superfícies (`--papel` fundo, `--card` placa, `--afundado` elevado),
   `--borda-placa`, `--cromado` (gradiente azul -> violeta do fio da placa), `--luz` (luz atmosférica, só escuro; no
   claro uma versão quase imperceptível ou `none`), texto branco quente; ciano, rosa, roxo, verde, coral, âmbar e o grifo
   mantidos (ajuste fino de lavagem `-fraco` sobre o preto). Apelidos legados e das aulas continuam todos definidos.
   Token novo `--largura` (coluna larga do desktop, ~72rem) declarado e AINDA não usado (a part 2 usa).
3. Teste novo **`tools/test_tema_contraste.py`** (registrado no `pytest.ini`) que LÊ os hex do `tema.css` (escuro e claro)
   e asserta, por WCAG 2.x: `tinta`/`tinta2`/`tinta3`/`acento`/`acento-tinta`/`rosa`/`roxo-tinta`/`ok`/`erro`/`aviso`
   >= 4,5:1 sobre `papel`, `card` e `afundado`; `tinta` >= 7:1 nas três; `linha-forte` >= 3:1 sobre `card` e `afundado`;
   `--borda-placa` >= 1,6:1 contra `papel`; `--sobre` >= 4,5:1 sobre `acento`, `rosa`, `roxo`, `erro`, `aviso`, `ok`.
4. Primitiva `.placa` na base do `tema.css` (UMA regra; nenhuma tela a redefine): fundo `--card`, borda 1 px
   `--borda-placa`, `--raio`, `padding` da escala, e o fio cromado de 1 px no topo (pseudo-elemento ou
   `border-image`/gradiente no topo -- sem `box-shadow`), `min-width:0`. Sem `max-width` no `tema.css` (o painel e o
   player contam `max-width` <= 2 na página pronta). Classe sem colisão nas 43 aulas (`grep -l 'placa' artifacts/aula-*.html`
   vazio antes de cunhar).
5. Casca do hub (`core/templates/hub.html`): o `body` do shell leva `--luz` sobre `--papel` (sem `background-attachment:
   fixed`; nada `sticky`/`fixed`); marca e abas sobre a luz; `.hub-quadro` com fundo transparente e o hub injeta
   `html,body{background:transparent}` nos documentos dos iframes do painel e do leitor (pelo mesmo caminho do
   `painelListas`/`grifoEstilo`), para a luz não ser cortada no topo do iframe. O standalone do painel e do player segue
   com o `--papel` próprio.
6. Artesania: `python -X utf8 tools/ui_capturas.py --hub <build em scratch>` nas 11 cenas a 390/768/1280 com "ok" e zero
   erro de JS, lido a 390 (painel, teoria, listas, cards, aula); suíte inteira verde (os contratos do `docs/UI.md` §7
   seguem: cor literal só no `tema.css`, `max-width` <= 2, um `.wrap`, sem jargão no `tema.css` embutido);
   `auto_check --changed` PASSED.
7. `docs/UI.md`: §1 (direção v4, a regra "um bloco por seção, nunca uma caixa por número"), §3 (tabela de tokens v4 +
   contraste medido pelo teste), §5 (componente "Placa"), §11 (histórico v4 com a fala dele de 13/10); ⚰️ "o único
   gradiente da UI" vira lápide em linha própria com data e motivo (AGENTE §10.10; cadastrar o termo só se a redação
   antiga sair de um portador lido no ato).

## Escopo

`core/templates/tema.css`, `core/templates/hub.html` (só a casca: `body`, `.hub-topo`, `.hub-abas`, `.hub-quadro`, a
injeção de fundo transparente), `tools/test_tema_contraste.py` (novo), `pytest.ini`, `docs/UI.md`, e o teste da casca
em `tools/test_hub.py` (luz no body, iframe transparente).

## Anti-escopo

Layout de qualquer aba (parts 2-4); `.placa` aplicada em tela (parts 2-4); `--largura` em uso; glow, sombra, animação;
o `CSS_RESUMO` (A16); fonte; o leitor além do fundo transparente; o player além de herdar os tokens.

## Decisões técnicas

- **Ponto de partida da paleta escura (medido em 13/10):** `--papel #0C0C12`, `--card #15151E`, `--afundado #1E1D2A`,
  `--linha #2B2A3A` (filete interno), `--borda-placa` ~`#383650` (>= 1,6:1), `--linha-forte #6E6A8A` (3,2-3,8:1),
  `--tinta #F6EFEA` (14,6-17,1:1), `--tinta2 #BDB7CC` (8,6-10,0), `--tinta3 #948FAA` (5,4-6,3); ciano `#00D9E8`,
  rosa `#FF4FA3` (5,5-6,4), `--roxo-tinta #BE95F0` (6,9+), verde/coral/âmbar de hoje (6,7+). `--sobre #0C0C12`.
  Cromado: `linear-gradient(90deg,#2F7BFF,#7A4DFF 55%,#B04FE0)`. Luz: duas `radial-gradient` (azul à esquerda, violeta
  à direita) a ~14-16% de opacidade, ~26rem de altura, `no-repeat` -- lida a 390 como "profundidade", nunca como cor
  atrás de texto longo. Claro: papel `#F4F3F8`, placa `#FFFFFF`, elevado `#ECEAF3`, `--linha-forte` mais escuro que o
  da v3 (o `#8E87AD` dá 2,8:1 sobre o elevado claro: falha o item 3).
- **Por que a placa mora no `tema.css`:** é uma primitiva de base usada por 4 telas (hub, painel, player, leitor);
  quatro cópias seriam o A1 de volta. O A2 (regra de componente no tema sobrescrevendo a da tela) não se repete porque
  nenhuma tela redefine `.placa`: compõe por cima (`class="placa dash-hoje"`).
- **Fio cromado sem `box-shadow`:** `::before` de 1 px com `--cromado`, `inset` no topo, raio herdado; `overflow:hidden`
  NÃO (corta foco e tabelas) -- o pseudo-elemento segue o raio com `border-radius` próprio.
- **Iframe transparente:** a luz vive no `body` do shell; o iframe do painel começa a ~130 px do topo, dentro da luz. Fundo
  opaco no iframe faria uma emenda horizontal visível.

## Padrões aplicáveis

`docs/UI.md` (§2 casa de cada regra, §7 contratos), memória `feedback_artifact_width_alignment` (um `max-width`),
`feedback_artifact_celular_nowrap_sticky`. Padrão novo: a primitiva de base `.placa` (registrar no §5).

## Riscos

- Preto quase puro + branco quente pode ofuscar (halation) em leitura longa -> o corpo das aulas usa `--tinta` sobre a
  placa (15,9:1), não sobre o preto; a part 4 confere a 390 à noite.
- O claro fica esquecido -> o teste de contraste cobre os dois blocos.
- `--luz` atrás do título da aba abaixa o contraste -> o teste mede contra `--papel`; conferir na captura que o pico da
  luz não passa de ~+0,03 de luminância.
