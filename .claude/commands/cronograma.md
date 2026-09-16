---
description: "Derivador read-only do cronograma de Reta Final (EMED): extrai Cronograma.pdf -> grade.json e cruza com performance/FSRS. Assinatura canônica de tools/cronograma.py. Governado por core/contracts/cronograma-contract.md."
type: skill
layer: commands
status: canonical
---

# Skill: Cronograma

> Assinatura canônica de `tools/cronograma.py`. Governado por `core/contracts/cronograma-contract.md`.
> 🔴 **Read-only:** este CLI NUNCA escreve no `ipub.db` (nem taxonomia, nem sessoes_bulk, nem FSRS, nem review_log). Cláusula 5 do contrato.

---

## Quando usar

- No **boot** (via `day_plan.py`, que importa este módulo) para saber semana de conteúdo, temas previstos e ritmos-alvo.
- Quando o `Cronograma.pdf` muda → `--rebuild`.
- Para planejar cobertura (`--radar`) ou medir o gap de volume vs meta (`--gap`).

## SSOT e derivado

- **SSOT** = `Cronograma.pdf` (raiz, IP do EMED, gitignored; `data/Cronograma.pdf` e aceito como fallback pelo `resolve_pdf_path()` -- hotfix s166, o `--check` abortava sem ele).
- **Derivado versionado** = `core/cronograma/grade.json` (estrutural, sem texto clínico → commitado).
- **Segundo derivador (Extensivo, 52 semanas)** -- SSOT = `[52 wk] Cronograma Extensivo.pdf` (raiz, IP do EMED, gitignored; `data/[52 wk] Cronograma Extensivo.pdf` aceito como fallback por `resolve_pdf_extensivo()`, mesmo padrão do `resolve_pdf_path`). Derivado versionado = `core/cronograma/grade_extensivo.json`. PRD `plano-ssot-e-cards-v2`, Parte 1 -- ver seção própria abaixo.

## Subcomandos

```bash
python tools/cronograma.py --rebuild              # extrai o PDF -> grade.json (+ valida) -- regrave após o PDF mudar
python tools/cronograma.py --check                # grade.json em dia vs PDF? (sha256) -> fresh|stale|missing
python tools/cronograma.py --validate             # asserções da Fase 1 (S10=273, S11-28=6689/222, áreas)
python tools/cronograma.py --json [--semana N]    # imprime a grade inteira ou só a semana N
python tools/cronograma.py --gap [--meta M] [--desde N]    # gap de volume: acum(ipub) + cronograma restante vs meta (default 10000)
python tools/cronograma.py --radar [--desde N]    # cobertura futura × performance, fronteira pré/pós-ENAMED
python tools/cronograma.py --sync-drive <xlsx>    # lê o "Cronograma de Reta Final.xlsx" local (ordem manual + conclusão) e grava o snapshot preparacao_estado.cronograma_conclusao_drive (W8 do reconcile; ritual do usuário, o agente só pede)
```

- `--desde N`: semana inicial p/ `--gap`/`--radar`. **Default = semana nominal por data**; passe a semana de **conteúdo** (ex.: `--desde 11`) para o gap/radar refletirem a posição real do estudante (atrás do calendário).
- `--meta M`: meta de volume p/ `--gap` (default 10000 = meta-prova ENAMED; 12000 = teto).

## Flags do radar

- 🟢 coberta pré-ENAMED · 🟡 só pós-ENAMED (tarde) · 🔴 fraca SEM cobertura restante · ⚪ gap total (0q feito · 0 no cronograma restante).
- Normaliza rótulos sujos na leitura (W4): `GO` sinalizado (split não-trivial), mojibake `Obstetrícia` corrigido. **Não toca o db.**

## API para consumidores (import, não reparseia)

`day_plan.py`/`performance.py`/`/refrescar`/`/revisar` **importam** funções, não reparseiam o PDF (Cláusula 4):

