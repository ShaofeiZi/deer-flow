---
name: knowledge-backend-gateway-rest-api
description: >
  Covers the REST API routing layer: thread CRUD, run lifecycle, agents, models, MCP, memory,
  skills, artifacts, uploads, suggestions, feedback, channels, and assistants compatibility.
  Navigate when: adding new API endpoints, modifying request/response schemas, debugging HTTP
  status codes, changing SSE stream format, adding pagination, implementing new resource types.
  Excludes: authentication middleware (see ../authentication/), channel dispatch logic (see ../channel-integrations/).
  Keywords: routers, threads, runs, agents, models, MCP, memory, skills, artifacts, uploads,
  suggestions, feedback, channels, assistants, SSE, pagination, thread_runs, ThreadMetaStore.
---

## Module Structure

The REST API layer provides the HTTP interface for all DeerFlow functionality. Routers are thin
handlers that delegate business logic to `services.py` and dependency injection via `deps.py`.
The API follows LangGraph Platform compatibility where applicable while adding DeerFlow-specific
endpoints for models, MCP, memory, skills, and artifacts.

### Directory Layout
- `backend/app/gateway/routers/__init__.py` — Router module exports
- `backend/app/gateway/routers/threads.py` — Thread CRUD, state, history, search, delete
- `backend/app/gateway/routers/thread_runs.py` — LangGraph-compatible runs lifecycle (create, stream, wait, cancel, list)
- `backend/app/gateway/routers/runs.py` — Stateless runs (stream/wait without pre-existing thread)
- `backend/app/gateway/routers/agents.py` — Custom agent CRUD with per-agent skills config
- `backend/app/gateway/routers/models.py` — AI model listing and configuration
- `backend/app/gateway/routers/mcp.py` — MCP server configuration management
- `backend/app/gateway/routers/memory.py` — Global memory data access
- `backend/app/gateway/routers/skills.py` — Skills listing and enabled-status management
- `backend/app/gateway/routers/artifacts.py` — Thread artifact access and download
- `backend/app/gateway/routers/uploads.py` — User file uploads for threads
- `backend/app/gateway/routers/suggestions.py` — Follow-up question suggestions
- `backend/app/gateway/routers/feedback.py` — User feedback (thumbs-up/down) for runs
- `backend/app/gateway/routers/channels.py` — IM channel status and restart endpoints
- `backend/app/gateway/routers/assistants_compat.py` — LangGraph Platform assistants API stub
- `backend/app/gateway/routers/auth.py` — Authentication endpoints (login, register, setup, password change)

### Key Entry Points
- Thread creation: `POST /api/threads` in `backend/app/gateway/routers/threads.py`
- Run creation: `POST /api/threads/{thread_id}/runs` in `backend/app/gateway/routers/thread_runs.py`
- Run streaming: `GET /api/threads/{thread_id}/runs/stream` in `backend/app/gateway/routers/thread_runs.py`
- Agent CRUD: `POST/GET/PATCH/DELETE /api/agents` in `backend/app/gateway/routers/agents.py`

## Gotchas
- Thread search (`POST /api/threads/search`) reads from `ThreadMetaStore` (SQL or memory-backed), not the LangGraph Store directly — threads created before `thread_meta` adoption may not appear until a run syncs them (`backend/app/gateway/routers/threads.py`, `git:d8ecaf46`)
- Deleting a thread must also remove the `threads_meta` row in SQLite mode, otherwise deleted threads keep appearing in `/threads/search` — the endpoint now routes through `ThreadMetaStore.delete()` for both backends (`backend/app/gateway/routers/threads.py`, `git:d8ecaf46`)
- Renaming a thread via `POST /threads/{id}/state` must sync through `ThreadMetaStore.update_display_name()`, not just the LangGraph Store — otherwise renames only appear in search after the next agent run completes (`backend/app/gateway/routers/threads.py`, `git:d8ecaf46`)
- `AgentUpdateRequest` uses `model_fields_set` to distinguish "field omitted" from "explicitly set to null" — critical for `skills` where `None` means "inherit all" not "don't change" (`backend/app/gateway/routers/agents.py`, `git:30d619de`)
- The `/history` endpoint reads messages from the checkpointer's `channel_values` (authoritative source), not from `RunEventStore` — switching data sources silently changes which messages appear (`backend/app/gateway/routers/threads.py`, `git:d8ecaf46`)
- `normalize_input()` delegates dict→message coercion to `langchain_core.messages.utils.convert_to_messages` — a hand-rolled version previously only forwarded `content` and collapsed every role to `HumanMessage`, silently stripping frontend-supplied attachments (`backend/app/gateway/services.py`, `git:3132`)
- Stateless run endpoints carry `thread_id` in the request body, so `@require_permission(owner_check=True)` cannot protect them from the path param — ownership is enforced inside `start_run()` before any run is created (`backend/app/gateway/services.py`)

