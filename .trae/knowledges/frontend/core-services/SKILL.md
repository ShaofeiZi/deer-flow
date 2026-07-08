---
name: frontend-core-services
description: >
  Core service layer for the DeerFlow frontend — covers thread streaming, API client
  management, authentication, and configuration. Navigate here when working on
  LangGraph SDK integration, CSRF-protected fetch, SSR auth guards, or dual-mode
  (gateway/static) URL resolution.
covers:
  - frontend/src/core/
navigate-when:
  - debugging LangGraph SDK client initialization or stream lifecycle
  - understanding CSRF token injection for state-changing API calls
  - modifying SSR authentication flow (getServerSideUser, AuthProvider)
  - resolving environment-based URL configuration (getBackendBaseURL, getLangGraphBaseURL)
  - working with thread streaming, history loading, or optimistic updates
excludes:
  - UI components (workspace-interface domain)
  - settings persistence (settings-system domain)
  - i18n (internationalization domain)
keywords:
  - LangGraph SDK
  - CSRF
  - authentication
  - thread streaming
  - API client
  - SSR auth guard
  - dual-mode
  - static website
  - useStream
  - React Query
---

## Module Structure

```
frontend/src/core/
├── api/                  # CSRF fetch wrapper + LangGraph SDK client factory
│   ├── fetcher.ts        # fetch() with CSRF injection + 401 redirect
│   ├── api-client.ts     # getAPIClient() with CSRF onRequest hook + static client fallback
│   └── stream-mode.ts    # sanitizeRunStreamOptions for stream payloads
├── auth/                 # Authentication: SSR guard, client context, types
│   ├── server.ts         # getServerSideUser() — tagged union AuthResult
│   ├── AuthProvider.tsx   # Client auth context with logout, refreshUser, visibility detection
│   ├── types.ts          # User schema (Zod), AuthResult tagged union, parseAuthError
│   ├── gateway-config.ts # Gateway URL validation with Zod
│   ├── auth-disabled-user.ts # Fake user when auth is disabled
│   └── static-user.ts    # Fake user for static/demo mode
├── config/
│   └── index.ts          # getBackendBaseURL(), getLangGraphBaseURL()
├── threads/              # Thread streaming, history, mutations, types
│   ├── hooks.ts          # useThreadStream, useThreadHistory, useThreads, useInfiniteThreads (~1508 lines)
│   ├── types.ts          # AgentThread, AgentThreadState, AgentThreadContext, RunMessage
│   ├── api.ts            # fetchThreadTokenUsage
│   ├── utils.ts          # Thread utility functions
│   ├── token-usage.ts    # Token usage query key and helpers
│   ├── static-demo.ts    # Static demo thread data for static mode
│   ├── export.ts         # Thread export functionality
│   └── index.ts          # Barrel exports
├── static-mode.ts        # isStaticWebsiteOnly() — gate for dual-mode behavior
├── messages/             # Message utilities (shared with message-rendering)
├── artifacts/            # Artifact loading (shared with artifact-display)
├── settings/             # Settings persistence (see settings-system domain)
├── i18n/                 # Internationalization (see internationalization domain)
└── ...
```

Key entry points:
- `getAPIClient()` in `api-client.ts` — the single source of truth for LangGraph SDK client instances
- `fetch()` in `fetcher.ts` — centralized fetch wrapper with CSRF and 401 handling
- `getServerSideUser()` in `auth/server.ts` — SSR auth guard returning a tagged union
- `useThreadStream()` in `threads/hooks.ts` — main hook for LangGraph streaming with history merging

## Gotchas

- Every state-changing API call MUST use the centralized `fetch()` wrapper or `getAPIClient()`, not raw `fetch()` — raw calls lack CSRF headers and will fail with 403 on POST/PUT/DELETE/PATCH (frontend/src/core/api/fetcher.ts:56-89)
- The `getAPIClient()` factory caches clients in a module-level `Map` keyed by `"default"` / `"mock"` — creating a new client with different config requires clearing the cache or using the `isMock` parameter (frontend/src/core/api/api-client.ts:160-171)
- SSR auth uses a 5-second `AbortController` timeout on `/api/v1/auth/me` — slow gateway responses return `gateway_unavailable`, not `unauthenticated`, so the UI must handle both (frontend/src/core/auth/server.ts:10,70-71)
- `getServerSideUser()` returns a tagged union (`authenticated` | `needs_setup` | `system_setup_required` | `unauthenticated` | `gateway_unavailable` | `config_error`) — callers MUST exhaustively switch on `tag`, never check `user` directly (frontend/src/core/auth/types.ts:16-22)
- In static/demo mode (`NEXT_PUBLIC_STATIC_WEBSITE_ONLY=true`), `getAPIClient()` returns a fully stubbed LangGraph client — `runs.stream` and `runs.joinStream` are empty async generators, and thread data comes from static JSON files (frontend/src/core/api/api-client.ts:122-158)
- The `useStream` hook from `@langchain/langgraph-sdk/react` uses `reconnectOnMount: true` — on page refresh, it reconnects to the last active run, which can cause stale stream state if the thread ID changed during navigation (frontend/src/core/threads/hooks.ts:493-497)

## Architecture

