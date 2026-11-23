ARG PYTHON_IMAGE=python:3.14.4-slim
FROM ${PYTHON_IMAGE} AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /workspace
# Integration gate: add validated and hash-locked Streamlit dependencies.
# COPY requirements/frontend.lock /tmp/frontend.lock
# RUN python -m pip install --require-hashes -r /tmp/frontend.lock
# Add the Streamlit command only when ui/app.py is implemented and tested.
