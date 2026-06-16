---
name: knowledge-platform-docker-infrastructure
description: >
  Covers Docker multi-stage builds, compose orchestration, nginx reverse proxy configuration,
  and the Kubernetes sandbox provisioner for DeerFlow.
  Navigate when: modifying Dockerfiles, changing compose service definitions, debugging
  container networking or volume mounts, updating nginx routing rules, changing the provisioner,
  or troubleshooting Docker-based deployments.
  Excludes: CI/CD pipelines (see ../ci-cd/), operational scripts (see ../operational-scripts/).
  Keywords: Docker, docker-compose, nginx, provisioner, DooD, multi-stage build, uvicorn,
  GATEWAY_WORKERS, UV_EXTRAS, dev-entrypoint, sandbox, reverse proxy, SSE, upstream.
---

## Module Structure

Docker infrastructure defines how DeerFlow is containerized and orchestrated across development
and production environments. It includes multi-stage Dockerfiles for backend and frontend, two
docker-compose configurations (dev and prod), nginx as a unified reverse proxy, and an optional
Kubernetes-based sandbox provisioner.

### Directory Layout
- `docker/` — Container orchestration and configuration
  - `docker-compose.yaml` — Production deployment: nginx + frontend + gateway + optional provisioner
  - `docker-compose-dev.yaml` — Development environment with hot-reload source mounts
  - `nginx/nginx.conf` — Production nginx config (path-based routing, SSE support, request-time DNS)
  - `nginx/nginx.local.conf` — Local development nginx config (used by `make dev`)
  - `dev-entrypoint.sh` — Gateway container startup: UV_EXTRAS resolution, self-heal uv sync, uvicorn handoff
  - `provisioner/` — Kubernetes sandbox provisioner
    - `app.py` — FastAPI app managing per-sandbox Pod + Service lifecycle
    - `Dockerfile` — Provisioner container build
    - `README.md` — Provisioner usage and PVC upgrade notes
- `backend/Dockerfile` — Multi-stage backend build (builder → dev → runtime)
- `frontend/Dockerfile` — Multi-stage frontend build (base → dev → builder → prod)

### Key Entry Points
- `docker-compose.yaml` — `make up` production deployment
- `docker-compose-dev.yaml` — `make docker-start` development environment
- `backend/Dockerfile` — Backend image build with optional `UV_EXTRAS` build arg
- `frontend/Dockerfile` — Frontend image build with `--target dev|prod`
- `docker/dev-entrypoint.sh` — Gateway container startup logic
- `docker/nginx/nginx.conf` — Reverse proxy routing rules

## Gotchas
- Gateway defaults to a single worker (`GATEWAY_WORKERS=1`) because RunManager and StreamBridge are in-process singletons; multi-worker without sticky sessions breaks run cancellation, SSE reconnect, request dedup, and IM channels (`docker/docker-compose.yaml`, `git:05ae4467`)
- The production compose file requires `DEER_FLOW_CONFIG_PATH` and `DEER_FLOW_EXTENSIONS_CONFIG_PATH` env vars; without them the gateway reads host paths from .env and fails with FileNotFoundError inside the container (`docker/docker-compose.yaml`, `git:d8ecaf46`)
- nginx uses request-time DNS resolution (`set $gateway_upstream gateway:8001`) with `resolver 127.0.0.11 valid=0s` — static upstream blocks would cache dead IPs after container restarts (`docker/nginx/nginx.conf`, `git:028493bf`)
- The `/api/` catch-all location must appear AFTER all explicit prefix/regex locations; nginx longest-prefix matching means more specific blocks win, but missing the catch-all breaks auth routes like `/api/v1/auth/*` (`docker/nginx/nginx.conf`, `git:88d47f67`)
- uvicorn `--reload-exclude` with absolute paths requires the directory to exist before startup on Python 3.12; otherwise it globs the pattern and raises NotImplementedError, crashing startup on a fresh checkout (`docker/dev-entrypoint.sh`, `git:93e3281c`)
- The dev compose mounts `gateway-venv` as a named volume to preserve the .venv built during image build — mounting the full `backend/` directory would shadow it with the empty host directory (`docker/docker-compose-dev.yaml`)
- `proxy_buffering off` is set at the server level to avoid permission errors when nginx runs as non-root and tries to spool large responses to `/var/lib/nginx/proxy` (`docker/nginx/nginx.conf`, `git:48e038f7`)
- The provisioner's `USERDATA_PVC_NAME` uses subPath `deer-flow/users/{user_id}/threads/{thread_id}/user-data` — older versions used `threads/{thread_id}/user-data` and require migration (`docker/provisioner/README.md`, `git:e74e126e`)
- The `UV_EXTRAS` build arg in backend/Dockerfile treats the value as a single token (e.g. `postgres`), unlike the dev entrypoint which splits on commas/whitespace for multi-extra support (`backend/Dockerfile`, `docker/dev-entrypoint.sh`)

