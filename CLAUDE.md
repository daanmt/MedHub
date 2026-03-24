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

## Arquivos críticos em Tools/

| Arquivo | Função |
|---|---|
| `Tools/estilo-resumo.md` | Padrão de formatação **obrigatório** para resumos |
| `Tools/comando de analise de questao.md` | Protocolo de análise de questão (9 etapas) |
| `Tools/extract_pdfs.py` | Script de extração de PDFs (CLI genérica) |
| `Tools/insert_questao.py` | CLI: insere erro no `ipub.db` (SSOT de erros) |
