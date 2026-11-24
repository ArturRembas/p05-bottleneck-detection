# TASK-03 — Canonical event-log contract fixtures (v0.1.0)

**Status:** proposed design baseline, pending group review. All data and approval references are synthetic. The normative proposal is [`docs/CANONICAL_EVENT_LOG.md`](../../docs/CANONICAL_EVENT_LOG.md); the companion schemas are under [`schemas/`](../../schemas/). This directory does not contain a production ingestion implementation or a validated bottleneck detector.

## Contents and scope

| File | Purpose |
| --- | --- |
| `completion_only.csv` | §9.1; observed DFG and gaps, no established waiting or processing duration. |
| `complete_temporal_log.csv` | §9.2; one enriched completion observation, service 900 s and wait 600 s. |
| `paired_lifecycle.csv` | §9.3; three events for one known activity instance. |
| `minimal_log.xes` | §9.4; example of trace/event selectors and UTC conversion; not a full XES conformance test. |
| `mapping_source.csv` | §9.5; exact UTF-8/LF source bytes for the JSON examples. |
| `confirmed_mapping.example.json` | §9.5; synthetic confirmed-mapping representation, not authenticated approval. |
| `canonical_log.json` | §9.5; expected canonical representation of `mapping_source.csv`. |
| `quality_report.example.json` | Illustrative associated quality record referenced by the log; no separate quality-report schema ratified. |
| `xes_mapping.example.json` | Additional proposed mapping for the XES fixture; intentionally unconfirmed. |
| `validation_cases.json` | VC-01–VC-20 from §9.6, fixture references, structural expectations and selected numerical oracles. |
| `validation/` | Deliberately invalid, incomplete or ambiguous examples for design review and later implementation tests. |
| `verification_report.txt` | Recorded output of the design-artifact verifier. |
| `.gitattributes` | Local LF policy to preserve source hashes across operating systems. |

The CSV/XES and two primary JSON examples were extracted directly from the normative draft without changing their contents. Do not edit or normalize the source bytes without updating the corresponding checksum references. No research artifact under `research/pm4py-exploration/` is copied, modified or imported here.

## Machine-readable representation choices requiring review

The two JSON Schemas use JSON Schema Draft 2020-12 and cover the **initial proposed JSON serialization**, not a public REST contract. The core may still use a Pandas DataFrame internally.

- A normalized record requires `source_event_index`, generated during normalization; the input still requires only `case_id`, `activity` and `timestamp`. Optional event fields may be omitted or null.
- The log metadata uses the reference-based `quality_report_ref` representation from §9.5; the associated report is illustrated separately. The schema does not define storage or a general embedded quality-report model.
- Mapping selectors are explicit `{scope, name}` objects. This initial serialization selects CSV columns or XES trace case identifiers and event attributes. More elaborate classifier, inheritance and projection rules remain outside this initial serialization.
- Mapping transformations express the simple defaults in §9.5 explicitly. Additional named declarative fields (`lifecycle_mapping`, `resource_role`, `timestamp_semantics_detail`, `field_time_rules`, `additional_null_markers`, `correlation_rule`) are proposed encodings for the semantics in §§4 and 6. No arbitrary executable transformation is admitted. The `correlation_rule` value `case_activity_instance` names the proposed simple correlation key; support for other rules, DST disambiguation, authoritative sequence selectors or source-specific transformations requires further review. No parser support is asserted by these keys.
- Canonical timestamps require UTC (`Z` or `+00:00`); mapping confirmation timestamps also use UTC in this proposed JSON representation. Explicit RFC 3339 date-time format checks are enabled by the verifier. The JSON representation does not validate all IANA timezone or timestamp precision requirements of a future implementation.
- Unknown properties are rejected by the initial structural contract (except explicitly declared lifecycle-value mapping keys). This is a proposed serialization policy; preserving additional source attributes outside the minimal model remains possible as described in §3.3. These choices do not add mandatory source columns or change any API contract.

## Verification boundary

The verifier checks both metaschemas, evaluates the listed positive and negative JSON examples with format checking enabled, verifies all 20 catalogue entries and referenced fixture paths, checks source hashes and illustrative references, and independently computes selected expected values. It does not implement CSV/XES ingestion, lifecycle pairing, capability assessment, authentication, trusted mapping approval, PM4Py algorithms or detector logic.

A structural acceptance can be correct even for a log that must be rejected by semantic validation. For example, VC-12 contains repeated event IDs across records; VC-16 contains proposed/rejected mappings or mismatched approval references. These objects have valid shapes but do not authorize analysis. Source-event uniqueness, cross-field timestamp order, correlation, DST resolution, matching source/mapping identities, and trustworthy confirmation all require separate checks. No executable product test outcome is claimed for those requirements.

### Run the design-artifact checks

From the repository root, using an isolated Python environment with `jsonschema[format]==4.26.0` installed:

```bash
python tools/verify_task03_contract.py
```

The recorded run used Python 3.13.5 and jsonschema 4.26.0. These are **verification-tool versions only**, not a change to the P05 Python/runtime baseline or historical research dependencies. Do not add this dependency to product requirements solely for this check.

For a local-Python-free check, a proposed disposable Docker command (requires access to the image and package registry; not executed in the recorded run) is:

```bash
docker run --rm -v "$PWD:/workspace:ro" -w /workspace python:3.13.5-slim \
  sh -c 'python -m pip install "jsonschema[format]==4.26.0" && python tools/verify_task03_contract.py'
```

This is a temporary verification environment, not an additional P05 application service. The source tree is read-only. The command pins the validator version, not its complete transitive dependency graph or the base image digest; it is not a fully locked build. The group's existing Docker/Compose configuration remains unchanged.

## Review checklist

- [ ] Review SC-01–SC-08 and the companion serialization choices against the decision register.
- [ ] Verify the source-to-canonical examples, both schemas and expected outcomes.
- [ ] Re-run the design verifier and record evidence; distinguish the unimplemented VC outcomes.
- [ ] Review mapping provenance and capability semantics with TASK-04 and agentic specifications.
- [ ] Review the evidence prerequisites with TASK-05 without adopting research thresholds.
- [ ] Confirm the PR changes only TASK-03 design artifacts, not application API or historical research.
- [ ] Record group decisions and obtain another team member's review before merging and closing #3.
