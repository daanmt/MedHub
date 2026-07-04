# Session 073 -- Consolidação do Harness em Fluxo Único
**Data:** 2026-05-27
**Ferramenta:** Claude Code (Opus 4.7)
**Continuidade:** Sessão 072

---

## O que foi feito

Iniciativa: amarrar todo o contexto/harness do MedHub em um fluxo único, previsível, minimalista, eficiente e conciso. O diagnóstico do usuário apontava 3 camadas de "agent guidance" coexistindo (`.claude/commands/`, `.agents/workflows/`, `.vibeflow/patterns/`) com duplicação semântica e drift acumulado.

**Auditoria em paralelo (3 agentes read-only, ~666 linhas em `artifacts/audits/harness/`):**

1. **Agent A** -- mapeamento de redundância skills × workflows. Encontrou 3 pares + 4 singletons:
   - **Pair 1** (`analisar-questao` ↔ `analisar-questoes`): duplicate-with-rot. Workflow shipava CLI de 8 args com semântica errada de `--correta` ("letra" vs "texto completo" da skill canônica em §9).
   - **Pair 2** (`extrair-pdf` ↔ `criar-resumo`): complementar limpo -- prova empírica de que o limite funciona.
   - **Pair 3** (`estilo-resumo` ↔ `criar-resumo`): duplicação parcial das regras de estilo.
   - Hooks (`tools/hooks/memory_*.py`) **não lêem nenhuma das superfícies** -> zero runtime risk para consolidação.
   - Recomendou two-surface com contrato em `AGENTE §7`.

2. **Agent B** -- consumo de `.vibeflow/patterns/`. Confirmou que `vibeflow:gen-spec` cita patterns por path relativo (evidência: `.vibeflow/specs/performance.md:31, :102-104`); `vibeflow:implement`/`:audit` consumption não é derivável só do repo state. **Descoberta crítica:** `domain-engine-api.md` afirmava "5 exports estáveis" do `app.engine` quando reality são 2 (per `app/engine/__init__.py:13-19` + AGENTE §6).

3. **Agent C** -- target shape + plano de commits. Produziu texto literal do contrato §7.2, 7 commits atômicos ordenados por reversibilidade, e 5 open questions com recomendações por linha.

**Decisões travadas (3 escolhas arquiteturais via `AskUserQuestion`):**

