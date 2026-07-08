---
name: knowledge-platform-operational-scripts
description: >
  Covers operational scripts for DeerFlow: service lifecycle management (serve.sh, deploy.sh,
  docker.sh), dependency detection (detect_uv_extras.py, check.py), configuration wizards
  (setup_wizard.py, configure.py, config-upgrade.sh), code quality scanners, and utility
  scripts.
  Navigate when: modifying the dev startup sequence, changing deployment logic, updating
  the setup wizard, debugging service lifecycle issues, adding new operational tooling,
  or modifying dependency detection.
  Excludes: Docker infrastructure (see ../docker-infrastructure/), CI/CD pipelines (see ../ci-cd/).
  Keywords: serve.sh, deploy.sh, docker.sh, setup_wizard, detect_uv_extras, wait-for-port,
  check.py, configure, config-upgrade, doctor, sandbox, dev, prod, daemon, stop, restart.
---

## Module Structure

Operational scripts manage the full lifecycle of DeerFlow: dependency checking, configuration,
service startup/shutdown, deployment, and code quality scanning. They are the primary interface
between developers and the running system, invoked through `make` targets in the root Makefile.

### Directory Layout
- `scripts/serve.sh` — Unified service launcher (dev/prod/daemon/stop/restart) for local development
- `scripts/deploy.sh` — Production Docker deployment: build, start, down, secret generation
- `scripts/docker.sh` — Docker development environment: init, start, stop, logs, restart
- `scripts/detect_uv_extras.py` — Resolve uv optional extras from UV_EXTRAS env or config.yaml
- `scripts/wait-for-port.sh` — Cross-platform TCP port readiness check with timeout
- `scripts/setup_wizard.py` — Interactive configuration wizard (LLM provider, model selection)
- `scripts/wizard/` — Wizard submodules
  - `providers.py` — LLM provider definitions with per-model vision overrides
  - `steps/llm.py` — LLM provider and model selection step
  - `steps/search.py` — Search provider configuration step
  - `steps/execution.py` — Execution/sandbox configuration step
  - `ui.py` — Terminal UI utilities
  - `writer.py` — Config file generation
- `scripts/check.py` — Cross-platform dependency checker (node, pnpm, uv, nginx)
- `scripts/check.sh` — Shell-based dependency check (legacy)
- `scripts/configure.py` — Generate local config files from templates
- `scripts/config-upgrade.sh` — Merge new fields from config.example.yaml into config.yaml
- `scripts/doctor.py` — Configuration and system health verification
- `scripts/setup-sandbox.sh` — Pre-pull sandbox container image
- `scripts/detect_blocking_io_static.py` — Static inventory of blocking IO calls
- `scripts/detect_thread_boundaries.py` — Async/thread boundary point inventory
- `scripts/sync_labels.py` — GitHub label synchronization from declarative config
- `scripts/sandbox_memory_profile.py` — Kubernetes sandbox pod memory snapshot collection
- `scripts/cleanup-containers.sh` — Remove sandbox containers by name pattern
- `scripts/start-daemon.sh` — Daemon mode service launcher
- `scripts/run-with-git-bash.cmd` — Windows Git Bash wrapper for shell scripts
- `scripts/export_claude_code_oauth.py` — Claude Code OAuth credential export
- `scripts/load_memory_sample.py` — Memory sample data loader
- `scripts/tool-error-degradation-detection.sh` — Tool error degradation detection
- `Makefile` — Top-level task runner dispatching to these scripts

### Key Entry Points
- `make dev` → `scripts/serve.sh --dev` — Start all services in development mode
- `make up` → `scripts/deploy.sh` — Build and start production Docker services
- `make docker-start` → `scripts/docker.sh start` — Start Docker development environment
- `make setup` → `scripts/setup_wizard.py` — Interactive configuration
- `make check` → `scripts/check.py` — Dependency verification
- `make stop` → `scripts/serve.sh --stop` — Stop all services

