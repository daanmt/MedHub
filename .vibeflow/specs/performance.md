# Spec: /performance — Checagem rápida de performance MedHub

> Generated via /vibeflow:gen-spec on 2026-04-23
> Source PRD: `.vibeflow/prds/performance.md`

## Objective

Permitir ao usuário obter, em < 3 segundos e com um único comando (`/performance`), um relatório markdown estruturado em 5 blocos sobre seu progresso rumo às metas mensais de preparação para residência médica — substituindo a query ad-hoc que falhou uma vez neste projeto por erro de nome de coluna.

## Context

- **Existe hoje:**
  - `ipub.db` (SQLite local) com tabela `sessoes_bulk` populada (~3.130 questões em 20+ áreas).
  - `tools/registrar_sessao_bulk.py` — padrão de CLI standalone com `sqlite3` direto.
  - `tools/insert_questao.py` — padrão de CLI com argparse e `try/finally`.
  - `.claude/commands/extrair-pdf.md` — padrão estrutural de skill markdown.
  - Metas mensais cumulativas (mar/2026 → dez/2026) e faixas de custo/Q definidas no PRD.
- **Não existe:** nenhum consumidor read-only dessa tabela para análise de performance. A página `1_dashboard.py` faz consulta via UI, mas não cobre o caso de uso "checagem rápida na conversa com Claude".
- **Por que agora:** na sessão 071 a query ad-hoc falhou por usar `acertos` em vez de `questoes_acertadas` — sinal claro de que vale encapsular.

## Definition of Done

1. **Executável:** `python tools/performance.py` roda sem erro, sem flags obrigatórias, e imprime em stdout um relatório markdown com 5 blocos na ordem definida no scope.
2. **Bloco 1 (Total acumulado):** mostra `total_questões`, `total_acertos`, `performance_%` computados via `SELECT SUM(questoes_feitas), SUM(questoes_acertadas) FROM sessoes_bulk`.
3. **Bloco 2 (Meta do mês + ritmo):** mostra meta cumulativa do mês corrente (de `METAS_MENSAIS`), déficit (meta − total), ritmo diário necessário (`déficit ÷ dias_restantes_no_mês` via `calendar.monthrange`). Se `déficit ≤ 0` → mostra "meta atingida" em vez de ritmo.
4. **Bloco 3 (Custo/questão):** mostra `custo_q_acumulado` e `custo_q_mes` em duas linhas, cada uma classificada na faixa correta com emoji+rótulo (de `FAIXAS_CUSTO`) e distância absoluta até `META_CUSTO_Q = 0.10`. Parcela do mês calculada como `METAS_MENSAIS[mes_atual] - METAS_MENSAIS[mes_anterior]` (com fallback documentado se `mes_atual` for o primeiro da série).
5. **Bloco 4 (Marcos adiante):** mostra distância em questões até ENARE (17.000) e Final (23.000).
6. **Bloco 5 (Áreas fracas + gaps):** lista todas áreas com `questoes_feitas > 0 AND %acerto < 75` ordenadas por pior performance; em linha separada, lista áreas de `AREAS_VALIDAS` (importada de `registrar_sessao_bulk.py` ou replicada) que não aparecem em `sessoes_bulk` (zero questões).
7. **Craftsmanship:** script segue `.vibeflow/patterns/db-access-layer.md` (authorized CLI exception) — `DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipub.db')`, `try/finally: conn.close()`, queries parametrizadas (zero f-strings em SQL), sem `import pandas`, e skill `.claude/commands/performance.md` com frontmatter `description/type/layer/status` espelhando `extrair-pdf.md`.

## Scope

- Criar `tools/performance.py` (~150 linhas Python stdlib) com:
  - Constantes topo: `METAS_MENSAIS`, `FAIXAS_CUSTO`, `META_CUSTO_Q = 0.10`, `AREAS_VALIDAS`.
  - Função `get_totais(conn)` → `(total_q, total_a)`.
  - Função `get_por_area(conn)` → lista ordenada de `(area, q, a, pct)`.
  - Função `get_questoes_do_mes(conn, mes_yyyy_mm)` → `int`.
  - Função `classificar_custo(valor)` → `(emoji, rotulo)` usando `FAIXAS_CUSTO`.
  - Função `formatar_relatorio(...)` → `str` markdown.
  - `main()` com `argparse` (sem flags obrigatórias), orquestração das queries e `print(relatorio)`.
- Criar `.claude/commands/performance.md` com:
  - Frontmatter canônico.
  - Instrução ao Claude: rodar `python tools/performance.py`, ler saída, complementar com 2–4 linhas de análise estratégica (ex.: priorizar área fraca X, ajustar ritmo para Y).
- Edit `ESTADO.md` (mapa de artefatos): adicionar linha `| Checagem de performance | tools/performance.py |`.
- Edit `CLAUDE.md` (seção Skills disponíveis): adicionar linha apontando para `.claude/commands/performance.md`.

## Anti-scope

- **Não** adicionar flags de filtro (`--area`, `--mes`, `--json`) no v0.
- **Não** usar pandas — stdlib é suficiente e mantém consistência com `registrar_sessao_bulk.py`.
- **Não** criar testes automatizados (script de leitura simples, baixo risco).
- **Não** calcular projeções futuras (ex.: "em que dia você chega a 23.000 no ritmo atual") — snapshot apenas.
- **Não** mostrar custo/Q por mês histórico individual (apenas acumulado + mês corrente).
- **Não** mostrar áreas fortes, últimas sessões, gráficos, CSVs — anti-scope herdado do PRD.
- **Não** modificar `app/utils/db.py` nem o schema de `sessoes_bulk`.
- **Não** usar `obsidian-notes-rag`, ChromaDB, Ollama ou qualquer serviço externo.

