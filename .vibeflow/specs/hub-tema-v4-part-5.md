# Spec: hub-tema-v4 -- part 5: Painel compacto, quatro anéis no topo

> PRD: `.vibeflow/prds/hub-tema-v4-fosco-em-camadas.md` (pós-v0). Gerada em 13/10/2026 (s227), do feedback dele sobre a
> Version 113: *"o 'Painel' ainda está muito disperso. Esses 4 blocos deveriam aparecer junto no topo, através desses
> anéis com percentual - talvez apenas o 'Por bloco' não virar anél, mas gráfico, junto de 'Revisões nos próximos 7
> dias', que deveria ser renomeado para 'Flashcards da semana'"*.

## Objetivo

O topo do Painel vira UMA placa com quatro anéis lado a lado (Questões, Cards, Ritmo, Até 01/11), cada um com o
percentual no centro; abaixo, Por bloco e Flashcards da semana lado a lado; depois o Plano de hoje.

## Definition of Done

1. Antes de escrever, carregar `frontend-design:frontend-design` e `dataviz` (ferramenta Skill).
2. **Placa "Hoje, terça 13/10"** com 4 anéis (SVG inline, `pathLength=100`, trilho `--trilho`, % no centro, rótulo e
   valor abaixo do anel; `role="img"` + `aria-label` com os números): **Questões** = feitas / `q_hoje` (`--acento`);
   **Cards** = consumidos / teto (`--rosa`, com o link "Ir para os cards"); **Ritmo** = real 7 d / capacidade do sprint
   (sem sprint, / o necessário por dia), cor de estado (`--aviso` abaixo, `--ok` em dia, sempre com o texto "abaixo de
   80/dia" / "em dia"), linha extra "23,5 em 14 dias · 78,4% de acerto"; **Até 01/11** = feito / meta, em `--roxo`, com
   um 2º arco (mais claro, mesmo anel) até onde o acumulado chega cumprindo o sprint, e a linha "cumprindo o sprint:
   9.306 · fora: 997 q". Cada anel contra a própria meta; nenhum número soma unidades. A meta 10.000 aparece uma vez (no
   valor do anel Até 01/11). As âncoras `data-vivo` seguem nos números de Questões e Cards (o anel fica no publicado).
   A 390 px: grade 2 x 2; a partir de 760 px (iframe): 4 em linha.
3. As placas "Ritmo de questões" e "Até 01/11" somem (o conteúdo foi para o topo); a barra de projeção `.proj-barra` e a
   barra `.rb` saem com elas.
4. **Por bloco** (mesmo gráfico de linhas de hoje) e **Flashcards da semana** (o gráfico de barras de hoje, renomeado de
   "Revisões nos próximos 7 dias") lado a lado a partir de 760 px, mesma altura; empilhados a 390.
5. Testes: os de hoje que travam a forma antiga viram ⚰️ com o motivo e a forma nova ganha teste (`test_topo_quatro_aneis`,
   `test_ate_01_11_anel_com_projecao_do_sprint`, `test_flashcards_da_semana_renomeado`); os de paridade seguem
   (`test_boot_painel_listas_mesmo_hoje`, `q_hoje` do tile = o do boot); `max-width` <= 2; sem jargão; cor só por token.
6. Artesania: `ui_capturas.py --cenas painel` a 390/768/1280 "ok", lido a 390 e 1280, com o dado real (0/0) e com
   progresso; suíte de painel verde.

## Escopo

`tools/painel.py`, `tools/test_painel.py` (e `tools/test_plano_dia.py` só se a paridade precisar de ajuste).

## Anti-escopo

Fonte dos números, Plano de hoje, hub.html, tema.css, contratos e docs (o principal escreve), glow, gauge semicircular.

## Riscos

- `cronograma-contract` v1.7 diz "a meta aparece uma vez, como alvo da barra de projeção" -> o principal atualiza o
  contrato (o anel passa a ser a projeção).
