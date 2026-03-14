# HANDOFF — Ponto de Passagem de Bastão

> **Última atualização:** Sessão 021 (Arquitetura Machine Learning FSRS)

## 📌 Status Atual
- A inteligência do **FSRS Optimizer** foi incorporada ao ROADMAP. A arquitetura reflete que o PyTorch processará os datasets de séries temporais da nossa tabela `fsrs_revlog` para aplicar Estimativa de Máxima Verossimilhança (MLE) periodicamente.
- O sistema dual (Scheduler diário vs Optimizer periódico) foi mapeado como o Santo Graal do nosso motor de flashcards.

## 🚧 Obstáculos / Problemas Atuais
- A Tabela de Questões do banco tem apenas 1 questão de teste populada, enquanto o `caderno_erros.md` contêm 67 registros críticos. Precisamos dessa massa de dados para o ML funcionar.

## ➡️ Próximo Passo Imediato (próxima sessão)
- Criar script "etl_markdown_to_sqlite.py" com um LLM parser para extrair as 67 questões de forma autônoma e populá-las no SQLite de uma vez só.
