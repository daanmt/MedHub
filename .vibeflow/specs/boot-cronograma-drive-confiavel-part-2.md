---
title: "Part 2 -- Integridade de rotulo: material_indicado verificado (F30) + lastro no insert (F31)"
type: spec
status: ready
prd: .vibeflow/prds/boot-cronograma-drive-confiavel.md
ledger: AUDITORIA_MEDHUB.md (resolve F30, F31)
date: "2026-07-09"
budget: 6 files
---

# Spec Part 2 -- Integridade de rotulo (Onda B: F30 + F31)

## Objective

O plano do dia deixa de prometer "so ler o resumo" para temas cujo `.md` nao existe, e a insercao de um erro em tema sem lastro escrito passa a ser sinalizada no ato -- ambos verificacoes locais, sem depender do Drive.

## Context

Duas convencoes do projeto sao hoje disciplina, nao mecanismo. (1) O cronograma marca `material_indicado: resumo` por heuristica do tipo de tarefa, sem checar se `resumos/**/*.md` para aquele tema existe -- Pre-Natal era tema-zero mascarado como "so revisar o resumo" (F30). (2) O par Siamese Twins (`AGENTE.md` 6: erro->db, licao->resumo) e convencao -- `insert_questao.py` grava o erro/card mesmo quando o tema nao tem nenhum lastro (`.md` nem PDF-fonte), e so meses depois, num refresh de FSRS, o buraco aparece (F31, caso vivo Leishmaniose, recomendado como refresh no boot de hoje). O resolver `get_topic_context._find_resumo` ja indexa `path.stem.lower()` desde s096, entao a verificacao e barata e read-only.

## Definition of Done

1. **F30 (render):** ao montar `temas_material`/"proximos temas" em `day_plan.py::_cronograma_hoje`, uma task com `material_indicado` efetivo `resumo` cujo tema NAO resolve a um `.md` (via o resolver de resumo) e exibida como `extensivo` -- nunca `resumo`.
2. **F30 (difficulty):** a mesma verificacao alimenta o resolvedor de `material_indicado` do caminho `--difficulty`/`_material_indicado`, de modo que um tema sem `.md` nao e tratado como "so ler o resumo" na calibracao.
3. **F31 (insert):** `insert_questao.py` emite um WARN read-only `[SEM-LASTRO] area/tema` quando o tema do erro nao resolve a `.md` E nao ha PDF-fonte par em `resumos/**`; a insercao **nao** e bloqueada e o exit code fica inalterado.
4. (Quality gate) `python -X utf8 tools/auto_check.py --changed` retorna `PASSED`; a verificacao e read-only (nenhum write novo, reusa o resolver existente); nenhum `import sqlite3` novo fora de db.py/CLIs; texto ASCII limpo.

## Scope

- `tools/day_plan.py`: no render de `_cronograma_hoje` e no resolvedor `_material_indicado` (caminho `--difficulty`), verificar existencia real do `.md` e rebaixar o rotulo (F30).
- `tools/insert_questao.py`: apos resolver `(area, tema)`, checar lastro e emitir WARN quando ausente (F31). CLI standalone (excecao autorizada a conexao propria, conventions 24).
- `tools/test_autonomia_hooks.py` (ou suite de cronograma/insert): fixture tema-com-md -> rotulo preservado; tema-sem-md -> rebaixado a `extensivo` (F30); insert em tema-sem-lastro -> WARN presente + exit inalterado (F31).

## Anti-scope

- **Nao cria nem edita resumos** -- so sinaliza a ausencia. Fechar o gap de conteudo (autoria do `.md`) e trabalho de sessao de estudo, nao desta spec.
- **Nao bloqueia** a insercao de erro sem lastro (WARN, nunca BLOCK) -- o erro real precisa entrar no db mesmo sem resumo.
- **Nao mexe** em FSRS/schema do `ipub.db`, nem no algoritmo de resolucao `_find_resumo` (so consome).
- **Nao toca** ordenacao/disparo do Drive (Part 1) nem higiene de estado (Part 3).

## Technical Decisions

- **Reusar `_find_resumo`, nao reimplementar.** A resolucao tema->`.md` ja existe e indexa o stem; a spec so consome o `None`. TODO(implement): confirmar o simbolo/import exato (`app.engine.get_topic_context._find_resumo` ou wrapper publico do engine) -- se for privado, expor um helper fino no engine em vez de duplicar o glob.
- **PDF-par via glob em `resumos/**`** com o mesmo `_norm` de tema ja usado (F31): um tema com PDF-fonte mas sem `.md` e F30 (rebaixa rotulo), nao F31; F31 e o caso severo sem `.md` E sem PDF.
- **F30 rebaixa para `extensivo`, o rotulo de "material denso / construir do zero"** ja usado na frente extensivo (`day_plan --difficulty`), mantendo a semantica existente.
- **WARN read-only, aditivo ao stdout** do insert -- nao altera o retorno bool nem o exit (evita colidir com F27, que e outra correcao).

## Applicable Patterns

- `db-access-layer.md`: `insert_questao.py` como CLI standalone com conexao propria; a checagem de lastro e read-only sobre o filesystem (`resumos/`), sem tocar o db.
- `error-insertion-pipeline.md`: o WARN entra no pipeline de insercao sem alterar o contrato de saida (erro->questoes_erros + flashcards).

## Risks

- **Falso-negativo do resolver** (tema real com `.md` que o `_find_resumo` nao casa por nome divergente) -> exibiria `extensivo` indevido / WARN espurio. Mitigacao: reusar exatamente o resolver ja validado (indexa stem); o custo de um falso `extensivo` e baixo (mais profundidade, nao menos cobertura).
- **Ruido de WARN** em temas legitimamente sem resumo por design -> aceitavel: e exatamente o sinal que o F31 quer tornar visivel; nasce WARN (politica s106/107), nunca bloqueia.

## Dependencies

- `.vibeflow/specs/boot-cronograma-drive-confiavel-part-1.md` (compartilha o render de `_cronograma_hoje` em `day_plan.py`; implementar a Part 1 primeiro).
