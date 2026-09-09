# Session 174 -- Sessao de ENGENHARIA: ciclo A do destilado fechado (F71 F88 F80 F85 F76), a ALTERA "UTC no db" cai diante do nucleo FSRS, e o normalizador se revela vazio

**Data:** 2026-09-09 (tarde, ~14h -> ~16h30) · **Ferramenta:** Claude Code (Fable 5.1) · **Continuidade:** `session_173.md`
**Sessao DEDICADA de engenharia** (autorizada pelo operador em 09/09; ele fora do terminal). Conducao delegada ao `/ai-eng` (`ai-eng-9f`) sob D71: implement E audit aqui, ele orquestra (GO/NO-GO/ALTERA), silencio = GO. **Zero estudo, zero cards, zero questoes.**

---

## 0. Como a sessao rodou (o protocolo, medido)

- Entrada: `docs/DESTILADO-ENG-2026-09-09.md` (A: 6 hotfixes · B: 4 specs · C: decisoes do operador) + vereditos do `/ai-eng` num envio: **A = GO com ORDEM ALTERADA** (F71 primeiro, "o que muda o que o operador estuda ate 13/09 vem antes da higiene"), 3 ALTERAs no F71, 2 no F80, 1 no F76, A6 so dry-run; **B = GO nos termos do ledger**; **C = fora**.
- Loop por item: trace `vibeflow:hotfix` (Tempo 1) -> **teste de regressao VERMELHO** -> fix -> Tempo 2 -> `auto_check --changed` -> commit. 5 traces, 5 suites novas, **39 testes nasceram vermelhos** (11 + 5 + 6 + 3 + 9 dos 39 totais; os restantes sao preservacao). Suite **413 -> 452**, `auto_check` PASSED em todos os 5 commits.
- **1 pergunta ao `/ai-eng` antes de escrever** (F80, fork real) -- resposta em ~10 min, ALTERA revertida. **2 riders** dele sobre o F71 absorvidos no F88 (nao deferidos).
- Fechamento: `vibeflow:audit --consolidate-hotfixes` sobre os **10** docs de `.vibeflow/hotfixes/` (5 de hoje + 5 anteriores): **77/77 regressoes verdes, 0 regressed, 3 promote, Critical Gate limpo** no diff do ciclo (26 arquivos, +2019/-129).

## 1. Os cinco hotfixes