- Dual-mode architecture: `isStaticWebsiteOnly()` gates all gateway-dependent code — when true, the app uses static demo data and stubbed clients; when false, it connects to the real gateway via LangGraph SDK (frontend/src/core/static-mode.ts:3-5)
- CSRF protection uses the Double Submit Cookie pattern — the gateway sets a `csrf_token` cookie at login, and the frontend echoes it as an `X-CSRF-Token` header on state-changing methods; both `fetcher.ts` and `api-client.ts` share the same `readCsrfCookie()` + `isStateChangingMethod()` helpers (frontend/src/core/api/fetcher.ts:17-37,56-89)
- Auth flow is split between SSR guard (`getServerSideUser`) and client context (`AuthProvider`) — the SSR guard runs in layout.tsx and passes `initialUser` to the client provider, avoiding auth flicker; the client provider handles logout, refresh, and tab visibility detection (frontend/src/core/auth/server.ts:16-101, frontend/src/core/auth/AuthProvider.tsx:47-173)
- Thread streaming merges three message sources: history (loaded via `useThreadHistory`), live stream (from `useStream`), and optimistic (user's own messages before server echo) — the `mergeMessages` function deduplicates by message identity and trims overlapping history suffix (frontend/src/core/threads/hooks.ts:194-232)
- The LangGraph SDK client's `runs.stream` is wrapped to sanitize stream options via `sanitizeRunStreamOptions`, and `runs.joinStream` is wrapped to handle inactive run stream errors (409) by clearing the reconnect key from sessionStorage (frontend/src/core/api/api-client.ts:94-117)
- Environment-based URL resolution: `getBackendBaseURL()` and `getLangGraphBaseURL()` both fall back to `window.location.origin` on the client and `http://localhost:2026` on the server, with env var overrides taking precedence (frontend/src/core/config/index.ts:11-43)

## Decisions

- Auth tokens are stored in HttpOnly cookies (not localStorage) — the frontend never reads JWT tokens directly; it only holds display user info, and the browser automatically sends cookies with `credentials: "include"` (frontend/src/core/auth/AuthProvider.tsx:42-45)
- The `AuthResult` tagged union uses `tag` as the discriminator (not `status` or `type`) — this enables TypeScript exhaustive checking with `assertNever()` and prevents silent fallthrough when new states are added (frontend/src/core/auth/types.ts:16-26)
- Thread model overrides are stored per-thread in localStorage under `deerflow.thread-model.<threadId>` keys, separate from global settings — this allows per-conversation model selection without polluting the global settings object (frontend/src/core/settings/local.ts:20,67-91)

## Patterns

- Client factory caching: `getAPIClient()` uses a module-level `Map<string, LangGraphClient>` to avoid recreating clients — the cache key is `"default"` or `"mock"`, and clients are created lazily on first access (frontend/src/core/api/api-client.ts:160-171)
- Tagged union for auth state: instead of nullable user + error string, `AuthResult` uses a discriminated union with `tag` — callers use `switch (result.tag)` for exhaustive handling, and `assertNever()` catches unhandled cases at compile time (frontend/src/core/auth/types.ts:16-26)
- Stream lifecycle management: `useThreadStream` tracks `onStreamThreadId` separately from `threadId` to handle the gap between sending a message and receiving the server-assigned thread ID — the `handleStreamStart` callback bridges this gap (frontend/src/core/threads/hooks.ts:397-488)
- Summarization middleware detection: `getSummarizationMiddlewareMessages()` inspects `onUpdateEvent` data for known middleware update keys (`SummarizationMiddleware.before_model`, `DeerFlowSummarizationMiddleware.before_model`) to extract summarized messages and move them to history (frontend/src/core/threads/hooks.ts:258-280)
- Optimistic cache updates: `upsertThreadInSearchCache()` and `upsertThreadInInfiniteCache()` update React Query caches directly when a new thread is created via stream, avoiding a full refetch — they handle both insert (new thread) and merge (existing thread) cases (frontend/src/core/threads/hooks.ts:282-372)

## Conventions

- All API calls use `credentials: "include"` to send HttpOnly cookies — this is enforced by the centralized `fetch()` wrapper and the LangGraph SDK's `onRequest` hook (frontend/src/core/api/fetcher.ts:77-81)
- SSR auth uses `cache: "no-store"` on all gateway fetches to prevent stale user data from being served across requests (frontend/src/core/auth/server.ts:52,76)
- Error parsing follows a layered unwrap pattern: try top-level `{code, message}`, then `{detail: {code, message}}`, then `{detail: string}`, then `{detail: [{msg, type, loc}]}` — this handles FastAPI's various error envelope formats (frontend/src/core/auth/types.ts:63-94)
- The `onRequest` hook in `api-client.ts` reads the CSRF cookie per-request (not at construction time) to handle login/logout/password-change cookie rotation transparently (frontend/src/core/api/api-client.ts:28-39)

## Dependencies

- `@langchain/langgraph-sdk` — provides `Client` class and `useStream` React hook for LangGraph Server communication (frontend/src/core/api/api-client.ts:3, frontend/src/core/threads/hooks.ts:3)
- `@tanstack/react-query` — powers `useThreads`, `useInfiniteThreads`, `useThreadHistory`, and cache management for thread data (frontend/src/core/threads/hooks.ts:6-11)
- `zod` — validates user schema, auth error responses, and gateway configuration (frontend/src/core/auth/types.ts:1, frontend/src/core/auth/gateway-config.ts)
- `@t3-oss/env-nextjs` — validates environment variables at build time via `env.js` (frontend/src/env.js)
- `next/headers` — provides `cookies()` for SSR auth guard and server-side locale detection (frontend/src/core/auth/server.ts:1, frontend/src/core/i18n/server.ts:1)
- `sonner` — toast notifications for stream errors and mutation feedback (frontend/src/core/threads/hooks.ts:13)

## Child Knowledge Nodes

- **thread-client** (`frontend/core-services/thread-client/SKILL.md`) — Thread streaming, history loading, message merging, and React Query integration
- **api-integration** (`frontend/core-services/api-integration/SKILL.md`) — CSRF fetch wrapper, LangGraph SDK client factory, auth guards, and URL configuration
