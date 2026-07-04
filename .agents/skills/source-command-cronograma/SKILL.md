---
name: "source-command-cronograma"
description: "Derivador read-only do cronograma de Reta Final (EMED): extrai Cronograma.pdf -> grade.json e cruza com performance/FSRS. Assinatura canônica de tools/cronograma.py. Governado por core/contracts/cronograma-contract.md."
---

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

- **SSOT** = `Cronograma.pdf` (raiz, IP do EMED, gitignored).
- **Derivado versionado** = `core/cronograma/grade.json` (estrutural, sem texto clínico → commitado).

## Subcomandos

```bash
python tools/cronograma.py --rebuild              # extrai o PDF -> grade.json (+ valida) -- regrave após o PDF mudar
python tools/cronograma.py --check                # grade.json em dia vs PDF? (sha256) -> fresh|stale|missing
python tools/cronograma.py --validate             # asserções da Fase 1 (S10=273, S11-28=6689/222, áreas)
python tools/cronograma.py --json [--semana N]    # imprime a grade inteira ou só a semana N
python tools/cronograma.py --gap [--meta M] [--desde N]    # gap de volume: acum(ipub) + cronograma restante vs meta (default 10000)
python tools/cronograma.py --radar [--desde N]    # cobertura futura × performance, fronteira pré/pós-ENAMED
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
