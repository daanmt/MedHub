---
type: spec
projeto: MedHub
feature: revisao-calibrada
part: 2
slug: revisao-calibrada-part-2-inferencia
status: ready
relates_to:
  - docs/plans/s094-revisao-calibrada-PRD.md
  - tools/day_plan.py
  - tools/review_radar.py
  - app/utils/db.py
---

# Spec — Revisão Calibrada · Parte 2: Inferência da Nota

> Deriva do PRD R4 §7.3-7.6. Cobre **DoD-5, DoD-6**. Depende da Parte 1.

## Objective
O boot/`day_plan.py` passa a propor uma **nota de dificuldade inferida (1-10)** + degrau + propósito para um tema, lendo só sinais frios — sem tocar estado.

## Context
`day_plan.build()` já compõe o Plano do Dia read-only (volume, FSRS, cronograma via `cronograma.py`, dormente via `dormant_refresh.pick`). Falta o eixo do PRD: inferir o quão difícil um tema é *para o usuário*. Os sinais existem dispersos: `taxonomia.percentual_acertos` (via `db`), último bloco (`sessoes_bulk`), `score`/`dias_sem_revisar` (via `review_radar.coletar()` — não há `score(tema)`, e sim lista com `score`), `leu_tema` (review_log/ultima_revisao/`_find_resumo` da Parte 1). `grade.json` **não** tem `prevalencia_enamed` → eixo 4 neutro (§7.7).

## Definition of Done
1. **CLI numérico.** `python tools/day_plan.py --difficulty "<area>" "<tema>"` imprime JSON com: `nota_inferida` (int ∈[1,10]), `degrau` (∈{D2,D5,D8,D10}), `proposito` (∈{exercicios,flashcards}), `nota_usuario` (int|null), `divergencia` (obj|null), `cronograma_hint`, `sugestao_passo`.
2. **Assertions de inferência (falsificável por fixtures).** `percentual_acertos < 50%` ⇒ `nota_inferida ≥ 7`; `percentual_acertos ≥ 80%` **e** `score_dorm < 7` **e** prevalência não-alta ⇒ `nota_inferida ≤ 3`; estreia pura (sem acerto histórico e `not leu_tema`) ⇒ `nota_inferida ≥ 9`.
3. **Divergência.** `nota_usuario=3` (da Parte 1) e `nota_inferida=6` ⇒ `divergencia` não-nulo carregando os dois valores; `|Δ| < 3` ⇒ `divergencia = null`. A nota do usuário **não** é sobrescrita.
4. **Mapa nota→degrau.** 9-10→D10, 7-8→D8, 4-6→D5, 1-3→D2 (PRD §4.6).
5. **Craftsmanship gate (anti-circularidade + read-only).** `infer_nota()` lê **apenas** sinais frios independentes (`percentual_acertos`, `acerto_bloco` de blocos de exercício/DRENAR, `score_dorm`, prevalência) — **nunca** a profundidade da preparação nem acerto "morno" pós-PREPARAR (§7.6). `day_plan` continua sem escrever em nenhuma tabela (grep: nenhum INSERT/UPDATE/commit). `clamp(1,10)` aplicado; piso de banca só se prevalência='alta'.

## Scope
- `infer_nota(sinais)` em `day_plan.py` (função de pontos do PRD §7.3, 4 eixos; eixo 4 neutro até grade ter prevalência).
- Helper que monta `sinais` de um `(area,tema)`: `percentual_acertos`/`acerto_bloco` via `db`, `score_dorm` filtrando `review_radar.coletar(area)` pelo tema, `leu_tema` via `review_log`/`get_dificuldade`+`_find_resumo`.
- `proposito`: heurística do PRD §7.4 — fila vencida do tema grande → `flashcards` (direcionado); senão `exercicios` (amplo).
- Flag `--difficulty <area> <tema>` no argparse de `day_plan.main()` (saída JSON dedicada).
- `nota_usuario` lida via `db.get_dificuldade` (Parte 1); divergência computada sempre que houver nota do usuário.

## Anti-scope
- Persistir a nota inferida (a aplicação/persistência da nota acontece na abertura de task — Parte 4 documenta; aqui é só proposta read-only).
- Histerese temporal multi-sessão (registrar série de blocos) — documentar regra na Parte 4; aqui implementar só o cálculo pontual + frescor por `dificuldade_at`.
- Alterar o render do Plano do Dia default (sem `--difficulty`) além de, no máximo, uma linha opcional.
- Tocar FSRS / review_log.

## Technical Decisions
- **`infer_nota` mora em `day_plan.py`** (não em `db.py`): é lógica de domínio read-only, e `day_plan` já importa `db`, `review_radar` (via `dormant_refresh`), `performance`. `db.py` é só acesso a dados.
- **Eixo 2 via `coletar()` + filtro**, não nova função no radar: evita duplicar SQL; `coletar(area)` já devolve `score`/`dias`/`retr`/`n_vencidos` por tema.
- **Degradação graciosa** (§7.7): sem `prevalencia_enamed` na grade, eixo 4 = peso neutro; nenhum piso de banca dispara. Quando a grade ganhar o campo, só `cronograma.py` muda.
- **Histerese assimétrica documentada, cálculo pontual aqui**: subir com 1 sinal forte é o default; descer exige 2 sinais frios (regra normativa na Parte 4) — a série temporal fica para uma iteração futura.

## Applicable Patterns
- `db-access-layer.md` — toda leitura via `db.py`; nenhuma conexão nova em `day_plan` além das já existentes.
- `domain-engine-api.md` — reusar `_find_resumo` (Parte 1) para `leu_tema`.
- CLI tools — argparse, JSON `ensure_ascii=False`.

## Risks
- **Circularidade de sinal** (§7.6). Mitigação: gate DoD-5 proíbe ler a própria saída; só sinais frios.
- **`coletar()` custo** (varre taxonomia+fsrs). Mitigação: `--difficulty` é pontual (1 tema); aceitar o custo, é CLI de boot.
- **`acerto_bloco` ambíguo** (qual "último bloco"). Mitigação: definir como a linha mais recente de `sessoes_bulk` para `(area,tema)`; `None` se inexistente (eixo 3 não atua).

## Dependencies
- `.vibeflow/specs/revisao-calibrada-part-1-fundacao-dados.md` (precisa de `get_dificuldade` + `_find_resumo` corrigido).
