---
type: research
status: active
relates_to: [core/templates/hub.html, core/templates/player.html, core/templates/tema.css, core/templates/tema-aula.css, tools/painel.py, docs/UI.md]
---

# Auditoria técnica do hub (Impeccable `audit`, s231, 19/10/2026)

> Ferramenta: plugin Impeccable 4.6.0, comando `audit` (`reference/audit.md`). Alvos: `tmp/hub/index.html` (build de
> 19/10, 537 KB), `core/templates/player.html`, `core/templates/hub.html`, `artifacts/aula-kawasaki.html` (aula antiga,
> família `.rail`) e `artifacts/aula-rd-cm-1510.html` (RD nova). O Painel (`artifacts/painel.html`) foi auditado antes,
> na mesma sessão. Somente leitura: nenhum arquivo-fonte editado. Sem PRODUCT.md/DESIGN.md (o `impeccable context`
> rodou e avisou; a autoridade visual usada foi o `docs/UI.md`). Nenhum texto de questão, aula ou card neste relatório.

Evidência renderizada: `python tools/ui_capturas.py --cenas teoria,listas,questao,revelada,fim,cards,verso,aula
--larguras 390,1280` (Edge headless, viewport emulado, tema escuro padrão) -> 16 capturas em
`tmp/impeccable_s231/audit/capturas/`, **zero rolagem horizontal e zero erro de JS** em todas. O tema claro foi
conferido por cálculo de contraste (hex do `tema.css`), não por captura. Gestos de toque não foram sintetizados (não
há gesto de arrastar no hub: só toque/clique e `pointerdown` passivo para marcar "apertado").

## Placar de saúde

| # | Dimensão | Nota | Achado principal |
|---|----------|------|------------------|
| 1 | Acessibilidade | 3 | estado da Certeza (Sólida/Dúvida/Chute) só por classe, sem `aria-pressed`; meta das linhas lidas a ~3:1 |
| 2 | Performance | 3 | página única de 537 KB (203 KB de JS do hub + 106 KB do lote de cards embutido); nada patológico |
| 3 | Tematização | 4 | cor literal só no `tema.css` (2 exceções justificadas); contraste testado nos dois temas |
| 4 | Responsivo | 3 | sem rolagem a 390/1280; 44 px quase em toda parte; 36 px nos 3 botões do Cards (decisão dele) e 34 px nos atalhos da aula |
| 5 | Integridade da implementação | 3 | sistema coerente e documentado; resíduo legado nas aulas antigas (paleta e fontes próprias neutralizadas pela injeção) |
| **Total** | | **16/20** | **Bom** (atacar a dimensão 1) |

Painel (auditoria anterior, mesma sessão): **17/20**; um P2 real (meta `--tinta3` a 4,4:1 nos cartões de tarefa
tingidos pela área); `cramped-padding` no `.tarefa` foi falso positivo (faixa decorativa de 4 px); hierarquia
tipográfica plana é escolha deliberada. **Hub inteiro: 16-17/20, banda Bom.**

## Veredito de integridade da implementação

**Passa.** O hub expressa um sistema próprio e verificável: um arquivo de tokens (`tema.css`) com os dois temas,
`test_tema_contraste.py` passando (13/13), uma primitiva de superfície (`.placa`) composta pelas telas, componentes
mapeados no `docs/UI.md` com teste que trava cada regra. Os 128 achados `side-tab` do detector são o padrão
documentado da casa (barra do cronograma, aviso, filete de seção), não atalho genérico. O ponto de deriva real está
nas aulas antigas, que ainda trazem paleta, três famílias de fonte e `@media` escuro próprios; o leitor neutraliza
tudo na injeção (`hub.html:696-701`), então o custo é de manutenção, não de tela.

## Resumo executivo

- Nota: **16/20 (Bom)**; Painel 17/20.
- Achados: **P0 0 · P1 2 · P2 4 · P3 5**.
- Principais:
  1. [P1] Certeza da questão sem estado acessível (`aria-pressed`).
  2. [P1] Linhas "lidas"/feitas da Teoria com `opacity:.7` derrubam a meta para ~3,0-3,3:1 (os dois temas).
  3. [P2] Meta `--tinta3` a 4,35-4,45:1 nas linhas tingidas de Teoria/Listas (o mesmo P2 do Painel, mesma fórmula).
  4. [P2] Foco se perde ao responder: o botão Responder some e o veredito não é anunciado.
  5. [P2] Botões do topo do Cards a 36 px (decisão registrada dele -- ver conflito com o UI.md).
- Próximo passo: um `/impeccable harden` curto em `hub.html` (estado ARIA + foco), depois `/impeccable colorize`
  (ou ajuste de token) para a meta sobre fundo tingido.