## Architecture
- Router prefix convention: models/mcp/memory/skills/agents/channels at `/api/<resource>`, threads at `/api/threads`, runs at `/api/threads/{thread_id}/runs`, auth at `/api/v1/auth` (`backend/app/gateway/app.py`)
- `_SERVER_RESERVED_METADATA_KEYS` strips `owner_id` and `user_id` from client-supplied metadata on every inbound model — defense-in-depth against metadata-blob echo gap (`backend/app/gateway/routers/threads.py`)
- Thread metadata access is fully routed through `ThreadMetaStore` abstraction — no direct LangGraph Store reads/writes remain in the threads router, ensuring sqlite and memory backends behave identically (`backend/app/gateway/routers/threads.py`, `git:d8ecaf46`)
- `merge_run_context_overrides()` writes whitelisted keys into both `configurable` and `context` so they're visible to legacy configurable readers AND LangGraph `ToolRuntime.context` consumers (`backend/app/gateway/services.py`)

## Decisions
- Chose `ThreadMetaStore` abstraction over direct LangGraph Store access for all thread metadata operations — enables uniform sqlite/memory backend behavior and eliminates dual-write paths (`backend/app/gateway/routers/threads.py`, `git:d8ecaf46`)
- `user_id` is intentionally propagated into `config['context']` in addition to whitelisted keys, so non-web callers (IM channels) that supply identity in `body.context` keep it on `ToolRuntime.context` (`backend/app/gateway/services.py`)

## Patterns
- All router endpoints that need thread ownership verification use `@require_permission("threads", "read", owner_check=True)` decorator pattern (`backend/app/gateway/routers/threads.py`)
- Destructive/mutating routes (DELETE, PATCH, state-update) use `require_existing=True` so a deleted thread can't be re-targeted via the missing-row code path (`backend/app/gateway/authz.py`)
- Feedback endpoints validate run existence and thread membership before accepting feedback submissions (`backend/app/gateway/routers/feedback.py`)

## Conventions
- Pydantic models for request/response are defined inline in each router module, not in a separate schemas package (`backend/app/gateway/routers/`)
- `Field(description=...)` is used on all response model fields for OpenAPI documentation (`backend/app/gateway/routers/threads.py`)
- `sanitize_log_param()` is called on all user-supplied identifiers before logging to prevent log injection (`backend/app/gateway/routers/threads.py`)

## Dependencies
- `langgraph-sdk` SSE decoder expects the wire format produced by `format_sse()`: `event:` → `data:` → `id:` (optional) → blank line (`backend/app/gateway/services.py`)
- `langchain_core.messages.utils.convert_to_messages` is the authoritative dict→message converter — bypassing it strips `additional_kwargs` (`backend/app/gateway/services.py`)

## Performance Characteristics
- Thread search with SQL backend uses `ThreadMetaRepository.search()` with metadata/status filters and pagination, replacing the old two-phase Store + Checkpointer scan approach (`backend/app/gateway/routers/threads.py`, `git:d8ecaf46`)
- Feedback stats use SQL aggregation (`SELECT COUNT/SUM`) instead of Python-side counting, eliminating the `limit=10000` truncation risk (`backend/app/gateway/routers/feedback.py`, `git:d8ecaf46`)
