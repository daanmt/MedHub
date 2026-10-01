# Hotfix: player-volta-no-tempo

origin: session
status: partial

## Symptom
01/10/2026, lote `2026-09-30a` (150 cards) no hub (https://claude.ai/artifact/3RksMfkzNWYSQD7D6JXNEr). Relato do operador: "enquanto fazia os cards, caso eu saisse do artifact e voltasse, para checar outro projeto, os cards 'voltavam no tempo'". Ele terminou os 150 e colou o JSON de notas da tela de fim. Cruzamento com `sessoes/2026-09-30a/notas` no db: 150/150 presentes, 149 identicos; o card 714 tem no aparelho `{rating_primeira:1, defeito:true, motivo:"Siglas que nao conheco e contexto limitado"}` e no db so `{rating_primeira:1}` (doc version 1 -- a escrita do defeito nunca chegou). Timestamps do db monotonicos na ordem do lote: as notas reapresentadas nao foram regravadas (`avaliar` pula card ja em `notas`).

## Checkpoint
hypothesis: (a) `iniciar()` monta a fila so com o localStorage ANTES de `colecao.get()` resolver; se o operador da a 1a nota antes disso, `interagiu`=true e o `montarFila()` pos-db e pulado -- a fila fica a velha e reapresenta cards ja feitos. (b) `restaurar(docs)` SOBRESCREVE o registro local pelo do db (`absorver` = `notas.set`), entao um defeito que so o aparelho tem e apagado (e o espelho local e regravado sem ele); `reenviarPendentes` so reenvia card AUSENTE no db, nunca o que o db tem a menos. (c) Nada ressincroniza ao voltar a aba visivel.
falsification_test: com db ADIADO no harness (resolve so depois do 1o gesto) e o db ja contendo as notas, o card na tela depois do 1o gesto ainda e um card resolvido; com db contendo 714 sem defeito e o aparelho com defeito, o espelho final perde o defeito e o db nao recebe a escrita.
blind_spots: por que o `set()` do defeito do 714 nao chegou ao db (falha silenciosa do runtime? escrita em voo ao sair do artifact?) nao foi observado; o localStorage do iframe do artifact pode ter vindo vazio na volta (particionamento), o que agrava (a) -- nao medido no aparelho.

## Preservation
- O reload sem db (so localStorage) continua retomando de onde parou (test_notas_sobrevivem_ao_reload_sem_db).
- So o que o db nao tem e reenviado; nota ja gravada igual nao e reescrita (test_notas_locais_sao_reenviadas_quando_o_db_abre).
- O card virado na tela nao e trocado no meio da resposta.

## Eliminated / Evidence

## Root cause
`core/templates/player.html`: (a) no boot, o remontar da fila depois de `colecao.get()` estava condicionado a `!interagiu` -- nota dada antes de o db responder congelava a fila montada so com o aparelho; (b) `absorver` fazia `notas.set` com o registro que chegava (db sobrescrevia o aparelho) e `reenviarPendentes` so via card ausente; (c) `visibilitychange` so cuidava do relogio.

## Fix
files_changed: core/templates/player.html
- `mesclar(a, b)`: 1a nota (ts mais antigo) fica; defeito de qualquer lado vale. `absorver` mescla em vez de sobrescrever.
- `reenviarPendentes` reenvia tambem o card que o db tem A MENOS (defeito ou nota so no aparelho).
- `remontar()`: refaz a fila a cada estado novo; o card na tela fica na frente se ainda pendente (sem embaralhar), e so e trocado se ja resolvido. Substitui o `if(!interagiu)`.
- `sincronizarComDb()` (boot) e `ressincronizar()` ao voltar a aba visivel e no `pageshow` persistido; `pagehide` tambem espelha as notas.

## DoD
- [x] db que chega depois da 1a nota poda a fila (P2 na tela, nao P1)
- [x] defeito que so o aparelho tem sobrevive ao restaurar e e reenviado ao db
- [x] voltar a aba relê o db e tira da fila o que outra abertura gravou
- [x] suite inteira verde (1289)

## Regression
WHEN o player recarrega sem espelho local, o operador da nota ao 1o card e SO DEPOIS o db responde com os cards 100 e 101 ja feitos THEN a tela mostra o 3o card (P2) e a 1a nota gravada no db nao e sobrescrita; WHEN o aparelho tem {101: nota 1 + defeito} e o db {101: nota 1} THEN o espelho mantem o defeito e o db o recebe; WHEN a aba volta visivel e o db ganhou o 101 noutra abertura THEN a fila pula para P2.
test: tools/test_player_js.py::test_db_que_chega_depois_da_1a_nota_poda_a_fila_e_nao_volta_no_tempo, ::test_defeito_que_so_o_aparelho_tem_sobrevive_ao_db_e_e_reenviado, ::test_voltar_a_aba_ressincroniza_com_o_db
oracle_type: specified
reproduction: synthetic
verification: red-green

## Deviations
- reproduction e synthetic: harness node com db falso (novo modo `dbAdiado`), nao o runtime do artifact. Status fica `partial` por isso; a prova real e o proximo lote drenado com idas e vindas.
- Blind spot que segue aberto: POR QUE o `set()` do defeito do 714 nao chegou ao db nao foi observado. O fix garante o reenvio na proxima abertura/volta de aba; nao explica a perda original.
- 714: marca de reforja gravada a mao a partir da copia JSON do operador (`fsrs_queue.py --record-lote ... --apply --expect 0`, marcas_reforja=1).
