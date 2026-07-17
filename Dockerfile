# ==========================================
# Stage 1: Build Frontend
# ==========================================
FROM node:26-alpine3.23 AS frontend-build

WORKDIR /app/frontend

# Install pnpm globally
RUN npm install -g pnpm

# Copy package.json and pnpm-lock.yaml first for better caching
COPY frontend/package.json frontend/pnpm-lock.yaml ./

# Install dependencies (frozen-lockfile is the pnpm equivalent of npm ci)
RUN pnpm install --frozen-lockfile

# Copy the rest of the frontend code
COPY frontend/ .

# Build the frontend
RUN pnpm run build

# ==========================================
# Stage 2: Setup Backend
# ==========================================
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim

# Define the arguments! Default to 1000 (the most common Linux user ID)
ARG UID=1000
ARG GID=1000

# Setup a non-root user!
# We use the ${UID} and ${GID} variables so it matches host machine!
RUN groupadd --system --gid ${GID} ariabox \
 && useradd --system --gid ${GID} --uid ${UID} --create-home ariabox

WORKDIR /app

# Performance & Logging tweaks
ENV PYTHONUNBUFFERED=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Install dependencies first
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=backend/uv.lock,target=uv.lock \
    --mount=type=bind,source=backend/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev

# Copy the rest of the backend code and install the project itself
COPY backend/ /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Copy Frontend's built files into the final image
COPY --from=frontend-build /app/frontend/dist /app/frontend_dist

# Environment variables for production
ENV FRONTEND_DIST_DIR=/app/frontend_dist
ENV HOST_URL=0.0.0.0
ENV HOST_PORT=8960

EXPOSE 8960

# Give non-root user (created above) ownership of the /app folder
RUN chown -R ariabox:ariabox /app

# Use non-root user to run the app
USER ariabox

# Run the app using the CLI entry point
CMD ["uv", "run", "ariabox"]
