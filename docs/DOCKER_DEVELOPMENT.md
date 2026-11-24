# P05 — Shared Docker development environment

## Current gates

The infrastructure is integrated on `master` through PR [#9](https://github.com/ArturRembas/p05-bottleneck-detection/pull/9). Its recorded validation covers Ubuntu, Fedora/Podman and Windows/WSL2; this is infrastructure and research evidence, not application acceptance.

The `master` branch currently has package scaffolds but no FastAPI application or Streamlit script to start. The `app` Compose profile is deliberately **not runnable as an application** yet. The application Dockerfiles build scaffold images, NOT a finished P05 product. Backend/frontend lock files and application entrypoints are explicit integration gates.

The `research` service is **one-shot tooling only**, not a third application container and not a production dependency. PR #8 has been merged into `master`. The historical research baseline is available under `research/pm4py-exploration/`.

## Prerequisites

Docker Engine or Docker Desktop with Compose v2; Git. No local Python installation required. Linux: appropriate Docker group/rootless permissions. Windows: Docker Desktop + WSL2 preferred. Check `docker version` and `docker compose version`.

## Clone-clean setup

```sh
git clone --branch master https://github.com/ArturRembas/p05-bottleneck-detection.git
cd p05-bottleneck-detection
cp .env.docker.example .env
mkdir -p .local/private-data .local/results .local/research-runs
# Configuration and scaffold-image checks (not application runtime tests):
docker compose --profile app config --quiet
docker compose --profile app build
```

## Historical research (PR #8 merged)

```sh
# Run from a checkout containing merged PRs #8 and #9.
# Set P05_RESEARCH_SOURCE=./research/pm4py-exploration in .env once.
# Edit the existing setting instead of appending duplicate keys.
# Research baseline audit (does not change source):
docker compose --profile research build research
docker compose --profile research run --rm research verify
# Individual experiment; creates separate local run directory:
docker compose --profile research run --rm research EXP-01
# Repeat EXP-02 ... EXP-10
```

Research inputs are mounted `:ro`; scripts execute on a temporary copy and output to `.local/research-runs/<UTC>-EXP-XX-<pid>/`. The original historical archive is never overwritten. The PR #9 audit recorded 37 matching checksums, no mismatches and 10 missing historical run logs; inspect the actual audit output and investigate unexpected missing files or mismatches. Store comparison reports and commit SHAs with future validation evidence.

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
docker compose --progress plain --profile app build
docker compose --profile app ps -a
docker compose --profile app logs --tail=200 backend
docker compose --profile app down --remove-orphans
docker image ls
```

Never use `docker compose down -v` as a routine stop; it can delete named volumes. Do not paste secrets into logs/issues.
