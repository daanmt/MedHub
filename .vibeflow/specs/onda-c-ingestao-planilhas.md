# Spec: Onda C — Ingestão de Planilhas via Google Workspace MCP

> Gerado via /vibeflow:gen-spec em 2026-06-03
> ROADMAP.md Linha Evolutiva 8 (MedHub Agent-First)

## Objective

Permitir que o agente ingira o volume de questões das planilhas do Google (lidas via Google Drive MCP) e registre em `sessoes_bulk`, substituindo a extração manual de `.xlsx`.

## Context

Hoje o volume entra via `tools/registrar_sessao_bulk.py` chamado manualmente, e o histórico veio de uma migração one-shot de `dashboard-emed.xlsx` (extração manual). As planilhas vivem na conta Google do usuário. Com o Google Drive MCP (claude.ai connector), o agente pode ler a planilha e popular o banco — coerente com a tese agent-first (o agente lê/interpreta, o código persiste). `registrar()` já existe (idempotente, valida `acertos<=feitas`, conhece `AREAS_VALIDAS`).

## Definition of Done

1. `tools/importar_sessoes.py --rows-file <json>`: lê um JSON com lista de linhas `[{sessao, area, feitas, acertos, data?, obs?}]` e chama `registrar()` (de `registrar_sessao_bulk.py`) para cada uma — **sem reimplementar** a lógica de persistência. Imprime resumo: inseridas / puladas / inválidas.
2. Valida cada linha: `area` ∈ `AREAS_VALIDAS` e `acertos <= feitas`; linha inválida é **reportada e pulada** (não aborta o lote).
3. Idempotência preservada: `registrar()` já pula duplicatas `(sessao, area)`; o resumo distingue **inseridas** de **puladas (já existentes)**.
4. Skill `.claude/commands/importar-planilha.md` documenta o fluxo agêntico: (a) autenticar Google Drive via `/mcp`; (b) ler a planilha via Drive MCP; (c) mapear colunas → `{sessao, area, feitas, acertos}`; (d) normalizar a área para `AREAS_VALIDAS`; (e) gravar via `importar_sessoes.py --rows-file`; (f) reportar ao usuário.
5. **(Quality)** `importar_sessoes.py` segue convenções de CLI (argparse, saída UTF-8, importa `registrar` de `registrar_sessao_bulk` — sem `import sqlite3` novo); skill em pt-BR com frontmatter; assinatura do CLI documentada em **uma** skill (§7.2).
6. Teste: JSON com 2 linhas válidas + 1 inválida (área desconhecida) → 2 inseridas, 1 reportada como inválida; re-rodar → 2 puladas (idempotência). Verificado com cleanup (sem poluir `sessoes_bulk`).

## Scope

- `tools/importar_sessoes.py` (novo) — importador em lote a partir de JSON, wrapper sobre `registrar()`.
- `.claude/commands/importar-planilha.md` (novo) — skill do fluxo agêntico de ingestão.

## Anti-scope

- A **leitura real** da planilha no Google Drive (é agent-driven em runtime, depende do OAuth do MCP que o usuário completa via `/mcp`).
- Conectar/automatizar o OAuth (interativo, fora do código).
- FSRS, flashcards, Streamlit, dashboard.
- Mudança de schema (`sessoes_bulk` inalterado).
- Reimplementar `registrar()` ou tocar `registrar_sessao_bulk.py`.

## Technical Decisions

- **`importar_sessoes.py` reusa `registrar()`** (import de `registrar_sessao_bulk`) — caminho único de escrita, idempotência e validação herdadas; o CLI só orquestra o lote + resumo.
- **JSON via `--rows-file`** (mesmo padrão de `--cards-file` da Onda B): o agente escreve as linhas mapeadas em arquivo e passa o path; evita quoting/unicode do PowerShell.
- **Mapeamento de colunas é do agente** (skill), pois varia por planilha; o CLI valida contra `AREAS_VALIDAS` e reporta o que não casar — a normalização de nomes de área é responsabilidade do agente antes de gravar.
- **Read da planilha = agente via MCP**; código só persiste (agent-first).

## Applicable Patterns

- `db-access-layer.md` — persistência via a função canônica (`registrar`), sem `sqlite3` novo no importador.
- `agent-workflow-protocol.md` — fluxo documentado como skill (§7.2); o agente orquestra MCP→mapeamento→CLI.

## Risks

- **OAuth do Google Drive pendente** (runtime) → a skill instrui `/mcp`; o caminho determinístico (importador) é testável e fica pronto independentemente.
- **Estrutura de planilha varia** → mapeamento de colunas fica na skill (responsabilidade do agente); o CLI valida e reporta linhas inválidas em vez de abortar.
- **Nomes de área divergentes** (ex.: "GO" vs "Ginecologia") → o agente normaliza para `AREAS_VALIDAS`; linhas não-normalizadas são reportadas, não gravadas erradas.

## Dependencies

Nenhuma dependência de código. **Runtime:** o usuário autentica o Google Drive MCP via `/mcp` para o live read.
