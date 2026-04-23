---
description: "Checagem rápida de performance MedHub — total acumulado, meta do mês, custo/questão e áreas fracas. Read-only."
type: skill
layer: commands
status: canonical
---

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
2. **Meta do mês** — meta acumulada do mês corrente (de `METAS_MENSAIS` hardcoded no script), déficit, ritmo diário necessário para fechar o mês.
3. **Custo por questão** — em duas dimensões:
   - *Acumulado*: investimento total ÷ todas as questões.
   - *Mês corrente*: parcela do mês ÷ questões feitas no mês.
   Cada um classificado em faixa visual (🟢 Meta / 🟡 Ótimo / 🟠 Bom / 🔴 Alto / 🟣 Crítico) com distância da meta final (R$ 0,10/q em dez/2026).
4. **Marcos adiante** — distância em questões até ENARE (17.000) e Final (23.000).
5. **Áreas fracas e gaps** — áreas com performance < 75% ordenadas por pior, e áreas de `AREAS_VALIDAS` com 0 questões.

---

## Protocolo de resposta ao usuário

1. **Rodar o script** via Bash: `python tools/performance.py`.
2. **Relaya o relatório** para o usuário (ele já vem formatado em markdown).
3. **Complementa com 2–4 linhas de leitura estratégica** ao final, apontando 1–3 ações concretas para os próximos dias/semanas. Exemplos de ângulos úteis:
   - Se **ritmo necessário > 100q/dia**: recomendar priorizar bloco de revisão por questões em vez de criar resumos novos.
   - Se **custo/Q do mês > 3× a meta**: sinalizar que o mês está subutilizando o investimento — incentivar volume.
   - Se **áreas com 0 questões**: sugerir abrir um bloco inaugural (30–50q) de entrada na área.
   - Se **performance < 70% em área com volume > 50q**: sugerir análise de padrões de erro ou revisão do resumo.

A leitura estratégica **não** duplica o relatório — aponta ação.

---

## Atualização de metas

Quando as metas mensais ou faixas de custo mudarem, editar **apenas** no topo de `tools/performance.py`:

- `METAS_MENSAIS` — dict `{"YYYY-MM": {"meta_acumulada": int, "investimento": float}}`.
- `FAIXAS_CUSTO` — lista ordenada de tuplas `(limite_superior, emoji, rotulo)`.
- `META_CUSTO_Q` — alvo final (default `0.10`).

Nenhuma outra mudança é necessária.

---

## Notas

- Script é **read-only**. Nunca altera `ipub.db`. Pode ser rodado a qualquer momento da sessão sem side effects.
- Depende apenas da tabela `sessoes_bulk` — fonte de verdade para volume por área (populada via `tools/registrar_sessao_bulk.py`).
- Se o mês corrente sair da série `METAS_MENSAIS` (ex.: rodar em jan/2027 sem atualizar), o script degrada graciosamente: blocos 2 e 3 trazem aviso, blocos 1/4/5 seguem funcionais.
