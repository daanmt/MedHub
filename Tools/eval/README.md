# RAG Retrieval Eval

Minimal reproducible eval for `app.engine.rag.search`. Replaces the folklore numbers (Recall@5 ≈ 0.90, MRR ≈ 0.708) cited in older internal docs — which had no runner, no fixture, and a phantom expected-resumo file — with measurements that anyone with the repo + Ollama + ChromaDB can reproduce.

## Run

```bash
ollama pull nomic-embed-text      # one-time
python Tools/index_resumos.py     # one-time (or after editing resumos/)
python Tools/eval/run_eval.py     # writes Tools/eval/REPORT.md
```

Options:
- `--no-hyde` — disable HyDE for the run (skips the optional Anthropic / Ollama-llama3 call)
- `--both` — run both `hyde=on` and `hyde=off` for side-by-side comparison
- `--output PATH` — custom report path
- `--k N` — MRR window (default 10)

## Fixture

`queries.json` — 18 (query, expected_resumo) pairs mined from `history/session_*.md`. Each entry has:

- `id` — stable area-prefixed slug (`go-001`, `ped-002`, …)
- `query` — raw string passed to `rag.search()`
- `area` — optional filter; passed to `search(area=...)`
- `expected_resumo_path` — repo-relative path of the gold resumo; must `Path.exists()` at runtime (the runner fails fast otherwise)
- `notes` — provenance (session number / DB id)

## Authoring rules (anti-gaming)

1. **Source from real errors only.** Every entry must come from an actual error logged in `ipub.db` or a real session in `history/`. No synthetic queries.
2. **Gold file must exist at commit time.** The runner asserts `expected_resumo_path` exists before running anything. This prevents the historical trap of citing `[OBS] Sangramentos da Segunda Metade.md` (in the old PRDs) when only `Primeira Metade.md` was ever created.
3. **Do not edit a query to fit retrieval output.** Misses are data. Either fix the chunker, add the missing resumo, or accept the miss.
4. **Do not copy section headers verbatim into queries.** The chunker injects `[Tema (aliases) > Header]` as a context prefix at index time (`rag.py:269`); using a header as the query leaks that prefix and gives an inflated score.
5. **Fixture is append-only** unless an entry is proven malformed (logged in `notes`).
6. Target growth: 30–50 entries once the pattern is proven across more areas.

## What this measures

- **Recall@1 / Recall@3 / Recall@5** — fraction of queries where the gold resumo appears in the top-1 / top-3 / top-5 chunks (by `metadata.source` match).
- **MRR@10** — mean reciprocal rank of the gold resumo within the top-10. `0` for misses.

## What this does NOT measure

- **Section-level retrieval.** A hit means "the right file appeared", not "the right section appeared". A query about ZUSPAN that returns the intro chunk of `Síndromes Hipertensivas` counts as a hit even if the chunk content is irrelevant.
- **Retrieval → generation end-to-end.** No signal on whether the downstream flashcard prompt actually benefited from the retrieved chunks.
- **Latency / token cost.** HyDE makes an LLM call per query; this report doesn't quantify it.
- **Statistical significance at small n.** With n=18, the 95% binomial CI is ~22pp wide. Recall@5 of 0.83 has CI ~`[0.62, 0.95]`. Treat point estimates as directional, not definitive.
- **Production traffic distribution.** Queries here are *what the author analyzed*, not what an agent would receive in live use.
- **Corpus drift.** Adding/renaming a resumo silently invalidates fixture entries — the runner catches non-existent paths but won't tell you a renamed file's old path used to match.

## Comparison with the old folklore

The cited Recall@5 ≈ 0.90 / MRR ≈ 0.708 came from `.vibeflow/prds/rag-hybrid-rerank-hyde-cache.md` and `ROADMAP.md` (attributed to "Sessão 064"). They were measured against an unknown fixture by a manual procedure and reference a `rag_benchmark_report_v2.md` that does not exist anywhere in the repo. The single concrete query in those PRDs (`"Diferença clínica de placenta prévia de DPP"`) points to an expected gold file (`[OBS] Sangramentos da Segunda Metade.md`) that was never created — only `Primeira Metade.md` exists.

This eval supersedes those numbers. Any future Recall@5 / MRR claim about MedHub's RAG layer should reference `Tools/eval/REPORT.md` (with its fixture sha256 and the git sha of `app/engine/rag.py`), not the old folklore.
