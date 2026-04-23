# Audit Report: performance

> Generated via /vibeflow:audit on 2026-04-23
> Source spec: `.vibeflow/specs/performance.md`

**Verdict: PASS**

## DoD Checklist

- [x] **1. Executável sem flags, 5 blocos markdown** — `tools/performance.py:276-279` usa `argparse` sem flags obrigatórias. `formatar_relatorio()` (tools/performance.py:252-265) encadeia exatamente 5 blocos na ordem definida (`bloco_total` → `bloco_meta_mes` → `bloco_custo` → `bloco_marcos` → `bloco_areas`). Execução confirmada no implement phase com saída estruturada em 5 blocos.

- [x] **2. Bloco 1 (Total acumulado) via SUM correta** — `tools/performance.py:65-71` `get_totais()` executa `SELECT SUM(questoes_feitas), SUM(questoes_acertadas) FROM sessoes_bulk`. `bloco_total()` (tools/performance.py:124-138) imprime `total_q`, `total_a` e `pct = 100.0 * total_a / total_q`. Guard para `total_q = 0` implementado.

- [x] **3. Bloco 2 (Meta + ritmo)** — `bloco_meta_mes()` (tools/performance.py:141-168) calcula meta de `METAS_MENSAIS[mes_atual]`, déficit, e ritmo via `dias_restantes_no_mes()` (tools/performance.py:115-117) que usa `calendar.monthrange`. Guard `déficit ≤ 0` explícito (tools/performance.py:158-159) imprime "Meta atingida" em vez de ritmo. Fallback para mês fora da série (tools/performance.py:142-148).

- [x] **4. Bloco 3 (Custo/Q)** — `bloco_custo()` (tools/performance.py:171-211) mostra ambas dimensões. `classificar_custo()` (tools/performance.py:100-104) retorna `(emoji, rotulo)` iterando `FAIXAS_CUSTO`. Parcela do mês calculada via diff `METAS_MENSAIS[mes_atual] - METAS_MENSAIS[mes_anterior]` (tools/performance.py:180-184) com fallback para primeiro mês da série. Distância da meta R$ 0,10 impressa em ambas as linhas.

- [x] **5. Bloco 4 (Marcos)** — `MARCOS = [("ENARE...", 17000), ("Final...", 23000)]` (tools/performance.py:59-62). `bloco_marcos()` (tools/performance.py:214-222) itera e imprime distância para cada alvo. Guard para meta atingida (`faltam ≤ 0`) presente.

- [x] **6. Bloco 5 (Áreas fracas + gaps)** — `bloco_areas()` (tools/performance.py:225-249). Fracas: `[(a,q,ac,p) if q>0 and p<75.0]` ordenadas por `pct` asc (pior primeiro). Gaps: `[a for a in AREAS_VALIDAS if a not in areas_com_q]`. Output do smoke test confirmou 4 fracas ordenadas corretamente (Hepato 57.1% → Otorrino 68.4%) e 3 gaps listados.

- [x] **7. Craftsmanship** — Todos os itens verificados:
  - `DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')` (tools/performance.py:25) — padrão tools/ idêntico a `registrar_sessao_bulk.py:23` e `insert_questao.py:7`.
  - `try/finally: conn.close()` (tools/performance.py:284-292).
  - Query dinâmica parametrizada: `strftime('%Y-%m', data_sessao) = ?` com `(mes_atual,)` (tools/performance.py:93-94). Zero f-strings em SQL.
  - Nenhum `import pandas` (verificado via imports explícitos, tools/performance.py:18-23).
  - Skill `.claude/commands/performance.md` tem frontmatter canônico (`description/type/layer/status`) idêntico em estrutura a `extrair-pdf.md`.

## Pattern Compliance

