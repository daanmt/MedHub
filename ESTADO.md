---
type: snapshot
layer: root
status: canonical
relates_to: AGENTE, HANDOFF, roadmap
---

# ESTADO — MedHub (Preparação para Residência Médica)
*Atualizado: 2026-03-27 (sessão 057) | Ferramenta: Claude Code*

---

Workspace state-driven de estudos médicos. Processa questões de prova, registra padrões de erro no banco SQLite (`ipub.db`) e mantém resumos clínicos estruturados em `Temas/`.

### 🚩 Metas Estratégicas (Roadmap 2026)
- **Meta Final:** 23.000 questões até 12/2026 (Custo/Q: R$ 0,20).
- **Marco ENARE:** 17.000 questões até 10/2026 (Custo/Q: R$ 0,24).
- **Indicador Atual (Março):** 2.631 / 3.000 (Faltam 369 | ~62 q/dia).
- **Performance:** 79,74% (Média Geral).

---

## INÍCIO OBRIGATÓRIO DE SESSÃO

**Leia `AGENTE.md` antes de qualquer ação.** Este arquivo contém o protocolo de boot e a ordem de leitura para garantir a continuidade do projeto.

> [!IMPORTANT]
> **SINGLE SOURCE OF TRUTH (SSOT):** O banco SQLite (`ipub.db`) é a fonte de verdade para erros, métricas e estado FSRS. O `caderno_erros.md` textual foi arquivado em `history/legacy/`. O conteúdo clínico lapidado mora exclusivamente em `Temas/`. Regra "Siamese Twins": **o erro vai pro DB, a lição vai pro resumo (Temas/)**.

- **200+ erros estruturados** no SQLite (`ipub.db`) — consulte o Dashboard para número exato.
- **37+ resumos clínicos** consolidados em `Temas/`.
- **57 sessões** de estudo catalogadas em `history/`.
- **Memory v1 & v3 ativos**: `app/memory/` configurado com `ANTHROPIC_API_KEY` permanente e consolidação LLM funcional.

---

## Mapa de artefatos

### Infraestrutura
| Artefato | Arquivo |
|---|---|
| Bootstrap protocol | `AGENTE.md` |
| Estado do projeto | `ESTADO.md` (este arquivo) |
| Estado operacional curto | `HANDOFF.md` |
| Direção do produto | `roadmap.md` |
| Dashboard Streamlit | `streamlit_app.py` |
| Parser Stateful | `app/utils/parser.py` |
| Player Flashcards | `app/pages/2_estudo.py` |
| CLI de Revisão FSRS | `Tools/review_cli.py` |
| Auditoria FSRS | `Tools/audit_fsrs.py` |
| Auditoria Qualidade Cards | `Tools/audit_flashcard_quality.py` |
| Auditoria Integridade DB | `Tools/audit_integrity.py` |
| Pipeline LLM Qualitativo | `Tools/regenerate_cards_llm.py` |
| Session logs | `history/session_NNN.md` |

### Dados
| Artefato | Arquivo |
|---|---|
| Banco principal (erros, FSRS, cronograma) | `ipub.db` (local only — não commitar) |
| Cache de flashcards LLM | `flashcards_cache.json` (commitado) |

### Conteúdo
| Artefato | Arquivo |
|---|---|
| Resumos clínicos | `Temas/{Área}/{Subespecialidade}/{Tema}.md` |
| Spec de formatação | `.claude/commands/estilo-resumo.md` |
| Protocolo de análise | `.claude/commands/analisar-questao.md` |

### Material de referência (PDFs — não editáveis)
| Artefato | Pasta |
|---|---|
| Fichas de prova | `Fichas/` (5 PDFs por área) |
| Memorex por área | `Memorex/` (6 subpastas) |
| Textos extraídos | `%TEMP%` — deletados ao final de cada sessão (Zero PDF) |

---

## Últimas sessões

