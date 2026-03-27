---
type: workflow
layer: agents
status: canonical
description: Registrar sessão no history ao final do trabalho
---

# Workflow: Registrar Sessão

## Quando usar
Ao final de qualquer sessão de trabalho significativa (criação de resumo, análise de questões, refatoração).

## Passos

### 1. Identificar o próximo número
Criar `history/session_NNN.md` seguindo o protocolo de fechamento do `AGENTE.md`.

### 2. Criar o session log
Criar `history/session_NNN.md` com o seguinte formato:

```markdown
# Session NNN — [Título descritivo]
**Data:** YYYY-MM-DD
**Ferramenta:** [Antigravity / Claude Code / Gemini / etc.]
**Continuidade:** Sessão NNN-1 (se aplicável)

---

## O que foi feito
- [Lista de ações realizadas]

## Padrões de erro identificados (se sessão de questões)
- [Áreas com erros recorrentes e elo quebrado]

## Artefatos criados/modificados
- [Lista de arquivos com paths relativos]

## Decisões tomadas
- [Decisões importantes para contexto futuro]

## Próximos passos (se houver)
- [O que ficou pendente]
```

### 3. Atualizar ESTADO.md
Adicionar entrada na seção "Últimas sessões" do `ESTADO.md` com resumo de uma linha.

### 4. Sincronização Autônoma do RAG (Automático)
Disparado automaticamente pelo hook `PostToolUse(Write)` quando `history/session_NNN.md` é criado.
Fallback manual (se o hook falhar): `mcp__obsidian-notes-rag__reindex(clear=False)`

### 5. Consolidação de Memória Longa (Automático — Memory v1)
Disparado automaticamente em background pelo hook `PostToolUse(Write)` quando `history/session_NNN.md` é criado.
Fallback manual (se o hook falhar):
```powershell
python -m app.memory.manager <NNN>
```
Onde `<NNN>` é o número da sessão recém-registrada (e.g., `048`).
