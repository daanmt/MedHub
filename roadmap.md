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

## 🚀 Fase 2: Reforma v3.0 - Estabilização e Zero-DB (Status: Concluído)
*Consolidar a arquitetura baseada em Markdown, eliminar over-engineering e estabilizar o player.*

**Entregas Concluídas:**
- [x] **Arquitetura Zero-DB (SSOT):** O Markdown (`caderno_erros.md`) é a única fonte de verdade para leitura na UI.
- [x] **Parser Stateful:** Herança robusta de Área/Tema via cabeçalhos MD.
- [x] **Flashcard Anti-Crash:** Player ultra-estável baseado em shuffle de índices (fim do KeyError).
- [x] **Dashboard Honesto:** Métricas 100% fiéis ao caderno, sem resíduos de FSRS fake.
- [x] **Persistência Federada:** Registro de novos erros via escrita direta no MD.

---

## 🔬 Fase 3: Motor de Retenção FSRS v4 Real (Status: Próximo Passo)
*Implementar a matemática de agendamento (Stability/Difficulty) baseada em logs reais.*

**Objetivos:**
- [ ] **FSRS Real Integration:** Substituir o sistema de navegação simples por agendamento real via pesos de memória.
- [ ] **Review Log (history/):** Persistir a performance de cada card no histórico para calibragem futura.
- [ ] **Busca Semântica no App:** Implementar busca por palavras-chave em todos os resumos da pasta `Temas/`.

---

## 🧠 Fase 4: O Workflow Fechado — Simulados e Analytics (Visão de Futuro)
*O sistema coordena ativamente as revisões do aluno.*

**Objetivos:**
- [ ] **Gerador de Simulados Personalizados:** Questões focadas nas fraquezas (Weakness-based testing).
- [ ] **Relatórios de Desempenho Metacognitivo:** Insights automáticos sobre padrões de erro (ex: desatenção a números).

---

## 📝 Próximos Passos Imediatos (Diretrizes de Execução)

1. **Escalabilidade:** Expandir a base de erros para romper o marco de 100 entradas reais no caderno.
2. **Setup do FSRS Core:** Importar lógica de pesos matemáticos para o backend para agendar os flashcards de forma real.
