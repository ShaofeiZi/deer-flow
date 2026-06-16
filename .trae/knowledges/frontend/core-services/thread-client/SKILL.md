---
name: frontend-thread-client
description: >
  Thread streaming, history loading, message merging, and React Query integration
  for the DeerFlow frontend. Navigate here when working on LangGraph `useStream`
  lifecycle, optimistic message handling, history pagination, token usage tracking,
  or thread cache management.
covers:
  - frontend/src/core/threads/
navigate-when:
  - debugging stream message ordering or deduplication issues
  - understanding how optimistic messages are created and cleared
  - modifying thread history loading (useThreadHistory, infinite scroll)
  - adding or changing thread-related React Query cache updates
  - working with token usage tracking or summarization middleware messages
  - implementing thread export or static demo thread data
excludes:
  - LangGraph SDK client factory (api-integration domain)
  - CSRF fetch wrapper (api-integration domain)
  - message rendering (message-rendering domain)
  - artifact display (artifact-display domain)
keywords:
  - useThreadStream
  - useThreadHistory
  - useStream
  - optimistic messages
  - message merging
  - React Query
  - thread cache
  - summarization middleware
  - token usage
  - AgentThread
---

## Module Structure

```
frontend/src/core/threads/
├── hooks.ts          # useThreadStream, useThreadHistory, useThreads, useInfiniteThreads, mutations (~1508 lines)
├── types.ts          # AgentThread, AgentThreadState, AgentThreadContext, RunMessage, ThreadTokenUsageResponse
├── api.ts            # fetchThreadTokenUsage — fetches token usage from backend
├── utils.ts          # pathOfThread, textOfMessage, titleOfThread
├── token-usage.ts    # threadTokenUsageQueryKey and related helpers
├── static-demo.ts    # loadStaticDemoThread, loadStaticDemoThreads, staticDemoThreadState
├── export.ts         # Thread export functionality
└── index.ts          # Barrel exports
```

Key entry points:
- `useThreadStream()` — the main hook that orchestrates LangGraph streaming, history loading, and optimistic message management
- `useThreadHistory()` — infinite-scroll history loading with `useInfiniteQuery`
- `useThreads()` / `useInfiniteThreads()` — thread list queries with React Query
- `mergeMessages()` — deduplicates and merges history, live stream, and optimistic messages

## Gotchas

- The `useStream` hook uses `reconnectOnMount: true` — on page refresh it reconnects to the last active run; if the thread ID changed during navigation, stale stream state may appear until the new stream starts (frontend/src/core/threads/hooks.ts:493-497)
- Optimistic messages are NOT cleared immediately when server AI messages arrive — they wait until the server's human message count increases, because AI "messages-tuple" events can arrive before the input human message from "values" events (frontend/src/core/threads/hooks.ts:751-767)
- `sendMessage` uses a `sendInFlightRef` guard to prevent double-sends — calling `sendMessage` while a previous send is in flight silently returns without error (frontend/src/core/threads/hooks.ts:776-779)
- Thread switching resets all in-flight state (`startedRef`, `sendInFlightRef`, `messagesRef`, `summarizedRef`, `pendingUsageBaselineMessageIdsRef`) — failing to reset any of these causes optimistic messages or stream state to leak across chat views (frontend/src/core/threads/hooks.ts:715-723)
- The `mergeMessages` function assumes history/stream overlap is a contiguous suffix of history — if messages are interleaved (non-contiguous overlap), the deduplication will produce incorrect results (frontend/src/core/threads/hooks.ts:210-225)
- `upsertThreadInSearchCache` and `upsertThreadInInfiniteCache` mutate React Query caches directly — they must handle both insert (new thread) and merge (existing thread) cases, and must preserve existing metadata/values during merge (frontend/src/core/threads/hooks.ts:282-372)

## Architecture

