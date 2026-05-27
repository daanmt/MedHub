---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, roadmap]
---

# ESTADO — MedHub

*Atualizado: 2026-05-27 (sessão 072) | Ferramenta: Claude Code (Opus 4.7)*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) primeiro — protocolo, convenções, decisões críticas e arquitetura de memória vivem lá. Este arquivo só responde *onde estamos hoje*.

---

## Metas

- **Meta Final:** 23.000 questões até 12/2026 (Custo/Q: R$ 0,20)
- **Marco ENARE:** 17.000 questões até 10/2026 (Custo/Q: R$ 0,24)
- **Indicador Atual (Abril/2026):** 3.064 / 17.000 — faltam ~13.936 q
- **Performance Geral:** 80,0% (2.453 acertos / 3.064 questões — fonte: `sessoes_bulk`)
- **Resumos consolidados:** 44+ em `resumos/`
- **Erros estruturados no `ipub.db`:** 200+ (número exato no Dashboard)

---

## Últimas 10 sessões

**2026-05-27 | Claude Code (sessão 072):** **Housekeeping + auditoria técnica do repo.** Sweep de código (10 commits: branch hygiene, MIT LICENSE, `init_db.py` schema fix, README rewrite, untrack `.obsidian/workspace.json`, requirements.txt pinned, delete 5 orphan modules, archive 6 one-shot migrations, delete 4 engine/memory API orphans, build `Tools/eval/` retrieval eval com baseline `R@5=0.778 / MRR@10=0.657` substituindo folklore não-reproduzível). Meta-layer cleanup (4 commits: prune 10 stale docs incl. `.planning/codebase/*` + `OVERVIEW.md`; mark `.vibeflow/specs+prds+audits` archived; `history/INDEX.md` + move sessions 001-028 para `legacy/`; consolidação dos 6 docs raiz em 4 — `AGENTE.md` expandido, `CLAUDE.md` stub, `ESTADO.md` slim, `roadmap.md` trim). Push para origin; About+topics curados no GitHub.
**2026-04-23 | Claude Code (sessão 071):** **Análise de Úlceras Genitais (43q/38a, 5 erros, 3 eixos metacognitivos) + criação da skill `/performance` via ciclo vibeflow completo (discover→spec→implement→audit).**
**2026-04-16 | Antigravity (sessão 070):** Análise Preventiva (23q/18a, 5 erros sobre DO e notificações compulsórias) + bulk register.
**2026-04-16 | Gemini 3.1 Pro (sessão 069):** Resumo `Sistemas de Informação em Saúde` (SIM, SINAN, SINASC, SISAB).
**2026-04-16 | Gemini 3.1 Pro (sessão 068):** Cirurgia Infantil (44q/40a, 4 erros) + fix de 197 FKs órfãs + `data_sessao`.
**2026-04-16 | Antigravity (sessão 067):** Arquitetura `sessoes_bulk` + migração histórica (3.020q, 79,9%) + dashboard reescrito.
**2026-04-10 | Antigravity (sessão 066):** Análise Síndromes Hipertensivas (6 erros, IDs 349-359) + bugfixes em `insert_questao.py`.
**2026-04-09 | Antigravity (sessão 065):** Resumo `Síndromes Hipertensivas na Gestação` (ZUSPAN/PRITCHARD).
**2026-04-07 | Antigravity (sessão 064):** RAG v2 (multi-query Raw+HyDE, ThreadPoolExecutor, BM25 estrutural-depois-desabilitado, `.env`).
**2026-04-05 | Antigravity (sessão 063):** Auditoria dos 2 ChromaDB coexistentes (canônico + MCP obsidian-notes-rag).

> Histórico completo: [`history/INDEX.md`](history/INDEX.md).

---

## Próximos passos

Ver [`roadmap.md`](roadmap.md) — Linhas Evolutivas.

**Prioridades imediatas:**

1. **Pipeline RAG inverso:** integrar `get_topic_context()` com `app/engine/rag.py` (688 chunks já indexados) e usar em geração de cards quando reativada.
2. **Busca semântica na Biblioteca:** `st.text_input` em `app/pages/3_biblioteca.py` chamando `rag.search()`.
3. **Meta volumétrica:** processar questões erradas continuamente (meta ENARE 17k até out/2026).
4. **Expansão de conteúdo:** avançar em `resumos/` (GO: DIP e Sangramentos).

---

## Repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao final de cada sessão: atualizar este arquivo e registrar em `history/`.*
