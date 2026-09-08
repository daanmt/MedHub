# Hotfix: reforja-sem-rastro

origin: third-party
status: verified

## Symptom

Reforja de flashcard executada **nao deixa nenhum rastro rastreavel**. Auditoria da s170
(subagente Sonnet, relatorio em `scratchpad/audit_reforja_reincidencia.md`) mediu:

- Unico chamador de `event_log.registrar` no repo: `tools/insert_questao.py:39-41` e `:296-301`,
  e apenas para card NOVO (tipos `generation` / `reincidencia`).
- `app/utils/db.py:737-812` (`update_flashcard_fields`) reescreve o card, faz
  `card_version = COALESCE(card_version,1)+1`, commita em `:809` -- **zero evento**.
- `tools/recurate_cards.py:186` (dentro de `aplicar()`) faz `UPDATE flashcards SET ...` DIRETO,
  sem passar por `update_flashcard_fields`, commita em `:188` -- **zero evento**.
- `flashcards` nao tem coluna de timestamp de update. O unico sinal de intervencao que
  sobrevive e `card_version`.

Consequencia medida no banco real: o card **#321** esta em `card_version=2` com o texto do
defeito **identico** -- a versao subiu sem que o defeito fosse corrigido, e nada no sistema
registra o que aconteceu. 23 cards da fila corrente estao em `card_version=1`
(confirmadamente nunca reforjados) e nenhum aparece em CLI algum.

## Checkpoint

hypothesis: os dois caminhos de reescrita (`db.update_flashcard_fields` e
`recurate_cards.aplicar`) commitam sem chamar `event_log.registrar`. Nao e regressao nem
falha de runtime: a chamada nunca existiu nesses caminhos -- so no de criacao.

falsification_test: se a hipotese estiver errada, um teste que reescreve um card por cada
caminho e le `history/generation_log.jsonl` encontraria linha de evento. Espera-se ZERO.

blind_spots: (a) nao verifica se `card_version` esta correto -- so a ausencia do evento;
(b) nao cobre `insert_card_base` / `insert_card_extra` (criam card, nao reescrevem);
(c) o evento nao prova que o defeito foi CORRIGIDO, so que houve reescrita -- o fechamento
explicito de marca de reforja e escopo do spec A, nao deste hotfix.

## Preservation

- `event_log.registrar` **nunca levanta excecao** (contrato em `tools/event_log.py:9`):
  falha de log jamais pode derrubar a escrita do card.
- Evento carrega **so ids/contagens/tags -- NUNCA texto clinico** (`tools/event_log.py:10`).
  Nenhum campo de frente/verso pode entrar no evento.
- `aplicar()` continua all-or-nothing: excecao no meio faz rollback do lote inteiro
  (`recurate_cards.py:191-193`) e, apos o fix, **nao emite evento nenhum**.

## Root cause

A chamada a `event_log.registrar` **nunca existiu** nos caminhos de REESCRITA -- so no de
CRIACAO (`insert_questao.py`). Nao e regressao: o pipeline de eventos (P3 part-4) nasceu
cobrindo `generation`/`reincidencia` e a reforja ficou de fora do desenho. Como `flashcards`
tambem nao tem timestamp de update, a reescrita virou a unica operacao do pipeline que muda
o SSOT sem deixar registro -- e `card_version` sozinho nao distingue "reescrito e corrigido"
de "reescrito e ainda defeituoso" (caso #321).

## Fix

files_changed: app/utils/db.py, tools/recurate_cards.py

Novo tipo de evento `reforja`, emitido **so apos commit bem-sucedido**, carregando
`card_id`, `writer`, `version_antes`, `version_depois`, `reason`, `campos` (nomes de coluna)
e `n_campos`. Zero texto clinico.

- `app/utils/db.py` -- `update_flashcard_fields` passa a ler `card_version` no SELECT de
  existencia (antes lia `SELECT 1`, descartando o dado de que precisava) e chama o helper novo
  `_log_reforja()` depois do `conn.commit()`/`close()`. O `except` largo garante que log
  quebrado nunca derruba a escrita.
- `tools/recurate_cards.py` -- `aplicar()` acumula os eventos numa lista `pendentes` dentro da
  transacao e so os emite em `_flush_eventos()` **depois** do `conn.commit()`. Emitir dentro do
  laco produziria evento-fantasma no rollback: o lote e all-or-nothing e o log tem que contar a
  mesma historia que o banco. Cobre tambem o ramo `aposentar` (`reason='aposentar'`, versao
  inalterada).

## DoD

- [x] Reescrita bem-sucedida por `db.update_flashcard_fields` emite exatamente 1 evento pos-commit.
- [x] Reescrita bem-sucedida por `recurate_cards.aplicar` emite exatamente 1 evento por card refeito, pos-commit.
- [x] Caminho que nao commita (card inexistente; gate reprovado; rollback do lote) emite ZERO eventos.
- [x] `auto_check --changed` PASSED e a suite inscrita em `pytest.ini` (F43).

## Regression

WHEN um flashcard existente e reescrito por qualquer um dos dois caminhos de escrita
THEN exatamente 1 linha de evento e appendada apos o commit, carregando `card_id`, `writer`,
`card_version` antes/depois e `reason` -- e, quando a escrita NAO commita (card inexistente ou
excecao com rollback), NENHUMA linha e appendada.

test: tools/test_reforja_event_log.py
oracle_type: specified
reproduction: real
verification: red-green

## Deviations

- Escopo do `writer`: o brief pedia "qual tool escreveu". Gravado como identificador estavel
  (`db.update_flashcard_fields` / `recurate_cards`) e nao como caminho de arquivo -- caminho
  quebra no primeiro rename e o evento e append-only (nao da para corrigir depois).
- Adicionados 2 testes alem dos 2 lados exigidos: `test_gate_reprovado_nao_emite_evento`
  (o gate de qualidade levanta ANTES de abrir conexao -- 2o caminho de nao-commit, distinto do
  card inexistente) e `test_falha_no_log_nao_derruba_a_escrita` (trava a propriedade de
  Preservation, que nenhum dos 4 originais cobria).
- Campo `campos` no payload: nomes de coluna sao tags, nao conteudo. Entram porque a telemetria
  pedida pelo /ai-eng no spec seguinte (crescimento do verso entre versoes) precisa saber SE o
  verso foi tocado numa reescrita, e sem isso o evento nao sustenta essa medicao.
- DEFERIDO (achado colateral, nao corrigido aqui -- uma chamada, um bug): `recurate_cards.py`
  trata os predicados de atomicidade (`checar_front`/`checar_verso`, onde vive `LIMITE_CHARS`)
  como **AVISO** e nao como ERRO (`recurate_cards.py:160-166`). E o gate que deixaria a reforja
  engordar o verso passar. Vai para o spec da guarda de nao-crescimento (2/3-B).
