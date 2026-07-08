# Audit Report: cronograma-sync-conclusao-drive

> Spec: `.vibeflow/specs/cronograma-sync-conclusao-drive.md` | Auditado em 2026-07-08

**Verdict: PASS**

### DoD Checklist

- [x] **1. `--sync-drive` parseia xlsx + matching `(semana,tema,tipo_norm)` + grava em `preparacao_estado`.**
  Evidência: `tools/cronograma.py:430-524` (`_norm_tema_xlsx`, `_parse_conclusao_xlsx`, `diff_drive`, `sync_drive`) + subcomando `--sync-drive` (linha 536, handler no `main()`). Rodado contra o xlsx real desta sessão: `[OK] snapshot gravado em preparacao_estado: 352 tasks · 119 concluídas · 30 sem match`. Confirmado via `db.get_preparacao('cronograma_conclusao_drive')`: MFC (S11/S12 Teoria), Imunizações (S11/S12 Teoria), Apendicite Aguda (S12 Teoria+Revisão), DITC I (S5/S8 Teoria) = `concluido:true`; DITC II (S11 Teoria), Distúrbios do Potássio (S12), Cefaleias;Epilepsias (S12), HAS Pt.2 (S12) = `concluido:false`. Bate 1:1 com a apuração manual ad-hoc desta sessão que originou o achado F33.
- [x] **2. `day_plan.py` filtra "próximos temas" por conclusão fresca.**
  Evidência: `tools/day_plan.py:128-192` (`_conclusao_drive` + filtro em `_cronograma_hoje`). `python tools/day_plan.py` pós-sync real não lista MFC-Teoria/Imunizações-Teoria/Apendicite/DITC-I entre os temas — lista apenas as tasks genuinamente pendentes (MFC-Revisão, Distúrbios do Potássio, Cefaleias;Epilepsias). Teste `test_cronograma_hoje_filtra_por_conclusao_fresca` (tools/test_orquestrador.py) cobre o caso isolado com fixture determinística.
- [x] **3. Fallback + `conclusao_desatualizada` quando ausente/velho, nunca falha silenciosa.**
  Evidência: `_conclusao_drive()` retorna `fresco=False` quando `atualizado_em` não é do dia corrente; `_cronograma_hoje` propaga `conclusao_desatualizada=True` e volta a listar a semana inteira sem filtro. `render()` (day_plan.py:670-673) imprime `⚠️ conclusão real desatualizada (sync: ...)`. Testes `test_conclusao_drive_ausente`, `test_conclusao_drive_desatualizada_cai_no_fallback`, `test_conclusao_drive_fresca` e a segunda metade de `test_cronograma_hoje_filtra_por_conclusao_fresca` cobrem os 3 estados (ausente/velho/fresco).
- [x] **4. W8 em `reconcile-contract.md`.**
  Evidência: linha na tabela (reconcile-contract.md:40) + resolução no PASSO 3 (linhas 67-70), mesmo formato WARNING-nunca-BLOCKING de W5-W7.
- [x] **5. Cláusula 5 de `cronograma-contract.md` corrigida.**
  Evidência: linhas 50-52 documentam as duas chaves de `preparacao_estado` (`semana_conteudo`, `cronograma_conclusao_drive`), depreciam explicitamente o ponteiro de texto antigo, e a seção "Fora de escopo" + Changelog v1.1 registram o fechamento parcial de R8.
- [x] **6. `AGENTE.md §2 passo 4` com instrução mecânica de sync.**
  Evidência: linha 49 — instrução completa (gatilho `⚠️ conclusão real desatualizada` → MCP Drive → `--sync-drive` → antes do plano do dia; 1×/dia-calendário; fallback não-bloqueante se MCP falhar).

### Pattern Compliance

- [x] **CLI conventions (`.vibeflow/conventions.md §CLI tools`, mirror local de `cronograma.py`)** — `--sync-drive` segue o mesmo estilo de subcomando dos existentes (`--rebuild`/`--check`/`--gap`): `argparse` com `metavar`/`dest`, print humano com prefixo `[OK]`/`[ERRO]` (consistente com `preparacao.py`/`day_plan.py`), `sys.exit(1)` em erro de parsing. Evidência: `tools/cronograma.py:536-552`.
- [x] **`agent-workflow-protocol.md` (boot sequence única)** — o passo de sync entra dentro do §2 passo 4 já normatizado, não cria uma sequência paralela. Evidência: `AGENTE.md:49`.
- [x] **`cronograma-contract.md` Cláusula 3/4 (read-on-demand, derivador único)** — nenhum cron/daemon introduzido; `cronograma.py` continua sendo o único ponto de parse (agora também do xlsx, além do PDF). `day_plan.py` só lê o snapshot já gravado, nunca chama MCP.
- [x] **Reuso do SSOT `preparacao_estado` em vez de arquivo novo** (desvio deliberado do PRD, documentado na spec) — confirmado: nenhum arquivo `core/cronograma/conclusao_drive.json` foi criado; único write é `db.set_preparacao(...)` (`tools/cronograma.py:520`).

### Convention Violations

Nenhuma encontrada.

### Critical Gate

Diff completo (`git diff HEAD` nos 6 arquivos) escaneado contra o catálogo de regras — nenhum arquivo do diff é `.sql`/`.tf`/`.hcl`/`.yml`/Dockerfile (fora do escopo da maioria dos domínios). Varredura textual por padrões destrutivos/segurança (DROP/DELETE/TRUNCATE, secrets hardcoded, `eval`/`exec`/`subprocess`, TLS/verify off, debug flags) nas linhas adicionadas de `tools/cronograma.py` e `tools/day_plan.py`: zero ocorrências. A única menção a tabelas sensíveis (`taxonomia_cronograma`/`sessoes_bulk`/`fsrs_cards`/`fsrs_revlog`) no diff é um comentário reforçando que elas NÃO são tocadas — confirma a fronteira dura da Cláusula 5, não a viola.

Clean — no destructive operations detected.

### Tests

`python tools/test_orquestrador.py` → **19/19 PASS** (11 pré-existentes + 8 novos desta feature).
`python -X utf8 tools/auto_check.py --changed` → **TODOS OS CHECKS PASSARAM** (harness autônomo obrigatório, `AGENTE.md §1.3`). 1 WARN pré-existente e não relacionado (`PARITY_DRIFT: analisar-questao`, arquivo já modificado antes do início desta feature) — não bloqueia.

### Budget

6/6 arquivos (orçamento sugerido em `.vibeflow/index.md`: ≤6). Nenhum arquivo fora do Scope da spec foi tocado.

### Follow-up (fora deste audit, não bloqueia PASS)

- Fechar **F33** em `AUDITORIA_MEDHUB.md` como RESOLVIDO, nos moldes de F29 — explicitamente adiado pela spec (Anti-scope) para depois do audit.
- `PARITY_DRIFT: analisar-questao` (WARN pré-existente, não relacionado a esta feature) segue pendente — considerar `python tools/sync_skills.py` numa sessão futura.
