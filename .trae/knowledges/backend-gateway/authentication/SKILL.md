---
name: knowledge-backend-gateway-authentication
description: >
  Cross-cutting authentication and authorization system: JWT token handling, password hashing,
  user repository, auth middleware, CSRF protection, permission decorators, internal auth,
  auth-disabled mode, and LangGraph auth compatibility.
  Navigate when: modifying login flow, debugging token issues, adding OAuth provider,
  changing permission model, investigating session expiry, adding new protected routes,
  troubleshooting 401/403 errors, understanding owner isolation.
  Keywords: auth, JWT, OAuth, login, session, AuthMiddleware, TokenService, refresh token,
  bcrypt, CSRF, require_auth, require_permission, AuthContext, AuthErrorCode, TokenError,
  UserRepository, LocalAuthProvider, token_version, owner isolation, contextvar.
---

## Module Structure

The authentication system is a cross-cutting concern that spans the entire gateway. It provides
JWT-based session authentication, bcrypt password hashing with versioned hash format, a SQLite-backed
user repository, middleware-level request gating, decorator-based permission checks, CSRF protection,
and repository-layer owner isolation via contextvars.

### Decision Entry
- `AuthMiddleware.dispatch()` in `backend/app/gateway/auth_middleware.py` — Main auth gate: validates JWT cookie, stamps `request.state.user` and contextvar, rejects unauthenticated requests to non-public paths
- `is_auth_disabled()` in `backend/app/gateway/auth_disabled.py` — Returns True when `DEER_FLOW_AUTH_DISABLED=1` AND environment is not production
- `is_valid_internal_auth_token()` in `backend/app/gateway/internal_auth.py` — Validates `X-DeerFlow-Internal-Token` header for trusted internal callers

### Directory Layout
- `backend/app/gateway/auth/__init__.py` — Public auth module API exports
- `backend/app/gateway/auth/config.py` — AuthConfig (JWT secret, token expiry, OAuth credentials)
- `backend/app/gateway/auth/jwt.py` — JWT token creation (HS256) and validation with TokenError enum
- `backend/app/gateway/auth/password.py` — Versioned bcrypt hashing (v2: SHA-256 pre-hash + bcrypt)
- `backend/app/gateway/auth/models.py` — User and UserResponse Pydantic models
- `backend/app/gateway/auth/errors.py` — AuthErrorCode, TokenError, AuthErrorResponse enums
- `backend/app/gateway/auth/providers.py` — AuthProvider abstract base class
- `backend/app/gateway/auth/local_provider.py` — LocalAuthProvider: email/password auth with auto-rehash
- `backend/app/gateway/auth/repositories/base.py` — UserRepository abstract interface
- `backend/app/gateway/auth/repositories/sqlite.py` — SQLAlchemy-backed SQLiteUserRepository
- `backend/app/gateway/auth/credential_file.py` — Secure credential file writer (0600 permissions)
- `backend/app/gateway/auth/reset_admin.py` — CLI tool for admin password reset
- `backend/app/gateway/auth_middleware.py` — Global AuthMiddleware: fail-closed safety net
- `backend/app/gateway/authz.py` — @require_auth and @require_permission decorators
- `backend/app/gateway/csrf_middleware.py` — Double Submit Cookie CSRF protection
- `backend/app/gateway/auth_disabled.py` — E2E/local auth-disabled mode
- `backend/app/gateway/internal_auth.py` — Internal auth token for trusted gateway-to-gateway calls
- `backend/app/gateway/langgraph_auth.py` — LangGraph Server compatibility auth handler

### Key Entry Points
- `AuthMiddleware` class in `backend/app/gateway/auth_middleware.py` — Per-request authentication gate
- `@require_auth` / `@require_permission` in `backend/app/gateway/authz.py` — Route-level auth decorators
- `get_current_user_from_request()` in `backend/app/gateway/deps.py` — JWT→User resolution pipeline
- `create_access_token()` in `backend/app/gateway/auth/jwt.py` — Token creation with token_version

## Branching Table

