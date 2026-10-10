# Spec: medhub Fase 0 · Lote 0 — Part 2b: família hub/cards/EMED mede forma ou fixture

> Gerada: 2026-10-10 | PRD: `.vibeflow/prds/medhub-fase0-preparar-ambiente.md` (ai-eng) | Evidência: `brain/observed-systems/medhub-reforma-2026-10-10/E-testes-harness.md` §P7 Classe 1 (itens 1, 5, 8, 9, 10, 11) e Classe 2 (`test_hub_resumos:160-168`, `test_hub_quadro:150-173,1292`)
> Parte 2b (de 7). Pode correr em paralelo com a 2c, depois da 2a.
> Repo-alvo: medhub (implement + audit no loop vibeflow dele). Código conferido em leitura @ `6d0239a`.

## Objective

Os testes da família hub/cards/EMED que leem o banco, o plano ou os registros reais deixam de quebrar quando o operador estuda ou registra conteúdo: cada um passa a medir a forma do dado real (marcado `vivo`, com skip declarado) e ganha um gêmeo hermético sobre fixture.

## Context

Conferido no código (linhas atuais):

| Arquivo:linha | O que asserta hoje | Quebra quando |
|---|---|---|
| `tools/test_card_alinhamento_frente.py:222-253` | `medido == {"P1": 11, "P2": 4, "P3": 1}` sobre `flashcards` reais (já `skipif` sem banco) | card é reforjado/criado — já quebrou 12→13 (17/09) e 13→11 (29/09) |
| `tools/test_emed_banco.py:659-676` | todo `emed_solucoes.objetivo` real cabe no catálogo (skip sem banco) | doc novo com objetivo fora de `core/objetivos.json` |
| `tools/test_hub.py:523-546` | `hub.construir(raiz=ROOT)` com aulas e plano reais: `problemas == []`, `manifesto["aulas"] == min(len(artifacts/aula-*.html), CAP)`, semanas do plano presentes | operador conclui tarefa; aula nova sem registro; **sem banco, provavelmente falha** (o plano degrada para `[]` e o `re.search` de `qd-sem` exige semana) |
| `tools/test_hub_quadro.py:160-173` | conjunto **exato** de chaves de `core/hub_quadro.json` | RD/aula nova registrada |
| `tools/test_hub_quadro.py:1285-1311` | `len(rds) == 20` + plano real sem "grande area" | RD nova — caso s216 (2 FAILED) |
| `tools/test_hub_resumos.py:160-168` | `len(resumos) == len(reg) == 31` e `len(slugs) == 31` | resumo novo no registro |
| `tools/test_hub_resumos.py:247-262` e `:374-381` | S4 / Teoria × Painel do plano real (skip declarado sem plano) | S4 sem pendentes: `re.search(...).group(0)` levanta; já relaxado na s222 ("31 → 30 ao concluir a t40") |

**Que fricção esta spec remove — e ela é virtuosa ou viciosa?** Viciosa: suíte vermelha porque o operador estudou ou registrou conteúdo. Nenhuma fricção virtuosa é tocada.

## Definition of Done

1. [ ] As 7 funções da tabela levam `@pytest.mark.vivo` e, quando o dado que leem falta (banco, plano, registro ou `artifacts/aula-*.html`), pulam com `pytest.skip("VIVO: ...")` dizendo o que não foi medido — inclusive `test_hub.py::test_repo_real_monta_sem_problema`, que hoje pode falhar sem banco.
2. [ ] Nenhuma delas compara contra literal de contagem ou conjunto fixo do dado real: `test_card_alinhamento_frente.py:252`, `test_hub_quadro.py:165` (conjunto de chaves), `test_hub_quadro.py:1292` (`== 20`) e `test_hub_resumos.py:163-164` (`== 31`) viram asserções de forma — ex.: registro e disco concordam (`len(resumos) == len(reg)`), toda RD tem `disciplinas` ≥ 1 e fonte existente, todo tipo pertence ao conjunto permitido, a fração acusada pelo predicado fica numa banda declarada. O audit cita a asserção nova de cada uma.
3. [ ] Cada uma das 7 tem ≥ 1 gêmeo não-`vivo` (fixture sintético em `tmp_path`, `db_sintetico` da part-2a, registro/plano sintético) que exercita a mesma regra com um caso plantado. Gêmeo que já existe no arquivo é citado pelo nome no audit; o que falta é escrito.
4. [ ] `python -m pytest tools/test_card_alinhamento_frente.py tools/test_emed_banco.py tools/test_hub.py tools/test_hub_quadro.py tools/test_hub_resumos.py -q -m "not vivo"` passa; `-m vivo` sobre os mesmos arquivos passa na máquina do operador.
5. [ ] Suíte completa `python -m pytest tools/ -q` verde; nenhuma violação dos Don'ts de `.vibeflow/conventions.md`; comentários que justificavam o número fixo (ex.: `test_card_alinhamento_frente.py:244-251`) viram lápide curta (`⚰️` + data + motivo), não somem.

## Scope

`tools/test_card_alinhamento_frente.py`, `tools/test_emed_banco.py`, `tools/test_hub.py`, `tools/test_hub_quadro.py`, `tools/test_hub_resumos.py`. **Budget: 5 arquivos.**

## Anti-scope

- **Fronteiras:** design no ai-eng, implementação no medhub.
- **Nada que mude conteúdo clínico, FSRS ou o hub publicado:** `tools/hub.py`, `core/templates/*`, `core/hub_quadro.json`, `core/hub_resumos.json`, os predicados de `app/utils/card_checks.py` e o catálogo `core/objetivos.json` **não mudam** — só os testes.
- Não atualizar a spec `.vibeflow/specs/alinhamento-frente-do-card.md` do medhub com número novo.
- Classe 2 fora destes 5 arquivos (`test_provas`, `test_vocabulario_area`, `test_cronograma_extensivo`, `test_consistencia_registros` etc.) → Lote 3.
- Não editar `conftest.py` nem `pytest.ini`.

## Technical Decisions

1. **Forma em vez de número.** A pergunta que cada teste vivo responde passa de "o dado é este?" para "o dado tem a forma que o código promete?". Perde-se a detecção de mudança de contagem — que era exatamente o que quebrava a suíte sem defeito. Contagem é relatório, não regressão.
2. **Banda declarada para predicados de card** (ex.: P1/P2/P3 ≤ uma fração pequena do baralho e > 0 só se o fixture plantar): mesmo modelo que `test_comprimento_total` já usa (`frac <= 0.10`).
3. **`test_hub` vivo continua escrevendo só em `tmp_path`** (`out=tmp_path / "hub"`), como hoje.

## Applicable Patterns

- `tools/test_comprimento_total.py:200-219`: ratchet de forma ("NAO asserta um numero exato -- o baralho cresce").
- `tools/test_hub_resumos.py:259` (s222): "mede a forma, nao a contagem".
- Convenção `VIVO:` e fixture `db_sintetico` da part-2a.

## Risks

- **"A forma ficou frouxa e não pega nada."** → DoD 3: o gêmeo hermético planta o caso e exige a acusação; a forma viva só cobre o que o fixture não alcança.
- **"Skip demais na máquina do operador."** → Lá o banco e os registros existem; `-m vivo` tem de passar (DoD 4).
- **"O tique commita `core/hub_quadro.json` no meio."** → Os testes deixam de depender do conteúdo exato; reler os arquivos antes de editar (`AGENTE.md §10.1`).

## Dependencies

- `.vibeflow/specs/medhub-fase0-lote0-harness-hermetico-part-2a.md` (fixture `db_sintetico`, marcador `vivo`, convenção `VIVO:`).
