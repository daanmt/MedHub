# MedHub

> **Adaptive medical-residency study system.** Second instance of the same context-harness pattern that drives the Daktus CDSS pipeline, applied to a different domain: metacognitive learning. Each wrong answer triggers a closed loop — structured error logging, RAG-backed clinical summary refinement, and FSRS spaced-repetition scheduling — that compounds across sessions.

**Status:** in active use for IPUB/UFRJ residency preparation

---

## What It Is

MedHub is a state-driven adaptive study environment for medical residency exams. The thesis: a study system that *learns with the student* by closing the loop between failure, diagnosis, knowledge, and retention.

Every wrong answer on a practice question triggers three simultaneous events:

1. **A structured record** with diagnostic metadata is written to the SQLite store (`ipub.db`).
2. **The corresponding clinical summary** in `Temas/` is refined (or created) to address the conceptual gap.
3. **A new entry** is scheduled in the FSRS spaced-repetition engine.

The result is a cumulative, cross-session learning loop. The same architecture used in production for clinical content (skill-based context, externalized state, markdown contracts) is the architecture used here for personal knowledge.

---

## The Architectural Connection

MedHub is the second proving ground for the **context-harness pattern** I developed independently while building the [Daktus CDSS pipeline](https://github.com/daanmt/agente-daktus-content):

| Element | Daktus pipeline | MedHub |
|---|---|---|
| State source of truth | `ESTADO.md` | `ESTADO.md` |
| Session continuity | `HANDOFF.md`, `history/session_NNN.md` | `HANDOFF.md`, `history/session_NNN.md` |
| Agent contracts | `tools/skills/*.md` | `.agents/workflows/*.md` |
| Domain knowledge | `referencia/`, `especialidades/` | `Temas/` (Obsidian vault) |
| Model agnosticism | Markdown-based instructions | Markdown-based instructions |
| Boot protocol | `CLAUDE.md` | `AGENTE.md`, `CLAUDE.md` |

The pattern was not transferred from a framework. It emerged independently in both projects because both have the same structural needs: portability across LLMs, externalized state, auditable contracts, deterministic gates around probabilistic reasoning.

---

## How It Works

```
Wrong answer on a practice question
    │
    ▼
┌────────────────────────────────────────────────────┐
│  Closed Loop                                       │
│                                                    │
│  1. Structured error logging  →  ipub.db (SQLite)  │
│  2. Clinical summary refined  →  Temas/*.md        │
│  3. FSRS entry created        →  ipub.db           │
└────────────────────────────────────────────────────┘
    │
    ▼
Cumulative knowledge base
    │
    ▼
RAG retrieval over Temas/ + PDFs (Ollama + Obsidian vault)
    │
    ▼
LLM generates: flashcards, refined summaries, weak-area reinforcement
```

---

## Key Design Decisions

**Markdown vault as knowledge layer.** Clinical summaries live as Obsidian-formatted `.md` files in `Temas/`, organized by area (Cirurgia, Clínica Médica, GO, Pediatria, Preventiva). Human-readable, version-controllable, navigable as a knowledge graph.

**RAG with local embeddings.** Retrieval is built on Ollama running locally for embedding inference and an Obsidian-backed semantic vault. Local-first by design — no external dependency on cloud embedding APIs for personal study material. The knowledge base never leaves the machine.

**SQLite as single source of truth for operational state.** `ipub.db` holds errors, FSRS scheduling, and metadata. One file, no infrastructure, fully portable.

**Workflows as markdown contracts.** `.agents/workflows/*.md` define task protocols (analyze questions, create summaries, generate reinforcement, log sessions) that any LLM can execute. Switch the model, keep the protocol.

**Deterministic data layer around probabilistic reasoning.** Question analysis follows a 9-step explicit protocol (`Tools/comando de analise de questao.md`); summary formatting follows a strict spec (`Tools/estilo-resumo.md`); insertion into `ipub.db` is a deterministic CLI (`Tools/insert_questao.py`). The LLM reasons; the harness enforces.

---

## Repository Structure

```
MedHub/
│
├── AGENTE.md              # bootstrap protocol (read first)
├── ESTADO.md              # canonical snapshot
├── HANDOFF.md             # operational state (next step)
├── roadmap.md             # product direction
│
├── ipub.db                # SSOT for errors, FSRS, schedule
├── flashcards_cache.json  # LLM-generated flashcard cache
│
├── .agents/workflows/     # portable task protocols
│   ├── analisar-questoes.md
│   ├── criar-resumo.md
│   ├── registrar-sessao.md
│   └── gerar-reforco.md
│
├── Temas/                 # clinical knowledge base (Obsidian)
│   └── INDEX.md           # navigation hub
│
├── history/               # session logs
├── Tools/                 # utility scripts and quality specs
├── app/                   # Streamlit multipage app
└── streamlit_app.py       # entry point
```

---

## Getting Started

```bash
# 1. Read AGENTE.md (mandatory boot protocol)
# 2. Read ESTADO.md (canonical snapshot)
# 3. Read HANDOFF.md (where the last session stopped)
# 4. Use the appropriate workflow from .agents/workflows/

# Dashboard:
streamlit run streamlit_app.py
```

---

## Tech Stack

Python · TypeScript (UI components) · Streamlit · SQLite · Plotly · Ollama (local embeddings) · Obsidian vault (semantic knowledge layer) · FSRS (spaced-repetition algorithm) · pdfplumber / PyPDF2 · Markdown-based agent contracts

---

## About

Built and maintained by [Daniel Martins](https://www.linkedin.com/in/danielmartinsf), final-year medical student at UFJF preparing for IPUB/UFRJ residency.

Background: engineering (EFOMM — systems modeling, automation) + medicine (UFJF, final-year). I build AI systems for high-stakes domains where the cost of error is real. The architecture I built for production clinical content turned out to be the architecture I needed for my own learning.
