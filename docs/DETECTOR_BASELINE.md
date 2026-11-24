# P05 — Detector Baseline and Admissible Evidence Levels

| Document control | Value |
| --- | --- |
| Version | `0.1.0` |
| Date | 2026-11-24 |
| Status | **Draft for group review — proposed design baseline** |
| Work item | [TASK-05 — Issue #7](https://github.com/ArturRembas/p05-bottleneck-detection/issues/7) |
| Milestone | M1 — Architecture & Design |
| Reviewed integration baseline | `master`, `ba11a17fd5cf2c8e1c1f2ac39d4287c27186dc38` |
| Input contract dependency | [TASK-03, PR #15](https://github.com/ArturRembas/p05-bottleneck-detection/pull/15), head `c1835ca10803c36f791db4502b7e9e7965dc3ad9` (draft) |
| External contract dependency | [TASK-04, PR #10](https://github.com/ArturRembas/p05-bottleneck-detection/pull/10) (under review) |

## 1. Purpose, status and boundaries

TASK-05 specifies a simple, reproducible detector baseline, its ranking rule, minimum support and admissible evidence. It does not implement a detector, certify real-world accuracy, define a new HTTP contract, select production severity thresholds or modify the historical research archive. The proposed rules become binding only after group approval. References to D05, D09, D11, D13–D16 and D21 identify relevant use cases, not a ratified release allocation.

A capacity bottleneck is a resource or process constraint that limits attainable system throughput under specified demand, capacity and operating conditions. The detector initially identifies observable delay and waiting signals, not proven capacity constraints. Long service, a large gap, repeated activities, positive waiting or high utilization alone do not establish such a constraint. Human review can assess evidence but cannot turn missing evidence into measurements.

## 2. Design basis and research evidence

The established project direction separates deterministic results, AI interpretations and simulation estimates; the modular Python/Pandas/PM4Py core is independent of LLM availability. `docs/PROJECT_SCOPE.md` identifies the exact ranking, severity and evidence levels as open design decisions. `docs/VALIDATION_PLAN.md` proposes a simple maximum-gap ranking as a comparison baseline. Here, “maximum-gap ranking” is made explicit as the maximum **mean** observed gap across DFG edges, not the largest single interval.

| Research evidence | Archived observation | Design consequence |
| --- | --- | --- |
| EXP-02 | Fresatura → Fresatura: 2520 s, one occurrence; Fresatura → Saldatura: 2130 s, four occurrences | Report support and prevent a single observation from automatically leading the supported ranking. |
| EXP-03–04 | Repeated activities and inferred parallelism | Use an explicitly selected analytical view; do not equate repetition with defective rework or ordering with causality. |
| EXP-05–06 | One CNC: mean wait 17.5 min; two CNC: 0 min under the controlled configuration | Separate waiting evidence from capacity interventions and retain scenario assumptions. |
| EXP-07 | Capacity-constrained CNC, capacity-constrained Cutting, and slow CNC without waiting | Avoid treating service duration as a capacity diagnosis. |
| EXP-08 | Temporary peak and overload both yield positive mean waiting | Positive waiting cannot establish persistence. |
| EXP-09 | Waiting-pattern classifications use 6 observations, a tail of 3 and a 70% growth threshold | Historical heuristic only; defer production queue-pattern rules. |
| EXP-10 | Structural analytical capability checks; semantic validation not performed | Require semantically confirmed evidence and explicit limitations. |

The EXP-01–EXP-10 archive is integrated through PR #8. PR #9 records container reproduction of the historical research results. Neither PR validates the proposed detector on independent data. No archived code or thresholds are adopted automatically.

## 3. Proposed decision set

| ID | Decision | Proposed baseline |
| --- | --- | --- |
| DB-01 | Detection objective | Rank observable signals and distinguish them from capacity hypotheses. |
| DB-02 | Admissible evidence | Three evidence categories: delay hotspot, queue evidence candidate, capacity bottleneck hypothesis. They are not severity levels or probabilities. |
| DB-03 | Reference and supported ranking | Retain unfiltered maximum-mean-gap reference; use supported mean-gap and mean-wait rankings separately. |
| DB-04 | Minimum support | At least 3 admissible observations AND 3 distinct cases per target/metric; configurable, versioned engineering guardrail, not statistical significance. |
| DB-05 | Missingness and abstention | Preserve zero versus unknown, distinguish partial coverage, unavailable input and insufficient support. |
| DB-06 | Traceable outputs | Typed targets, metric semantics, evidence, support, limitations and rule version; no automatic severity or confirmed causal diagnosis. |
| DB-07 | Validation | Independent numerical oracles, known synthetic scenarios, adversarial cases, and later independent/empirical evaluation. |

These local IDs are proposals, not approved decision-register entries. No existing contract is changed by this document.

## 4. Input and analytical views

Use a validated canonical log, exact confirmed mapping revision, analytical capability assessment and a declared view, as proposed in TASK-03. Required fields are `case_id`, `activity`, `timestamp`; optional queue and service endpoints and resource information are used only when their meaning and correlation are established. Preserve case boundaries and source references. Lifecycle observations must not be mistaken for distinct completed occurrences. Ties resolved only by source order must retain an ordering-ambiguity limitation. A homogeneous observation sequence may support a descriptive gap ranking; unknown timestamp meaning must not be relabeled as completion. Exclude semantically unusable observations from the affected metric with explicit counts/reasons, not from the source log silently.

The detector consumes deterministic metrics and evidence from mining/performance modules. It does not parse CSV/XES, approve mappings, call LLMs, simulate interventions or expose HTTP endpoints. PM4Py discovery and DFG aggregations must use the same declared view as independent timestamp arithmetic; default library behavior must be checked against the selected semantics.

## 5. Evidence categories and admissibility

| Category | Required evidence | Permitted claim | Prohibited inference |
| --- | --- | --- | --- |
| L1 — `delay_hotspot` | Valid comparable within-case adjacent timestamps, reproducible view, sufficient support | Relatively large observed interval for a transition in this view | Queue wait, service duration, causal precedence or capacity diagnosis |
| L2 — `queue_evidence_candidate` | Observed and correlated queue-entry/service-start pairs, sufficient support, positive observed wait | Waiting observed for the associated activity/station in the stated population | Persistent queue, queue length, saturation or capacity constraint solely from wait |
| L3 — `capacity_bottleneck_hypothesis` | Corroborating resource/pool identity, capacity and availability, workload/demand, relevant window and evidence of throughput limitation; reviewed attribution and alternative explanations | A qualified capacity hypothesis for review | Proven root cause, operational recommendation as fact, or automatic promotion from L1/L2 |

L1 and L2 may coexist; neither automatically implies the other. L3 is not automatically emitted by the initial ranking baseline; record unavailable or not assessed where corroborating context is missing. A future reviewed capacity rule may use independent operational evidence or controlled comparisons. Simulation outcomes remain conditional estimates. A controlled synthetic intervention can establish the known scenario mechanism without establishing the same mechanism in a real plant.

Processing duration is a separate diagnostic KPI, not an L2 trigger. Queue length and utilization require their own evidence, including observation boundaries and denominators; a series of completed waits is insufficient to infer general occupancy. Waiting-time dynamics may be inspected descriptively, but EXP-09 classification parameters remain exploratory and are not required for the initial detector.

## 6. Deterministic ranking

### 6.1 Reference comparator

For each ordered transition `(a,b)` in a declared case view, compute all admissible adjacent gaps in seconds. The reference comparator ranks transitions by descending arithmetic mean gap, without the proposed minimum-support filter. Report sample counts and retain ties. No gap is interpreted as waiting. This intentionally simple comparator is for evaluation, not a production diagnosis.

### 6.2 Supported baseline

For a target `g` and one metric, let `x_1,...,x_n` be eligible non-negative intervals. Define:

- `n`: eligible pairs (gap) or occurrences (wait); `c`: number of distinct case IDs contributing eligible intervals.
- `N`: all identifiable candidate pairs or occurrences in the declared target/view, including missing or unusable intervals; `coverage = n/N` when N is known and positive. Otherwise disclose that coverage is unknown.
- `mean = sum(x_i)/n` when `n > 0`; retain observed zeros in the denominator.
- Also report median, maximum, and, for waiting, fraction of eligible occurrences with positive wait. These are descriptive metrics, not additional ranking weights.

The proposed default guardrail is `n >= 3` and `c >= 3`. A target failing either test retains descriptive metrics if computable but receives no supported rank. This default is chosen to exclude singleton and single-case repetition effects while keeping small research fixtures useful; it does not guarantee representativeness. Record any override with the rule configuration and do not select thresholds after inspecting evaluation outcomes.

**L1:** group by directed transition `(source_activity, target_activity)` and rank supported positive mean gaps descending. **L2:** group by activity or explicitly mapped station (one declared grouping per run) and rank supported positive mean waits descending. Waiting is computed as `service_start - queue_entry` for the same occurrence, not from a DFG performance statistic. A single positive wait among otherwise zero waits can qualify as an observed signal if support is met, but must be identified as isolated evidence, not repeated congestion. Zero means produce no positive candidate for that metric. Negative or invalid intervals are not converted to zero.

Rank separately by metric, target kind, view, window and coverage class (full versus partial/unknown); never form a global ordering by mixing gaps and waits or pooling different population definitions. Partial results are restricted to the eligible subset and must not be extrapolated. All eligible targets and their coverage remain inspectable. Equal scores share a dense rank; a stable lexical target order is only a display tie-breaker. Rank 1 means largest supported positive mean in its ranking group, not an abnormality, severity or confirmed bottleneck. No fixed top-k, composite score, universal duration cutoff or statistical significance threshold is imposed. A UI may show a subset without changing the underlying ranks.

### 6.3 Outcome semantics

| Condition | Expected outcome |
| --- | --- |
| No admissible observations | Metric unavailable; no rank; reason. |
| Admissible observations but below minimum support | Descriptive statistic; insufficient support; no supported rank. |
| Supported and all observed intervals zero | No positive candidate; this is not unavailable data. |
| Supported positive intervals | Rank within the relevant metric/coverage group and disclose limitations. |
| Missing or invalid optional endpoints | Partial/unavailable as applicable; no fabricated wait. |
| Capacity evidence absent | L3 not assessed/unavailable; do not infer absence of a capacity bottleneck. |

An empty candidate list alone is ambiguous. The accompanying capability and support information must explain whether no positive signal was observed, no supported target existed, or the analysis was unavailable. A valid dataset with a single observed case may still support descriptive metrics.

## 7. Logical output and interface coordination

Each finding should identify the evidence category, target kind and target identity (both endpoints for an edge), metric identifier, unit (`seconds` for elapsed durations), statistic, eligible count, distinct-case count, denominator/coverage if available, capability status, ranking group and rank, evidence references, limitations, mapping revision, dataset fingerprint, selected view/window and detector rule/version/configuration. Evidence records should not expose confidential raw identifiers to unauthorized consumers. An interval computed from observed endpoints is derived, not a simulated estimate.

PR #10 already proposes `ProcessKPI`, `MetricStatus`, `CapabilityReport`, `MetricProvenance` and `CandidateBottleneck`. Its `CandidateBottleneck` is activity-oriented, requires a severity enum, and does not explicitly encode transition endpoints, evidence category or separate ranking scopes. TASK-04 must review a faithful representation; do not assign arbitrary LOW/MEDIUM/HIGH/CRITICAL or silently turn a transition into an activity. The public `TimeSemantics` vocabulary also requires the TASK-03 alignment already identified. No API/Pydantic/OpenAPI changes belong in this design PR. Until a reviewed public mapping exists, do not expose ambiguous findings as a compatible contract.

AI explanations may refer to the deterministic findings, explain limitations or suggest hypotheses separately. They must not alter ranks or evidence. Human confirmation and publication authorization are separate from analytic support. No real-world capacity change is authorized by a finding.

## 8. Design-level validation catalogue

The following are proposed acceptance oracles, not executed detector tests. Archived EXP results are historical comparison evidence. Where the historical fixture lacks a confirmed mapping, the future test must explicitly declare and confirm its semantics.

| ID | Scenario | Expected behavior |
| --- | --- | --- |
| DV-01 | EXP-02, 4 cases | Reference rank 1: Fresatura → Fresatura (2520 s, n=1); supported rank 1: Fresatura → Saldatura (2130 s, n=c=4). Singleton has no supported rank. |
| DV-02 | EXP-06, one CNC | L2 Fresatura CNC: mean 1050 s, n=c=8, positive-wait fraction 7/8. No automatic L3. |
| DV-03 | EXP-06, two CNC | All observed waits zero; no L2 candidate, not unavailable. |
| DV-04 | EXP-07 A/B | L2 ranks the known affected activity (CNC/Cutting); mean 1650 s, n=c=12. |
| DV-05 | EXP-07 C | CNC service 1200 s, zero waits; no L2 candidate. No capacity diagnosis from duration. |
| DV-06 | EXP-08 temporary peak vs overload | Both yield L2 signals, means 202.5 s and 1050 s respectively; neither automatically yields L3 or a persistent-queue label. |
| DV-07 | TASK-03 completion-only fixture | Gap statistics possible; wait unavailable; one case means no supported ranking. |
| DV-08 | TASK-03 partial-wait fixture | Report eligible and excluded occurrences, no zero imputation, restricted scope; enforce support. |
| DV-09 | Repeated events in one case, even n >= 3 | Distinct-case guardrail prevents supported ranking; no claim of defective rework. |
| DV-10 | Equal positive scores, same group | Shared rank, deterministic display; no forced winner. |
| DV-11 | Missing/ambiguous lifecycle or negative optional interval | Affected measure unavailable or partial; no unsupported correlation or clipped duration. |
| DV-12 | Multiple cases and tied timestamps | No cross-case gap; deterministic tie-break and ambiguity limitation. |
| DV-13 | Supported waits [0, 0, 9] s from three cases | Mean 3 s, positive fraction 1/3; isolated signal only, not persistent congestion. |
| DV-14 | Comparable targets with full and partial coverage | Separate ranking groups; disclose coverage; no claim of overall priority. |
| DV-15 | Capacity information absent or simulation alone | No automatic L3; simulated outcomes remain estimates. |

For M2, implement tests with independent interval arithmetic and fixed configuration; compare supported outputs with the unfiltered comparator on the same views. Validate target identity, ranks/ties, eligibility, coverage and abstention before evaluating accuracy. Future ground truth must distinguish delay/queue observations from actual capacity constraints and include scenarios independent of rule design. Report false positives, false negatives, abstentions and coverage separately; use ranking metrics such as hit@k only where a justified target oracle exists. Retain code SHA, data checksums, mapping revision, rule configuration, environment and evaluation results. Do not tune and evaluate on the same scenarios without disclosure.

## 9. M1 acceptance and deferred work

- [ ] Group reviews and records DB-01–DB-07, including the minimum-support default and the scope of automated evidence categories.
- [ ] TASK-03 final semantics are reconciled with the proposed baseline; PR #15 is not assumed merged.
- [ ] TASK-04 reviewers agree on the required interface reconciliation or explicitly track unresolved incompatibilities and prohibit misleading output.
- [ ] Ranking, support, coverage, zero/missingness, ties and abstention behavior are unambiguous.
- [ ] Historical research references and design oracles are reviewed; no research results are relabeled as product tests.
- [ ] At least one other team member reviews the PR and confirms its evidence.

Deferred to implementation/evaluation: mining adapter and detector code, new fixture files/automated tests as needed, robust threshold calibration, persistence, queue occupancy and validated queue dynamics, capacity estimation, simulation, public schema extensions, severity policy and empirical validation. M1 does not require an executable detector. These deferrals do not remove approved project objectives or ratify M2 scope.

## 10. References

- [Issue #7](https://github.com/ArturRembas/p05-bottleneck-detection/issues/7), [Issue #3](https://github.com/ArturRembas/p05-bottleneck-detection/issues/3), [Issue #6](https://github.com/ArturRembas/p05-bottleneck-detection/issues/6).
- Repository: `docs/ARCHITECTURE.md`, `docs/PROJECT_SCOPE.md`, `docs/VALIDATION_PLAN.md`.
- Research archive: `research/pm4py-exploration/docs/13_rapporto_esplorazione_pm4py_v0.1.md`, `results/exp02_summary.json`, `results/exp06_summary.json`–`results/exp10_summary.json` within that archive; `core/queue_diagnostics.py` within that archive.
- [PR #8](https://github.com/ArturRembas/p05-bottleneck-detection/pull/8), [PR #9](https://github.com/ArturRembas/p05-bottleneck-detection/pull/9), [PR #10](https://github.com/ArturRembas/p05-bottleneck-detection/pull/10), [PR #15](https://github.com/ArturRembas/p05-bottleneck-detection/pull/15).
