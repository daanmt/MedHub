# Audit Report: Orquestracao da Preparacao -- Part 4 (errors-file + status anulada)

> Auditado em 2026-07-06. Spec: `.vibeflow/specs/orquestracao-preparacao-part-4.md`.
> Dependencia part-3: audit PASS confirmado. Testes rodados de forma independente.

**Verdict: PASS**

### DoD Checklist

- [x] 1. `--errors-file` insere N erros numa transacao unica; resumo; schema validado antes -- `insert_batch` (validacao PRE-transacao por item/campo); `test_lote_valido_transacao_unica`.
- [x] 2. Item invalido -> rollback TOTAL + msg apontando item/campo + exit != 0 -- `test_item_invalido_nada_inserido` (pre-validacao) e `test_excecao_no_meio_rollback_total` (ValueError DENTRO da transacao: itens 1-2 nao persistem); exit 1 no main via sys.exit.
- [x] 3. Re-execucao do mesmo lote nao duplica -- dedupe por conteudo (area+tema+TRIM(enunciado)); `test_dedupe_reexecucao_nao_duplica` ([SKIP] avisado, contagens inalteradas).
- [x] 4. `status anulada|banca-divergente`: persiste em `questoes_erros.status` (ALTER ADD COLUMN idempotente via PRAGMA-check), NAO cunha card/FSRS, [GATE-EVIDENCIA] emitido; o registro do erro permanece -- `test_status_anulada_sem_card_com_gate` + `test_single_com_status_anulada`. Contadores da taxa: o insert nunca incrementou realizadas/acertadas (nota arquitetural do proprio arquivo -- volume via bulk), logo a taxa real fica limpa por construcao; a fila fica limpa pela ausencia de card.
- [x] 5. Matcher F25 roda por item do lote (skip em anuladas) -- chamada dentro de insert_questao, exercitada pelo lote nos testes.
- [x] 6. Craftsmanship -- transacao com commit unico no fim e rollback no except (convencao CLI tools/); modo single sem flags novas byte-compativel (required condicional com MESMA mensagem/exit do argparse; validado por regressao test_reincidencia + smoke); ASCII; pytest 36 passed; standalone verde.

### Pattern Compliance

- [x] `error-insertion-pipeline.md` -- pipeline de 4 passos preservado POR ITEM; `insert_questao(conn=...)` participa da transacao maior sem duplicar SQL (refactor minimo, zero copia).
- [x] `db-access-layer.md` -- excecao standalone do insert_questao mantida; nenhum sqlite3 novo fora dela.
- [x] Convencao CLI tools/ -- argparse, prints legiveis, return bool, finally/close.

### Critical Gate

Clean. Unica mudanca de schema do ciclo: `ALTER TABLE questoes_erros ADD COLUMN status TEXT DEFAULT NULL` -- aditiva, DEFAULT NULL, idempotente (PRAGMA-check). Desvio consciente da nota conservadora do PRD documentado na spec (secao Decisoes tecnicas): alternativa tabela-satelite rejeitada por fragmentar o SSOT do erro. `grep 'SELECT \*' sobre questoes_erros` nao encontrou consumidor posicional que a coluna nova quebre.

### Notas / achados laterais (ledger)

1. Modo single: o main NAO faz `sys.exit(1)` em falha do insert (docstring promete exit 1; o codigo retorna False e sai 0) -- bug PRE-EXISTENTE, fora do anti-scope byte-identico desta part. Candidato F27.
2. `--elo` agora tem consumidor (matcher F25), mas segue sem coluna propria -- candidato F28 (persistir ou documentar que vive nos cards).

**Ready to ship. CICLO 2 COMPLETO: 4/4 specs implementadas e auditadas PASS.**
