---
name: "source-command-cronograma"
description: "Derivador read-only do cronograma de Reta Final (EMED): extrai Cronograma.pdf -> grade.json e cruza com performance/FSRS. Assinatura canônica de tools/cronograma.py. Governado por core/contracts/cronograma-contract.md."
---

<!-- 🔴 ARQUIVO GERADO por tools/sync_skills.py -- NAO EDITE AQUI.
     Edite `.claude/commands/cronograma.md` e rode `python tools/sync_skills.py`.
     Qualquer edicao feita neste arquivo e SOBRESCRITA no proximo sync. -->

# source-command-cronograma

Use this skill when the user asks to run the migrated source command `cronograma`.

## Command Template

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
python tools/cronograma.py --sync-drive <xlsx>    # ⚰️ REVOGADO 17/09/2026 -- não invocar, não pedir ao usuário (ver a lápide abaixo)
```

### ⚰️ `--sync-drive` — REVOGADO em 17/09/2026 (PRD `plano-ssot-e-cards-v2`, Parte 4)

> **Não invocar e não pedir o ritual ao usuário.** O flag **continua existindo em código** e ainda
> grava `preparacao_estado.cronograma_conclusao_drive` — mas **ninguém lê mais esse snapshot**:
> `day_plan._conclusao_drive`, `_ordenar_por_drive`, o ramo calendário de `_cronograma_hoje`, o
> banner `Drive desatualizado` e a condição **W8** do reconcile foram todos removidos/revogados
> no mesmo commit.
>
> **Motivo:** o snapshot era a terceira fonte de "o que vem agora" (junto do `grade.json` e da
> cabeça do usuário) e envelhecia em silêncio útil-zero — 42 dias no boot medido de 06/09, com a
> recomendação do dia nomeando tema já feito. Conclusão e ordem passaram a ser **colunas** de
> `plano_tarefas` (`status`/`origem_conclusao` e `semana_plano`/`ordem`), editáveis por comando:
> `python tools/plano.py --concluir ID --sessao N` · `--cortar ID --motivo "..."` ·
> `--mover ID --semana N` · `--confirmar-area AREA --feitas "..." --pendentes "..."`.
> Assinatura completa desses flags em [`/engenharia-cli`](engenharia-cli.md).
>
> A **remoção do código** é a **Parte 8** do mesmo PRD, e está bloqueada aguardando o operador
> confirmar que não faz mais o ritual de reordenação manual do xlsx. Até lá, o flag fica: lápide,
> não deleção. Norma: `cronograma-contract.md` v1.3 (Cláusula 5 + Cláusula 5b revogada) e
> `reconcile-contract.md` v1.4 (W8).

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

## ⚰️ Ponteiro de semana de conteúdo — REVOGADO em 17/09/2026 (Parte 4)

> ⚰️ *Era: "`day_plan.py` lê o ponteiro textual **`Próxima = SNN`** (HANDOFF > ESTADO; fallback =
> semana nominal por data). É o **único write** que a feature de cronograma autoriza (Cláusula 5)".*
> **As duas metades morreram.** `day_plan._semana_conteudo`/`_resolver_semana_conteudo` foram
> removidos: a posição do boot passou a ser a **semana do plano** (menor `semana_plano` com
> pendência em `plano_tarefas`), impressa por `python tools/day_plan.py --handoff-block` e
> vigiada pelo `POSICAO_DRIFT` do `auto_check`. E o write deixou de ser único — `plano_tarefas`
> é a tabela da feature (`cronograma-contract` v1.3, Cláusula 5). A chave
> `preparacao_estado.semana_conteudo` sobrevive com **um** leitor
> (`tools/cobertura_conhecimento.py`); `preparacao.py --set-semana` alimenta só esse leitor e
> **não move mais o boot**.

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
