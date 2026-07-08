---
name: knowledge-backend-core-runtime-engine-state-persistence
description: >
  Covers state persistence: checkpointer factory (memory/sqlite/postgres backends),
  store factory with InMemoryStore fallback, RunEventStore (memory, DB, JSONL backends),
  serialization utilities, and user context resolution. Navigate when: adding persistence
  backends, debugging checkpoint issues, configuring store backends, or working on
  event recording.
  Excludes: run management (see ../run-management/), streaming (see ../streaming/).
  Keywords: checkpointer, store, InMemoryStore, SqliteSaver, PostgresSaver,
  MemorySaver, RunEventStore, MemoryRunEventStore, serialization, user_context,
  ContextVar, resolve_runtime_user_id, DEFAULT_USER_ID, AUTO sentinel,
  singleton pattern, reset_checkpointer, reset_store.
---

## Module Structure

State persistence provides durable storage for agent checkpoints, key-value store, and
run events. It supports multiple backends (memory, SQLite, PostgreSQL) with a unified
factory pattern and singleton lifecycle management.

### Directory Layout
- `backend/packages/harness/deerflow/runtime/checkpointer/__init__.py` — Public API exports
- `backend/packages/harness/deerflow/runtime/checkpointer/provider.py` — Sync checkpointer factory (memory/sqlite/postgres)
- `backend/packages/harness/deerflow/runtime/checkpointer/async_provider.py` — Async checkpointer factory
- `backend/packages/harness/deerflow/runtime/store/__init__.py` — Public API exports
- `backend/packages/harness/deerflow/runtime/store/provider.py` — Sync store factory (memory/sqlite/postgres)
- `backend/packages/harness/deerflow/runtime/store/async_provider.py` — Async store factory
- `backend/packages/harness/deerflow/runtime/store/_sqlite_utils.py` — SQLite utility functions
- `backend/packages/harness/deerflow/runtime/events/__init__.py` — Public API: MemoryRunEventStore, RunEventStore
- `backend/packages/harness/deerflow/runtime/events/store/` — Event store backends (base, memory, db, jsonl)
- `backend/packages/harness/deerflow/runtime/serialization.py` — Message serialization utilities
- `backend/packages/harness/deerflow/runtime/user_context.py` — ContextVar-based user context resolution

### Key Entry Points
- `create_checkpointer()` in `backend/packages/harness/deerflow/runtime/checkpointer/provider.py` — Checkpointer factory
- `create_store()` in `backend/packages/harness/deerflow/runtime/store/provider.py` — Store factory
- `MemoryRunEventStore` in `backend/packages/harness/deerflow/runtime/events/__init__.py` — Default event store
- `resolve_runtime_user_id()` in `backend/packages/harness/deerflow/runtime/user_context.py` — User ID resolution

## Gotchas
- Checkpointer and store factories use singleton pattern — calling `reset_checkpointer()` or `reset_store()` while runs are in-flight can cause data loss (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`, `backend/packages/harness/deerflow/runtime/store/provider.py`)
- InMemoryStore is used as a silent fallback when the configured store backend is unavailable — only a warning is logged, no error is raised (`backend/packages/harness/deerflow/runtime/store/provider.py`)
- User context resolution uses 3-tier fallback: `runtime.context` → `ContextVar` → `DEFAULT_USER_ID` — if none is set, the default user ID is used silently without error (`backend/packages/harness/deerflow/runtime/user_context.py`)
- `AUTO` sentinel is used for repository methods to indicate the user ID should be resolved from context rather than passed explicitly (`backend/packages/harness/deerflow/runtime/user_context.py`)
- SQLite backend requires the `aiosqlite` or `sqlite3` package depending on sync vs async usage (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`)

## Architecture
- Checkpointer and store share the same backend selection logic (memory/sqlite/postgres) but maintain independent singleton instances (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`, `backend/packages/harness/deerflow/runtime/store/provider.py`)
- Factory functions accept optional `config` parameter — when omitted, they read from `get_app_config()` (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`)
- Event store supports three backends: in-memory (default), SQLite database, and JSONL files (`backend/packages/harness/deerflow/runtime/events/store/`)
- User context uses `contextvars.ContextVar` for request-scoped user ID propagation through async call chains (`backend/packages/harness/deerflow/runtime/user_context.py`)

## Decisions
- Singleton pattern with explicit reset was chosen over dependency injection to simplify the API while still supporting reconfiguration (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`)
- InMemoryStore fallback was chosen over raising an error to ensure the system remains operational even if the configured backend is temporarily unavailable (`backend/packages/harness/deerflow/runtime/store/provider.py`)
- ContextVar was chosen for user context propagation because it works transparently through asyncio task chains without explicit parameter passing (`backend/packages/harness/deerflow/runtime/user_context.py`)

## Patterns
- Factory functions: `create_checkpointer(config=None)` returns a singleton, `reset_checkpointer()` destroys and allows recreation (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`)
- Backend selection: check config → instantiate appropriate backend class → wrap in LangGraph-compatible interface (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`)
- User context: `resolve_runtime_user_id(runtime, default=DEFAULT_USER_ID)` with 3-tier resolution (`backend/packages/harness/deerflow/runtime/user_context.py`)

## Conventions
- Backend names: `memory`, `sqlite`, `postgres` (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`)
- Event store backends: `memory`, `db` (SQLite), `jsonl` (JSON Lines files) (`backend/packages/harness/deerflow/runtime/events/store/`)
- `DEFAULT_USER_ID` is a module-level constant used when no user context is available (`backend/packages/harness/deerflow/runtime/user_context.py`)

## Dependencies
- LangGraph for `BaseCheckpointSaver` and `BaseStore` abstractions (`backend/packages/harness/deerflow/runtime/checkpointer/`, `backend/packages/harness/deerflow/runtime/store/`)
- `langgraph.checkpoint.memory.MemorySaver` for in-memory checkpointer (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`)
- `langgraph.checkpoint.sqlite.SqliteSaver` and `langgraph.checkpoint.postgres.PostgresSaver` for persistent backends (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`)
- `contextvars` for user context propagation (`backend/packages/harness/deerflow/runtime/user_context.py`)
