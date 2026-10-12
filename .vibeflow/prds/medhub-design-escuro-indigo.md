# PRD: MedHub — design escuro minimalista (tema índigo)

> Generated via discover on 2026-10-12

## Problem
Ele lê teoria no celular (390 px) em sessões longas, à noite. Hoje o MedHub tem três identidades visuais que não conversam: o shell do hub (tokens `--papel/--acento`, verde-água), cada uma das 43 aulas (CSS próprio, 3 famílias de fonte: Fraunces, Source Sans 3, IBM Plex Mono; paleta teal/carmim/âmbar/ameixa) e o painel. A aba Teoria empilha cartões com borda, sombra e tarja de atraso; o alerta vermelho se repete em cada linha atrasada. Cada elemento a mais é carga cognitiva (ver `feedback_conteudo_curto_carga_cognitiva`).

## Target Audience
Um único usuário, médico em preparação para residência (UERJ/MFC em 01/11/2026; depois ENAMED/Psiquiatria), lendo no celular, majoritariamente no escuro.

## Proposed Solution
Um sistema visual único, escuro por padrão, aplicado ao hub por uma **camada de tema** em vez de reescrever 43 aulas:
- **⚰️ Atualização (12/10/2026, mesmo dia): a paleta passou a ser a Vice City** (`#0B0F2B` fundo, ciano `#00F0FF` acento, rosa `#FF5CA8` alerta, roxo `#BC6CFF` e pêssego `#FFB86B` realces; texto `#F4F1FF`), por escolha dele ("essa paleta me parece melhor"), acento e fundo confirmados via AskUserQuestion; tema v2 no ar (hub Version 99). O resto deste PRD (estrutura, tipo, mecanismo da camada, escopo) segue valendo; a v1 índigo está no commit `1d71743`. O texto abaixo descreve a v1.
- **Cor da v1 (decidido por ele, 12/10/2026):** fundo preto `#000000`; superfícies em degraus de azul da paleta dele (`#06064D` cartão, `#10106A` faixa/cabeçalho, `#171775` realce); acento `#8484DB`; texto `#EDEDFF` (branco levemente azulado, para evitar o halo do branco puro sobre preto puro), secundário `#CCCCFF`, terciário `#9A9AE6`. Um único tom de alerta (amora `#FF9DB3` no escuro) para armadilha e atraso; callouts de "banca" e "aside" viram azul. Claro como alternativa por `data-theme="light"` (papel `#F7F7FF`, tinta `#000042`, acento `#4343A8`).
- **Tipo (decidido):** uma família só, Atkinson Hyperlegible Next, pela distinção entre 0/O e 1/l em doses e cortes (o zero cortado é assumido). Substitui Fraunces + Source Sans 3 + IBM Plex Mono.
- **Estrutura:** cartões viram linhas com filete; área da tarefa vira etiqueta; o alerta de atraso aparece uma vez, no título da seção; numerais dos degraus grandes e leves (os degraus são mesmo uma sequência). Raio único de 12 px; sem sombras.
- **Mecanismo:** `tema.css` injetado no leitor (iframe `srcdoc`) depois do CSS de cada aula, com seletores `:root:not([data-theme="light"])` e `:root[data-theme="dark"]` (especificidade 0,2,0) para vencer o CSS próprio de cada aula; mesmas regras remapeiam os tokens do shell.

## Success Criteria
- As 43 aulas e a aba Teoria exibem o mesmo sistema (uma fonte, uma paleta) sem editar cada aula.
- Contraste de texto ≥ 4,5:1 em todos os pares; corpo ≥ 7:1 (medido: `#EDEDFF` sobre preto 17+:1; `#9A9AE6` sobre `#06064D` 6,8:1).
- A 390 px: zero rolagem horizontal da página (tabelas largas rolam na própria caixa), alvos de toque ≥ 44 px, foco visível, `prefers-reduced-motion` respeitado.
- Ele lê uma aula inteira no celular e aprova tela a tela (regra do hub: tela nova só publica conferida em navegador real).

## Scope v0
- `tema.css` (tokens escuro + claro, tipo único, estrutura em linhas) — protótipo em `tmp/design/tema.css`.
- Aba Teoria: semanas e Biblioteca em linhas; alerta uma vez por seção.
- Leitor de aulas: camada de tema injetada no `srcdoc`.
- Fonte via Google Fonts (já usada pelas aulas).
- Atualizar o contrato `/aula-base` (régua de design: tokens, tipo único) para aulas novas já nascerem no sistema.

## Anti-scope
- Painel (`artifacts/painel.html`), player de cards, aba Listas/Questões, bancada: fora da v0 (ele escolheu "tokens + Teoria + leitor").
- Reescrever o HTML das 43 aulas ou migrar para um motor de geração (frente aberta do `/aula-base §3`).
- Novo conteúdo, redução de texto das aulas (outra frente: `feedback_conteudo_curto_carga_cognitiva`).
- Animações novas; ícones; imagens decorativas; gradientes.
- Conversão de tabelas largas em cartões empilhados no celular (precisa de `data-label` no HTML; ver Open Questions).

## Technical Context
- Shell: `core/templates/hub.html` (CSS do hub, classes `qd-*`) + `core/templates/player.html` (região `@player:css`, tokens `--papel...--alerta`); `tools/hub.py` monta o `index.html` e o leitor mostra aulas em `iframe srcdoc` (`hub.py` ~l.1522: `<style>body{margin:0}img{max-width:100%}...`), ponto natural para injetar o tema.
- 42 das 43 aulas usam os mesmos tokens (`--paper --ink --ink2 --ink3 --line --line2 --sunk --card --teal* --carmine* --amber* [--plum*] --on`) e as mesmas fontes; 1 usa nomes próprios (`--bg --surface --accent...`, Barlow Semi Condensed) e precisa de mapeamento à parte.
- Armadilha de cascata: o CSS de cada aula define o escuro em `@media (prefers-color-scheme: dark){:root:not([data-theme="light"])}` (0,2,0), que vence um `:root` simples; o tema espelha os seletores.
- Contratos herdados: 1 `.wrap` único; sem `nowrap` longo; sticky desligado no celular; `min-width:0`; `tabular-nums`; dark mode nas duas formas (media e atributo).
- Teste visual: Edge headless tem largura mínima ~500 px; para 390 px usar `<iframe width=390>`. Protótipo e capturas em `tmp/design/` (gitignorado).

## Open Questions
- Tabelas largas a 390 px (ex.: comparativo de 3 colunas) rolam dentro da caixa; vale o custo de marcar `data-label` para empilhar no celular?
- Tema claro: manter como alternativa (toggle) ou só escuro? Hoje o hub segue `prefers-color-scheme`; o protótipo força escuro por padrão.
- A aula que usa nomes próprios de token (1 de 43) migra à mão ou entra num mapa à parte?
- Painel e player entram numa v1 (mesma camada) depois da aprovação tela a tela da v0?
