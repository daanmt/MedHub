# Audit Report: flashcards-p3 (parts 1–4)

> Auditor: ai-eng · 2026-08-14 · Base: `34d712e` → HEAD (5 commits: PRD+specs no 1º; 4 parts)
> Testes: **pytest 182 passed** (baseline pré-P3: 168) — corrida completa no ato
> Critical Gate: **Clean** — diff `34d712e...HEAD` sem achados no catálogo

**Verdict geral: PASS 4/4**

## part-1 — proveniência no revlog — **PASS**
- [x] ALTER idempotente `card_version`/`selection_reason` (padrão `_ensure_status_column`); chamado no caminho de escrita, não na fábrica
- [x] Versão capturada do BANCO no ato do record; `selection_reason` opcional retro-compatível — `test_proveniencia_card_version_e_reason` (v1 vista→revlog 1; reforja→v2; sem reason→NULL)
- [x] `fsrs_queue --record --reason` com choices; zero backfill; lock otimista/upsert intactos (suíte part-2 anterior passa sem edição)

## part-2 — banda prioritária — **PASS**
- [x] Bucket `erros_frescos` (state=0 + questao_id NOT NULL + janela 48h + cap 8, mais fresco primeiro); sem duplicata com `novos` — `test_buckets_e_reasons`, `test_sem_duplicata_entre_buckets`, `test_cap_da_banda`
- [x] Ordem servida `atrasados → erros_frescos → hoje → novos` com `selection_reason` — `test_ordem_servida_na_fila`
- [x] Card-base fresco NÃO fura a fila (não é anti-reincidência) — testado
- [x] `get_cards_by_bucket` migrado p/ `ativo_where('f.')` — `test_aposentado_fora_de_todos_os_buckets`
- **Desvio de spec DECLARADO**: o anti-scope dizia "NÃO mexer em day_plan.py" — o terreno refutou (day_plan CONSOME `get_cards_by_bucket` em 2 pontos e a paridade F3 com `--list` é invariante do repo). Edição mínima: `erros_frescos` conta como `novos` no cluster (total certo, sem chave nova de display); suíte `test_plano_dia`/`test_orquestrador` verde.

## part-3 — preview + contrato de apresentação — **PASS**
- [x] `db.preview_ratings`: read-only comprovado (snapshot antes/depois idêntico), shape completo, monotonicidade Again≤Hard≤Good≤Easy — `test_preview_read_only_e_shape`
- [x] Paridade com `evaluate` TESTADA (scheduler determinístico; preview quebra JUNTO se o scheduler mudar) — `test_paridade_com_scheduler`; flag `balanceado_apos_record` explícito (≥4d)
- [x] `--next` embute preview (falha nunca derruba a fila); `--preview CARD_ID` sob demanda; `--list` sem preview (4×N sem uso)
- [x] `revisar.md` §"Contrato de apresentação": anti-vazamento de tema pré-revelação (modo #8 deixa de ser tribal), preview junto das opções, exibir motivo, gravar com `--reason`

## part-4 — eventos + eficácia + fim do bypass — **PASS**
- [x] `event_log.py` JSONL append-only; nunca levanta (`test_falha_de_log_nunca_levanta`); decisão anti-ledger documentada (opened/resolved auto-resolveria eventos)
- [x] Eventos com **flush pós-commit** — rollback = zero eventos falsos (`test_insert_gera_evento_pos_commit_e_falha_gera_zero`); evento nunca carrega texto clínico (assert explícito)
- [x] `update_flashcard_fields` gateado — bypass documentado da regen queue fechado (`test_update_flashcard_fields_gate_fecha_bypass`); degradação anunciada sem `tools/`; caminho válido intacto (v++ preservado)
- [x] `learning_efficacy.compute` testado com fixture de proveniência; pre-P3 agrupado honesto; smoke no banco real: 1466 reviews pre-P3, **1º sinal: tipo `mecanismo` Again 27.7% vs 16-19% dos demais**; gate anti-decorativo no docstring (3 ciclos sem alterar decisão → remover)

## Pattern/Convention Compliance
- [x] db-access-layer (params `?`, close explícito, fábrica única) · warn-first (tudo novo em auditoria/telemetria é WARN; erro só no gate de escrita) · agent-workflow-protocol (revisar.md como contrato) · pt-BR · `ipub.db` fora de todo teste

## Notas / limites honestos
1. Proveniência começa AGORA — histórico (1466 reviews) fica `pre-P3` para sempre (sem backfill; decisão de honestidade, não limitação técnica).
2. `card_version` capturada no ato do record: reforja no meio de uma revisão aberta registraria a versão nova (janela de segundos, single-user — aceito e documentado).
3. Preview mostra intervalo pré-balanceador (±5% possível no record, flag avisa).
4. A taxa de reincidência é proxy por eventos pós-P3 — só ganha significado com semanas de uso.
5. **Sequência combinada com o operador**: agora → boot medhub (decisão nq=1 + curadoria mensurável + 1ª sessão com a mecânica nova) → handoff de feedback ancorado em uso → ajustes; P4 segue data-gated.

**Ready to ship.**