| # | commit | o que era | o que ficou |
|---|---|---|---|
| **F71** | `015dac0` | balanceador FSRS empurrava cards do dia do ENAMED para o dia SEGUINTE (#381/#823) | `escolher_dia(..., dias_evitar)`: blackout = prova + 1 dia lido de `core/provas.json` (G4: teste prova zero data real no codigo); nunca pousa nem cruza; alvo em blackout vai para ANTES; sem vaga = `(alvo, 0)` + OVERFLOW declarado. Re-rodada `fsrs_load.py --blackout [--apply]` (dry-run + COUNT-ASSERT §10.7): **34 movidos** (23 de 13/09 -> 12/09; 8 do blackout da UERJ), **17 overflow** em 14/09 (alvo original irrecuperavel). **13/09 zerado; 12/09 com 48.** |
| **F88** (A5 numerado) | `91c40e2` | `cronograma --gap` dizia **10000 / 6305** e o boot **10400 / 7036** do mesmo banco (literal de argparse desde a s126 + escopo sem Simulado) | `performance.volume_vs_marco` e a UNICA conta; `gap_payload` e `build` chamam a mesma; `--meta` vira what-if. **Riders do F71:** `app/utils/provas.py` = leitor unico de `provas.json` (`day_plan` re-exporta, `db` delega); `db.overflow_blackout` + linha no boot com os 17 ids. |
| **F80** | `37e0859` | 3 carimbos (`review_time`, `data_registro`, `reviewed_at`) em UTC pelo `DEFAULT CURRENT_TIMESTAMP`; `sessoes_bulk` local -- "a sessao cruzou a meia-noite" | **Zona canonica = LOCAL.** `db.agora()/carimbo()/hoje()` nos **4** writers (o `review_log` tinha o mesmo defeito e o ledger nao listava); teste congela o instante nos 4 + leitor `realizado_do_dia` + **varredura estrutural** (writer novo no DEFAULT falha nomeando o arquivo). Historico UTC declarado (commit-fronteira; shift constante -3h, Brasil sem horario de verao desde 2019); backfill = operador. |
| **F85** | `f658e9f` | `except` do import de `card_checks` degradava para WARN "porque o app nao pode quebrar sem tools/" -- o app era a UI Streamlit, removida | fail-loud (`RuntimeError ... RECUSADA`), mesma forma do gemeo F84; comentario orfao vira lapide; `fsrs_queue` docstring sem "Streamlit". |
| **F76** | `b8929b3` | `--record --reason` aceitava proveniencia falsa (#559 vencido gravado como agendado) | `db.bucket_de` (puro) recomputa o bucket ANTES de aplicar; **`fsrs_revlog.reason_servido`** (coluna nova, lazy); divergencia = `[WARN]` em stderr (nao bloqueia) + consultavel por SQL (query do contador B1 fixada em teste); `--reason auto`; `revisar.md` §4 + espelho. |

## 2. O que a sessao ensinou (alem dos fixes)

- 🔴 **A evidencia venceu a ALTERA.** O `/ai-eng` tinha mandado "UTC no db; local so na apresentacao". Antes de escrever, li o nucleo: `fsrs.py` grava `due`/`last_review` **local por construcao**, `insert_questao` grava `fsrs_cards.due` local, e todo leitor de "dia" compara com `date.today()`. UTC canonico deixaria o banco em DUAS zonas ate migrar nucleo + balanceador + fila + leitores -- spec, nao hotfix. Perguntei (D71: "duvida nova de escopo = perguntar antes de escrever"); ele reverteu em 10 min: *"Cai a minha, fica a de voces."* O protocolo funcionou nos dois sentidos.
- **O orcamento de 2 arquivos do `vibeflow:hotfix` foi estourado em 3 dos 5** (F71 = 3, F88 = 5, F80 = 3), sempre declarado no trace e com GO explicito ("fatiar so adicionaria cerimonia"). O limite e do skill; o contrato que governa e o §10.6.
- **F80 tinha 4 writers, nao 3.** A varredura estrutural achou `review_log.reviewed_at` no mesmo defeito. Ler o mecanismo atual > ler o ledger (D67).
- **O guarda G4 ingenuo pegou a data do proprio hotfix.** A 1a versao procurava qualquer `AAAA-MM-DD`; a certa procura as datas do `provas.json` REAL no codigo. Um teste que passa por acidente e tao ruim quanto um que falha por acidente.
- **A6 -- o instrumento le o nada.** `normalize_taxonomia.py` simula 286 -> 286: a RODADA 2 ja foi aplicada e nao ha regra para F65/F67. Medido read-only: **F67 = 10 grupos / 22 linhas / 193 cards + 104 erros; F65 = 35 cards presos em `[bulk]` (eram 72) + 201 erros em balde** (nao medido antes). E as areas fantasma `GO`/`Clinica Medica`, dissolvidas na s097, **voltaram** com 7 linhas novas porque nenhum writer valida `area` -> **F89**. Arquivo do operador: `docs/DRYRUN-F65-F67-2026-09-09.md`.
- **Permissao do harness:** o classificador do modo automatico bloqueou o comando composto `backup + --apply` sobre o `ipub.db`; separado em dois (backup primeiro), passou. Nenhum contorno; o dry-run e o COUNT-ASSERT ja estavam declarados.

## 3. Estado que muda para a proxima sessao

- **Fila FSRS:** 13/09 (prova) com 0 cards; 12/09 com 48; 17 presos em 14/09 (decisao do operador).
- **Todo `--record` a partir de agora** grava `reason_servido` e avisa divergencia; **todo carimbo** e local.
- **Boot** mostra o overflow do blackout e o mesmo par de volume que o `--gap`.
- **Decisoes empilhadas do operador** (HANDOFF item 5): RODADA 3 do normalizador (fusoes + 35 cards + 201 erros), 17 cards do overflow, backfill UTC->local, + as de sempre.
- **Bloco B** (F81, fila de reforja, F77, F35) = proxima sessao dedicada; `reason_servido` entra no F81 como campo lido.

## 4. Commits (6) e arquivos

`015dac0` F71 · `91c40e2` F88 · `37e0859` F80 · `f658e9f` F85 · `b8929b3` F76 · selo desta sessao (HANDOFF, session_174, INDEX, MEMORIA-AUDITORIA §1-3, ledger §6q + F89, consolidacao, dry-run A6, `exchange-log`; **destilado consumido**).
Novos: `app/utils/provas.py` · `tools/test_{fsrs_blackout_provas,volume_fonte_unica,fuso_unico,card_gate_fail_loud,reason_divergente}.py` · 5 traces em `.vibeflow/hotfixes/2026-09-09-*.md` · `.vibeflow/audits/2026-09-09-hotfix-consolidation.md` · `docs/DRYRUN-F65-F67-2026-09-09.md`.

## 5. Encerramento formal (pedido do operador, ~16h50)

Pergunta dele: *"tudo de engenharia ja foi resolvido? E todos os ledgers anteriores?"* -- medido no ledger: **91 ids, 47 resolvidos, 11 abertos, 7 abertos so em ESTADO/HANDOFF (F63-F69), 7 parciais, 2 anti-scope, 8 SEM STATUS ESCRITO nunca (F16-F20 F27 F28 F32)**. Resposta: nao -- metade.
Ordem dele: *"deixe tudo organizado no ai-eng; ele deve ter contexto de todos os tech debts, pois iremos resolve-los progressivamente. Apos, encerre formalmente a sessao; na proxima ja venho com questoes."*
Feito: **`docs/MEMORIA-AUDITORIA.md §11` = inventario completo em 4 tiers** (Tier 0 ordem selada · Tier 1 engenharia pura · Tier 2 decisoes do operador · Tier 3 triagem dos 8 sem status), com classe, remedio e dependencia por item; §9 (fila do operador) recebeu lapide apontando para o Tier 2; `AGENTE.md §10.9` e o HANDOFF apontam para a §11; inventario enviado ao `ai-eng-9f` pelo canal (registrado no `exchange-log`). **Proxima janela dedicada abre com o Tier 3 (30 min) e segue o Tier 0.** Proxima sessao = ESTUDO com questoes; zero engenharia.
