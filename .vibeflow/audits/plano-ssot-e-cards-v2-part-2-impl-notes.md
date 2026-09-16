# Notas de implementacao -- plano-ssot-e-cards-v2-part-2

Coding Agent, 2026-09-16. Ver relatorio completo no handback ao orquestrador.

## Divergencias da instrucao (declaradas, nao corrigidas por conta propria)

1. **Formula de `semana_plano` da RF prioridade 1.** A instrucao deu a formula
   `1 + (semana_rf - 17) * 7 // 12` **e** o mapeamento enumerado
   (S17-S18 -> 1, S19-S20 -> 2, S21-S22 -> 3, S23-S24 -> 4, S25-S26 -> 5, S27-S28 -> 6).
   As duas coisas **discordam** em S24, S26 e S28 (a formula manda 5, 6 e 7). O `7`
   parece typo de `6`: `1 + (S-17) * 6 // 12` == `1 + (S-17) // 2` == o mapeamento
   enumerado. Implementei o **enumerado** (`semana_fase1_pri1`), que e o que a
   instrucao escreve por extenso. Trocar e uma linha.

2. **"CM dirigida (semana 3-7 conforme a RF)" estava sub-especificado.** Nao havia
   formula. Implementei banda proporcional que preserva a ordem da RF e usa a faixa
   inteira: `semana_fase1_cm(S) = 3 + (S - 17) * 5 // 12` (S17-S19 -> 3, S20-S21 -> 4,
   S22-S24 -> 5, S25-S26 -> 6, S27-S28 -> 7). Efeito colateral medido: a semana 7
   fica com so 2 tarefas. Se a intencao era outra, e uma funcao pura testada.

3. **`semana_plano` de linha `feita`/`cortada` = NULL.** A instrucao fala em
   `semana_plano` sempre no contexto de tarefa *pendente*. Escolhi NULL para feita e
   cortada: uma tarefa marcada no Dashboard foi feita no calendario do **extensivo**,
   nunca ocupou slot deste plano -- datar para tras seria ficcao. Custo: o painel
   (part-8) nao consegue dizer "semana 8: 15 tarefas, 3 feitas" a partir do plano.

4. **`area_norm == "Multi"` (26 tarefas do extensivo).** `Multi` nao esta em
   `core/areas.json` e a instrucao nao deu regra. Nao chutei area: a linha grava
   `area = NULL` **com a nota dizendo qual rotulo a fonte trazia**
   (`area_fonte=Radiologia fora de core/areas.json (F89)`), e o dry-run imprime o
   COUNT. Sao 6 tarefas de Radiologia em S41-S47 (que entram na Fase 2 pela formula
   normal) + 20 de "Todas as Disciplinas" em S50-S52 (que ja nasciam `cortada`).
   `validar_area` continua recusando area PRESENTE e fora do vocabulario.

5. **`q_previstas` da Reta Final: terceira marca, `q_rateio`.** A instrucao previa
   duas fontes (`n_questoes` declarado | fallback 43/0 com `q_estimada`). A RF tem
   uma terceira: 15 das 149 tarefas S17-S28 tem `questoes_fonte = "rateio_igual"`,
   numero **derivado** pelo parser. Usar o valor sem marca o passaria por medido;
   substituir por 43 jogaria fora o unico sinal existente e quebraria a referencia de
   4.036q. Fica o valor com `nota` contendo `q_rateio`. Total RF pendente =
   **4035,5q**, que e o "4.036" do orquestrador.

6. **`ref_semana_fonte = 0` para `custom`.** NULL quebraria o UNIQUE (no SQLite dois
   NULLs sao distintos num indice unico) e a semeadura deixaria de ser idempotente em
   silencio para as 22 linhas custom.

## Decisoes de craftsmanship

- **`tools/plano.py` nao escreve nada.** O scanner do `test_writer_allowlist`
  confirma: `varrer_repo()["tools/plano.py"]` e `None`. Por isso ele **nao** entra na
  allowlist (entraria como entrada morta e `test_allowlist_sem_entrada_morta` cairia);
  so `app/utils/db.py` ganhou `plano_tarefas`.
- **Dry-run e read-only inclusive de DDL.** `plano_upsert_tarefas(aplicar=False)` e
  `plano_listar` **nao** chamam `_ensure_plano_table`: tabela ausente devolve conjunto
  vazio / lista vazia. Verificado contra o `ipub.db` real -- depois do
  `--semear --dry-run`, `sqlite_master` continua sem `plano_tarefas` e o arquivo
  mantem tamanho e mtime.
- **Re-seed nao pisa em progresso.** O `ON CONFLICT DO UPDATE` toca so
  `CAMPOS_SEMEADOS`; `status`, `data_conclusao`, `sessao_bulk_id` e `origem_conclusao`
  ficam de fora (sao da part-3). Ha teste dedicado
  (`test_reseed_nao_pisa_em_progresso`).
- **`bloco` e derivado, nao coluna.** `db.bloco_de(area)` + `BLOCOS_UERJ`; o filtro
  `--bloco` roda em Python sobre o resultado.

## Regressao viva

`test_fontes_reais_reproduzem_os_numeros_medidos` le os JSONs versionados (nenhum
banco) e trava 735 / 425 / 149 / **139 pendentes** / 4035,5q. Divergencia ali quer
dizer que a fonte mudou -- investigar, nunca ajustar a constante.

## Pendencias que NAO podia executar (fora do escopo de arquivos)

- `pytest.ini`: inscrever `test_plano.py` em `python_files`
  (`test_suites_orfas::test_repo_real_nao_tem_suite_orfa` esta vermelho por isso).
- `python tools/sync_skills.py`: o espelho de `engenharia-cli` ficou stale
  (`test_espelho_gerado::test_o_banner_nao_entra_no_corpo_comparado_pela_paridade`).
- `AGENTE.md` secao 7.4 (tabela gerada de CLIs): ja estava stale antes desta parte
  (faltava `cards_prune.py`); agora falta tambem `plano.py`.
- `--semear --apply --expect 896` no `ipub.db` real e o commit: ato do orquestrador.
