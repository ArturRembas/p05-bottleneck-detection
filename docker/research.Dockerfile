ARG PYTHON_IMAGE=python:3.14.4-slim
FROM ${PYTHON_IMAGE}
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
RUN apt-get update && apt-get install -y --no-install-recommends bash graphviz ca-certificates \
 && rm -rf /var/lib/apt/lists/*
COPY research-lock.txt /tmp/research-lock.txt
RUN python -m pip install --no-cache-dir -r /tmp/research-lock.txt
COPY tools/run-research.sh /opt/p05/run-research.sh
COPY tools/check-research-manifest.py /opt/p05/check-research-manifest.py
RUN chmod 755 /opt/p05/run-research.sh
WORKDIR /tmp
