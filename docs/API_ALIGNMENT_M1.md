# TASK-04 — Proposed M1 API alignment

This is a contract scaffold, not an operational analysis service. All business operations return structured HTTP 501 after applicable request validation. The proposed changes require group and consumer review; SC/DB decisions are not ratified by this document. The existing preliminary OpenAPI version 0.2.0 is retained pending a versioning decision. Payloads are not backwards compatible.

## Workflow and trust boundaries

- Upload returns a typed dataset identity, input hash and minimized structural profile in the future implementation.
- Mapping proposal and confirmation are separate operations. Mapping documents are owned by TASK-03 (PR #15, ea4da5f), not duplicated in this API. The proposal endpoint references an already stored draft; creation/storage of that draft, selector validation, correction and AI-assisted generation are deferred. The implementation must validate the referenced document against TASK-03, including CSV/XES scopes, transformations, and exact input hash. Raw event data must not be sent to external models.
- Confirmation must be a trusted, authenticated human decision for an exact dataset hash, mapping ID and version. A client-provided reference is not proof of authorization. Ingestion separately requires authorization bound to the intended operation. No automatic execution follows mapping confirmation.
- Internal retrieval must enforce access control. External consumers must access only an authorized immutable published revision through a separate read interface (route and consumer agreement deferred). Countermeasure approval and publication are independent decisions. Publication requires an explicit consumer list and a server-verified approval bound to the path analysis ID, result revision and consumers. No default permission or fabricated notification.

## Evidence and temporal semantics

Source timestamps, analytical view and metric semantics are independent. Durations use seconds. Observed gaps are not queue waits. Unavailable values are null with reasons, not zero. Candidate primary metrics represent mean durations with matching evidence category and sample size. L1 applies to transition gaps; L2 applies to correlated queue waits for an activity or explicitly mapped workstation. L3 is reserved in the vocabulary but rejected by this initial detector finding contract until a reviewed rule and corroboration are available. No causal or persistent congestion conclusion follows from a positive wait alone.

Support thresholds are explicit and versioned; the proposed defaults are three observations and three distinct contributing cases. Rank is allowed only for positive supported results. Comparable groups distinguish metric, target kind, view, observation window and coverage class. Observation coverage and affected-case ratios are independent. Evidence references in full reports resolve to evidence records in the same revision; artifact resolution and authorization are deferred. View/window/config references must resolve to persisted definitions in the future backend. Median and maximum are optional in this scaffold. Cross-finding ranking computation, tie handling, observation-window inclusion rules, and validation of actual timestamp correlations are not implemented. Capability status describes data eligibility, separately from runtime implementation. Detailed per-capability population metadata remains to be agreed.

## Verification

Run `python schemas/generate_schema.py` followed by `python -m pytest tests/test_api_contracts.py -q` in the chosen dependency environment. Compare the generated artifact to the committed artifact under matching versions. Tests establish structural consistency, not operational service correctness, authentication, empirical detector performance or consumer acceptance. Keep TASK-04 open (`Refs #6`) until remaining acceptance criteria are met.
