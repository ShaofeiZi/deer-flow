---
name: knowledge-backend-core-sandbox-execution-docker-sandbox
description: >
  Covers AioSandbox (Docker-based sandbox): agent_sandbox SDK integration, threading.Lock
  for command serialization, ErrorObservation retry, file download with path traversal
  protection, and AioSandboxProvider with pluggable backends (local container vs remote/K8s).
  Navigate when: debugging Docker sandbox issues, adding backend types, configuring sandbox
  timeouts, or troubleshooting command serialization.
  Excludes: local sandbox (see ../local-sandbox/), sandbox tools (see ../sandbox-tools/).
  Keywords: AioSandbox, AioSandboxProvider, agent_sandbox, Docker sandbox, threading.Lock,
  ErrorObservation, pluggable backends, local_backend, remote_backend, K8s, idle_timeout,
  path_traversal, command_serialization.
---

## Module Structure

AioSandbox provides a Docker-based isolated execution environment using the `agent_sandbox`
SDK. It supports pluggable backends (local container, remote/K8s), command serialization
via threading.Lock, and automatic retry on transient errors.

### Directory Layout
- `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py` — AioSandbox implementation with command execution, file ops
- `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py` — AioSandboxProvider with pluggable backends, idle timeout
- `backend/packages/harness/deerflow/community/aio_sandbox/backend.py` — Backend abstraction for sandbox infrastructure
- `backend/packages/harness/deerflow/community/aio_sandbox/local_backend.py` — Local Docker container backend
- `backend/packages/harness/deerflow/community/aio_sandbox/remote_backend.py` — Remote/K8s backend
- `backend/packages/harness/deerflow/community/aio_sandbox/sandbox_info.py` — Sandbox metadata and info types

### Key Entry Points
- `AioSandbox` in `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py` — Docker-based sandbox
- `AioSandboxProvider` in `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py` — Provider with backend selection
- Backend classes in `backend/packages/harness/deerflow/community/aio_sandbox/backend.py` — Pluggable infrastructure

## Gotchas
- AioSandbox uses `threading.Lock` for command serialization — concurrent commands on the same sandbox instance are serialized, not truly parallel (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)
- ErrorObservation responses from the SDK are automatically retried — the sandbox treats them as transient failures rather than permanent errors (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)
- File download includes path traversal protection — attempts to access paths outside the sandbox root are blocked (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)
- AioSandboxProvider supports an idle timeout — sandboxes that are idle beyond the configured timeout are automatically cleaned up (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`)
- Signal handling is managed by the provider to ensure clean sandbox shutdown on process termination (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`)

## Architecture
- Pluggable backend architecture: `local_backend` for Docker containers on the same host, `remote_backend` for K8s or remote container orchestration (`backend/packages/harness/deerflow/community/aio_sandbox/backend.py`)
- Command execution flow: acquire lock → send command to SDK → await response → check for ErrorObservation → retry if needed → release lock (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)
- Provider lifecycle: `acquire()` creates a sandbox via the configured backend, `release()` returns it to the pool or destroys it, `reset()` recreates from scratch (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`)
- Thread-lock executor pattern: the provider uses a thread-lock executor to manage concurrent sandbox operations safely (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`)

## Decisions
- `threading.Lock` was chosen over asyncio.Lock for command serialization because the agent_sandbox SDK may use synchronous internals (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)
- Pluggable backends were introduced to support both local development (Docker) and production (K8s) without code changes (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`)
- ErrorObservation retry was added because the SDK can return transient errors during container startup or network flaps (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)

## Patterns
- Command execution: `with self._lock: result = await self._sandbox.execute(...)` — all commands go through the lock (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)
- Error handling: check `isinstance(result, ErrorObservation)` and retry with configurable max attempts (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)
- Backend selection: provider reads config to determine which backend class to instantiate (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`)

## Conventions
- Sandbox operations return structured results with stdout, stderr, and exit_code (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)
- Backend classes implement a common interface defined in `backend.py` (`backend/packages/harness/deerflow/community/aio_sandbox/backend.py`)
- Idle timeout is configured in seconds; 0 or negative means no timeout (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`)

## Dependencies
- `agent_sandbox` SDK — the core Docker sandbox execution library (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)
- `deerflow.sandbox.sandbox.Sandbox` — abstract base class that AioSandbox implements (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)
- `deerflow.sandbox.sandbox_provider.SandboxProvider` — abstract base class for the provider (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`)
