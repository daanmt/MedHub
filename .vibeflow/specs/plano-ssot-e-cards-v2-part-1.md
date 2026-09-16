---
type: spec
projeto: MedHub
feature: plano-ssot-e-cards-v2
part: 1
slug: plano-ssot-e-cards-v2-part-1
status: ready
relates_to:
  - .vibeflow/prds/plano-ssot-e-cards-v2.md
  - tools/cronograma.py
  - core/cronograma/grade_extensivo.json
  - .claude/commands/cronograma.md
---

# Spec -- Parte 1: `grade_extensivo.json` derivado do Cronograma Extensivo (52 semanas)

> PRD `plano-ssot-e-cards-v2`, P1 (primeira metade). Mapa de partes: 1-4 = P1 (plano SSOT), 6 = P2 (ledger de listas), 7-8 = P3 (painel + congelar Drive), 9 = P4 (player). Parte 5 = P5 (poda, entregue na s183).

## Objective
O derivador único do cronograma passa a produzir também a grade do Extensivo (52 semanas, 735 tarefas) a partir do PDF, no mesmo modelo versionado do `grade.json`, para que o plano (Parte 2) e o Dashboard do Drive (707 tarefas = S1-S48 do extensivo) falem o mesmo catálogo.

## Context
`tools/cronograma.py --rebuild` só conhece o `Cronograma.pdf` da Reta Final (30 sem, 352 tarefas). O `Dashboard EMED 2026` cataloga as 707 tarefas do extensivo (medido na s183: 674/735 casam por nome), e o `[52 wk] Cronograma Extensivo.pdf` está na raiz (gitignored por `*.pdf`). O parser foi prototipado na s183 (52 semanas com tabela "Resumo" + "Passo a Passo"; `disciplina`, `assunto`, `tipo` Teoria I/II/III | Revisão | Revisão por Questões, `paginas_livro`, `n_links_questoes`, `n_questoes` quando a lista declara). Sem esta parte, `plano_tarefas` não tem de onde ser semeada para a Fase 2.

## Definition of Done
1. `python tools/cronograma.py --rebuild-extensivo` gera `core/cronograma/grade_extensivo.json` com `_meta {fonte, sha256 do PDF, gerado_em, n_semanas, n_tasks, n_teoria, n_revisao, n_rpq}` e `semanas[52].tasks[]` com `{tarefa, disciplina, area_norm, assunto, subtemas[], tipo, tipo_norm, paginas_livro[[ini,fim]], n_paginas, n_links_questoes, n_questoes|null, url_lista|null}`; `n_tasks == 735` e `n_semanas == 52` (números medidos na s183; divergência é BLOCK do próprio rebuild, não WARN).
2. `python tools/cronograma.py --check-extensivo` devolve exit 0 quando o JSON está em dia com o PDF (sha256) e exit 1 com mensagem quando não está; PDF ausente = mensagem clara, exit 1, nunca traceback.
3. `area_norm` de toda task pertence a `core/areas.json` ("Medicina Preventiva" -> `Preventiva`, "Obstetricia" -> `Obstetrícia`, etc.) ou a `Multi` para "Todas as Disciplinas"; `tools/test_cronograma_extensivo.py` cobre parser (fixture de 2 semanas sintéticas em texto), normalização de disciplina, sha-check e a asserção 735/52 sobre o JSON versionado.
4. `python tools/cronograma.py --rebuild` (Reta Final) continua produzindo exatamente `n_tasks: 352` e `total_questoes: 10218.5` -- teste de regressão existente passa.
5. Flags novas documentadas em `.claude/commands/cronograma.md` (skill dona), espelho regenerado (`sync_skills --check` exit 0); `auto_check --changed` PASSED, incluindo D5.
6. Craftsmanship: zero violação dos Don'ts de `conventions.md` (sem `import sqlite3` fora de `db.py`; sem LaTeX/setas Unicode em docs; nenhum PDF ou trecho de Livro Digital copiado para o repo -- só metadados).

## Scope
- `tools/cronograma.py`: `--rebuild-extensivo`, `--check-extensivo`, `resolve_pdf_extensivo()` (raiz -> `data/` fallback, como o `resolve_pdf_path` do hotfix s166), parser em funções puras (`parse_extensivo_text(texto) -> semanas`).
- `core/cronograma/grade_extensivo.json` (versionado, gerado).
- `tools/test_cronograma_extensivo.py` + registro em `pytest.ini`.
- `.claude/commands/cronograma.md` (+ espelho gerado).

## Anti-scope
Nenhuma escrita no `ipub.db` (a fronteira read-only do `cronograma-contract` v1.2 segue intacta nesta parte). Nenhuma extração de URL de lista além do que o texto do PDF expõe (sem scraping). Nenhuma mudança em `day_plan.py`. Nada de tocar o `grade.json` da Reta Final além do teste de regressão.

## Technical Decisions
- **Mesmo módulo, segundo derivador**: reusar `PyPDF2` e as helpers de normalização (`normaliza_tipo`, `AREA_PDF_TO_CANON`) em vez de um `cronograma_extensivo.py` novo -- a §7.2 exige assinatura canônica em UMA skill e o `/cronograma` já é a dona. Trade-off: arquivo maior; ganho: um só lugar para a taxonomia EMED -> canônica.
- **Tipo normalizado com 3 valores** (`teoria` | `revisao` | `revisao_questoes`), preservando o rótulo bruto (`Teoria I/II/III`, `Revisão I/II`) em `tipo`, porque o Dashboard casa pelo rótulo bruto e o plano agrupa pelo normalizado.
- **Sha256 do PDF no `_meta`** para o `--check-extensivo`, igual ao W5 do reconcile para a Reta Final; o PDF é IP e não viaja, então o JSON versionado é a cópia auditável.
- **Falha dura no rebuild quando a contagem diverge de 735/52**: o parser é frágil a texto colado ("GastroenterologiaPolipose"); melhor recusar gerar que versionar um catálogo com buraco silencioso. Recontagem só por decisão explícita (`--expect-tasks N`, documentada).

## Applicable Patterns
- `warn-first-check.md`: o `--check-extensivo` entra no reconcile como W5b **WARN** (Parte 4 liga ao `auto_check`); esta parte só entrega o comando.
- `agent-workflow-protocol.md`: skill = assinatura atômica; a orquestração "rebuild -> semear" fica no workflow (Parte 2).

## Risks
- Texto do PDF colando disciplina+assunto -> regex por disciplina conhecida + asserção de contagem (DoD 1). Mitigação extra: relatório `parse_report` impresso no rebuild com as linhas não reconhecidas.
- `n_questoes` só existe em ~76 listas com N explícito; o resto fica `null` e o plano usa média por tipo (Parte 2) -- declarar no `_meta`.

## Dependencies
Nenhuma. É a primeira parte.
