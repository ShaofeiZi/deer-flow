---
name: knowledge-backend-core-sandbox-execution-local-sandbox
description: >
  Covers LocalSandbox: filesystem-based sandbox with PathMapping, container-to-local
  path resolution, shell detection, read-only mount enforcement, and the dual-track
  cache in LocalSandboxProvider. Navigate when: debugging path resolution issues,
  modifying local sandbox behavior, understanding path mapping, or troubleshooting
  sandbox acquisition failures.
  Excludes: Docker sandbox (see ../docker-sandbox/), sandbox tools (see ../sandbox-tools/).
  Keywords: LocalSandbox, LocalSandboxProvider, PathMapping, container_path, local_path,
  reverse_resolution, shell_detection, read_only_mounts, dual_track_cache, per_thread_lru,
  VIRTUAL_PATH_PREFIX, sandbox acquisition.
---

## Module Structure

LocalSandbox provides a filesystem-based execution environment that maps container-style
paths to local filesystem paths. It supports shell detection across zsh/bash/sh/powershell/cmd
and enforces read-only mounts for safety. The provider uses a dual-track caching strategy
to prevent cross-thread sandbox contamination.

### Directory Layout
- `backend/packages/harness/deerflow/sandbox/local/local_sandbox.py` — LocalSandbox with PathMapping, shell detection, command execution
- `backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py` — LocalSandboxProvider with dual-track cache, thread-safe acquire/get/reset
- `backend/packages/harness/deerflow/sandbox/sandbox.py` — Abstract Sandbox ABC that LocalSandbox implements
- `backend/packages/harness/deerflow/sandbox/sandbox_provider.py` — Abstract SandboxProvider ABC that LocalSandboxProvider implements

### Key Entry Points
- `LocalSandbox` in `backend/packages/harness/deerflow/sandbox/local/local_sandbox.py` — Concrete sandbox implementation
- `LocalSandboxProvider` in `backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py` — Provider with caching
- `PathMapping` in `backend/packages/harness/deerflow/sandbox/local/local_sandbox.py` — Container-to-local path translation

## Gotchas
- LocalSandboxProvider uses a dual-track cache: a generic singleton for backward compatibility AND a per-thread LRU (cap 256) — the per-thread cache is the primary path; the singleton is a fallback (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`, `git:380255f7`)
- PathMapping must handle both forward (container → local) and reverse (local → container) resolution — output from commands needs reverse mapping to show container paths (`backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`)
- Shell detection probes for zsh, bash, sh, powershell, and cmd in order — the first available shell is used for command execution (`backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`)
- Read-only mounts are enforced at the sandbox level — attempting to write to read-only paths raises an error (`backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`)
- The per-thread LRU cache has a cap of 256 — exceeding this causes older sandbox entries to be evicted (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`)

## Architecture
- PathMapping is the core abstraction: it translates between container paths (`/mnt/user-data/...`) and local filesystem paths, with support for multiple mount points (`backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`)
- Dual-track caching: `_generic_sandbox` (singleton) for backward compatibility + `_per_thread_sandboxes` (LRU dict, cap 256) for thread isolation (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`)
- Provider lifecycle: `acquire()` creates or reuses a sandbox, `get()` returns existing without creation, `release()` cleans up, `reset()` destroys and recreates (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`)
- Path mapping configuration comes from `app_config.sandbox` at provider initialization time (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`)

## Decisions
- Per-thread sandbox instances were introduced to prevent cross-thread contamination when multiple concurrent requests share a process (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`, `git:380255f7`)
- Shell detection is done once at sandbox creation and cached — the shell is not re-detected on each command (`backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`)
- PathMapping is set up from config at provider init and passed to each sandbox instance (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`)

## Patterns
- Path resolution: `_resolve_container_to_local(path)` for input paths, `_resolve_local_to_container(output)` for command output (`backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`)
- Thread-safe acquire: uses `threading.Lock` to protect cache access during sandbox creation and retrieval (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`)
- Sandbox reset: `reset()` calls `release()` followed by `acquire()` to provide a fresh sandbox instance (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`)

## Conventions
- Container paths use `VIRTUAL_PATH_PREFIX = "/mnt/user-data"` as the root (`backend/packages/harness/deerflow/config/paths.py`)
- Sandbox instances are identified by `thread_id` in the provider cache (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`)
- Command execution returns stdout, stderr, and exit_code as a tuple (`backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`)

## Dependencies
- `deerflow.config.paths` for VIRTUAL_PATH_PREFIX and directory layout (`backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`)
- `deerflow.config.app_config` for sandbox path mapping configuration (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`)
