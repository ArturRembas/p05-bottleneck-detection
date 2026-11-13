# P05 — Bottleneck Detection in Processes

**AI Puzzle Framework · Complex Systems Design · MSc in Computer Science · University of Camerino**

**Team:** Artur Rembas, Luca Repupilli, Diego Marinozzi  
**Supervisor:** Prof. Flavio Corradini  
**Planning horizon:** October 2026 – February 2027  
**Project status:** Architecture agreed at the 6 November 2026 checkpoint; implementation and test status must be demonstrated through repository evidence.

## Purpose

P05 is an **autonomous, interoperable process-analysis component** for reconstructing observed workflows from event logs and identifying **candidate bottlenecks**, delays, repetitions, rework, and inefficient hand-offs, with a discrete-manufacturing case study.

The system separates three classes of outputs:

1. **Deterministic observations** — reproducible process models, measurements and evidence computed from supported event-log semantics.
2. **AI-assisted interpretation** — mapping proposals, explanations and candidate interventions, subject to validation and attribution.
3. **Simulation estimates** — conditional outcomes from explicit models, assumptions and parameters; not observed improvements.

A long activity duration or inter-event gap does **not**, by itself, prove the existence of a production-capacity bottleneck or a queue.

## Scope and architecture

The approved project direction includes:

- **Ingestion:** CSV, XES and an OCEL pathway whose precise first-release scope remains open; validation, normalization and AI-assisted semantic mapping with human confirmation.
- **Deterministic core:** Python, Pandas and PM4Py for discovery, directly-follows graphs, variants, time distributions and candidate bottleneck detection.
- **AI layer:** LangGraph-based routing, specialized analysis/retrieval/UI/what-if agents, governed tools, RAG and a separate validated Experience Store.
- **Simulation:** SimPy for controlled benchmarks and optional what-if comparisons.
- **Application and interfaces:** FastAPI + REST/OpenAPI 3.1, read-only MCP tools, Streamlit UI; two Docker containers orchestrated with Docker Compose.
- **Interoperability:** P06 Scheduling, P20 Resource Allocation, P17 Data Analytics and P21 What-if.

**Approved architecture does not mean that every capability has been implemented.** The API contract, detector rules, calibration, authorization and initial MVP use-case subset require detailed review.

## Proposed component layout

```text
core/           # deterministic log ingestion, mining, detection, typed result models
ai/             # proposed agent orchestration, mapping assistance, RAG integration
simulation/     # SimPy benchmark generation and scenario evaluation
api/            # FastAPI application interface and versioned exchange endpoints
ui/             # Streamlit client (must consume API, not bypass the core)
tests/          # unit, integration and benchmark tests
schemas/        # versioned machine-readable contracts
examples/       # explicitly synthetic, non-sensitive examples
docs/           # architecture, source traceability, governance and evaluation
.github/        # issue forms, pull-request template and repository guidance
```

The directory layout is a **proposal for implementation**, not evidence that all modules are operational.

## Current development approach

Start from the existing exploratory prototype and evolve it into a single verifiable path:

```text
Event log → Validation → Confirmed mapping → PM4Py metrics
          → Candidate bottleneck findings → Versioned JSON → FastAPI → Streamlit
```

The deterministic path must remain usable when AI services, document retrieval or simulation are unavailable. Work on modules can proceed in parallel once interfaces are agreed.

## Milestones

| Milestone | Planning target | Intended evidence |
| --- | --- | --- |
| M1 — Architecture & Design | 2026-11-22 | Reviewed requirements/use cases, component boundaries and draft API contracts |
| M2 — Prototype v1 | 2026-12-20 | Tested vertical slice of ingestion, PM4Py, detection, REST and UI |
| M3 — Prototype v2 | 2027-01-31 | Extended AI/RAG, controlled simulation and interaction where validated |
| M4 — Final Delivery | 2027-02-15 | Reproducible evaluation, demo, documentation and integration examples |

These are **group-approved roadmap targets**, not certified academic deadlines or completed deliveries. Read the precise completion proposals in `docs/MILESTONES.md`.

## Getting started

```bash
git clone git@github.com:OWNER/p05-bottleneck-detection.git
cd p05-bottleneck-detection
python3 -m venv .venv
source .venv/bin/activate
```

Replace `OWNER` with the actual GitHub account or organization. Install runtime dependencies from the tracked, tested requirements once the prototype migration PR is merged. The documentation-only scaffold is **not claimed to be runnable**.

## Collaboration

- `main` is the shared integration branch; use short-lived `feat/*`, `fix/*`, `docs/*`, or `chore/*` branches.
- Open a pull request for each coherent change; link relevant issues and include test evidence.
- Never treat exploratory code, mock numbers or synthetic fixtures as verified production results.
- Do not commit API keys, private event logs, confidential documents, virtual environments or generated databases.

See [CONTRIBUTING.md](CONTRIBUTING.md), [Architecture](docs/ARCHITECTURE.md), [Scope and decisions](docs/PROJECT_SCOPE.md), [Use-case catalogue](docs/USE_CASE_CATALOG.md) and [Evaluation](docs/VALIDATION_PLAN.md).

## Source hierarchy and traceability

1. Official AI Puzzle Framework v5 and supervisor instructions.
2. The group decision register (updated 12 November 2026).
3. Consolidated specifications and reviewed technical documentation.
4. Meeting transcripts and notes.
5. Proposals and explorations.

GitHub Issues track work and review; they do **not** by themselves ratify project decisions. A complete use-case catalogue is available, but individual use cases remain **draft candidates** until the group confirms their status and MVP inclusion.

## Data, ethics and limitations

Data must be used lawfully with documented provenance, privacy considerations and permitted redistribution. Human review is required for significant semantic mappings and publication of results to other puzzle pieces. AI interpretations must not rewrite measured values or imply causality without evidence. Scenario outputs are conditional estimates.

## License

**Not yet selected.** This repository is initially intended to be private; do not assume that source code or datasets may be redistributed until the group decides on a license and checks dataset rights.
