# Audit Report: medhub-rag-layer-part-1

> Auditado em: 2026-04-05
> Spec: `.vibeflow/specs/medhub-rag-layer-part-1.md`

**Verdict: PASS**

---

### DoD Checklist

- [x] **1. `app/engine/rag.py` com 4 funções + ImportError guard**
  `get_collection()`, `index_resumo(path: Path, collection=None) -> int`, `index_all(resumos_dir: str = "resumos") -> dict[str, int]`, `search(query, n_results, area) -> list[dict]` — todas presentes e com assinaturas corretas. `_CHROMA_AVAILABLE = False` quando chromadb ausente; importável sem erro.
  Evidence: `rag.py:24-29` (try/except ImportError), `rag.py:43-227` (4 funções)

- [x] **2. `_chunk_by_headers()` implementa as 3 regras**
  — Split em `## ` e `### ` via `re.match(r"^#{2,3} ", line)` ✓
  — Merge < 100 chars no anterior (testado: "Sub-curta" de 5 chars foi mergeada na anterior) ✓
  — Split > 1500 chars no `\n\n` mais próximo do ponto médio: algoritmo `left/right = rfind/find("\n\n")`, escolhe o mais próximo de `mid` ✓
  — Retorna `list[dict]` com chaves `header` e `text` ✓
  Evidence: `rag.py:64-139`; testes rodados → merge rule PASS, split rule PASS (2 chunks de 1121+1121 chars a partir de texto de ~2400 chars)

- [x] **3. `tools/index_resumos.py` CLI funcional**
  Argparse com `--dir` ✓; loop per-file `for filename, count in sorted(results.items())` imprime contagem por arquivo ✓; `sys.exit(1)` em todos os casos de erro (chromadb ausente, diretório não encontrado, falha de conexão Ollama) ✓; exit 0 implícito ao completar sem erro ✓
  Evidence: `tools/index_resumos.py:22-76`

- [x] **4. `get_topic_context()` retorna `relevant_chunks` como 6ª chave**
  Chave inicializada a `[]` no dict `result` (linha 110). Bloco 5 usa lazy import `from app.engine.rag import search as rag_search` dentro de `try/except Exception: pass` — nenhuma exceção propaga. Quando chromadb ausente: `search()` retorna `[]` via guard `_CHROMA_AVAILABLE`. Cada item tem `text`, `metadata`, `distance`.
  Evidence: `get_topic_context.py:110` (inicialização), `get_topic_context.py:162-167` (bloco 5)

- [x] **5. `data/chroma/` em `.gitignore`**
  `.gitignore` linha 8: `data/chroma/`
  Evidence: `.gitignore:8`

- [x] **6. Quality gate**
  — `import sqlite3` ausente em `rag.py` ✓
  — `import chromadb` presente apenas em `rag.py` e `tools/index_resumos.py` (varredura completa de `app/**/*.py` e `tools/*.py`) ✓
  — Sem violações dos Don'ts de `conventions.md` ✓
  Evidence: verificação programática (grep em todos os arquivos Python)

---

### Pattern Compliance

- [x] **db-access-layer** — ChromaDB isolado em `app/engine/rag.py` exatamente como SQLite está isolado em `app/utils/db.py`. Nenhuma página ou módulo externo importa chromadb diretamente. `search()` retorna `list[dict]` tipado (não raw cursor rows). Safe default em caso de falha (`[]`).

- [x] **error-insertion-pipeline** — `tools/index_resumos.py` segue padrão: `argparse` com `--dir` explícito, `sys.path.insert(0, project_root)`, mensagens human-readable em stdout, `sys.exit(1)` em falha. Sem finally-close equivalente (ChromaDB não tem conexão explícita para fechar — correto).

---

### Convention Violations

Nenhuma.

---

### Observação Técnica (não bloqueia PASS)

`_chunk_by_headers()` não inclui o header da seção no texto do chunk — apenas armazena em `metadata["section"]`. Para recall, seria levemente melhor prefixar `f"## {header}\n{text}"` no campo `documents[]` do upsert, para que o embedding carregue o contexto da seção. Não é requisito do spec — melhoria pontual para v1.

---

### Budget

Arquivos alterados: 4 / ≤ 6

---

### Tests

`pytest tools/test_memory.py` → **4/4 PASS** (testes pré-existentes, não relacionados ao RAG — regressão limpa)

---

### Overall

**PASS — pronto para Part 2.**

Run: `/vibeflow:implement .vibeflow/specs/medhub-rag-layer-part-2.md`