## Achados por severidade

### [P1] Certeza (Sólida / Dúvida / Chute) sem estado exposto
- **Local:** `core/templates/hub.html:586-590` (marcação), `:2893` e `:2901` (só `classList.toggle("on")`).
- **Categoria:** Acessibilidade.
- **Impacto:** leitor de tela anuncia três botões iguais; não diz qual está escolhido. A cor/borda é o único sinal.
  Para o usuário atual (vidente, celular) o impacto prático é baixo; a classificação P1 segue a régua do audit
  (violação AA).
- **Norma:** WCAG 2.2 4.1.2 (Nome, Função, Valor).
- **Recomendação:** `aria-pressed="true|false"` nos três botões junto com a classe `on` (ou `role="radiogroup"` +
  `role="radio"`/`aria-checked`, como as alternativas já fazem em `:2854`/`:2934`). O par Questões/Simulados
  (`:2691`) já faz certo com `aria-selected` -- copiar o padrão.
- **Comando:** `/impeccable harden`.

### [P1] Linha "feita"/lida da Teoria com opacidade 0,7
- **Local:** `core/templates/hub.html:145` (`.qd-item[data-feito] > .qd-bloco{opacity:.7}`).
- **Categoria:** Acessibilidade (contraste).
- **Impacto:** a meta (`--tinta3`) sobre o fundo tingido cai para **3,2-3,3:1 no escuro e 3,0-3,1:1 no claro**
  (calculado com a mistura `color-mix(area 9%, --afundado)` + opacidade). Item concluído não é "desabilitado": continua
  clicável e legível por regra.
- **Norma:** WCAG 1.4.3 (4,5:1).
- **Recomendação:** sinalizar "feito" sem opacidade no texto -- tirar a lavagem da área, trocar a faixa por
  `--linha-forte`, ou baixar só a faixa/fundo, mantendo `tinta`/`tinta2`/`tinta3` intactos.
- **Comando:** `/impeccable colorize` (ou `/impeccable polish`).

### [P2] Meta `--tinta3` abaixo de 4,5:1 nas linhas tingidas de Teoria e Listas
- **Local:** `core/templates/hub.html:136-137` (fundo `color-mix(in srgb,var(--area) 9%,var(--afundado))`), mesma
  fórmula do Painel (`tools/painel.py:1115`).
- **Categoria:** Acessibilidade (contraste).
- **Impacto:** no escuro, `tinta3` fica em **4,35 (GO), 4,42 (Simulado), 4,45 (MFC)**:1; CM 4,51, demais 4,6-4,8. No
  claro todas passam (4,76-5,42). É a contagem de questões e a data nas linhas de backlog -- texto lido a toda hora.
- **Norma:** WCAG 1.4.3.
- **Recomendação:** subir `--tinta3` escuro um passo (ex.: ~`#9C97B2`) e reconferir no `test_tema_contraste.py`
  acrescentando a superfície tingida, ou usar `tinta2` na meta dessas linhas. Resolve Painel, Teoria e Listas de uma
  vez porque a fórmula é a mesma.
- **Comando:** `/impeccable colorize`.

### [P2] Foco perdido e veredito mudo ao responder a questão
- **Local:** `core/templates/hub.html:3061-3064` (`qzRevelar`: `#qz-antes` vira `hidden` com o botão Responder
  focado; `#qz-veredito` sem `role="status"`/`aria-live`).
- **Categoria:** Acessibilidade (teclado/leitor).
- **Impacto:** quem responde por teclado (Enter) fica com o foco no `body`; o próximo Tab recomeça do topo. Leitor de
  tela não anuncia "Certa/Errada".
- **Norma:** WCAG 2.4.3 (Ordem do foco), 4.1.3 (Mensagens de status).
- **Recomendação:** após revelar, `focus()` no veredito (`tabindex="-1"`) ou dar `role="status"` a ele.
- **Comando:** `/impeccable harden`.

### [P2] Botões do topo do Cards a 36 px
- **Local:** `core/templates/player.html:70` (`.topo-acoes button{min-height:36px}`).
- **Categoria:** Responsivo (alvo de toque).
- **Impacto:** Virar, Pausar e Defeito são os toques mais frequentes da aba no celular; 36 px passa no mínimo AA
  (WCAG 2.5.8, 24 px) mas fica abaixo dos 44 px que o próprio sistema adota. Mitigação real: o card inteiro também
  vira ao toque. A 390 px o "Defeito do card" quebra para uma segunda linha (o UI.md descreve os três "numa linha").
