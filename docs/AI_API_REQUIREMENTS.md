# P05 — Agent-Facing API Requirements and Risk Tiers

> **Status:** WORKING DESIGN PROPOSAL — group review required.  
> **Related task:** [TASK-06, GitHub issue #11](https://github.com/ArturRembas/p05-bottleneck-detection/issues/11).  
> **Baseline checked:** 24 November 2026.  
> **Purpose:** Define the agent-facing capabilities, interface boundaries and proposed risk policies without claiming that unimplemented operations are available.

## 1. Scope and design constraints

P05 combines deterministic process analysis with AI-assisted semantic mapping, evidence-grounded interpretation, document retrieval and conversational control. This document identifies the *capabilities* required by the agentic layer and their relationship to the backend contract. It is not itself an approved OpenAPI specification or an implementation plan for every capability.

### 1.1 Source and decision status

- **Course and project requirements:** The approved project abstract requires AI-assisted semantic mapping with mandatory human verification before full ingestion, grounded explanations, RAG assistance, interoperable interfaces, and human oversight.
- **Group-approved architecture (reported in project scope):** Python, FastAPI, Streamlit, LangGraph-based router/agents, a RAG Knowledge Base, a separate validated Experience Store, REST/OpenAPI 3.1, and read-only MCP exposure.
- **Layer-level working design (Luca):** Four specialized agents, multi-intent routing with deterministic dispatch, the Tool Registry, Guardrails, R0–R3 risk tiers, and a Human-in-the-Loop (HITL) Gate. These internal details require documentation and confirmation in the group decision register.
- **Current API candidate:** PR #10, OpenAPI 3.1 contract v0.2, remains under review at the date above. Its defined operations must not be presented as functioning application services.
- **Documents pending reconciliation:** SRS v0.2, the consolidated use-case specification and current decision-register entries. This draft does not invent their contents or decision identifiers.

### 1.2 Non-negotiable behavior

1. The LLM **does not compute** process metrics, graph structure, rankings or simulation outputs. Numerical facts come from deterministic tools, with provenance.
2. The human must explicitly confirm or correct semantic mapping **before full ingestion**; no agent may self-approve the mapping.
3. Actions classified R2/R3 require application-enforced human approval. Approval must bind the actor, exact operation, parameters and relevant data/result version.
4. Observed inter-event gaps are not automatically queue waiting times or processing durations, particularly for completion-only logs.
5. Deterministic, AI-generated and simulated outputs remain distinct. AI hypotheses are not evidence of causality.
6. The deterministic path must remain usable when the LLM, RAG or agentic runtime is unavailable.
7. Mock/synthetic fixtures must be identified as synthetic and never served as real operational results.
8. Tool discovery is not authorization. Server-side access controls, policy checks and an explicit allowlist are required independently of LLM choices.
9. Sensitive data sent to cloud models must be minimized and pseudonymized subject to an agreed data-protection policy. R0 does not mean that external data transfer is automatically permitted.

### 1.3 Three distinct interfaces

- **Agent capability:** an intention-oriented operation available to an agent (e.g. `detect_bottlenecks`).
- **Tool adapter:** a typed, policy-controlled implementation that may call a backend endpoint, an AI/RAG service or a UI action.
- **REST endpoint:** an HTTP operation maintained in the shared FastAPI contract. Not every capability requires a distinct REST endpoint, and no new path below is considered approved.

The agent and the dashboard should use the same reviewed backend application services for shared domain actions. UI-only actions and retrieval/model adapters may have distinct bindings. MCP, when implemented, exposes only explicitly authorized read-only capabilities and may not bypass publication controls.

## 2. Existing OpenAPI v0.2 contract (PR #10)

**Source files:** [`api/main.py`](https://github.com/ArturRembas/p05-bottleneck-detection/blob/task-04-openapi-contracts/api/main.py), [`api/schemas.py`](https://github.com/ArturRembas/p05-bottleneck-detection/blob/task-04-openapi-contracts/api/schemas.py), [`schemas/openapi_v0.2.json`](https://github.com/ArturRembas/p05-bottleneck-detection/blob/task-04-openapi-contracts/schemas/openapi_v0.2.json).

The operation names below are Python function names, **not the exact current generated `operationId` strings**. The risk assignments are working proposals, not annotations implemented in PR #10.

| Function / capability | Method and route | Declared input → output | Proposed risk | Current maturity |
|---|---|---|---|---|
| `create_analysis` | `POST /api/v1/analyses` | CSV/XES upload + `case_id_col`, `activity_col`, `timestamp_col` → `AnalysisResultPayload` | R2 when full ingestion/analysis is performed | Upload checks; then `501` |
| `get_bottlenecks` | `GET /api/v1/analyses/{analysis_id}/bottlenecks` | Analysis ID → `CandidateBottleneck[]` | R0 | `501` |
| `get_process_kpis` | `GET /api/v1/analyses/{analysis_id}/kpis` | Analysis ID → `ProcessKPI[]` | R0 | `501` |
| `get_full_analysis` | `GET /api/v1/analyses/{analysis_id}/full-report` | Analysis ID → `AnalysisResultPayload` | R0 | `501` |
| `approve_countermeasure` | `POST /api/v1/analyses/{analysis_id}/countermeasures/approve` | `ApprovalRequest` → `ApprovalResponse` | Human-only approval operation; R2 governance | `501`; authorization/audit absent |
| `export_bpmn` | `GET /api/v1/analyses/{analysis_id}/export-bpmn` | Analysis ID → BPMN XML | R2 provisional; may be R0 if retrieving an already approved artifact | `501` |
| `health` | `GET /health` | No business input → service status | R0, technical only | Implemented health response |

The generated OpenAPI specification already contains `operationId` values. Explicit stable IDs are a possible improvement, not a missing OpenAPI feature. Existing domain operations are currently contract scaffolds; integration with a real analysis repository has not been established by PR #10.

The v0.2 schemas already contain `MetricStatus`, `TimeSemantics`, `MetricProvenance`, `ProcessKPI`, `CandidateBottleneck`, `AIInterpretation`, `CapabilityReport`, `SimulationScenarioResult` and `ErrorResponse`. They distinguish measured/derived/estimated/unavailable metrics and separate deterministic findings, AI interpretations and simulation scenarios.

**Required clarification:** `CandidateBottleneck.waiting_time` must not be filled with a completion-to-completion interval misleadingly labeled as measured queue waiting time. The meaning and resolution mechanism of `evidence_refs` also require agreement.

## 3. Agentic capability catalogue

This is the **full working catalogue** represented in the 19 November agentic design and reviewed against the architecture diagram. A catalogue item is **not** an implemented tool, an approved endpoint or a commitment to deliver it in Prototype v1.

**Legend:** `LLM` = model-backed capability; `HITL` = mandatory human confirmation on guarded execution; `UI` = dashboard action. All risk assignments and milestone allocations are proposals. `M2 core` means a narrow, testable vertical slice is proposed for Prototype v1; `M3+` means a later or conditional implementation.

### 3.1 Knowledge Agent (INFO)

| Capability | Responsibility / interface | Risk | Candidate scope |
|---|---|---|---|
| `retrieve_knowledge` (working name) | Retrieve relevant passages from authorized procedures and technical documents using the Knowledge Base; return citation identifiers and source context. RAG adapter; no assumed REST route. | R0 + corpus authorization | M2 core |

The **Knowledge Base** contains authorized document content. The **Experience Store** is separate: it contains only reviewed/validated examples (e.g. corrected mappings) and is not automatically a general-purpose document corpus. Its use and validation policy remain open.

### 3.2 Planner/Executor Agent (EXECUTE)

The Planner/Executor owns workflow coordination, not direct numerical computation. Its four domains remain workflows within one agent unless a later evaluation justifies extracting additional agents.

| Domain | Candidate tool | Meaning and suggested adapter | Risk | Candidate scope |
|---|---|---|---|---|
| Ingestion | `profile_log` | Obtain deterministic column/profile information; backend ingestion/profile service. A cached-profile read is R0; producing/storing a new profile may need stronger controls. | R0 conditional | M2 core |
| Ingestion | `propose_mapping` | LLM-assisted semantic mapping from minimized, pseudonymized profile and representative samples; return suggestions and uncertainty, **not** confirmation. | R0 + privacy gate | M2 core |
| Ingestion | `ingest_log` | Apply an explicitly confirmed mapping and execute full deterministic ingestion/normalization. | R2 + HITL | M2 core |
| Bottleneck analysis | `discover_dfg` | Request deterministic process discovery / DFG generation. | R1 if lightweight/reversible; R2 if costly/persistent | M2 subset |
| Bottleneck analysis | `detect_bottlenecks` | Invoke an evidence-based deterministic detector; do not let the LLM assign the ranking. | R1 if lightweight/reversible; R2 if costly/persistent | M2 subset |
| Bottleneck analysis | `explain_bottlenecks` | LLM interpretation grounded in candidate IDs, deterministic metrics, evidence and limitations; reusable outside chat. | R0 + evidence guard | M2 core |
| What-if | `propose_countermeasures` | LLM-generated intervention candidates, explicitly labeled as hypotheses; no physical intervention. | R0 + policy checks | M3+ |
| What-if | `simulate_scenario` | Submit typed scenario assumptions to SimPy and retrieve a separately labeled simulation result. | R2 + HITL | M3+ |
| Output & publish | `export_bpmn` | Retrieve or generate BPMN 2.0 output. Match to existing API operation where possible. | R2 provisional; see §4 | M3+ / core export dependency |
| Output & publish | `export_report` | Generate/retrieve a report, clearly separating deterministic/AI/simulation content. | R2 provisional | M3+ |
| Output & publish | `publish_results` | Publish an approved immutable result revision to external consumers (P06/P20/P17/P21). | R3 + HITL + audit | M3+ |

**Important:** `confirm_mapping` is a required **human decision/gate**, not a general tool through which an LLM can confirm its own suggestion. Similarly, a countermeasure approval endpoint is never a self-approval tool.

### 3.3 Result Analyst Agent (DATA-QA)

| Candidate tool | Responsibility / suggested adapter | Risk | Candidate scope |
|---|---|---|---|
| `get_performance_stats` | Read relevant deterministic performance metrics and their temporal semantics. | R0 | M2 subset |
| `get_activity_stats` | Read activity-level statistics with provenance. | R0 | M3+ unless exposed by M2 report |
| `get_variants` | Read process variants and relevant filters. | R0 | M3+ unless exposed by M2 report |
| `get_rework_stats` | Read deterministic repetition/rework statistics. | R0 | M3+ unless exposed by M2 report |
| `get_bottleneck_report` | Read candidate rankings, evidence references and limitations. Initially may adapt `get_bottlenecks` or `get_full_analysis`. | R0 | M2 core |
| `explain_result` | LLM explanation of a selected metric, activity or candidate grounded in retrieved evidence. May share a service with `explain_bottlenecks`. | R0 + evidence guard | M2 subset |

Do not assume one new REST endpoint per tool. First verify whether `get_full_analysis` or existing/approved data services can satisfy the required read-only contracts. Absent data must be reported as unavailable, not generated by the model.

### 3.4 UI Navigator Agent (UI-CONTROL)

| Candidate tool | Responsibility / suggested adapter | Risk | Candidate scope |
|---|---|---|---|
| `apply_filter` | Apply a validated reversible dashboard filter based on actual fields and values. | R1 | M3+ |
| `clear_filters` | Reset authorized dashboard filters. | R1 | M3+ |
| `set_view` | Select an available Streamlit view. UI action; not automatically a REST endpoint. | R1 / UI | M3+ |
| `highlight_node` | Highlight a DFG/process element identified in the current Workspace. UI action; not automatically a REST endpoint. | R1 / UI | M3+ |

The authoritative Workspace contract (active dataset, analysis, selection, filters, view) remains an open design question. Streamlit's session behavior and synchronization with backend state need testing.

### 3.5 Shared capabilities, not additional agents

- **Semantic Mapper:** the model-backed mapping proposal service may be called from ingestion UI without a chat session.
- **Grounded Explanation Service:** the model-backed explanation capability may be called by the Result Analyst, Planner/Executor or dashboard without changing deterministic results.
- **Tool Registry and Guardrails:** shared policy-enforcement infrastructure, not specialized agents.
- **HITL Gate:** independent approval mechanism around actions, not a model-generated decision.
- **LLM Gateway:** shared provider boundary, prompt/version management and data-minimization policy.
- **Trace Store:** proposed trace of requests, tool calls, model versions, approvals and outcomes; distinct from validated experiences.

A separate **Process Analyst Agent** or **What-if Agent** is *not* included in the present design. The corresponding domains remain Planner/Executor workflows. Reconsider splitting only if tests show meaningful benefits in independent planning/state, correctness or operational isolation.

## 4. Proposed tool contract and risk policy

### 4.1 Minimum registry fields (proposal)

Each exposed tool should have a reviewed entry containing:

| Field | Meaning |
|---|---|
| `tool_name` | Stable logical name (may differ from FastAPI function name and generated OpenAPI ID). |
| `description` | Narrow purpose and disallowed behavior. |
| `owner_component` | Backend service, AI/RAG service or UI action owner. |
| `adapter_type` | `rest`, `rag`, `llm`, `ui` or equivalent controlled category. |
| `contract_ref` | Existing OpenAPI operation or separately documented typed input/output schema. |
| `allowed_callers` | Which agents, UI entry points or external consumers may invoke it. |
| `risk_tier` | Reviewed R0–R3 classification; contextual conditions recorded if applicable. |
| `approval_policy` | Required user identity, approval conditions and authorization boundaries. |
| `evidence_and_provenance` | References needed for traceability and grounded responses. |
| `availability` | `contract-only`, `planned`, `implemented` or `verified` (according to evidence). |

The Registry can be derived in part from reviewed OpenAPI operations. Non-REST tools require explicit declarations, and all tools require an execution allowlist. A future `x-p05-risk` OpenAPI extension is **proposed**, not part of v0.2.

### 4.2 Risk classification (layer-level design; not yet ratified)

| Tier | Working definition | Examples | Gate |
|---|---|---|---|
| R0 | Read-only or non-mutating advisory interaction | KPI retrieval, authorized RAG retrieval, mapping **proposal** | Automatic only after access, privacy and input validation |
| R1 | Authorized reversible operation | Dashboard filters, lightweight discovery | Automatic, undoable where applicable |
| R2 | Expensive, persistent or consequential internal operation | Full ingestion, simulation, material export | Human approval before action |
| R3 | External publication/transfer of operational results | Send approved result revision to P06/P20/P17/P21 | Explicit human approval, immutable revision and audit |

**Contextual rules:** a nominally R0 action that transmits data to a cloud LLM still requires data-transfer policy checks; a large or persistent R1 computation may be reclassified R2; downloading an existing BPMN artifact might be R0, while expensive generation or persistent export may be R2. The final classification of `export_bpmn` is therefore **open**. Human mapping confirmation is mandatory regardless of the proposal tool's R0 label.

### 4.3 Execution boundary

Working flow: **Registry selection → automatic Guardrails → HITL Gate when required → authorized service/tool invocation → trace and result validation**.

- Validate typed arguments, permitted resources and existing identifiers deterministically.
- Reject unauthorized or unavailable operations; do not fabricate results when a service returns `501` or equivalent.
- Enforce per-operation human approval in application code and bind it to the exact action parameters and version.
- On rejection or timeout, fail safely; do not execute or auto-resume the protected action.
- Verify that every factual number stated in an AI explanation is grounded in a cited deterministic/simulation output. The explanation must identify simulations and hypotheses explicitly.
- Keep identity, authorization, external publication and audit enforcement in trusted backend services, not in a prompt or UI-only guard.

### 4.4 Priority M2 interface requirements (proposed; **not** endpoint definitions)

| Workflow boundary | Minimum inputs | Minimum outputs / rules | Dependency |
|---|---|---|---|
| Dataset profile retrieval | Authorized dataset reference and profile version | Pseudonymized field names/types, missingness, bounded representative samples, warnings; no unrestricted raw log to cloud | Ingestion/core + TASK-03 |
| Mapping proposal | Profile reference/version and schema-field targets | Candidate source→canonical field mapping, ambiguity and rationale, model/prompt provenance; clearly *proposed* | AI service + LLM Gateway |
| Mapping confirmation | Exact proposal and mapping revision, authenticated human decision (`confirm`, `modify`, `reject`) | Confirmed immutable mapping revision, actor/time audit; full ingestion prohibited without approval | Ingestion API + HITL + Streamlit |
| Deterministic analysis | Approved mapping/dataset reference, requested parameters | Analysis identity/status and deterministic results or explicit unavailability; no fabricated metric | API + PM4Py core |
| Read-only findings | Authorized analysis ID and optional selection | KPIs, candidates, temporal semantics, evidence refs, limitations | Existing PR #10 response models; real backend pending |
| Grounded explanation | Analysis/candidate/selection reference and resolved evidence | AI interpretation, citations/evidence refs, hypothesis/limitation type, model/prompt version; numbers must match tools | AI explanation service + core evidence |
| Authorized RAG question | User question and allowed corpus/scope | Answer with resolvable citations or explicit abstention; document-level access control | Knowledge Base + Knowledge Agent |
| Minimal agent tool call | User request, allowed tools, active analysis context | Typed tool name/arguments, checked authorization, grounded output, trace reference | LangGraph + Registry/Guardrails |

These rows intentionally avoid inventing concrete URL paths, status codes or final Pydantic classes. Route names, lifecycle transitions, schema versioning, persistence and ownership must be negotiated with TASK-03/TASK-04 and confirmed against the SRS. The earlier `contracts/draft-v0.1/openapi.yaml` provides *illustrative design alternatives*, not an approved contract.

### 4.5 Later contracts to reserve (M3 or later, not M2 commitments)

- Parameterized what-if scenario submission to SimPy, with assumptions, replications, simulation provenance and human approval.
- Report/BPMN artifact retrieval versus generation, with cost and privacy policy appropriate to each behavior.
- Approved external publication: immutable result revision, authenticated human approval, publication state, permitted consumers and auditable exchange.
- Read-only MCP exposure: only explicitly published and authorized operations/results; no automatic export of all internal R0 tools.
- Shared Workspace/Streamlit synchronization and natural-language UI actions.
- Experience Store write validation, review, retention and example retrieval; never bypass mapping confirmation.

## 5. Prototype scope and dependencies

The **approved roadmap** calls for AI v1 mapping + human confirmation, RAG and grounded bottleneck explanations during Prototype v1 (M2, target 20 December 2026). The capability subset and practical sequencing still require agreement with the group; the catalogue does not expand the approved deliverables by itself.

**Proposed minimal M2 vertical slice:**

1. Read a deterministic, privacy-filtered dataset profile and return a mapping proposal, then obtain a real human decision before full ingestion.
2. Retrieve a real or explicitly synthetic-labeled deterministic analysis result from the backend; generate an evidence-grounded explanation without changing any KPI.
3. Answer a bounded knowledge question from an authorized RAG corpus with citations or abstention.
4. Demonstrate a limited LangGraph/Tool Registry route with read-only tool calls, argument validation, traceability and controlled behavior if an API or LLM is unavailable.
5. Define and test the necessary R2/HITL boundary; do not silently approve or run expensive actions.

The full UI Navigator, free planning, iterative what-if and external publication workflows remain candidates for M3+. RAG and explanations are **not removed from M2** merely because some kit drafts place them in M3.

**Dependencies requiring coordination:**

- **TASK-03 (#3):** canonical event schema, admissible mapping semantics and confirmation boundary.
- **TASK-04 (#6), PR #10:** API baseline and agreed extensions for profile, mapping, evidence, AI service boundary and publication.
- **Ingestion/core implementation:** deterministic profile and normalized log; actual performance/bottleneck evidence.
- **Streamlit/UI:** confirmation cards and access to the same authorized backend state.
- **TASK-07 (#12):** static/dynamic agent architecture, LangGraph interruption/resumption and Workspace ownership.
- **Decision register/SRS/use cases:** ratification of previously open issues; no invented decision IDs or implemented behavior.

## 6. Open questions and review checklist

### 6.1 Open questions

1. Which service owns dataset/profile/mapping lifecycle and versioned confirmation? Which operation is allowed to trigger full ingestion?
2. Are stable `operationId` values mandated, or should the Registry maintain separate stable logical tool names?
3. What evidence fields are returned in `full-report`, and how are `evidence_refs` resolved without exposing unrestricted logs?
4. Which operations are R1 versus R2 after actual cost, persistence and side-effect evaluation (especially discovery and export)?
5. How is a human decision authenticated, audited, bound to exact action parameters and resumed through LangGraph/Streamlit?
6. Which internal results are accessible to the UI/agent, and which revisions are eligible for published REST/MCP exchange?
7. What are the approved cloud-data minimization rules, provider policy, allowed RAG corpus and Experience Store retention rules?
8. Which agentic functions form the agreed M2 MVP, given capacity and the already elapsed M1 target (22 November 2026)?

### 6.2 TASK-06 review checklist

- [ ] The seven existing PR #10 operations and their actual maturity are correctly represented.
- [ ] All four specialized agents and all 22 working capabilities are catalogued, with no implied endpoint implementation.
- [ ] Each capability has a provisional risk, owner/adapter boundary and proposed scope.
- [ ] Human mapping approval, R2/R3 safeguards and trusted authorization are explicit.
- [ ] Deterministic temporal and numeric evidence limitations are preserved.
- [ ] M2/M3 scope is labeled proposed where it is not approved; unresolved decisions are visible.
- [ ] TASK-03/TASK-04, SRS, consolidated use cases and the decision register are checked by relevant reviewers.
- [ ] At least one other team member reviews this document in a PR; resulting decisions are recorded separately.

**Verification appropriate to this documentation-only task:** confirm the file exists; review all links and tables; run `git diff --check` on the branch when using a local clone. No runtime functionality or passing agent tests are claimed by this document.

## References

- [TASK-06 — GitHub issue #11](https://github.com/ArturRembas/p05-bottleneck-detection/issues/11)
- [TASK-07 — GitHub issue #12](https://github.com/ArturRembas/p05-bottleneck-detection/issues/12)
- [TASK-03 — GitHub issue #3](https://github.com/ArturRembas/p05-bottleneck-detection/issues/3)
- [TASK-04 — GitHub issue #6](https://github.com/ArturRembas/p05-bottleneck-detection/issues/6)
- [PR #10 — OpenAPI contract v0.2](https://github.com/ArturRembas/p05-bottleneck-detection/pull/10)
- [Project scope](https://github.com/ArturRembas/p05-bottleneck-detection/blob/master/docs/PROJECT_SCOPE.md)
- [Architecture — working design](https://github.com/ArturRembas/p05-bottleneck-detection/blob/master/docs/ARCHITECTURE.md)
- Local project context: `02_CONTESTO_AI_Layer_P05.md`, especially §§3, 5 and 8 (19 November 2026); original agentic design: `05_Architettura_Agentica_P05_28-10.md` (superseded wherever inconsistent with §8).
