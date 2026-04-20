# syntax=docker/dockerfile:1

# --- Stage 1: install dependencies ---
FROM node:18-alpine AS builder

WORKDIR /app
COPY package.json .
# Install production deps only
RUN npm install --omit=dev

# --- Stage 2: lean runtime ---
FROM node:18-alpine

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy installed modules and app source from builder
COPY --from=builder /app/node_modules ./node_modules
COPY app.js .
COPY public ./public

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

CMD ["node", "app.js"]