- [x] **db-access-layer.md** — follows correctly.
  - Standalone CLI authorized exception aplicado (padrão listado explicitamente em Where: "tools/insert_questao.py — standalone CLI with its own connection (authorized exception)"). Evidence: tools/performance.py:25, 286.
  - Connection → work → explicit close via `try/finally`. Evidence: tools/performance.py:284-292.
  - Parameterized query para input dinâmico. Evidence: tools/performance.py:93-94.
  - Pós-processamento em Python (ratio, sort, filter), não em SQL. Evidence: tools/performance.py:85, 228-230, 241-242.
  - Read-only → sem `conn.commit()` (consistente com regra "commit before close on writes" — aqui não há write).

- [x] **error-insertion-pipeline.md** — não se aplica diretamente (não há writes, não há pipeline de erros). Estrutura de CLI em `tools/` (argparse, DB_PATH, try/finally) seguida consistentemente.

- [x] **agent-workflow-protocol.md** — não se aplica. Skill é read-only; não entra em boot/closure.

## Convention Compliance

Verificado contra `.vibeflow/conventions.md`:

- [x] **Language:** todo código e docstrings em pt-BR, termos técnicos em inglês aceitos. ✓
- [x] **Tools naming:** `performance.py` em `snake_case` dentro de `tools/`. ✓
- [x] **CLI tools convention:** argparse usado (mesmo sem flags), DB_PATH com padrão de `tools/`, `try/finally: if conn: conn.close()`, print human-readable no stdout. ✓
- [x] **DB access:** `import sqlite3` apenas em exceção autorizada (`tools/`). Nenhum uso em pages ou utilitários app. ✓
- [x] **Don'ts:** Nenhum gatilho dos "Don'ts" disparado — não altera `db.py`, não toca resumos, não cria flashcards_cache, não altera `medhub-ui-refresh-main/`, não commita `ipub.db`. ✓

## Convention Violations (if any)

Nenhuma.

## Tests

**Warning:** No pytest / test runner detectado no projeto. O único arquivo de teste existente (`tools/test_memory.py`) é um smoke test standalone do módulo de memória, não um runner de projeto. Anti-scope do spec é explícito: "Não criar testes automatizados".

**Verificação manual (implement phase):** `python tools/performance.py` executou e produziu relatório válido em 5 blocos. Falha inicial `UnicodeEncodeError` (cp1252 × emojis) corrigida com `sys.stdout.reconfigure(encoding='utf-8')` em `main()` (tools/performance.py:271-274) — uma tentativa de fix, dentro do limite de 2.

## Budget

4 / ≤ 6 arquivos:
- `tools/performance.py` (novo)
- `.claude/commands/performance.md` (novo)
- `ESTADO.md` (1 linha na seção Infraestrutura)
- `CLAUDE.md` (1 linha em Skills, 1 linha em Scripts)

## Findings adicionais (informativos — não bloqueiam PASS)

Saída do smoke test expôs dois problemas de **dados**, não de código:

1. **Drift de taxonomia em `sessoes_bulk`:**
   - `"Obstetricia"` (sem acento) registrado no DB vs `"Obstetrícia"` em `AREAS_VALIDAS` → falsamente listada como gap.
   - `"GO"` criado como área paralela em sessão 071, fora de `AREAS_VALIDAS`.
   Ambos foram antecipados como risco (Risk #8 do spec: "Drift entre `AREAS_VALIDAS` dos dois scripts"). O script revela o drift fielmente; não esconde.

2. **`data_sessao` da migração histórica** (sessão 067, `migrar_sessoes_bulk.py`) foi setada para 2026-04-16 (data da migração) em vez da data original das sessões. Resultado: `bloco_custo` do mês corrente usa 3.130q como denominador, inflando artificialmente a performance do mês. Fora do escopo deste spec.

Ambos findings são material para backlog de limpeza de dados em sessão futura, não correções pós-audit.

## Overall

**PASS.** Todos os 7 DoD checks verificados com evidência. Pattern compliance total (`db-access-layer.md`). Zero violações de convenção. Budget dentro do limite (4/6). Único teste disponível (manual) passou após 1 fix no implement phase. Findings de dados são informativos e não afetam a correção do código.

**Ready to ship.**
