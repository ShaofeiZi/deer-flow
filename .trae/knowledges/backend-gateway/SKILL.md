---
name: knowledge-backend-gateway
description: >
  Covers the FastAPI API Gateway: lifespan bootstrap, middleware chain, dependency injection,
  run lifecycle services, CSRF protection, auth-disabled mode, and LangGraph auth compatibility.
  Navigate when: modifying gateway startup/shutdown, adding middleware, debugging 503/504 errors,
  changing dependency injection, troubleshooting worker hangs, understanding config hot-reload boundaries.
  Excludes: REST API routing (see rest-api/), authentication/authorization (see authentication/),
  IM channel integrations (see channel-integrations/).
  Keywords: gateway, FastAPI, lifespan, middleware, deps, langgraph_runtime, StreamBridge, RunManager,
  RunContext, SSE, CSRF, auth_disabled, tiktoken, uvicorn, shutdown, config hot-reload.
---

## Module Structure

The API Gateway is the central FastAPI application that orchestrates all DeerFlow backend services.
It manages the full application lifecycle: config loading, persistence engine initialization,
middleware chain setup, router registration, channel service start/stop, and graceful shutdown.

### Directory Layout
- `backend/app/gateway/app.py` — FastAPI app creation, lifespan handler, middleware registration, router mounting
- `backend/app/gateway/config.py` — GatewayConfig (host, port, enable_docs) from env vars
- `backend/app/gateway/deps.py` — Singleton accessors (StreamBridge, RunManager, checkpointer, stores) and langgraph_runtime() context manager
- `backend/app/gateway/services.py` — Run lifecycle service layer: SSE formatting, input normalization, config building, start_run, sse_consumer
- `backend/app/gateway/csrf_middleware.py` — Double Submit Cookie CSRF protection for state-changing requests
- `backend/app/gateway/auth_disabled.py` — E2E/local auth-disabled mode helpers
- `backend/app/gateway/langgraph_auth.py` — LangGraph Server compatibility auth handler reusing Gateway JWT/CSRF logic
- `backend/app/gateway/internal_auth.py` — Internal auth token for trusted gateway-to-gateway calls (channel manager)
- `backend/app/gateway/pagination.py` — Pagination utilities
- `backend/app/gateway/path_utils.py` — Path resolution helpers
- `backend/app/gateway/utils.py` — Shared utilities including log injection sanitizer

### Key Entry Points
- `create_app()` in `backend/app/gateway/app.py` — FastAPI app factory
- `lifespan()` in `backend/app/gateway/app.py` — Application lifecycle (startup/shutdown)
- `langgraph_runtime()` in `backend/app/gateway/deps.py` — Bootstrap/teardown of all runtime singletons
- `start_run()` in `backend/app/gateway/services.py` — Main run creation and agent launch

## Gotchas
- Gateway worker can hang indefinitely in `uvicorn --reload` mode when a channel's `stop()` stalls (e.g. Feishu WebSocket waiting for ack); the lifespan now wraps shutdown hooks in `asyncio.wait_for(timeout=5.0)` as defense-in-depth (`backend/app/gateway/app.py`, `git:4e724101`)
- Config hot-reload boundary: `AppConfig` is NOT cached on `app.state` — routers resolve it live via `get_app_config()` which does mtime-based reload. But engines created in `langgraph_runtime()` (stream bridge, persistence, checkpointer, store) are restart-required and stay bound to the startup snapshot (`backend/app/gateway/deps.py`)
- `get_config()` at request time returns 503 on any config materialization failure (missing file, YAML parse error, validation error) — semantically "gateway cannot serve without usable configuration" (`backend/app/gateway/deps.py`)
- In-flight runs must be drained BEFORE the AsyncExitStack tears down the checkpointer connection pool, otherwise a run mid-graph races the closed pool and raises PoolClosed (`backend/app/gateway/deps.py`, `git:3373`)
- tiktoken encoding cache is pre-warmed at startup with a 5-second timeout; when `memory.token_counting='char'`, the warm-up is skipped entirely to avoid network calls in restricted environments (`backend/app/gateway/app.py`, `git:3429`)
- The lifespan uses TWO separate shutdown timeout budgets: `_SHUTDOWN_HOOK_TIMEOUT_SECONDS` (5.0s for channel stop) and `_RUN_DRAIN_TIMEOUT_SECONDS` (5.0s for run drain) — both count toward the server's graceful-shutdown window (`backend/app/gateway/app.py`, `backend/app/gateway/deps.py`)

