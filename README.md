---
type: onboarding
layer: root
status: canonical
---

# MedHub — Ambiente de Estudo para Residência Médica

## O que é

O MedHub é um ambiente de estudo adaptativo state-driven para residência médica.

Cada erro de questão desencadeia três eventos simultâneos:
- um registro estruturado com metadados diagnósticos no banco (`ipub.db`),
- um refinamento do resumo clínico correspondente em `resumos/`, e
- uma entrada no motor de retenção FSRS.

O resultado é um loop fechado entre falha, diagnóstico, conhecimento e retenção — que opera de forma contínua e cumulativa entre sessões.

O sistema também expõe busca semântica sobre a base de conhecimento via **RAG V2** (`app/engine/rag.py`): Multi-query (Raw + HyDE), paralelismo de busca (ThreadPoolExecutor), propagação de contexto nos chunks. Recall@5 = 90% (ChromaDB + nomic-embed-text, 688 chunks, corpus `resumos/`).

Portável para qualquer LLM via `AGENTE.md` + workflows em `.agents/`.

## Para começar

1. Leia `AGENTE.md` — protocolo de boot obrigatório
2. Leia `ESTADO.md` — snapshot canônico do projeto (estado atual + histórico de sessões)
3. Use o workflow apropriado em `.agents/workflows/`
4. Dashboard: `streamlit run streamlit_app.py`

## Arquitetura do projeto

```
MedHub/
│
├── AGENTE.md              ← bootstrap protocol (ler primeiro)
├── ESTADO.md              ← snapshot canônico (fonte de verdade documental)
├── ROADMAP.md             ← direção evolutiva do produto
├── README.md              ← este arquivo
│
├── ipub.db                ← SSOT de dados (erros, FSRS, cronograma) — não commitar
├── medhub_memory.db       ← memória cross-session (LangMem) — não commitar
│
├── .agents/workflows/     ← workflows portáveis por tarefa
│   ├── analisar-questoes.md
│   ├── criar-resumo.md
│   ├── registrar-sessao.md
│   └── gerar-reforco.md
│
├── resumos/                ← base de conhecimento clínica (resumos por área)
│   ├── INDEX.md           ← hub de navegação (todos os temas com wikilinks)
│   ├── Cirurgia/
│   ├── Clínica Médica/
│   ├── GO/
│   ├── Pediatria/
│   └── Preventiva/
│
├── history/               ← logs de sessão (session_NNN.md)
│   └── legacy/            ← arquivos arquivados (caderno_erros, progresso, planos antigos)
│
├── artifacts/             ← artefatos transitórios (não commitados, exceto /legacy)
│   ├── backups/           ← backups do ipub.db (ipub_backup_YYYYMMDD_HHMMSS.db)
│   ├── llm_runs/          ← inputs e outputs dos passes LLM por sessão
│   │   └── 058/           ← passe qualitativo de flashcards (sessão 058)
│   └── legacy/            ← artefatos aposentados (commitados para rastreabilidade)
│       ├── flashcards_cache.json   ← pipeline de flashcards v1 (pré-ipub.db, aposentado)
│       └── HANDOFF_056.md         ← handoff de sessão 056
│
├── .claude/commands/      ← skills atômicas (spec + invocação)
│   ├── estilo-resumo.md   ← spec de formatação obrigatória
│   ├── analisar-questao.md← protocolo de análise + insert_questao.py
│   ├── extrair-pdf.md     ← wrapper para extract_pdfs.py (Zero PDF)
│   └── auditar-resumos.md ← linter de qualidade para resumos/
│
├── tools/                 ← scripts Python (CLIs)
│   ├── insert_questao.py         ← CLI: insere erro no ipub.db
│   ├── extract_pdfs.py           ← CLI: extrai PDF para %TEMP%, política Zero PDF
│   ├── index_resumos.py          ← (re)indexa resumos/ no ChromaDB (RAG)
│   ├── backup_db.py              ← cria backup datado em artifacts/backups/
│   ├── init_db.py                ← inicializa schema do ipub.db
│   ├── cleanup_db.py             ← limpeza de registros obsoletos no banco
│   ├── audit_flashcard_quality.py← auditoria permanente de qualidade de cards
│   ├── audit_integrity.py        ← auditoria de integridade do banco
│   ├── audit_fsrs.py             ← auditoria operacional FSRS
│   ├── audit_resumos.py          ← linter de qualidade para resumos/
│   ├── review_cli.py             ← CLI de revisão FSRS (3 buckets)
│   ├── regenerate_cards.py       ← regeneração heurística + apply de passe LLM
│   ├── regenerate_cards_llm.py   ← passe qualitativo via API Claude
│   ├── sync_flashcards.py        ← sincronização de flashcards entre fontes
│   ├── migrate_flashcards.py     ← migração de schema de flashcards
│   ├── migrate_memory.py         ← migração de dados de memória
│   └── fix_taxonomy_bridge.py    ← corrige tema_ids órfãos em taxonomia_cronograma
│
├── data/
│   └── chroma/            ← índice ChromaDB (RAG V2 — não commitar)
│
└── app/                   ← Streamlit multipage app
    ├── streamlit_app.py   ← entry point
    ├── pages/
    │   ├── 1_dashboard.py ← painel de performance
    │   ├── 2_estudo.py    ← player FSRS
    │   └── 3_biblioteca.py← navegação de resumos
    ├── engine/            ← API de domínio (agentes usam isto, não queries diretas)
    │   ├── rag.py         ← busca semântica RAG V2 (HyDE + Multi-query)
    │   ├── analyze_error.py
    │   ├── generate_flashcards.py
    │   ├── get_review_queue.py
    │   ├── get_topic_context.py
    │   └── summarize_performance.py
    ├── memory/            ← memória cross-session (LangGraph + LangMem)
    │   ├── manager.py     ← consolidação LLM de sessões
    │   ├── store.py       ← SQLiteMemoryStore → medhub_memory.db
    │   └── inspect.py     ← CLI de inspeção
    └── utils/
        ├── db.py          ← ÚNICO ponto de import sqlite3 na camada app
        ├── fsrs.py        ← algoritmo FSRS v4
        ├── styles.py      ← design system (COLORS, inject_styles)
        └── parser.py      ← parser stateful de questões
```

