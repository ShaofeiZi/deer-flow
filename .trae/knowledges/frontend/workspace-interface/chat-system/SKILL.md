---
name: knowledge-frontend-chat-system
description: >
  Covers the chat/thread system: chat page routing, thread ID management, chat box layout
  with resizable artifact panel, and the useThreadChat hook for new thread creation.
  Navigate when: modifying chat page behavior, thread routing (/chats/[thread_id]), new thread
  creation flow, chat box resizable layout, or thread ID lifecycle.
  Excludes: message rendering (see ../message-rendering/), artifact content display (see
  ../artifact-display/), thread streaming/data fetching (see ../../core-services/thread-client/).
  Keywords: chat, thread, ChatBox, useThreadChat, thread_id, new chat, resizable panel,
  chat page, thread routing, /chats/new.
---

## Module Structure

The chat system manages the chat page lifecycle: routing between new and existing threads,
generating thread IDs for new chats, and providing the resizable chat+artifact panel layout.

### Directory Layout
- `frontend/src/components/workspace/chats/` — Chat system components
  - `chat-box.tsx` — Resizable panel group: chat panel (60%) + artifact panel (40%)
  - `use-chat-mode.ts` — Chat mode detection (new vs existing thread)
  - `use-thread-chat.ts` — Thread ID management hook for new/existing threads
  - `index.ts` — Barrel exports
- `frontend/src/app/workspace/chats/` — Chat route pages
  - `page.tsx` — Chat index page (new chat or redirect)
  - `[thread_id]/page.tsx` — Specific thread chat page
  - `[thread_id]/layout.tsx` — Thread-level layout with providers
  - `[thread_id]/providers.tsx` — Thread context provider wrapper

### Key Entry Points
- `ChatBox` in `frontend/src/components/workspace/chats/chat-box.tsx` — Resizable chat + artifact panel
- `useThreadChat` in `frontend/src/components/workspace/chats/use-thread-chat.ts` — Thread ID lifecycle hook
- `frontend/src/app/workspace/chats/[thread_id]/page.tsx` — Thread chat page entry

## Gotchas
- `useThreadChat` generates a UUID for new threads via `useRef` — the ref persists across renders but must be reset when navigating away from `/new`; failing to reset causes stale UUIDs to leak into existing thread views (`frontend/src/components/workspace/chats/use-thread-chat.ts`)
- After `history.replaceState` updates the URL from `/chats/new` to `/chats/{UUID}`, Next.js `useParams` may still return the stale `"new"` value because `replaceState` does not trigger router updates — `useThreadChat` explicitly guards against this to prevent 422 errors from LangGraph (`frontend/src/components/workspace/chats/use-thread-chat.ts`)
- The `ChatBox` uses `ResizablePanelGroup` with IDs derived from `pathname` — the ID must be sanitized to remove special characters to avoid DOM ID validation errors (`frontend/src/components/workspace/chats/chat-box.tsx`)
- Artifact panel auto-opens when `write_file` or `str_replace` tool calls are detected during streaming — this uses a `setTimeout` with 100ms delay and checks `isLoading && isLast` to only fire for the most recent tool call (`frontend/src/components/workspace/chats/chat-box.tsx`)
- In static website mode, the first artifact is auto-selected on thread load via `autoSelectFirstArtifact` state — this flag is set to false after the first selection to prevent re-selection on re-renders (`frontend/src/components/workspace/chats/chat-box.tsx`)
- Thread ID changes trigger artifact deselection — the `threadIdRef` comparison in the effect ensures artifacts from the previous thread are cleared (`frontend/src/components/workspace/chats/chat-box.tsx`)

## Architecture
- The chat box uses a horizontal `ResizablePanelGroup` with two panels: chat (default 100%) and artifacts (default 0%). When an artifact is opened, the layout animates to 60/40 split (`frontend/src/components/workspace/chats/chat-box.tsx`)
- New thread creation uses a client-generated UUID that serves as the thread ID before the server confirms — this UUID is passed to `useThreadStream` which creates the thread on first message send (`frontend/src/components/workspace/chats/use-thread-chat.ts`)
- The `isMock` flag is read from URL search params (`?mock=true`) and passed through to the API client to use mock endpoints (`frontend/src/components/workspace/chats/use-thread-chat.ts`)

## Patterns
- Thread ID is managed via `useState` initialized from `useParams`, with `useRef` for the generated UUID — the ref provides stable identity across renders while state triggers re-renders when the thread ID changes (`frontend/src/components/workspace/chats/use-thread-chat.ts`)
- The artifact panel's resizable handle is hidden (`pointer-events-none opacity-0`) when no artifact is open, preventing accidental resize of the invisible panel (`frontend/src/components/workspace/chats/chat-box.tsx`)
