---
name: knowledge-platform
description: >
  Covers the platform layer: Docker infrastructure, CI/CD pipelines, and operational scripts
  that build, deploy, and run DeerFlow in development and production.
  Navigate when: modifying Dockerfiles or compose files, debugging deployment issues,
  adding CI workflows, changing the dev startup sequence, updating nginx routing,
  or modifying operational scripts.
  Excludes: application business logic (see backend/ and frontend/ domains).
  Keywords: Docker, docker-compose, nginx, CI/CD, GitHub Actions, deploy, serve, dev,
  Makefile, uvicorn, provisioner, sandbox, UV_EXTRAS, GATEWAY_WORKERS, BETTER_AUTH_SECRET.
---

## Module Structure

The platform layer provides the infrastructure and tooling to build, test, deploy, and run
DeerFlow across development, Docker-dev, and production environments. It consists of three
subdomains: Docker infrastructure (multi-stage builds, compose orchestration, nginx reverse
proxy), CI/CD pipelines (linting, testing, labeling, container publishing), and operational
scripts (service lifecycle, dependency management, configuration wizards).

### Directory Layout
- `docker/` — Docker Compose files, nginx configs, provisioner, dev entrypoint
  - `docker-compose.yaml` — Production deployment (nginx + frontend + gateway + optional provisioner)
  - `docker-compose-dev.yaml` — Development Docker environment with hot-reload mounts
  - `nginx/nginx.conf` — Production nginx reverse proxy configuration
  - `nginx/nginx.local.conf` — Local development nginx configuration
  - `dev-entrypoint.sh` — Gateway container startup script (UV_EXTRAS, self-heal sync)
  - `provisioner/` — Kubernetes sandbox provisioner (app.py, Dockerfile)
- `.github/workflows/` — CI/CD pipeline definitions
  - `lint-check.yml` — Backend (ruff) + frontend (eslint, prettier, typecheck, build)
  - `backend-unit-tests.yml` — Backend pytest suite
  - `frontend-unit-tests.yml` — Frontend test suite
  - `e2e-tests.yml` — Playwright E2E tests
  - `backend-blocking-io-tests.yml` — Blockbuster async blocking IO gate
  - `replay-e2e.yml` — Record/replay front-back contract verification
  - `triage.yml` — Consolidated PR/issue labeling (area, size, risk, needs-validation)
  - `label-sync.yml` — Declarative label sync from .github/labels.yml
- `scripts/` — Operational tooling and service lifecycle management
  - `serve.sh` — Unified service launcher (dev/prod/daemon/stop/restart)
  - `deploy.sh` — Production Docker deployment orchestration
  - `docker.sh` — Docker development environment management
  - `detect_uv_extras.py` — Resolve uv optional extras from env + config.yaml
  - `wait-for-port.sh` — Cross-platform TCP port readiness check
  - `setup_wizard.py` — Interactive configuration wizard
  - `check.py` — Dependency checker (node, pnpm, uv, nginx)
  - `configure.py`, `config-upgrade.sh`, `doctor.py` — Config management tools
  - `setup-sandbox.sh` — Pre-pull sandbox container image
  - `sync_labels.py` — GitHub label synchronization
  - `detect_blocking_io_static.py`, `detect_thread_boundaries.py` — Code quality scanners
  - `sandbox_memory_profile.py` — Kubernetes sandbox memory profiling
  - `cleanup-containers.sh`, `start-daemon.sh` — Service utilities
- `Makefile` — Top-level task runner dispatching to scripts
- `backend/Dockerfile` — Multi-stage backend build (builder → dev → runtime)
- `frontend/Dockerfile` — Multi-stage frontend build (base → dev → builder → prod)

### Key Entry Points
- `make dev` — Start all services in development mode (hot-reload)
- `make up` — Build and start production Docker services
- `make docker-start` — Start Docker development environment
- `scripts/serve.sh` — Core service lifecycle (gateway + frontend + nginx)
- `scripts/deploy.sh` — Production deployment with secret generation
- `docker-compose.yaml` — Production service definitions

## Gotchas
- Gateway defaults to a single worker (`GATEWAY_WORKERS=1`) because RunManager and StreamBridge are in-process singletons; multi-worker without sticky sessions breaks run cancellation, SSE reconnect, and IM channels (`docker/docker-compose.yaml`)
- The production compose file requires `DEER_FLOW_CONFIG_PATH` and `DEER_FLOW_EXTENSIONS_CONFIG_PATH` env vars to be set for the gateway container; without them the gateway reads host paths from .env and fails with FileNotFoundError inside the container (`docker/docker-compose.yaml`, `git:d8ecaf46`)
- nginx uses request-time DNS resolution (`set $gateway_upstream gateway:8001`) with `resolver 127.0.0.11 valid=0s` to avoid stale IPs when containers restart; static upstream blocks would cache dead IPs (`docker/nginx/nginx.conf`, `git:028493bf`)
- The `/api/` catch-all location in nginx must appear AFTER all explicit prefix/regex locations — nginx longest-prefix matching means more specific blocks win, but missing the catch-all breaks auth routes (`docker/nginx/nginx.conf`, `git:88d47f67`)
- `make dev` runs `uv sync` on every restart, which wipes optional extras unless `UV_EXTRAS` is set or `detect_uv_extras.py` auto-detects them from config.yaml (`scripts/serve.sh`, `git:94da8f67`)
- CORS is deferred to the Gateway allowlist (`GATEWAY_CORS_ORIGINS`), not handled at the nginx proxy layer — adding wildcard CORS at nginx bypasses CSRF origin checks (`docker/nginx/nginx.conf`, `git:c3bc6c7c`)
- uvicorn `--reload-exclude` with absolute paths requires the directory to exist before startup on Python 3.12, otherwise it globs the pattern and raises NotImplementedError (`scripts/serve.sh`, `docker/dev-entrypoint.sh`, `git:93e3281c`)

