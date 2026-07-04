---
name: "source-command-performance"
description: "Checagem rápida de performance MedHub — total acumulado, meta do mês, custo/questão e áreas fracas. Read-only."
---

# source-command-performance

Use this skill when the user asks to run the migrated source command `performance`.

## Command Template

# Skill: Performance

Wrapper para `tools/performance.py`. Comando read-only que consulta `ipub.db` (tabela `sessoes_bulk`) e imprime um relatório markdown estruturado sobre o progresso rumo às metas de preparação para residência médica.

Use quando o usuário pedir qualquer variação de: "como está minha performance?", "quantas questões já fiz?", "quanto falta pra meta?", "em qual área estou pior?".

---

## Invocação

```bash
python tools/performance.py
```

Zero argumentos. Rode direto e leia a saída — ela já é um relatório completo.

---

## O que o relatório informa

O script imprime 5 blocos em markdown, nesta ordem:

1. **Total acumulado** — questões feitas, acertos, performance geral (%).
2. **Marcos adiante** ⭐ *prioridade do relatório (decisão sessão 075)* — distância em questões até cada marco de `MARCOS`. Marcos **com data** (ex.: ENAMED 13/09/2026, alvo 12.000) ganham: dias restantes, ritmo necessário para o alvo e projeções de acumulado para cada ritmo de `RITMOS_PROJECAO` (80/90/100 q/dia), cada uma com % do alvo e custo/q projetado na data da prova.
3. **Meta do mês** — meta acumulada do mês corrente (de `METAS_MENSAIS` hardcoded no script), déficit, ritmo diário necessário para fechar o mês.
4. **Custo por questão** — em duas dimensões:
   - *Acumulado*: investimento total ÷ todas as questões.
   - *Mês corrente*: parcela do mês ÷ questões feitas no mês.
   Cada um classificado em faixa visual (🟢 Meta / 🟡 Ótimo / 🟠 Bom / 🔴 Alto / 🟣 Crítico) com distância da meta final (R$ 0,20/q em dez/2026 — coerente com ESTADO.md: R$ 4.410 / 23.000q).
5. **Áreas fracas e gaps** — áreas com performance < 75% ordenadas por pior, e áreas de `AREAS_VALIDAS` com 0 questões.

---

## Protocolo de resposta ao usuário

1. **Rodar o script** via Bash: `python tools/performance.py`.
2. **Relaya o relatório** para o usuário (ele já vem formatado em markdown). Os **marcos datados e suas projeções de ritmo são a informação prioritária** — destacá-los na resposta.
3. **Complementa com 2–4 linhas de leitura estratégica** ao final, apontando 1–3 ações concretas para os próximos dias/semanas. Exemplos de ângulos úteis:
   - Se **ritmo necessário > 100q/dia**: recomendar priorizar bloco de revisão por questões em vez de criar resumos novos.
   - Se **custo/Q do mês > 3× a meta**: sinalizar que o mês está subutilizando o investimento — incentivar volume.
   - Se **áreas com 0 questões**: sugerir abrir um bloco inaugural (30–50q) de entrada na área.
   - Se **performance < 70% em área com volume > 50q**: sugerir análise de padrões de erro ou revisão do resumo.

A leitura estratégica **não** duplica o relatório — aponta ação.

---

## Atualização de metas

Quando as metas mensais ou faixas de custo mudarem, editar **apenas** no topo de `tools/performance.py`:

- `METAS_MENSAIS` — dict `{"YYYY-MM": {"meta_acumulada": int, "investimento": float}}` (investimento é **acumulado**).
- `MARCOS` — lista de tuplas `(nome, alvo_acumulado, data_da_prova | None)`. Marcos com data ganham projeções de ritmo.
- `RITMOS_PROJECAO` — tupla de ritmos diários (q/dia) projetados para marcos datados.
- `FAIXAS_CUSTO` — lista ordenada de tuplas `(limite_superior, emoji, rotulo)`.
- `META_CUSTO_Q` — alvo final (default `0.20`).

Nenhuma outra mudança é necessária.

---

## Notas

- Script é **read-only**. Nunca altera `ipub.db`. Pode ser rodado a qualquer momento da sessão sem side effects.
- Depende apenas da tabela `sessoes_bulk` — fonte de verdade para volume por área (populada via `tools/registrar_sessao_bulk.py`).
- Se o mês corrente sair da série `METAS_MENSAIS` (ex.: rodar em jan/2027 sem atualizar), o script degrada graciosamente: blocos 3 e 4 trazem aviso, blocos 1/2/5 seguem funcionais (marcos datados perdem só o custo/q projetado).
- Se a data de um marco já passou, o bloco 2 avisa para atualizar `MARCOS` em vez de projetar ritmo negativo.
