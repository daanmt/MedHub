---
tags: [harness, auto-check, warn, governance, invariants, drift]
modules: [tools/auto_check.py, tools/doc_drift.py, tools/ledger_self.py]
applies_to: [scripts, governance-checks]
confidence: established
---
# Pattern: Warn-First Check (invariante de governança no harness)

> Promovido em 2026-07-12 (série auto-evolução) após o 3º uso consistente:
> checks 3-6 pré-existentes · check 7 (doc_drift) · instrumentação ledger-of-self.

## What

Todo invariante de governança novo entra como **check do `auto_check.py`** (nunca
disciplina textual solta) e **nasce WARN** — visível, contável, mas sem alterar o
exit-code. Só endurece para BLOCK quando a base zera E o operador decide.

## The Pattern

1. **A regra mora num módulo próprio, testável** (`doc_drift.py`, `ledger_self.py`,
   função `check_*` pura) — o `auto_check` só orquestra.
2. **Bloco no `main()` do auto_check**, com janela de relevância (roda no `--all`
   sempre; no `--changed`/`--staged` só quando os arquivos-gatilho mudaram):

```python
# N. <Nome do invariante> (<origem/spec>). WARN, não bloqueia:
if relevante:
    achados = modulo.run_checks(...)
    for a in achados:
        print(f"\n[WARN] TAG_DO_CHECK: {a['...']} -- <mensagem acionável>.")
    # success=True: WARN não rebaixa o veredito (não altera all_passed).
    results_summary.append((desc, True, len(achados)))
    _ledger_record("tag_do_check", [...])   # memória (ledger-of-self)
```

3. **Parse/execução defensivos**: sem dados → silêncio (nunca falso-positivo
   barulhento); entrada malformada → WARN de sintaxe, nunca crash; sensor
   indisponível → WARN visível (nunca silêncio que mascare sensor quebrado).
4. **Instrumentar no ledger-of-self** (`_ledger_record`) — o achado sobrevive ao
   stdout e ganha recorrência/ciclo de vida.

## Anti-patterns

- Regra de governança implementada como prosa em doc/contrato sem check executável.
- Check novo nascendo BLOCK sem cruzar contra a base real primeiro (ver decisão
  2026-07-04: regra de linter cruza contra `--all` ANTES de escolher severidade).
- Swallow silencioso de exceção do próprio sensor (falsa segurança).
- Lógica da regra dentro do `auto_check` (deve morar no módulo/gerador).
