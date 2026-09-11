# Audit Report: s177 item 1.5 -- revogacao medida da heuristica F7 (+ rider F96)

**Data:** 2026-09-11 · **HEAD base:** `31c712a` · **Escopo:** item 1.5 da fila selada (janela 3 de engenharia)

**Veredito: PASS**

> **Razao declarada para o formato:** este item nao tem spec em `.vibeflow/specs/` -- e um item de
> fila de divida tecnica (`docs/MEMORIA-AUDITORIA.md §11`, linha 1.6), cujo DoD e a instrucao
> selada: *"medir precisao sobre a base; promover a BLOCK ou matar"*. O DoD auditado abaixo e a
> decomposicao binaria dessa instrucao, declarada antes da execucao. O `.vibeflow/specs/engenharia-ledger-part-5.md`
> (que ENTREGOU a heuristica em 05/07/2026) foi lapidado no mesmo commit para nao ser re-derivado.

## DoD Checklist

- [x] **1. Medicao unica, com ALCANCE e PRECISAO, registrada onde alguem le.**
  Alcance: o lexico tocava a RESPOSTA de **15** cards e a ARMADILHA de **12**, de **1611**; apenas
  **8 elegiveis** (casa nos dois lados: 91, 92, 94, 95, 96, 97, 913, 983), todos do mesmo tema --
  **0,5% da base, um unico eixo clinico**. Precisao: **2 disparos, 1 verdadeiro** (#95 verdadeiro,
  #913 falso-positivo por eixo IDADE). Registrada em 3 portadores: `AUDITORIA_MEDHUB.md §F7`
  (fechamento integral), `docs/MEMORIA-AUDITORIA.md §11` linha ~~1.6~~, e a lapide no proprio sitio
  (`tools/audit_flashcard_quality.py:87-114`).
- [x] **2. Instrumento e lexico deletados sem quebrar o CLI.**
  Removidos `check_discriminacao_lexicon`, `LEXICON_PATH`, `_norm_txt`, `import unicodedata`, a
  secao de report e `tools/data/competidores_categorias.json` (diretorio `tools/data/` ficou vazio e
  saiu junto). Varredura: nenhum outro consumidor de `tools/data` no repo. CLI re-executado --
  **exit 0** e numeros byte-identicos aos de antes (43/1419 com >=1 sinal · 1376 OK · cross-field
  84 / 26 / 2 / 461).
- [x] **3. Os achados REAIS do F7 preservados como estado, nao como prosa.**
  `python tools/reforja.py --fila` -> 2 abertas: `#95 discriminacao_incompleta` e
  `#120 diagnostico_raro_forcado`, ambas `[sem predicado]` **declarado** (fecham por palavra humana,
  `evidencia='humana'`). Verificado que nenhuma das duas colide com o `--backfill --dry-run` (9
  linhas, outros ids) -- a decisao do operador sobre o backfill segue intacta.
- [x] **4. Revogacao registrada de forma legivel por MAQUINA.**
  `tools/test_heuristica_f7_morta.py` (4 asserts), inscrita no `pytest.ini` (invariante F43 verde).
  Nasceu vermelha **duas vezes, por dois caminhos**: com o lexico recriado em disco
  (`test_lexico_nao_volta_ao_disco`) e com o simbolo reinjetado no modulo
  (`test_simbolos_da_heuristica_nao_ressuscitam`, mensagem verificada). Adaptacao consciente do
  ritual de 3 passos do `AGENTE.md §10.10`: para clausula de TEXTO o registro e o
  `_TERMOS_REVOGADOS`; para CODIGO morto, uma suite.
- [x] **5. Suite verde e harness autonomo aprovado.**
  `pytest -q` -> **583 passed** (578 -> 582 pelo item, +1 pelo rider). `python -X utf8
  tools/auto_check.py --changed` -> **PASSED**, 15 checks, nenhum BLOCK.
- [x] **6. Rider F96 com teste ANTES do fix e delta 0 no log de producao.**
  Vermelho medido em bytes (`212823 -> 212949`, 1 linha por rodada da suite); fix de 1 linha na
  fixture autouse do `conftest.py`; verificacao no repo real: suite completa com
  `history/memory_errors.log` em **delta 0 bytes**.

## Pattern Compliance

- [x] **Sensors (WARN-first) -- `.vibeflow/conventions.md`:** *"A sensor that cannot judge something
  stays silent about it -- honest silence beats fake coverage, and false positives are how a sensor
  gets ignored."* E a norma que decide este item: o sensor errava **metade** dos disparos no proprio
  eixo que sabia ler. Matar e a aplicacao da convencao, nao uma excecao a ela.
- [x] **Tombstone como afirmacao de ausencia:** *"A line that asserts an absence e a tombstone, not a
  lie"*. A lapide em `audit_flashcard_quality.py` afirma a ausencia, datada, com a medicao e o
  ponteiro para onde a classe continua viva. Evidencia: `tools/audit_flashcard_quality.py:87`.
- [x] **verification-stack (`AGENTE.md §10.8`):** o eixo semantico do F7 foi **declarado**
  nao-verificavel por gate em vez de convertido em metrica. Nenhum numero novo foi inventado para o
  painel.
- [x] **Higiene binaria (`AGENTE.md §3.4`):** veredito fica-ou-morre respeitado -- o lexico nao foi
  para `archive/`, foi deletado; o unico conteudo vivo dele (os 2 achados) migrou antes.
- [x] **CLI tools (`tools/`):** superficie argparse do CLI intocada; `main`, `build_sql`,
  `count_signal`, `SIGNALS` cobertos por smoke no teste novo.
- [x] **Db access layer:** nenhum `import sqlite3` novo; a medicao correu sobre `db.get_connection()`
  em script de scratchpad, fora do repo.

## Convention Violations

Nenhuma.

## Critical Gate

Clean -- nenhuma operacao destrutiva detectada no diff (`git diff HEAD`).
Notas de varredura, para o registro:
- A delecao de `tools/data/competidores_categorias.json` **nao** casa regra do catalogo (nao e
  migracao, schema, IaC, K8s ou config de seguranca); e remocao de insumo de heuristica, com
  consumidor unico verificado por `grep` e com o dado vivo migrado antes.
- Nenhuma regra de *protecao removida* (SEC101-103/107, DAT103/105) casa: o que saiu e um detector
  de qualidade de conteudo em modo WARN, jamais um guard de auth/sanitizacao/criptografia. O que a
  remocao poderia custar -- **cobertura** -- foi medido, e o saldo esta no DoD 1.

## Limites DECLARADOS (nao maquiados)

1. **A suite-guarda casa texto.** `test_lapide_segue_no_sitio` assere substring (`"HEURÍSTICA F7 --
   REVOGADA"`, `"tools/reforja.py --fila"`): pega remocao e reescrita grosseira da lapide, **nao**
   pega a mesma heuristica reintroduzida com outro nome de funcao e outro arquivo de lexico. Mesmo
   limite -- e mesma honestidade -- do gate `CONTRATO_REVOGADO`.
2. **Precisao medida sobre n=2.** Uma amostra de 2 disparos nao sustenta um numero de precisao
   estavel; o que ela sustenta e a **decisao**, porque o eixo do erro foi identificado por leitura
   (o card #913 discrimina por IDADE) e e estrutural, nao amostral: nenhuma curadoria de lexico
   corrige um proxy que ignora qual eixo o card usa.
3. **As 16 linhas `'Z:'` ficam no `memory_errors.log`.** Sao registro de falhas que de fato
   ocorreram; apaga-las destruiria a evidencia do F96. O numero do painel (1458) carrega 16 linhas
   de artefato de teste -- declarado no ledger para nao voltar a ser "achado".
4. **Reachability do CLI segue parcial.** `audit_flashcard_quality.py` tinha **zero** testes ate
   hoje; a suite nova cobre a revogacao e um smoke de superficie -- os **8 sinais** e os detectores
   cross-field continuam sem fixture. Nao entrou no escopo deste item; e materia do **1.7 (D5)**,
   que ja lista este CLI entre os sem assinatura canonica.

## Achado colateral verificado e DESCARTADO (registro anti-redescoberta)

`sys.stdout.reconfigure(...)` no import existe em **29 CLIs vivos**, incluindo o auditado. **Nao** e
sitio-gemeo do F94: aquele era **reatribuicao** (`sys.stdout = io.TextIOWrapper(...)`), que quebra a
captura do pytest com `I/O operation on closed file`; `reconfigure` muta o encoding do stream
existente e ~10 desses modulos ja sao importados por suites com a bateria verde. Convencao da casa,
nao defeito.

---

12 hotfix docs not yet consolidated -- `audit --consolidate-hotfixes`.