- **Norma:** WCAG 2.5.5 (AAA, 44 px); regra da casa (UI.md: "Botão ... 44 px de altura").
- **⚠ Conflito com o `docs/UI.md`:** o UI.md registra "os três botões compactos (36 px, o tamanho do Pausar da v120)"
  como pedido dele (s229). Não mudar sem perguntar; se ele mantiver, registrar como exceção explícita na tabela de
  componentes (hoje a linha "Botão" diz 44 px).
- **Comando:** `/impeccable adapt` (só com aval dele).

### [P2] Hub sem `h1` e sem landmark `main`
- **Local:** `core/templates/hub.html:500-502` (marca em `<p class="hub-marca">`), seções em `<section role="tabpanel">`
  sem `<main>`; os títulos de aba são `h2` (`:518`, `:553`), e a aba Cards traz o `h1` do player (`player.html:189`).
- **Categoria:** Acessibilidade (semântica).
- **Impacto:** navegação por cabeçalho/landmark incoerente entre abas (Cards tem `h1`, as outras não).
- **Norma:** WCAG 1.3.1; boa prática de landmarks.
- **Recomendação:** envolver as quatro `section` num `<main>`; um `h1` visualmente oculto ("MedHub") ou promover os
  títulos de aba e rebaixar o `h1` do player quando embutido.
- **Comando:** `/impeccable harden`.

### [P3] Título de seção com `role="button"` no próprio `h3`
- **Local:** `core/templates/hub.html:1866` (`<h3 class="qd-titulo" role="button" tabindex="0">`).
- **Impacto:** o `role` apaga a semântica de cabeçalho (some da navegação por títulos). Teclado funciona (`:1831`).
- **Recomendação:** `<h3><button aria-expanded>...</button></h3>`.
- **Comando:** `/impeccable harden`.

### [P3] Botão "Riscar" sem estado
- **Local:** `core/templates/hub.html:2856` (marcação), `:2927` (toggle só de classe).
- **Recomendação:** `aria-pressed` acompanhando `.riscada`.
- **Comando:** `/impeccable harden`.

### [P3] Alvos pequenos dentro das aulas
- **Local:** `core/templates/tema-aula.css:41` (`.nav a{min-height:34px}`); aulas antigas com `.rail a` em chip de
  ~30 px abaixo de 920 px (`artifacts/aula-kawasaki.html:79` e `:88`, não sobrescrito em altura pelo `tema-aula.css:56`).
- **Recomendação:** `min-height:44px` nos atalhos do topo da aula, na camada `tema-aula.css` (vale para as 54 aulas).
- **Comando:** `/impeccable adapt`.

### [P3] Texto de 11 px em aulas antigas
- **Local:** `artifacts/aula-kawasaki.html:81` (número do trilho, 11 px) e `:117` (selo `.fora`, 11 px).
- **Impacto:** baixo (rótulos curtos). Os 11,5 px da RD (`aula-rd-cm-1510.html:53`) são texto de SVG com `viewBox`
  (escala com a figura) e o `sup.ref` de 11 px é sobrescrito -- ver falsos positivos.
- **Comando:** `/impeccable typeset` (na camada `tema-aula.css`, sem reescrever aula).

### [P3] `tema.css` embutido duas vezes no build
- **Local:** `core/templates/hub.html:694` (`TEMA_CSS`, ~22 KB como string JS para injetar nos iframes) além do
  `<style>` da página.
- **Impacto:** ~22 KB a mais no download; nenhum efeito visual.
- **Recomendação:** ler o texto do `<style>` do shell em tempo de execução em vez de duplicar no build.
- **Comando:** `/impeccable optimize`.

## Falsos positivos do detector (verificados na fonte)

O detector devolveu 188 achados em 5 alvos (126 no `index.html`, 57 na Kawasaki, 2 na RD, 1 no player, 2 no
`hub.html`). Todos os tipos foram conferidos; **186 são falsos positivos** (os 2 restantes viraram o P3 de 11 px):

