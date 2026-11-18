# P05 — Shared Docker development architecture (proposal, not merged)

## Current gates

The `master` branch currently has package scaffolds but no FastAPI application or Streamlit script to start. The `app` Compose profile is deliberately **not runnable as an application** yet. The proposed Dockerfiles build base Python images, NOT a finished P05 product. Backend/frontend lock files and application entrypoints are explicit integration gates.

The `research` service is **one-shot tooling only**, not a third application container and not a production dependency. PR #8 is open and its research tree is not present in `master`.

## Prerequisites

Docker Engine or Docker Desktop with Compose v2; Git. No local Python installation required. Linux: appropriate Docker group/rootless permissions. Windows: Docker Desktop + WSL2 preferred. Check `docker version` and `docker compose version`.

## Clone-clean setup

```sh
git clone https://github.com/ArturRembas/p05-bottleneck-detection.git
cd p05-bottleneck-detection
cp .env.docker.example .env
mkdir -p .local/private-data .local/results .local/research-runs
# After Docker proposal files are integrated:
docker compose --profile app config
# Build verifies Dockerfile parsing/base image only, not app dependencies:
docker compose --profile app build
```

## Historical research WITHOUT merging PR #8

```sh
git fetch origin research/pm4py-exploration
git worktree add ../p05-research origin/research/pm4py-exploration
# Set P05_RESEARCH_SOURCE in .env to absolute path:
# /.../p05-research/research/pm4py-exploration
# Research baseline audit (does not change source):
docker compose --profile research build research
docker compose --profile research run --rm research verify
# Individual experiment; creates separate local run directory:
docker compose --profile research run --rm research EXP-01
# Repeat EXP-02 ... EXP-10
```

Research inputs are mounted `:ro`; scripts execute on a temporary copy and output to `.local/research-runs/<UTC>-EXP-XX-<pid>/`. The original historical archive is never overwritten. Hash audit reports historical run logs not committed to GitHub as missing. Store comparison reports and commit SHAs with future validation evidence.

Important: `research-lock.txt` records exact historical version pins, **not a fully reproducible hashed lock**. Rebuilding may fail due to wheel availability on Python 3.14.4; document failures and decide whether to adjust platform or create a separately labeled reproduction environment. Never silently change historical versions.

## When the application is implemented

Add tested application entrypoints, hash-locked backend/frontend/development dependencies, actual `CMD` or Compose commands, and health checks in a separate PR. Then:

```sh
docker compose --profile app -f compose.yaml -f compose.dev.yaml up --build
docker compose --profile app ps
docker compose --profile app logs -f backend
docker compose --profile app down
# run pytest after the dev image actually installs pytest:
docker compose --profile app -f compose.yaml -f compose.dev.yaml run --rm backend python -m pytest -q
```

`-f` options must precede subcommands. These commands are **future acceptance checks**, not a claim of current success. For production, use validated immutable images without bind mounts and with published port/authentication controls; a production override is not needed at scaffold stage.

## Version strategy

- Keep Python version explicit for each image; initial compatibility candidate `3.14.4` because it matches the historic archive, **pending verification** with FastAPI/Streamlit/LangGraph/SimPy.
- Preserve EXP-01–10 versions: Python 3.14.4, PM4Py 2.7.23.11, Pandas 2.3.3.
- Treat Ubuntu PM4Py 2.7.23.12 / Pandas 3.1.1 as a **separate comparison matrix**, not an implicit upgrade.
- `requirements/*.in` are dependency intent, not locks. Generate resolved, hash-bearing locks per image/platform after testing; review and commit them. Fix the base image by digest after verification. Record `pip freeze`, architecture and build digest for each actual run.
- Use separate historical research environment even if runtime chooses different versions later. Do not pull the historical results into tests automatically.

## IDE independence

IDE configuration is local. Use terminal Docker Compose commands as the canonical test interface. Avoid IDE-specific files in the official Docker configuration.

## Operational troubleshooting

```sh
docker compose --profile app config
docker compose --profile app build --progress plain
docker compose --profile app ps -a
docker compose --profile app logs --tail=200 backend
docker compose --profile app down --remove-orphans
docker image ls
```

Never use `docker compose down -v` as a routine stop; it can delete named volumes. Do not paste secrets into logs/issues.
