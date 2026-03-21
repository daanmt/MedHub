---
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

## Artefatos criados/modificados
- [Lista de arquivos com paths relativos]

## Decisões tomadas
- [Decisões importantes para contexto futuro]

## Próximos passos (se houver)
- [O que ficou pendente]
```

### 3. Atualizar ESTADO.md
Adicionar entrada na seção "Últimas sessões" do `ESTADO.md` com resumo de uma linha.

### 4. Sincronização Autônoma do RAG (Obrigatório)
Rodar o comando de indexação local do Obsidian para garantir que a IA tenha acesso imediato a todas as atualizações na próxima sessão:
```powershell
obsidian-notes-rag index
```
- *Nota: Este passo garante a "amnésia zero" para o banco vetorial do projeto e mantém a funcionalidade MCP global sempre atualizada.*
