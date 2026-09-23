---
type: spec
projeto: MedHub
feature: medhub-hub-v0
part: 1
slug: medhub-hub-v0-part-1
status: ready
relates_to:
  - .vibeflow/prds/medhub-hub-2026-09-22.md
  - docs/HUB-BRIEF-2026-09-22.md
  - core/templates/player.html
  - tools/fsrs_queue.py
---

# Spec -- MedHub HUB v0, parte 1: `tools/hub.py` monta a pagina unica (Cards + Aulas + Painel) e o manifesto do publish

> Sessao s192 (22/09/2026, noite), ENGENHARIA. PRD `medhub-hub-2026-09-22` (sem discover, decisao do
> `/ai-eng`). Passo (i)+(ii) da ordem do `/ai-eng`: montador puro com testes, e a casca de 3 abas com o
> player INLINE. Nada e publicado nesta parte.

## Objective
Uma pagina so -- `index.html` com as abas Cards (o player que ja existe, inline), Aulas e Painel -- e o
mapa `files` do publish saem de UM comando testado, em vez de um artifact novo por aula, player e painel.

## Context
Hoje cada superficie e um artifact separado (player por `fsrs_queue.py --build-player`, painel por
`painel.py --html`, aula por `/aula-base`); o operador apaga os artifacts porque a conta e compartilhada e
os links do HANDOFF morrem. O `/ai-eng` fechou: player INLINE na pagina (o `db` e da pagina; runtime em
arquivo secundario nao verificado), `files` so para estatico, limite = 255 ENTRADAS, arquivo omitido no
update e MANTIDO e so `null` remove. O player vive em `core/templates/player.html` (542 linhas, lote no
`<script id="lote">` de marcador unico, teclado global Espaco/1-4/D).

**Friccao (F110):** remove friccao VICIOSA -- link que morre, artifact novo por superficie, galeria do time
poluida; nao toca nenhuma virtuosa (recall antes do verso, nota honesta, relearning seguem no player
intacto).

## Definition of Done
1. `python tools/hub.py --build --lote ARQ.json [--publicado LISTA] [--out DIR]` grava em `DIR` (default
   `tmp/hub/`) `index.html` e `manifesto.json` = `{"file_path": ..., "files": {publicado: fonte|null}}`,
   com as fontes DIRETO das SSOT (`artifacts/painel.html` -> `painel.html`, `artifacts/aula-<slug>.html` ->
   `aulas/<slug>.html`; paths relativos a raiz do repo), pronto para o `Artifact publish`; roda o `--check`
   no fim e sai != 0 se ele acusar. Aulas e painel abrem DENTRO do index (leitor na propria aba, `fetch`
   relativo + iframe `srcdoc` com altura pelo conteudo; falha do `fetch` -> aviso com link para a pagina
   inteira), sem navegar o frame.
2. `tools/test_hub.py` (inscrito em `pytest.ini`) passa com: **golden** do manifesto para um repo
   sintetico fixo; **propriedade** (todo href relativo do index esta no manifesto com valor nao-nulo;
   `entradas + 1 <= 255 - 8`; `extrair_lote(montar_index(..lote..)) == lote`); **perturbacao** (aula que
   sumiu da fonte e consta em `--publicado` sai como `null`); **cap** (130 aulas -> 120 mais novas; as que
   caem e estavam publicadas viram `null`); `--check` falha com arquivo inexistente e com href fora do
   manifesto; titulo de aula com `<script>` sai escapado.
3. O player continua com UMA fonte: `core/templates/player.html` ganha marcadores de regiao (css, corpo,
   js; cada um exatamente 1x) e o `hub.py` compoe a partir deles; o teclado do player so age com a aba
   Cards ativa (`<html data-aba>`; sem o atributo, o standalone age como hoje). `tools/test_fsrs_queue_player.py`
   segue verde sem edicao, e um teste monta o hub com os templates REAIS.
4. Celular (feedback registrado): o `index.html` montado nao contem `sticky` nem `nowrap`, tem UM `.wrap`,
   rotulos de aba <= 15 caracteres, todo item de grid de conteudo variavel com `min-width:0`, alvo de toque
   >= 44px nas abas.
5. `python tools/hub.py --extrair-lote PAGINA.html --out-lote ARQ.json` recupera o lote de uma pagina
   salva (a versao viva lida por `Artifact read`), para o `--record-lote --lote` e para remontar sem
   depender de `tmp/`.
6. Craftsmanship: assinatura completa do `hub.py` em `.claude/commands/engenharia-cli.md` (D5), espelho
   regenerado (`sync_skills --check` exit 0); `python -X utf8 tools/auto_check.py --changed` PASSED; zero
   LaTeX e zero seta/travessao Unicode no codigo e na doc.

## Scope
`tools/hub.py` (novo), `tools/test_hub.py` (novo), `core/templates/hub.html` (novo),
`core/templates/player.html` (marcadores + guarda de aba), `pytest.ini`, `.claude/commands/engenharia-cli.md`
(+ espelho gerado).

