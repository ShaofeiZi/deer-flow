---
name: knowledge-backend-core-runtime-engine-run-management
description: >
  Covers run management: RunManager with RunRecord lifecycle, background agent worker,
  multitask strategies (reject/interrupt/rollback), run cancellation, SQLite retry
  logic, orphaned run reconciliation, and shutdown drain. Navigate when: debugging
  run lifecycle issues, modifying run creation flow, implementing new multitask
  strategies, or troubleshooting run cancellation.
  Excludes: streaming (see ../streaming/), state persistence (see ../state-persistence/).
  Keywords: RunManager, RunRecord, RunStatus, DisconnectMode, worker, background task,
  asyncio.Task, abort_event, multitask_strategy, create_or_reject, ConflictError,
  orphaned runs, shutdown drain, SQLite retry, PersistenceRetryPolicy.
---

## Module Structure

Run management handles the full lifecycle of agent runs: creation, execution in background
tasks, status tracking, cancellation, and cleanup. It supports multiple multitask strategies
for handling concurrent runs on the same thread.

### Directory Layout
- `backend/packages/harness/deerflow/runtime/runs/manager.py` — RunManager with RunRecord, SQLite retry, persistence, shutdown
- `backend/packages/harness/deerflow/runtime/runs/worker.py` — Background agent execution via asyncio.Task
- `backend/packages/harness/deerflow/runtime/runs/schemas.py` — RunStatus, DisconnectMode enums
- `backend/packages/harness/deerflow/runtime/runs/naming.py` — Run naming utilities
- `backend/packages/harness/deerflow/runtime/runs/store/` — RunStore abstraction (base, memory)

### Key Entry Points
- `RunManager` in `backend/packages/harness/deerflow/runtime/runs/manager.py` — Central run lifecycle manager
- `RunRecord` in `backend/packages/harness/deerflow/runtime/runs/manager.py` — Mutable run state container
- `RunStatus` enum in `backend/packages/harness/deerflow/runtime/runs/schemas.py` — Run status values
- `worker` in `backend/packages/harness/deerflow/runtime/runs/worker.py` — Background execution entry point

## Gotchas
- `create_or_reject()` holds the asyncio lock across both check and insert to eliminate TOCTOU race — separate `has_inflight()` + `create()` calls are not safe (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- SQLite persistence failures are retried with bounded backoff (max 5 attempts, 50ms → 1s) — transient lock contention is handled, but permanent failures propagate (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- On shutdown, RunManager drains in-flight runs with a timeout — runs that don't settle within the timeout may race checkpointer teardown and cause `PoolClosed` errors (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Cancelled runs use `abort_event` + `task.cancel()` — the worker must check `abort_event.is_set()` to cooperatively stop (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Orphaned inflight runs (persisted rows without local workers after restart) are reconciled to `error` status on startup (`backend/packages/harness/deerflow/runtime/runs/manager.py`)

## Architecture
- Run lifecycle: `create()` → `set_status(running)` → worker executes agent in background → `set_status(success/failed/error)` → `cleanup()` after configurable delay (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Multitask strategies: `reject` (refuse if inflight exists), `interrupt` (cancel inflight, start new), `rollback` (cancel and revert checkpoint) (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Run persistence: in-memory dict is primary, optional RunStore provides durability across restarts (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Worker creates a LangGraph runtime context, sets up stream modes, and executes the agent graph in an asyncio.Task (`backend/packages/harness/deerflow/runtime/runs/worker.py`)

## Decisions
- `create_or_reject()` was introduced to atomically check for inflight runs and create new ones, eliminating the TOCTOU race in the previous two-step approach (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Bounded retry for SQLite persistence was added because SQLite lock contention is transient under normal load — permanent failures should still propagate (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Shutdown drain was implemented to let in-flight runs flush their final checkpoints before the checkpointer is closed, preventing `PoolClosed` errors (`backend/packages/harness/deerflow/runtime/runs/manager.py`)

## Patterns
- RunRecord uses `asyncio.Task` for background execution and `asyncio.Event` for cancellation signaling (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Status transitions are persisted to the backing store with best-effort semantics — failures are logged but don't block the run (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Store hydration: when a run is not in memory, the manager falls back to the persistent store, with a re-check for concurrent in-memory insertion (`backend/packages/harness/deerflow/runtime/runs/manager.py`)

## Conventions
- RunStatus enum: pending, running, success, failed, error, interrupted, cancelled, timed_out (`backend/packages/harness/deerflow/runtime/runs/schemas.py`)
- DisconnectMode enum: cancel, interrupt, rollback (`backend/packages/harness/deerflow/runtime/runs/schemas.py`)
- Run IDs are UUID4 strings (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- Timestamps use ISO 8601 format via `now_iso()` utility (`backend/packages/harness/deerflow/runtime/runs/manager.py`)

## Dependencies
- asyncio for Task management and Lock synchronization (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- SQLite/SQLAlchemy for persistent run storage (`backend/packages/harness/deerflow/runtime/runs/manager.py`)
- LangGraph for agent graph execution in worker (`backend/packages/harness/deerflow/runtime/runs/worker.py`)
