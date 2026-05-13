# Copyright (c) 2026 Vlady
# SPDX-License-Identifier: AGPL-3.0-only

# ── Build stage ────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip

# Install deps first (cache layer)
COPY pyproject.toml .
RUN pip install --no-cache-dir --target=/install \
    mcp>=1.0.0 httpx>=0.27.0 pydantic>=2.0.0 pyyaml>=6.0 python-dotenv>=1.0.0 tenacity>=8.0.0 \
    openai>=1.0.0 anthropic>=0.30.0 ollama>=0.4.0

# ── Runtime stage ──────────────────────────────────────────────────────────
FROM python:3.12-slim

LABEL org.opencontainers.image.title="ServiceNow Universal MCP"
LABEL org.opencontainers.image.description="LLM-agnostic MCP server for ServiceNow"
LABEL org.opencontainers.image.source="https://github.com/vladarchitectservicenow-oss/servicenow-universal-mcp"
LABEL org.opencontainers.image.licenses="AGPL-3.0"
LABEL org.opencontainers.image.version="1.1.0"

WORKDIR /app

COPY --from=builder /install /usr/local/lib/python3.12/site-packages/

# Copy source
COPY src/ /app/src/
COPY pyproject.toml /app/

ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV MCP_SERVER_PORT=8000
ENV MCP_LOG_LEVEL=INFO

EXPOSE 8000

# Non-root user
RUN useradd --create-home --shell /bin/bash mcp && chown -R mcp:mcp /app
USER mcp

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health', timeout=5)" || exit 1

ENTRYPOINT ["python", "-m", "mcp_server.cli"]
CMD ["--http", "--port", "8000"]
