---
type: snapshot
layer: root
status: canonical
relates_to: [AGENTE, roadmap]
---

# ESTADO — MedHub

*Atualizado: 2026-06-03 (sessão 074) | Ferramenta: Claude Code (Opus 4.8)*

> **Boot:** ler [`AGENTE.md`](AGENTE.md) primeiro — protocolo, convenções, decisões críticas e arquitetura de memória vivem lá. Este arquivo só responde *onde estamos hoje*.

---

## Metas

- **Marco ENAMED (prioridade):** 12.000 questões até 13/09/2026 — ritmo alvo ~86q/dia (projeções no `/performance`)
- **Marco ENARE:** 17.000 questões até 10/2026 (Custo/Q: R$ 0,24)
- **Meta Final:** 23.000 questões até 12/2026 (Custo/Q: R$ 0,20)
- **Indicador Atual (Maio/2026):** 3.170 / 12.000 ENAMED — faltam ~8.830 q
- **Performance Geral:** 80,4% (2.549 acertos / 3.170 questões — fonte: `sessoes_bulk`, 100% conciliada com planilha Drive em 03/06)
- **Resumos consolidados:** 44+ em `resumos/`
- **Erros estruturados no `ipub.db`:** 200+ (número exato no Dashboard)

---

## Últimas 10 sessões

**2026-06-03 | Claude Code (sessão 074):** **Pivot Agent-First fechado (Ondas A-D commitadas).** Retomada da sessão interrompida: Onda D (Streamlit Encolhe) completada — `2_estudo.py` vira Caderno de Erros read-only (FSRS Player removido em favor de `/revisar`), `flashcard_front/back` e `get_next_due_card` removidos, `get_caderno_detalhado` em `db.py`. Audit **PASS** (6/6 DoD, pytest 4/4 + test_fsrs 14/14). Trabalho acumulado das Ondas A-C herdado e commitado atomicamente por onda (staging por hunk em `db.py`): adapter py-fsrs + `/revisar` + `fsrs_queue.py` (A), cards metacognitivos + aposentadoria de `regenerate_cards{,_llm}.py` (B), `/importar-planilha` + `importar_sessoes.py` (C). Streamlit agora = Dashboard + Caderno + Biblioteca.
**2026-05-27 | Claude Code (sessão 073):** **Consolidação do harness em fluxo único.** Audit em paralelo (3 agentes A/B/C → ~666 linhas em `artifacts/audits/harness/`, gitignored) identificou duplicação skills×workflows e staleness em `.vibeflow/patterns/`. 7 commits atômicos: contrato §7.2 em AGENTE (skills = referência, workflows = orquestração que invoca skills sem copiar), fix de 3 bugs em workflows (8-arg CLI stale, `Tools\` casing, backslash path), correção da staleness em `domain-engine-api.md` (5→2 exports), 4 module docstrings canônicos (`db.py`, `styles.py`, `fsrs.py`, `insert_questao.py`), replace-all `Temas/` → `resumos/` em 7 arquivos. Zero behavioral change. `.claude/settings.local.json` continua em separate PR.
**2026-05-27 | Claude Code (sessão 072):** **Housekeeping + auditoria técnica do repo.** Sweep de código (10 commits: branch hygiene, MIT LICENSE, `init_db.py` schema fix, README rewrite, untrack `.obsidian/workspace.json`, requirements.txt pinned, delete 5 orphan modules, archive 6 one-shot migrations, delete 4 engine/memory API orphans, build `tools/eval/` retrieval eval com baseline `R@5=0.778 / MRR@10=0.657` substituindo folklore não-reproduzível). Meta-layer cleanup (4 commits: prune 10 stale docs incl. `.planning/codebase/*` + `OVERVIEW.md`; mark `.vibeflow/specs+prds+audits` archived; `history/INDEX.md` + move sessions 001-028 para `legacy/`; consolidação dos 6 docs raiz em 4 — `AGENTE.md` expandido, `CLAUDE.md` stub, `ESTADO.md` slim, `roadmap.md` trim). Push para origin; About+topics curados no GitHub.
**2026-04-23 | Claude Code (sessão 071):** **Análise de Úlceras Genitais (43q/38a, 5 erros, 3 eixos metacognitivos) + criação da skill `/performance` via ciclo vibeflow completo (discover→spec→implement→audit).**
**2026-04-16 | Antigravity (sessão 070):** Análise Preventiva (23q/18a, 5 erros sobre DO e notificações compulsórias) + bulk register.
**2026-04-16 | Gemini 3.1 Pro (sessão 069):** Resumo `Sistemas de Informação em Saúde` (SIM, SINAN, SINASC, SISAB).
**2026-04-16 | Gemini 3.1 Pro (sessão 068):** Cirurgia Infantil (44q/40a, 4 erros) + fix de 197 FKs órfãs + `data_sessao`.
**2026-04-16 | Antigravity (sessão 067):** Arquitetura `sessoes_bulk` + migração histórica (3.020q, 79,9%) + dashboard reescrito.
**2026-04-10 | Antigravity (sessão 066):** Análise Síndromes Hipertensivas (6 erros, IDs 349-359) + bugfixes em `insert_questao.py`.
**2026-04-09 | Antigravity (sessão 065):** Resumo `Síndromes Hipertensivas na Gestação` (ZUSPAN/PRITCHARD).
**2026-04-07 | Antigravity (sessão 064):** RAG v2 (multi-query Raw+HyDE, ThreadPoolExecutor, BM25 estrutural-depois-desabilitado, `.env`).

> Histórico completo: [`history/INDEX.md`](history/INDEX.md).

---

## Próximos passos

Ver [`ROADMAP.md`](ROADMAP.md) — Linhas Evolutivas.

**Prioridades imediatas (guiadas pelo cronograma — SSOT: `Cronograma de Reta Final.xlsx` no Drive, ver `/importar-planilha`):**

1. **Arboviroses:** fechar Revisão + bloco de questões (Revisão por Questões com Meningites e Sepse na semana 22–26/06). Resumo já existe (`resumos/Clínica Médica/Infectologia/Arboviroses.md`) — acumular armadilhas conforme erros.
2. **Diabetes (bloco em curso):** criar resumo `Diabetes Mellitus - Complicações Crônicas` (gap — DM2 e Compl. Agudas já existem); Teoria é da semana 01–05/06 e a Revisão por Questões do bloco DM completo fecha em 15–19/06.
3. **Meta volumétrica:** ENAMED 12k até 13/09 exige ~86q/dia — priorizar blocos de Revisão por Questões.
4. **Pipeline RAG inverso:** integrar `get_topic_context()` com `app/engine/rag.py` (688 chunks já indexados).
5. **Busca semântica na Biblioteca:** `st.text_input` em `app/pages/3_biblioteca.py` chamando `rag.search()`.

---

## Repositório

```
GitHub: github.com/daanmt/MedHub
Local:  C:\Users\daanm\MedHub
```

*Ao final de cada sessão: atualizar este arquivo e registrar em `history/`.*