## Fontes de verdade

| Dado | Fonte de verdade |
|---|---|
| Erros de questão | `ipub.db` → tabela `questoes_erros` |
| Flashcards + FSRS | `ipub.db` → tabelas `flashcards`, `fsrs_cards`, `fsrs_revlog` |
| Cronograma EMED | `ipub.db` → tabela `taxonomia_cronograma` |
| Memória cross-session | `medhub_memory.db` (LangMem) — não commitar |
| Resumos clínicos | `resumos/**/*.md` (44+ arquivos) |
| Índice semântico (RAG) | `data/chroma/` (688 chunks, nomic-embed-text) — não commitar |
| Estado do projeto | `ESTADO.md` |

## Dois eixos de qualidade de flashcards

O pipeline distingue dois eixos **ortogonais** — não confundir:

| Eixo | Campo | Significado |
|---|---|---|
| **Sinais objetivos** | `audit_flashcard_quality.py` | Detecta artefatos no conteúdo: letra de gabarito, prefixo "Sobre X:", badge RESPOSTA DIRETA, regra mestre vazia |
| **Fila qualitativa** | `needs_qualitative` (0/1/2) | 0=aprovado, 1=pendente revisão LLM, 2=aposentado (não entra na fila FSRS) |

Um card pode ter `needs_qualitative=0` (não precisa de LLM) e ainda ter sinais objetivos ruins — ou o inverso. Ver `ESTADO.md` para histórico do passe qualitativo.

## Política de artefatos e backups

### Backups
- Criados por `tools/backup_db.py` com integridade verificada
- Destino: `artifacts/backups/ipub_backup_YYYYMMDD_HHMMSS.db`
- Não commitados (`.gitignore`)
- Backup mais recente: `artifacts/backups/ipub_backup_20260405_191106.db`
- Manter ao menos os 2 mais recentes; remover os antigos manualmente

### Artefatos LLM
- Inputs e outputs dos passes LLM em `artifacts/llm_runs/<sessão>/`
- Não commitados (JSONs grandes, deriváveis do ipub.db)
- Servem como trilha de auditoria do passe qualitativo e base de rollback lógico

### Legacy
- `artifacts/legacy/` — commitado para rastreabilidade histórica
- `flashcards_cache.json`: pipeline v1 de flashcards (pré-ipub.db), aposentado na sessão 058
- `HANDOFF_056.md`: handoff de sessão 056, absorvido pelo ESTADO.md

## Camadas do sistema

| Camada | Artefatos |
|---|---|
| Bootstrap / protocolo | `AGENTE.md`, `CLAUDE.md` |
| Estado e snapshot | `ESTADO.md` |
| Dados operacionais | `ipub.db`, `medhub_memory.db` |
| Base de conhecimento | `resumos/**` · hub: `resumos/INDEX.md` |
| Workflows portáveis | `.agents/workflows/**` |
| Skills (spec + invocação) | `.claude/commands/*.md` |
| Interface | `streamlit_app.py`, `app/**` |
| Histórico | `history/session_NNN.md` |
| Artefatos transitórios | `artifacts/` (ver política acima) |
