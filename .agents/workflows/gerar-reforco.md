---
type: workflow
layer: agents
status: canonical
description: Gerar flashcards dinâmicos via MCP baseados nos piores tópicos do Cronograma
---

### 1. Identificar o Alvo (Tema mais Crítico)
Descubra qual é a fraqueza atual do usuário consultando a tabela do cronograma:
```powershell
python -c "import sqlite3; c=sqlite3.connect('ipub.db').cursor(); c.execute('SELECT tema, percentual_acertos FROM taxonomia_cronograma WHERE questoes_realizadas > 0 ORDER BY percentual_acertos ASC LIMIT 1'); print(c.fetchone())"
```

### 2. Recuperar a Matéria no Cérebro (RAG/MCP)
Use a tool interna do MCP do Obsidian (ou leia diretamente os arquivos na pasta `resumos/`) buscando pelo nome do tema crítico retornado no passo 1. O objetivo é absorver o conhecimento nativo do usuário, especialmente a seção de **Armadilhas de Prova**.

### 3. Síntese do Tutor
Analise o resumo clínico lido. Crie de 1 a 3 Flashcards super-diretos e focados na fraqueza. O flashcard deve focar apenas no que faz o candidato errar.
- **Formato:** Elo quebrado (Pergunta) + Raciocínio Mestre (Resposta).
- **Tom:** A resposta do flashcard deve utilizar a terminologia formal do Padrão-Ouro (sem gírias de plantão).

### 4. Materializar no Motor FSRS
Persistir cada card via `insert_questao.py` conforme a invocação canônica de 17 argumentos em `.claude/commands/analisar-questao.md §9`. Para reforço sintético: `--area "Reforço RAG"`, `--erro "Lacuna de conhecimento"`, `--marcada "N/A"`, `--armadilha "N/A"`; demais campos (incluindo os 5 estruturados de flashcard) vêm da síntese do tutor.

### 5. Update
Avise o usuário que os cards foram injetados e estão disponíveis para repetição espaçada na aba "Player FSRS" do Streamlit.
