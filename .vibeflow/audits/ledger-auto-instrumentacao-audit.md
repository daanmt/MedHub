# Audit Report: ledger-auto-instrumentacao (degrau 2/4)

> Auditado em 2026-07-12 — Fable/ai-eng. Implementação: commit `96791c5`.
> Spec: `.vibeflow/specs/ledger-auto-instrumentacao.md`

**Verdict: PASS**

### Testes (gate obrigatório)

`python -m pytest -q` → **88 passed** (79 + 9 da suíte nova), 0 failed. Suíte
`test_ledger_self.py` adicionada à whitelist do `pytest.ini` (pitfall da spec 1 aplicado).

### DoD Checklist

- [x] **1. WARN → evento estruturado** — `tools/ledger_self.py::record()`; prova viva:
  anotação falsificada → `--changed` → evento `opened` com `{ts, check, fingerprint,
  alvo, payload}` em `history/ledger_self.jsonl`; fingerprint = sha1(check+alvo)[:12],
  payload FORA do fingerprint (mesma divergência com números novos = mesmo achado).
  Checks 3-7 do `auto_check` instrumentados nos pontos onde o achado já está isolado.
- [x] **2. Dedup** — `test_mesmo_warn_re_run_nao_duplica_e_incrementa`: 3 runs com o
  mesmo WARN → 1 linha no jsonl, `occurrences=3` no estado derivado
  (`ledger_self_state.json`, reescrito por run, gitignored).
- [x] **3. Ciclo de vida** — prova viva: restaurado o doc e rodado `--all` → evento
  `resolved` apendado; jsonl mostra o par opened→resolved, nada deletado; reaparição →
  novo `opened` (flapping preservado como sinal). Nuance validada: check que NÃO rodou
  não resolve (o `--changed` pós-restore pulou o check 7 porque o doc voltou a ser
  igual ao HEAD — o achado só resolveu quando o check rodou de fato no `--all`).
- [x] **4. Superfície de leitura** — `python tools/ledger_self.py --list` ordena abertos
  por recorrência; linha JSONL corrompida → `[WARN] LEDGER_SELF` e segue (teste +
  `validar_jsonl`); estado corrompido → reinicia com WARN, jsonl íntegro (teste).
- [x] **5. AUDITORIA_MEDHUB.md intocado** — `test_so_escreve_em_history_ledger_self`:
  snapshot do filesystem prova que só `history/ledger_self*` é escrito.
- [x] **6. Craftsmanship** — pytest 88 verde; import resiliente no `auto_check` (sem o
  módulo, detecção segue); CLI argparse pt-BR; payloads = valores estruturais
  (contadores/semanas/regras/stems) — zero conteúdo clínico.

### Pattern Compliance

- [x] `error-insertion-pipeline.md` (CLI) — argparse, stdout legível, exit 0.
- [x] `agent-workflow-protocol.md` — ledger-of-self alimentará o closure (degrau 4).
- [x] Família warn-first — instrumentação não altera a semântica WARN-first de nenhum
  check (`success=True` intactos); `record` nunca lança (harness resilience).

### Convention Violations

Nenhuma.

### Critical Gate

Clean — no destructive operations detected. (`ledger_self.py` escreve apenas em
`history/ledger_self*`; nenhum sqlite; nenhum subprocess novo.)

### Nota de design registrada

Resolução é **por check que rodou**: um achado aberto só resolve quando o check de
origem re-executa limpo. Consequência prática: achados de checks condicionais (check 7
fora de `--all` sem doc-alvo mudado) podem ficar abertos mais tempo que a realidade —
o `--all` periódico é o reconciliador. Comportamento correto (nunca resolver por
ausência de evidência), documentado para o degrau 4 não interpretar "aberto há N runs"
como recorrência de execução.
