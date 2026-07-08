# Decision Log
> Newest first. Updated automatically by the architect agent.

## 2026-07-08 — Sync de conclusão real do cronograma (xlsx Drive): reusar `preparacao_estado`, não arquivo novo

**Contexto:** Achado F33 (`AUDITORIA_MEDHUB.md`) — o boot recomendava temas já concluídos porque `day_plan.py`/`grade.json` são calendário-driven e nunca liam o marcador de conclusão real (tema riscado) do xlsx `Cronograma de Reta Final.xlsx` do Drive. PRD/spec/implement/audit completo (`.vibeflow/{prds,specs,audits}/cronograma-sync-conclusao-drive.md`), verdict **PASS**.

**Decisão:** o PRD original propunha um arquivo novo `core/cronograma/conclusao_drive.json` (gitignored). O gen-spec descobriu que já existe exatamente o mecanismo necessário — `preparacao_estado` (tabela chave/valor/`atualizado_em`/`fonte` em `ipub.db`, criada pelo PRD `orquestracao-preparacao` part-1, 2026-07-06) — e o reusou (nova chave `cronograma_conclusao_drive`) em vez de duplicar lógica de cache/staleness. Matching entre `grade.json` (PDF, 1 task = 1 tema) e o xlsx (bundla vários temas por célula) é por `(semana, tema normalizado, tipo_norm)`, nunca por índice de task; sem match = `concluido:false` (conservador — nunca assume feito sem confirmação positiva do tachado).

**Pitfall (doc↔código drift, mesma classe do F33):** `core/contracts/cronograma-contract.md` v1.0 (Cláusula 5) ainda descrevia "o único write permitido é o ponteiro de texto `Próxima = SNN` em HANDOFF/ESTADO" — mas esse caminho já estava **deprecado** desde 2026-07-06 (`day_plan.py::_resolver_semana_conteudo()` emite `[WARN] POSICAO_VIA_TEXTO`). O contrato nunca foi atualizado quando o SSOT migrou pro db. Corrigido nesta feature (Cláusula 5 v1.1). **Regra geral: quando um PRD/spec migra o mecanismo de persistência de um sistema já normatizado por contrato, atualizar o contrato NO MESMO spec — não depois.**

**Pitfall (falso positivo de encoding):** a leitura do xlsx via MCP + prints em scripts ad-hoc no console do Windows (cp1252) mostrava acentuação corrompida (`"Doen�as"`), levando a crer que os dados vinham corrompidos do Drive. Não vinham — era só o console sem `sys.stdout.reconfigure(encoding="utf-8")` (mesmo pitfall de 2026-04-23 abaixo, mas na leitura via MCP em vez de emoji). O matching funciona corretamente com os dados reais (UTF-8 íntegro em memória); a normalização por `unicodedata` (strip de acentos) foi implementada mesmo assim como rede de segurança — inofensiva mesmo sem corrupção real.

---

## 2026-07-05 — Invariantes de estado executáveis (F1/F6) + runtime canônico é o Python do sistema

**Contexto:** Part 1 do PRD engenharia-ledger (`.vibeflow/audits/engenharia-ledger-part-1-audit.md`, PASS). Transplante do padrão Executable-State-Reconcile: `auto_check.py::check_session_pointer()` (ponteiro do HANDOFF <= max(history/session_NNN)+1; WARN `SESSION_POINTER_DRIFT`, warning-first) e `day_plan.py --handoff-block` (bloco numérico do HANDOFF vira derivado do db — números digitados à mão foram a raiz do F6).

**Decisão:** invariante de governança novo entra como check do `auto_check` (nunca disciplina textual solta); número de estado em doc de governança é derivado por CLI, nunca digitado. Hooks de sessão agora versionados em `.claude/settings.json` com `$CLAUDE_PROJECT_DIR` (F13) — `settings.local.json` guarda só o específico da máquina.

