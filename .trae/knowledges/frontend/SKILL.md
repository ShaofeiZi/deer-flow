---
name: knowledge-frontend
description: >
  Covers the DeerFlow Next.js frontend application: workspace UI, chat system, message rendering,
  artifact display, core services (thread client, API integration), settings, i18n, and landing site.
  Navigate when: modifying any frontend code, debugging UI issues, adding new workspace features,
  changing auth/login flow, adjusting i18n translations, or working on the landing page.
  Excludes: backend gateway, LangGraph agent logic, persistence layer (see backend knowledge nodes).
  Keywords: frontend, Next.js, React, workspace, chat, messages, artifacts, i18n, settings,
  auth, login, landing, streamdown, langgraph-sdk, tailwind, shadcn, PromptInput, InputBox,
  MessageList, ChatBox, AuthProvider, useThreadStream, fetcher, api-client.
---

## Module Structure

The frontend is a Next.js 15 App Router application using React 19, TypeScript, Tailwind CSS,
and shadcn/ui components. It provides the user-facing workspace for interacting with DeerFlow
agents, managing threads/chats, viewing artifacts, and configuring settings.

### Directory Layout
- `frontend/src/app/` — Next.js App Router pages and layouts
  - `(auth)/` — Login, setup, and auth layout pages
  - `workspace/` — Main workspace: chats, agents, layout with sidebar
  - `blog/` — Blog pages with MDX content
  - `[lang]/docs/` — Multi-language documentation pages
  - `api/` — Next.js API route handlers (memory proxy)
  - `mock/` — Mock API endpoints for static/demo mode
- `frontend/src/components/` — React components
  - `workspace/` — Workspace-specific components (sidebar, input, messages, artifacts, settings)
  - `ai-elements/` — Reusable AI UI primitives (PromptInput, ChainOfThought, reasoning, etc.)
  - `landing/` — Landing page sections (hero, skills, community, etc.)
  - `ui/` — shadcn/ui base components (button, dialog, sidebar, etc.)
- `frontend/src/core/` — Business logic, API clients, state management
  - `api/` — API client, fetcher with CSRF, stream mode sanitization
  - `auth/` — AuthProvider, server-side user fetch, gateway config, types
  - `threads/` — Thread streaming hooks, history loading, search, mutations
  - `messages/` — Message utilities, token usage models
  - `artifacts/` — Artifact content loading and preview
  - `streamdown/` — Markdown streaming plugin configurations
  - `i18n/` — Internationalization: context, hooks, server-side detection, translations
  - `settings/` — Local settings store with localStorage persistence
  - `config/` — Backend/LangGraph base URL resolution
  - `agents/`, `skills/`, `models/`, `mcp/`, `memory/`, `tasks/`, `uploads/` — Feature-specific API clients and hooks
- `frontend/src/content/` — MDX documentation content (en/zh)
- `frontend/src/hooks/` — Global hooks (shortcuts, mobile detection)
- `frontend/src/lib/` — Utility functions (cn, IME handling)
- `frontend/src/styles/` — Global CSS
- `frontend/src/env.js` — Environment variable validation with @t3-oss/env-nextjs

### Key Entry Points
- `frontend/src/app/layout.tsx` — Root layout with theme, i18n, and query client providers
- `frontend/src/app/workspace/layout.tsx` — Workspace layout: SSR auth guard, AuthProvider, gateway fallback
- `frontend/src/app/workspace/workspace-content.tsx` — Client-side sidebar + command palette shell
- `frontend/src/core/api/api-client.ts` — LangGraph SDK client factory with CSRF injection
- `frontend/src/core/api/fetcher.ts` — Centralized fetch wrapper with CSRF + 401 redirect
- `frontend/src/core/threads/hooks.ts` — `useThreadStream` — core streaming hook for chat

## Gotchas
- The `fetch` wrapper in `fetcher.ts` auto-redirects to `/login` on 401; any raw `fetch()` call bypasses CSRF injection and will get 403 from the gateway (`frontend/src/core/api/fetcher.ts`)
- `useThreadChat` must guard against stale `useParams` returning "new" after `history.replaceState` — otherwise downstream hooks receive an invalid thread ID and LangGraph returns 422 (`frontend/src/components/workspace/chats/use-thread-chat.ts`)
- The LangGraph SDK client's `onRequest` hook must read the CSRF cookie per-request (not at construction time) to handle login/logout cookie rotation transparently (`frontend/src/core/api/api-client.ts`)
- `reasoningPlugins` intentionally excludes `rehypeRaw` to prevent LLM-hallucinated HTML tags from rendering as DOM elements — if reasoning content needs raw HTML, this is the wrong plugin set (`frontend/src/core/streamdown/plugins.ts`)
- `isWelcomeMode` is a purely visual flag decoupled from backend thread creation — see issue #2746 (`frontend/src/components/workspace/input-box.tsx`)
- The `AuthProvider` never holds JWT tokens — only display information; tokens are HttpOnly cookies managed by the gateway (`frontend/src/core/auth/AuthProvider.tsx`)

