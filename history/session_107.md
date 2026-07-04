# Session 107 -- PRD de Autogovernanca Proativa IMPLEMENTADO (Partes 1-4, R1-R6)

**Data:** 2026-07-04
**Ferramenta:** Claude Code (Fable 5)
**Continuidade:** herda o PRD `autogovernanca-proativa` (registrado na s106) + as 4 specs vibeflow geradas por `/gen-spec`

---

## Contexto

A s106 fechou a revisao da entrega Antigravity e produziu o PRD `.vibeflow/prds/autogovernanca-proativa.md` (R1-R6) mais 4 specs em `.vibeflow/specs/autogovernanca-proativa-part-{1..4}.md`. Esta sessao executou o ciclo `/vibeflow:implement` + `/vibeflow:audit` das 4 partes, em ordem, terminando com um unico commit e push (fechamento).

## O que foi feito

### Parte 1 (R1+R2) -- Ancora de fraquezas + boot deterministico -- audit PASS
- `app/memory/inspect.py`: `_unwrap()` desembrulha o envelope LangMem `{kind,content}` (defensivo, cai para plano) nos blocos `weak_areas` e `workflow_rules`; `_rank_weak_areas()` faz dedup por `(area, especialidade)` + ranking deterministico (error_count desc, last_updated desc), top-8. Fim dos 20 `[? / ?]` -- contra o db real renderiza as fraquezas reais, zero placeholders, deterministico.
- `tools/hooks/memory_boot.py` v2: injeta fraquezas + resumo do `day_plan.py` (subprocess, timeout 8s, fallback silencioso) + flag de drift HANDOFF<->history + "Proximo passo imediato" do HANDOFF + contrato Presenca->Expansao (o boot OFERECE o proximo ato, nao executa a sessao).
- `tools/test_memory.py`: teste novo `test_context_unwrap` (store temp, assere ausencia de `[? / ?]`). Suite 5/5.

### Parte 2 (R3) -- Harness confiavel -- audit PASS
- `tools/audit_resumos.py`: modelo de 2 severidades BLOCK/WARN (so BLOCK governa o exit code). `errors='ignore'` removido -> `UnicodeDecodeError` vira BLOCK. Regras novas nascem WARN: frontmatter secao 5.2 incompleto + encoding nao-ASCII proibido, agregadas por tipo.
- `tools/test_revisao_calibrada.py`: `test_roundtrip` isolado em copia temp do `ipub.db` (o db real fica byte-identico); guard de `fsrs` com mensagem clara + exit 2 em vez de ImportError cru.
- `tools/auto_check.py`: distingue WARN de BLOCK no relatorio final (badge de WARN via linha machine-readable, sem reimplementar a regra).
- **Desvio sinalizado:** a DoD 1 listava "emoji em header" como regra BLOCK vigente, mas ela nunca foi enforcada e a base tem 28+ headers com estrela/aviso/circulo legitimos -> promove-la quebraria a DoD 3. Nao introduzida (novas regras nascem WARN). Registrado no audit e em decisions.md.

### Parte 3 (R4) -- Paridade multi-agente -- audit PASS
- `tools/sync_skills.py` (NOVO): gerador deterministico `.claude/commands/*.md` -> `.agents/skills/source-command-*/SKILL.md` (fonte canonica unica). Modo default regenera; `--check` acusa drift de paridade (exit 1, nomeando os arquivos). Idempotente (2a execucao escreve 0 arquivos).
- Pre-sync sem perda: portadas ao canonico `.claude/commands/estilo-resumo.md` as adicoes que so existiam no espelho (bullet "Deep-Researchness em Resumos D10 / Extensivo" + secao "Autoverificacao Obrigatoria").
- Resultado: `revisar` destalado (ganha PREPARAR/DRENAR), `cronograma` espelhado (faltava), 11 skills cobertas.
- `tools/auto_check.py`: passo de paridade (roda mesmo quando so um command/skill muda) -> WARN, nao bloqueia (warning-first).

### Parte 4 (R5+R6) -- Defeitos extensivo + governanca -- audit PASS
- `tools/day_plan.py`: **C1** matching tema<->grade por igualdade normalizada (casefold+trim+colapso de espaco), ignora temas vazios, early-return (`_material_do_tema`); **G5** precedencia dura -- nota explicita do usuario NUNCA e sobrescrita; extensivo sem nota aplica floor 9 (degrau D10, nao D8) + sinal `deep_research`.
- `tools/cronograma.py`: heuristica `material_indicado` recalibrada (**C4**) -- menciona "Extensivo"/"Livro Digital Completo" E nao-revisao, no lugar do gatilho largo `tipo==teoria`. `--rebuild`: 155 extensivo / 197 resumo = **44%** (era 79%), n_tasks=352 e total=10218 preservados.
- Regra D10 unica e verbatim em `day_plan.py`, `core/contracts/revisao-calibrada-contract.md` e `AGENTE.md secao 1.2`.
- `AGENTE.md`: **secao 1.3 real** (Reflexo Autonomo de Validacao, movido para fora do 1.2) + tabela 7.4 registra `auto_check.py`/`setup_hooks.py`/`sync_skills.py` + secao 6 ganha 2 decisoes (harness staged-only+warning-first; fonte canonica de skills).
- **Decisao C4:** a TD sugeria "ausencia de Resumo", inviavel (694 ocorrencias estruturais no PDF) -> substituido pela contraparte semantica real (nao-revisao). Registrado no audit e em decisions.md.

## Validacao
- 4 relatorios de auditoria PASS em `.vibeflow/audits/autogovernanca-proativa-part-{1..4}-audit.md`.
- `python -X utf8 tools/auto_check.py --all` exit 0 (linter + suite central Partes 1-4 + harness de autonomia + paridade). `ipub.db` byte-identico antes/depois.
- Critical Gate limpo nas 4 partes (unico gatilho recorrente: `subprocess.run` no auto_check, override spec-documentado).
- Commit unico **e13ee0b** (27 arquivos, +1208/-281), aprovado pelo pre-commit hook.

## Decisoes registradas (decisions.md)
- Linter em 2 severidades; regra nova nasce WARN.
- Heuristica `material_indicado` por mencao textual (nao `tipo==teoria`); precedencia D10 (nota explicita vence, floor so na inferencia).

## Proximo passo
Voltar ao ritmo de questoes da S11 (Imunizacoes, Sepse, Anemias Hemoliticas; ~107q/dia). Ratificar em uso real o `day_plan --difficulty` recalibrado. Pendencias de fundo: reescrever `TCE.md` + `Sistemas de Informacao em Saude.md`.