| Tipo | Qtd | Por que não é defeito |
|---|---|---|
| `side-tab` (borda esquerda grossa + raio) | 128 (125 + 1 + 2) | É o padrão documentado: barra do cronograma com faixa de área de 4 px (`hub.html:136`, UI.md "Rodada 4"), aviso âmbar de 3 px (`hub.html:268`, `player.html:126`, UI.md "Aviso"), retorno da assinatura (`hub.html:467`). A contagem alta vem de uma ocorrência por linha renderizada. **Remover conflitaria com o UI.md.** |
| `low-contrast` na aba Painel (1,5:1, "gradient on button") | 1 | O gradiente `--horizonte` é uma barra de 2 px no pé da aba ativa (`hub.html:76`, `background-size:400% 2px`); o texto fica sobre o fundo transparente/papel (17:1). |
| `low-contrast` na Kawasaki (1,2-3,0:1, texto claro sobre `#fff`) | 54 | Leitura do arquivo solto: o detector misturou a paleta escura da aula com fundo branco. No hub a aula só aparece com o `tema.css` injetado depois do CSS dela (`hub.html:696-707`), que redefine `--paper/--ink/...`; o contraste real é o do tema (testado). |
| `cramped-padding` em `.tw` (Kawasaki) | 1 | `.tw` é o contêiner de rolagem da tabela (`aula-kawasaki.html:157`); a tabela encosta na borda de propósito e as células têm 9-11 px de padding. |
| `tiny-text` 11,5 px na RD | 2 | `.fa-s` é `font-size` de `<text>` dentro de SVG com `viewBox` (`aula-rd-cm-1510.html:53`): escala com a figura; o `sup.ref` de 11 px é índice de referência. |

## Padrões sistêmicos

- **Estado só por classe** em controles de escolha montados em JS (Certeza, Riscar): o hub já resolve bem onde houve
  cuidado (grifo com `aria-pressed`, alternativas com `role=radio`/`aria-checked`, modo com `aria-selected`); falta
  aplicar o mesmo padrão aos dois que escaparam.
- **`--tinta3` sobre fundo tingido**: a mesma fórmula `color-mix(area 9%, --afundado)` aparece no Painel e em
  Teoria/Listas; o `test_tema_contraste.py` mede só `papel/card/afundado`, então a superfície tingida escapa do teste.
  Acrescentar essa superfície ao teste fecha a classe inteira.

## Achados positivos

- **Tokens de verdade:** cor literal fora do `tema.css` só em dois pontos justificados (`#fff` atrás da figura escaneada,
  `hub.html:443`; *fallback* `#b3261e` em `:where()`, `hub.html:1220`). Player e `tema-aula.css`: zero.
- **Contraste testado** nos dois temas por `test_tema_contraste.py` (13/13); pontos conferidos à mão neste audit:
  rosa sobre placa 5,96:1, `tinta3` sobre placa 5,85 (escuro) / 6,52 (claro), branco sobre ciano claro 5,6:1.
- **44 px consistente** em quase todo controle do hub (abas, grifo, linhas, alternativas, Riscar, elos, campos).
- **Abas acessíveis:** `role=tablist/tab/tabpanel`, `aria-selected`, *roving tabindex* e setas (`hub.html:505-509`,
  `:675-680`). Alternativas com `role=radiogroup`/`radio`, Enter/Espaço e atalhos A-E/1-5/S-D-C (`:3287-3299`).
- **Formulários rotulados** (`aria-label` em todos os campos; checkbox "Revisar depois" dentro de `<label>`), figuras
  com `alt`, `role=status` nos avisos e `aria-live` no card do player.
- **Foco visível global** (`tema.css`: `:focus-visible` ciano 2 px) e nenhum `outline:none`.
- **Movimento:** só transições de 140 ms de cor; `prefers-reduced-motion` desliga sem perder estado.
- **Responsivo:** zero rolagem horizontal e zero erro de JS nas 16 capturas (8 cenas x 390/1280).
- **Performance:** *resize* com *debounce* (`hub.html:997`), um temporizador por tela, fontes das aulas removidas na
  injeção (uma família só), figuras como data URI WebP no banco, não na página.

## Ações recomendadas

1. **[P1] `/impeccable harden`** -- `hub.html`: `aria-pressed` na Certeza (e no Riscar), foco/`role=status` no
   veredito após Responder, `<main>` + `h1`, botão dentro do `h3` das seções.
2. **[P1] `/impeccable colorize`** -- linha feita sem `opacity` no texto; `--tinta3` sobre fundo tingido >= 4,5:1
   (Painel + Teoria + Listas de uma vez), com a superfície tingida acrescentada ao `test_tema_contraste.py`.
3. **[P2] `/impeccable adapt`** -- 44 px nos atalhos da aula (`tema-aula.css`); os 36 px do Cards **só com aval dele**
   (conflito com decisão registrada no UI.md).
4. **[P3] `/impeccable typeset`** -- piso de 12 px para os rótulos de 11 px das aulas antigas, pela camada de leitura.
5. **[P3] `/impeccable optimize`** -- deixar de embutir o `tema.css` duas vezes no build.
6. **`/impeccable polish`** -- passada final e reconferência com `python tools/ui_capturas.py` (390/768/1280).

> Pode pedir para rodar um de cada vez, todos juntos ou em qualquer ordem.
>
> Rode `/impeccable audit` de novo depois das correções para ver a nota subir.
