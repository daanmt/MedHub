# HANDOFF — Ponto de Passagem de Bastão

> **Última atualização:** Sessão 020 (Workflows Híbridos DB/Markdown)

## 📌 Status Atual
- Os workflows principais do projeto e as regras do Agente foram oficialmente transfigurados para a Fase 2 (Híbrida).
- Criada a infraestrutura segura via linha de comando (`insert_questao.py`), permitindo inserir novos inputs diretamente no SQLite sem risco de injection/queries manuais.

## 🚧 Obstáculos / Problemas Atuais
- A Tabela de Questões do banco tem apenas 1 questão de teste populada, enquanto o `caderno_erros.md` contêm 67 registros. O abismo temporal precisa ser fechado o quanto antes para não perdermos a métrica real do FSRS.

## ➡️ Próximo Passo Imediato (próxima sessão)
- Criar script "etl_markdown_to_sqlite.py" com um LLM parser que consegue extrair inteligentemente em lote as 67 "Armadilhas de Prova" do arquivo `.md` e inserir de uma vez só no banco `ipub.db`.
