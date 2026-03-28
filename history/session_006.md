# Session 006 — Eliminação de Extracted/ e Limpeza Automática Pós-Resumo
**Data:** 2026-03-05
**Ferramenta:** Antigravity
**Continuidade:** Sessão 005

---

## O que foi feito

- Deletada pasta `Extracted/` e seus 9 arquivos (entulho de extrações anteriores)
- Reescrito `tools/extract_pdfs.py`: extração agora vai para pasta temp do sistema (`%TEMP%`), não para `Extracted/`
- Adicionado `--delete-pdfs <pasta>`: deleta todos os PDFs da pasta indicada
- Adicionado `--delete-temps <paths...>`: deleta arquivos `.txt` temporários de extração
- Atualizado `.agents/workflows/criar-resumo.md` com passo 7 de limpeza automática
- Removida entrada `Extracted/` do `.gitignore` (pasta extinta)
- Atualizado `ESTADO.md` com novo fluxo e decisões críticas

## Artefatos criados/modificados

- `tools/extract_pdfs.py` (reescrito)
- `.agents/workflows/criar-resumo.md` (atualizado)
- `.gitignore` (entrada Extracted/ removida)
- `ESTADO.md` (atualizado)
- `history/session_006.md` (este arquivo)

## Decisões tomadas

- Extrações são efêmeras: vão para `%TEMP%` e devem ser deletadas ao final do workflow
- PDFs da pasta do tema também são deletados automaticamente pelo script após o resumo ser consolidado
- O agente nunca deve criar scripts ad hoc de extração — usar `extract_pdfs.py` diretamente

## Próximos passos

- Retomar análise de questões de Asma
