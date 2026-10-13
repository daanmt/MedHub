# PRD: Painel como dashboard do sprint (uma meta na tela) + figura nas 5 RDs da UERJ 2022

> Gerado em 13/10/2026 (s226, tarde) do pedido dele com prints. Rápido já aplicado no commit `9289737` (cor do "Hub",
> barra da aba no degradê, tags do Painel no rosa do "novas", legendas em prosa fora). Loop vibeflow: PRD -> specs ->
> UM subagente Opus implementa e audita.

## Problem

Pedido dele (13/10): *"Integre estes dois blocos, com seus aprendizados recentes sobre a modalidade de dashboard dos
artifacts [...] não é para criar um artifact novo, mas apenas utilizar a habilidade para inserir neste bloco inicial do
artefato do medhub -- aproveite e resolva as divergências entre metas nos prints"*. Os dois blocos: **Hoje + Ritmo de
questões** e **Por bloco**. As divergências, medidas no Painel da Version 110:
- "Questões **0 de ~115**" (o por-dia da meta 10.000) x "Plano de hoje: **76** questões" (o sprint);
- "**114,9** por dia até a prova" x o sprint de **80 q/dia**;
- a frase do sprint ("9.306 em 01/11, 694 abaixo") saiu como legenda, e a projeção sumiu da tela.

E (13/10, mesma mensagem): *"encontrei uma skill que pode nos ajudar com as aulas e a criação de imagens [...]
https://github.com/Garinmckayl/anima"*; depois: *"vamos apenas fazer com as cinco revisões direcionadas da uerj, para
testar [...] criar/refazer aulas/resumos [fica] para as próximas sessões"*.

## Target Audience

Ele, no celular e no desktop, abrindo o Painel para decidir o dia; 18 dias até a UERJ (01/11).

## Proposed Solution

1. **Dashboard no topo do Painel** (dentro do `painel.html` do hub, sem artifact novo), no padrão da skill `dataviz`
   (tiles de KPI, um número por tile, barra fina, sem legenda em prosa):
   - **Hoje**: Questões `feitas de q_hoje do sprint` · Cards `feitos de teto` · a dose some quando cumprida;
   - **Ritmo**: real 7 d **contra 80/dia do sprint** (abaixo/em dia), real 14 d, acerto acumulado;
   - **Até 01/11**: uma barra de projeção -- feito (7.817) -> cumprindo o sprint (9.306) -> meta (10.000), com o "fora
     do sprint" (997 q) como o trecho que falta;
   - **Por bloco**: uma linha por bloco (CIR, CM, GO, MFC, PED, Simulados) com barra de acerto e tarefas feitas/total --
     substitui a tabela; o bloco mais fraco em destaque;
   - **Revisões nos próximos 7 dias** fica como está (já é gráfico), dentro do dashboard.
   O "Plano de hoje" segue logo abaixo, como a lista do que fazer.
2. **Uma meta na tela, um ritmo**: o único "por dia" do Painel passa a ser o do **sprint** (80, e o `q_hoje` do dia); a
   meta 10.000 aparece UMA vez, como o alvo da barra de projeção. Sem sprint (depois de 31/10), volta o por-dia da meta.
   Isso revoga, para a tela e até 31/10, a regra s203 "o único por-dia é o da meta" -- §10.10 (declarar, lapidar,
   cadastrar o termo) no `cronograma-contract` e onde mais a regra estiver.
3. **Figura nas 5 RDs da UERJ 2022** com a skill `anima` (teste): uma figura de mecanismo por RD, onde ela ajuda a
   escada (ex.: CM -- PTHrP e osso blástico x lítico; CIR -- curva de febre pós-operatória por dia; GO -- EGB e cortes;
   PED -- cateter umbilical -> trombose portal -> varizes; MFC -- sensível x específico). Figura inline (SVG/HTML)
   dentro da RD, legível no leitor do hub (tema v3, 390 px), com a fonte citada; nenhuma afirmação clínica nova sem a
   fonte da própria RD.

## Success Criteria

- Painel real: o tile de Questões mostra `0 de 76` em 13/10 (o `q_hoje` do sprint), não `~115`; o Ritmo compara com 80;
  "114,9" não aparece; a barra de projeção mostra 7.817 -> 9.306 -> 10.000. Teste de paridade: o `q_hoje` do tile = o do
  "Plano de hoje" = o do boot.
- Sem legenda em prosa no dashboard (teste: nenhum `<p class="nota">` dentro dele).
- `ui_capturas.py` (painel) a 390/768/1280 sem rolagem horizontal; contraste dos tiles dentro do `docs/UI.md`.
- As 5 RDs ganham 1 figura cada, conferidas no leitor a 390 px; RD sem figura útil fica sem (declarado).

## Scope v0

1. Dashboard + meta única na tela (`tools/painel.py`, testes, `docs/UI.md`, contratos).
2. Figuras anima nas 5 RDs `artifacts/aula-rd-*-1310.html` -- **só depois que ele instalar a skill** (código de terceiro:
   `! npx skills add Garinmckayl/anima -g -a claude-code`); antes, a part fica bloqueada e declarada.

## Anti-scope

- Artifact novo; mudar Teoria/Listas/Cards; FSRS; a meta em si (10.000 segue a meta declarada).
- Figuras em aulas-base e resumos, e refazer aulas/resumos: **próximas sessões** (HANDOFF), decisão dele.
- Instalar a skill pelo agente.

## Technical Context

- `tools/painel.py`: `_html_dia` (Hoje), `_html_ritmo` (Ritmo; já sem a nota), `_html_blocos` (tabela), `_bloco_sprint`/
  `_html_sprint` (Plano de hoje), CSS no próprio arquivo; dados em `coletar()` (`ritmo`, `blocos`, `sprint` com
  `fechando_q`, `q_fora`, `fora`). `plano.agenda_sprint`/`resumo_sprint` = fonte do sprint; `performance.volume_vs_marco`
  = o por-dia da meta.
- Regras de UI: `docs/UI.md` (tokens, `--horizonte` é o único gradiente; ciano = progresso/ação; âmbar = aviso);
  skill `dataviz` (forma, cor, tiles) e `artifact-design`.
- RDs: `artifacts/aula-rd-{cm,cir,go,ped,mfc}-1310.html` (CSS só com tokens, `.wrap` único, leitor injeta `tema.css` +
  `tema-aula.css`).

## Open Questions

- A barra de projeção mostra o "fora do sprint" em cinza ou em âmbar? Proposta: cinza (não é erro, é o que não cabe).
