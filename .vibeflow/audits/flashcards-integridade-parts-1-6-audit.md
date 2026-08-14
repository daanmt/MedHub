# Audit Report: flashcards-integridade (parts 1–6)

> Auditor: ai-eng · 2026-08-14 · Base: `ad1ccde` → HEAD (6 commits do ciclo)
> Testes: **pytest 168 passed** (baseline pré-ciclo: 115) — corrida fresca no ato do audit
> Critical Gate: **Clean** — diff `ad1ccde...HEAD` sem achados no catálogo (nenhum DROP/TRUNCATE/mass-delete/secret/exec adicionado; nenhuma proteção removida)

**Verdict geral: PASS 6/6**

---

## part-1 — P0: contrato de geração, vazamentos e FK enforcement — **PASS**

- [x] DoD1 sem cards/par → falha alta, zero linhas; anulada preserva F26 — `test_sem_cards_falha_alto_zero_linhas`, `test_batch_sem_cards_nada_inserido`, `test_single_sem_cards_exit_fail`, `test_status_anulada_sem_card_com_gate`
- [x] DoD2 caminho heurístico removido — greps `qual a conduta/criterio correto`/`Qual o distrator tipico`/`frente_elo` em código: zero (só fixtures de teste); todo insert grava `'qualitative', 0` (`insert_questao.py`, INSERT literal)
- [x] DoD3 filtro nq em `get_fresh_error_cards` — `test_fresh_error_cards_filtra_aposentado`
- [x] DoD4 regen queue canônica — `test_regen_queue_definicao_canonica_de_ativo` (nq=3 fora)
- [x] DoD5 PRAGMA na fábrica + CLI; IntegrityError em órfão — `test_pragma_fk_ligado_na_fabrica`, `test_fk_imposta_em_insert_orfao`
- [x] DoD6 `check_fk_orphans.py` — rodado no real: `[OK] 0 orfaos nas 5 varreduras`, exit 0, ledger
- [x] DoD7 craftsmanship — pytest verde; conventions respeitadas (sqlite3 só em db.py/CLIs; params `?`; pt-BR)
- **Desvio de budget declarado**: 8 arquivos de código (spec previa 6) — os 2 extras são fixtures pré-existentes (`test_orquestrador.py` +1 coluna; `test_reincidencia.py` cards no helper) cujo reparo foi FORÇADO pela mudança de comportamento intencional. Sem alternativa dentro do DoD7.

## part-2 — trava técnica em record_review — **PASS**

- [x] DoD1-2 lock otimista + corrida sem log — `test_corrida_segunda_aplicacao_falha_sem_log` (2ª aplicação → `ConcurrentReviewError`, revlog=1)
- [x] DoD3 upsert do df.empty — `test_card_sem_linha_fsrs_ganha_insert`
- [x] DoD4 `last_elapsed_days` populado — `test_last_elapsed_days_populado`
- [x] DoD5 callers fail-safe — `fsrs_queue.py` (emit recorded:false + exit 1) e `review_cli.py` (risco R1 da spec: 2º caller encontrado e tratado)
- [x] DoD6 fluxo normal intacto — `test_fluxo_normal_intacto` + `test_fsrs.py` OK + suíte do balancer OK

## part-3 — biblioteca card_checks + writers principais — **PASS**

- [x] DoD1 biblioteca pura, RE_PROIBIDO fonte única, atomicidade por import — `card_checks.py`; `test_nucleo_puro_sem_banco`
- [x] DoD2 6 predicados com fixture+controle — `test_card_checks.py` (15 casos)
- [x] DoD3 gate no insert com violações todas de uma vez — código + `test_excecao_no_meio_rollback_total` (rollback total preservado)
- [x] DoD4 apply_reforja comportamento idêntico — smoke dry-run no ato do audit: `[ERRO] seta Unicode proibido em verso_resposta` + `NADA aplicado (all-or-nothing)` (mesmos formatos de mensagem)
- [x] DoD5 fixtures sintéticas replicam o incidente — texto dummy, zero conteúdo clínico no repo
- [x] DoD6 pytest verde, zero duplicação de regex

## part-4 — writers restantes + fim do no-op — **PASS**