**Pitfall (runtime):** o runtime canônico dos CLIs é o **Python do sistema** (Python312) — a `.venv/` está stale e NÃO tem o pacote `fsrs` (o `app/utils/fsrs.py` importa `from fsrs import Scheduler, Card, Rating`, py-fsrs de referência); rodar tools pela `.venv` quebra. Confirma também que `fsrs-review-flow.md` (pattern doc) está desatualizado (mostra FSRS custom) — regenerar via /vibeflow:analyze, não editar à mão.

---

## 2026-07-04 — Heurística `material_indicado` (extensivo vs resumo): menção textual, não `tipo==teoria`

**Contexto:** Parte 4 do PRD de Autogovernança (`.vibeflow/audits/autogovernanca-proativa-part-4-audit.md`, PASS). O gatilho antigo em `tools/cronograma.py` (`tipo_norm=='teoria' OR /extensivo/`) marcava 279/352 tasks (79%) como extensivo — esvaziava a calibração (quase tudo virava D10). Novo critério (`cronograma.py:179`): `material_indicado='extensivo'` só quando o `raw` do PDF menciona "Extensivo"/"Livro Digital Completo" **E** a task **não** é de revisão (`revis[ãa]o`). Resultado pós-`--rebuild`: 155 extensivo / 197 resumo = 44% (n_tasks=352, total=10218 preservados).

**Decisão:** A Technical Decision da spec dizia "menção a Extensivo E ausência de 'Resumo'", mas "Resumo" ocorre 694× no PDF (estrutural, não discriminante) — usá-lo como exclusão zeraria a marcação. Substituído pela **contraparte semântica real**: exclusão por **revisão** (revisar o LDI já estudado ≠ leitura extensiva fresca). Ancorado no DoD mensurável (< 60%).

**Precedência D10 (G5):** material extensivo **nunca** sobrescreve nota explícita do usuário (`fonte='usuario'`). Só a inferência sem nota recebe floor 9 (degrau D10) + sinal `deep_research: true`. A regra é **única e verbatim** em `tools/day_plan.py`, `core/contracts/revisao-calibrada-contract.md` e `AGENTE.md §1.2`.

**Pitfall:** Ao editar `AGENTE.md`/contrato, preservar as strings-âncora que `tools/test_revisao_calibrada.py` faz grep (`test_contrato`/`test_agente`/`test_degrau_mecanico`) — rodar a suíte após cada edição documental.

---

## 2026-07-04 — Linter de resumos em 2 severidades (BLOCK/WARN); regras novas nascem WARN

**Contexto:** Parte 2 do PRD de Autogovernança (`.vibeflow/audits/autogovernanca-proativa-part-2-audit.md`, PASS). `tools/audit_resumos.py` ganhou modelo de duas severidades: BLOCK (exit 1, bloqueia commit) para as regras vigentes (Armadilhas ausente, tabela ASCII, `UnicodeDecodeError`) e WARN (exit 0, só adverte, agregado por tipo) para regras novas (frontmatter §5.2, encoding não-ASCII proibido `→ — – $\rightarrow$`). `errors='ignore'` removido da leitura. `test_roundtrip` isolado em cópia temp do `ipub.db`. Guard de `fsrs` na suíte com mensagem clara.

**Decisão:** Warning-first — regra nova **nasce WARN** e só vira BLOCK "quando a base zerar" (decisão do usuário). O exit code vem de `block_total`; `auto_check` distingue WARN de BLOCK no relatório via linha machine-readable `[AUTO-CHECK-META] BLOCK_TOTAL=x WARN_TOTAL=y` (não reimplementa a regra).

**Pitfall (contradição de spec):** A DoD 1 listou "emoji em header" como regra BLOCK "vigente", mas ela **nunca** foi enforçada e a base tem 28+ headers com `⭐`/`⚠️`/`🔴` legítimos — promovê-la a BLOCK quebraria a DoD 3 (`auto_check --all` exit 0). Resolução: **não introduzida**. Se for lintar emoji-em-header no futuro, nasce WARN e exige antes uma decisão sobre os marcadores que a base usa de propósito. Regra geral: ao adicionar regra de linter, cruzar contra a base real (`auto_check --all`) ANTES de escolher a severidade.

