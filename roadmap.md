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

## 🚀 Fase 2: Motor de Retenção e Dash Dinâmico (Status: Concluído)
*Transformar texto estático em banco de dados relacional e controle de cronograma.*

**Entregas Concluídas:**
- [x] **Integração Absoluta com o Cronograma (Excel -> DB):** Planilha do Estratégia mapeada e editável via Dashboard.
- [x] **Arquitetura SQLite (SSOT):** Centralização de erros e cronograma no `ipub.db`.
- [x] **App Streamlit Minimalista:** 4 abas integradas (Dash, Resumos, Caderno DB, Histórico).

---

## 🔬 Fase 3: Motor de Retenção FSRS v4 (Status: Próximo Passo)
*Implementar rigorosamente o motor FSRS de agendamento e otimização.*

**Objetivos:**
- [ ] **Scheduler:** Agendamento de revisões (Stability/Difficulty) no `fsrs_cards`.
- [ ] **Optimizer:** Script em PyTorch para calibragem da curva de esquecimento.
- [ ] **Interface de Revisão:** Aba no Streamlit para responder flashcards e coletar logs (Review Log).

---

## 🧠 Fase 4: O Workflow Fechado — Simulados e Analytics (Visão de Futuro)
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
