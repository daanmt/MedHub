---
title: "Audit -- Part 2: Integridade de rotulo (F30 material_indicado + F31 lastro no insert)"
type: audit
spec: .vibeflow/specs/boot-cronograma-drive-confiavel-part-2.md
date: "2026-07-09"
verdict: PASS
---

# Audit Report: boot-cronograma-drive-confiavel-part-2

**Verdict: PASS**

### DoD Checklist
- [x] **DoD 1 (F30 render)** -- `temas_material` em `_cronograma_hoje` passa cada task por `_material_efetivo(t['tema'], t.get('material_indicado','resumo'))`; task com rotulo `resumo` sem `.md` e exibida como `extensivo`. Evidencia: `tools/day_plan.py` (`temas_material`) + `_material_efetivo` (rebaixa quando `_find_resumo` None). Teste `test_07_material_efetivo_rebaixa_sem_md`.
- [x] **DoD 2 (F30 difficulty)** -- `difficulty_report`: `mat = _material_efetivo(tema, _material_do_tema(tema))`. Evidencia ao vivo: `day_plan --difficulty Infecto Leishmaniose` -> `"material_indicado": "extensivo"` + passo `[Material: extensivo]` (era `resumo`, tema-zero sem `.md`). Compoe corretamente com G5 (nota-8 explicita do usuario vence o floor D10; o rotulo de material reflete a realidade). Teste `test_07`.
- [x] **DoD 3 (F31 insert)** -- `insert_questao.py` emite `[SEM-LASTRO] area/tema` quando `_tem_lastro(tema)` False (`_find_resumo` None E sem PDF-fonte par); dentro de `try/except`, apos o insert, ANTES de `return True` -> nao bloqueia, exit inalterado. Evidencia: bloco F31 em `insert_questao` + helper `_tem_lastro`. Teste `test_08_tem_lastro_detecta_ausencia` (True p/ tema com `.md`, False p/ bogus).
- [x] **DoD 4 (quality gate)** -- `pytest` 62 passed / 0 failed; `auto_check --changed` PASSED; verificacao read-only (reusa `_find_resumo`, nenhum write novo); nenhum `import sqlite3` novo (o de `insert_questao` e pre-existente, excecao CLI standalone); texto novo ASCII-limpo.

### Pattern Compliance
- [x] **db-access-layer.md** -- as duas checagens sao read-only: `_material_efetivo` consome `app.engine.get_topic_context._find_resumo` (sem SQL); `_tem_lastro` faz glob no filesystem (`resumos/**/*.pdf`) + `_find_resumo`, zero acesso a db. Nenhum `import sqlite3` novo introduzido. `insert_questao.py` segue como CLI standalone (excecao autorizada).
- [x] **error-insertion-pipeline.md** -- o WARN F31 entra no MESMO ponto e padrao do F25 (pos-insert, dentro do `try`, `except: pass`, antes de `return True`), sem alterar a transacao atomica de 4 passos nem o contrato de saida (bool/exit). Anti-pattern "inserir fora do insert_questao" nao aplicavel; a checagem nao escreve nada.

### Convention Violations
- Nenhuma. Imports lazy (`importlib`, `glob`, `unicodedata`) dentro dos helpers seguem o estilo ja praticado no arquivo (`day_plan.py` ja usa `importlib.import_module` dentro de funcoes; mantem o topo enxuto). Naming snake_case pt-BR/EN conforme `conventions.md`.

### Critical Gate
- ✅ Clean -- scan das linhas adicionadas de `day_plan.py`/`insert_questao.py`/`test_autonomia_hooks.py` (DROP/DELETE/TRUNCATE/delete_all/purge/eval/exec/subprocess/import sqlite3/secret/token/force_destroy/0.0.0.0/verify=false) retornou zero match. As checagens sao read-only; nenhuma operacao destrutiva ou regressao de seguranca. O `ALTER TABLE ... ADD COLUMN` em `insert_questao.py` e pre-existente (`_ensure_status_column`, F26) e nao esta no diff desta parte.

### Notas (nao bloqueiam)
- **Budget: 3/6 arquivos** (`day_plan.py`, `insert_questao.py`, `test_autonomia_hooks.py`). Anti-scope intacto: nao cria/edita resumos, nao bloqueia o insert, nao toca FSRS/schema/algoritmo de `_find_resumo`, nao mexe em ordenacao/disparo (part-1) nem higiene (part-3).
- **Design:** o rebaixamento vive em `_material_efetivo` aplicado nos DOIS call-sites (render + difficulty); `_material_do_tema` continua retornando o rotulo cru da grade (determinismo/early-return preservados). Registrado em `decisions.md`.
- **Warning pre-existente** (`UnicodeDecodeError` em thread de background do RAG) segue presente nos runs, fora do diff -- nao e falha (62 passed).
- **Lição da part-1 aplicada:** rodei o `pytest` completo (nao so `auto_check --changed`) antes de declarar verde -- nenhuma regressao desta vez.

### Proximo passo
Ready to ship. Part 3 (higiene de estado) liberada -- depende da part-1 (PASS) e e independente da part-2.