## Gotchas
- `serve.sh` resolves `DEERFLOW_ROOTS` from the main checkout + all linked git worktrees because all worktrees share the same dev ports (8001/3000/2026); a service started from any worktree must be reclaimable from another, otherwise `make stop`/`make dev` can neither kill nor take over a port (`scripts/serve.sh`, `git:cd5bedaa`)
- `serve.sh` uses `lsof` to check if a PID belongs to a deer-flow worktree by matching open file paths against `DEERFLOW_ROOTS` with a trailing slash guard to prevent sibling dirs like `deer-flow-notes` from matching (`scripts/serve.sh`)
- `detect_uv_extras.py` is intentionally stdlib-only because it must run BEFORE `uv sync` populates the venv — it cannot depend on PyYAML or any third-party library (`scripts/detect_uv_extras.py`)
- `detect_uv_extras.py` validates extra names against `^[A-Za-z][A-Za-z0-9_-]*$` — a stray shell metacharacter in `.env` cannot reach `uv sync` downstream; invalid entries are dropped with a stderr warning (`scripts/detect_uv_extras.py`)
- `deploy.sh` generates `BETTER_AUTH_SECRET` and `DEER_FLOW_INTERNAL_AUTH_TOKEN` with a fallback chain (python3 → python → openssl) and persists them to 0600 files under `DEER_FLOW_HOME` for survival across restarts (`scripts/deploy.sh`, `git:8cd4710b`)
- `deploy.sh` auto-detects sandbox mode from config.yaml by parsing the `sandbox.use` and `sandbox.provisioner_url` fields with awk; the detection logic is duplicated in `docker.sh` with slightly different provider class names (`scripts/deploy.sh`, `scripts/docker.sh`)
- `serve.sh` creates `backend/sandbox` directory before uvicorn startup because uvicorn's `--reload-exclude` with absolute paths requires the directory to exist on Python 3.12 — otherwise it globs and raises NotImplementedError (`scripts/serve.sh`, `git:93e3281c`)
- `wait-for-port.sh` validates the port argument as numeric and in range 1-65535, and supports Windows via PowerShell `Get-NetTCPConnection` fallback (`scripts/wait-for-port.sh`, `git:18bbb82f`)
- The `UV_EXTRAS` env var is parsed differently in local vs Docker image-build paths: `detect_uv_extras.py` and `dev-entrypoint.sh` split on commas/whitespace for multi-extra support, but `backend/Dockerfile` treats it as a single token (`scripts/detect_uv_extras.py`, `backend/Dockerfile`, `git:94da8f67`)
- `serve.sh`'s `stop_all()` force-kills survivors on ports 8001, 3000, and 2026 after graceful shutdown — port 2026 is included so a lingering nginx that wasn't matched by name still gets reclaimed (`scripts/serve.sh`, `git:cd5bedaa`)

## Architecture
- Three deployment modes share the same `serve.sh` script: `--dev` (hot-reload uvicorn), `--prod` (optimized, pre-built frontend), and `--daemon` (background via nohup) (`scripts/serve.sh`)
- `serve.sh` starts services in a fixed order: Gateway (port 8001, 30s timeout) → Frontend (port 3000, 120s timeout) → Nginx (port 2026, 10s timeout); each service must be port-ready before the next starts (`scripts/serve.sh`)
- `deploy.sh` handles the full production lifecycle: config seeding (from example templates), secret generation (BETTER_AUTH_SECRET, DEER_FLOW_INTERNAL_AUTH_TOKEN), sandbox mode detection, and docker compose orchestration (`scripts/deploy.sh`)
- `detect_uv_extras.py` resolves extras in priority order: 1) `UV_EXTRAS` env var, 2) auto-detection from config.yaml (database.backend=postgres, checkpointer.type=postgres, channels.discord.enabled=true) (`scripts/detect_uv_extras.py`)
- The setup wizard (`setup_wizard.py`) uses a modular step-based architecture with per-provider model definitions, vision capability overrides, and config file generation via `wizard/writer.py` (`scripts/setup_wizard.py`, `scripts/wizard/`)
- `docker.sh` and `deploy.sh` both contain independent sandbox mode detection logic using awk to parse config.yaml — they detect `local`, `aio`, and `provisioner` modes but use slightly different provider class name strings (`scripts/deploy.sh`, `scripts/docker.sh`)

## Decisions
- `detect_uv_extras.py` is stdlib-only by design because it must run before the venv exists; this constrains YAML parsing to a hand-rolled parser that handles only the shallow nesting DeerFlow uses (`scripts/detect_uv_extras.py`)
- Chose to NOT suppress stderr from `detect_uv_extras.py` in `serve.sh` so developers see whitelist warnings and detector crashes; `|| true` keeps `set -e` from killing startup on detector failure (`scripts/serve.sh`, `git:94da8f67`)
- `serve.sh` force-kills survivors on all three service ports after graceful shutdown as a safety net; this is intentionally aggressive because a lingering process on any port blocks the next `make dev` (`scripts/serve.sh`)
- Secret generation in `deploy.sh` uses a fallback chain (python3 → python → openssl) rather than requiring a specific tool, maximizing compatibility across minimal containers and Windows environments (`scripts/deploy.sh`, `git:8cd4710b`)
- The `--no-sync` alternative for `make dev` was rejected because it would drop the self-heal branch and auto-pickup of new pyproject deps; `--no-sync` is only used in the production Docker CMD where it's appropriate (`scripts/serve.sh`, `git:94da8f67`)