**Encoding:** `←`/`…` são legítimos e preservados — a lista de proibidos é fechada (`→ — – $\rightarrow$`), não "todo não-ASCII".

---

## 2026-06-03 — FSRS Player do Streamlit removido: revisão é conversacional (`/revisar`)

**Contexto:** Onda D (audit PASS em `.vibeflow/audits/onda-d-streamlit-encolhe-audit.md`). Com a Onda A, a revisão espaçada migrou para `/revisar` + `tools/fsrs_queue.py` (funciona via celular). O player do `2_estudo.py` tab2 ficou redundante e carregava bugs conhecidos (closure capturando card errado, `fc_idx % total` mascarando overflow, `sqlite3` cru em página).

**Decisão:** Remover o player em vez de consertá-lo. `2_estudo.py` vira **Caderno de Erros read-only** via `db.py::get_caderno_detalhado(area=None)`. Símbolos mortos removidos junto: `db.py::get_next_due_card()` (bug latente — colunas `frente`/`verso` inexistentes) e `styles.py::flashcard_front/back` (0 callers). Streamlit agora é só Dashboard + Caderno + Biblioteca.

**Pitfall:** Pattern docs em `.vibeflow/patterns/` ficaram stale (referenciam player/tabs/`flashcard_front`) — regenerar via `/vibeflow:analyze`, não editar dentro dos marcadores auto.

---

## 2026-04-23 — CLIs Python com emoji: forçar UTF-8 no stdout (Windows cp1252)

**Contexto:** Implementação de `tools/performance.py` (skill `/performance`) usa emojis de faixa (🟢🟡🟠🔴🟣) para classificação visual de custo/questão. Primeira execução em Windows crashou com `UnicodeEncodeError: 'charmap' codec can't encode '\U0001f7e3'` — o cp1252 default do Windows não cobre planos astrais Unicode, e ao rodar via subprocess (como Claude Code faz via Bash) o stdout é cp1252, não UTF-8.

**Decisão:** CLIs em `tools/` que imprimem emoji DEVEM incluir no topo de `main()`:
```python
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass  # Python < 3.7
```

**Pitfall para futuros scripts:** `insert_questao.py` e `registrar_sessao_bulk.py` também sofrem disso (imprimem `quest�o` em vez de `questão`), mas com caracteres pt-BR o cp1252 degrada sem crashar. Com emojis do plano astral (U+1F7E0+), crasha. Para qualquer novo CLI com emoji, aplicar a reconfiguração.

---

## 2026-04-23 — Drift de taxonomia em `sessoes_bulk`: aceitar como diagnóstico visível

**Contexto:** Auditoria de `performance.py` expôs duas inconsistências de dados:
1. `"Obstetricia"` (sem acento) no DB vs `"Obstetrícia"` em `AREAS_VALIDAS` — falsamente listada como gap.
2. `"GO"` criado como área paralela a Ginecologia/Obstetricia na sessão 071.

**Decisão:** Não normalizar em `performance.py`. O script deve revelar fielmente o drift. Futuras consolidações de dados em SQL migration script separado (fora do escopo do v0). Correção cirúrgica:
- Sessões futuras: usar exatamente os nomes de `AREAS_VALIDAS` de `registrar_sessao_bulk.py` ao chamar `--area`.
- Para dados históricos: criar `tools/normalizar_areas.py` quando prioridade justificar (tech debt).

---

## 2026-04-07 — BM25 como re-ranker pós-Chroma: alpha=0.8, Threshold Fixo, Desabilitado por Regressão

**Contexto:** O BM25 foi implementado para resolver colisões léxicas (Placenta vs DPP), mas degradou o Recall global (90% → 73%) ao elevar termos genéricos ("tratar", "diagnóstico") de outras especialidades.

