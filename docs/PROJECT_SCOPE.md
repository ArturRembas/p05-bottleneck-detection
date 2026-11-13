# Project Scope and Decision Status

**Reference date:** 12 November 2026. **Status:** Summary of available official and group records, not a substitute for the decision register.

## Official requirements (AI Puzzle Framework v5, P05 and common deliverables)

- Analyze timestamped operational events to reconstruct an observed process.
- Identify likely bottlenecks, waiting/non-productive time, rework and process variants.
- Produce an observed process map, stage-level timing distributions, ranked candidate bottlenecks and inefficiency indicators.
- Remain useful independently of other puzzle pieces and document at least one interoperable output mechanism.
- Provide a runnable demonstrator, data/schema/privacy description, evaluation against baseline, machine-readable examples and at least two potential connections to other pieces.
- Account for human oversight, traceability, security, and validation before operational automation.

## Approved group design (checkpoint 2026-11-06; confirmed 2026-11-12)

- Discrete manufacturing; Python + Pandas + PM4Py; SimPy simulation capability.
- Streamlit UI and FastAPI backend as separate Docker containers orchestrated via Docker Compose.
- LangGraph-based AI router/agents, RAG Knowledge Base and separate validated Experience Store.
- REST/OpenAPI 3.1, MCP read-only access, integrations with P06/P20/P17/P21.
- Human confirmation for semantic mapping and before external publication.
- Incremental development and the M1–M4 planning targets.

The planned support for CSV/XES/OCEL and BPMN export is an **approved architectural objective**, while the precise behaviors and scope of first-release support remain open.

## Proposals in this repository kit (NOT group-approved)

- Modular Python package layout and a strictly API-driven Streamlit client.
- Versioned `AnalysisResult` fields and JSON error semantics in draft contract v0.1.
- Three evidence levels (delay hotspot / queue congestion candidate / capacity bottleneck candidate).
- Initial MVP vertical slice, issue labels/PR workflow, acceptance tests and milestone completion definitions.
- Proposed details in the 38 use-case Issue drafts and other planning Issues.

## Open decisions requiring explicit review

- Exact bottleneck ranking, severity thresholds and benchmark ground truth.
- Temporal semantics, queue evidence and available analysis capabilities.
- Detailed OpenAPI/MCP access, security and publication policy.
- MVP use-case subset; supported OCEL behavior and BPMN export fidelity.
- RAG corpus, AI model/runtime, privacy and Experience Store validation.
- Persistent storage, simulation calibration and experimental evaluation.

## Principle

**Approved architecture ≠ implemented feature ≠ experimentally verified outcome.** Each claim in the final report should link to its corresponding source, commit, test or measured experiment.
