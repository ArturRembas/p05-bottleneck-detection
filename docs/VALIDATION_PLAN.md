# Validation and Evidence Plan — Proposed

## Research questions

- Can the system reconstruct the correct flow and variants from a known event log?
- Can each calculated interval be traced to valid timestamps and appropriate lifecycle semantics?
- Does the detector distinguish a **delay hotspot** from an observed queue or a capacity constraint?
- Do AI mapping suggestions improve usability while requiring explicit human confirmation?
- Are AI explanations grounded in existing measurements and authorized documentation?
- Can other puzzle components consume versioned outputs with correct access controls?

## Minimum experimental baselines

| Capability | Baseline | Proposed measurement |
| --- | --- | --- |
| Mapping | Manual mapping | Field-level correctness, correction rate and time |
| Process discovery | Known synthetic flow | Edge/variant agreement against the source generator |
| Time metrics | Independent timestamp arithmetic | Absolute/relative numerical error |
| Bottleneck ranking | Simple maximum-gap ranking | Detection quality against known synthetic bottleneck labels |
| AI interpretation | Measurements without LLM | Unsupported-claim rate, source attribution and human usefulness |
| Simulation | Original calibrated scenario | KPI agreement, sensitivity, seed stability and uncertainty |

## Suggested test layers

1. **Unit:** parsers, mapping validation, timestamps, deterministic metrics, ranking and schema validation.
2. **Integration:** upload → approved mapping → PM4Py → finding → versioned result → REST/UI.
3. **Contract:** valid examples and invalid payloads for REST/OpenAPI and read-only MCP.
4. **Experimental:** SimPy with known injected bottleneck conditions; independently review real event logs when lawful and available.
5. **Shadow mode:** compare findings with historical or expert observations without changing real production decisions.

## Evidence policy

Record dataset provenance/checksum, parameters, transformations, code commit SHA, dependency versions, evaluation script, ground-truth definition, observed metrics, limitations, and expert review. For simulations record model version, random seed and number of replications.

**No tests are claimed complete by this plan.** Numeric results in earlier slides (e.g. Welding wait improvements) are illustrative until reproduced and validated.