- `load_grade()` → dict da grade · `get_semana(grade, n)` · `semana_corrente(grade, hoje)` (nominal por data).
- `gap_volume(grade, total_acum, meta, desde_semana)` · `radar(grade, por_area, desde_semana)` + `render_radar(r)`.
- `AREA_PDF_TO_CANON` (linchpin do JOIN) · `ENAMED` · `SEMANA_1_INICIO`.

## Ponteiro de semana de conteúdo

`day_plan.py` lê o ponteiro textual **`Próxima = SNN`** (HANDOFF > ESTADO; fallback = semana nominal por data). É o **único write** que a feature de cronograma autoriza (Cláusula 5), atualizado no fechamento quando a semana de conteúdo vira.

## Extensivo (52 semanas) -- segundo derivador

> PRD `plano-ssot-e-cards-v2`, Parte 1. Mesmo módulo/PDF-lib do derivador da Reta Final (§7.2: assinatura canônica em UMA skill) -- 52 semanas / 735 tarefas medidas no PDF real (s183).

```bash
python tools/cronograma.py --rebuild-extensivo             # extrai '[52 wk] Cronograma Extensivo.pdf' -> grade_extensivo.json
python tools/cronograma.py --check-extensivo                # grade_extensivo.json em dia vs o PDF? (sha256) -> fresh|stale|missing|missing_pdf
python tools/cronograma.py --rebuild-extensivo --expect-tasks N   # override da contagem esperada (default 735) -- SÓ quando o PDF do EMED mudou de verdade
```

- 🔴 **Falha dura por decisão da spec:** `--rebuild-extensivo` recusa gravar `grade_extensivo.json` quando a contagem parseada não bate **735 tarefas / 52 semanas** (ou quando alguma tarefa fica sem disciplina reconhecida) -- levanta `ExtensivoContagemDivergente`, nunca versiona um catálogo com buraco silencioso.
- `--expect-tasks N` é a **única** válvula de escape: quando passada, destrava a checagem inteira (tarefas *e* semanas, contra o que o parser efetivamente encontrou) -- porque a spec só previu um flag para "o PDF do EMED mudou de verdade". Sem o flag, os dois números continuam invariantes.
- `_meta` de `grade_extensivo.json`: `{fonte, sha256, gerado_em, n_semanas, n_tasks, n_teoria, n_revisao, n_rpq}`. Cada task: `{tarefa, disciplina, area_norm, assunto, subtemas[], tipo, tipo_norm, paginas_livro[[ini,fim]], n_paginas, n_links_questoes, n_questoes|null, url_lista|null}`.
- `tipo_norm` tem **3 valores** (`teoria` | `revisao` | `revisao_questoes`, via `normaliza_tipo` -- o mesmo da Reta Final); `tipo` preserva o rótulo bruto (`Teoria I/II/III`, `Revisão I/II`, `Revisão por Questões`, `Questões Erradas`, `Diversos Assuntos`).
- `area_norm` reusa `AREA_PDF_TO_CANON` (mesma taxonomia EMED -> canônica da Reta Final -- um só lugar, não uma segunda tabela). Duas exceções documentadas caem em `Multi`: **"Todas as Disciplinas"** (coringa multi-área, igual à Reta Final) e **"Radiologia"** (não está em `core/areas.json` -- mudar a lista é decisão do operador, F89). Tarefas com lista encadeada de disciplinas (ex. Semana 52 "Revisão Final": *"Cardio, Psiquiatria e Nefro"*) também viram `Todas as Disciplinas`/`Multi` em vez de ficarem presas à primeira disciplina da lista.
- `url_lista` é **best-effort**, nunca scraping -- só o que o texto do PDF já expõe (link "Caderno de Questões" quando a tarefa declara um); `null` quando o PDF não expõe. `n_questoes` só existe em ~76/735 tarefas (as que declaram N explícito na lista) -- o resto é `null`.
- Anti-scope: nenhuma escrita no `ipub.db` nesta parte (mesma fronteira read-only do `cronograma-contract`); nenhuma extração de URL além do que o PDF expõe.
