---
name: frontend-api-integration
description: >
  API integration layer for the DeerFlow frontend — covers the CSRF-protected fetch
  wrapper, LangGraph SDK client factory, SSR authentication guard, client auth context,
  and environment-based URL configuration. Navigate here when working on API call
  security, auth flow, gateway connectivity, or dual-mode (gateway/static) client
  initialization.
covers:
  - frontend/src/core/api/
  - frontend/src/core/auth/
  - frontend/src/core/config/
  - frontend/src/core/static-mode.ts
navigate-when:
  - debugging 403 errors on POST/PUT/DELETE/PATCH (missing CSRF header)
  - understanding how the LangGraph SDK client is created and configured
  - modifying SSR authentication flow or the AuthResult tagged union
  - adding new environment variables for backend/gateway URLs
  - working with static/demo mode client stubbing
  - handling auth error response parsing from FastAPI
excludes:
  - thread streaming logic (thread-client domain)
  - settings persistence (settings-system domain)
  - i18n (internationalization domain)
keywords:
  - CSRF
  - Double Submit Cookie
  - fetch wrapper
  - LangGraph SDK
  - getAPIClient
  - getServerSideUser
  - AuthProvider
  - AuthResult
  - tagged union
  - static mode
  - gateway config
---

## Module Structure

```
frontend/src/core/api/
├── fetcher.ts          # fetch() with CSRF injection + 401 redirect; readCsrfCookie(), getCsrfHeaders()
├── api-client.ts       # getAPIClient() — LangGraph SDK client factory with CSRF onRequest hook + static client
└── stream-mode.ts      # sanitizeRunStreamOptions() for stream payload sanitization

frontend/src/core/auth/
├── server.ts           # getServerSideUser() — SSR auth guard returning tagged AuthResult
├── AuthProvider.tsx     # Client auth context: user state, logout, refreshUser, visibility detection
├── types.ts            # User schema (Zod), AuthResult tagged union, parseAuthError(), buildLoginUrl()
├── gateway-config.ts   # Gateway URL validation with Zod
├── auth-disabled-user.ts # Fake user when AUTH_DISABLED=true
└── static-user.ts      # Fake user for static/demo mode

frontend/src/core/config/
└── index.ts            # getBackendBaseURL(), getLangGraphBaseURL()

frontend/src/core/static-mode.ts  # isStaticWebsiteOnly() — gate for dual-mode behavior
```

Key entry points:
- `fetch()` in `fetcher.ts` — centralized fetch wrapper; every API call should use this instead of raw `fetch()`
- `getAPIClient()` in `api-client.ts` — single source of truth for LangGraph SDK client instances
- `getServerSideUser()` in `auth/server.ts` — SSR auth guard; returns a tagged union, callers must exhaustively switch
- `AuthProvider` in `AuthProvider.tsx` — client-side auth context; holds display user info only, never tokens

## Gotchas

- Raw `fetch()` calls to state-changing endpoints (POST/PUT/DELETE/PATCH) will fail with 403 because they lack the `X-CSRF-Token` header — ALWAYS use the centralized `fetch()` wrapper or `getAPIClient()` (frontend/src/core/api/fetcher.ts:56-89)
- The `getAPIClient()` factory caches clients in a module-level `Map` — if you change gateway config at runtime, existing cached clients will still point to the old URL; the cache key is `"default"` or `"mock"` (frontend/src/core/api/api-client.ts:160-171)
- SSR auth has a 5-second timeout on `/api/v1/auth/me` — if the gateway is slow or unreachable, `getServerSideUser()` returns `gateway_unavailable`, NOT `unauthenticated`; the UI must handle both states differently (frontend/src/core/auth/server.ts:10,70-101)
- `getServerSideUser()` checks `setup-status` when no session cookie exists — if the system hasn't been initialized, it returns `system_setup_required`; if the setup-status endpoint is unreachable, it falls through to `unauthenticated` (frontend/src/core/auth/server.ts:42-67)
- The `AuthResult` tagged union has 6 variants — adding a new variant without updating all `switch` statements will cause a TypeScript compile error via `assertNever()`, which is intentional to prevent silent fallthrough (frontend/src/core/auth/types.ts:16-26)
- In static mode, `getAPIClient()` returns a fully stubbed client where `runs.stream` and `runs.joinStream` are empty async generators — any code that assumes stream events will arrive will silently do nothing (frontend/src/core/api/api-client.ts:122-158)

## Architecture

