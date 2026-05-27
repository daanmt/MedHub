"""
run_eval.py — minimal retrieval eval for app.engine.rag.search.

Loads a fixture of (query, expected_resumo_path) pairs and reports
Recall@k and MRR@10 against the live ChromaDB index. Writes a markdown
report to tools/eval/REPORT.md and prints a summary to stdout.

Requirements at runtime:
  - Ollama running locally with nomic-embed-text pulled
  - ChromaDB persistent index at data/chroma/ (run tools/index_resumos.py first)
  - Optional: ANTHROPIC_API_KEY in .env for HyDE (otherwise falls back to
    Ollama llama3, then to identity)

Usage:
  python tools/eval/run_eval.py                    # default: HyDE on
  python tools/eval/run_eval.py --no-hyde          # compare without HyDE
  python tools/eval/run_eval.py --both             # run both configs
  python tools/eval/run_eval.py --output PATH      # custom report path

Honest scope (see tools/eval/README.md):
  - 18 queries → ~22pp 95% binomial CI at this n; subtle ranking
    changes are inside the noise band.
  - Author-defined gold set, not blind. Mitigation: include misses on
    purpose, do not edit queries to fit retrieval results.
  - Measures "did we retrieve the right file", not "did we retrieve the
    right section" and not retrieval→generation end-to-end.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Make the project root importable when running from anywhere
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from app.engine.rag import search, _CHROMA_AVAILABLE  # noqa: E402

FIXTURE_PATH = REPO_ROOT / "tools" / "eval" / "queries.json"
DEFAULT_REPORT_PATH = REPO_ROOT / "tools" / "eval" / "REPORT.md"


def normalize_source(s: str) -> str:
    """Return repo-relative POSIX path for a chunk metadata source."""
    p = Path(s)
    try:
        p = p.resolve().relative_to(REPO_ROOT)
    except (ValueError, OSError):
        pass
    return str(p).replace("\\", "/")


def load_fixture(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        fixture = json.load(f)
    missing = [
        e["expected_resumo_path"]
        for e in fixture
        if not (REPO_ROOT / e["expected_resumo_path"]).exists()
    ]
    if missing:
        raise SystemExit(
            "Fixture has expected_resumo_path entries that do not exist:\n  "
            + "\n  ".join(missing)
        )
    return fixture


def eval_one(entry: dict, k: int, use_hyde: bool) -> dict:
    hits = search(
        entry["query"],
        n_results=k,
        area=entry.get("area"),
        use_hyde=use_hyde,
    )
    sources = [normalize_source(h["metadata"]["source"]) for h in hits]
    expected = entry["expected_resumo_path"].replace("\\", "/")
    rank = next((i + 1 for i, s in enumerate(sources) if s == expected), None)
    return {
        "id": entry["id"],
        "query": entry["query"],
        "area": entry.get("area"),
        "expected": expected,
        "rank": rank,
        "top_sources": sources[:3],
        "n_hits": len(hits),
    }


def metrics(results: list[dict]) -> dict[str, float]:
    n = len(results)
    if n == 0:
        return {"R@1": 0.0, "R@3": 0.0, "R@5": 0.0, "MRR@10": 0.0, "n": 0}

    def recall_at(k: int) -> float:
        return sum(1 for r in results if r["rank"] is not None and r["rank"] <= k) / n

    mrr = sum(1.0 / r["rank"] for r in results if r["rank"] is not None) / n
    return {"R@1": recall_at(1), "R@3": recall_at(3), "R@5": recall_at(5), "MRR@10": mrr, "n": n}


def _git_sha(path: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "log", "-n1", "--format=%h", "--", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return out.stdout.strip() or "unknown"
    except (OSError, subprocess.TimeoutExpired):
        return "unknown"


def _fixture_hash(fixture: list[dict]) -> str:
    payload = json.dumps(fixture, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def render_markdown(runs: dict[str, dict], fixture: list[dict]) -> str:
    lines: list[str] = []
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines.append("# RAG Retrieval Eval — MedHub\n")
    lines.append(f"_Generated {ts}_\n")
    lines.append(f"- Fixture: `{FIXTURE_PATH.relative_to(REPO_ROOT)}` (sha256[:12] `{_fixture_hash(fixture)}`, n={len(fixture)})")
    lines.append(f"- RAG impl: `app/engine/rag.py` @ git `{_git_sha(REPO_ROOT / 'app/engine/rag.py')}`")
    lines.append(f"- ChromaDB available: `{_CHROMA_AVAILABLE}`")
    lines.append("")
    lines.append("## Summary\n")
    lines.append("| Config | n | Recall@1 | Recall@3 | Recall@5 | MRR@10 |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for label, data in runs.items():
        m = data["summary"]
        lines.append(
            f"| {label} | {m['n']} | {m['R@1']:.3f} | {m['R@3']:.3f} | {m['R@5']:.3f} | {m['MRR@10']:.3f} |"
        )
    lines.append("")
    lines.append("## Per-query detail\n")
    for label, data in runs.items():
        lines.append(f"### {label}\n")
        lines.append("| id | rank | area | query | expected | top-3 sources |")
        lines.append("|---|---:|---|---|---|---|")
        for r in data["per_query"]:
            rank_cell = str(r["rank"]) if r["rank"] is not None else "MISS"
            top3 = "<br>".join(r["top_sources"]) if r["top_sources"] else "_(none)_"
            q = r["query"][:80] + ("…" if len(r["query"]) > 80 else "")
            lines.append(
                f"| `{r['id']}` | {rank_cell} | {r['area'] or '-'} | {q} | {r['expected']} | {top3} |"
            )
        lines.append("")
    lines.append("## Honest caveats\n")
    lines.append("- n=18 → ~22pp 95% binomial CI; point estimates are noisy.")
    lines.append("- Gold set is author-defined and not blind.")
    lines.append("- Measures file-level recall, not section-level. A correct file at the wrong chunk still counts as a hit.")
    lines.append("- No retrieval→generation end-to-end signal. No latency, no cost.")
    lines.append("- Cited folklore numbers (Recall@5 ≈ 0.90 / MRR ≈ 0.708) were measured against an unknown fixture by an unknown procedure; this report supersedes them, it does not confirm them.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-hyde", action="store_true", help="Disable HyDE for the run")
    parser.add_argument("--both", action="store_true", help="Run both HyDE on and HyDE off")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH, help="Report markdown path")
    parser.add_argument("--k", type=int, default=10, help="Max k for MRR window (default 10)")
    args = parser.parse_args()

    if not _CHROMA_AVAILABLE:
        print("ChromaDB not available — install chromadb and re-run.", file=sys.stderr)
        return 2

    fixture = load_fixture(FIXTURE_PATH)

    configs: list[tuple[str, bool]] = []
    if args.both:
        configs = [("hyde=on", True), ("hyde=off", False)]
    elif args.no_hyde:
        configs = [("hyde=off", False)]
    else:
        configs = [("hyde=on", True)]

    runs: dict[str, dict] = {}
    for label, use_hyde in configs:
        print(f"\n[{label}] Running {len(fixture)} queries (k={args.k})…")
        results = [eval_one(e, k=args.k, use_hyde=use_hyde) for e in fixture]
        s = metrics(results)
        runs[label] = {"per_query": results, "summary": s}
        print(
            f"  R@1={s['R@1']:.3f}  R@3={s['R@3']:.3f}  R@5={s['R@5']:.3f}  "
            f"MRR@10={s['MRR@10']:.3f}  (n={s['n']})"
        )

    md = render_markdown(runs, fixture)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(md, encoding="utf-8")
    print(f"\nReport written to {args.output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
