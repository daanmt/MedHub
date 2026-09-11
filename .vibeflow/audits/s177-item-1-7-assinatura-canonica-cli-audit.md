# Audit Report: s177 item 1.7 -- D5, assinatura canônica de CLI (+ rider F97)

**Data:** 2026-09-11 · **HEAD base:** `ca5e333` · **Escopo:** item 1.7 da fila selada (janela 3)

**Veredito: PASS**

> **Razao declarada para o formato:** item de fila de divida tecnica (`docs/MEMORIA-AUDITORIA.md
> §11`, linha 1.7), sem spec em `.vibeflow/specs/`. O DoD auditado e a decomposicao da instrucao
> selada -- *"assinatura canonica das CLIs: UMA spec, N arquivos, lint fail-loud"* -- declarada
> antes da execucao.

## DoD Checklist

- [x] **1. Medicao ANTES do remedio, e ela corrigiu a estimativa.**
  O D4 amostrava *"`day_plan` (4 de 10 flags), `recurate_cards`, `detect_clones`, ..."*. Medido:
  **65 flags orfas em 24 CLIs** e **17 CLIs sem skill dona** -- de 168 flags em 32 CLIs (**39%**).
  Entre os sem dona, `recurate_cards` (reescreve o baralho in-place, preservando FSRS) e
  `normalize_taxonomia` (declaradamente **[DESTRUTIVO]**): o uso correto dos dois so existia no
  fonte.
- [x] **2. UMA spec, N arquivos.**
  `.claude/commands/engenharia-cli.md` -- a casa dos CLIs que nao pertencem a skill de estudo,
  cobrindo 17 deles em 5 secoes (sensores · manutencao do `ipub.db` · curadoria em lote · Plano do
  Dia · posicao no cronograma), com o marcador `[DESTRUTIVO]` e o ponteiro para `§10.7` em cada um
  que grava. Sem ela a §7.2 era **literalmente inexequivel** para esses CLIs: nao havia skill onde
  a assinatura pudesse morar.
- [x] **3. Os 7 CLIs COM dona receberam a assinatura na dona, nao na spec nova.**
  `registrar_sessao_bulk` (8 flags) -> `importar-planilha.md` · `dormant_refresh` (3) ->
  `revisar.md` · `emed_flashcards` (3) + `audit_card_atomicity` (1) -> `estilo-flashcard.md` ·
  `cobertura_conhecimento` (1) -> `extrair-pdf.md` · `insert_questao --status` ->
  `analisar-questao.md`. **`day_plan` inteiro foi para `engenharia-cli.md`** (a maioria das flags e
  de harness/boot/fechamento) com ponteiro explicito no `revisar.md`, para a assinatura nao existir
  em dois lugares -- que e o que a §7.2 proibe.
- [x] **4. Lint fail-loud, e o "loud" e BLOCK por MEDICAO.**
  `tools/cli_signature_check.py` + check 15 do `auto_check`. Nasce **BLOCK**, nao WARN, porque a
  politica *"regra nova nasce WARN e vira BLOCK quando a base zerar"* teve sua condicao satisfeita
  **no mesmo commit**: 65 -> **0** orfas, 17 -> **0** CLIs sem dona. Mesma mecanica do F79b na s176.
- [x] **5. O sensor le o programa, nao o arquivo.**
  Extracao por **AST**. A 1a versao usava regex sobre o fonte e se acusou: a string
  `add_argument("--x")` escrita na propria docstring virou uma flag `--x` inexistente. O caso virou
  teste (`test_flag_citada_em_docstring_nao_conta`).
- [x] **6. Ratchet testado.**
  `tools/test_cli_assinatura.py`, 11 testes: AST x docstring · fallback em arquivo quebrado · orfa
  sem skill · documentada na dona · **skill que nao cita o CLI nao o documenta** · documentacao
  parcial · CLI sem flag · suite nao e CLI · isento pulado · **toda isencao tem motivo escrito**
  (licao F95) · e o teste de repo real exigindo **zero**.
- [x] **7. Paridade e tabela gerada.**
  `sync_skills.py` rodado, `--check` **exit 0** (§10.3). A tabela §7.4 do `AGENTE.md` foi
  **regenerada** por `reachability_check --tabela` (ela e gerada, nao editada) e o §7.3 ganhou a
  linha do `/engenharia-cli`. `reachability_check`: **131 alvos, 0 orfaos**.