- [x] DoD1-2 base/extra: gate pré-escrita all-or-nothing + PRAGMA — `test_base_gate_reprova_e_nada_grava`, `test_extra_gate_reprova_encoding`, casos válidos gravando
- [x] DoD3 recurate: item vazio rejeitado sem `card_version++` — `test_recurate_item_vazio_rejeitado_sem_noop`; gate parcial — `test_recurate_gate_rejeita_template`, `test_recurate_valido_aplica`
- [x] DoD4 teste por writer — `test_writer_gates.py` (7 casos)
- [x] DoD5 defaults de dry-run INALTERADOS (anti-scope respeitado)

## part-5 — definição canônica + batch + calibração — **PASS**

- [x] DoD1 VIEW + helper + equivalência — `test_view_ativos_equivale_expressao_canonica` (NULL/0/1 dentro; 2/3 fora; view==inline==helper)
- [x] DoD2 consumidores canônicos — atomicity JÁ era canônico (terreno); self_sufficiency ganhou COALESCE (equivalente: 0 NULLs no banco); quality ganhou o filtro que não tinha (mudança SEMÂNTICA INTENCIONAL: sinais passam a auditar ativos — 978, não 1277 — declarada no relatório do CLI)
- [x] DoD3 exclude-set removido — agregado agora "TOTAL COM ≥1 SINAL (todos os sinais)": 50/978 no real
- [x] DoD4 cross-field no batch + export — seção DETECTORES CROSS-FIELD ativa; achado real novo: 385 questões com distrator-perdido, 14 resposta-embutida em ativos
- [x] DoD5 suíte do atomicity — `test_audit_card_atomicity.py` (10 casos, incl. guardas de cópula/entre)
- [x] DoD6 **calibração medida: recall 68/68** (meta ≥66) — template 34 + distrator-típico 34 + embutida 34; falso-positivo aparente erro-level 14/978; persistido no ledger (`calibracao_card_checks`)
- [x] DoD7 pytest verde; calibração fora do CI; warn-first

## part-6 — watermark de dado no harness — **PASS**

- [x] DoD1 tripla persistida + gatilho por dado em qualquer modo — código + prova viva: 1ª corrida `--changed` disparou "Watermark de dado: ipub.db mudou" com zero staged relevantes
- [x] DoD2 marco sela só após os checks — `test_sem_marco_dispara_e_selar_estabiliza` + 2ª corrida real sem disparo
- [x] DoD3 sensor defensivo fail-open com WARN — `test_marco_corrompido_dispara_com_warn`, `test_banco_inacessivel_dispara_com_warn` (marco NÃO avança sem leitura real)
- [x] DoD4 4 cenários testados — `test_auto_check_watermark.py` (5 casos)
- [x] DoD5 warn-first; função própria testável; `mode=ro`

---

## Pattern Compliance

- [x] `db-access-layer` — fábrica única com PRAGMA/view; params `?` em todo SQL novo; `finally: close()`; exceções CLIs standalone documentadas
- [x] `warn-first-check` — fk_orphans, cross-field batch e watermark nasceram WARN, regra em módulo próprio, ledger instrumentado, sensor nunca silencia
- [x] `error-insertion-pipeline` — gate DENTRO do pipeline (transação única preservada, F25/F26/F31 intactos)
- [x] Conventions — pt-BR, argparse, stdout humano, `ipub.db` fora do git (nenhum teste depende do banco real)

## Critical Gate

Clean — no destructive operations detected (diff `ad1ccde...HEAD` varrido contra o catálogo; nenhuma linha adicionada/removida casa regra CRITICAL/HIGH/WARNING).

## Notas para o agente MedHub (worklists geradas pelo ciclo, não são gaps do audit)

1. **385 questões com distrator-perdido** (`audit_flashcard_quality.py`, seção cross-field) — modo de falha #6 agora visível em escala; triagem é trabalho de curadoria.
2. **14 cards ativos com resposta-embutida aparente** (ids no relatório/calibração) — triar: defeito real vs falso-positivo; se FP recorrente, ajustar limiar (`card_checks.RUN_MIN/JACCARD_MIN`) e re-rodar `calibrate_card_checks.py`.
3. **Decisão pendente (B.4 do handoff-resposta)**: semântica de `needs_qualitative=1` (contrato × banco divergem) — bloqueia só o CHECK de schema (anti-scope deste ciclo).
4. P3/P4 do plano (banda prioritária no dreno, `card_version`/`selection_reason` no revlog, preview de intervalos no `/revisar`, optimizer) — próximo ciclo, aguarda GO.

**Ready to ship.**
