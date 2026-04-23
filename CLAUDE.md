---
type: onboarding
layer: root
status: canonical
relates_to: [AGENTE, ESTADO, KNOWLEDGE_ARCHITECTURE]
---

# CLAUDE.md — Agente de Estudo para Residência Médica

## INICIO OBRIGATÓRIO DE SESSÃO

**Leia `AGENTE.md` antes de qualquer ação.** Este arquivo contém o protocolo de boot e a ordem de leitura para garantir a continuidade do projeto.

## Workflows disponíveis

| Tarefa | Workflow |
|---|---|
| Criar resumo de tema | `.agents/workflows/criar-resumo.md` |
| Analisar questões erradas | `.agents/workflows/analisar-questoes.md` |
| Registrar sessão no history | `.agents/workflows/registrar-sessao.md` |
| Gerar flashcards de reforço | `.agents/workflows/gerar-reforco.md` |

## Skills disponíveis (`.claude/commands/`)

| Skill | Função |
|---|---|
| `.claude/commands/estilo-resumo.md` | Padrão de formatação **obrigatório** para resumos |
| `.claude/commands/analisar-questao.md` | Protocolo de análise de questão + invocação do `insert_questao.py` |
| `.claude/commands/extrair-pdf.md` | Wrapper para `extract_pdfs.py` (política Zero PDF) |
| `.claude/commands/auditar-resumos.md` | Linter de qualidade para `resumos/` |
| `.claude/commands/performance.md` | Checagem rápida de performance (questões, metas, custo/Q, áreas fracas) — read-only |

## Scripts em tools/

| Script | Função |
|---|---|
| `tools/extract_pdfs.py` | CLI: extração de PDFs (ver skill `/extrair-pdf`) |
| `tools/insert_questao.py` | CLI: insere erro no `ipub.db` (ver skill `/analisar-questao`) |
| `tools/performance.py` | CLI: relatório de performance em markdown (ver skill `/performance`) |
