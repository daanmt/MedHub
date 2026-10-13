# Spec: hub-tema-v4 -- part 3: Teoria, Listas e Cards em placas

> PRD: `.vibeflow/prds/hub-tema-v4-fosco-em-camadas.md` (fatia 3). Gerada em 13/10/2026 (s227).

## Objetivo

Teoria, Listas e Cards deixam de ser listas soltas no fundo: cada seção vira uma placa e, no desktop, as telas com duas
listas usam duas colunas.

## Contexto

Teoria = "Revisões direcionadas · N" + Biblioteca por área (markup do `tools/hub.py`, CSS `qd-*` no `hub.html`). Listas =
Questões/Simulados + Hoje / Próximos dias / Fora do sprint / Outras / Resolvidas (JS do `hub.html`, `qz-*`). Cards =
topo com contadores + o card (único objeto com moldura hoje) (`core/templates/player.html`). A 390 px a Teoria deixa
metade da tela vazia; as linhas ficam soltas sobre o fundo.

## Definition of Done

1. Antes de escrever, carregar `frontend-design` (ferramenta Skill).
2. **Teoria:** "Revisões direcionadas" e "Biblioteca" são duas placas; no desktop (>= ~900 px) lado a lado (RDs à
   esquerda); a 390 empilhadas. As linhas internas, o recolher, as etiquetas "novas" e o foco de 3 px ficam (testes
   `test_hub_quadro.py` de hoje verdes).
3. **Listas:** o seletor Questões/Simulados fica fora das placas; Hoje é uma placa; Próximos dias, Fora do sprint e
   Outras listas formam outra; Resolvidas uma terceira (recolhida); no desktop Hoje à esquerda e Próximos dias à
   direita. O texto explicativo do topo (`qz-sub`) fica, numa linha de legenda. Testes de agrupamento verdes
   (`test_listas_agrupam_por_hoje_proximos_dias_e_fora_do_sprint`, `test_listas_e_painel_mesmo_hoje`, chip, retentativa).
4. **Cards:** o topo (título, "N de 150 hoje", fila, relógio, pausar, barra, tally) é uma placa; o card é a placa
   elevada (`--afundado`) dentro da coluna `--wrap`; botões fora da placa do card como hoje. Interação, atalhos e
   gravação idênticos (testes do player verdes; standalone do `--build-player` com o tema).
5. A coluna `--wrap` provisória da part 2 sai das abas desta part (substituída pelas grades acima); a regra de largura
   segue: um `max-width` por tela, placas da mesma grade com bordas alinhadas.
6. Artesania: `ui_capturas.py` nas 11 cenas a 390/768/1280 "ok", zero erro de JS, lido a 390 e 1280 (teoria, listas,
   simulados, cards, verso, fim); suíte inteira verde; `auto_check --changed` PASSED; cor só por token.
7. `docs/UI.md` §5 (linha de lista dentro de placa; Teoria/Listas/Cards), §6, §7 (testes novos ou ajustados), §11.

## Escopo

`core/templates/hub.html` (CSS `qd-*`/`qz-*` das listas e o JS que monta os grupos da aba Listas), `tools/hub.py` (markup
da Teoria), `core/templates/player.html` (topo e card), `tools/test_hub_quadro.py`, `tools/test_hub_render.py`,
`docs/UI.md`.

## Anti-escopo

A tela da questão aberta e o leitor (part 4); o conteúdo, a ordem e os rótulos das listas; o fluxo do player; glow;
"Ver mais"; ícones.

## Decisões técnicas

- Grade de 2 colunas por `@media (min-width:900px)` no shell (`display:grid;grid-template-columns:repeat(2,minmax(0,1fr))`
  num contêiner por aba), `align-items:start` (placas de alturas diferentes não esticam).
- O JS das Listas ganha os contêineres das placas na montagem (`secao(...)`), sem mudar a lógica de grupos.

## Padrões aplicáveis

`docs/UI.md` §5 (linha de lista, chip, segmentado), a primitiva `.placa` da part 1, `assinarResiliente` (não tocar).

## Riscos

- O `data-recolhida` e as margens negativas entre recolhidas (`.qd-semanas > [data-recolhida] + [data-recolhida]`)
  dependem de irmãos diretos -> conferir que a placa não quebra o seletor.
- Publicar com uma lista aberta repete o A18 -> publicar fora do bloco de estudo dele.

## Dependencies

- `.vibeflow/specs/hub-tema-v4-part-1.md`
- `.vibeflow/specs/hub-tema-v4-part-2.md`
