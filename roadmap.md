# Product Roadmap: Sistema de Estudos IPUB

> **Visão de Produto:** Um ecossistema de aprendizado ativo para residência médica que transforma passividade (ler) em hiper-retenção (testes, espaçamento e análise metacognitiva de erros). 
> **Foco Core:** Automação do trabalho braçal de criar materiais, permitindo ao usuário focar exclusivamento no estudo e na resolução clínica.

---

## 📍 Fase 1: MVP - Fundação de Conhecimento (Status: Concluído / Em uso)
*A infraestrutura básica para curadoria de conhecimento médico e diagnóstico de erros de prova.*

**Entregas Atuais:**
- [x] **Agente LLM Integrado (Antigravity):** Atua como co-piloto na IDE para processamento rápido baseando-se em `AGENTE.md` e `ESTADO.md`.
- [x] **Caderno de Erros Centralizado (`caderno_erros.md`):** Taxonomia robusta baseada em Habilidades Sequenciais e Metacognição (Diagnóstico do tipo de erro).
- [x] **Base de Conhecimento (`Temas/`):** Geração e formatação padronizada de resumos clínicos otimizados, alimentados diretamente pelos erros das questões.
- [x] **Motor de Extração de Texto:** Script local (`extract_pdfs.py`) para consumir grandes volumes de PDFs e apostilas sem poluir o repositório.
- [x] **Workflows Standard Operating Procedures (SOPs):** `.agents/workflows/` (Ex: Analisar questões médicas complexas garantindo o mesmo output sempre).

---

## 🚀 Fase 2: Motor de Retenção, Espaçamento e Tracking (Status: Próximo Passo)
*Transformar texto estático em flashcards inteligentes (FSRS) e criar a tabela mestre de métricas vinculada ao cronograma.*

**Objetivos:**
- [ ] **Integração com Tabela de Acompanhamento (Cronograma Estratégia Med):**
  - Implementar o acompanhamento estruturado em blocos de disciplinas idênticos ao cronograma oficial (ex: *Cardiologia*, *Ginecologia - Sangramentos*).
  - **Métricas Chave:** Nº de questões resolvidas, Nº de Acertos, Percentual de Acertos (%), Data da última revisão do bloco.
  - Eliminar métricas subutilizadas (ex: custo por questão) para focar estritamente em **Tração Teórica**.
- [ ] **Conversão Automatizada para Flashcards e Export (Anki / Texto):** 
  - Script/Workflow onde o Agente traduz os "Elos Quebrados" do `caderno_erros.md` em pares *Front/Back* e *Cloze Deletions*.
- [ ] **Core do Algoritmo Mnemônico — Implementar Lógica FSRS:**
  - Garantir que a lógica de consumo de Flashcards seja baseada no modelo **FSRS** (Free Spaced Repetition Scheduler), superior ao modelo SM-2 legado do Anki padrão, para otimizar os dias de intervalo (Again, Hard, Good, Easy) respeitando a curva de esquecimento.

---

## 🖥️ Fase 3: App Streamlit & Arquitetura de Banco de Dados (Em Planejamento)
*Sair da interface da IDE (Markdown) para uma aplicação Web (Streamlit) sustentada por um RDBMS, democratizando o acesso e facilitando a interação diária.*

**Objetivos de Banco de Dados (SQLite):**
- [ ] **Modelagem Física e Migração (`ipub.db`):**
  - Substituir os `.md` por um banco local estruturado (SQLite garante portabilidade fácil num arquivo só).
  - **Tabela `questoes`:** id, area, tema (baseado no Estratégia), enunciado, alternativa_correta, alternativa_marcada, tipo_erro, elo_quebrado, data_resolucao.
  - **Tabela `flashcards`:** id, tipo (Frente/Verso ou Cloze), question, answer, source_tema.
  - **Tabela `fsrs_logs`:** fk_flashcard, state (New/Learning/Review), difficulty, stability, last_review_date, next_review_date (Coração do algoritmo de revisão).
  - **Tabela `metricas_cronograma`:** fk_tema, total_questions_done, total_correct, updated_at.

**Objetivos de Frontend (Streamlit App):**
- [ ] **UI/UX Módulo 1 - Painel Cronograma (Dashboard Principal):**
  - Tabela interativa visual mostrando os Temas (Cardiologia, Pediatria), com barras de progresso percentuais (%) de acertos e highlights em vermelho para temas com taxa de retenção perigosa (< 70%).
- [ ] **UI/UX Módulo 2 - Input "One-Click" de Questões:** 
  - Área de texto limpa. O aluno cola o bloco cru copiado da plataforma (com alternativas e gabarito). Botão **[Analisar e Salvar]** aciona o Agente LLM via API no backend para preencher os dados do banco sem olhar pra IDE.
- [ ] **UI/UX Módulo 3 - Flashcards Arena (Modo FSRS):** 
  - Interface escura e focada. Aparece a frente da carta. Botão **[Revelar]**. Mostra o verso e renderiza os 4 botões FSRS (*Again*, *Hard*, *Good*, *Easy*) que disparam a função de "next_review_date" no banco de dados.
- [ ] **UI/UX Módulo 4 - Leitor de Resumos (Wiki):** 
  - Layout limpo renderizando o HTML dos arquivos da pasta `Temas/`, linkando palavras-chave para seus respectivos flashcards no banco.

---

## 🧠 Fase 4: O Workflow Fechado — Simulados e Analytics Ativo (Visão de Futuro)
*O sistema não apenas armazena, mas coordena ativamente as revisões do aluno.*

**Objetivos:**
- [ ] **Gerador de Simulados Personalizados:** 
  - O sistema "puxa" do Banco de Dados questões e temas que o aluno tem alta taxa de erro (ex: Trauma Pediátrico) e monta um arquivo de 50 questões "Cirúrgicas" personalizadas focadas nas fraquezas (Weakness-based testing).
- [ ] **Rotinas de Revisão Automática D-7 / D-30:**
  - O Agente notifica o aluno no frontend: *"Hoje você tem 15 flashcards de Clínica Médica que completaram 7 dias e 3 conceitos de Ginecologia para revisar"*.
- [ ] **Ataque Antecipado de Armadilhas:**
  - Relatório semanal automatizado: *"Nos últimos 7 dias, 40% dos seus erros foram por desatenção a limiares numéricos, especialmente na área de Pediatria."* (Insights que um humano só perceberia meses depois).

---

## 📝 Próximos Passos Imediatos (Diretrizes de Execução)

1. **Setup Inicial do Banco (SQLite):** (Agente) Escrever o script Python `init_db.py` com o schema relacional (*questoes*, *flashcards*, *fsrs_logs*, *metricas_cronograma*).
2. **Setup do FSRS Core:** (Agente) Importar ou transcrever a biblioteca pyFSRS (ou portar a matemática de stability/difficulty) para o backend do IPUB para agendar os flashcards.
3. **Hello World do Streamlit:** (Agente + Usuário) Subir `app.py` integrando a visualização da Tabela de Acompanhamento puxando dados mockados ou reais da migração do DB, validando o pareamento com o cronograma do Estratégia.
