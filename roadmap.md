---
type: roadmap
layer: root
status: canonical
relates_to: ESTADO
---

# Roadmap de Produto — MedHub

> Direção evolutiva, não plano de sprint.
> Sem datas. Sem status de tarefa. Sem checklists de MVP.

---

## Fundação (concluído)

O MedHub foi construído em quatro camadas fundacionais:

- **Fundação (Fase 1):** Agente LLM integrado via `AGENTE.md`, base de conhecimento em `resumos/`, workflows portáveis em `.agents/`, extração de PDFs via `extract_pdfs.py`.
- **Estabilização (Fase 2):** Arquitetura Zero-DB resolvida (SSOT = `ipub.db`), parser stateful, dashboard honesto, expurgo de arquivos legados.
- **Schema FSRS (Fase 3):** Tabelas `flashcards`, `fsrs_cards`, `fsrs_revlog` migradas. 277 cards gerados. Passe qualitativo LLM completo (0 pendentes). CLI de revisão e motor FSRS operacional via `tools/review_cli.py`.
- **RAG V2 + Memória (Fase 4):** `app/engine/rag.py` com Multi-query (Raw + HyDE), ThreadPoolExecutor, Context Propagation. Recall@5 = 90%. `app/memory/` com LangGraph + LangMem + SQLiteMemoryStore operacional (`medhub_memory.db`).

---

## Trilhos de Desenvolvimento

Quatro trilhos em paralelo — cada um tem foco e cadência próprios.

### Trilho A — Core de Revisão
Objetivo: FSRS funcionando de ponta a ponta (registro → algoritmo → próxima due).

- `tools/review_cli.py`: CLI MVP com política de 3 buckets (atrasados → hoje → novos) ✓
- `tools/audit_fsrs.py`: auditoria operacional do estado FSRS ✓
- `app/pages/2_estudo.py`: player Streamlit integrado ao `record_review()` ✓
- Session log no CLI (N revisados, distribuição 1-4, próximas dues) ✓
- `insert_questao.py` estável (bugfix sessão 066: remoção de colunas obsoletas, tratamento de `cronograma_progresso`) ✓

### Trilho B — Interfaces
Objetivo: Streamlit como dashboard e consulta; CLI como interface primária de revisão.

- Dashboard FSRS: curva de retenção por área, distribuição de states
- Métricas de streak e consistência de revisão
- Interface de revisão qualitativa para cards `needs_qualitative`

### Trilho C — Fontes de Cards
Objetivo: alimentar o banco com cards de alta qualidade de múltiplas fontes.

- `questoes_erros` → flashcards: pipeline heurístico corrigido (strip_letter_ref, sem "Sobre X:") ✓
- Qualidade atual: **277/277 OK (100%)**, 0/277 com sinais críticos ✓ (sessão 058)
- `tools/audit_flashcard_quality.py`: auditoria permanente de qualidade ✓
- Passe LLM completo: 189 cards reescritos, 0 needs_qualitative=1 pendentes ✓ (sessão 058)
- Taxonomia bridge: 21 tema_ids órfãos corrigidos via `tools/fix_taxonomy_bridge.py` ✓ (sessão 058)
- PDFs Estratégia → flashcards: `tools/import_pdf_cards.py` (a implementar)

### Trilho D — Analytics
Objetivo: fechar o loop entre performance e estudo.

- Métricas FSRS no dashboard: curva de esquecimento, retention rate
- Simulados orientados por fraqueza (menor acerto no banco)
- Relatório metacognitivo: padrões de erro por tipo e área

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
- Auditoria de precisão do RAG: refinar chunking e testar recall semântico ✓ (Sessão 064: Recall@5 90% atingido com HyDE + Multi-query)
- Motor RAG V2: HyDE + Raw query, ThreadPoolExecutor, Context Propagation nos chunks ✓ — BM25 desabilitado (regressão, tech debt)
- Cobertura semântica: 44+ resumos indexados (688 chunks) em `data/chroma/` ✓
- `/discover` (Tech Debt): Cross-Encoders dedicados, Reciprocal Rank Fusion (RRF), normalização de score → meta Recall@5 99%+
- Busca semântica via `sqlite-vec` como alternativa à busca literal (a implementar)
- Cobertura crescente: áreas com mais erros no banco merecem mais resumos

---

### 3. MedHub como Motor de Revisão

**Por que existe:** Conhecimento sem revisão espaçada decai. A matemática do FSRS existe para combater a curva de esquecimento. Esta linha garante que o estudante revisite o que precisa, quando precisa — não o que é conveniente ou recente.

**O que habilita:** O player FSRS fecha o loop entre erro → registro → retenção. Flashcards contextualizados com o conteúdo dos resumos (pipeline RAG inverso) elevam a qualidade da revisão de "lembrar a resposta" para "compreender o raciocínio".

**O que consolida:**
- Pipeline RAG inverso: injetar conteúdo do `resumos/` no prompt de geração de flashcard (eliminar "atrofia semântica")
- Input obrigatório de contexto clínico ao registrar erro
- Dashboard de revisão com curva de esquecimento por área

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
- Memória longa ativa: `weak_areas` e `session_insights` no LangMem operacionais ✓ — integração com session planner pendente

---

### 6. MedHub como Agente Metacognitivo

**Por que existe:** Saber *o que* errar e *o que* estudar é diferente de saber *por que* o padrão de erro persiste. A metacognição transforma dados de performance em consciência sobre o próprio processo de aprendizagem.

**O que habilita:** Relatórios que vão além de "você errou Sífilis 3 vezes" — e chegam em "você sistematicamente seleciona o diagnóstico mais comum em vez de aplicar o critério do fluxograma". Isso é informação acionável para mudar o comportamento de estudo.

**O que consolida:**
- `consolidate_session()` ativo: Memory v1 em produção (`app/memory/`, `medhub_memory.db`) ✓ (sessão 055)
- Dashboard metacognitivo: top tipos de erro por área, padrões de elo quebrado, evolução temporal
- Relatórios periódicos gerados pelo agente ao fechar ciclos de estudo

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

## Anti-goals

O MedHub não deve virar:

1. **Dumping ground de Markdown.** Cada nota em `resumos/` existe porque um erro de questão ou uma apostila a justificou. Não criar resumos por completismo de área.
2. **Chatbot genérico.** O agente tem identidade, protocolo e contexto específicos. Não generalizar para outros domínios.
3. **App desconectado da base de conhecimento.** O Streamlit deve consumir o que está no banco e nos resumos — não criar uma camada de dados paralela.
4. **Memória competindo com a fonte canônica.** O `medhub_memory.db` captura preferências e padrões de fraqueza, não replica o conteúdo de `resumos/` ou `ESTADO.md`.
5. **Stack sofisticada sem clareza pedagógica.** Toda peça precisa ter uso real, não especulativo. A régua: se não foi usado em sessões reais, simplificar ou remover.
6. **Arquitetura inflada sem uso real.** O risco de um projeto solo de engenharia é acumular camadas que parecem necessárias mas não são exercidas.
