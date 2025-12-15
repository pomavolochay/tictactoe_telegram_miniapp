# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:python3.12-bookworm AS base
WORKDIR /app
ENV UV_PROJECT_ENV=.venv
ENV PATH="/app/.venv/bin:$PATH"
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY README.md ./README.md
COPY apps/backend/pyproject.toml ./pyproject.toml
COPY apps/backend/src ./src
RUN uv sync --no-dev

FROM base AS dev
CMD ["uv", "run", "uvicorn", "tictactoe.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS prod
EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
CMD ["uv", "run", "uvicorn", "tictactoe.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
