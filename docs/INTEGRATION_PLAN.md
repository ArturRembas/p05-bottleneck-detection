# Docker integration plan and remaining application gates

## Source state
- `master` is the actual default/integration branch; do not rename it in this change.
- PR #8 has been merged into `master`; its research baseline is available under `research/pm4py-exploration/`.
- PR #9 has been merged into `master`; its validation and review history are recorded in [PR #9](https://github.com/ArturRembas/p05-bottleneck-detection/pull/9).
- Existing `contracts/draft-v0.1/` was not changed by PR #9.

## Historical infrastructure work item
**Title:** `chore: establish reproducible Docker/Compose development and research execution`

**Refs:** TASK-03, TASK-05; PR #8 (research baseline only).

## Historical branch and PR
- `chore/docker-compose-foundation` from `master`.
- Include Dockerfiles, Compose, dependency intents, research runner and documentation.
- Do not import application code or change contracts in this PR.

## Original merge gates (historical checklist)
1. Confirm two application services only; `research` is manual on-demand tooling.
2. Confirm `docker compose config` on Ubuntu and Windows/WSL2 and at least two machines.
3. Build images; if build fails, record specific package/wheel/image compatibility issues.
4. No service is advertised as operational until a real application entrypoint exists.
5. Research source mounted read-only; new results kept under `.local/research-runs/`.
6. Run EXP-01–10 under historical pins where possible; report differences in a new comparison report, never edit archived results.
7. Review the checksum manifest and explicitly enumerate missing historical logs.
8. `contracts/draft-v0.1/` unchanged; no API semantics changed.
9. No credentials/raw sensitive data or IDE-specific configuration committed.
10. Peer review of PR #9 is recorded; see its review history, including the scope of the review and subsequent Windows compatibility correction. PR #8 was merged independently.

## Candidate follow-up work (not new approved tasks)
1. `feat/minimal-api-health` — real FastAPI entrypoint and health endpoint, test and locked runtime image.
2. `feat/minimal-ui-health` — Streamlit client connected via `http://backend:8000` on internal Compose network.
3. `test/docker-ci` — pytest and smoke tests executed in containers.
4. `research/pm4py-compatibility` — repeat baseline under current dependencies, record structured differences.

The infrastructure PR is complete. Coordinate these follow-up proposals with the existing M1/M2 Issues and reviewed contracts; do not create duplicate tasks or assume the application entrypoints are already integrated.
