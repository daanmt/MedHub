---
type: rules
layer: root
status: canonical
relates_to: [AGENTE, ESTADO, README]
---

# Arquitetura de Conhecimento — MedHub

Regras duras do workspace. Toda nota nova e todo agente devem obedecer este documento.

---

## 1. Tipos de Nota

| type | Onde fica | Exemplo |
|---|---|---|
| `knowledge` | `Temas/` | `Insuficiência Cardíaca.md` |
| `bootstrap-protocol` | raiz | `AGENTE.md` |
| `snapshot` | raiz | `ESTADO.md` |
| `handoff` | raiz | `HANDOFF.md` |
| `roadmap` | raiz | `roadmap.md` |
| `onboarding` | raiz | `README.md`, `CLAUDE.md` |
| `rules` | raiz | `KNOWLEDGE_ARCHITECTURE.md` |
| `spec` | `Tools/` | `estilo-resumo.md` |
| `workflow` | `.agents/workflows/` | `analisar-questoes.md` |
| `hub` | qualquer nível | `Temas/INDEX.md` |
| `reference` | `Tools/` | `Anatomia do MedHub.md` |
| `session` | `history/` | `session_043.md` |

---

## 2. Frontmatter Mínimo por Tipo

### Notas de conhecimento clínico (`Temas/`)
```yaml
---
type: knowledge
area: [Clínica Médica | GO | Cirurgia | Pediatria | Preventiva]
especialidade: Cardiologia        # omitir se área == especialidade
status: [active | stub]
aliases: [IC]                     # apenas siglas consolidadas; omitir se não existir
---
```

### Documentos raiz canônicos
```yaml
---
type: [bootstrap-protocol | snapshot | handoff | roadmap | onboarding | rules]
layer: root
status: canonical
relates_to: [ESTADO, AGENTE]      # máximo 3 referências
---
```

### Specs e referências (`Tools/`)
```yaml
---
type: [spec | reference]
layer: tools
status: canonical
---
```

### Workflows (`.agents/workflows/`)
```yaml
---
type: workflow
layer: agents
status: canonical
description: Uma linha descrevendo o que o workflow faz
---
```

### Hubs
```yaml
---
type: hub
layer: [root | knowledge | agents]
status: active
---
```

**Regra:** não adicionar campos decorativos. Se o campo não orienta busca ou filtragem, não existe.

---

## 3. Naming Conventions

### `Temas/`
- Hierarquia: `Temas/{Área}/{Especialidade}/{Tema}.md`
- Prefixos opcionais (`[GIN]`, `[OBS]`, `[CIR]`, `[ORL]`) são legados — não propagar
- Nomenclatura nova: nome descritivo direto, sentence case, sem prefixo
- Exemplos corretos: `Insuficiência Cardíaca.md`, `Tuberculose.md`, `Amenorreia.md`

### `history/`
- Padrão: `session_NNN.md` (numeração sequencial global, três dígitos, zero-padded)
- Não criar sessões retroativas

### Raiz
- Maiúsculas para docs canônicos: `AGENTE.md`, `ESTADO.md`, `HANDOFF.md`, `CLAUDE.md`
- Minúsculas para docs estruturais: `roadmap.md`

---

## 4. Política de Wikilinks

- Wikilinks são **intencionais**, não automáticos
- Usar quando o link cria significado navegacional real
- Hubs apontam para notas (`Temas/INDEX.md` → todos os temas)
- Notas de conhecimento **não linkam de volta** para docs raiz (evita ruído no grafo)
- Docs raiz linkam para workflows e hubs relevantes
- Aliases permitem wikilinks curtos: `[[IC]]` resolve para `Insuficiência Cardíaca.md`

---

## 5. Política de Aliases

- Aliases apenas para **siglas clínicas consolidadas** (reconhecidas em prova/literatura)
- Máximo 3 aliases por nota
- Não criar aliases para variações de grafia ou sinônimos informais

Exemplos válidos: `IC`, `DRC`, `LRA`, `TB`, `DM2`, `TCE`, `DUP`, `DITC`, `SUA`, `PLECT`

