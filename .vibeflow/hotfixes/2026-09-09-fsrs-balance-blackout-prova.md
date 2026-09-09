# Hotfix: fsrs-balance-blackout-prova

origin: third-party
status: verified

## Symptom

Ledger **F71** (s166, `AUDITORIA_MEDHUB.md`): o load balancer do agendamento FSRS
(`app/utils/fsrs_balance.escolher_dia`, chamado por `db._balancear_due` dentro de
`record_review`) escolhe o dia de menor carga na janela de +-5% do intervalo **sem saber que
existe prova**. Caso real registrado: os cards **#381 e #823** tinham `due` 2026-09-13 (dia do
ENAMED, pico de 22 cards) e foram movidos para **2026-09-14 (+1d)** -- o dia seguinte a prova,
o primeiro em que a revisao ja nao serve ao objetivo daquela semana.

Medicao read-only no `ipub.db` em 2026-09-09 (HEAD `ab0d057`), cards ativos com `state > 0`:

| dia | cards |
|---|---|
| 2026-09-12 | 25 |
| **2026-09-13 (ENAMED)** | **24** |
| **2026-09-14** | **19** (inclui #381 e #823, `scheduled_days` 8) |
| 2026-09-15 | 18 |

`core/provas.json` ja existe e alimenta o countdown do `day_plan`; `escolher_dia(alvo,
intervalo, carga, hoje, state)` nao recebe nenhum sinal dele.

## Checkpoint

hypothesis: `escolher_dia` trata todo dia da janela como candidato equivalente; como o dia da
prova e um pico (o FSRS agendou muita coisa ali) e o dia seguinte esta mais vazio, o criterio
"menor carga" empurra sistematicamente cards do dia da prova para DEPOIS dela. O modulo e puro
por contrato, entao o sinal tem de entrar como parametro (`dias_evitar`), derivado de
`core/provas.json` pelo caller em `db._balancear_due`.

falsification_test: com `carga = {12: 25, 13: 24, 14: 19}` e `alvo = 13`, `intervalo = 8`
(folga 1), o codigo atual devolve 14. Se devolvesse 12, a hipotese estaria errada.

blind_spots: (a) `scheduled_days` dos cards ja movidos foi ajustado para o intervalo efetivo --
o "alvo original" do FSRS nao e recuperavel do banco; a re-rodada sobre a fila existente parte
do `due` gravado. (b) O balanceador so cobre `state == 2` com intervalo >= 4: cards em
aprendizado/relearning que caem no dia da prova nao sao tocados (fronteira dura (c) do s128) --
alcance declarado, nao pretendido. (c) O parser de `provas.json` do `day_plan` vive em
`tools/`; `app/` nao pode importa-lo sem inverter a camada -- entra um leitor tolerante minimo
em `db.py` (duplicacao registrada em Deviations).

## Preservation

- **Fronteiras duras do s128 intactas:** `stability`/`difficulty` nunca tocados; |deslocamento|
  <= folga (+-5%, piso 1, teto 10); so `state == 2` e intervalo >= 4; nunca hoje/passado;
  empate preserva o alvo. `tools/test_fsrs_balance.py` (BLOCKING 2c) continua verde.
- **Sem sinal de prova, comportamento identico ao atual** (`dias_evitar=None` -> mesma
  escolha de antes). Nenhum chamador existente muda de resultado.
- **Falha no balanceamento nunca derruba a gravacao da revisao** (try/except em
  `_aplicar_review`); `provas.json` ausente/ilegivel = blackout vazio + WARN em stderr, nunca
  excecao. Stdout do `fsrs_queue --record` segue JSON puro (hotfix 2026-09-06).
- **Nenhuma data de prova no codigo** (G4): o blackout e lido de `core/provas.json`.

## Eliminated / Evidence

## Root cause

`escolher_dia` respondia "qual dia da janela tem menos carga?" sem nenhuma nocao de que um
dia da janela pode ser a prova. Como o FSRS agenda muito para o dia da prova (pico) e o dia
seguinte esta mais vazio, o proprio criterio de "menor carga" empurrava sistematicamente
cards do dia da prova para DEPOIS dela. `core/provas.json` existia, alimentava o countdown do
`day_plan`, e nao chegava ao balanceador -- Reachability-Debt variante 2 (ninguem le) no
caminho de decisao mais sensivel a data do repo.

## Fix

files_changed: `app/utils/fsrs_balance.py` · `app/utils/db.py` (os 2 de CODIGO do hotfix) ·
`tools/fsrs_load.py` (superficie de operador da re-rodada, item iii do veredito) ·
`tools/test_fsrs_blackout_provas.py` + `pytest.ini` (regressao, inscrita)

- **Regra pura** (`fsrs_balance`): `escolher_dia(..., dias_evitar=None)` + `blackout_de(datas)`
  (prova + `BLACKOUT_DIAS_APOS=1`). (a) nunca pousa em blackout; (b) nunca cruza a prova
  (`_cruza_blackout`); (c) alvo em blackout so aceita candidato antes do inicio da faixa
  (`_inicio_do_blackout`); (d) sem candidato -> `(alvo, 0)` e o caller reconhece overflow por
  `dia in dias_evitar`. Sem `dias_evitar`, identico ao s128.
- **Caller** (`db`): `PROVAS_PATH` + `blackout_provas(path)` (leitor tolerante, so
  `tipo == "prova"`, WARN em stderr) e `_balancear_due(cursor, metrics, hoje=None,
  dias_evitar=None)` injetavel; overflow vira `[FSRS_BALANCE] OVERFLOW ...` em stderr com o
  due do FSRS mantido.
- **Re-rodada sobre a fila** (`db.rebalancear_blackout(conn, hoje, dias_evitar, aplicar)` +
  `fsrs_load.py --blackout [--apply]`): dry-run declara o diff por `de -> para` com COUNT;
  `--apply` grava com COUNT-ASSERT (escritos != declarados = rollback) e guarda `AND due = ?`
  por linha. So `due`/`scheduled_days`; `stability`/`difficulty` e revlog intocados. A escrita
  vive em `db.py` (allowlist F49); `fsrs_load.py` segue sem SQL de escrita.

**Executado sobre o `ipub.db` real em 2026-09-09 (backup `ipub_backup_20260909_144033.db`
antes):** dry-run -> `34 movidos / 17 overflow` -> `--apply` -> `escritos: 34` (COUNT-ASSERT
ok) -> 2o dry-run = `0 movidos / 17 overflow` (idempotente). Diff declarado:

| de -> para | cards |
|---|---|
| 2026-09-13 -> 2026-09-12 | 23 |
| 2026-09-13 -> 2026-09-11 | 1 |
| 2026-09-14 -> 2026-09-11 | 2 |
| 2026-11-01/02 -> 2026-10-28..31 | 8 |
| **overflow em 2026-09-14** (folga +-1d, sem vaga antes da prova) | **17** (#321 #558 #788 #1187 #245 #706 #381 #823 #1479 #1159 #707 #553 #709 #419 #486 #632 #463) |

Distribuicao 10..15/09 depois: 55 · 40 · 48 · **0 (prova)** · 17 · 18.

## DoD

- [x] **Caso real nasceu vermelho:** `carga={12:25, 13:24, 14:19}`, alvo 13/09, intervalo 8 ->
      codigo antigo devolvia `(14/09, +1)` (medido); 11 de 12 testes vermelhos antes do fix,
      15/15 verdes depois (3 da re-rodada tambem nasceram vermelhos).
- [x] **Fronteiras do s128 preservadas:** `tools/test_fsrs_balance.py` (BLOCKING 2c) verde;
      `test_sem_blackout_comportamento_identico_ao_anterior` verde; suite 428 passed;
      `auto_check --changed` PASSED (0 BLOCK).
- [x] **G4:** `test_nenhuma_data_de_prova_no_codigo` le as datas do `provas.json` real e prova
      que nenhuma esta em `fsrs_balance.py` nem em `db.py`.
- [x] **§10.7 na re-rodada:** dry-run + COUNT declarado + COUNT-ASSERT + verificacao pos-op
      (idempotencia) -- executado e registrado acima.

## Regression

WHEN o dia-alvo do FSRS cai no blackout de uma prova (dia da prova ou o seguinte) e existe
candidato antes da prova dentro da folga, THEN o card vai para ANTES da prova (o de menor
carga), nunca para depois; WHEN nao existe candidato antes da prova na folga, THEN o `due`
fica no alvo (deslocamento 0) e o caller reporta OVERFLOW em stderr; WHEN o alvo esta fora do
blackout, THEN nenhum candidato cruza a prova nem cai em dia de blackout.
test: `tools/test_fsrs_blackout_provas.py` (15 testes; inscrito em `pytest.ini`)
oracle_type: specified
reproduction: real
verification: red-green

## Deviations

- **Guarda G4 reescrito durante o ciclo:** a 1a versao procurava qualquer `AAAA-MM-DD` no
  modulo puro e pegou a data do proprio hotfix na docstring. Trocado por "nenhuma data do
  `provas.json` REAL aparece no codigo" -- que e o que o G4 pede.
- **Terceiro arquivo de codigo, fora do orcamento do hotfix:** `tools/fsrs_load.py` ganhou
  `--blackout [--apply]`. Nao e parte do fix do defeito (2 arquivos), e a superficie do item
  (iii) do veredito do `/ai-eng` (re-rodada com diff declarado) -- tratado como unidade
  separada no mesmo ciclo, com seus 3 testes proprios. Declarado aqui, nao escondido.
- **Leitor de `provas.json` duplicado (deferido):** `db.blackout_provas` e
  `day_plan.carregar_provas` leem o mesmo arquivo com parsers distintos (o de `tools/` nao pode
  ser importado por `app/` sem inverter a camada). Mesma familia do G4/A5; consolidar num
  `app/utils/provas.py` e tarefa de spec, nao deste hotfix.
- **#381/#823 ficaram em overflow, nao voltaram para 12/09:** o alvo original (13/09) nao e
  recuperavel do banco (`scheduled_days` ja foi ajustado na 1a passagem); a partir do `due`
  gravado (14/09) a folga de +-1d nao alcanca nenhum dia antes da prova. Empurrar alem da
  folga violaria a fronteira de +-5%. Sao os 17 do painel; decisao de move-los a mao e do
  operador (blind_spot (a) confirmado).
- **Colateral observado, nao tocado:** `--blackout` tambem moveu 8 cards do blackout da UERJ
  (01-02/11) -- correto pela regra, mas e efeito sobre um calendario a 53 dias; registrado.
