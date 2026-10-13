## Audit Report: painel-dashboard-sprint part-2 (uma figura em cada RD da UERJ 2022 -- teste)

> 13/10/2026 (s226). Auditado pelo mesmo subagente que implementou, com olhar adversarial, sobre o diff do commit
> `1ad34e6`. Suíte `python -X utf8 -m pytest tools/ -q` = **1755 passed** (o hook do commit rodou a suíte inteira de
> novo: 1755 passed); `auto_check --changed` PASSED.

**Verdict: PASS** (com dois desvios declarados, nenhum defeito médio ou alto)

### DoD Checklist
- [x] **1. Skill instalada e o `SKILL.md` lido; o que ela roda declarado antes do 1º uso.** `.claude/skills/anima/SKILL.md`
  lido inteiro (174 linhas). O que ela roda: o kit é ESM puro para Node (`kit/iso-kit.mjs` e afins) que monta strings
  SVG e grava uma página HTML ao lado do `build.mjs`; `scripts/capture.mjs`, `drive.mjs` e `lines.mjs` abrem Chrome
  headless e falam com o DevTools em `127.0.0.1`; sem rede externa achada (varredura do principal). **Nenhum script da
  skill foi executado** nesta part (nem Node, nem Chrome): a skill serviu de molde de enquadramento (Fig n + título,
  legenda curta, fonte, esquema declarado, nada de linha solta). Desvio: a declaração está aqui e no retorno ao
  principal, não no `history/session_NNN.md` (o log da sessão é do principal).
- [x] **2. Uma figura por RD, inline, sem CDN nem arquivo externo, `Fonte:` = a da seção.** Uma `figure.fig-an` em cada
  `artifacts/aula-rd-{cir,cm,go,ped,mfc}-1310.html` (contagem = 1 em cada), SVG inline; a `Fonte:` de cada figura é
  copiada do `<p class="src">` da própria seção pelo gerador. Todas as 5 candidatas ganharam figura (nenhuma ficou sem):
  CIR febre por dia de pós-operatório com a marca das 24 h; CM vértebra blástica x lítica; GO os três cortes (37 sem,
  18 h, 38 °C) com a marca "Q32: 12 h, ainda não"; PED cateter umbilical -> trombose portal -> fluxo hepatofugal ->
  colateral -> varizes -> melena; MFC sensível x específico com pontos.
- [x] **3. Nenhuma afirmação clínica nova.** Conferido texto a texto contra a seção. Dois cortes feitos antes do commit
  por esse motivo: "forma osso (esclerose)" virou "forma osso" (a RD só diz "sem esclerose" do mieloma) e "não da lesão
  óssea" saiu da legenda do CM; no GO, "filho anterior com doença por EGB indica sempre" virou "do passado, só conta o
  filho com doença por EGB" (a redação da RD). Os pontos do MFC são declarados ilustrativos na figura e na legenda.
- [x] **4. Cores só por tokens; legível a 390 px e no claro.** 0 cor literal nas linhas adicionadas (grep de `#hex` e
  `rgb(` no diff); só os apelidos das aulas (`--teal*`, `--amber*`, `--plum*`, `--ink*`, `--line2`, `--sunk`, `--card`).
  Capturas a 390 e 768, escuro e claro (20 PNGs em `tmp/ui_capturas/rd_fig/`), todas lidas.
- [x] **5. Conferido no leitor + suíte verde.** Hub de rascunho `tmp/hub_dash_p2` + `ui_capturas.py --cenas aula
  --larguras 390,768` (abre `aulas/rd-cir-1310.html` no leitor real, medida "ok"; a cena para no topo da aula, então a
  figura foi conferida por render próprio com o MESMO esqueleto do `documentoCompleto(comTema(...))` do `hub.html`,
  numa moldura de largura exata -- o truque do iframe do próprio `ui_capturas`). Suíte 1755 verde.

### Pattern Compliance
- [x] `docs/UI.md` §1-§4: cor só por token, roxo = dado visual, ciano/teal = o que decide, âmbar = a marca da questão,
  estado nunca só por cor (contorno, rótulo "indica", "negativo exclui", cheio x vazado no MFC).
- [x] Largura: a moldura ocupa o `.wrap` inteiro; o `max-width:26rem` é do SVG DENTRO da moldura (não cria zigue-zague
  de bordas). Registrado no `docs/UI.md` §9.
- [x] Peso: 2,4 a 3,8 KB por figura + ~2,5 KB de CSS por RD (teto da spec: ~60 KB).
- [x] Anti-escopo: nenhuma aula-base, resumo ou outra RD tocada; nada de WebGL/3D; nada publicado.

### Achados (adversariais, todos registrados)
1. **CORRIGIDO antes do commit (médio, alta confiança).** 1ª rodada de capturas a 390: rótulos do CM cortados à
   direita, a marca do GO em cima do título "Bolsa rota", os veredictos do MFC encostados no divisor, rótulos do PED
   entrando no esôfago, e o "33 sem" do GO cortado 2-3 px à esquerda a 768. Geometria refeita, fonte do SVG subiu de 11
   para 11,5-13,5 px, e as 20 capturas foram refeitas e lidas.
2. **BAIXO / confiança média (decisão dele).** Em CIR, GO e MFC a figura repete a tabela logo acima ("tudo está longo
   demais", s195). Mantive as duas porque a spec é um teste de valor da figura; se a figura vencer, a tabela sai.
3. **BAIXO (desvio declarado).** Figuras estáticas: o molde da anima pede movimento calmo, readout ao vivo e controle de
   pausa; aqui não há mecanismo que ganhe com movimento e o leitor do hub é lido no celular. Também não usei o kit
   isométrico (3D de anatomia), que não serve para régua, linha do tempo e contagem.
4. **INFO.** O PED desenha o cateter entrando pela base da veia porta e o esôfago ao lado do fígado: posição
   esquemática, declarada na legenda ("Esquemático, fora de escala").
5. **INFO.** Tema claro conferido por captura, não por medida de contraste: os textos usam `--ink*`, `--teal-ink` e
   `--amber-ink`, os mesmos que o resto das aulas usa no claro.

### Critical Gate
Clean -- só HTML/CSS/SVG estático nas RDs e uma nota no `docs/UI.md`; nenhum script, escrita em banco ou rede.

Ready to ship (publicar é do principal).
