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
- [ ] **Core Mnemônico FSRS v4 (Scheduler + Optimizer):**
  - Implementar rigorosamente o motor FSRS de forma dupla, separando o Agendador operacional do Otimizador.
  - **O Scheduler:** Transitará as métricas base (Dias passados Δt) usando previsores em tempo real de **E** (Estabilidade), **D** (Dificuldade) e **R** (Retenção Desejada definida pelo aluno). Proibição absoluta de learning steps maiores que 1 dia.
  - **O Optimizer (Núcleo de Inteligência IPUB):** Script em PyTorch que roda periodicamente (ex: 1x semana). Usa BPTT (Backpropagation Through Time) e MLE (Maximum Likelihood Estimation) sobre o `fsrs_revlog` para reconstruir a curva de esquecimento, ajustando os coeficientes globais do usuário e garantindo o "Stochastic Shortest Path" de menos revisões com mais memória.

---

## 🖥️ Fase 3: App Streamlit & Arquitetura de Banco de Dados (Em Planejamento)
*Sair da interface da IDE (Markdown) para uma aplicação Web (Streamlit) sustentada por um RDBMS, democratizando o acesso e facilitando a interação diária.*

**Objetivos de Banco de Dados (SQLite) - [Standby / Background ML]:**
- O banco `ipub.db` será mantido estritamente para os cálculos de Machine Learning (Otimizador FSRS) em background, mas **NÃO** será a fonte de verdade visual. A persistência central retorna para o Markdown.

**Objetivos de Frontend (Streamlit App) — Zero DB Architecture:**
A interface gráfica obedecerá o princípio "Toda persistência é via os próprios `.md` existentes, com backup `.bak` automático". A pasta raiz será `app/` para não sujar o repositório LLM.
- [x] **Fase 1 — Base:** Configuração Multipages (`st.navigation`), parser raw dos markdowns e utilitários de I/O de arquivos.
- [x] **Fase 2 — Leitura:** `01_dashboard.py` (Métricas rápidas parseadas do caderno), `03_resumos.py` (Árvore de arquivos de `Temas/`) e `05_historico.py` (Histórico `history/`).
- [x] **Fase 3 — Escrita:** `02_caderno_erros.py` (Filtros e Forms de Inserção direta no `caderno_erros.md`) e Editor visual para os resumos.
- [x] **Fase 4 — Análise:** `04_progresso.py` renderizando Plotly (Acertos vs Erros e Heatmaps de sessão).
- [ ] **Fase 5 — Polimento:** Refinamentos "P2" (UX e Analytics Avançado com a planilha EMED).

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

1. **Refinamentos UI/UX (P2):** Ampliar a inteligência do Streamlit, implementando filtros na tabela de erros e carregando dados do Cronograma EMED 2026.
2. **Setup do FSRS Core:** (Agente) Importar ou transcrever a biblioteca pyFSRS (ou portar a matemática de stability/difficulty) para o backend do IPUB para agendar os flashcards.
