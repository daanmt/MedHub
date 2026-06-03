---
type: roadmap
layer: root
status: canonical
relates_to: [ESTADO]
---

# Roadmap de Produto — MedHub

> Direção evolutiva, não plano de sprint.
> Sem datas. Sem status de tarefa. Sem checklists de MVP.

A fundação está pronta (agente LLM + workflows portáveis + `ipub.db` como SSOT + FSRS operacional + RAG local + memória cross-session). Este documento descreve para onde o sistema pode evoluir — não o que já foi feito. Para o histórico de implementação, ver [`history/INDEX.md`](history/INDEX.md); para o estado atual, ver [`ESTADO.md`](ESTADO.md).

---

## Linhas Evolutivas

### 1. MedHub como Sistema de Registro

**Por que existe:** Todo o resto depende desta camada. Se o erro não for registrado com qualidade — tipo, tema, elo quebrado, armadilha — as camadas superiores não têm substrato. O registro é o acelerador de todas as outras linhas.

**O que habilita:** O banco `ipub.db` como SSOT operacional cria a matéria-prima para análise, retenção e adaptação. Sem registro estruturado, há apenas acúmulo de notas.

**O que consolida:**
- Motor lexical fuzzy para normalização de taxonomia (eliminar variações de grafia como "Sífilis Congênita" vs. "Sifilis Congenita")
- Logging rápido integrado na UI (reduzir fricção do `insert_questao.py` manual)

---

### 2. MedHub como Workspace Semântico

**Por que existe:** O registro de erros sem base de conhecimento de qualidade é apenas um log. A base `resumos/` transforma o registro em compreensão. A lição identificada na questão precisa encontrar o lugar exato no resumo — não o fim do arquivo, mas o ponto temático correto.

**O que habilita:** A base semântica é o que permite flashcards contextualizados, simulados orientados por fraqueza e busca por embeddings. Sem `resumos/` de qualidade, o sistema gera ruído, não insight.

**O que consolida:**
- Migração completa da nomenclatura (remover prefixos legados `[GIN]`, `[OBS]`, `[CIR]`, `[ORL]`)
- Eliminação de stubs (`TCE.md` precisa de conteúdo ou ser removido)
- Cobertura crescente: áreas com mais erros no banco merecem mais resumos
- **Retrieval baseline reproducible:** `tools/eval/REPORT.md` (R@5=0.778 / MRR@10=0.657 com HyDE; 18 queries; rodar via `python tools/eval/run_eval.py`)
- `/discover` (tech debt): Cross-Encoders dedicados, Reciprocal Rank Fusion (RRF), normalização de score → meta R@5 ≥ 0.95
- Busca semântica via `sqlite-vec` como alternativa à busca literal (a implementar)

---

### 3. MedHub como Motor de Revisão

**Por que existe:** Conhecimento sem revisão espaçada decai. A matemática do FSRS existe para combater a curva de esquecimento. Esta linha garante que o estudante revisite o que precisa, quando precisa — não o que é conveniente ou recente.

**O que habilita:** O player FSRS fecha o loop entre erro → registro → retenção. Flashcards contextualizados com o conteúdo dos resumos (pipeline RAG inverso) elevam a qualidade da revisão de "lembrar a resposta" para "compreender o raciocínio".

