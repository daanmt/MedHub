# PRD: MedHub HUB -- uma pagina so (Cards + Aulas + Painel), permanente, com o Claude Code como motor

> Sem discover, por decisao do `/ai-eng` (ai-eng-9c, 22/09/2026 ~19:30): o PRD e o brief
> `docs/HUB-BRIEF-2026-09-22.md` + as decisoes fechadas abaixo + os fatos do runtime medidos na s192.
> Permit textual (operador, 22/09): *"deixar o medhub aberto no claude code, e que atraves da pagina
> deployada conseguir utilizar o medhub remotamente pelo celular, enquanto conseguisse interagir com os
> artifacts in live, com o claude code sendo o 'motor' do processamento e gestao do banco de dados."*

## Problem

A conta claude.ai e COMPARTILHADA com o time de conteudo. Cada aula-base, player e painel que o MedHub
publica vira um artifact novo na galeria do time; o operador apaga por higiene; os links do HANDOFF morrem
no mesmo dia. Medido em 22/09: player de 16/09, Autopsia da UERJ 2023, painel (duas URLs em minutos) e a
aula de Hernias apagados. "URL fixa" e "URL nova" tratam sintoma. A causa e a poluicao, nao a hospedagem.

## Target Audience

Operador unico. Le no CELULAR (touch; `nowrap` longo e `sticky` alto sao defeitos registrados), estuda
pelas aulas-base, drena cards no player (60 cards em 16,5 min, s183). O time de conteudo compartilha a
conta e ve a galeria.

## Proposed Solution

Um artifact "MedHub", fixado, republicado no lugar. A pagina (`index.html`, montada por `tools/hub.py
--build`) tem 3 abas: **Cards** (o player INLINE, lote injetado, capability `db`), **Aulas** (lista de
links para `aulas/<slug>.html`) e **Painel** (link para `painel.html`). Os secundarios sao `files` do MESMO
artifact. O Claude Code e o motor: le as notas por `ArtifactData`, grava o FSRS por `--record-lote`
(`record_review`, caminho unico), monta por `hub.py --build`, republica por `Artifact publish` com `url`.
A pagina escreve UMA coisa: `sessoes/<sessao>/notas`.

## Decisoes fechadas em 22/09 pelo /ai-eng (ai-eng-9c; registro 166 do ledger dele)

Casadas por conteudo. O `history/exchange-log.jsonl` daqui so registra o que SAI (hook no `SendMessage`);
o texto integral da resposta vive no ledger do `/ai-eng` (`brain/observed-systems/exchange-log.jsonl`) --
este PRD e o portador do destilado no repo.

1. **Artifact runtime x deploy externo -> GO artifact.** Externo = backend proprio e perde o `db`.
   Anti-apagamento de custo zero no 1o publish: (i) `pin` uma vez (a conta e compartilhada, o time ve o
   pin); (ii) `description` = "permanente, republicado no lugar. NAO apagar."; (iii) `<title>` fixo
   "MedHub", nunca datado. Trade-off aceito: quem usa a conta ve o estudo (notas de drill, nao PHI). Humano
   ainda pode apagar -- a DoD MEDE sobrevivencia, nao a promete.
2. **Player INLINE no `index.html`**, nunca arquivo secundario: a capability `db` e declarada para a
   PAGINA; se o runtime chega a arquivo secundario nao foi verificado. Inline e dominante (se chegar, nao
   custa; se nao chegar, e a unica que funciona). `files` so para estatico.
3. **RD = arquivo do hub derivado de `history/session_NNN.md`** pelo `hub.py --build` (v1a). `db` so para
   o que a pagina origina (notas; comandos no v1b). Motivo: RD no `db` + copia em `history/` seria a 4a
   dupla autoridade. `onSnapshot` so volta se o reload for atrito MEDIDO (v2).
4. **Comandos (v1b) = colecao `comandos` no `db`**, lida por pull (`/loop` + boot); comentario e canal
   secundario, "ao vivo" so dentro de sessao que armou o watch, e a DoD do v1b MEDE.
