---
type: snapshot
layer: root
status: canonical
relates_to: AGENTE, HANDOFF, roadmap
---

# ESTADO — MedHub (Preparação para Residência Médica)
*Atualizado: 2026-03-25 (sessão 046) | Ferramenta: Claude Code*

---

Workspace state-driven de estudos médicos. Processa questões de prova, registra padrões de erro no banco SQLite (`ipub.db`) e mantém resumos clínicos estruturados em `Temas/`. Portável para qualquer LLM via [[AGENTE]] + workflows em `.agents/`.

---

## INÍCIO OBRIGATÓRIO DE SESSÃO

**Leia `AGENTE.md` antes de qualquer ação.** Este arquivo contém o protocolo de boot e a ordem de leitura para garantir a continuidade do projeto.

> [!IMPORTANT]
> **SINGLE SOURCE OF TRUTH (SSOT):** O banco SQLite (`ipub.db`) é a fonte de verdade para erros, métricas e estado FSRS. O `caderno_erros.md` textual foi arquivado em `history/legacy/`. O conteúdo clínico lapidado mora exclusivamente em `Temas/`. Regra "Siamese Twins": **o erro vai pro DB, a lição vai pro resumo (Temas/)**.

- **200+ erros estruturados** no SQLite (`ipub.db`) — consulte o Dashboard para número exato.
- **36+ resumos clínicos** consolidados em `Temas/`.
- **46 sessões** de estudo catalogadas em `history/`.
- **Memory v1 ativo**: `app/memory/` + `medhub_memory.db` (LangGraph + LangMem + SQLiteStore).

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
| Player Flashcards | `app/pages/02_flashcards.py` |
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
| Spec de formatação | `Tools/estilo-resumo.md` |
| Protocolo de análise | `Tools/comando de analise de questao.md` |

### Material de referência (PDFs — não editáveis)
| Artefato | Pasta |
|---|---|
| Fichas de prova | `Fichas/` (5 PDFs por área) |
| Memorex por área | `Memorex/` (6 subpastas) |
| Textos extraídos | `%TEMP%` — deletados ao final de cada sessão (Zero PDF) |

---

## Últimas sessões

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

Alinhado com [[roadmap]] Fase 4:

1. **Gerador de Simulados Personalizados:** Questões focadas nas fraquezas (Weakness-based testing).
2. **Relatórios de Desempenho Metacognitivo:** Insights automáticos sobre padrões de erro.
3. Continuar alimentando `Temas/` nas áreas com menor cobertura de questões.

---

## Decisões críticas (não reverter)

- **Memory v1**: `app/memory/` (LangGraph + LangMem + SQLiteMemoryStore). Backend: `medhub_memory.db`. Não acoplado ao `ipub.db`. Smoke tests em `Tools/test_memory.py`.
- **Governança via AGENTE.md**: O boot e o fechamento seguem estritamente o `AGENTE.md`.
- **SSOT = ipub.db**: O diagnóstico do erro é gravado via CLI (`Tools/insert_questao.py`) no banco. O `caderno_erros.md` está arquivado em `history/legacy/`.
- **Siamese Twins V2.0**: Erro → DB. Lição/Armadilha → Resumo em `Temas/`.
- **Resumos seguem** `Tools/estilo-resumo.md` — bullets hierárquicos, ⭐/⚠️/🔴; sem tabelas, sem fluxogramas ASCII.
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
