# Pin the image digest after the team validates availability and Python compatibility.
ARG PYTHON_IMAGE=python:3.14.4-slim
FROM ${PYTHON_IMAGE} AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /workspace
# No application dependencies or entrypoints are invented by the scaffold.

FROM base AS runtime
# Integration gate: replace this comment with an installation of a fully resolved,
# versioned requirements lock (including hashes), after dependency compatibility is tested.
# COPY requirements/backend.lock /tmp/backend.lock
# RUN python -m pip install --require-hashes -r /tmp/backend.lock

FROM runtime AS dev
# Integration gate: tests dependencies must be installed via reviewed dev.lock.
# COPY requirements/dev.lock /tmp/dev.lock
# RUN python -m pip install --require-hashes -r /tmp/dev.lock
