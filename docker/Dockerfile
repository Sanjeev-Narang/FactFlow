# ── STAGE 0: Production Frontend Builder ─────────────────────────────────────
FROM node:22-alpine AS frontend-builder
WORKDIR /app
COPY ./frontend/package*.json ./
RUN npm ci
COPY ./frontend/ .
RUN npm run build

# ── STAGE 1: Shared Base ─────────────────────────────────────────────────────
FROM python:3.13-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# ── STAGE 2: Development ─────────────────────────────────────────────────────
FROM base AS development

COPY --from=frontend-builder /app/dist /tmp/dist

EXPOSE 8000



# ── STAGE 3: Production Backend ──────────────────────────────────────────────
FROM base AS production

# Force the container to use the venv's Python and binaries
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=FactFlow.settings.production

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

# Copy backend source code
COPY . .

# 🚀 NEW: Pull the compiled Vite assets directly into your backend container
COPY --from=frontend-builder /app/dist /app/frontend/dist

# 🚀 NEW: Compile all static mappings right before starting the container
RUN uv run manage.py collectstatic --noinput

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