## Architecture
- Three-stage backend build: builder (compiles native extensions with build-essential + Node.js), dev (retains toolchain for startup-time `uv sync`), runtime (clean python:3.12-slim-bookworm without build-essential, ~200 MB smaller) (`backend/Dockerfile`)
- Four-stage frontend build: base (shared pnpm setup), dev (deps only, CMD overridden by compose), builder (full `pnpm build` with `SKIP_ENV_VALIDATION=1`), prod (minimal node:22-alpine with pre-built output) (`frontend/Dockerfile`)
- nginx serves as unified reverse proxy on port 2026 with path-based routing: `/api/langgraph/*` → gateway (with rewrite), explicit `/api/*` prefix blocks → gateway, `/api/sandboxes` → provisioner, everything else → frontend (`docker/nginx/nginx.conf`)
- Sandbox execution uses Docker-out-of-Docker (DooD): the gateway/provisioner containers mount the host Docker socket and start sandbox containers as siblings on the host network (`docker/docker-compose.yaml`, `docker/docker-compose-dev.yaml`)
- The dev entrypoint script runs `uv sync --all-packages` at container start with self-heal (recreate .venv and retry on failure), then hands off to uvicorn via `exec` so uvicorn becomes PID 1 (`docker/dev-entrypoint.sh`)
- Named Docker volumes (`gateway-venv`, `gateway-uv-cache`) persist across container restarts in dev mode; the uv cache volume avoids macOS symlink issues with host bind mounts (`docker/docker-compose-dev.yaml`)

## Decisions
- Chose single-worker Gateway default as a stop-gap; shared cross-worker stream bridge (Redis) is not yet implemented, tracked in issue #3191 (`docker/docker-compose.yaml`, `git:05ae4467`)
- Extracted `dev-entrypoint.sh` from inline compose command to improve readability and enable shellcheck linting; mounted read-only so edits take effect on restart without image rebuild (`docker/dev-entrypoint.sh`, `git:94da8f67`)
- Deferred CORS to Gateway allowlist (`GATEWAY_CORS_ORIGINS`) rather than nginx proxy layer so CORS and CSRF origin checks stay aligned from a single source of truth (`docker/nginx/nginx.conf`, `git:c3bc6c7c`)
- Use `resolver 127.0.0.11 valid=0s` (Docker's internal DNS) with `set` variables instead of `upstream` blocks to force request-time DNS resolution, preventing stale IPs after container restarts (`docker/nginx/nginx.conf`, `git:028493bf`)

## Patterns
- Docker compose files use `env_file` for bulk variable inheritance and explicit `environment` blocks only for overrides and interpolated values (`docker/docker-compose.yaml`, `docker/docker-compose-dev.yaml`)
- `NO_PROXY` is always declared in compose files to exempt internal service hostnames (gateway, frontend, nginx, provisioner, host.docker.internal) from proxy, while `HTTP_PROXY`/`HTTPS_PROXY` are inherited from `.env` (`docker/docker-compose.yaml`, `docker/docker-compose-dev.yaml`)
- CLI auth directories (`.claude`, `.codex`) are mounted read-only with `create_host_path: true` for auto-auth support in sandboxed code execution (`docker/docker-compose.yaml`, `docker/docker-compose-dev.yaml`)
- nginx location blocks for API routes all share the same pattern: `proxy_pass http://$gateway_upstream`, `proxy_http_version 1.1`, standard proxy headers, with buffering directives at server level (`docker/nginx/nginx.conf`)

## Conventions
- `docker/dev-entrypoint.sh` is anchored at `/bin/sh` (not bash) for alpine compatibility and uses POSIX-only constructs (`docker/dev-entrypoint.sh`)
- nginx config uses `proxy_buffering off` and `proxy_cache off` at the server level to avoid repeating these directives in every location block (`docker/nginx/nginx.conf`, `git:48e038f7`)
- The nginx `listen [::]:2026` line is conditionally removed in dev compose when IPv6 is unavailable (via `test -e /proc/net/if_inet6`) (`docker/docker-compose-dev.yaml`)
- All container names follow the `deer-flow-<service>` pattern for both dev and production (`docker/docker-compose.yaml`, `docker/docker-compose-dev.yaml`)

## Dependencies
- nginx:alpine is the reverse proxy base image for both dev and production (`docker/docker-compose.yaml`, `docker/docker-compose-dev.yaml`)
- ghcr.io/astral-sh/uv:0.7.20 is the default UV source image, overridable via `UV_IMAGE` build arg (`backend/Dockerfile`)
- node:22-alpine is the frontend base image; pnpm@10.26.2 is pinned via corepack (`frontend/Dockerfile`)
- python:3.12-slim-bookworm is the backend base image (`backend/Dockerfile`)
- docker:cli image is used to copy the Docker CLI binary into backend containers for DooD sandbox support (`backend/Dockerfile`)
- The provisioner depends on `fastapi`, `uvicorn[standard]`, and `kubernetes` Python packages (`docker/provisioner/Dockerfile`)

## Networking
- Production compose uses a single `deer-flow` bridge network; dev compose uses `deer-flow-dev` with a fixed subnet `192.168.200.0/24` (`docker/docker-compose.yaml`, `docker/docker-compose-dev.yaml`)
- `host.docker.internal:host-gateway` extra_hosts mapping enables containers to reach the host for DooD sandbox networking (`docker/docker-compose.yaml`, `docker/docker-compose-dev.yaml`)
- nginx SSE/streaming support: `proxy_set_header Connection ''`, `chunked_transfer_encoding on`, `X-Accel-Buffering no`, and 600s timeouts on the `/api/langgraph/` location (`docker/nginx/nginx.conf`)
- The provisioner location uses a `set $provisioner_upstream` variable so nginx resolves it at request time, allowing nginx to start even when the provisioner container is not running (`docker/nginx/nginx.conf`)
