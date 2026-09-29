# Spec: nota 1 volta no dia seguinte -- part 1 (motor)

> Origem: F140, auditado na s204 (`.vibeflow/audits/f140-fila-pos-bloco-audit.md`).
> Decisão do operador (28/09/2026): *"volta apenas no dia seguinte. 'hoje' é apenas no redrill, já contemplado."*

## Objetivo

Card que recebe nota 1 deixa de ser re-servido e regravado no mesmo dia: o motor agenda sempre em dias inteiros.

## Contexto

`app/utils/fsrs.py` cria o `Scheduler` com `learning_steps=()` e deixa `relearning_steps` no default do py-fsrs (1 passo de 600 s). Nota 1 sobre card em `state=2` leva a `state=3` com `due = revisão + 10 min`. O player já re-drilla a nota < 3 dentro do lote sem gravar; o passo do motor duplica isso e grava uma 2ª nota. `tools/fsrs_optimize.py:318` monta um Scheduler próprio com os mesmos argumentos digitados à mão.

## Que fricção esta spec remove -- e ela é virtuosa ou viciosa?

Remove a 2ª nota gravada no mesmo dia pelo motor: **viciosa** (duplicata sem decisão pedagógica, consome teto). O relearning até o critério, que é a fricção **virtuosa**, vive no re-drill do player e não é tocado.

## Definition of Done

1. `tools/test_fsrs.py` ganha o check "Again em Review fica em Review (2), `due` >= 1 dia, lapse +1", escrito ANTES do fix e visto vermelho.
2. Check de propriedade no mesmo arquivo: para estado em {novo, 2, 3 legado} e nota em {1, 2, 3, 4}, `due - revisão >= 1 dia`.
3. `tools/test_fsrs_optimize.py::test_scheduler_do_otimizador_usa_os_kwargs_de_producao` passa: adapter e otimizador leem a mesma constante.
4. Golden read-only sobre cópia do banco: replay do revlog inteiro com o Scheduler novo mantém S e D iguais ao gravado em todas as linhas; só `state` e `due` diferem, e só nas linhas de nota 1 sobre `state` 2 ou 3.
5. `.vibeflow/index.md` e `.vibeflow/conventions.md` descrevem o Scheduler que existe.
6. Suíte completa verde e `python -X utf8 tools/auto_check.py --changed` PASSED; nenhuma violação dos Don'ts de `conventions.md`.

## Escopo

- `app/utils/fsrs.py`: constante pública com os argumentos-base do Scheduler, incluindo `relearning_steps=()`; docstring e comentários corrigidos.
- `tools/fsrs_optimize.py`: `_scheduler` parte da constante do adapter; limite (d) da docstring atualizado.
- `tools/test_fsrs.py`, `tools/test_fsrs_optimize.py`.
- `.vibeflow/index.md`, `.vibeflow/conventions.md`.

## Anti-escopo

- Fila, `--new-limit`, teto: part 2.
- Contratos, skills, ledger, termos revogados: part 3.
- F141 (ramo de curto prazo com menos de 24 h), F142 (trava de 2ª gravação, teto por card).
- Subir o py-fsrs para 6.3.2.
- Migração de dado: os 4 cards ativos hoje em `state=3` não são tocados; amanhecem `atrasados` e saem do estado 3 na próxima nota.
- Remover o tratamento de `state=3` do balanceador e do blackout (F98): fica como está, cobre o legado.

## Decisões técnicas

- **`relearning_steps=()` e não filtro na fila.** Só isso tira os dois sintomas (re-serviço e "vira atrasado"); S e D saem idênticos; a biblioteca tem ramo próprio para o campo vazio. Custo: o estado 3 deixa de ser produzido.
- **Fonte única dos argumentos.** O otimizador digitava os mesmos kwargs; divergiria em silêncio. Passa a importar do adapter.
- **Sem migração.** Card legado em `state=3` cai no ramo de borda da biblioteca e volta a Review com qualquer nota.

## Padrões aplicáveis

- `patterns/db-access-layer.md`: nenhum acesso novo a banco; o adapter segue puro.
- `patterns/warn-first-check.md`: nenhum sensor novo nesta parte.

## Riscos

- **Teste que dependia do estado 3 produzido pelo adapter.** Mapeado por leitura: só `test_fsrs.py:73`. Mitigação: suíte completa antes do commit.
- **Agenda da tela de fim do player** usa `db.preview_ratings`, que passa pelo adapter: a previsão da nota 1 muda para o dia seguinte. É o comportamento desejado; `tools/test_preview_ratings.py` confere a paridade.

## References

- `.vibeflow/audits/f140-fila-pos-bloco-audit.md` -- evidência, replay e simulação do remédio.
- `tmp/f140_auditoria/o1_t1_replay.py` -- replay de partida (reproduz 3.579 de 3.579 com o Scheduler atual).
