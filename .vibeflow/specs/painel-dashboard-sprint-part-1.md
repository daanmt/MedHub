# Spec: painel-dashboard-sprint -- part 1: dashboard no topo do Painel, uma meta na tela

> PRD: `.vibeflow/prds/painel-dashboard-sprint.md` (Solution 1 e 2). Gerada em 13/10/2026 (s226).

## Objetivo

O topo do Painel vira um dashboard (Hoje · Ritmo · Até 01/11 · Por bloco · Revisões 7 dias) em que o único "por dia"
é o do sprint e a meta 10.000 aparece uma vez, como alvo da projeção.

## Definition of Done

1. Antes de escrever, carregar as skills `dataviz` e `artifact-design` (ferramenta Skill) e seguir forma/cor/tiles delas
   dentro dos tokens do `docs/UI.md` (nenhuma cor literal; `--horizonte` não vira cor de dado).
2. Com sprint: tile **Questões** = `feitas_hoje de q_hoje` (o `q_hoje` de `plano.agenda_sprint`); tile **Ritmo** = real 7 d
   contra `capacidade_q` do `core/sprint.json` (rótulo "abaixo de 80/dia" / "em dia"), real 14 d, acerto acumulado; o
   texto "por dia até a prova" e o `alvo_marco` (~115 / 114,9) NÃO aparecem. Sem sprint: o comportamento atual.
   Testes: `test_dashboard_questoes_usa_o_q_hoje_do_sprint`, `test_dashboard_sem_sprint_volta_a_meta`.
3. **Barra de projeção até 01/11**: segmentos feito -> cumprindo o sprint -> meta, com os 3 números (7.817 · 9.306 ·
   10.000) e o fora do sprint (997 q) como o trecho que falta; acessível (texto alternativo com os números). Teste.
4. **Por bloco** como linhas com barra de acerto (0-100%) + "feitas/total", o bloco de menor acerto destacado (sem só
   cor: rótulo "mais fraco"); Simulados na última linha; a `<table>` some. A nota "Fora da tabela" não volta. Teste.
5. Nenhum `<p class="nota">` de prosa dentro do dashboard; `Revisões nos próximos 7 dias` entra no dashboard sem mudar o
   gráfico. Paridade: o `q_hoje` do tile = o do "Plano de hoje" = o do boot (`test_boot_painel_listas_mesmo_hoje` segue
   verde e ganha o tile).
6. Contrato: a regra s203 "o único por-dia é o da meta" é suspensa para a TELA enquanto houver sprint -- §10.10 no
   `core/contracts/cronograma-contract.md` (versão + lápide em linha própria + termo na §12 do
   `docs/MEMORIA-AUDITORIA.md` se a redação antiga sair) e `AGENTE.md §2` passo 4 se citar a regra.
7. Artesania: `python -X utf8 tools/ui_capturas.py --hub <rascunho> --cenas painel` a 390/768/1280 sem rolagem e lido a
   390; suíte inteira verde; `auto_check --changed` PASSED; `docs/UI.md` (componente "dashboard" na §5 + histórico).

## Escopo

`tools/painel.py`, `tools/test_painel.py`, `tools/test_plano_dia.py` (paridade), `docs/UI.md`,
`core/contracts/cronograma-contract.md`, `docs/MEMORIA-AUDITORIA.md` / `AGENTE.md` (só se o §10.10 pedir).

## Anti-escopo

Hub (Teoria/Listas/Cards), `plano.py` além de ler, FSRS, `performance.MARCOS`, o "Plano de hoje" (fica como está).

## Decisões técnicas

- HTML/CSS puro no `painel.html` (sem lib de gráfico): barras com `<i style="width:%">`, como as que já existem; o
  `painel.html` roda num iframe do hub e o leitor não carrega CDN.
- O "fora do sprint" na projeção em `--tinta3`/`--linha` (não é erro).

## Riscos

- Teste do boot/Painel que trava o texto "por dia até a prova" -> trocar pela forma nova com ⚰️ no teste antigo.
