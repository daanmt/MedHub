---
type: spec
projeto: MedHub
feature: medhub-hub-v0
part: 3
slug: medhub-hub-v0-part-3
status: ready
relates_to:
  - .vibeflow/prds/medhub-hub-2026-09-22.md
  - .claude/commands/revisar.md
  - .agents/workflows/registrar-sessao.md
  - .claude/commands/aula-base.md
  - core/contracts/revisao-calibrada-contract.md
---

# Spec -- MedHub HUB v0, parte 3: o rito passa a republicar o hub (F90) e o hub vai ao ar

> Sessao s192 (22/09/2026). Passos (iii)+(iv) da ordem do `/ai-eng`: os tres portadores do rito mudam no
> MESMO commit (declarar + lapidar + cadastrar, AGENTE.md §10.10), e o 1o publish sai com
> `capabilities`, `description`, `pin` e titulo fixos.

## Objective
Todo fechamento, todo lote de cards e toda aula nova passam a REPUBLICAR o mesmo artifact "MedHub" (URL
nas 8 primeiras linhas do HANDOFF) em vez de criar um artifact novo, e a pagina so consegue escrever notas.

## Context
Hoje o rito cria artifact novo em tres portadores: `revisar.md` "DRENAR no player" (passo 3, "Publicar
como Artifact com `capabilities: {db: {}}`"), `registrar-sessao.md` §6 (painel; a lapide de 22/09 matou a
"mesma URL" porque ele apaga artifacts) e `aula-base.md` ("Ate esse motor existir: publicar a aula-base
como Artifact HTML direto"). Com UM artifact fixado e marcado "NAO apagar", "mesma URL" volta a ser
invariante (decisao do `/ai-eng`), e `artifact-deleted` vira excecao que REPORTA, nunca silencia.
Contrato do runtime (0.2.54): omitir `capabilities` no republish MANTEM a declaracao; `{}` LIMPA; regras do
`db` por nivel, e o OWNER atende todo nivel (conta compartilhada = quem abre e owner). Publish em artifact
que a conversa nao leu e recusado; `files` sobre path nao lido/listado tambem. `db` tem teto de 5.000 docs.

**Friccao (F110):** remove friccao VICIOSA (procurar o link do dia, artifact novo por superficie, poda
manual da galeria); nenhuma virtuosa muda (o DRENAR continua silencioso, a RD continua no chat, a nota
continua do operador).

## Definition of Done
1. **F90 num commit so:** `revisar.md` ganha "DRENAR no hub" (abrir lote = gravar a sessao atual ->
   `--export-player` -> `hub.py --build` -> republicar com `url`, sem `capabilities`; fechar = `ArtifactData
   list` -> `--record-lote`; podar SO a sessao que SAIU do hub e SO depois que uma releitura dela deu
   `--record-lote` com 0 novas E 0 rejeitadas (`--expect 0`), nunca a sessao do lote corrente; `ArtifactData
   batch delete` <= 50 por chamada, re-list = 0, contagem podada no session log); `registrar-sessao.md` §6 (painel -> `hub.py --build` com o lote VIVO -> republicar; a lapide
   de 22/09 e revertida e `artifact-deleted` = hub recriado COM `capabilities` + `description` + `pin` e
   linha no HANDOFF, nunca silencioso); `aula-base.md` (aula = `artifacts/aula-<slug>.html` + republicar o
   hub); `revisao-calibrada-contract.md` -> **v1.7** (estava na v1.6; a superficie do DRENAR e a aba Cards do hub; regras do
   `db`; Invariantes A/C/F intactos); marcadores `TERMO-REVOGADO` em `docs/MEMORIA-AUDITORIA.md` para as
   frases mortas; espelhos regenerados. `python -X utf8 tools/auto_check.py --changed` PASSED (inclui o gate
   `CONTRATO_REVOGADO`).
2. **1o publish** do `tmp/hub/` montado com lote fresco: `<title>MedHub</title>`, `description`
   "MedHub: permanente, republicado no lugar. NAO apagar.", `pin: true`, `capabilities` EXPLICITO:
   `{db: {rules: [{path: "", read: "view", write: "admin"}, {path: "sessoes", write: "interact"}]}}`.
3. **Fronteira de escrita provada por comando (DoD 7 do PRD):** `ArtifactData set` com `as_level:
   "interact"` em `sessoes/dod7-teste/notas` passa; em `comandos` e em `rd` e RECUSADO; o doc de teste e
   apagado e o re-list da colecao volta vazio. O limite do owner fica ESCRITO no rito (a regra protege de
   membro da org em `interact`; para o owner a fronteira e o codigo da pagina + a validacao do
   `--record-lote`).
4. **Passe funcional do `db`** (verificacao do runtime): `ArtifactData list` da colecao que a pagina
   escreve (`sessoes/<sessao>/notas`) responde (vazia) logo apos o publish.
5. **HANDOFF:** a URL do hub nas 8 primeiras linhas, e a linha "Datas & links" aponta aulas e painel
   para as abas do hub. Os 4 artifacts avulsos de aula de 22/09 ficam com a ordem do `/ai-eng`: o operador
   so os apaga DEPOIS de abrir 1 aula pelo hub no celular (metade "abre 1 aula" da DoD 2) -- nunca antes.

## Scope
`.claude/commands/revisar.md`, `.agents/workflows/registrar-sessao.md`, `.claude/commands/aula-base.md`,
`core/contracts/revisao-calibrada-contract.md`, `docs/MEMORIA-AUDITORIA.md`, `HANDOFF.md` (+ espelhos
gerados). Atos: export do lote, build, publish, testes de `db`, delete do doc de teste.

## Anti-scope
Apagar os artifacts avulsos antigos (player 16-22/09, aulas de 22/09, Autopsia): e do operador. RD no hub
(v1a). Colecao `comandos` aberta (v1b; nesta parte ela e prova de RECUSA). `room`, `sample`, `user`.
Apagar `--build-player` ou o template standalone (continuam validos; o rito so deixa de publica-los).

## Technical Decisions
- **Raiz `write: admin`, `sessoes` `write: interact`:** tudo que nao e nota fica fechado para membro da
  org; notas seguem abertas para quem usa a pagina. Trade-off declarado: o owner (a conta compartilhada)
  passa por cima -- a regra nao e barreira contra quem abre logado na conta do time, e isso vai escrito.
- **Poda depois da troca de lote, nunca no fechamento:** apagar notas de um lote que ainda esta na pagina
  faria o reload reapresentar os cards como novos (a pagina restaura do `db`). A idempotencia da parte 2
  torna seguro reler antes de podar.
- **Termos revogados literais:** cadastrar as frases exatas que morrem ("Publicar como Artifact com",
  "publicar a aula-base como Artifact HTML direto", "sem prometer permanencia") -- o gate casa substring;
  o limite (mesma regra com outras palavras passa) fica declarado, como no §10.10.

## Applicable Patterns
- `agent-workflow-protocol.md` (fechamento): o rito continua ordem de atos do agente; o CLI nao publica.
- AGENTE.md §10.10 (F90): declarar + lapidar + cadastrar no MESMO commit.

## Risks
- **`artifact-deleted` no dia seguinte** (o time apaga mesmo fixado): o rito recria e REPORTA; a DoD 1 do
  PRD (parte 4) mede sobrevivencia em vez de prometer.
- **Publish recusado por "nao lido"** numa sessao nova: o rito comeca por `Artifact read` + `list
  scope=files` (parte 4 prova).
- **Pin/description nao impedirem o apagamento:** fora do controle do codigo; declarado no PRD.

## Dependencies
- .vibeflow/specs/medhub-hub-v0-part-1.md
- .vibeflow/specs/medhub-hub-v0-part-2.md