## Technical Decisions

### 1. Stdlib-only (sqlite3 + datetime + calendar) em vez de pandas

Trade-off: pandas seria mais confortável para agrupamento, mas:
- `registrar_sessao_bulk.py` (padrão vizinho do projeto) não usa pandas.
- 5 queries, nenhuma com > 30 linhas de resultado — overhead de pandas não se justifica.
- Import-time de pandas é ~300ms; com stdlib o script fica < 100ms.
- Faz o DoD #1 (< 3s) trivial em vez de apenas confortável.

### 2. `AREAS_VALIDAS` replicado em `performance.py` (não importado)

Trade-off: importar de `registrar_sessao_bulk.py` evitaria duplicação, mas:
- `tools/` não tem `__init__.py` — import de sibling é frágil (depende de cwd).
- Os dois scripts são standalone por design (pattern `db-access-layer.md`).
- 20 strings é uma duplicação aceitável em troca de zero acoplamento.
- Alternativa superior seria extrair uma `constants.py` em `tools/`, mas isso infla o budget e foge do escopo do v0.

### 3. Queries parametrizadas via `cursor.execute(..., params)`

Trade-off: interpolação f-string seria mais simples para a única query dinâmica (filtro por mês), mas:
- Convenção do projeto (`db-access-layer.md` Rules) proíbe string interpolation em SQL.
- `strftime('%Y-%m', data_sessao) = ?` com `(mes_atual,)` é uma linha a mais e zero risco.

### 4. Edge case: mês corrente fora da série `METAS_MENSAIS`

Decisão: se `datetime.now().strftime('%Y-%m')` não estiver em `METAS_MENSAIS`, o script imprime um aviso no lugar dos blocos 2 e 3 e segue com os blocos 1, 4, 5. Motivo: degradação graciosa é melhor que erro — o script continua útil em jan/2027 mesmo sem atualização.

### 5. Edge case: total de questões = 0

Decisão: `custo_q_acumulado` exibido como "N/A (0 questões)". Mesmo para `custo_q_mes` se `questoes_no_mes = 0`. Evita `ZeroDivisionError` sem complicar o fluxo.

### 6. Emojis no output

Emojis (🟢🟡🟠🔴🟣) são parte do PRD. Risco de mau rendering em PowerShell já observado neste projeto (`insert_questao.py` imprime `quest�o`), mas no contexto de uso (stdout do Claude Code, terminal UTF-8) renderizam corretamente. Aceito sem mitigação extra — se quebrar em ambiente específico, fix é posterior.

### 7. Skill `.claude/commands/performance.md` como wrapper instrucional

A skill **não** duplica lógica — só instrui Claude a rodar o script e complementar com 2–4 linhas de leitura estratégica da saída. Padrão igual ao `extrair-pdf.md`. Isso mantém a lógica em um só lugar (o script) e permite evolução independente do "coaching layer".

## Applicable Patterns

- **[db-access-layer.md](../patterns/db-access-layer.md)** — standalone CLI exception. Seguir `DB_PATH`, `try/finally: conn.close()`, queries parametrizadas. O script é read-only; não precisa `conn.commit()`.
- **[error-insertion-pipeline.md](../patterns/error-insertion-pipeline.md)** — não se aplica diretamente (sem writes), mas fornece o blueprint estrutural de script CLI em `tools/` (argparse, DB_PATH, exit codes, prints de status).
- **[agent-workflow-protocol.md](../patterns/agent-workflow-protocol.md)** — não se aplica diretamente (skill de leitura, não altera estado de sessão).

Nenhum padrão novo introduzido. Nenhum conflito com convenções existentes.

## Risks

| Risco | Mitigação |
|---|---|
| **Query falha por schema** (ex.: `sessoes_bulk` renomeada no futuro) | DoD #7 exige queries parametrizadas; mudança de schema explode teste manual do DoD #1. Baixo risco — a tabela é SSOT e tem > 3.000 linhas. |
| **Mês corrente sai da série `METAS_MENSAIS`** (ex.: rodar em jan/2027) | Decisão técnica #4: degradação graciosa com aviso, blocos 1/4/5 continuam. |
| **Divisão por zero** (sem questões registradas) | Decisão técnica #5: guard explícito retorna "N/A". |
| **Emoji mal renderizado em algum terminal** | Aceito como trade-off; ambiente real de uso é Claude Code stdout, UTF-8 garantido. |
| **Parcela do mês incorreta na primeira linha da série (2026-03)** | Documentado no PRD e script: `parcela_mes = METAS_MENSAIS[mes_atual]["investimento"]` diretamente (superestima custo/Q do mês, mas acumulado permanece correto). Aceito no v0. |
| **Drift entre `AREAS_VALIDAS` dos dois scripts** | Baixo — lista de 20 especialidades estável; se surgir área nova, basta editar nos dois locais. Próximo refactor (v1+) pode extrair para `tools/_constants.py`. |
| **Usuário esquece de atualizar `METAS_MENSAIS`** após 12/2026 | Aceito — comportamento degradado já coberto (decisão #4); fora do escopo automatizar. |

## Dependencies

Nenhuma — spec autocontida em 4 arquivos.