- Double Submit Cookie CSRF: the gateway sets a `csrf_token` cookie at login; the frontend reads it via `readCsrfCookie()` and echoes it as `X-CSRF-Token` header on state-changing methods; both `fetcher.ts` and `api-client.ts` share the same helpers (frontend/src/core/api/fetcher.ts:17-89)
- Split auth architecture: SSR guard (`getServerSideUser`) runs in `layout.tsx` and passes `initialUser` to `AuthProvider`; the client provider handles logout, refresh, and tab visibility detection — this avoids auth flicker on page load (frontend/src/core/auth/server.ts:16-101, frontend/src/core/auth/AuthProvider.tsx:47-173)
- Dual-mode gating: `isStaticWebsiteOnly()` gates all gateway-dependent code — when true, auth returns a static user, the API client is stubbed, and no real network calls are made (frontend/src/core/static-mode.ts:3-5)
- Client factory with stream wrapping: `createCompatibleClient()` wraps `runs.stream` with `sanitizeRunStreamOptions` and wraps `runs.joinStream` to handle inactive run stream errors (409) by clearing the reconnect key from sessionStorage (frontend/src/core/api/api-client.ts:82-120)
- Layered error parsing: `parseAuthError()` tries 4 envelope formats in order — top-level `{code, message}`, `{detail: {code, message}}`, `{detail: string}`, `{detail: [{msg, type, loc}]}` — to handle FastAPI's various error response shapes (frontend/src/core/auth/types.ts:63-94)
- URL resolution with SSR fallback: `getBackendBaseURL()` and `getLangGraphBaseURL()` use `window.location.origin` on the client and `http://localhost:2026` on the server, with env var overrides (`NEXT_PUBLIC_BACKEND_BASE_URL`, `NEXT_PUBLIC_LANGGRAPH_BASE_URL`) taking precedence (frontend/src/core/config/index.ts:11-43)

## Decisions

- Auth tokens are stored exclusively in HttpOnly cookies — the frontend never reads JWT tokens; `AuthProvider` only holds display user info (`id`, `email`, `system_role`), and the browser sends cookies automatically via `credentials: "include"` (frontend/src/core/auth/AuthProvider.tsx:42-45)
- The `AuthResult` tagged union uses `tag` as the discriminator (not `status` or `type`) — this enables TypeScript exhaustive checking and prevents silent fallthrough when new auth states are added (frontend/src/core/auth/types.ts:16-26)
- Logout clears local state immediately (before the server responds) and falls back to `window.location.href = "/"` if the logout request fails — this ensures all in-flight subscriptions are torn down even during a gateway outage (frontend/src/core/auth/AuthProvider.tsx:108-138)
- The CSRF cookie is read per-request (not at construction time) in the `onRequest` hook — this handles login/logout/password-change cookie rotation transparently without requiring client re-creation (frontend/src/core/api/api-client.ts:28-39)

## Patterns

- Tagged union for auth state: instead of nullable user + error string, `AuthResult` uses a discriminated union — callers `switch` on `result.tag`, and `assertNever()` provides compile-time exhaustiveness checking (frontend/src/core/auth/types.ts:16-26)
- Client factory caching: `getAPIClient()` uses a module-level `Map<string, LangGraphClient>` — clients are created lazily on first access and reused for subsequent calls with the same cache key (frontend/src/core/api/api-client.ts:160-171)
- Tab visibility refresh: `AuthProvider` listens for `visibilitychange` events and refreshes the user when the tab becomes visible again, throttled to once per 60 seconds — this catches session expiration while the tab was backgrounded (frontend/src/core/auth/AuthProvider.tsx:144-161)
- SSR-safe cookie reading: `readCsrfCookie()` returns `null` when `document` is undefined, making it safe to import from server components without guards (frontend/src/core/api/fetcher.ts:29-37)
- Gateway config validation: `getGatewayConfig()` uses Zod to validate `GATEWAY_INTERNAL_URL` at module load time — invalid config throws immediately, preventing silent failures later (frontend/src/core/auth/gateway-config.ts)

## Conventions

- All API calls use `credentials: "include"` — enforced by the centralized `fetch()` wrapper and the LangGraph SDK's `onRequest` hook (frontend/src/core/api/fetcher.ts:77-81)
- SSR auth fetches use `cache: "no-store"` to prevent stale user data across requests (frontend/src/core/auth/server.ts:52,76)
- CSRF header injection only applies to state-changing methods (POST/PUT/DELETE/PATCH) — GET/HEAD/OPTIONS/TRACE skip CSRF to mirror the gateway's `should_check_csrf` logic (frontend/src/core/api/fetcher.ts:65-75)
- The `onRequest` hook creates a fresh `Headers` instance instead of mutating the caller-supplied headers — this prevents side effects on shared header objects (frontend/src/core/api/api-client.ts:34-38)

## Dependencies

- `@langchain/langgraph-sdk` — `Client` class for LangGraph Server communication (frontend/src/core/api/api-client.ts:3)
- `zod` — validates user schema, auth error responses, and gateway configuration (frontend/src/core/auth/types.ts:1, frontend/src/core/auth/gateway-config.ts)
- `@t3-oss/env-nextjs` — validates environment variables at build time (frontend/src/env.js)
- `next/headers` — `cookies()` for SSR auth guard cookie access (frontend/src/core/auth/server.ts:1)
- `next/navigation` — `useRouter`, `usePathname` for auth redirects (frontend/src/core/auth/AuthProvider.tsx:3)
