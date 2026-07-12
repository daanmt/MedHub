# Spec: Consolidação do Mecanismo de Conhecimento — Parte 3 (Robustez e visibilidade)

> Gerado via /vibeflow:gen-spec on 2026-07-12
> PRD: `.vibeflow/prds/mecanismo-conhecimento-consolidacao.md`
> Parte 3 de 3 — comportamento novo, mínimo e aditivo
> Dependencies: `.vibeflow/specs/mecanismo-conhecimento-consolidacao-part-1.md`

## Objective

Dar continuidade ao mecanismo quando a infra falha (fallback textual no engine quando Ollama/Chroma estão offline) e tornar o débito de cobertura impossível de ignorar (WARN quando o tema da semana não tem `.md` canônico) — sem destilar conteúdo.

## Context

`app/engine/rag.py.search()` retorna `[]` se Ollama ou Chroma estão indisponíveis; só a UI Streamlit degrada para `os.walk`, mas um agente que chama o engine fica cego. A lógica de busca textual já existe em `app/engine/get_topic_context.py` (índice `{termo→path}` via rglob + `path.stem` + frontmatter + difflib) — é wiring, não construção. Separadamente, ~274 dos 343 PDFs de fonte (80%) nunca viraram `.md` canônico; `tools/cobertura_conhecimento.py` já cruza PDFs×md e prioriza órfãos, mas o gap não aparece no fluxo diário. Tornar o débito visível (sem autorá-lo) é o lado-ferramenta legítimo de R4; a destilação em si é trabalho de conteúdo do operador, fora de escopo.

## Definition of Done

1. Com Ollama parado (ou Chroma ausente), `app/engine/rag.py.search()` retorna resultados textuais relevantes por tema (reusando a lógica de `get_topic_context.py`) em vez de `[]`, e marca o resultado como `source=fallback_textual` para o consumidor distinguir.
2. O caminho semântico normal (Ollama vivo) é **inalterado** — o fallback só ativa em falha; verificável por teste que força a exceção/indisponibilidade.
3. `tools/auto_check.py --all` emite um WARN (não erro, não bloqueia) quando o tema da semana corrente do cronograma não tem `.md` canônico correspondente, com o ranking de rendimento vindo de `cobertura_conhecimento.py`.
4. O WARN é silencioso quando há cobertura (nenhum falso positivo para tema já coberto).
5. **[qualidade]** `pytest` verde; o fallback e o WARN têm teste cada; `import sqlite3` só em `db.py`; retorno do engine permanece estruturado (`dict`/`dataclass`, nunca string livre) conforme `domain-engine-api.md`.

## Scope

- `app/engine/rag.py` — fallback textual em `search()` (e/ou `search_two_tier()`), reusando o índice de `get_topic_context.py`.
- `app/engine/get_topic_context.py` — expor/compartilhar a função de índice textual se necessário (refactor mínimo, sem mudar contrato).
- `tools/auto_check.py` — chamar a checagem de cobertura no `--all` e emitir WARN.
- `tools/cobertura_conhecimento.py` — reusar o ranking existente; expor a checagem "tema da semana tem `.md`?" se ainda não houver.

## Anti-scope

- **NÃO** destilar PDF em `.md` — o WARN só sinaliza; a autoria é do operador.
- **NÃO** mudar o ranking de rendimento já existente em `cobertura_conhecimento.py` (só consumi-lo).
- **NÃO** tornar o WARN bloqueante (é sinal, não gate) — `auto_check` não deve falhar por cobertura ausente.
- **NÃO** alterar o caminho semântico quando a infra está viva.
- **NÃO** adicionar embeddings/modelo/dep para o fallback — é lexical puro.
- **NÃO** cachear novos artefatos; o fallback lê `resumos/` direto.

## Technical Decisions

- **Reuso > reconstrução**: o fallback não inventa busca textual — importa a lógica de `get_topic_context.py`. Se isso exigir extrair a função para um ponto compartilhável, é refactor mínimo com contrato preservado.
- **Marcar a proveniência**: `source=fallback_textual` no retorno, análogo ao `source=pdf_raw` do two-tier — o agente sempre sabe se o resultado é semântico curado, bruto, ou degradado.
- **WARN, não erro**: cobertura ausente é débito conhecido, não falha; poluir o exit code de `auto_check` com isso quebraria o pre-commit. Sinal visível, fluxo não interrompido.
- **Cache do índice de resumos em memória do processo** (limitação conhecida em `get_topic_context.py`): fora do v0 — registrar como follow-up se o fallback expuser o problema; não aumentar o blast radius agora.

## Applicable Patterns

- `patterns/domain-engine-api.md` — retorno estruturado, contrato estável, tratamento de not-found explícito.
- `patterns/db-access-layer.md` — se tocar dados, via `db.py`.
- `conventions.md` — pt-BR, flat, `sqlite3` só em `db.py`.

## Risks

- **Risco**: o fallback textual retorna resultados de qualidade inferior e o agente não percebe. → Mitigação: `source=fallback_textual` obrigatório no retorno (DoD #1); documentar que fallback ≠ curado.
- **Risco**: extrair a função de índice de `get_topic_context.py` quebra seu contrato atual. → Mitigação: refactor com o teste existente de `get_topic_context` como rede; contrato preservado (DoD #5).
- **Risco**: o WARN de cobertura gera ruído em toda sessão e vira decoração ignorada. → Mitigação: só dispara para o tema da semana corrente sem `.md` (não para todos os 274 órfãos); silencioso quando coberto (DoD #4).
- **Risco**: "tema da semana" depende da grade do cronograma, que pode estar dessincronizada. → Mitigação: se a grade não resolver o tema, o WARN não dispara (degrada para silêncio, não para falso positivo).