**Decisão:**
- **Alpha=0.8:** Redução drástica da influência léxica para evitar falsos positivos em corpus médico denso.
- **Threshold Fixo (0.35):** Normalização do score coseno ancorada no limite de corte do RAG, não no máximo relativo do lote recuperado. Isso garante estabilidade de score independente da qualidade do vizinho.
- **Desabilitado em Produção:** O reranker BM25 permanece no código (`_bm25_rerank`), mas a chamada em `search()` foi comentada/removida. **Tech Debt para /discover**: O sistema performa melhor com Coseno Puro + HyDE + Context Propagation no momento.

**HyDE cache & Parallellism:** 
- `_HYDE_CACHE` module-level p/ evitar re-chamadas de API na mesma sessão.
- `ThreadPoolExecutor` no `search()` dispara HyDE e `get_collection()` em paralelo: latência final = `max(LLM, DB)`, não a soma. Redução média de ~1s no TTFT.


---

## 2026-04-05 — Arquitetura RAG: dois índices, papéis distintos, sem conflito

**Contexto:** O projeto tinha `obsidian-notes-rag` MCP instalado sem clareza sobre seu papel. Após diagnóstico (sessão 063), ficou claro que coexistem dois sistemas ChromaDB com propósitos distintos.

**Decisão:**

| Sistema | Path | Corpus | Consumido por |
|---|---|---|---|
| `app/engine/rag.py` | `data/chroma/` (688 chunks) | `resumos/**/*.md` (44 arquivos clínicos, chunking H2/H3) | `get_topic_context()`, `generate_contextual_cards()`, `3_biblioteca.py` — via Python import |
| `obsidian-notes-rag` MCP | `AppData/Local/obsidian-notes-rag/medhub/` (862 chunks) | Vault completo (147 md, inclui ESTADO, history, etc.) | Agentes externos via MCP protocol |

**RAG canônico = `app/engine/rag.py`**. É o sistema fundação, integrado ao engine, com fallback silencioso (`_CHROMA_AVAILABLE = False → []`). Não depende de processo externo.

**MCP `obsidian-notes-rag` = auxiliar opcional**. Útil para agentes que precisam buscar qualquer nota do vault (não só resumos clínicos). Bug conhecido: o servidor sobe sem `--provider ollama` em sessões Antigravity (lê configuração global, não o `.mcp.json` local). O `.mcp.json` no repositório está correto — precisa restart do servidor MCP para herdar `--provider ollama --model nomic-embed-text:latest`.

**Eles não se interferem**: paths físicos distintos, clients ChromaDB independentes.

**Pitfall:** O MCP falha silenciosamente com `OPENAI_API_KEY not set` quando o servidor sobe sem `--provider ollama`. Não confundir com falha do RAG interno — são sistemas independentes.

**Grep de referências RAG:** `grep -rn "rag\|chroma\|obsidian" app/ tools/ --include="*.py"` para auditar referências antes de qualquer refatoração.

---

## 2026-04-05 — DROP COLUMN quebra audit scripts que referenciam colunas legacy

**Contexto:** `medhub-cleanup` spec dropou `frente`/`verso` de `flashcards`. `tools/audit_flashcard_quality.py` usava essas colunas em `EFF_FRONT`/`EFF_BACK` (CASE ELSE fallback), quebrando com `OperationalError: no such column: verso`.

**Pitfall:** Ao dropar colunas de schema migration, verificar TODOS os scripts em `tools/` que referenciam essas colunas — não apenas os listados no scope da spec.

**Fix:** Simplificar `EFF_FRONT`/`EFF_BACK` para `COALESCE(NULLIF(TRIM(campo_v5), ''), '[placeholder]')` — sem ELSE fallback para colunas legacy.

**Grep de segurança pré-DROP:** `grep -rn "frente\|verso" tools/ --include="*.py"` antes de executar qualquer DROP COLUMN de colunas com nomes comuns.