- [x] **8. Suite verde e harness aprovado.**
  `pytest -q` -> **605 passed** (594 -> 605). `auto_check --all` -> **PASSED** com o check novo
  verde.

## Rider F97 -- prescricao revogada viva no codigo

- [x] **Achado, corrigido e cadastrado.** Lendo `--help` para escrever as assinaturas: o help de
  `dormant_refresh --kind` dizia *"Gatilho do PREPARAR"*, e `day_plan.py:756` montava o passo do dia
  como *"..., **PREPARAR** {descomprimido}+mecanismo, {largura}; depois DRENAR"* -- mecanismo
  revogado na s170, **na ordem que a s170 inverteu**, na string que o agente le no **1o turno de
  toda sessao**. Seis dias depois de uma revogacao que teve lapide, contrato v1.3 e cadastro de
  termo.
- [x] **A classe e o FORMATO do portador.** `_PORTADORES_NORMA` so tinha markdown. F90 mirou o
  registro de TERMOS; F95, o de PORTADORES; este mira a premissa por baixo: *norma mora em
  documento*. Nao mora -- as strings de `day_plan` e do `--help` sao o portador mais proximo da
  execucao que existe. `tools/day_plan.py` e `tools/dormant_refresh.py` entraram na lista.
- [x] **Provado, nao presumido.** Com a frase plantada numa linha ativa o gate acusou
  `('tools/dormant_refresh.py', 189, 'prescricao', ...)`; removida, volta a `[]`.

## Pattern Compliance

- [x] **Sensores (WARN-first / promocao por medicao):** a promocao a BLOCK cita a condicao da
  politica e a medicao que a satisfaz, no comentario do proprio check.
- [x] **Assinatura de sensor uniforme:** `run_checks(root=None) -> [{'alvo','payload'}]`, igual a
  `doc_drift` e `reachability_check`; entra no `_ledger_record` como os demais.
- [x] **Fonte unica:** `engenharia-cli.md` **aponta** para `estilo-flashcard.md` e `revisar.md` em
  vez de repetir regra de autoria/revisao; `revisar.md` aponta para `engenharia-cli.md` para
  `day_plan`. Nenhuma assinatura em dois lugares.
- [x] **Tabela gerada nao se edita a mao** (`AGENTE.md §7.4`): regenerada pelo comando que a gera.
- [x] **Isencao com motivo escrito** (`ISENTOS`, 3 entradas) -- e um teste trava isso.
- [x] **Encoding §4.5** no material novo: `->` em vez de seta Unicode nos arquivos de codigo.

## Convention Violations

Nenhuma.

## Critical Gate

Clean -- nenhuma regra do catalogo casa o diff. O item e read-only sobre dados: nao escreve no
`ipub.db`, nao altera schema, nao toca credencial. As unicas escritas sao arquivos de documentacao,
um sensor novo, um teste novo e 4 linhas de string em 2 CLIs.

## Limites DECLARADOS (nao maquiados)

1. **Extracao estatica.** Parser construido dinamicamente escapa. Rodar 32 subprocessos `--help` em
   todo commit custaria mais do que o sinal vale; a convencao da casa e `add_argument` explicito.
2. **Presenca, nao semantica.** O check ve a string `--x` na skill certa; nao julga se a linha
   explica o argumento. Mede **piso**, nao qualidade -- e o piso agora esta em 100%.
3. **Flag generica pode colar em skill vizinha.** `--json`/`--apply` mencionados por causa de outro
   CLI contam como documentados. Isso **INFLA** a cobertura (falso negativo), nunca acusa
   injustamente.
4. ⚰️ **"Flag documentada em DUAS skills" NAO e reportada.** A medicao encontrou candidatos, mas o
   unico sinal disponivel e **co-ocorrencia**, que acontece o tempo todo entre skills vizinhas.
   Converter isso em achado seria inventar metrica. Declarado como nao-verificavel por este check.
5. **A isencao por SECAO do gate de revogacao nao existe em `.py`** (e baseada em heading markdown):
   em codigo a isencao cai para heuristica de **linha**. Comentario de lapide com `⚰️` passa; lapide
   de varias linhas sem marcador em cada uma, nao. Ampliar para bloco de comentario e trabalho da
   **1.8**.
6. **Falso positivo medido e descartado:** `app/memory/__init__.py:5` contem `Camada 1` com outro
   significado (camada de memoria). Por isso o arquivo **nao** entrou em `_PORTADORES_NORMA` -- e o
   limite de substring literal que o F90 ja declarou, encontrado aqui pela segunda vez.

---

12 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.
