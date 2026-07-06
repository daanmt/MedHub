---
type: contract
layer: core
status: ativo
relates_to: [AGENTE, fsrs-management-contract, forgetting-curve-contract]
---

# Contrato de Orquestracao da Preparacao (Recomendador do Dia)

> Norma do recomendador (PRD orquestracao-preparacao, part-2; 2026-07-06).
> Mecanica: `tools/day_plan.py::recomendar_dia` (funcao pura, deterministica).
> A tabela de parametros da secao 4 ESPELHA as constantes do CLI (mesmos nomes e
> valores) -- a paridade e verificada por teste (`tools/test_orquestrador.py`).
> Ajustar comportamento = editar o parametro nos dois lugares.

## 1. Principio

O day_plan deixa de ser relatorio e passa a RECOMENDAR o dia: mix de blocos com
quantidades, justificativa citando sinais derivados e projecao de fechamento da
grade. Deterministico e transparente -- nada de ML; toda decisao e explicavel por
uma regra nomeada abaixo. Reduzir carga, descansar e fazer simulado sao saidas
legitimas do recomendador (decisao do operador, 2026-07-05). O objetivo que a
funcao serve: fechar o cronograma INTEIRO antes da prova com a melhor performance
sustentavel -- nao maximizar volume num dia isolado.

## 2. Sinais (todos derivados do db)

- ritmo real de questoes (q/dia, janela movel de `sessoes_bulk`; Simulado nao conta)
- grade restante x dias ate a prova -> ritmo necessario e folga projetada
- divida FSRS (vencidos) + teto efetivo do dia (F4, fsrs-management-contract v1.1)
- backlog de cards novos
- posicao SSOT (part-1): semana de conteudo + atraso vs calendario nominal
- cards de erro FRESCOS do tema-alvo (state 0 criados na janela; F23)
- contexto declarado do dia: `--tempo H` e `--energia alta|media|baixa` (opcionais;
  quando omitidos o output DECLARA os defaults assumidos; o informado e registrado
  em `preparacao_estado` como serie bruta para o preditivo futuro)

## 3. Regras (ordem de avaliacao)

- **R1 mini-drill (anti-reincidencia, F23):** ha cards de erro frescos do tema-alvo
  (janela `FRESCOS_JANELA_HORAS`) -> o PRIMEIRO bloco e o mini-drill deles.
- **R2 descanso:** energia = baixa E folga projetada >= `LIMIAR_FOLGA_DESCANSO_DIAS`
  -> dia leve: sem tema novo; FSRS reduzido (cap `FSRS_LEVE_CAP`) apenas se ha
  vencidos. A avaliacao ENCERRA aqui (nao empilha questoes num dia de descanso).
- **R3 simulado:** semana de conteudo multipla de `PERIODO_SIMULADO_SEMANAS` ->
  slot de simulado (area 'Simulado' do registro de volume). Recomendacao de slot,
  nunca geracao de conteudo.
- **R4 questoes da grade:** qtd = min(capacidade do dia, ritmo necessario arredondado
  para cima). Grade ATRASADA (folga < 0) -> capacidade maxima do dia.
  capacidade = tempo_h x `QUESTOES_POR_HORA` x fator de energia.
- **R5 fsrs:** qtd = min(teto efetivo, vencidos + 15). O teto dinamico (F4) segue
  sendo o unico governador da divida -- este contrato nao o altera.

## 4. Parametros (paridade testada com tools/day_plan.py)

| Parametro | Valor | Significado |
|---|---|---|
| JANELA_RITMO_DIAS | 14 | janela movel do ritmo real (q/dia) |
| TEMPO_DEFAULT_H | 4.0 | horas assumidas sem --tempo |
| QUESTOES_POR_HORA | 15 | conversao tempo -> capacidade de questoes |
| LIMIAR_FOLGA_DESCANSO_DIAS | 3 | folga projetada minima p/ descanso com energia baixa |
| PERIODO_SIMULADO_SEMANAS | 4 | cadencia do slot de simulado |
| FRESCOS_JANELA_HORAS | 48 | janela do mini-drill anti-reincidencia |
| FSRS_LEVE_CAP | 15 | cap de cards no dia leve/descanso |

`ENERGIA_DEFAULT` = media. `FATOR_ENERGIA`: alta 1.0 · media 0.85 · baixa 0.6.

## 5. Gate anti-decorativo

Se em 3 sessoes de uso a recomendacao nao alterar nenhuma decisao real do dia
(operador consistentemente segue outra coisa sem motivo registrado no fechamento),
revisar parametros ou REMOVER a secao. Recomendacao ignorada e pior que ausente.
