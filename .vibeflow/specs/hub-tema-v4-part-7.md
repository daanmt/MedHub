# Spec: hub-tema-v4 -- part 7: "Fonte:" espalhada vira Referências no fim (leitor)

> Gerada em 13/10/2026 (s227). Pedido dele: *"nos resumos, favor remover todos os 'Fonte:...' espalhados pelo texto, e
> concentrá-los ao final, tal como um artigo. Preferir referências de guidelines/pcdt/ms/sociedades, tanto para os
> resumos quanto para as aulas. Isso será evoluído depois nos resumos, junto com a melhoria na estética dos mesmos, com
> o uso da /anima, mas já precisamos refinar os contratos/skills relacionados"*.
> Medido em 13/10: 96 linhas "Fonte:" em 25 aulas/RDs (`p.src`, `span.fa-src` em legenda de figura, outras formas) e 11
> em 7 resumos `.md`. Decisão do principal: **agora, na camada do leitor** (sem reescrever as 25 aulas nem os resumos,
> que migram na fonte junto com a reforma de estética com a /anima); os contratos de autoria mudam no mesmo dia (pelo
> principal), para o que nascer já nascer certo.

## Objetivo

No leitor do hub, toda linha "Fonte:"/"Fontes:" sai do meio do texto e vira uma seção **Referências** numerada no fim do
documento, com um número sobrescrito discreto no lugar de onde saiu, como num artigo.

## Definition of Done

1. Transformação no `preparar` do leitor (só `#hub-leitor-quadro`), ANTES do `fonteLigar`, dos atalhos/âncoras e do
   `grifoLigar`: acha os elementos cujo texto começa por `Fonte:`/`Fontes:` (`p`, `li`, `small`, `div`, `span` -- inclusive
   `p.src`, `span.fa-src` dentro de `figcaption`), tira o prefixo, deduplica textos iguais, numera na ordem de
   aparição e põe, no lugar, um `<sup class="hub-ref"><a href="#hub-ref-N">N</a></sup>` (no fim do bloco anterior quando
   a fonte era um parágrafo sozinho; dentro da legenda quando estava nela). Uma fonte que tem vários itens (`·`) vira
   uma entrada só.
2. No fim do conteúdo da aula (o último contêiner de texto dela: `.wrap`/`main`/`article`), uma seção
   `<section class="hub-refs"><h2>Referências</h2><ol>` com `id="hub-ref-N"` em cada item; o `fonteLigar` segue
   transformando `resumos/X.md` em link para o resumo publicado (agora dentro da lista). O número sobrescrito rola até a
   referência (âncora interna do quadro: a regra de hoje rola a página-mãe).
3. Idempotente (abrir de novo não duplica); documento sem "Fonte:" não ganha seção; falha aqui nunca derruba o leitor
   (try/catch, como o `fonteLigar`).
4. Grifos salvos antes continuam no lugar (o `grifoResolver` re-ancora pelo texto): teste com um grifo DEPOIS de uma
   fonte movida.
5. `tema-aula.css`: `.hub-ref` (sobrescrito pequeno, ciano de link) e `.hub-refs` (filete em cima, título no idioma das
   seções, lista em `--fs-legenda`/`tinta2`), sem cor literal.
6. Testes: a transformação sobre um documento sintético com `p.src`, `span.fa-src` em `figcaption`, duas fontes iguais e
   um parágrafo que só CITA a palavra "fonte" no meio (não move); capturas a 390 de uma RD com figura (`rd-cir-1310`) e de
   uma aula antiga, nos 2 temas, mostrando o texto sem "Fonte:" e a seção no fim.

## Escopo

`core/templates/hub.html` (JS do leitor), `core/templates/tema-aula.css`, `tools/test_hub_render.py`.

## Anti-escopo

Reescrever as aulas ou os resumos na fonte; trocar a fonte interna (resumo, card, PDF EMED) por diretriz (é a reforma
com a /anima); mudar os contratos/skills (o principal faz); o `CSS_RESUMO` (A16).
