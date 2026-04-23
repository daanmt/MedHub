# PRD: /performance — Checagem rápida de performance MedHub

> Generated via /vibeflow:discover on 2026-04-23

## Problem

Consultar a performance acumulada (questões feitas, acertos, distância da meta mensal, ritmo necessário, áreas fracas) hoje é **ad-hoc**: requer escrever um bloco Python inline com SQL direto no `ipub.db`. Isso é lento, propenso a erro (na própria sessão 071 a query falhou na primeira tentativa por usar o nome de coluna errado — `acertos` em vez de `questoes_acertadas`), e não padroniza o formato do relatório entre sessões.

O usuário tem metas mensais cumulativas bem definidas (3.000 → 4.500 → 6.250 → ... → 23.000 entre mar/2026 e dez/2026) e precisa saber, a qualquer momento: onde está, quanto falta até a meta do mês corrente, qual ritmo diário mínimo para fechar o mês, e quais áreas precisam de atenção. A ausência desse comando reutilizável custa ~60 segundos e um bug toda vez que a informação é pedida.

## Target Audience

Usuário único — proprietário do projeto MedHub (estudante de residência médica). Uso em sessões Claude Code durante a preparação.

## Proposed Solution

Skill `/performance` que executa um script `tools/performance.py`. O script consulta `ipub.db` (tabela `sessoes_bulk`), cruza com uma tabela de metas mensais hardcoded no próprio script, e imprime em markdown um relatório estruturado. O Claude complementa a saída com uma recomendação estratégica baseada nos números (2–4 linhas).

## Success Criteria

1. Comando `/performance` retorna o relatório completo em < 3 segundos.
2. O relatório informa, sem necessidade de query adicional:
   - Total acumulado de questões e acertos (% geral).
   - **Mês corrente:** meta do mês, quanto falta, ritmo diário necessário até o fim do mês.
   - **Custo/questão** em duas dimensões (acumulado + mês corrente), classificado em faixa visual, com distância da meta final (R$ 0,10 em dez/2026).
   - **Próximos marcos:** distância até ENARE (out/2026 = 17.000) e meta final (dez/2026 = 23.000).
   - Áreas com performance < 75% (alerta).
   - Áreas com 0 questões (gaps absolutos).
3. Zero erros de coluna/schema — o script deve ser a única fonte operacional dessa query.
4. Atualização das metas requer editar **apenas o dicionário `METAS_MENSAIS` no topo do script** (uma única edição).

## Scope v0

1. Script `tools/performance.py`:
   - Argparse sem flags obrigatórias (opcional: `--area <nome>` para drill-down individual — **fora do v0**).
   - `METAS_MENSAIS` hardcoded no topo (dict `{"YYYY-MM": {"meta_acumulada": int, "investimento": float}}`).
   - `FAIXAS_CUSTO` hardcoded no topo (lista ordenada de tuplas `(limite_superior, emoji, rótulo)`).
   - `META_CUSTO_Q = 0.10` (alvo dez/2026).
   - Cálculo do mês corrente via `datetime.now()`.
   - 5 blocos de output em markdown: (1) Total acumulado; (2) Meta do mês + ritmo; (3) Custo/questão (acumulado + mês corrente + faixa + distância da meta R$ 0,10); (4) Marcos adiante (ENARE, Final); (5) Áreas fracas e gaps.
2. Skill `.claude/commands/performance.md`:
   - Frontmatter padrão (description, type, layer, status).
   - Instrução para Claude: executar `python tools/performance.py` e complementar com análise estratégica breve (2–4 linhas) baseada no relatório.
3. Atualização pontual de `ESTADO.md` e `CLAUDE.md` apontando para a nova skill.

## Anti-scope

- **Não** ler metas de `ESTADO.md`, JSON externo ou tabela nova no DB — fica hardcoded no script.
- **Não** incluir "áreas fortes" no relatório (não aciona decisão).
- **Não** incluir "últimas sessões" no relatório (já reportado por `registrar_sessao_bulk.py` e `ESTADO.md`).
- **Não** calcular custo/questão histórico por mês individual anterior (apenas acumulado + mês corrente).
- **Não** gerar projeção de custo/Q até dezembro nem curva de evolução — apenas snapshot.
- **Não** gerar gráficos, CSVs ou arquivos de saída — apenas stdout em markdown.
- **Não** implementar flag `--area` nem filtros por data no v0.
- **Não** criar testes automatizados (script de leitura simples, baixo risco).
- **Não** modificar schema do DB.

## Technical Context

### Padrões do projeto aplicáveis (de `.vibeflow/conventions.md` e CLAUDE.md)