| Dimension | Authenticated (Session) | Auth-Disabled (E2E/Local) | Internal (Channel) |
|-----------|------------------------|---------------------------|---------------------|
| User identity | Real User from JWT cookie → DB lookup | Synthetic `e2e-user` admin | Synthetic internal user with `DEFAULT_USER_ID` |
| Auth source | `AUTH_SOURCE_SESSION` | `AUTH_SOURCE_AUTH_DISABLED` | `AUTH_SOURCE_INTERNAL` |
| CSRF enforcement | Full double-submit cookie check on state-changing methods | Disabled entirely | Bypassed (internal calls use header token) |
| Owner isolation | Contextvar set from JWT user; all repos filter by owner_id | No filtering (synthetic admin sees all) | Exempt from thread ownership checks in `start_run()` |
| Token validation | Strict: decode → DB lookup → token_version match | Skipped (synthetic user returned) | Uses `X-DeerFlow-Internal-Token` header with `secrets.compare_digest` |
| JWT secret source | `AUTH_JWT_SECRET` env var or auto-generated `.jwt_secret` file | N/A (no tokens issued) | N/A (separate internal token) |
| Production guard | Normal operation | Blocked: `is_auth_disabled()` returns False when `DEER_FLOW_ENV=production` | Always available |

## Affected Scope
- `backend/app/gateway/auth_middleware.py` — Global request gating: stamps user on `request.state` and contextvar for all non-public paths
- `backend/app/gateway/authz.py` — Route-level decorators: `@require_auth` (12+ route usages), `@require_permission` with owner_check
- `backend/app/gateway/deps.py` — User resolution pipeline: `get_current_user_from_request`, `get_optional_user_from_request`, `get_local_provider`
- `backend/app/gateway/routers/auth.py` — Auth endpoints: login, register, logout, setup, password change, me
- `backend/app/gateway/routers/threads.py` — Thread ownership enforcement via `@require_permission(owner_check=True)` on all mutating endpoints
- `backend/app/gateway/routers/thread_runs.py` — Run creation gated by thread ownership
- `backend/app/gateway/routers/runs.py` — Stateless runs enforce thread ownership inside `start_run()`
- `backend/app/gateway/services.py` — `inject_authenticated_user_context()` stamps user_id for background tools; internal role exempt from ownership checks
- `backend/app/gateway/csrf_middleware.py` — CSRF validation on all state-changing requests
- `deerflow/runtime/user_context.py` — ContextVar-based owner isolation consumed by all persistence repositories
- `deerflow/persistence/thread_meta/` — ThreadMetaRepository filters by owner_id via AUTO sentinel
- `deerflow/persistence/run/` — RunRepository filters by owner_id
- `deerflow/persistence/feedback/` — FeedbackRepository filters by owner_id
- `deerflow/runtime/events/store/db.py` — DbRunEventStore stamps owner_id on writes, filters on reads

## Gotchas
- JWT tokens include a `token_version` claim that must match `User.token_version` — changing the user's password increments `token_version`, immediately invalidating all existing tokens for that user (`backend/app/gateway/auth/jwt.py`, `backend/app/gateway/deps.py`)
- The auth middleware calls the STRICT user resolver (`get_current_user_from_request`) so fine-grained error codes (token_expired, token_invalid, user_not_found) propagate — without this, non-isolation routes like `/api/models` would accept any cookie-shaped string as authentication (`backend/app/gateway/auth_middleware.py`)
- `@require_permission` with `owner_check=True` uses `ThreadMetaStore.check_access()` which returns True for missing rows (untracked legacy thread) and NULL-owner rows — only an existing row with a different user_id triggers 404. Use `require_existing=True` on destructive routes to close this gap (`backend/app/gateway/authz.py`)
- Auth middleware stamps BOTH `request.state.user` AND the `deerflow.runtime.user_context` contextvar — repository-layer owner filters depend on the contextvar being set, not on `request.state` (`backend/app/gateway/auth_middleware.py`)
- `AuthMiddleware` runs before `@require_auth` decorators — if the middleware already authenticated the user, `@require_auth`'s `_authenticate()` short-circuits because `request.state.auth` is already set, avoiding a second JWT-decode + DB-lookup pipeline (`backend/app/gateway/auth_middleware.py`, `backend/app/gateway/authz.py`)
- Password hashing uses a versioned format (`$dfv2$...` for SHA-256 + bcrypt, `$dfv1$...` for plain bcrypt) — `needs_rehash()` auto-upgrades v1 hashes on next successful login, but the rehash failure is non-fatal (login still succeeds) (`backend/app/gateway/auth/password.py`)
- JWT secret is auto-generated and persisted to `.jwt_secret` if `AUTH_JWT_SECRET` is not set — sessions survive restarts but the secret is not shared across instances, so multi-replica deployments MUST set `AUTH_JWT_SECRET` explicitly (`backend/app/gateway/auth/config.py`)
- `DEER_FLOW_AUTH_DISABLED=1` is automatically disabled in production (`DEER_FLOW_ENV=production` or `ENVIRONMENT=production`) — the `is_auth_disabled()` function checks both conditions (`backend/app/gateway/auth_disabled.py`)
- Internal auth token is auto-generated via `secrets.token_urlsafe(32)` if `DEER_FLOW_INTERNAL_AUTH_TOKEN` is not set — each gateway worker gets a different token, so channel manager calls within the same process always work but cross-process calls need the env var (`backend/app/gateway/internal_auth.py`)
- Admin initial credentials are written to `.deer-flow/admin_initial_credentials.txt` with mode 0600 instead of being logged — prevents cleartext secrets in log aggregators (`backend/app/gateway/auth/credential_file.py`, `git:94eee95f`)

