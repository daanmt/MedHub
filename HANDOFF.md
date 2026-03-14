# HANDOFF — Ponto de Passagem de Bastão

> **Última atualização:** Sessão 019 (Infraestrutura Relacional DB e FSRS)

## 📌 Status Atual
- Foi instanciado o banco base `ipub.db` via `init_db.py` mapeando as 5 tabelas centrais (`taxonomia_cronograma`, `questoes_erros`, `flashcards`, `fsrs_cards`, `fsrs_revlog`).
- O `roadmap.md` amadurecido especifica de forma tática o DSR de estabilidade e o banimento de learning steps nativos seguindo as recomendações oficiais do Open Spaced Repetition.

## 🚧 Obstáculos / Problemas Atuais
- Entrar na fase de migração de dados puros: Necessário extrair em lote o antigo markdown `caderno_erros.md` da Fase 1 e fazer injeção (INSERT SQL) dessas 67 entradas preenchendo as chaves estrangerias certas das novas tabelas.

## ➡️ Próximo Passo Imediato (próxima sessão)
- Criar script "etl_markdown_to_sqlite.py" que faz parsing do arquivo de erros atual convertendo texto estruturado em chaves primárias dentro da tabela `questoes_erros`.