**2026-03-27 | Claude Code (sessão 057b):** **Refatoração de qualidade de flashcards (Fases 1-4)**. Auditoria permanente (`audit_flashcard_quality.py`): baseline era 277/277 ruins (100%). Fix no pipeline heurístico (`strip_letter_ref`, template armadilha). Regeneração completa de 277 cards: 239 heuristic OK + 38 heuristic_flagged. Resultado: 31/277 problemáticos (11.2%), 0 campos estruturados NULL. 169 cards marcados `needs_qualitative=1` para passe LLM. FSRS preservado (5 reviews, 5 stability>0). Pipeline LLM (`regenerate_cards_llm.py`) criado. Integridade auditada (`audit_integrity.py`). fix em `insert_questao.py` (fallback "Sobre X:" eliminado).
**2026-03-27 | Claude Code (sessão 057):** **FSRS operacional — CLI de revisão + fix Streamlit**. Substituição do `_avancar()` hardcoded em `2_estudo.py` por `record_review()` real. Criação de `Tools/review_cli.py` (3 buckets: atrasados/hoje/novos, args --limit/--new-limit/--area/--tema). Criação de `Tools/audit_fsrs.py` (auditoria operacional). ROADMAP.md reescrito com 4 trilhos (A Core Revisão, B Interfaces, C Fontes Cards, D Analytics).
**2026-03-27 | Claude Code (sessão 056):** **Pipeline flashcards v5 — migração + regeneração heurística**. Schema `flashcards` migrado com 8 novos campos. 277 cards regenerados (219 heuristic OK, 20 qualitative, 38 flagged). Ferramentas: `Tools/backup_db.py`, `Tools/migrate_flashcards.py`, `Tools/regenerate_cards.py`, `Tools/audit_cards.py`. `insert_questao.py` atualizado com 5 args estruturados.
**2026-03-27 | Claude Code (sessão 055):** **Automação do sistema de memória via hooks**. Auditoria completa das 4 camadas de memória. Correção do `manager.py` (2 managers separados, pt-BR, session_id injetado, `_sync_error_counts`). Migração de 37 WeakAreas para namespace correto. Fix do MCP obsidian-notes-rag em agente-daktus-content (env vars). Hooks automáticos: `memory_boot.py` (SessionStart) + `memory_session_log.py` (PostToolUse Write). AGENTE.md e registrar-sessao.md atualizados.
**2026-03-25 | Antigravity (sessão 051):** **Cirurgia Infantil**. Conclusão do resumo clínico, abrangendo de HDC a defeitos de parede abdominal. 80/20 benchmark e Zero PDF integral.
**2026-03-25 | Antigravity (sessão 050):** **Início de Cirurgia Infantil**. Extração de PDFs e mapeamento clínico.
**2026-03-25 | Antigravity (sessão 049):** **Icterícia e Sepse Neonatal (Pediatria)**. Criação do resumo clínico a partir de PDFs originais. Aplicação integral do Gold Standard 80/20 e workflow Zero PDF.
**2026-03-25 | Antigravity (sessão 048):** **Trauma Abdominal e Pélvico (Cirurgia)**.
**2026-03-25 | Antigravity (sessão 047):** **Leitura de produto completa.** Diagnóstico, visão de produto e roadmap evolutivo (7 linhas) elaborados a partir do estado real do repositório. Aplicação documental: `roadmap.md` reescrito (de backlog para direção de produto), `README.md` com parágrafo de visão, `ESTADO.md` alinhado ao novo roadmap.
**2026-03-25 | Claude Code (sessão 046):** **Memory v1 (LangGraph + LangMem + SQLiteMemoryStore)**. Implementação completa da camada de memória cross-session: `app/memory/` (store, checkpointer, schemas, tools, manager, inspect), `Tools/test_memory.py` (4/4 smoke tests), `MEMORY_ARCHITECTURE.md`. Atualização de AGENTE.md (boot step 5), `registrar-sessao.md` (passo 5 consolidação), `KNOWLEDGE_ARCHITECTURE.md` (seção 9), `requirements.txt`.
**2026-03-24 | Antigravity (sessão 045):** **Sífilis na Gestação e Congênita**. Análise de questão sobre RN de mãe mal tratada com VDRL reagente. Refinamento de fluxograma NTT e inclusão de armadilhas de reinfecção/parceiro. Registro no SQLite (ipub.db).
**2026-03-24 | Antigravity (sessão 044):** **Ginecologia (Úlceras Genitais)**. Criação do resumo clínico `Úlceras Genitais.md` e análise de 3 questões críticas (Herpes gestacional, Fluxograma > 4 sem). 3 erros registrados no SQLite. Limpeza "Zero PDF" executada.
**2026-03-23 | Antigravity (sessão 043):** **Auditoria arquitetural completa (inside job)**. Diagnóstico e correção de todos os documentos centrais. Alinhamento de ESTADO.md, README.md, HANDOFF.md, roadmap.md, workflows. Adição de wikilinks e frontmatter para Obsidian. Limpeza de referências obsoletas.
**2026-03-23 | Antigravity (sessão 042):** **Vigilância em Saúde**. Criação do resumo clínico `Vigilância em Saúde.md` a partir de PDFs originais. Foco em PNVS 2018, Saúde Única e competências ANVISA. Limpeza "Zero PDF" executada.
**2026-03-23 | Antigravity (sessão 041):** **Análise de Erros (Pediatria)**. Análise de 46 questões (42/46). Refinamento do resumo de Emergências Pediátricas (IOT, Pneumotórax, Adrenalina precoce). 4 erros registrados no SQLite (IDs 211-217).
**2026-03-23 | Antigravity (sessão 040):** **Análise de Erros (Dermatologia)**. Análise de 24 questões (16/24). Refinamento do resumo de Hanseníase e PLECT com regras de estesiometria, cultura em Sabouraud, Pentamidina e RX de tórax. Aplicação da Regra de Acúmulo de Armadilhas.
**2026-03-22 | Antigravity (sessão 039):** **Refinamento de Otorrinolaringologia**. Análise de 19 questões (13/19). Inclusão de cisto dermoide (USG hiperecogênico), hemangioma subglótico (Propranolol), fixação de traqueostomia e prognóstico HPV em orofaringe.
**2026-03-22 | Antigravity (sessão 038):** **Dermatologia (Hanseníase e PLECT)**. Criação do resumo clínico `Hanseníase e Síndromes Verrucosas.md`. Extração profunda de 2 apostilas, seguindo o padrão PLECT e 80/20. Limpeza total de PDFs executada.
**2026-03-22 | Antigravity (sessão 037):** **Otorrinolaringologia Cirúrgica**. Criação do resumo `Neoplasias, Congênitas e Traqueostomia.md` abrangendo do cisto tireoglosso ao esvaziamento cervical. Seguida rigorosamente a estética Gold Standard.
**2026-03-22 | Antigravity (sessão 036):** **Consolidação de Arboviroses**. Criação de `Arboviroses.md` (Dengue, Chikungunya, Zika) focando no diagnóstico diferencial e armadilhas clássicas. Remoção automatizada dos PDFs-base (Zero PDF).
**2026-03-21 | Antigravity (sessão 035):** **Reestruturação de Sífilis na Gestação**. Adição de seção de LCR, diagnóstico diferencial STORCH e ajustes em fluxogramas.
**2026-03-20 | Antigravity (sessão 034):** **Refinamento de DM e Auditoria**. Análise de 2 questões de Diabetes (CAD e Manejo). Audit completo do resumo `Diabetes Mellitus - Complicações Agudas.md`. Marca histórica de **100 erros** atingida no caderno e sincronizada no SQLite.
**2026-03-20 | Antigravity (sessão 033):** **Consolidação de Diabetes Agudo**. Criação do resumo clínico `Diabetes Mellitus - Complicações Agudas.md`. Cobertura completa de CAD (adulto/pediatria), EHH e Hipoglicemia.
**2026-03-18 | Antigravity (sessão 032):** **Refinamento Avançado de Colo e Governança**. Revisão profunda do resumo `[GIN] Rastreamento Colo.md` com diretrizes 2025 e análise de 9 erros.
**2026-03-16 | Antigravity (sessão 031):** **Expansão em Psiquiatria e Nefrologia**. Criação dos resumos de `Dependência Química.md`, `Intoxicações Exógenas.md` e `Lesão Renal Aguda.md`.
**2026-03-15 | Antigravity (sessão 030):** **Consolidação de Pancreatites**. Criação do resumo de `Pancreatite Aguda e Crônica.md`. Foco em critérios de Atlanta 2012.
**2026-03-15 | Antigravity (sessão 029):** **UI Refresh**. Implementado sistema de design Flat com `app/utils/styles.py`. Arquitetura híbrida de botões FSRS implementada.
**2026-03-14 | Antigravity (sessões 018–028):** Ver `history/session_NNN.md` para detalhes individuais.