5. **Limite do `files` = ENTRADAS (255)**, nao bytes. No update, arquivo OMITIDO e MANTIDO; so `null`
   remove. Publicar `files` exige ter lido/listado os paths. Politica como DADO + teste: cap de aulas =
   120; manifesto emite `null` para o que sai; historico fica em `artifacts/` (SSOT).
6. **Timing:** v0 agora (fora do estudo); v1a antes de 01/11; v1b depois de 01/11; v2 fechado.
7. **Sequencia:** spec direto -> implement (F93) -> `/vibeflow:audit` -> selo. Silencio do `/ai-eng` = GO.

## Fatos do runtime medidos na s192 (contrato 0.2.54, `.d.ts` do harness)

- **`db` tem teto de 5.000 documentos por artifact.** Fonte: `db.d.ts` do contrato 0.2.54, bloco `DB`
  ("CAPACITY: an artifact's database holds at most 5,000 documents in total"), servido pelo harness em
  `bundled-skills/<versao>/artifact-capabilities/0.2.54/db.d.ts`. Notas = 1 doc por card: ~55 dias a 90
  notas/dia, ~25 dias a 200/dia (22/09 foram 202 no lote). Pagina permanente exige poda.
- **Regras do `db`:** `capabilities.db.rules = [{path, read, write}]`, niveis `view < interact < admin <
  owner`; raiz default `read: view, write: interact`. **"The owner meets every level"**: com a conta
  compartilhada, quem abre logado nela e OWNER. A regra limita membros da org em `interact`; para o owner,
  a fronteira e o codigo da pagina (um unico write path) + a validacao do `--record-lote`.
- **`window.claude`:** existe antes do script quando a pagina esta no frame do viewer; servida top-level,
  todo `use()` resolve `null` "for now". Arquivo secundario navegado dentro do frame: nao documentado.
- **Publish em artifact que a conversa nao leu e RECUSADO** (entrega a versao viva); `files` sobre path nao
  lido/listado tambem.
- **`Artifact list` devolve no maximo 50** por chamada: prova de "nenhum artifact novo" e por URL no topo
  da galeria, nao por contagem total.
- **`fsrs_revlog.review_time` e LOCAL** (carimbo F80); a nota da pagina carrega `ts` UTC ISO. A
  idempotencia do `--record-lote` e derivavel do revlog.

## Alteracoes da s192 sobre o plano do /ai-eng (decididas, reportadas no canal)

- **A. Aulas entram no v0** (eram v1a). A DoD 6 ja exige o manifesto com `null` para aula removida;
  conectar agora evita construido-e-nao-conectado e deixa o operador apagar os 4 artifacts de aula de
  22/09. Custo: `aula-base.md` entra no F90 do v0. **RD segue no v1a.**
- **B. `--record-lote` idempotente pelo revlog** -- REVISTA no mesmo dia pelo `/ai-eng` (GO com
  condicao): com o relogio da GRAVACAO, "review_time >= ts" engole em silencio uma 2a nota do mesmo card, e o
  FSRS calcula o intervalo a partir da hora errada. Forma final: o revlog grava o MOMENTO DA REVISAO (ts da
  nota, truncado ao segundo); JA GRAVADA = linha com `review_time` igual; revisao mais nova sem a igual =
  FORA DE ORDEM, reportada. Motivo de origem: pagina permanente = sessao relida (o card #92 de 22/09
  precisou de marca manual `gravado_em` no `db`).
- **C. Poda do `db` no rito do v0** (docs da sessao que SAIU do hub, depois da troca de lote), nao no v1b:
  a 200 notas/dia o teto chega antes de 01/11. Gate do `/ai-eng`: so poda sessao cuja releitura deu 0 novas
  e 0 rejeitadas; nunca a do lote corrente; contagem no session log.
- **D. DoD 7 declara o limite do owner** (acima). O teste por `as_level: interact` prova a regra para
  membro da org; nao prova nada sobre o owner. Complemento do `/ai-eng`: a fronteira real vira teste NO
  WRITER -- `--record-lote` poe doc estranho em quarentena (rejeita e reporta, grava os validos).
