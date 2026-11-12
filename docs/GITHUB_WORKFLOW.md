# GitHub Collaboration Rules — Proposal

## Source of truth

- Official course documents define external requirements.
- The group Decision Register is authoritative for approved choices.
- Version-controlled specifications and code reflect implementation.
- GitHub Issues describe proposed/approved requirements, outstanding work and questions.

## Repository practices

- `main`: reviewed shared integration branch.
- Changes: short-lived `feat/*`, `fix/*`, `docs/*`, `test/*`, `chore/*` branches.
- Every PR: link Issues, describe the change, show test evidence and state known limitations.
- Avoid force-pushing to `main`, secrets, private data and unreviewed changes.
- Prefer peer reviews even when branch protection is not available on the GitHub plan.

## Board configuration

Create GitHub Project **P05 — Development & Roadmap** with statuses `Backlog`, `Ready`, `In Progress`, `In Review`, and `Done`. Add `Priority` single-select `P0`, `P1`, `P2`; optional `Start date` and `Target date`. Suggested views: Board grouped by Status, Table grouped by component, Roadmap grouped by milestone.

## Approval versus completion

- `spec:proposed`: a candidate, not approved.
- `spec:needs-review`: unresolved or awaiting group agreement.
- `spec:approved`: evidence of formal group approval, with Decision ID.
- A merged PR is not evidence that the end-to-end use case is fully implemented.
- Mark `Done` only after acceptance criteria and tests are verified.

See `docs/USE_CASE_CATALOG.md` and `docs/MILESTONES.md` for scope and targets.
