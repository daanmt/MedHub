# Spec: Hub integração -- part 5: regra P09 -- o lote conta no dia em que começou

> Escrita em 2026-10-05 (s216). Decisão dele (05/10): *"pelo dia em que o lote começou"*. Caso real: lote `2026-10-04a`, 70 de 150 notas depois de 00h; o Painel mostrou "212 de 100" (s215).

## Objetivo

Um lote de cards que vira a meia-noite conta inteiro no dia em que recebeu a primeira nota, no teto do dia seguinte e no "Hoje" do Painel; o FSRS continua gravando o horário real.

## Contexto

`consumo_do_dia()` (`fsrs_queue.py:180-193`) e `painel._bloco_dia` (`painel.py:164-206`) usam `day_plan.realizado_do_dia(hoje)["cards"]` = `COUNT(DISTINCT card_id) FROM fsrs_revlog WHERE date(review_time)=?` (`day_plan.py:1357-1370`). `--record-lote` grava `review_time` = `ts` real da nota (`notas_player.relogio`); `fsrs_revlog` não tem coluna de sessão. O marcador `tmp/hub/ultima_gravacao_hub.json` guarda `sessao` e `gravado_em` (`fsrs_queue.py:550-554`); as notas do lote ficam em `tmp/player_<sessao>_db` (com `ts`) e o lote em `tmp/player_<sessao>.json`. `realizado_do_dia` é usado também pelo boot e pela aderência (`day_plan.py:904-911, 1421`); mudá-lo quebra `test_contador_divida.py:114,177`, `test_fuso_unico.py:106-107`, `test_aderencia.py:147`.

**Fricção que esta spec remove:** o teto do dia seguinte "comido" por um lote de ontem e um Painel que mostra 212 de 100 -- viciosa. Protege a virtuosa: o FSRS guarda o horário real (o intervalo do card não mente).

## Definition of Done

1. **`day_plan.consumo_logico(hoje)`** nova, ao lado de `realizado_do_dia`: devolve o consumo de cards de `hoje` descontando os `card_id` do último lote gravado (`ultima_gravacao_hub.json` -> `tmp/player_<sessao>_db` ou `history/quarentena`) cuja PRIMEIRA nota (`min(ts)` -> `relogio.dia_logico`) caiu num dia anterior a `hoje`. Sem marcador ou sem notas: igual a `realizado_do_dia`. Testes novos em `tools/test_fsrs_queue_player.py`: `test_lote_que_virou_a_meia_noite_conta_no_dia_da_primeira_nota` (fixture sintética: 80 notas às 23h, 70 às 00h30; consumo de hoje = 0) e `test_sem_marcador_consumo_logico_e_o_do_relogio`.
2. **`consumo_do_dia` usa `consumo_logico`.** `test_teto_do_dia_desconta_o_que_ja_foi_revisado_hoje` passa; `test_export_para_amanha_usa_o_relogio_de_amanha` passa (o `--para` continua movendo o relógio; um lote iniciado hoje conta hoje).
3. **`painel._bloco_dia` usa `consumo_logico`**, e `_html_dia` mostra o consumo lógico sobre o teto; o cabeçalho "Hoje, <data>" continua pelo relógio (decisão desta spec, ver Technical Decisions). `test_saldo_de_cards_e_consumo_sobre_teto` e `test_saldo_nunca_negativo` passam; teste novo `test_painel_nao_conta_o_lote_de_ontem_no_saldo_de_hoje`.
4. **`realizado_do_dia` intacto** (boot e aderência seguem pelo relógio); `test_contador_divida`, `test_fuso_unico`, `test_aderencia` sem mudança.
5. **Documentado:** `fsrs-management-contract.md` ganha a cláusula "dia do lote = dia da 1ª nota (P09, 05/10/2026)" com CHECK apontando para o teste da DoD 1; `hub-backend.md` passo 5 cita que o saldo pós-gravação é o lógico.
6. **Suíte e harness.** `pytest tools/ -q` verde; `auto_check --changed` PASSED; sem Don'ts (acesso ao db só por `app/utils/db.py`).

## Scope

**Arquivos (6):** `tools/day_plan.py` · `tools/fsrs_queue.py` · `tools/painel.py` · `tools/test_fsrs_queue_player.py` · `tools/test_painel.py` · `core/contracts/fsrs-management-contract.md` (+ `hub-backend.md` 1 linha, e espelho por `sync_skills.py`).

## Anti-scope

- Reescrever `review_time` no revlog. Coluna de sessão no revlog. Flag nova no tique ou no export.
- Mudar o teto (100/150), a aderência ou o boot.
- O "Hoje ao vivo" da página (part 6) -- esta part só corrige o número PUBLICADO.

## Technical Decisions

- **Função nova, não mudança de `realizado_do_dia`:** 4 chamadores e 5 testes dependem da semântica de relógio; só o teto e o Painel pedem a lógica (decisão dele). Trade-off: dois conceitos de "hoje" no código, nomeados.
- **Fonte = marcador + notas do lote, não o revlog:** o revlog não sabe de sessão; o marcador e o `_db` já existem no rito do tique. Sem flag nova (anti-escopo do PRD).
- **Cabeçalho pelo relógio:** "Hoje, 06/10" com saldo lógico é o que ele lê de manhã; mudar a data do cabeçalho confundiria o dia das listas. Pergunta aberta do mapa respondida aqui; se ele discordar, é 1 linha.
- **Só o ÚLTIMO lote gravado:** um lote é drenado e gravado uma vez; lotes anteriores já estão fora da janela de "hoje" por construção. Se dois lotes virarem a noite no mesmo dia (nunca aconteceu), o segundo é o que conta.

## Applicable Patterns

- `db-access-layer.md`: nenhum `sqlite3` fora de `app/utils/db.py`.
- `warn-first-check.md`: cláusula nova com CHECK.

## Risks

- **`tmp/` apagado:** `consumo_logico` cai para o relógio sem erro (DoD 1).
- **Fuso:** `ts` da página é UTC com `Z`; converter por `relogio.dia_logico`, nunca por string (A17).