## Architecture
- Three deployment modes share the same codebase: local dev (`make dev` via serve.sh), Docker dev (`make docker-start` via docker-compose-dev.yaml), and production (`make up` via docker-compose.yaml + deploy.sh) (`Makefile`, `scripts/serve.sh`, `scripts/deploy.sh`)
- nginx serves as the unified reverse proxy on port 2026, routing `/api/*` to the gateway, `/api/sandboxes` to the provisioner, and everything else to the frontend (`docker/nginx/nginx.conf`)
- The backend Dockerfile uses a three-stage build: builder (compiles native extensions), dev (retains toolchain for startup-time `uv sync`), runtime (clean image without build-essential, ~200 MB smaller) (`backend/Dockerfile`)
- The frontend Dockerfile uses a four-stage build: base (shared setup), dev (deps only), builder (full Next.js compile), prod (minimal runtime with pre-built output) (`frontend/Dockerfile`)
- Sandbox execution supports three modes auto-detected from config.yaml: local (LocalSandboxProvider), aio (AioSandboxProvider via DooD), and provisioner (Kubernetes-based sandbox provisioning) (`scripts/deploy.sh`, `scripts/docker.sh`)
- The dev Docker entrypoint (`dev-entrypoint.sh`) was extracted from an inline compose command to keep the compose file readable and allow shellcheck linting (`docker/dev-entrypoint.sh`, `git:94da8f67`)

## Decisions
- Chose single-worker Gateway default as a stop-gap because shared cross-worker stream bridge (e.g. Redis) is not yet implemented; multi-worker support is tracked in issue #3191 (`docker/docker-compose.yaml`, `git:05ae4467`)
- Extracted `dev-entrypoint.sh` from inline compose command to improve readability and enable linting; the script is mounted read-only at runtime so edits take effect on restart without image rebuild (`docker/dev-entrypoint.sh`, `git:94da8f67`)
- `detect_uv_extras.py` is intentionally stdlib-only because it must run before `uv sync` populates the venv; it cannot depend on PyYAML (`scripts/detect_uv_extras.py`)
- Deferred CORS to Gateway allowlist rather than nginx proxy layer so CORS and CSRF origin checks stay aligned from a single source of truth (`docker/nginx/nginx.conf`, `git:c3bc6c7c`)

## Patterns
- All service lifecycle scripts follow a consistent pattern: detect mode from config.yaml, resolve environment variables with fallback chains, then delegate to docker compose or direct process management (`scripts/serve.sh`, `scripts/deploy.sh`, `scripts/docker.sh`)
- Secret generation uses a fallback chain: python3 → python → openssl, with generated secrets persisted to 0600 files under `DEER_FLOW_HOME` for survival across restarts (`scripts/deploy.sh`)
- The Makefile is a thin dispatcher that delegates to shell scripts; all substantive logic lives in `scripts/` (`Makefile`)
- Docker compose files use `env_file` for bulk variable inheritance and explicit `environment` blocks only for overrides and interpolated values (`docker/docker-compose.yaml`, `docker/docker-compose-dev.yaml`)

## Conventions
- All shell scripts must be run from the repo root directory; they auto-detect their location via `$(dirname "${BASH_SOURCE[0]}")/..` (`scripts/serve.sh`, `scripts/deploy.sh`, `scripts/docker.sh`)
- `docker/dev-entrypoint.sh` is anchored at `/bin/sh` (not bash) for alpine compatibility and uses POSIX-only constructs (`docker/dev-entrypoint.sh`)
- nginx config uses `proxy_buffering off` and `proxy_cache off` at the server level to avoid repeating these directives in every location block (`docker/nginx/nginx.conf`, `git:48e038f7`)
- Windows compatibility is handled via `scripts/run-with-git-bash.cmd` wrapper and `_pick_python()` fallback chains in shell scripts (`Makefile`, `scripts/serve.sh`)

## Dependencies
- nginx:alpine is the reverse proxy base image for both dev and production (`docker/docker-compose.yaml`, `docker/docker-compose-dev.yaml`)
- ghcr.io/astral-sh/uv:0.7.20 is the default UV source image, overridable via `UV_IMAGE` build arg for restricted networks (`backend/Dockerfile`)
- node:22-alpine is the frontend base image; pnpm@10.26.2 is pinned via corepack (`frontend/Dockerfile`)
- python:3.12-slim-bookworm is the backend base image (`backend/Dockerfile`)
- GitHub Actions use `actions/checkout@v6`, `actions/setup-python@v6`, `astral-sh/setup-uv@v7`, `actions/setup-node@v4` (`.github/workflows/`)

## Child Knowledge Nodes
- `./docker-infrastructure/SKILL.md` — Navigate when: modifying Dockerfiles, compose files, nginx config, provisioner, or debugging container issues
- `./ci-cd/SKILL.md` — Navigate when: adding/modifying CI workflows, debugging pipeline failures, understanding PR labeling automation
- `./operational-scripts/SKILL.md` — Navigate when: modifying serve.sh, deploy.sh, docker.sh, setup wizard, dependency detection, or service lifecycle scripts
