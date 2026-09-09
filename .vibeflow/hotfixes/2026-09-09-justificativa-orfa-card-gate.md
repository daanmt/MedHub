# Hotfix: justificativa-orfa-card-gate

origin: third-party
status: verified

## Symptom

Ledger **F85** (s170/s171): em `app/utils/db.update_flashcard_fields`, o import lazy de
`card_checks` (gate de qualidade da reescrita) esta dentro de um `try/except Exception` que
imprime `[WARN] CARD_GATE: card_checks indisponivel (...) — reescrita sem gate.` e **segue
escrevendo**. O comentario que autoriza isso diz: *"indisponível -> WARN e segue (a camada CLI
já valida; o app não pode quebrar sem tools/ — degradação anunciada)"*. Esse "app" era a UI
Streamlit, **removida** (AGENTE.md §6: `summarize_performance()` removido junto com a UI). A
justificativa sobreviveu ao proprio motivo e continua autorizando escrita sem gate.

Medido em 2026-09-09 (HEAD `37e0859`): com `sys.modules["card_checks"] = None`,
`db.update_flashcard_fields(1, {"frente_pergunta": ...})` devolve `True`, imprime o WARN em
**stdout** e grava (`card_version` 3 -> 4). O gemeo desta funcao -- o ratchet do verso, F84 --
ja e fail-loud na mesma funcao, 20 linhas abaixo (`RuntimeError(... RECUSADA)`).

Classe 2 (claim envelhecido em docstring, sem caminho de decisao): `fsrs_queue.py:9` ("o
player Streamlit local"). `db.py:9` ("Callers acima: `app/pages/*.py`") ja foi reescrito pelo
F80 nesta sessao. `get_topic_context.py:19` e lapide em preterito: **nao tocar**.

## Checkpoint

hypothesis: Reachability-Debt variante 3 -- o `except` le uma razao que ja nao existe. Nao
ha mais "app" que precise degradar: o unico chamador real de `update_flashcard_fields` fora
dos CLIs e a regen queue instruindo o agente, que tem `tools/` no disco. Se `card_checks`
nao importa, algo esta quebrado e a escrita e o ultimo lugar onde se deve seguir. Remedio =
a mesma forma do F84: fail-loud (`RuntimeError`, escrita recusada, nada gravado) e o
comentario orfao removido.

falsification_test: se o gate ja fosse fail-loud, `sys.modules["card_checks"] = None` faria a
chamada levantar. Medido: devolve `True` e grava. Hipotese sobrevive.

blind_spots: (a) o WARN ia para **stdout** -- num CLI de saida JSON isso quebraria o
consumidor (mesma familia do hotfix `fsrs-balance-stdout`); morre junto com o fail-open.
(b) `card_checks` continua vivendo em `tools/` e sendo importado por `__file__` -- a
dependencia `app -> tools` e um smell registrado (F85 nao o resolve; mover a biblioteca e spec).

## Preservation

- Com `card_checks` disponivel, comportamento identico: mesmos predicados
  (`checar_encoding`, template, resposta embutida), mesma `ValueError` de gate reprovado.
- O ratchet do verso (F84) continua funcionando e continua so bloqueando quando a escrita toca o
  verso. `tools/test_ratchet_verso.py` (14) e `tools/test_reforja_event_log.py` verdes.
- `get_topic_context.py:19` intocado.

## Eliminated / Evidence

## Root cause

Um `except Exception` governado por uma premissa morta. A UI Streamlit (o "app" que "nao
podia quebrar sem tools/") foi removida no pivot agent-first (s074) e ninguem releu o
comentario que a citava -- ele seguiu autorizando a escrita sem gate por ~100 sessoes. O
gemeo F84, na mesma funcao, ja tinha sido corrigido para fail-loud no audit do `/ai-eng`
(06634b6); este ficou de proposito no ledger ("uma chamada, um bug") e chegou a vez.

## Fix

files_changed: `app/utils/db.py` (1 arquivo de codigo) · `tools/fsrs_queue.py` (so docstring,
Classe 2) · `tools/test_card_gate_fail_loud.py` + `pytest.ini` (regressao)

- `update_flashcard_fields`: o `except` do import de `card_checks` levanta `RuntimeError(...
  RECUSADA) from e`; o `if _cc is not None:` desaparece (o gate SEMPRE roda ou a funcao nao
  chega a escrever); o `print` em stdout morre junto. Comentario orfao substituido pela
  lapide com o motivo.
- `fsrs_queue.py` docstring: "o player Streamlit local nao e alcancavel" -> "e a UNICA
  superficie de revisao desde o pivot agent-first (s074): a UI local foi removida".
- `db.py:9` ("Callers acima: `app/pages/*.py`") ja tinha sido reescrito no F80 (mesma sessao).
- `get_topic_context.py:19` (lapide em preterito) NAO tocado, como o ledger manda.

## DoD

- [x] **Nasceu vermelho:** com `sys.modules["card_checks"] = None` a escrita passava
      (`True`, WARN em stdout, `card_version` 3 -> 4). 3 de 4 testes vermelhos; 4/4 depois.
- [x] **Fail-loud:** `RuntimeError` com "RECUSADA", `card_version` intacto, stdout vazio.
- [x] **Justificativa orfa fora da fonte** (5 fraseados) e docstring do `fsrs_queue` sem
      "Streamlit" (Classe 2).
- [x] **Preservacao:** gate vivo continua `ValueError("gate de qualidade ...")`;
      `test_ratchet_verso` (14) · `test_reforja_event_log` · `test_writer_gates` verdes;
      suite **443 passed**; `auto_check --changed` PASSED; `sync_skills --check` exit 0.

## Regression

WHEN `card_checks` nao pode ser importado (`sys.modules["card_checks"] = None`) e
`update_flashcard_fields` e chamado com qualquer campo, THEN levanta `RuntimeError` com
"RECUSADA", nada e gravado (`card_version` intacto) e nada vai para stdout; AND a fonte da
funcao nao carrega mais a justificativa orfa; AND a docstring de `fsrs_queue.py` nao cita
mais o player Streamlit.
test: `tools/test_card_gate_fail_loud.py` (4 testes; inscrito em `pytest.ini`)
oracle_type: specified
reproduction: real
verification: red-green

## Deviations

- **A dependencia `app/utils/db.py -> tools/card_checks.py` (import por `__file__`) continua.**
  Nao e este bug: mover a biblioteca de predicados para `app/` e spec (e mexe em 7 writers).
  Registrado como smell, nao corrigido.
- **Nenhuma outra ocorrencia da assinatura** ("premissa morta governando `except`") foi
  procurada alem das 4 ja triadas na s170 (1 Classe 1 = esta; 2 Classe 2 = doc; 1 lapide).
  Varredura nova e trabalho de auditoria, nao de hotfix.
