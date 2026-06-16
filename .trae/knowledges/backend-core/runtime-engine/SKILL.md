---
name: knowledge-backend-core-runtime-engine
description: >
  Covers the runtime engine: RunManager with RunRecord lifecycle, background agent worker,
  StreamBridge for SSE streaming, checkpointer and store providers, event store, user
  context resolution, and serialization. Navigate when: debugging run lifecycle, modifying
  streaming behavior, adding persistence backends, troubleshooting checkpoint issues, or
  working on run cancellation.
  Excludes: agent orchestration (see ../agent-orchestration/), configuration (see ../configuration/).
  Keywords: RunManager, RunRecord, RunStatus, StreamBridge, StreamEvent, checkpointer,
  store, InMemoryStore, SqliteSaver, PostgresSaver, RunEventStore, user_context,
  ContextVar, serialization, SSE, heartbeat, worker, background task.
---

## Module Structure

The runtime engine manages the execution lifecycle of agent runs: creating runs, executing
agents in background tasks, streaming events to clients via SSE, persisting checkpoints and
state, and recording events for audit trails.

### Directory Layout
- `backend/packages/harness/deerflow/runtime/__init__.py` — Re-exports checkpointer, runs, serialization, store, stream_bridge
- `backend/packages/harness/deerflow/runtime/runs/manager.py` — RunManager with RunRecord, SQLite retry, persistence
- `backend/packages/harness/deerflow/runtime/runs/worker.py` — Background agent execution via asyncio.Task
- `backend/packages/harness/deerflow/runtime/runs/schemas.py` — RunStatus, DisconnectMode enums
- `backend/packages/harness/deerflow/runtime/runs/naming.py` — Run naming utilities
- `backend/packages/harness/deerflow/runtime/runs/store/` — RunStore abstraction (base, memory)
- `backend/packages/harness/deerflow/runtime/stream_bridge/` — StreamBridge ABC, memory implementation, async provider
- `backend/packages/harness/deerflow/runtime/checkpointer/` — Checkpointer factory (memory/sqlite/postgres)
- `backend/packages/harness/deerflow/runtime/store/` — Store factory (memory/sqlite/postgres)
- `backend/packages/harness/deerflow/runtime/events/` — RunEventStore (memory, DB, JSONL backends)
- `backend/packages/harness/deerflow/runtime/user_context.py` — ContextVar-based user context resolution
- `backend/packages/harness/deerflow/runtime/serialization.py` — Message serialization utilities
- `backend/packages/harness/deerflow/runtime/converters.py` — Data conversion utilities
- `backend/packages/harness/deerflow/runtime/journal.py` — Run journal for audit logging

### Key Entry Points
- `RunManager` in `backend/packages/harness/deerflow/runtime/runs/manager.py` — Central run lifecycle manager
- `StreamBridge` ABC in `backend/packages/harness/deerflow/runtime/stream_bridge/base.py` — Streaming abstraction
- `create_checkpointer()` in `backend/packages/harness/deerflow/runtime/checkpointer/provider.py` — Checkpointer factory
- `create_store()` in `backend/packages/harness/deerflow/runtime/store/provider.py` — Store factory
- `resolve_runtime_user_id()` in `backend/packages/harness/deerflow/runtime/user_context.py` — User ID resolution

## Gotchas
- RunManager uses bounded retry for SQLite persistence failures — transient lock contention is retried, but permanent failures propagate (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- On gateway shutdown, RunManager drains in-flight runs before the checkpointer is closed — failing to drain can cause `psycopg_pool.PoolClosed` errors from langgraph-internal tasks (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- StreamBridge uses sentinel events: `HEARTBEAT_SENTINEL` for keepalive (every 15s) and `END_SENTINEL` to signal stream completion (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- User context resolution uses a 3-tier fallback: `runtime.context` → `ContextVar` → `DEFAULT_USER_ID` — if none is set, the default user ID is used silently (`backend/packages/harness/deerflow/runtime/user_context.py`)
- Checkpointer and store factories use singleton pattern with `reset_*()` functions — calling `reset` while runs are in-flight can cause data loss (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`, `backend/packages/harness/deerflow/runtime/store/provider.py`)

## Architecture
- Run lifecycle: `create()` → `set_status(running)` → worker executes agent → `set_status(success/failed/error)` → `cleanup()` after delay (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Multitask strategies: `reject` (refuse new run if inflight), `interrupt` (cancel inflight and start new), `rollback` (cancel and revert checkpoint) (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- StreamBridge decouples agent workers (producers) from SSE endpoints (consumers) with pub/sub pattern (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- Checkpointer and store share the same backend selection logic (memory/sqlite/postgres) with independent singleton instances (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`, `backend/packages/harness/deerflow/runtime/store/provider.py`)

## Decisions
- RunManager uses `create_or_reject()` for atomic check-and-create to eliminate TOCTOU race in separate `has_inflight` + `create` calls (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Orphaned inflight runs are reconciled on startup — persisted `pending`/`running` rows without a local worker are marked as `error` (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Model name is propagated through the runtime and persisted in run records for traceability (`backend/packages/harness/deerflow/runtime/runs/manager.py`, `git:de253e4a`)
- InMemoryStore is used as fallback when the configured store backend is unavailable, with a warning logged (`backend/packages/harness/deerflow/runtime/store/provider.py`)

## Patterns
- RunRecord is a mutable dataclass with asyncio.Task and asyncio.Event for background execution and cancellation (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- StreamBridge uses async generator pattern: `subscribe()` returns `AsyncIterator[StreamEvent]` for SSE consumption (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)
- Factory functions (`create_checkpointer`, `create_store`) use singleton pattern with explicit `reset_*()` for lifecycle management (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`)

## Conventions
- RunStatus enum: pending, running, success, failed, error, interrupted, cancelled, timed_out (`backend/packages/harness/deerflow/runtime/runs/schemas.py`)
- DisconnectMode enum: cancel, interrupt, rollback (`backend/packages/harness/deerflow/runtime/runs/schemas.py`)
- StreamEvent uses SSE-compatible fields: id (monotonically increasing), event (event name), data (JSON payload) (`backend/packages/harness/deerflow/runtime/stream_bridge/base.py`)

## Dependencies
- LangGraph for checkpointer and store abstractions (`backend/packages/harness/deerflow/runtime/checkpointer/`, `backend/packages/harness/deerflow/runtime/store/`)
- SQLite and PostgreSQL for persistent backends (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`)
- `deerflow.config.app_config` for backend selection and configuration (`backend/packages/harness/deerflow/runtime/`)

## Child Knowledge Nodes
- `./run-management/SKILL.md` — RunManager, RunRecord, worker, multitask strategies, cancellation
- `./streaming/SKILL.md` — StreamBridge, SSE events, heartbeat, pub/sub pattern
- `./state-persistence/SKILL.md` — Checkpointer, store, event store, serialization
