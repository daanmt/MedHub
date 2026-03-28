# Session 020 — Workflows Híbridos e Regra Siamese Twins
**Data:** 2026-03-14
**Ferramenta:** Antigravity
**Continuidade:** Sessão 019

---

## O que foi feito
- Criação e aprovação do Plano de Implementação da Fase 2 (Integração DB/Markdown).
- Estabelecida a Regra de Negócio de "Siamese Twins": O banco SQLite e o Caderno de Erros Markdown devem ser obrigatoriamente populados em sincronia a cada nova questão analisada.
- Adicionado o **Passo 6** oficial ao workflow base `analisar-questoes.md`, determinando o input obrigatório via shell script.
- Escrito e validado o CLI Helper `tools/insert_questao.py`, permitindo a injeção cega e segura dos outputs do LLM (questão, alternativa, armadilha, elo) direto nas 4 tabelas fundamentais (incluindo o gerador automático do Card FSRS).

## Artefatos criados/modificados
- `implementation_plan.md`
- `tools/insert_questao.py` (Criado)
- `.agents/workflows/analisar-questoes.md`
- `AGENTE.md`
- `ESTADO.md`
- `HANDOFF.md`
- `history/session_020.md`

## Decisões tomadas
- O fechamento global (`AGENTE.md`) agora inclui obrigatoriedade no comando git para commitar também as atualizações binárias do `.db`.
- Para proteger o banco, LLMs não rodarão queries cruas de INSERT nos loops normais — usarão estritamente o wrapper Python.

## Próximos passos (se houver)
- Realizar a massiva extração ETL (Extract, Transform, Load) das ~67 questões do arquivo de Markdown legado `caderno_erros.md` para o `ipub.db`.
