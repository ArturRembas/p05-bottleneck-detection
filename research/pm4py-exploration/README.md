# PM4Py Exploration — P05 Research Archive

## Purpose

This directory contains exploratory experiments carried out to
investigate PM4Py capabilities relevant to P05 — Bottleneck
Detection in Processes.

The research focuses on process discovery, performance analysis,
process variants, rework, queue dynamics, candidate bottleneck
detection, and event-log analytical capabilities.

This material is an exploratory research baseline. It is not
part of the production P05 core and does not define approved
application behavior or interoperability contracts.

## Contents

- `core/`: experimental helper functions and queue diagnostics.
- `scripts/`: ten exploratory experiments, EXP-01 through EXP-10.
- `data/`: controlled synthetic datasets.
- `docs/`: experiment protocols, observations, and technical report.
- `results/`: archived experimental results and audit metadata.
- `requirements.txt`: standalone research dependencies.

The main technical report is:

`docs/13_rapporto_esplorazione_pm4py_v0.1.md`

## Experiments

| ID | Research topic |
|---|---|
| EXP-01 | Directly-Follows Graph discovery |
| EXP-02 | Performance DFG and temporal metrics |
| EXP-03 | Process variants and repeated activities |
| EXP-04 | Parallelism and process discovery |
| EXP-05 | Resource capacity and waiting times |
| EXP-06 | Initial candidate bottleneck detection |
| EXP-07 | Generalization across synthetic scenarios |
| EXP-08 | Transient and persistent queues |
| EXP-09 | Queue dynamics classification |
| EXP-10 | Event-log capability profiling |

## Archived Baseline

The original exploratory report, dated October 28, 2026,
records ten experiments as passing their local checks.

Original recorded environment:

- Python 3.14.4
- PM4Py 2.7.23.11
- Pandas 2.3.3
- Linux

Archived results are provided in `results/`.

The audit manifest is available at:

`results/audit/baseline_v0.1.json`

Some original execution logs are intentionally excluded from
version control. The complete original manifest therefore cannot
be verified from the Git repository alone.

These results are historical experimental evidence.
They do not constitute independent validation of the complete
P05 system or its bottleneck detection algorithms.

## Reproducing the Experiments

From this directory, create an isolated Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt


Run an individual experiment:
python scripts/exp01_dfg.py


Other experiments are available in scripts/.

Running experiments may overwrite archived result files.
For independent reproduction, use a disposable copy of this
directory and compare the new outputs against the archived
baseline.

Compatibility and numerical equivalence across Python and
dependency versions have not yet been independently verified.
Scientific Limitations
- Synthetic examples do not establish real-world accuracy.
- Long activity durations do not necessarily imply bottlenecks.
- Inter-event gaps are not automatically queue waiting times.
- Queue classification requires adequate temporal evidence.
- Resource-level analysis requires suitable resource identifiers.
- Candidate bottlenecks are not proven capacity constraints.
- Existing experimental thresholds are not approved P05 rules.
All conclusions must be interpreted within the limitations
of the corresponding experiment and dataset.
Relationship to the Official P05 Architecture
This research may inform:
- TASK-03: Canonical event-log schema and mapping contract.
- TASK-05: Detector baseline and admissible evidence levels.
- Future deterministic mining and detector implementation.
- Experimental validation and benchmarking activities.
No production API, JSON Schema, REST, MCP, Docker, or core
integration contract is modified by this research archive.

The experimental code must not be imported directly into the
official application without separate review, testing, and
an explicit implementation decision.
Governance
This material is submitted for team review.

Experimental observations, approved architectural decisions,
implemented capabilities, and validated results must remain
clearly distinguishable.

Any future integration into the official P05 application
requires a dedicated Issue, Pull Request, review, and
appropriate test evidence.

The licensing obligations of third-party dependencies,
including PM4Py, must be reviewed before redistribution or
deployment in other contexts.