- **Acesso a DB em tools/:** scripts standalone em `tools/` podem usar `import sqlite3` diretamente (exceção explícita à regra de centralização em `db.py`). Padrão usado por `insert_questao.py` e `registrar_sessao_bulk.py`.
- **CLI pattern:** `argparse`, DB path via `os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')`, `try/finally: conn.close()`.
- **Skill pattern:** arquivo `.md` em `.claude/commands/` com frontmatter `description/type/layer/status`. Usar `extrair-pdf.md` como referência estrutural.
- **Language:** todo output em pt-BR. Termos técnicos em inglês são aceitáveis.

### Dados já disponíveis

Tabela `sessoes_bulk` (schema verificado):
```
id, sessao_num, area, questoes_feitas, questoes_acertadas, data_sessao, observacoes
```

Query central do v0:
```sql
SELECT SUM(questoes_feitas), SUM(questoes_acertadas) FROM sessoes_bulk;
SELECT area, SUM(questoes_feitas), SUM(questoes_acertadas)
  FROM sessoes_bulk GROUP BY area ORDER BY SUM(questoes_feitas) DESC;
```

### Tabela de metas (a hardcodar no script)

| Mês | Meta acumulada | Investimento (R$) |
|---|---:|---:|
| 2026-03 | 3.000 | 2.310,00 |
| 2026-04 | 4.500 | 2.520,00 |
| 2026-05 | 6.250 | 2.940,00 |
| 2026-06 | 8.000 | 3.150,00 |
| 2026-07 | 10.000 | 3.360,00 |
| 2026-08 | 12.500 | 3.570,00 |
| 2026-09 | 15.000 | 3.780,00 |
| 2026-10 | 17.000 | 3.990,00 |
| 2026-11 | 20.000 | 4.200,00 |
| 2026-12 | 23.000 | 4.410,00 |

Marcos especiais: ENARE = 2026-10 (17.000); Final = 2026-12 (23.000).

### Faixas de custo/questão (a hardcodar no script)

| Faixa | Limite | Emoji | Rótulo |
|---|---|:---:|---|
| Meta | ≤ R$ 0,10 | 🟢 | Meta (dez/2026) |
| Ótimo | R$ 0,10 – 0,20 | 🟡 | Ótimo |
| Bom | R$ 0,20 – 0,30 | 🟠 | Bom |
| Alto | R$ 0,30 – 0,50 | 🔴 | Alto |
| Crítico | > R$ 0,50 | 🟣 | Crítico |

Alvo: **R$ 0,10/questão em dez/2026**. O script deve exibir o custo/Q acumulado (soma investimento até mês corrente ÷ total de questões) e o custo/Q do mês corrente (investimento do mês ÷ questões feitas no mês — via filtro `data_sessao`), classificando cada um na faixa correspondente.

### Cálculos

O valor na coluna `investimento` de `METAS_MENSAIS` **já é cumulativo** (não é a parcela do mês — é o total investido da entrada da série até o fim daquele mês). A parcela do mês é derivada por diferença entre meses consecutivos.

```
investimento_acumulado = METAS_MENSAIS[mes_atual]["investimento"]
parcela_mes_atual      = METAS_MENSAIS[mes_atual]["investimento"]
                       - METAS_MENSAIS[mes_anterior]["investimento"]

custo_q_acumulado      = investimento_acumulado / total_questoes
custo_q_mes            = parcela_mes_atual / questoes_no_mes_atual
```

Observação: a parcela mensal é ≈ R$ 210, com exceção de maio/2026 que salta +R$ 420 (refletido na diferença entre as linhas 04 e 05 da tabela). Não há necessidade de tratar isso como caso especial — a subtração do acumulado anterior captura a parcela correta automaticamente.

Edge case: se o mês corrente for **o primeiro mês da série** (2026-03), não existe mês anterior em `METAS_MENSAIS`. Nesse caso, tratar `parcela_mes_atual = METAS_MENSAIS["2026-03"]["investimento"]` (pode superestimar o custo do mês individual porque o valor inclui investimentos anteriores à série — aceitável no v0; o custo/Q acumulado permanece correto).

Onde `questoes_no_mes_atual` é:
```sql
SELECT SUM(questoes_feitas) FROM sessoes_bulk
 WHERE strftime('%Y-%m', data_sessao) = :mes_atual
```

### Integração com fluxo existente

Skill invocável a qualquer momento na sessão. Não tem side effects (leitura pura). Não precisa entrar no boot de `AGENTE.md` nem no fechamento de sessão. Apenas mencionada em `CLAUDE.md` como skill disponível.

## Open Questions

None.
