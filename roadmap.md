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

## 🚀 Fase 2: Motor de Retenção (FSRS v4) e Dash de Progresso (Status: Próximo Passo)
*Transformar texto estático em flashcards guiados pelo algoritmo mnemônico FSRS v4 state-of-the-art e criar a tabela mestre de métricas vinculada ao cronograma.*

**Objetivos:**
- [ ] **Integração Absoluta com o Cronograma (Estratégia Med):**
  - Implementar o painel de métricas consumindo a taxonomia de disciplinas exata da planilha `Dashboard EMED 2026.xlsx`.
  - **Métricas Chave:** Nº de questões realizadas, Nº de Acertos, Percentual de Acertos (%). Ignorar métricas de vaidade (ex: custo por questão).
- [ ] **Conversão Automatizada para Flashcards e Export (Anki / Texto):** 
  - Script autônomo do Agente que traduz os "Elos Quebrados" do `caderno_erros.md` em pares *Frente/Verso* precisos.
- [ ] **Core Mnemônico (The FSRS v4 Algorithm):**
  - Implementar rigorosamente o agendador FSRS como motor de datas. O usuário escolhe sua **Retenção Desejada (R)**.
  - O sistema transitará as métricas base (Dias passados Δt) usando os preditores de FSRS clássicos:
    - **Estabilidade (E):** Tempo (dias) para a Retenção cair a 90% (variável vital na fórmula, otimizada após +1.000 revisões).
    - **Dificuldade (D):** Coeficiente de complexidade da questão.
    - **Retenção (R):** Probabilidade momentânea de conseguir evocar o flashcard na hora da revisão.
  - Proibição absoluta de learning steps (passos de aprendizado) maiores que 1 dia, seguindo as diretrizes do desenvolvedor do FSRS.

---

## 🖥️ Fase 3: App Streamlit & Arquitetura de Banco de Dados (Em Planejamento)
*Sair da interface da IDE (Markdown) para uma aplicação Web (Streamlit) sustentada por um RDBMS, democratizando o acesso e facilitando a interação diária.*

**Objetivos de Banco de Dados (SQLite):**
- [ ] **Modelagem Física e Migração (`ipub.db`):**
  - Substitução do repositório em texto para um banco leve e relacional estruturado nos moldes FSRS.
  - **Tabela `questoes`:** id, area, tema (taxonomia EMED), enunciado, alternativa_correta, alternativa_marcada, tipo_erro, elo_quebrado, data_resolucao.
  - **Tabela `flashcards`:** id, tipo, frente, verso, id_questao.
  - **Tabela `fsrs_cards`:** core state do FSRS (id_card, state [New/Learning/Review/Relearning], *D* (Dificuldade), *S* (Estabilidade), *R* (Retrovabilidade projetada), last_review, due_date, reps, lapses).
  - **Tabela `fsrs_revlog`:** Histórico atômico imutável (id_log, id_card, rating, delta_t, tempo_resposta) fundamental para rodar o Otimizador do FSRS no futuro.
  - **Tabela `dashboard_metricas`:** id_tema, questões_feitas, questoes_acertadas, percentual, updated_at.

**Objetivos de Frontend (Streamlit App):**
- [ ] **UI Módulo 1 - Cockpit de Progresso (EMED 2026):**
  - Tabela espelho visual importando o modelo do Excel original. Listagem de disciplinas por bloco, barras de progresso lineares com o percentual de acertos, highlights visuais se taxa < 70%.
- [ ] **UI Módulo 2 - Input Dinâmico de Erro:** 
  - Caixa de dump (para colar Ctrl+C/Ctrl+V do simulado). O backend aciona o workflow IPUB e já devolve a questão formatada, gerando o erro na Tabela `questoes` nativa do banco e criando a base do Flashcard automaticamente.
- [ ] **UI Módulo 3 - Arena FSRS (Deck Mode):** 
  - App minimalista de revisão, puxando apenas as cartas cujo `due_date` ≤ hoje. Botões (1-De Novo, 2-Difícil, 3-Bom, 4-Fácil). Clicar engatilha os coeficientes D e S da Tabela `fsrs_cards` calculando o intervalo futuro.
- [ ] **UI Módulo 4 - Wiki Markdown Engine:** 
  - Renderiza HTML clean dos resumos, possibilitando criação autônoma de flashcards a partir dos parágrafos com `🔴` das armadilhas de prova com 1 clique.

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
