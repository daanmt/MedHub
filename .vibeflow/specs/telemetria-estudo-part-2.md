# Spec: Telemetria de estudo — part 2: relatório de aderência — degrau 3/4

> Gerado de `.vibeflow/prds/HANDOFF-telemetria-comportamento-estudo.md` em 2026-07-12 (Fable/ai-eng).
> Executor: Fable/ai-eng (reforma delegada pelo operador).
> ⛔ Fronteira clínica: aderência é métrica de PROCESSO (contadores/timestamps); nenhuma
> leitura de conteúdo de card/resumo; nenhum juízo de conhecimento médico.

## Objective

`day_plan --aderencia` responde com números, derivados só do db: o que foi planejado
aconteceu? — blocos cumpridos/pulados, volume planejado×drenado, por dia.

## Context

Com a part-1, o planejado existe em `plano_dia`; o realizado sempre existiu
(`fsrs_revlog.review_time`, `review_log`, `sessoes_bulk.data_sessao`). Falta a comparação.
Trava anti-sycophancy do PRD: aferir contra o MEDIDO — `--energia` declarado é dimensão
do plano, jamais evidência de cumprimento.

## Definition of Done

1. [ ] `day_plan --aderencia [--semanas N]` (default 1) imprime, por dia: blocos
   planejados / cumpridos / parciais / pulados + volume planejado×realizado — derivado
   exclusivamente de `plano_dia` × tabelas de realizado; **zero input manual** e zero
   prosa fabricada (números e labels apenas).
2. [ ] Bloco planejado sem realização correspondente até o fim do dia → classificado
   `pulado` no relatório do dia seguinte (fixture temporal prova: plano D, revlog vazio,
   relatório em D+1 mostra pulado).
3. [ ] Teste prova a trava anti-sycophancy: as colunas-fonte da classificação
   cumprido/pulado vêm de `fsrs_revlog`/`review_log`/`sessoes_bulk` — `energia`/`tempo_h`
   não participam da classificação (alterar o flag na fixture não muda o veredito).
4. [ ] Matching planejado→realizado documentado e determinístico: por dia + `task_tipo`
   (+ `alvo_tema` quando o realizado tem tema); realizado sem plano correspondente aparece
   como `extra` (não é erro — é sinal).
5. [ ] Craftsmanship: `pytest` inteiro verde + suíte nova (cumprido, parcial, pulado,
   extra, semana vazia → relatório vazio sem crash); paridade R1-R5 intocada; convenções
   e Don'ts respeitados; saída no padrão derivável (apta a virar alvo de anotação
   `drift-check: sqlite` do degrau 1 se citada em doc).

## Scope

- `tools/day_plan.py`: subcomando/flag `--aderencia` + funções de classificação puras
  (testáveis sem db real).
- `tools/test_aderencia.py` (novo, fixture sintética — ids/labels fake).

## Anti-scope

- NÃO alimentar o recomendador com a série nesta spec (consumo por R1-R5 = ciclo futuro,
  após o operador ver o relatório e dizer o que importa).
- NÃO métricas de acerto clínico por tema como juízo de conhecimento (rating agregado =
  processo; interpretação de mérito = do usuário).
- NÃO alertas/notificações. NÃO gráficos/UI Streamlit (relatório CLI primeiro; página é
  demanda futura). NÃO retro-preencher aderência de datas sem plano persistido.

## Technical Decisions

- **Classificação em função pura** (`classificar_dia(plano_rows, realizado_rows) -> dict`):
  o db entra só na borda; a lógica é testável com listas — mesmo estilo de
  `infer_nota(sinais)`/`montar_sinais` já presentes no day_plan.
- **`parcial`** = realizado > 0 e < volume_planejado; limiar não configurável na v1
  (simplicidade; configurar só se o operador pedir — anti-decorativo).
- **`extra` é 1ª classe**: estudo não planejado é sinal de comportamento tão valioso
  quanto pulado — descartá-lo enviesaria a série para "só o que o plano previu".
- **Atraso de posição fica FORA do relatório v1**: já existe como `POSICAO_DRIFT` (check 5);
  duplicar aqui = dois donos para o mesmo número. O relatório referencia, não recalcula.
  (Ajuste consciente sobre o PRD, que sugeria incluí-lo — um dono por número.)

## Applicable Patterns

- `db-access-layer.md` — leitura via conexão da tool, fechada.
- `error-insertion-pipeline.md` — CLI/stdout.
- Estilo de função-pura-com-sinais do próprio `day_plan` (`infer_nota`) — padrão local.

## Risks

- **Matching frouxo** (tema com grafia diferente entre plano e realizado) → mitigação:
  normalização já existe (`_norm_tema`); realizado não-casado cai em `extra` — visível,
  nunca silenciosamente perdido.
- **Semana sem plano persistido** (série recém-nascida) → relatório explicita "sem plano
  gravado para D" em vez de zero fabricado (honestidade > completude).
- **Interpretação punitiva** (aderência baixa vira cobrança) → fora do software: relatório
  descreve, não julga; sem emoji, sem adjetivo.

## Dependencies

- `.vibeflow/specs/telemetria-estudo-part-1.md` (obrigatória — sem `plano_dia` não há comparação).
