# Spec: Consolidação do Mecanismo de Conhecimento — Parte 2 (Reconciliação de drift documental)

> Gerado via /vibeflow:gen-spec on 2026-07-12
> PRD: `.vibeflow/prds/mecanismo-conhecimento-consolidacao.md`
> Parte 2 de 3 — docs concordam com o código
> Dependencies: `.vibeflow/specs/mecanismo-conhecimento-consolidacao-part-1.md`

## Objective

Fazer a documentação de governança concordar com o código real, eliminando os quatro drifts doc-vs-realidade que sustentam a percepção de "bagunça" e podem levar um agente a agir sobre informação obsoleta.

## Context

Três das quatro "dores" reportadas eram drift, não falta de mecanismo. Após a Parte 1 remover o MCP obsidian, `AGENTE.md §2 L53` ainda mandaria o agente buscar por ele — contradição com `ROADMAP.md L124` (que já decidiu usar `rag.py`). O header do PRD `pipeline-conhecimento.md` diz "AGUARDA go" quando o ciclo 3 foi implementado e auditado PASS em 2026-07-06. `AUDITORIA_MEDHUB.md L292` e `HANDOFF.md L27` marcam F21 como aberto, mas ele está resolvido em `core/contracts/revisao-calibrada-contract.md v1.2` (Cláusula 10 + Invariante E). E o contador de resumos diverge entre docs (README "44" / ESTADO "66" / HANDOFF "69"); o real é 69.

## Definition of Done

1. `AGENTE.md §2` aponta `app/engine/rag.py` como o único motor de busca semântica; a referência a `mcp__obsidian-notes-rag__search_notes` é removida ou marcada como descontinuada — consistente com `ROADMAP.md L124`.
2. Header de `.vibeflow/prds/pipeline-conhecimento.md` marca **IMPLEMENTADO 2026-07-06** (com ponteiro para os 4 audits PASS), não "AGUARDA go".
3. F21 marcado **RESOLVIDO** em `AUDITORIA_MEDHUB.md` e `HANDOFF.md`, citando `revisao-calibrada-contract.md v1.2` como âncora.
4. O contador de resumos aparece derivado em **um** lugar canônico (runtime, ex.: helper que roda `find`/`glob` sobre `resumos/**/*.md`); os demais docs referenciam esse número ou o descrevem como "derivado", nunca hardcodam um valor divergente.
5. **[qualidade]** Leitura cruzada de `AGENTE.md`, `ROADMAP.md`, `pipeline-conhecimento.md`, `AUDITORIA_MEDHUB.md` e `HANDOFF.md` não revela nenhuma afirmação contraditória sobre: motor de busca, estado do ciclo 3, estado de F21, contagem de resumos.

## Scope

- `AGENTE.md` — §2 (motor de busca) e §6 se referenciar o MCP.
- `ROADMAP.md` — confirmar/consolidar a decisão L124 (não reabrir).
- `.vibeflow/prds/pipeline-conhecimento.md` — header de status.
- `AUDITORIA_MEDHUB.md` — entrada F21.
- `HANDOFF.md` — entrada F21 e contador.
- Um ponto canônico de contagem de resumos (helper existente em `tools/` se houver, ex.: dentro de `cobertura_conhecimento.py` ou `auto_check.py`; senão, uma linha derivada no doc que já roda `find`).

## Anti-scope

- **NÃO** alterar a semântica de nenhuma decisão — só propagar o estado real. F21, ciclo 3 e motor de busca já estão decididos; esta parte só faz os docs refletirem isso.
- **NÃO** reabrir a decisão do MCP (Parte 1 já o removeu; aqui só se atualiza o texto).
- **NÃO** criar novo schema de DB nem coluna para o contador — derivar de `find`, não persistir.
- **NÃO** tocar código de runtime além do helper de contagem (se necessário).

## Technical Decisions

- **Números derivados, nunca digitados** — é o padrão que o próprio MedHub adotou no ciclo 2. O contador de resumos deve ser computado, não escrito à mão; docs que precisam do número descrevem-no como derivado ou apontam para o comando.
- **Marcar histórico, não apagar** — em ledger (`AUDITORIA_MEDHUB.md`, `HANDOFF.md`), F21 vira RESOLVIDO com data e âncora, preservando a trilha; não deletar a entrada.
- **AGENTE.md é contrato** (`patterns/agent-workflow-protocol.md`) — a mudança em §2 muda o comportamento de busca de todo agente futuro; redação inequívoca.

## Applicable Patterns

- `patterns/agent-workflow-protocol.md` — AGENTE.md como contrato de sessão.
- `conventions.md` — números derivados, pt-BR.

## Risks

- **Risco**: editar `AGENTE.md` antes de a Parte 1 remover o MCP deixa uma janela onde o doc diz `rag.py` mas o hook ainda reindexa o obsidian. → Mitigação: `Dependencies` força Parte 1 antes.
- **Risco**: o contador derivado conta arquivos legados (`[GIN]`/stubs) e diverge do "conceito" de resumo ativo. → Mitigação: definir explicitamente o que conta (todos os `.md` sob `resumos/`, ou só `status: active`) e documentar a escolha junto ao helper.