- Three-source message merge: `mergeMessages()` combines history (loaded via `useThreadHistory`), live stream (from `useStream`), and optimistic (user's own messages) — deduplication uses message identity (`tool:<tool_call_id>` or `message:<id>`) and trims overlapping history suffix (frontend/src/core/threads/hooks.ts:194-232)
- Stream lifecycle split: `useThreadStream` tracks `onStreamThreadId` separately from `threadId` — `onStreamThreadId` is the ID passed to `useStream`, while `threadId` is the current route param; `handleStreamStart` bridges the gap when the server assigns a new thread ID (frontend/src/core/threads/hooks.ts:397-488)
- Summarization middleware detection: `getSummarizationMiddlewareMessages()` inspects `onUpdateEvent` data for known middleware keys (`SummarizationMiddleware.before_model`, `DeerFlowSummarizationMiddleware.before_model`) — when detected, summarized messages are moved from the live stream to history via `appendMessages` (frontend/src/core/threads/hooks.ts:258-280,544-572)
- Token usage baseline tracking: `pendingUsageBaselineMessageIdsRef` snapshots message IDs when streaming starts — only messages after the baseline are counted as "pending" for token usage display (frontend/src/core/threads/hooks.ts:738-749)
- Thread route resolution: `pathOfThread()` generates `/workspace/chats/<threadId>` or `/workspace/agents/<agentName>/chats/<threadId>` based on whether the thread has an `agent_name` in its context or metadata (frontend/src/core/threads/utils.ts:13-34)

## Patterns

- Optimistic message lifecycle: on send, human + (optional) AI "uploading" messages are set as optimistic; when server human message count increases, all optimistic messages are cleared — file uploads update the optimistic human message in-place with uploaded file info (frontend/src/core/threads/hooks.ts:807-898)
- Ref-based cross-callback state: `listenersRef`, `threadIdRef`, `messagesRef`, `summarizedRef`, `sendInFlightRef`, `pendingUsageBaselineMessageIdsRef` — all use refs to avoid stale closures in `useStream` callbacks without causing re-renders (frontend/src/core/threads/hooks.ts:424-427,700-703)
- Mode-to-context mapping: `sendMessage` derives `thinking_enabled`, `is_plan_mode`, `subagent_enabled`, and `reasoning_effort` from the user's selected mode (`flash`/`thinking`/`pro`/`ultra`) — this is the single place where mode strings map to boolean context flags (frontend/src/core/threads/hooks.ts:938-953)
- Cache invalidation on stream finish: `onFinish` invalidates thread search, infinite threads, and token usage queries — this ensures the sidebar and token display reflect the latest state after each run completes (frontend/src/core/threads/hooks.ts:668-684)
- Hidden message handling: `isHiddenFromUIMessage()` filters control messages from the visible message list — hidden messages that share an identity with a visible message are treated as control messages and removed during deduplication (frontend/src/core/threads/hooks.ts:87-117)

## Dependencies

- `@langchain/langgraph-sdk` — `useStream` hook and `Message`/`Run` types (frontend/src/core/threads/hooks.ts:1-3)
- `@tanstack/react-query` — `useQuery`, `useInfiniteQuery`, `useMutation`, `useQueryClient` for thread data management (frontend/src/core/threads/hooks.ts:6-11)
- `sonner` — toast notifications for stream errors, upload failures, and LLM retry messages (frontend/src/core/threads/hooks.ts:13,649)
- `@/core/api` — `getAPIClient()` for LangGraph SDK client instances (frontend/src/core/threads/hooks.ts:17)
- `@/core/api/fetcher` — centralized `fetch()` for token usage API calls (frontend/src/core/threads/hooks.ts:18)
- `@/core/i18n/hooks` — `useI18n()` for localized strings (frontend/src/core/threads/hooks.ts:20)
- `@/core/messages/utils` — `isHiddenFromUIMessage()` for message filtering (frontend/src/core/threads/hooks.ts:21)
- `@/core/settings` — `LocalSettings` type for context configuration (frontend/src/core/threads/hooks.ts:23)
- `@/core/uploads` — `uploadFiles()` and file type utilities for attachment handling (frontend/src/core/threads/hooks.ts:26)
