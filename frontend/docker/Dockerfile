# ── Base ───────────────────────────────────────────────────────────────
FROM node:22-alpine AS base

WORKDIR /app

RUN apk add --no-cache curl

# Expose Vite's default development port
EXPOSE 5173

# will add later
#CMD []

# ── Development ───────────────────────────────────────────────────────────────
FROM base AS development