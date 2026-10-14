# Spec: hub-tema-v4 -- part 6: marca-texto em três cores, só o fundo

> PRD: `.vibeflow/prds/hub-tema-v4-fosco-em-camadas.md` (pós-v0). Gerada em 13/10/2026 (s227). Pedido dele sobre a
> Version 113: *"o destaque não fica mais em rosa ou ciano, mas no amarelo antigo. Seria até interessante se desse para
> ter as 3 cores, na verdade, trocá-las [...] o destaque está mudando a cor do texto e ele poderia apenas manter a cor
> do texto e mudar o fundo dele"*. Decidido por ele (AskUserQuestion, 13/10): **uma cor ativa, trocável** (rosa por
> padrão), valendo para todos os grifos; o registro de cada grifo NÃO muda.

## Objetivo

O marca-texto das questões e do leitor pinta só o fundo (lavagem translúcida), mantém a cor do texto, e ele escolhe a
cor ativa (rosa, ciano ou amarelo) num seletor do topo do hub, lembrado no aparelho.

## Definition of Done

1. Tokens já no `tema.css` (o principal fez): `--grifo-rosa|ciano|amarelo` (color-mix), `--qz-grifo` = a ativa,
   `--qz-grifo-tinta: inherit`, troca por `:root[data-grifo="ciano"|"amarelo"]`; contraste travado em
   `test_tema_contraste.py`. A implementação só CONSOME os tokens (nenhuma cor literal).
2. Seletor "Cor do grifo" no topo do hub (à direita da marca): três amostras (rosa, ciano, amarelo) com o nome
   acessível, 44 px de alvo, a ativa marcada (`aria-pressed`/radio, nunca só pela cor); grava `data-grifo` no
   `<html>` do shell e no aparelho (`localStorage` com try/catch; sem armazenamento = rosa); sem `sticky`/`fixed`.
3. Questões: `.qz-grifo` com `background:var(--qz-grifo);color:inherit`. Leitor: `grifoEstilo` passa a ATUALIZAR o
   `<style id="hub-grifo-estilo">` do documento aberto quando a cor muda (hoje injeta uma vez só), com
   `color:inherit`; a troca vale na hora, sem reabrir a aula.
4. O registro dos grifos (respostas `grifos`, coleção do leitor) é byte a byte o mesmo; tocar num grifo segue
   removendo; os testes de grifo de hoje verdes.
5. Testes novos: o seletor (3 opções, 44 px, `data-grifo` no html, padrão rosa, aparelho lembra) e o leitor que
   atualiza o estilo na troca. Capturas a 390 da questão revelada e da aula com um grifo nas 3 cores, nos 2 temas.

## Escopo

`core/templates/hub.html`, `tools/test_hub_render.py` (e `core/templates/ui_harness.html` se a cena precisar de grifo).

## Anti-escopo

Cor por grifo, significado por cor, mudar o dado do grifo, `tema.css` (já pronto), docs (o principal escreve).
