# Hotfix: player-redrill-nao-persiste

origin: session
status: partial

## Symptom
01/10/2026 ~12h, lote `2026-09-30a`: o operador drenou os 150 e fez o redrill ("ja foi feito"), mas o hub ainda mostra "uma fila de 61 cards esperando la pelo redrill". 61 = 39 notas 1 + 23 notas 2 - o 714 (nota 1 + defeito, sai da fila) -- exatamente todo card com `rating_primeira < 3`. Relato dele: "suponho que o problema esteja no redrill nao estar sendo registrado no lote".

## Checkpoint
hypothesis: o resultado do redrill so existe na fila em memoria (`avaliar`: card ja em `notas` nao grava nada; `fila.shift()` sem `push` quando a nota >= 3). `montarFila()` decide "relearning" so por `rating_primeira < 3`, entao TODA remontagem (reload, e desde o hotfix 2026-10-01-player-volta-no-tempo tambem `ressincronizar()` ao voltar a aba) devolve os cards ja redrilados. O hotfix anterior ampliou o alcance: antes so o reload reapresentava.
falsification_test: no harness, dar nota 1 a um card, redrilar com nota 3 e disparar ocultar(true)/ocultar(false): se o card nao volta a fila, a hipotese cai.
blind_spots: o redrill que fica em nota < 3 de novo continua na fila (correto); nao ha registro de QUANTAS voltas o card deu (fora do escopo).

## Preservation
- Redrill continua sem segunda nota gravavel no FSRS (`rating_primeira` imutavel; so a 1a grava -- regua s204).
- Card com nota < 3 que ainda nao foi redrilado volta em relearning depois do reload (test_notas_sobrevivem_ao_reload_sem_db).
- `fsrs_queue.py --record-lote` le o lote como antes (campo novo ignorado pelo parser).

## Eliminated / Evidence

## Root cause
`core/templates/player.html`: `avaliar` so persistia a 1a nota; o redrill resolvido existia so na fila em memoria e `montarFila()` classificava relearning so por `rating_primeira < 3`.

## Fix
files_changed: core/templates/player.html
- `avaliar`: card ja anotado com nota < 3 que recebe >= 3 no redrill ganha `redrill_ok: true` no registro (aparelho + db). `rating_primeira` intocado.
- `montarFila` pula `redrill_ok`; `mesclar`/`absorver` carregam o campo (OR); `reenviarPendentes` reenvia quando so o aparelho o tem.

## DoD
- [x] redrill feito nao volta a fila ao voltar a aba nem no reload
- [x] db guarda `redrill_ok` e a 1a nota segue a gravada
- [x] suite inteira verde (1290)

## Regression
WHEN o card 100 recebe nota 1, os outros sao feitos e o redrill do 100 recebe 3, e a aba some e volta (ou a pagina recarrega so com o aparelho) THEN a fila fica em 0 e o db tem `{rating_primeira: 1, redrill_ok: true}`.
test: tools/test_player_js.py::test_redrill_feito_nao_volta_a_fila_ao_remontar
oracle_type: specified
reproduction: synthetic
verification: red-green

## Deviations
- Lote vivo 2026-09-30a: os 61 cards de nota < 3 (sem defeito) receberam `redrill_ok: true` direto no db do hub (2 batches, if_version 1), pela declaracao do operador ("ja foi feito"). So muda a fila da tela; FSRS intocado.
- Evidencia real do hotfix anterior: o 714 apareceu no db em version 2 -- o aparelho dele reenviou o defeito ao abrir a pagina corrigida.