- **E. Ordem de apagar (do `/ai-eng`):** os 4 artifacts avulsos de aula de 22/09 so saem DEPOIS de o
  operador abrir 1 aula pelo hub no celular.
- **F. Aulas e painel abrem DENTRO do hub (s192, ao carregar o contrato de pagina):** o contrato documenta
  `fetch()` relativo de arquivo publicado junto; navegar o frame para outro arquivo nao e documentado. A aba
  busca o arquivo e o mostra num leitor na propria aba (iframe `srcdoc`, altura pelo conteudo), sem sair da
  pagina: o drill nao perde estado e o `db` nao e tocado. Falha do `fetch` -> aviso com link para a pagina
  inteira. Os secundarios sao publicados direto das fontes (`artifacts/`), sem copia.

## Estado ao fim da s192 (22/09/2026)

- **Entregue:** parte 1 (`tools/hub.py` + `core/templates/hub.html` + testes) e parte 3 (rito F90 +
  contrato v1.7 + 1o publish). Hub no ar: https://claude.ai/artifact/3RksMfkzNWYSQD7D6JXNEr (fixado,
  `db` com 2 regras). DoD 7 provada por comando (`interact` escreve em `sessoes/*/notas`, e RECUSADO em
  `comandos` e `rd`); o servidor confirmou o teto: "1 of 5000 documents used".
- **Pendente:** parte 2 (ver o estado no topo da spec) e parte 4 (medicao nas proximas sessoes e no
  celular). Gate no rito ate a parte 2: notas do hub nao sao gravadas.
- **Custo de leitura por publish, com fonte (s193):** s192 = **378.575 tokens** para reler as 6 aulas antes do publish (Sonnet, `usage` do harness, `history/session_192.md` §4); s193, com o DIFF = **244.531 tokens** para 1 arquivo novo, a Autopsia de 399 KB (`history/session_193.md` §4) -- as 6 ja publicadas ficaram MANTIDAS e nao foram relidas.
- **Notas do `/ai-eng` no selo (22/09):** (a) o manifesto do `--publicado` vira DIFF contra a listagem (omitido = mantido): so arquivo novo ou alterado entra, e aula ja publicada nunca e relida -- a regra "ler inteiro o que a sessao nao escreveu" custou 378k tokens para 6 aulas e se repetiria a cada fechamento; (b) candidato v1: o lote sai do `<script id="lote">` para o `db` (`lotes/<data>`), e o `index.html` (~226 KB) so e republicado quando o CODIGO muda. (c) DoD 2 ganha "links de fonte dentro da aula abrem": no `srcdoc` link relativo morre -- as 6 aulas de 22/09 so tem URL absoluta e ancora `#` (varredura da s192), entao passam por construcao; aula nova com link relativo quebraria.

## Success Criteria (DoD v0, binaria)

1. A URL do hub fica nas 8 primeiras linhas do `HANDOFF.md` (o hook trunca em 8, F126/s189) e sobrevive
   a 2 fechamentos (publish com `url` sem `artifact-deleted`, registrado no selo de cada um).
2. Drill de >= 20 cards no celular pelo hub gravado por `--record-lote --apply --expect N` (COUNT-ASSERT
   batido); no meio do drill ele abre 1 aula, volta, e a nota seguinte ainda cai no `db`. So o operador
   prova.
3. Painel regenerado aparece na aba sem artifact novo: `Artifact list` (limit 50) antes e depois sem URL
   novo, numeros no session log; o rito roda numa SESSAO NOVA (read -> list files -> `hub.py --build
   --publicado` -> publish com `url` + `files`).
4. `python -X utf8 tools/auto_check.py --changed` PASSED.
5. F90 no MESMO commit: `registrar-sessao.md` §6 (lapide de 22/09 revertida: mesma URL = invariante;
   `artifact-deleted` = excecao REPORTADA no HANDOFF), `revisar.md` "DRENAR no player" (publicar =
   republicar o hub; 1o publish com `capabilities` explicito), `aula-base.md` (aula = arquivo do hub),
   `revisao-calibrada-contract.md` v1.7 (estava na v1.6), marcadores `TERMO-REVOGADO` em `docs/MEMORIA-AUDITORIA.md`.