## Architecture
- Middleware chain order: AuthMiddleware → CSRFMiddleware → CORSMiddleware → routers. Auth rejects unauthenticated requests to non-public paths (fail-closed), CSRF validates state-changing requests, CORS only activates when `GATEWAY_CORS_ORIGINS` is configured (`backend/app/gateway/app.py`)
- Request-time config resolution always routes through `get_app_config()` so `config.yaml` edits become visible without restart; the startup snapshot is only used for one-shot bootstrap (`backend/app/gateway/deps.py`)
- `RunContext` pairs a freshly-loaded `AppConfig` with startup-frozen `run_events_config`/`event_store` to prevent combining a live new config with a store bound to the previous backend (`backend/app/gateway/deps.py`)
- All dependency getters use `_require()` factory pattern — returns `app.state.<attr>` or raises 503, eliminating repetitive boilerplate (`backend/app/gateway/deps.py`)
- `wait_for_run_completion()` consumes the same StreamBridge as `sse_consumer()` so the non-streaming `/wait` path shares disconnect semantics — polls `request.is_disconnected()` and cancels background runs on client disconnect (`backend/app/gateway/services.py`, `git:3265`)

## Decisions
- Chose to NOT cache `AppConfig` on `app.state` — every request resolves config live, closing the split-brain bug where worker/lead-agent thread saw a stale startup snapshot (`backend/app/gateway/deps.py`, `git:3107`)
- `run_events_config` is frozen at startup alongside its `event_store` to prevent backend mismatch at runtime (`backend/app/gateway/deps.py`)
- Admin bootstrap (`_ensure_admin_user`) runs AFTER `langgraph_runtime` so `app.state.store` is available for orphan thread migration (`backend/app/gateway/app.py`)

## Patterns
- All gateway singleton getters follow `_require(attr, label)` factory returning `Callable[[Request], T]` — consistent 503-on-missing behavior (`backend/app/gateway/deps.py`)
- `format_sse()` produces LangGraph Platform wire format: `event:` → `data:` → `id:` (optional) → blank line, consumed by `useStream` React hook and `langgraph-sdk` SSE decoder (`backend/app/gateway/services.py`)
- `normalize_input()` delegates dict→message coercion to `langchain_core.messages.utils.convert_to_messages` so `additional_kwargs` (uploaded-file metadata) survive unchanged (`backend/app/gateway/services.py`)

## Conventions
- Router modules are thin HTTP handlers that delegate business logic to `services.py` (`backend/app/gateway/services.py`)
- `_CONTEXT_CONFIGURABLE_KEYS` whitelist controls which `body.context` keys are forwarded into both `configurable` and `context` for LangGraph compatibility (`backend/app/gateway/services.py`)
- Log parameters are sanitized via `sanitize_log_param()` to prevent log injection (`backend/app/gateway/utils.py`)

## Security Considerations
- `DEER_FLOW_AUTH_DISABLED=1` bypasses all authentication — but is automatically disabled when `DEER_FLOW_ENV=production` or `ENVIRONMENT=production` (`backend/app/gateway/auth_disabled.py`)
- Internal auth uses `X-DeerFlow-Internal-Token` header with `secrets.compare_digest` for timing-safe comparison; auto-generates a token if `DEER_FLOW_INTERNAL_AUTH_TOKEN` is not set (`backend/app/gateway/internal_auth.py`)
- CSRF middleware exempts auth endpoints (login/register/initialize) from double-submit token check but still validates Origin header to prevent login CSRF/session fixation (`backend/app/gateway/csrf_middleware.py`)

## Child Knowledge Nodes
- `./rest-api/SKILL.md` — Navigate when: adding new API endpoints, modifying request/response models, debugging routing issues, changing SSE stream format
- `./authentication/SKILL.md` — Navigate when: modifying login flow, debugging token issues, adding OAuth provider, changing permission model, investigating session expiry
- `./channel-integrations/SKILL.md` — Navigate when: adding a new IM platform, debugging channel message delivery, modifying channel dispatch logic, troubleshooting WebSocket connections
