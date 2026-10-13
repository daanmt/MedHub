# Spec: hub-tema-v4 -- part 2: Painel em bento, dois anéis, coluna larga

> PRD: `.vibeflow/prds/hub-tema-v4-fosco-em-camadas.md` (fatia 2). Gerada em 13/10/2026 (s227).

## Objetivo

O Painel vira um bento de placas (uma por seção) que, no desktop, ocupa a tela em grade, e o "Hoje" mostra dois anéis
concêntricos sem soma (questões ciano, cards rosa).

## Contexto

`tools/painel.py` monta hoje UMA `section.bloco.dia` com cinco `.dash-sec` separadas por filete + a `section` do Plano de
hoje; coluna `--wrap` 46rem, que a 1280 px deixa ~60% vazio. Os mockups 5_43PM e 6_02PM (raiz do repo) são a referência
de grade; o 5_43PM(2) a de celular (blocos empilhados).

## Definition of Done

1. Antes de escrever, carregar `frontend-design` e `dataviz` (ferramenta Skill); anéis e barra dentro dos tokens.
2. Cada parte do dashboard é uma `.placa` (Hoje, Ritmo, Até 01/11, Por bloco, Revisões 7 dias) e o Plano de hoje é uma
   placa (Próximos dias e Fora do sprint dentro dela, recolhidos como hoje). Os `data-bloco` atuais (`dia`, `ritmo`,
   `blocos`, `semana`, docs) e os textos ficam; nenhum `p.nota` volta ao dashboard; a meta 10.000 segue aparecendo uma
   vez (barra de projeção). Testes de hoje verdes (`test_dashboard_*`, `test_barra_de_projecao_feito_sprint_meta`,
   `test_por_bloco_*`, `test_boot_painel_listas_mesmo_hoje`).
3. **Hoje com dois anéis** (SVG inline, sem lib): externo `--acento` = questões feitas/`q_hoje` (ou o alvo sem sprint),
   interno `--rosa` = cards consumidos/teto; trilho `--afundado`; centro = o dia (como no preview que ele aprovou);
   legenda ao lado (desktop) ou abaixo (390) com "Questões X de Y" e "Cards X de Y" + as linhas `kpi-r` de hoje; nenhum
   número que some as duas unidades; `role="img"` + `aria-label` com os dois números. As âncoras `data-vivo` do "Hoje ao
   vivo" seguem nos números (o anel acompanha o vivo ou fica no publicado, declarado no código). Teste novo
   `test_hoje_dois_aneis_sem_soma`.
4. **Ritmo:** acima dos 3 números de hoje, uma barra do real 7 d contra a capacidade do sprint com a MARCA dos 80/dia
   (abaixo = âmbar + "abaixo de 80/dia", em dia = verde + texto); sem gauge. Teste novo `test_ritmo_barra_com_marca_do_sprint`.
5. **Grade:** no painel, `.wrap` usa `--largura`; até ~760 px uma coluna; acima, grade em que Hoje e Ritmo dividem a 1a
   linha, Até 01/11 ocupa uma linha, Por bloco e Revisões dividem a seguinte e o Plano de hoje fecha em largura total
   (bordas de todas as placas alinhadas: mesma grade, mesmo `gap`). No hub, o `.wrap` do shell usa `--largura` (classe
   própria no mesmo elemento: um `.wrap` só) e as abas Teoria, Listas e Cards ficam numa coluna `--wrap` centrada até a
   part 3 (um `max-width` por tela, filhos 100%). `max-width` <= 2 na página do painel segue.
6. Artesania: `ui_capturas.py` nas 11 cenas a 390/768/1280 "ok", zero erro de JS, lido a 390 e 1280 (painel, teoria,
   listas, cards); suíte inteira verde; `auto_check --changed` PASSED; cor só por token.
7. `docs/UI.md` §5 (Dashboard: placas, anéis, barra do ritmo, grade), §6 (Painel), §7 (testes novos), §11.

## Escopo

`tools/painel.py`, `tools/test_painel.py`, `core/templates/hub.html` (só `.wrap` do shell + coluna `--wrap` das outras
abas), `tools/test_hub.py` (se a coluna precisar de trava), `docs/UI.md`.

## Anti-escopo

Dados, fontes de número e textos do Painel; o Plano de hoje além de virar placa; "Ver mais N tarefas" (os Próximos dias
já recolhem); gauge; glow; Teoria/Listas/Cards além da coluna; o card "Diagnostic Intel IA".

## Decisões técnicas

- Anéis por `circle` com `pathLength="100"` + `stroke-dasharray="P 100"` (P = % já arredondado no Python), `stroke-linecap:
  round`, rotação -90°; 0% desenha só o trilho (sem ponto solto). Largura do traço ~10 px num `viewBox` de 120.
- Grade por `@media (min-width:760px)` no CSS do painel com `grid-template-columns:repeat(2,minmax(0,1fr))` e `grid-column:
  1 / -1` nas placas de largura total -- `media` no iframe mede a largura do iframe (= a do `.wrap` do shell).
- A coluna `--wrap` das abas não migradas é UM contêiner por aba (`#aba-aulas`, `#aba-questoes`, `#aba-cards` > filho
  direto), não por elemento.

## Padrões aplicáveis

`docs/UI.md` §5-§7; skill `dataviz` (anel = parte de um todo por unidade, nunca soma de unidades); a primitiva `.placa`
da part 1.

## Riscos

- Iframe do painel mede a altura pelo conteúdo (`medir`): a grade muda a altura entre larguras -> conferir a 768 e 1280
  que não sobra rolagem dupla.
- O `test_boot_painel_listas_mesmo_hoje` lê o número do tile -> o número continua no texto da legenda, não só no SVG.

## Dependencies

- `.vibeflow/specs/hub-tema-v4-part-1.md`