**O que consolida:**
- Pipeline RAG inverso: injetar conteúdo do `resumos/` no prompt de geração de flashcard (eliminar "atrofia semântica")
- Input obrigatório de contexto clínico ao registrar erro
- Dashboard de revisão com curva de esquecimento por área
- Implementação FSRS v4 fiel (hoje `app/utils/fsrs.py` é simplificação — 1 fórmula linear de dificuldade + 1 de estabilidade). Referência canônica do algoritmo: [`fsrs4anki`](https://github.com/open-spaced-repetition/fsrs4anki); port Python da mesma org: `py-fsrs`

---

### 4. MedHub como Sistema de Recuperação Orientada por Tarefa

**Por que existe:** O estudante não sabe sempre o que estudar primeiro. O sistema sabe — ele tem os dados. Esta linha transforma o banco de erros e o cronograma em recomendação ativa de estudo, não em relatório passivo.

**O que habilita:** Simulados personalizados baseados em fraqueza real (Weakness-based testing). O sistema seleciona questões ou flashcards não de forma aleatória, mas orientada pelo gap identificado no `ipub.db` e pela curva de esquecimento do FSRS.

**O que consolida:**
- Gerador de simulados: seleciona por área/tema com menor taxa de acerto no banco
- Relatório de desempenho metacognitivo: padrões de erro por tipo (desatenção, confusão de critério, erro de cálculo) — não apenas por tema
- Integração cronograma ↔ FSRS: prioridade de revisão ponderada por data da prova

---

### 5. MedHub como Agente de Execução do Estudo

**Por que existe:** As linhas anteriores dependem do estudante iniciar cada ciclo manualmente. Esta linha inverte: o sistema propõe, executa e confirma. O agente planeja a sessão, seleciona os materiais e registra os resultados — com mínima fricção para o usuário.

**O que habilita:** Uma sessão guiada por agente: "hoje você tem 45 minutos — o sistema identificou que Sífilis Congênita e Emergências Pediátricas têm maior gap. Vamos revisar." O agente executa o workflow completo sem que o usuário precise orquestrar manualmente.

**O que consolida:**
- Session planner: agente lê o banco, identifica gaps e propõe plano de sessão
- Execução autônoma do loop: análise → registro → atualização de resumo sem etapas manuais
- Memória longa ativa: `weak_areas` e `session_insights` no LangMem operacionais; integração com session planner pendente

---

### 6. MedHub como Agente Metacognitivo

**Por que existe:** Saber *o que* errar e *o que* estudar é diferente de saber *por que* o padrão de erro persiste. A metacognição transforma dados de performance em consciência sobre o próprio processo de aprendizagem.

**O que habilita:** Relatórios que vão além de "você errou Sífilis 3 vezes" — e chegam em "você sistematicamente seleciona o diagnóstico mais comum em vez de aplicar o critério do fluxograma". Isso é informação acionável para mudar o comportamento de estudo.

**O que consolida:**
- Dashboard metacognitivo: top tipos de erro por área, padrões de elo quebrado, evolução temporal
- Relatórios periódicos gerados pelo agente ao fechar ciclos de estudo
- Reaproveitar `weak_areas` da Camada 3 como input do relatório

---

### 7. MedHub como Sistema Adaptativo

**Por que existe:** Um sistema que aprende com o estudante precisa se recalibrar com o tempo. Temas dominados saem do radar ativo. Novas fraquezas emergem. O ritmo de estudo muda. O sistema acompanha essa evolução sem exigir reconfiguração manual.

**O que habilita:** Um ambiente que se torna mais inteligente a cada sessão — ajustando prioridades, reformulando flashcards conforme o conhecimento consolida, identificando quando um tema está sendo hiper-revisado sem necessidade ou quando uma área está sendo negligenciada.

**O que consolida:**
- TTL/max_entries por namespace (evitar que `weak_areas` acumule áreas já dominadas)
- Deduplicação LLM de `weak_areas` via `create_memory_store_manager`
- Recalibração de cronograma baseada em curva real de acertos por área
- Modelo de "gradiente de atenção": áreas com alta taxa de acerto recebem menos slot de sessão

---

### 8. MedHub Agent-First (Consolidação no Claude Code)

**Por que existe:** As linhas 1-7 assumiam o estudante orquestrando múltiplas plataformas (Antigravity, Gemini, Claude Code) e o Streamlit como rosto principal. Esta linha inverte a postura: **uma interface (Claude Code), o agente como cérebro, o código como esqueleto determinístico mínimo.** O que historicamente virou "cérebro em código" — geração heurística de cards, pipeline de RAG, interpretação de performance — pertence ao agente. O que é determinístico e precisa estar correto — o algoritmo FSRS e a persistência — pertence ao código. Tudo o mais (UI, ingestão) encolhe ou sai para MCP.

**O que habilita:** Uso remoto real (remote-control pelo celular) sem hospedar app nem migrar o SQLite para a nuvem — a revisão acontece na conversa. Menos superfície frágil (Ollama/ChromaDB deixam de ser caminho crítico; heurística de cards desaparece). Um único fluxo de dados: erro/planilha → agente → CLI de persistência → `ipub.db`.

**O que consolida:**
- **Revisão conversacional de flashcards:** o agente puxa a fila vencida (buckets atrasado/hoje/novo), apresenta card a card no chat e grava o rating via `record_review()`. O player Streamlit (`app/pages/2_estudo.py`) vira opcional/desktop — corrigir os bugs de closure/`session_state` ou descontinuar.
- **Geração de cards pelo agente:** aposentar `tools/regenerate_cards.py` + `regenerate_cards_llm.py` (421 linhas de heurística regex + batch LLM). Ao analisar um erro, o agente escreve o card de qualidade e passa pronto para `insert_questao.py` (que já aceita `--frente_*`/`--verso_*`).
- **FSRS fiel** (cruza com Linha 3): substituir `app/utils/fsrs.py` caseiro pela lógica de referência (`fsrs4anki`/`py-fsrs`). É o único pedaço que *deve* ser código correto e determinístico.
- **RAG local mantido, obsidian MCP descontinuado para busca:** decisão empírica — em teste comparativo o `rag.py` local acertou resumo + seção (dist 0.148, metadata de área/especialidade) enquanto o MCP `obsidian-notes-rag` retornou tópico errado, indexando um snapshot stale com `Temas/` + `resumos/` duplicados + ruído de projeto.
- **Ingestão via Google Workspace MCP:** planilhas na conta Google entram via MCP (Drive/Sheets) → `registrar_sessao_bulk.py`, substituindo a extração manual de `.xlsx`.
- **Streamlit encolhe ao que exige UI real:** dashboard cede espaço para a skill `/performance`; o app deixa de hospedar "inteligência".
- **Higiene latente:** corrigir `app/utils/db.py:98-99` (`get_next_due_card()` referencia colunas `frente`/`verso` já removidas) e adicionar `UNIQUE(area, tema)` em `taxonomia_cronograma`.

---

## Anti-goals

O MedHub não deve virar:

1. **Dumping ground de Markdown.** Cada nota em `resumos/` existe porque um erro de questão ou uma apostila a justificou. Não criar resumos por completismo de área.
2. **Chatbot genérico.** O agente tem identidade, protocolo e contexto específicos. Não generalizar para outros domínios.
3. **App desconectado da base de conhecimento.** O Streamlit deve consumir o que está no banco e nos resumos — não criar uma camada de dados paralela.
4. **Memória competindo com a fonte canônica.** O `medhub_memory.db` captura preferências e padrões de fraqueza, não replica o conteúdo de `resumos/` ou `ESTADO.md`.
5. **Stack sofisticada sem clareza pedagógica.** Toda peça precisa ter uso real, não especulativo. A régua: se não foi usado em sessões reais, simplificar ou remover.
6. **Arquitetura inflada sem uso real.** O risco de um projeto solo de engenharia é acumular camadas que parecem necessárias mas não são exercidas. (Lição da sessão 072: 4 funções da "engine API" e `app/memory/tools.py` foram deletadas após auditoria revelar zero callers.)
