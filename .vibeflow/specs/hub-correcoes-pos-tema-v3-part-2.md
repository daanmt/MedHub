# Spec: hub-correcoes-pos-tema-v3 -- part 2: Cards com o contador do Painel

> PRD: `.vibeflow/prds/hub-correcoes-pos-tema-v3.md` (item 2). Gerada em 13/10/2026 (s226).
> Decisão das Open Questions (minha, salvo redireção dele): **sem fila de véspera nesta v0**. A aba Cards mostra o
> contador do Painel; lote no ar que não é de hoje aparece rotulado ("fila de DD/MM -- a de hoje ainda não saiu") e
> segue drenável; o `/hub-backend` renova no 1º tique do dia.

## Objetivo

O número de cards que ele vê na aba Cards é o mesmo do Painel ("3 de 150"), e uma fila de outro dia nunca se
passa pela de hoje.

## Contexto

Painel: `tools/painel.py` `_html_dia` publica `consumo_hoje`/`teto` (`<b data-vivo="cards" data-base=...>`) e o hub
soma ao vivo as notas do lote (`painelVivo` -> `vivoCards`). Aba Cards: `core/templates/player.html` mostra
`#feitos/#total feitos · fila #pendentes` do lote injetado (`<script id="lote">`, com `gerado_em`). Em 13/10 o Painel
dizia "0 +3 de 150" e a aba "3/100 · fila 98", porque o lote no ar era de 10/10.

## Definition of Done

1. O build do hub injeta o contador do dia do Painel (`consumo_hoje`, `teto`, `data` do build) num bloco JSON único
   (ex.: `<script id="hub-dia">`), e o cabeçalho da aba Cards mostra **"N de T hoje"** com N = `consumo_hoje` + as
   notas vivas do lote (a MESMA conta do `vivoCards`) -- teste `test_cards_e_painel_mostram_o_mesmo_contador` em
   `tools/test_hub_render.py` (ou `test_fsrs_queue_player.py`) verde.
2. A fila (`fila N`) continua visível como segundo número, sem competir com o contador (rótulo menor).
3. Lote com `gerado_em` de dia diferente do dia local do aparelho: aviso único acima do 1º card,
   **"Fila de DD/MM -- a de hoje ainda não saiu."**; os cards seguem drenáveis e gravam como hoje -- teste com
   `gerado_em` de ontem e de hoje.
4. `/hub-backend` (`.claude/commands/hub-backend.md`): o 1º tique de um dia com lote de dia anterior no ar decide
   `nova_fila` (`hub.py --precisa-publicar`) mesmo sem o lote drenado -- teste em `tools/test_hub.py`
   (`test_lote_de_ontem_pede_fila_nova`). Notas já dadas no lote antigo continuam gravadas pelo `--record-lote` antes.
5. Artesania: regra P09 (o lote conta no dia da 1ª nota), teto e FSRS intocados (suítes `test_fsrs_*` e
   `test_painel*` verdes sem edição de expectativa); `sync_skills --check` exit 0; sem cor literal nova.

## Escopo

- `tools/hub.py` (injeção do `hub-dia`; regra do `--precisa-publicar`), `core/templates/player.html` (cabeçalho e
  aviso), `core/templates/hub.html` (reaproveitar `vivoCards` para a aba), `.claude/commands/hub-backend.md` (+ sync),
  testes em `tools/test_hub.py` e `tools/test_hub_render.py`.

## Anti-escopo

- Fila de véspera (`--export-player --para <amanhã>`), botão que dispara backend (classificador, s194), mudar teto,
  P09, `--record-lote` ou algoritmo FSRS. O player standalone fora do hub (mostra o lote como hoje).

## Decisões técnicas

- **Fonte do número = o mesmo dado do Painel**, injetado no build, não recalculado no player: um número, uma conta
  (a palavra dele: "o Painel é o referencial").
- **Dia pelo relógio do aparelho** (`diaLocal`, já usado no player para P09), não pela data do build.
- **Renovar no tique, não na página**: a página não escreve fila; só o backend publica.

## Padrões aplicáveis

- `docs/UI.md` §4 (aviso = âmbar, nunca só por cor), §7; `/hub-backend` rito de publish; `db-access-layer` (contagem
  pelo `painel`/`db`, sem SQL novo no `hub.py`).

## Riscos

- **Dupla contagem** (o `consumo_hoje` do build já inclui notas gravadas do mesmo lote) -> usar o `sessao_gravada` como
  o `painelVivo` faz; teste com lote parcialmente gravado.
- **PC desligado** -> a fila velha fica rotulada; é o limite declarado da v0 (backend manual).

## Dependencies

- .vibeflow/specs/hub-correcoes-pos-tema-v3-part-1.md (mesmo `hub.html`; evitar conflito de merge, não lógica)
