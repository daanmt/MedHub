# Audit Report: telemetria-estudo-part-1 (degrau 3/4, persistir o planejado)

> Auditado em 2026-07-12 — Fable/ai-eng. Implementação: commit `9037266`.
> Spec: `.vibeflow/specs/telemetria-estudo-part-1.md`

**Verdict: PASS**

### Testes (gate obrigatório)

`python -m pytest -q` → **96 passed** (88 + 8), 0 failed. Inclui as suítes de paridade
do recomendador (`test_orquestrador`, `test_preparacao`) — contrato R1-R5 intocado.

### DoD Checklist

- [x] **1. Migração idempotente + schema sem texto clínico** — `plano_dia` no schema
  canônico (`init_db.py`, `CREATE TABLE IF NOT EXISTS` + índice) e lazy DDL no ponto de
  escrita (padrão real do repo: é como `preparacao_estado` nasceu em
  `registrar_sessao_bulk.py:127`). Colunas = ids/enums/contadores/flags
  (`test_schema_sem_coluna_de_texto_clinico` fixa a lista fechada via PRAGMA).
  **Desvio documentado do literal**: sem backup pré-DDL — o "padrão `cleanup_db.py`"
  citado no DoD **não existe no repo** (referência stale da spec/PRD; o precedente real
  `migrate_dificuldade.py` também não usa backup) e o DDL é puramente aditivo (zero
  linhas existentes em risco). Implementada a INTENÇÃO (idempotência + segurança) —
  regra do decisions.md 2026-07-09: "a parte tardia implementa a INTENÇÃO do DoD contra
  a realidade corrente, não o literal".
- [x] **2. Persistência idempotente por dia** — prova viva: 2 runs `--tempo 2 --energia
  baixa` → 3 blocos (simulado/questoes/fsrs) com flags gravados, um único `criado_em`;
  `test_re_run_mesmo_dia_substitui_nunca_acumula` (3 blocos → re-run com 1 → 1 linha,
  zero órfãos — delete+insert transacional por `data`).
- [x] **3. `--no-persist`** — flag presente; default persiste (wiring em `main()`).
- [x] **4. Leitura** — `ler_plano(data)` + `--plano-de YYYY-MM-DD` (prova viva acima);
  ordenada por `ordem`; data sem plano → `[]`.
- [x] **5. Craftsmanship** — pytest 96 verde; falha de db → `[WARN] PLANO_DIA` sem crash
  (teste); conexões `finally`-fechadas com guard de aquisição; convenções respeitadas.

### Decisão de implementação registrada (resolução de ambiguidade da spec)

A spec diz "persistência ao final do `build()`"; implementada em `main()` logo após
`build()`, **apenas no caminho que renderiza o plano do dia** (default/`--json`). Os
modos de relatório (`--handoff-block`, `--review-plan`, `--difficulty`) NÃO regravam —
`--handoff-block` roda no fechamento com `build()` default e sobrescreveria a intenção
declarada de manhã (`--tempo/--energia`), corrompendo a série de aderência da part-2.
Prova viva: pós `--handoff-block`, o plano persistido manteve `tempo_h=2.0/baixa`.
Mesmo objeto `p`, uma fonte, dois consumidores — a mitigação da spec preservada.

### Achado colateral (registrado)

O docstring do `day_plan.py` dizia "read-only / SEM escrever nada" — já era stale ANTES
desta spec (`registrar_condicao_dia` grava `condicao_dia` desde a orquestração part-1) —
corrigido nesta implementação. E `condicao_dia` é KV last-write-wins (não é série por
dia, apesar do comentário "série bruta"); `plano_dia` agora carrega os flags POR DIA —
candidato a consolidação futura (um dono por número; fora deste escopo).

### Pattern Compliance

- [x] `db-access-layer.md` — escrita via conexão da tool (exceção autorizada), commit
  antes de close, rollback no erro.
- [x] Padrão lazy-DDL de `preparacao_estado` — replicado exatamente.

### Critical Gate

- ✅ Verificado `DELETE FROM plano_dia WHERE data = ?` — parametrizado, escopo = 1 dia,
  parte do contrato de idempotência declarado na spec (não é mass delete; DAT101 não se
  aplica — função de substituição transacional).
- Clean — no destructive operations detected.