---

## Próximos passos

Ver [[roadmap]] — Linhas Evolutivas.

Prioridade imediata (Linha 3 → Linha 4):
1. **Pipeline RAG inverso:** Injetar conteúdo de `Temas/` no prompt de geração de flashcard.
2. **Meta Volumétrica (60 q/dia):** Manter o ritmo para fechar Março com 3.000 questões.
3. **Consolidação de Memória:** Automática via hook PostToolUse(Write) ao criar `history/session_NNN.md`.
4. Continuar expandindo `Temas/` (GO: DIP e Sangramentos).

---

## Decisões críticas (não reverter)

- **Memory v1**: `app/memory/` (LangGraph + LangMem + SQLiteMemoryStore). Backend: `medhub_memory.db`. Não acoplado ao `ipub.db`. Smoke tests em `Tools/test_memory.py`.
- **Governança via AGENTE.md**: O boot e o fechamento seguem estritamente o `AGENTE.md`.
- **SSOT = ipub.db**: O diagnóstico do erro é gravado via CLI (`Tools/insert_questao.py`) no banco. O `caderno_erros.md` está arquivado em `history/legacy/`.
- **Siamese Twins V2.0**: Erro → DB. Lição/Armadilha → Resumo em `Temas/`.
- **Resumos seguem** `.claude/commands/estilo-resumo.md` — bullets hierárquicos, ⭐/⚠️/🔴; sem tabelas, sem fluxogramas ASCII.
- **Sessions numeradas globalmente** em `history/` — qualquer agente registra.
- **Zero PDF**: `extract_pdfs.py` extrai para `%TEMP%` e apaga o PDF original após consolidação.
- **Regra de Acúmulo**: Seção "Armadilhas de Prova" é cumulativa — nunca remover armadilhas antigas.

---

## Para retomar: leia nesta ordem

1. **`ESTADO.md`** (este arquivo) — visão geral do projeto.
2. **`HANDOFF.md`** — onde o último agente parou.
3. **`AGENTE.md`** — protocolo de boot e fechamento (regras que governam a sessão).

---

## Contexto do repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao final de cada sessão: atualizar este arquivo e registrar em `history/`.*