6. `hub.py --build` com golden do manifesto + propriedade (todo href relativo do index existe no
   manifesto; `|manifesto| <= 255 - 8`) + perturbacao (aula removida -> `null`) + `--check` que falha com
   arquivo inexistente; e `--record-lote` idempotente (2a leitura da mesma sessao grava 0).
7. Fronteira de escrita testada por comando: `ArtifactData` com `as_level: interact` cria em
   `sessoes/*/notas` e e RECUSADO em outra colecao; limite do owner declarado no rito.

## Scope v0

- `tools/hub.py` (novo, nucleo puro + CLI): `--build`, `--check`, `--extrair-lote`.
- `core/templates/hub.html` (novo): casca de 3 abas; o player entra por regioes marcadas de
  `core/templates/player.html` (fonte unica do player; o standalone continua montavel).
- `tools/fsrs_queue.py` + `app/utils/db.py`: idempotencia do `--record-lote` pelo revlog.
- Rito e contratos (F90): `revisar.md`, `registrar-sessao.md` §6, `aula-base.md`,
  `revisao-calibrada-contract.md`, `docs/MEMORIA-AUDITORIA.md`, `engenharia-cli.md` (assinatura do
  `hub.py`), espelhos, `HANDOFF.md`.
- Atos (agente): 1o publish (capabilities + description + pin + titulo), teste da DoD 7, apagar o doc de
  teste; operador: DoD 2; sessao seguinte: DoD 3.

## Anti-scope

- RD no hub (v1a). Comandos/`comandos`, watch de comentario, `/loop` (v1b). `room`, `sample` (v2).
- Deploy externo; backend proprio; qualquer UI fora de Artifact (zero Streamlit).
- A pagina gravar FSRS, cunhar card, editar resumo, decidir fila. Botao "aposentar".
- Mudar o formato das notas na pagina (1 doc por card continua) ou a regua/relearning do player.
- Artifact novo para teste ou spike: spike, se houver, e no proprio hub.

## Technical Context

- `core/templates/player.html` (542 linhas): lote em `<script id="lote" type="application/json">`
  (marcador UNICO, `fsrs_queue.MARCA_ABRE`, guarda de ambiguidade); `claude.use("db")` ->
  `sessoes/<sessao>/notas`, 1 doc por card `{card_id, rating_primeira, ts, defeito?, motivo?}`; restaura
  do `db` no load; teclado global (Espaco/1-4/D) -- no hub precisa de guarda por aba.
- `tools/fsrs_queue.py`: `injetar_lote(template, lote)`, `ler_notas`, `aplicar_notas` (dry-run +
  `--expect` + COUNT-ASSERT pos). Testes em `tools/test_fsrs_queue_player.py`.
- `tools/painel.py --html` -> `artifacts/painel.html` (11 KB, mesmos tokens de cor do player; classe
  `.bloco` colide com a do player -> fica arquivo secundario, nunca inline no v0).
- Aulas: `artifacts/aula-*.html` (6 hoje; 45-66 KB, `aula-s17` 339 KB), `<title>` legivel, data pelo git.
- Registro de suites: `pytest.ini` `python_files` (F43, `test_suites_orfas`). Termos revogados:
  marcador `<!-- TERMO-REVOGADO: termo | onde -->` em `docs/MEMORIA-AUDITORIA.md`.
- O CLI nunca fala com a API de Artifact: publicar, listar, ler o `db` sao atos do agente.

## Open Questions (medidas, nao decididas no papel)

- Navegar do index para um arquivo secundario e voltar mantem o `db` da pagina? (DoD 2 mede.)
- O `Artifact read` de uma sessao nova devolve o index inteiro no contexto? (DoD 3 mede o custo; se alto,
  v1 move o lote para `lote.json` buscado pela pagina.)