---

## 6. Arquitetura de Retrieval (Tiers)

### Tier 1 — Indexar e priorizar
Conteúdo semântico canônico. Porta de entrada para agentes.

| Arquivo | Por quê |
|---|---|
| `AGENTE.md` | Boot protocol — obrigatório em toda sessão |
| `ESTADO.md` | Snapshot do projeto — estado atual |
| `HANDOFF.md` | Próximo passo imediato |
| `README.md` | Onboarding e arquitetura |
| `roadmap.md` | Visão evolutiva |
| `KNOWLEDGE_ARCHITECTURE.md` | Este documento — regras do ambiente |
| `Temas/**/*.md` | Base de conhecimento clínico (núcleo do projeto) |
| `Temas/INDEX.md` | Hub de navegação para todos os temas |
| `.agents/workflows/*.md` | SOPs portáveis |
| `Tools/estilo-resumo.md` | Spec de formatação obrigatória |
| `Tools/comando de analise de questao.md` | Protocolo de análise |

### Tier 2 — Indexar com menor prioridade
Contexto auxiliar. Útil mas não prioritário.

| Arquivo | Por quê |
|---|---|
| `Tools/Anatomia do MedHub (Infraestrutura).md` | Referência de arquitetura |
| `Tools/Mapeamento de Skills e Workflows.md` | Referência de skills |
| `history/session_*.md` (últimas 10) | Histórico recente |

### Tier 3 — Não indexar / excluir
Material que polui retrieval e grafo.

| Diretório / Arquivo | Motivo |
|---|---|
| `medhub-ui-refresh-main/` | Projeto React legado, sem relação com conteúdo clínico |
| `history/legacy/` | Arquivos deprecados (caderno_erros.md, progresso.md) |
| `Fichas/` | PDFs de fichas (sem .md) |
| `Memorex/` | PDFs de memorex (sem .md) |
| `data/` | CSVs operacionais |
| `app/` | Código Python da UI |
| `.venv/`, `.claude/` | Artefatos de ambiente |

---

## 7. O que um Agente deve ler por tarefa

```
TAREFA                              LEIA PRIMEIRO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Retomar o projeto                → AGENTE.md → ESTADO.md → HANDOFF.md
Entender o estado atual          → ESTADO.md
Encontrar workflows              → .agents/workflows/
Encontrar temas clínicos         → Temas/INDEX.md → Temas/{Área}/{Tema}.md
Analisar questão errada          → .agents/workflows/analisar-questoes.md
Criar novo resumo                → .agents/workflows/criar-resumo.md + Tools/estilo-resumo.md
Ver regras do ambiente           → KNOWLEDGE_ARCHITECTURE.md (este arquivo)
O que ignorar                    → medhub-ui-refresh-main/, history/legacy/, Fichas/, Memorex/
```

---

## 8. Estado Canônico

- **SSOT de dados:** `ipub.db` (erros, FSRS, cronograma) — não commitar
- **SSOT documental:** `ESTADO.md`
- **SSOT de conhecimento clínico:** `Temas/`
- **SSOT de workflows:** `.agents/workflows/`
- O Obsidian é **interface de navegação**, não segunda fonte de verdade
- Notas do Obsidian não substituem `ESTADO.md`

---

## 9. Memória de Agentes (Camadas 2 e 3)

MedHub opera com três camadas de memória complementares. Detalhes em `MEMORY_ARCHITECTURE.md`.

| Camada | Backend | Escopo | Responsável |
|---|---|---|---|
| Camada 1 | Repositório git (Temas/, ipub.db, history/) | Cross-session, canônico | Agente + dev |
| Camada 2 | `medhub_memory.db::checkpoints` (SqliteSaver) | Within-thread, restaurável | LangGraph |
| Camada 3 | `medhub_memory.db::memory_store` (SQLiteMemoryStore) | Cross-thread, longa duração | LangMem |

**Regra:** conteúdo da Camada 1 **nunca** entra nas Camadas 2/3. Memória longa = preferências, padrões de fraqueza, regras procedurais e insights episódicos.
