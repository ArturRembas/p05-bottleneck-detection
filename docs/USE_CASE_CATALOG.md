# Use-Case Catalogue — Provisional

**Source:** Decision Register P05 (12 November 2026), `Use Cases - Draft` worksheet.

The catalogue contains **25 deterministic use cases D01–D25 and 13 agentic entries UC01–UC13**. **UC03 is an internal alternative of UC02**, not an independent top-level use case. The groups' approved architecture does not mean these individual scenarios or MVP boundaries have been ratified. Detailed GitHub Issue bodies in the accompanying `github-setup/issues/use-cases` are **proposals** to be reviewed against the complete Chat 02 specification.

| ID | Title | Domain | Proposed planning phase | Status |
| --- | --- | --- | --- | --- |
| D01 | Upload an Event Log and Inspect a Preview | Data Ingestion and Governance | M2 | Draft; not ratified as MVP |
| D02 | Inspect Column and Row Profiles | Data Ingestion and Governance | M2 | Draft; not ratified as MVP |
| D03 | Apply an Approved Mapping and Normalize the Log | Data Ingestion and Governance | M2 | Draft; not ratified as MVP |
| D04 | Inspect Log Quality and Data Anomalies | Data Ingestion and Governance | M2 | Draft; not ratified as MVP |
| D05 | Determine Available Analyses | Data Ingestion and Governance | M2 | Draft; not ratified as MVP |
| D06 | Store and Retrieve Versioned Event Logs | Data Ingestion and Governance | M3 | Draft; not ratified as MVP |
| D07 | Manage Plant Calendars and Resource Capacity | Data Ingestion and Governance | M3 | Draft; not ratified as MVP |
| D08 | Configure Analysis Methods and Criteria | Process Discovery and Exploration | M2 | Draft; not ratified as MVP |
| D09 | Discover and Inspect Process Models | Process Discovery and Exploration | M2 | Draft; not ratified as MVP |
| D10 | Search and Filter Process Data | Process Discovery and Exploration | M2 | Draft; not ratified as MVP |
| D11 | Inspect Process Variants and Repeated Activities | Process Discovery and Exploration | M2 | Draft; not ratified as MVP |
| D12 | Compare Process Discovery Methods | Process Discovery and Exploration | M3 | Draft; not ratified as MVP |
| D13 | Inspect Process Performance KPIs | Performance and Bottleneck Analysis | M2 | Draft; not ratified as MVP |
| D14 | Identify Candidate Bottlenecks | Performance and Bottleneck Analysis | M2 | Draft; not ratified as MVP |
| D15 | Analyze Queue Behavior | Performance and Bottleneck Analysis | M3 | Draft; not ratified as MVP |
| D16 | Inspect Evidence, Provenance and Limitations | Performance and Bottleneck Analysis | M2 | Draft; not ratified as MVP |
| D17 | Import External Reference KPIs | Performance and Bottleneck Analysis | M3 | Draft; not ratified as MVP |
| D18 | Calibrate the Plant Model and Validate the Baseline | Simulation and Validation | M3 | Draft; not ratified as MVP |
| D19 | Define and Validate a What-if Scenario | Simulation and Validation | M3 | Draft; not ratified as MVP |
| D20 | Run Scenarios and Compare Outcomes | Simulation and Validation | M3 | Draft; not ratified as MVP |
| D21 | Benchmark Detection Using Known Ground Truth | Simulation and Validation | M3 | Draft; not ratified as MVP |
| D22 | Evaluate Detection in Shadow Mode | Simulation and Validation | M4 | Draft; not ratified as MVP |
| D23 | Export Process Models and Analysis Results | Results and Interoperability | M2 | Draft; not ratified as MVP |
| D24 | Provide Results to External Consumers | Results and Interoperability | M3 | Draft; not ratified as MVP |
| D25 | Save and Retrieve Analysis Results | Results and Interoperability | M2 | Draft; not ratified as MVP |
| UC01 | Answer Informational Questions with Citations | Agentic / INFO | M3 | Draft; not ratified as MVP |
| UC02 | Upload and Map Logs with AI Assistance | Agentic / EXECUTE (Ingestion) | M2 | Draft; not ratified as MVP |
| UC03 | Reuse Validated Mapping Experience (Internal UC02 Alternative) | Agentic / — | M3 | Draft; not ratified as MVP |
| UC04 | Run a Guided Bottleneck Analysis | Agentic / EXECUTE (Bottleneck analysis) | M3 | Draft; not ratified as MVP |
| UC05 | Explain a Selected Process Element | Agentic / DATA-QA | M3 | Draft; not ratified as MVP |
| UC06 | Apply Natural-Language Filters and Views | Agentic / UI-CONTROL | M3 | Draft; not ratified as MVP |
| UC07 | Handle Multi-Intent Requests | Agentic / INFO + UI-CONTROL + DATA-QA | M3 | Draft; not ratified as MVP |
| UC08 | Answer Ad-Hoc Process Analysis Questions | Agentic / EXECUTE (piano libero) | M3 | Draft; not ratified as MVP |
| UC09 | Propose and Evaluate What-If Countermeasures | Agentic / EXECUTE (What-if) | M3 | Draft; not ratified as MVP |
| UC10 | Generate and Export Reports | Agentic / EXECUTE (Output) | M4 | Draft; not ratified as MVP |
| UC11 | Publish Results to Other Puzzle Pieces | Agentic / EXECUTE (Publish) | M3 | Draft; not ratified as MVP |
| UC12 | Handle Ambiguous or Out-of-Scope Requests | Agentic / CLARIFY | M3 | Draft; not ratified as MVP |
| UC13 | Respond to External Read-Only Agent Queries | Agentic / — (via MCP) | M3 | Draft; not ratified as MVP |

## Review rule

Before activating a use case for implementation, confirm its actors, preconditions, success/alternative flows, measurable acceptance criteria, interface needs, risks and planned milestone with the consolidated Chat 02 specification and the group.
