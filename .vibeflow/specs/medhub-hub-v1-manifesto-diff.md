---
type: spec
projeto: MedHub
feature: medhub-hub-v1
part: 1
slug: medhub-hub-v1-manifesto-diff
status: implemented
relates_to:
  - .vibeflow/prds/medhub-hub-2026-09-22.md
  - tools/hub.py
  - tools/test_hub.py
---

# Spec -- MedHub HUB v1 (DIFF, nao confundir com o v1a = RD como arquivo): o manifesto do publish vira DIFF (so arquivo novo ou alterado sobe)

> Sessao s193 (22/09/2026). Decisao do operador via `/ai-eng` (item 3): o DIFF entra logo apos a
> part-2 -- "registro local de hash por path publicado; so arquivo novo/alterado vai em `files`;
> omitido = mantido pelo runtime". Nota (a) do PRD: o custo nao e o upload, e a RELEITURA -- o
> Artifact exige ler inteiro todo arquivo que a sessao nao escreveu antes de publica-lo, e as 6
> aulas de 22/09 custaram 378k tokens; sem o DIFF isso se repete a cada fechamento.

## Objective
Republicar o hub manda so o que mudou: aula ja publicada e intocada fica fora de `files` (o runtime
a mantem) e nao precisa ser relida.

## Context
`hub.py --build` poe TODA aula selecionada e o painel em `files` a cada build. A listagem do
artifact (`Artifact list scope=files`) da path, tipo e TAMANHO -- nao da hash (medido em 22/09) --,
entao o hub.py nao ve o conteudo do servidor: precisa de um registro local do que publicou.

## Definition of Done
1. `--build` calcula sha256 + bytes de cada fonte selecionada; um path fica MANTIDO (fora de
   `files`, listado em `manifesto["mantidos"]`) so se TRES evidencias batem: o registro tem a mesma
   sha256, o path esta na listagem viva (`--publicado`) e, quando a listagem traz tamanho, ele e o
   do registro. Qualquer falha = vai em `files`. `null` para o que saiu segue igual ao v0.
2. O registro (`<out>/registro_publicado.json`) so muda por `--confirmar`, depois do publish
   ACEITO: copia `<out>/estado_pos_publish.json` (escrito pelo build: o estado vivo que o publish
   deixa -- enviados + mantidos, sem os nulos). O build nunca escreve o registro.
3. `checar()` e `--check` contam os mantidos como vivos (link do index para aula mantida nao e
   link morto; o teto de entradas conta os dois).
4. Sem registro (1a vez, `tmp/` limpo) ou sem `--publicado`: tudo vai -- o comportamento v0.
5. `--publicado` aceita a listagem do Artifact como ela sai (`- "aulas/x.html"  text/html  63060
   bytes`, cabecalho ignorado) e JSON com `{"path", "bytes"}`; o formato v0 segue valendo.
6. Testes em `tools/test_hub.py` (golden v0 ganha so `mantidos: []`): 1 byte alterado vai; mantida
   fica fora e o check passa; registro sem o path na listagem viva vai (artifact recriado);
   tamanho vivo divergente vai; `--confirmar` + 2o build sem mudanca = 0 arquivos; nulo sai do
   estado. `engenharia-cli.md` (+ `revisar.md` passos 3-4) com espelho; `auto_check` PASSED.

## Scope
`tools/hub.py`, `tools/test_hub.py`, `.claude/commands/engenharia-cli.md`, `.claude/commands/revisar.md`
(+ espelhos).

## Anti-scope
Lote no `db` (v1b). Republicar o `index.html` so quando o codigo muda. Poda. Hash no servidor.

## Technical Decisions
- **Tres evidencias para omitir, uma para mandar.** Omitir errado deixa o hub com conteudo velho
  em silencio; mandar a mais so custa upload e releitura. Por isso o registro sozinho nunca
  basta: o path tem de estar vivo, e o tamanho vivo (quando ha) tem de bater.
- **Registro so apos publish aceito**, por comando explicito: build que nao virou publish nao
  contamina. Esquecer o `--confirmar` e seguro (o proximo build manda de novo).
- Registro em `tmp/` (local, gitignored): perde-lo custa um publish completo, nunca um errado.

## Applicable Patterns
- Nucleo puro + casca (padrao do `hub.py`): o DIFF e funcao pura sobre dicts.
