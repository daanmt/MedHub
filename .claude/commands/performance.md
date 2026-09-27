---
description: "Checagem rápida de performance MedHub — total acumulado, a meta única (10.000 em 01/11), custo/questão e áreas fracas. Read-only."
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

O script imprime 4 blocos em markdown, nesta ordem:

1. **Total acumulado** — questões feitas, acertos, performance geral (%).
2. **A meta** ⭐ *prioridade do relatório* — **uma só** (s203, decisão do operador em 27/09/2026: "a única meta por hora é 01/11 e o alvo é 10k"): `MARCOS` tem UMA entrada, 10.000 questões na prova da UERJ em 01/11. Faltam, dias restantes, ritmo necessário (o MESMO da linha Meta do boot e do painel, `volume_vs_marco`) e projeções de acumulado para cada ritmo de `RITMOS_PROJECAO` (45/60/75 q/dia), cada uma com % do alvo e custo/q projetado na data da prova. ⚰️ *Eram "Marcos adiante" (ENAMED 12.000, Ciclo 2026 12.500, Stretch 15.000) e, no bloco 3, a "Meta do mês" (`METAS_MENSAIS.meta_acumulada`, ~203q/dia em set) -- réguas concorrentes que o operador revogou.*
3. **Custo por questão** — em duas dimensões:
   - *Acumulado*: investimento total ÷ todas as questões.
   - *Mês corrente*: parcela do mês ÷ questões feitas no mês.
   Cada um classificado em faixa visual (🟢 Meta / 🟡 Ótimo / 🟠 Bom / 🔴 Alto / 🟣 Crítico) com distância da meta de custo (`META_CUSTO_Q`, R$ 0,35/q -- recalibrada na s126).
4. **Áreas fracas e gaps** — áreas com performance < 75% ordenadas por pior, e áreas de **`AREAS_CLINICAS`** com 0 questões (fonte única `core/areas.json`; `Simulado` fica de fora **por decisão declarada** — é slot de volume agregado, não matéria que se possa deixar de estudar).

---

## Protocolo de resposta ao usuário

1. **Rodar o script** via Bash: `python tools/performance.py`.
2. **Relaya o relatório** para o usuário (ele já vem formatado em markdown). Os **marcos datados e suas projeções de ritmo são a informação prioritária** — destacá-los na resposta.
3. **Complementa com 2–4 linhas de leitura estratégica** ao final, apontando 1–3 ações concretas para os próximos dias/semanas. Exemplos de ângulos úteis:
   - Se **ritmo necessário da meta > capacidade do dia (~51q em 4h)**: recomendar priorizar bloco de revisão por questões em vez de criar resumos novos.
   - Se **custo/Q do mês > 3× a meta**: sinalizar que o mês está subutilizando o investimento — incentivar volume.
   - Se **áreas com 0 questões**: sugerir abrir um bloco inaugural (30–50q) de entrada na área.
   - Se **performance < 70% em área com volume > 50q**: sugerir análise de padrões de erro ou revisão do resumo.

A leitura estratégica **não** duplica o relatório — aponta ação.

---

## Atualização de metas

Quando a meta ou as faixas de custo mudarem, editar **apenas** no topo de `tools/performance.py`:

- `METAS_MENSAIS` — dict `{"YYYY-MM": {"investimento": float}}` (investimento **acumulado**; a coluna `meta_acumulada` saiu na s203).
- `MARCOS` — lista de tuplas `(nome, alvo_acumulado, data_da_prova | None)`. **Uma entrada** desde a s203: `MARCOS[0]` é A meta, lida por `volume_vs_marco` (boot, painel, HANDOFF, `cronograma.py --gap`). Outra entrada só por decisão do operador.
- `RITMOS_PROJECAO` — tupla de ritmos diários (q/dia) projetados para marcos datados.
- `FAIXAS_CUSTO` — lista ordenada de tuplas `(limite_superior, emoji, rotulo)`.
- `META_CUSTO_Q` — alvo de custo/q (hoje `0.35`).

Nenhuma outra mudança é necessária.

---

## Notas

- Script é **read-only**. Nunca altera `ipub.db`. Pode ser rodado a qualquer momento da sessão sem side effects.  <!-- CHECK: test_writer_allowlist -->
- Depende apenas da tabela `sessoes_bulk` — fonte de verdade para volume por área (populada via `tools/registrar_sessao_bulk.py`).
- Se o mês corrente sair da série `METAS_MENSAIS` (ex.: rodar em jan/2027 sem atualizar), o script degrada graciosamente: blocos 3 e 4 trazem aviso, blocos 1/2/5 seguem funcionais (marcos datados perdem só o custo/q projetado).
- Se a data de um marco já passou, o bloco 2 avisa para atualizar `MARCOS` em vez de projetar ritmo negativo.

---

## Diagnóstico de Variância e Zona (`tools/variancia.py`)

> **Assinatura canônica deste CLI** (AGENTE.md §7.2). Spec: `.vibeflow/specs/variancia-e-zona.md`. Read-only.

**Por que existe:** no platô dos 75-80% a **média não é o sinal — a variância é**. Nota alta numa prova e baixa em outra indica desempenho dependente do *perfil da prova*, não do conhecimento. Medido em 25/07: média 77,6% (boa) e **desvio de 12,0 pp** (alto).

| Comando | Função |
|---|---|
| `--metricas [--ultimos N] [--piso Q]` | n, média, desvio-padrão populacional, amplitude, coef. de variação |
| `--zona` | classificação de 2 eixos + prescrição + débito de simulado (render legível) |
| `--simulado-check` | há simulado na janela de 7d? (política: 1/semana) |
| `--json` | diagnóstico completo em JSON |

**As 4 zonas** (desempenho × cobertura da grade, cortes em 70%/70%):

| | Cobertura baixa | Cobertura alta |
|---|---|---|
| **Desempenho baixo** | `CONTEUDO` — falta base | `RETENCAO` — viu e não reteve; FSRS |
| **Desempenho alto** | `COBERTURA` — acerta o que estudou, falta terreno | `DIRECIONAMENTO` — gargalo é execução |

🔴 **A zona de 1 eixo do vídeo (60-65% = conteúdo, 70-80% = direcionamento) misclassifica quem tem nota de platô SEM ter fechado a grade.** O segundo eixo separa "não sei" de "ainda não vi". Em 25/07 o usuário está em **COBERTURA** (77,6% de acerto, 43% da grade percorrida) — prescrição é **avançar a grade**, não refinar.

🔴 **Variância corre POR FORA da zona.** Desvio >= 10 pp prescreve **simulado** em qualquer quadrante: sensibilidade a perfil de prova não se corrige com mais bloco temático, só com prova inteira e diversa.

🔴 **Cobertura NÃO vem de `taxonomia_cronograma.questoes_realizadas`** — esse campo está inflado (~19.6k contra 5.2k reais em `sessoes_bulk`). Vem da grade versionada + semana de conteúdo. Se um dia a cobertura parecer alta demais, é esse o defeito a suspeitar primeiro.
