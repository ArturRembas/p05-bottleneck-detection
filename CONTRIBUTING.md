# Contributing to P05

This repository supports collaborative academic development by the three P05 team members. The workflow favors small, reviewable changes and reproducible evidence over unnecessary process overhead.

## Before you start

1. Read `README.md`, `docs/PROJECT_SCOPE.md`, and the applicable use-case Issue.
2. Confirm that the requested work is **approved**, **proposed**, or an **open question**. Do not silently extend scope.
3. Check for an existing Issue to avoid duplication; agree an interface before parallel implementation.
4. Do not assign permanent ownership of components without an explicit group decision.

## Branching and review

Update `main`, then create a short-lived branch:

```bash
git switch main
git pull --ff-only origin main
git switch -c feat/log-validation
```

Use `feat/`, `fix/`, `docs/`, `test/` or `chore/` prefixes. Keep commits focused and use messages such as `feat: validate event timestamps`, `test: cover malformed CSV`, or `docs: clarify queue-time semantics`.

Before opening a Pull Request:

- Run relevant local tests and document their commands/results.
- Check that no mock KPI is presented as computed from data.
- Add or update schemas, examples and documentation when interfaces change.
- Keep deterministic metrics, AI interpretations and simulation estimates distinguishable.
- Check that secrets or disallowed source datasets were not staged (`git diff --cached`).

Open a PR against `main`, link the Issue (e.g. `Closes #123` only if the change actually satisfies the Issue's criteria), and request review from another group member. The author should not self-approve substantive behavior changes.

## Definition of Done (proposed, pending group review)

An implementation issue may be closed when:

- Acceptance criteria were met and reproduced.
- Relevant tests run successfully (or omissions are explicitly justified).
- Behavior on invalid data and data limitations is documented.
- Machine-readable contracts are updated if necessary.
- Human approval and privacy constraints are preserved.
- At least one reviewer has assessed the PR.

A use-case Issue remains open until the **end-to-end behavior** and its acceptance criteria have been verified, even if several implementation tasks were merged.

## Data-handling conventions

Use only synthetic or distributable fixtures inside `examples/` and `data/synthetic/`. Keep raw/private logs and derived sensitive data outside Git and respect `.gitignore`. Store configuration examples in `.env.example`, never real secrets. Do not commit LLM prompts containing private industrial data.

## Communication and decisions

Use GitHub Issues for tasks, questions and review comments. An architectural choice becomes **approved** only after group agreement documented in the decision register; link the decision ID in the Issue/PR. The consolidated decision register on Google Drive remains the source of record until the group explicitly changes this policy.
