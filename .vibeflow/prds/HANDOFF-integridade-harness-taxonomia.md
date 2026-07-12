# HANDOFF PRD: Integridade do Harness e da Taxonomia

> Gerado via /vibeflow:discover (M-HAND) on 2026-07-12 — Fable/ai-eng (arquiteto observador)
> **Destinatário: o agente INTERNO do MedHub.** Este é um handoff: o MedHub toca isto
> internamente, a partir da própria sessão — roda `/vibeflow:gen-spec` → `/implement` →
> `/audit` sobre este PRD. O arquiteto (ai-eng) NÃO implementa; entrega o design.

## Nota de origem (por que este PRD, e não "FSRS fiel")

O operador pediu um handoff do **FSRS fiel**. Ao fundamentar, verifiquei que o FSRS fiel
**já está implementado e é fiel** (commit `46df800` "feat(fsrs): onda A"; `app/utils/fsrs.py`
é adapter sobre `py-fsrs`; `tools/test_fsrs.py` passa incl. "stability bate com py-fsrs de
referência"). O item do ROADMAP estava stale — o mesmo padrão `Drift-as-Primary-Debt` que
motivou o ciclo de consolidação de 2026-07-12. Não fabrico um discovery para trabalho pronto.

Substituí o alvo pelo que está **verificadamente aberto e delegável** (fontes: schema do
`ipub.db` + leitura do `auto_check.py`, não o ROADMAP datado). Se o operador quiser outro
alvo (ex.: ingestão via Google Workspace MCP, ou a decisão "corrigir vs descontinuar" o
player Streamlit), redirecionar — este handoff é redirecionável.

## Problema

Dois furos de integridade, ambos pequenos e delegáveis:

1. **O harness não roda todas as suítes que existem.** `tools/auto_check.py --all` roda apenas
   `test_revisao_calibrada.py` e `test_autonomia_hooks.py`. O repo tem outras suítes
   (`test_fsrs.py`, `test_reincidencia.py`, `test_batch_insert.py`, `test_pytest_bridge.py`, …)
   que **não** são gated pelo pre-commit nem pelo `--all`. Consequência: um commit pode quebrar
   `test_fsrs` (o algoritmo que "deve estar correto") e o harness aprovar. É o furo mais
   perigoso — o gate que protege todo o trabalho futuro tem cobertura parcial. (Parte do F35
   do ledger: "seletor de suíte do auto_check".)

2. ~~**`taxonomia_cronograma` não tem `UNIQUE(area, tema)`.**~~ **ITEM CAI (corrigido
   2026-07-12, implantação do sensor de drift):** o índice `ux_taxonomia_area_tema` existe
   **desde a s083** (`tools/dedup_taxonomia.py`; também em `init_db.py` e documentado em
   `core/contracts/forgetting-curve-contract.md`). A "confirmação sem a constraint" acima
   foi erro de verificação da auditoria externa. Deste PRD resta APENAS o item 1
   (cobertura de suíte) — os critérios de sucesso 2 e a parte de migração não se aplicam.

## Público-alvo

O próprio agente/harness do MedHub (autogovernança) e, indiretamente, o operador — que confia
no `auto_check` como gate de entrega. Hoje o gate dá falsa segurança na cobertura de testes.

## Solução proposta (WHAT, não HOW — o HOW é do gen-spec interno)

- **Cobertura de suíte no harness:** o `auto_check` passa a rodar **todas** as suítes de teste
  estruturais relevantes (não uma lista fixa de 2). Decidir no gen-spec: rodar todas sempre no
  `--all`, ou um seletor que mapeia arquivo-mudado→suíte no `--changed`/`--staged`. O mínimo
  inegociável: `--all` não pode deixar `test_fsrs.py` (nem qualquer suíte viva) de fora.
- **Constraint de unicidade:** adicionar `UNIQUE(area, tema)` a `taxonomia_cronograma`, com
  dedup prévio das linhas existentes se houver duplicatas (migração idempotente + backup, no
  padrão do `cleanup_db.py`).

## Critérios de sucesso (o gen-spec transforma em DoD binário)

1. `auto_check --all` executa `test_fsrs.py` e as demais suítes vivas — verificável no relatório
   final (cada suíte aparece como linha PASSED/FAILED). Uma quebra proposital em `test_fsrs`
   passa a reprovar o `--all`.
2. A migração adiciona `UNIQUE(area, tema)`; inserir `(area, tema)` duplicado falha; contadores
   de taxonomia intactos após a migração; backup do `ipub.db` gerado antes do DDL.
3. `pytest` inteiro verde após as mudanças.
4. Nenhuma regressão no exit-code do pre-commit para mudanças sem suíte relevante (o harness não
   pode ficar mais lento/barulhento ao ponto de o operador desligá-lo).

## Anti-escopo

- **NÃO** re-implementar FSRS (feito).
- **NÃO** tocar a lógica das suítes de teste em si — só quais o harness invoca.
- **NÃO** transformar o WARN de cobertura de conhecimento (part-3 do ciclo anterior) em bloqueante.
- **NÃO** incluir a "reconcile de volume W1/F29" (a outra metade do F35): o arquiteto não tem
  contexto suficiente para especificá-la com honestidade — o agente interno (ou o operador) a
  escopa separadamente. Anti-fabricação.
- **NÃO** migrar SQLite para nuvem nem mexer no schema além da constraint.

## Contexto técnico (para o gen-spec interno)

- Harness: `tools/auto_check.py` (modos `--changed`/`--staged`/`--all`; checks 1-6). A lista fixa
  de suítes está nas seções 1-2 (linhas ~240-265). O padrão de "rodar suíte via subprocess +
  `run_command`" já existe — estender, não reinventar.
- Suítes vivas: inventariar via `glob tools/test_*.py` + `conftest.py` (pytest coleta 63 testes hoje).
  `test_pytest_bridge.py` já é uma ponte — verificar se cobre o gap antes de duplicar.
- Migração: seguir `tools/cleanup_db.py` (backup automático → validação → DDL). `db.py` é a única
  camada com `import sqlite3` (convenção). `UNIQUE` em SQLite exige recriar a tabela OU
  `CREATE UNIQUE INDEX` — a 2ª é menos invasiva e reversível; decidir no gen-spec.
- Budget: ≤6 arquivos (index.md). Provável split: (part-1) cobertura de suíte; (part-2) constraint.

## Handoff — como o MedHub toca isto

1. `/vibeflow:gen-spec .vibeflow/prds/HANDOFF-integridade-harness-taxonomia.md` (o MedHub decide
   o split em partes).
2. `/vibeflow:implement` + `/vibeflow:audit` por parte, gate de PASS entre elas.
3. Ao fechar, marcar F35 (parte "seletor de suíte") no `AUDITORIA_MEDHUB.md` e a higiene do
   `UNIQUE` no ROADMAP.

## Questões abertas

- Seletor por-mudança vs rodar-tudo-no-`--all`: decisão de custo/latência do harness — do gen-spec.
- A "reconcile de volume W1/F29" (resto do F35): fora deste handoff; precisa do contexto do operador.