## Anti-scope
Publicar qualquer coisa (parte 3). RD (v1a). Comandos, watch, `/loop` (v1b). Tocar `fsrs_queue.py`
(parte 2) ou o formato das notas. Regenerar o painel dentro do `hub.py` (o rito roda `painel.py --html`
antes). Painel inline na aba (a classe `.bloco` colide com a do player; fica arquivo). Politica de
selecao de aula por trilha/semana ou lista de fixas (com 6 aulas e cap 120, e YAGNI; a regra hoje e
"mais novas primeiro, cap 120"). Mexer em `artifacts/aula-*.html` ou `artifacts/painel.html` (fontes).

## Technical Decisions
- **Nucleo puro + casca impura.** `selecionar_aulas`, `montar_manifesto`, `montar_index`,
  `extrair_regioes_player`, `extrair_lote`, `hrefs_relativos`, `checar` recebem dados e
  devolvem dados (testaveis sem git, sem disco real). A casca (`main`) faz glob de `artifacts/aula-*.html`,
  le `<title>` por `html.parser`, pega a data de criacao por `git log --diff-filter=A --format=%as`
  (fallback: data do arquivo) e escreve no `--out`. Trade-off: data pelo git e deterministica no repo e
  dispensa registro manual (que envelheceria), ao custo de um subprocess por aula.
- **Composicao por marcadores, nao por copia.** `hub.html` tem placeholders unicos (`/* @hub:player-css */`,
  `<!-- @hub:player-corpo -->`, `<!-- @hub:player-js -->`, `<!-- @hub:status -->`, `<!-- @hub:aulas -->`,
  `<!-- @hub:painel -->`) e o SEU `<script id="lote">`; o lote entra por `fsrs_queue.injetar_lote` (mesma
  guarda de marcador unico e mesmo escape de `</script>`). Copiar o player para o hub criaria duas fontes;
  apagar o standalone mexeria no `--build-player` e seus testes -- fora do v0. Marcador ausente ou
  repetido = `ValueError` alto (licao do bug do marcador ambiguo, s183).
- **Secundarios abrem DENTRO do index, nunca navegando o frame.** O contrato de pagina do Artifact
  documenta `fetch()` relativo de arquivo publicado junto; navegar o frame para outro arquivo, nao (e
  `target=_blank` depende de o host servir top-level com sessao). A aba Aulas busca `aulas/<slug>.html` e
  mostra num iframe `srcdoc` (documento proprio: o CSS da aula nao colide com o do player), altura medida
  pelo conteudo (mesma origem); links externos da aula ganham `target=_blank`, ancoras internas rolam a
  pagina-mae, e o `data-theme` do hub passa para a aula. A aba Painel faz o mesmo com `painel.html` na 1a
  abertura. Ganho: o drill nao perde estado, o `db` nao e tocado, e nao ha copia nem link de volta a
  injetar. Plano B declarado (se o `srcdoc` falhar no celular): o link da lista ja e um `href` real.
- **Aba lembrada por hash (`#cards|#aulas|#painel`, o unico ancora que chega da URL) > `localStorage`
  (try/catch) > "cards".**
- **Manifesto = exatamente os argumentos `file_path` + `files`**, chaves ordenadas; `index.html` nunca
  entra em `files` (e o `file_path`) e nunca vira `null`.
- **O template nao traz `<!DOCTYPE>/<html>/<head>/<body>`** (o contrato de pagina diz que o publish
  embrulha o arquivo num esqueleto); `<title>MedHub</title>` nos primeiros 8 KB (so eles sao lidos para o
  titulo); o estado da aba mora em `data-aba` no elemento raiz, posto por script. `--publicado` aceita JSON (lista) ou texto (1 path por linha, `#`
  comenta) -- o agente transcreve o `Artifact list scope=files`.
- **Constantes como dado no modulo:** `CAP_AULAS = 120`, `LIMITE_ENTRADAS = 255`, `RESERVADAS = 8`.

## Applicable Patterns
- `warn-first-check.md`: o `--check` DETECTA e reporta; nao corrige. Diferenca declarada: ele e gate do
  proprio `--build` (exit != 0), porque manifesto com link morto e o defeito que o hub existe para matar.
- Padrao candidato registrado na part-9 e confirmado aqui: **"Artifact como superficie de entrada + CLI
  como writer unico"** -- a pagina so escreve notas; montar e publicar sao atos do agente.

## Risks
- **Player quebrar no hub** (CSS global do player, `h1`, `.wrap`): o hub adota o CSS do player como base
  (mesmos tokens) e so ACRESCENTA regras; teste de `.wrap` unico e de montagem com templates reais.
- **Teclado do player sequestrar a aba Aulas** (Espaco rolaria e viraria card invisivel): guarda por
  `data-aba`, com teste de presenca no JS montado.
- **Data de aula nao reproduzivel fora do git** (clone raso, arquivo novo nao commitado): fallback = data
  do arquivo, declarado na saida do `--build`.
- **`aula-s17.html` (339 KB) pesa na versao**: cabe (limite e por entradas e 16 MB por arquivo); nao e
  cortada.

## References
- `core/templates/player.html` -- a fonte do player que o hub compoe (nao copiar).
- `tools/fsrs_queue.py::injetar_lote` e `tools/test_fsrs_queue_player.py::test_template_real_e_injetavel_e_tem_wrap_unico` -- o mecanismo e o teste-modelo de template real.
- `tools/painel.py --html` -> `artifacts/painel.html` -- o arquivo que vira `painel.html`.
- `artifacts/aula-*.html` -- as fontes das aulas (6 em 22/09).

## Dependencies
Nenhuma.