## Architecture
- Three-layer auth: AuthMiddleware (global gate, fail-closed) → @require_auth/@require_permission decorators (route-level) → contextvar-based owner isolation (repository-layer, automatic) (`backend/app/gateway/auth_middleware.py`, `backend/app/gateway/authz.py`, `deerflow/runtime/user_context.py`)
- Provider Factory pattern: `AuthProvider` ABC with `LocalAuthProvider` implementation; OAuth providers can be added by subclassing (`backend/app/gateway/auth/providers.py`, `backend/app/gateway/auth/local_provider.py`)
- `UserRepository` ABC with `SQLiteUserRepository` implementation using the shared persistence engine — same session factory pattern as all other repositories (`backend/app/gateway/auth/repositories/base.py`, `backend/app/gateway/auth/repositories/sqlite.py`)
- Owner isolation is enforced at the STORAGE layer via contextvar sentinel pattern — `owner_id=AUTO` reads from `deerflow.runtime.user_context`, so any caller that forgets to pass owner_id still gets filtered results (`deerflow/runtime/user_context.py`, `git:94eee95f`)

## Decisions
- Chose contextvar-based owner isolation over passing user_id through every function signature — eliminates the risk of new routes accidentally leaking data and keeps router code unchanged (`deerflow/runtime/user_context.py`, `git:94eee95f`)
- Chose `token_version` invalidation over a token blocklist — simpler, no Redis dependency, immediate effect on password change (`backend/app/gateway/auth/jwt.py`)
- Chose SHA-256 pre-hash (v2) over plain bcrypt (v1) to avoid bcrypt's 72-byte silent truncation limit — transparent upgrade on next login (`backend/app/gateway/auth/password.py`)
- Chose to remove SQL orphan migration (unused in supported upgrade paths) — only LangGraph store orphan migration remains for the real "no-auth → with-auth" upgrade path (`backend/app/gateway/app.py`, `git:94eee95f`)

## Patterns
- `@require_auth` decorator must be placed BELOW `@require_permission` in the decorator stack — decorators execute bottom-to-top, so auth runs first (`backend/app/gateway/authz.py`)
- `AuthContext` is stored on `request.state.auth` after authentication — downstream handlers read it directly instead of re-resolving the user (`backend/app/gateway/authz.py`)
- All repository write paths stamp `owner_id` from the contextvar; background worker writes (no user context) pass `owner_id=None` which is valid for orphan rows (`deerflow/persistence/`, `git:94eee95f`)

## Conventions
- Auth error responses use structured `AuthErrorResponse(code=..., message=...)` instead of bare strings (`backend/app/gateway/auth/errors.py`)
- `TokenError` enum variants map to `AuthErrorCode` via `token_error_to_code()` — single source of truth for JWT→HTTP error mapping (`backend/app/gateway/auth/errors.py`)
- Test fixtures use `@pytest.fixture(autouse=True) _auto_user_context` to set a default user on every test, with `@pytest.mark.no_auto_user` opt-out (`git:94eee95f`)

## Security Considerations
- CSRF uses Double Submit Cookie pattern: `csrf_token` cookie (HttpOnly=False, SameSite=Strict) must match `X-CSRF-Token` header on state-changing requests (`backend/app/gateway/csrf_middleware.py`)
- Auth endpoints (login/register/initialize) are exempt from CSRF token check but still validate Origin header to prevent login CSRF/session fixation (`backend/app/gateway/csrf_middleware.py`)
- `_SERVER_RESERVED_METADATA_KEYS` strips `owner_id` and `user_id` from client-supplied metadata — prevents metadata-blob echo attacks (`backend/app/gateway/routers/threads.py`)
- Internal auth uses `secrets.compare_digest()` for timing-safe token comparison (`backend/app/gateway/internal_auth.py`)
- Common password blocklist rejects 40+ well-known passwords at registration (`backend/app/gateway/routers/auth.py`)
- Login rate limiting is per-IP with configurable subnet aggregation via `DEER_FLOW_RATE_LIMIT_TRUSTED_PROXIES` (`backend/app/gateway/routers/auth.py`)