## Patterns
- All service lifecycle scripts auto-detect their location via `$(dirname "${BASH_SOURCE[0]}")/..` and `cd` to the repo root before any operations (`scripts/serve.sh`, `scripts/deploy.sh`, `scripts/docker.sh`)
- Environment variables use consistent fallback chains: explicit env var → config file detection → hardcoded default (`scripts/serve.sh`, `scripts/deploy.sh`)
- Python scripts in `scripts/` use `from __future__ import annotations` and are compatible with Python 3.12+ (`scripts/detect_uv_extras.py`, `scripts/check.py`)
- Shell scripts use `set -e` for error handling and `set -u` (or `set -uo pipefail`) for undefined variable detection (`scripts/serve.sh`, `scripts/deploy.sh`, `scripts/setup-sandbox.sh`)
- The Makefile is a thin dispatcher — all substantive logic lives in `scripts/`; Makefile targets just set up the environment and delegate (`Makefile`)

## Conventions
- All scripts must be run from the repo root directory; they validate this by resolving their own path and `cd`-ing there (`scripts/serve.sh`, `scripts/deploy.sh`, `scripts/docker.sh`)
- Shell scripts use `REPO_ROOT` variable set via `$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)` pattern (`scripts/serve.sh`, `scripts/deploy.sh`)
- `_pick_python()` in `serve.sh` tries `python3`, `python`, then `py` — each must pass a `sys.version_info.major >= 3` check; this handles Windows/Git Bash where `python3` may resolve to a non-executable Microsoft Store alias (`scripts/serve.sh`, `git:18bbb82f`)
- Color output uses ANSI escape codes with `-e` flag on echo: `GREEN='\033[0;32m'`, `BLUE='\033[0;34m'`, `YELLOW='\033[1;33m'`, `RED='\033[0;31m'`, `NC='\033[0m'` (`scripts/deploy.sh`, `scripts/docker.sh`)
- `docker.sh` loads proxy environment variables from `.env` before starting containers so `NO_PROXY` interpolation can merge user-provided values (`scripts/docker.sh`, `git:f92a26d5`)

## Dependencies
- `bash` is required for `serve.sh`, `deploy.sh`, `docker.sh`, `setup-sandbox.sh`, `wait-for-port.sh` (`scripts/`)
- `python3` (or `python`) is required for `detect_uv_extras.py`, `check.py`, `setup_wizard.py`, `configure.py`, `doctor.py`, `sync_labels.py` (`scripts/`)
- `lsof` is used by `serve.sh` for port and process detection; falls back to `ss` and `netstat` in `wait-for-port.sh` (`scripts/serve.sh`, `scripts/wait-for-port.sh`)
- `nginx` is required on the host for local development mode (`scripts/check.py`, `scripts/serve.sh`)
- `docker` CLI is required for Docker-based deployment modes (`scripts/deploy.sh`, `scripts/docker.sh`)
- `uv` is required for backend dependency management (`scripts/serve.sh`, `scripts/check.py`)
- `pnpm` is required for frontend dependency management (`scripts/serve.sh`, `scripts/check.py`)

## Service Lifecycle
- `make dev` flow: check dependencies → stop existing services → config-upgrade → resolve uv extras → `uv sync` + `pnpm install` → start Gateway → start Frontend → start Nginx (`scripts/serve.sh`)
- `make up` flow: resolve DEER_FLOW_HOME → seed config.yaml/extensions_config.json if missing → generate BETTER_AUTH_SECRET + DEER_FLOW_INTERNAL_AUTH_TOKEN → detect sandbox mode → docker compose up --build (`scripts/deploy.sh`)
- `make stop` flow: kill uvicorn/next processes by pattern → graceful nginx quit → force-kill nginx by PID file → force-kill survivors on ports 8001/3000/2026 → cleanup sandbox containers (`scripts/serve.sh`)
- Worktree-aware stopping: `serve.sh` resolves all git worktree roots, checks if a PID's open files live under any worktree, and reports ports reclaimed from sibling worktrees (`scripts/serve.sh`, `git:cd5bedaa`)
- Daemon mode: wraps each service in `nohup sh -c "..." > /dev/null 2>&1 &`, waits for port readiness, then detaches the trap and exits (`scripts/serve.sh`)

## Configuration Management
- `make setup` runs the interactive wizard which guides through LLM provider selection, model choice, and optional search/execution config (`scripts/setup_wizard.py`)
- `make config` copies `config.example.yaml` to `config.yaml` if it doesn't exist (aborts if already present) (`scripts/configure.py`)
- `make config-upgrade` merges new fields from `config.example.yaml` into existing `config.yaml` without overwriting user values (`scripts/config-upgrade.sh`)
- `make doctor` verifies config file validity, checks API key availability, and validates system requirements (`scripts/doctor.py`)
- The wizard's `providers.py` includes per-model `supports_vision` overrides (e.g., MiniMax M3 supports vision but M2.7 is text-only) (`scripts/wizard/providers.py`, `git:cd5bedaa`)
