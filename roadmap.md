---
type: roadmap
layer: root
status: canonical
relates_to: ESTADO, HANDOFF
---

# Product Roadmap: Sistema de Estudos MedHub

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
- [x] **Dashboard Honesto:** Métricas 100% fiéis ao caderno, sem resíduos de FSRS fake.
- [x] **O Grande Expurgo (Audit 2026):** Remoção/arquivamento do caderno histórico (`caderno_erros.md`) e da sujeira da pasta Tools (`*.xlsx`, `etl_*.py`), transferindo o protagonismo 100% para o `ipub.db` + UI.

---

## 🔬 Fase 3: Motor de Retenção FSRS v4 Real (Status: Concluído)
*Implementar a matemática de agendamento (Stability/Difficulty) baseada em logs reais.*

**Entregas Concluídas:**
- [x] O Player FSRS agora roda nativo no SQLite, manipulando os states FSRS (Again/Hard/Good/Easy) sob demanda.
- [x] A Curva de Esquecimento Crítico (Dashboard) respeita o período de carência da memória de curto prazo (3 dias).
- [x] Unificação Minimalista em 3-Hubs na UI do Streamlit.

---

## 🧠 Fase 4: O Workflow Fechado — Simulados e Analytics (Status: Próximo Passo)
*O sistema coordena ativamente as revisões do aluno.*

**Objetivos:**
- [ ] **Gerador de Simulados Personalizados:** Questões focadas nas fraquezas (Weakness-based testing).
- [ ] **Relatórios de Desempenho Metacognitivo:** Insights automáticos sobre padrões de erro (ex: desatenção a números).

---

## 🗃️ Fase 5: Motor Lexical e Taxonomia Robusta (Visão de Futuro)
*Erradicar duplicatas de input e consolidar a governança dos dados num modelo SSOT Relacional.*

**A Fraqueza Atual:** A taxonomia do banco (`taxonomia_cronograma`) depende de correspondência exata de strings (ex: *Sífilis Congênita* vs *Sifilis Congenita*), e o pipeline de Flashcards sofre de "Atrofia Semântica" (gerando placeholders como "Este cenário costuma cair") porque o campo Base/Caso Clínico é frequentemente ignorado no input, deixando a LLM sem contexto para fabricar a Armadilha.

**Plano de Resolução Definitiva:**
1. **Dicionário Dimensional (dim_taxonomia):** Criar uma tabela estática e intocável de domínios, mapeando as 5 grandes áreas (Ped, Cir, GO, CM, Prev) para temas rígidos extraídos diretamente dos nomes dos arquivos Markdown em `Temas/`.
2. **Motor Lexical Fuzzy (NLP):** Integrar um algoritmo de similaridade de strings (ex: `thefuzz` / Levenshtein) nos scripts de ingestão (`insert_questao.py` e futuros inputs manuais) para travar 100% no ID Mestre.
3. **Pipeline RAG Inverso (Flashcard Contexto-Ciente):** Acoplar a injeção do Resumo original (o conteúdo de `Temas/`) diretamente no prompt do `flashcard_builder`. A IA não dependerá apenas da frase curta do Caderno; ela usará o próprio parágrafo do Resumo Oficial para popular a "armadilha" e o "cenário" com lastro literário real e zero abstração.
4. **Fim do Legado Excel (Autonomia):** Desenvolver o Widget super-rápido no Dashboard ("Logging Diário") com input obrigatório de caso base.

---

## 📝 Próximos Passos Imediatos (Diretrizes de Execução)

*Marco de 100 erros atingido na sessão 034. FSRS implementado na sessão 026 (Fase 3 concluída).*

1. **Gerador de Simulados:** Implementar gerador de simulados personalizados baseado nas fraquezas do cronograma (Fase 4).
2. **Relatório Metacognitivo:** Insights automáticos sobre padrões de erro recorrentes.
3. **Continuar expandindo Temas/**: Áreas com menor cobertura de questões são prioritárias.