- **Two-surface com contrato em AGENTE §7** -- skills + workflows preservados; codificar o limite que já existia implicitamente.
- **`.vibeflow/patterns/` escopo conservador** -- só fix da staleness do `domain-engine-api.md` + 4 docstrings de código. Sem `historical/` subdir, sem merges, sem frontmatter adicional (evita risco de `vibeflow:analyze` reescrever).
- **Drift bugs bundled** na mesma iniciativa: 17-arg CLI stale, `Tools\` casing, `Temas/` rename, menção legada a `caderno_erros`. Escopo `Temas/` expandido de 9 -> 15 ocorrências após verificação por grep (recomendação de C).

**Execução (7 commits atômicos):**

| # | SHA | Concern |
|---|-----|---------|
| 0 | `98a2e27` | chore: gitignore `artifacts/audits/` |
| 1 | `746cb55` | docs(agente): codificar contrato skills/workflows no §7 (novo §7.2 "Contrato", renumeração §7.2->§7.3, §7.3->§7.4) |
| 2 | `eb31554` | fix(workflows): delegar CLI canônica em `analisar-questoes` (-3 linhas: bloco 8-arg stale + menção `caderno_erros`) |
| 3 | `4e83704` | fix(workflows): delegar CLI canônica em `gerar-reforco` (corrige 3 bugs num só edit: 8-arg, `Tools\` casing, backslash path) |
| 4 | `d20a373` | fix(vibeflow): corrigir staleness de `domain-engine-api` (5->2 exports; example reescrito com `get_topic_context`+`summarize_performance`) |
| 5 | `0c2249b` | docs(code): add canonical module docstrings -- `app/utils/db.py`, `app/utils/styles.py`, `app/utils/fsrs.py`, `tools/insert_questao.py` |
| 6 | `403acf8` | fix(docs): `Temas/` -> `resumos/` em 7 arquivos (replace-all). `grep "Temas/"` retorna 0 em *.md |
| 7 | -- | (no-op: cleanup defensivo de `caderno_erros` já feito em Commit 2; nenhuma menção restante em `.claude/` ou `.agents/`) |

Zero behavioral change. Hooks intocados. `.claude/settings.local.json` continua modificado no working tree mas fora de escopo desta iniciativa (separate PR planejada -- ~60 entradas de permissão hardcoded com Windows paths).

## Artefatos criados/modificados

**Source-of-truth (commitados em 7 commits):**

- `AGENTE.md` -- novo §7.2 Contrato (12 linhas inseridas), renumeração §7.2->§7.3 (Skills) e §7.3->§7.4 (CLIs).
- `.gitignore` -- adicionado `artifacts/audits/`.
- `.claude/commands/analisar-questao.md` -- `Temas/` -> `resumos/`.
- `.claude/commands/auditar-resumos.md` -- `Temas/` -> `resumos/` (inclui frontmatter `description`).
- `.claude/commands/estilo-resumo.md` -- `Temas/` -> `resumos/` (inclui frontmatter `description`).
- `.claude/commands/extrair-pdf.md` -- `Temas/` -> `resumos/`.
- `.agents/workflows/analisar-questoes.md` -- delegação CLI para skill §9 + remoção menção `caderno_erros` + `Temas/` rename.
- `.agents/workflows/criar-resumo.md` -- `Temas/` -> `resumos/`.
- `.agents/workflows/gerar-reforco.md` -- delegação CLI para skill §9 + fix `Tools\` casing + backslash path + `Temas/` rename.
- `.vibeflow/patterns/domain-engine-api.md` -- staleness fix (5->2 exports; import block + workflow example reescritos).
- `app/utils/db.py` -- module docstring (10 linhas) -- DB access layer + convenções.
- `app/utils/styles.py` -- module docstring (13 linhas) -- design system Flat & Clinical.
- `app/utils/fsrs.py` -- module docstring (12 linhas) -- FSRS v4 simplificado.
- `tools/insert_questao.py` -- module docstring (10 linhas) -- CLI canônica de inserção atômica.

**Audit reports (locais, gitignored em `artifacts/audits/harness/`):**

- `A-skills-workflows.md` -- 232 linhas, mapeamento de pares + singletons + boundary rule proposto.
- `B-vibeflow-patterns.md` -- 219 linhas, runtime consumption + per-pattern recommendations.
- `C-target-proposal.md` -- 215 linhas, target shape + 7-commit plan + 5 open questions.

## Decisões tomadas

1. **Contrato como rule, não policy:** o §7.2 é prescritivo ("workflows referenciam skills e não copiam") em vez de descritivo. Cada edição futura tem critério objetivo para passar ou ser flagged como duplicação.
2. **`.vibeflow/` minimum-touch:** o plugin auto-managed levanta risco de `vibeflow:analyze` regenerar arquivos. Conservative scope evita esse risco; correções "shape-level" em `.vibeflow/patterns/` (active/historical split, merges) ficam para sessão dedicada com teste em branch.
3. **Module docstrings como SSOT do contrato comportamental:** o `__doc__` do código sobrevive a refactors melhor que markdown -- patterns devem apontar para o docstring, não duplicar.
4. **Auditorias preservadas:** os ~666 linhas de A+B+C ficam em `artifacts/audits/harness/` (gitignored) como referência do processo, não deletadas. Mesma disposição da sessão 072 com `history/legacy/`.
5. **Auto-auditoria checklist em `criar-resumo §6` fica no workflow** (não move pra skill): pre-save gate é orquestração timing-bound ao Step 6, não especificação. Cita regras por nome -- compliant com contrato.
6. **Expansão silenciosa do escopo `Temas/`** (9->15 ocorrências) honrada após grep confirmar drift idêntico em arquivos não listados originalmente. Custo: 2 arquivos extras tocados; benefício: `grep "Temas/" *.md` retorna 0 (drift completamente eliminado).

## Próximos passos

- **Push para `origin/main` pendente** (gated em "push" explícito do usuário). 7 commits locais aguardando.
- **`.claude/settings.local.json`** continua modificado no working tree -- separate PR planejada (~60 entradas de permissão hardcoded com Windows paths).
- **`.vibeflow/patterns/` reorganization** (active/historical split, frontmatter `status: active|historical`, merge de `design-system-usage` + `streamlit-page-structure` -> `frontend.md`) -- diferido per recomendação de Agent B, requer teste de comportamento do `vibeflow:analyze` em branch.
- **Verificar se `vibeflow:analyze` preservou o fix do `domain-engine-api.md`** na próxima vez que rodar o plugin; se sobrescrever, reaplicar via `vibeflow:teach`.
- **Roadmap continua** per `ROADMAP.md`: pipeline RAG inverso, busca semântica na Biblioteca, meta volumétrica ENARE (17k até out/2026).