## Architecture
- The frontend uses a dual-mode architecture: full gateway-connected mode and static/demo mode (`NEXT_PUBLIC_STATIC_WEBSITE_ONLY`). In static mode, the LangGraph SDK client is replaced with mock implementations that serve demo data (`frontend/src/core/api/api-client.ts`, `frontend/src/core/static-mode.ts`)
- Workspace layout is a server component that calls `getServerSideUser()` for SSR auth, then wraps children in `AuthProvider` + `WorkspaceContent` (client component with sidebar) (`frontend/src/app/workspace/layout.tsx`)
- Thread streaming uses `@langchain/langgraph-sdk/react`'s `useStream` hook with history loading via `useThreadHistory` that cursor-paginates through run messages (`frontend/src/core/threads/hooks.ts`)
- Message display merges three sources: history messages (from run event store), live stream messages (from LangGraph SSE), and optimistic messages (shown before server confirms) (`frontend/src/core/threads/hooks.ts`)
- Settings are persisted to localStorage with a custom `useSyncExternalStore`-based store that supports cross-tab synchronization via the `storage` event (`frontend/src/core/settings/store.ts`)

## Decisions
- Migrated from better-auth library to custom FastAPI-based auth with JWT in HttpOnly cookies and Double Submit Cookie CSRF pattern per RFC-001 (`frontend/src/core/auth/`, `git:94eee95f`)
- Chose `@t3-oss/env-nextjs` for environment variable validation to catch misconfiguration at build time rather than runtime (`frontend/src/env.js`)
- Chose `streamdown` (custom streaming markdown renderer) over raw `react-markdown` for animated word-by-word rendering during streaming (`frontend/src/core/streamdown/`)

## Patterns
- All API calls that mutate state (POST/PUT/DELETE/PATCH) must go through `fetchWithAuth` from `fetcher.ts` — raw `fetch()` silently breaks CSRF (`frontend/src/core/api/fetcher.ts`)
- Optimistic UI updates: human messages are shown immediately, then cleared when the server's copy arrives via the stream (`frontend/src/core/threads/hooks.ts`)
- Thread search caches (both flat and infinite) are optimistically updated on stream creation, title changes, and deletions to avoid refetch latency (`frontend/src/core/threads/hooks.ts`)
- Component files co-locate related exports in `index.ts` barrel files for clean imports (`frontend/src/components/workspace/messages/index.ts`, `frontend/src/components/workspace/artifacts/index.ts`)

## Conventions
- i18n keys follow dot-notation: `category.subCategory.specificKey` (e.g., `settings.sections.account`) (`frontend/src/core/i18n/locales/types.ts`)
- `use client` directive is used on all components that use hooks, browser APIs, or event handlers
- Server components are used for SSR data fetching (auth, locale detection) and pass data as props to client components
- Environment variables prefixed with `NEXT_PUBLIC_` are available client-side; all others are server-only (`frontend/src/env.js`)

## Dependencies
- `@langchain/langgraph-sdk` — LangGraph client for thread/runs/stream APIs; the `onRequest` hook is critical for CSRF (`frontend/src/core/api/api-client.ts`)
- `@tanstack/react-query` — Server state management for threads, runs, models, skills, agents
- `streamdown` — Custom streaming markdown renderer with plugin system (`frontend/src/core/streamdown/`)
- `next-themes` — Dark/light/system theme switching
- `sonner` — Toast notifications
- `zod` — Runtime schema validation for env vars, auth responses, settings

## Child Knowledge Nodes
- `./workspace-interface/SKILL.md` — Navigate when: modifying workspace layout, sidebar, header, input box, or command palette
- `./core-services/SKILL.md` — Navigate when: modifying API clients, thread streaming, auth flow, or config resolution
- `./settings-system/SKILL.md` — Navigate when: modifying settings UI, localStorage persistence, or settings-related hooks
- `./internationalization/SKILL.md` — Navigate when: adding translations, modifying locale detection, or changing i18n infrastructure
- `./landing-site/SKILL.md` — Navigate when: modifying landing page, blog, auth pages, or documentation layout
