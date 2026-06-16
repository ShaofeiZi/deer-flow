---
name: knowledge-frontend-artifact-display
description: >
  Covers artifact display: artifact panel, file list, file detail view, artifact content
  loading (from server and from tool call args), artifact preview utilities, and the
  useArtifacts hook for artifact state management.
  Navigate when: modifying artifact panel behavior, file list rendering, artifact content
  fetching, write-file preview, or artifact selection/deselection logic.
  Excludes: message rendering (see ../message-rendering/), chat box layout (see ../chat-system/).
  Keywords: artifact, ArtifactFileDetail, ArtifactFileList, useArtifacts, artifact content,
  write-file, file preview, artifact panel, artifact loading, .skill files.
---

## Module Structure

The artifact display system handles the right-side panel that shows files created or modified
by the AI agent. It supports two content sources: server-fetched files (via API) and
in-memory content from tool call arguments (for streaming preview).

### Directory Layout
- `frontend/src/components/workspace/artifacts/` — Artifact UI components
  - `artifact-file-detail.tsx` — Full file detail view with content rendering
  - `artifact-file-list.tsx` — List of artifact files in a thread
  - `artifact-trigger.tsx` — Button/trigger to open artifact panel
  - `context.tsx` — Artifact context provider (useArtifacts hook)
  - `index.ts` — Barrel exports
- `frontend/src/core/artifacts/` — Artifact data loading
  - `hooks.ts` — `useArtifactContent` hook for fetching artifact content
  - `loader.ts` — `loadArtifactContent` (server fetch) and `loadArtifactContentFromToolCall` (in-memory)
  - `preview.ts` — `buildWriteFileDraftContent` for write-file preview from tool call args
  - `utils.ts` — `urlOfArtifact` for constructing artifact API URLs
  - `index.ts` — Barrel exports

### Key Entry Points
- `useArtifacts` in `frontend/src/components/workspace/artifacts/context.tsx` — Artifact state: open/close, select/deselect, artifact list
- `useArtifactContent` in `frontend/src/core/artifacts/hooks.ts` — Fetches artifact content with 5-minute cache
- `loadArtifactContent` in `frontend/src/core/artifacts/loader.ts` — Fetches file content from the backend API
- `loadArtifactContentFromToolCall` in `frontend/src/core/artifacts/loader.ts` — Extracts content from tool call args for streaming preview

## Gotchas
- `.skill` files are treated specially: the loader appends `/SKILL.md` to the filepath before fetching, because skill files are actually directories containing a SKILL.md entry point (`frontend/src/core/artifacts/loader.ts`)
- `loadArtifactContentFromToolCall` returns `undefined` (not null) when content can't be found — callers must handle this to avoid rendering "undefined" as text (`frontend/src/core/artifacts/loader.ts`)
- The `write-file:` URL scheme is used to identify in-memory artifacts — the `useArtifactContent` hook checks for this prefix to decide whether to fetch from server or extract from tool calls (`frontend/src/core/artifacts/hooks.ts`)
- Artifact content is cached for 5 minutes via `staleTime` in react-query — changes to files on disk won't be reflected until the cache expires or is invalidated (`frontend/src/core/artifacts/hooks.ts`)
- When switching threads, artifacts are updated from `thread.values.artifacts` but the selected artifact is NOT automatically deselected — a commented-out code block shows this was intentional due to artifact auto-discovery not working (`frontend/src/components/workspace/chats/chat-box.tsx`)
- The `buildWriteFileDraftContent` function searches through thread messages to find the tool call with matching message_id and tool_call_id — if messages have been summarized/truncated, the draft content may not be found (`frontend/src/core/artifacts/preview.ts`)

## Architecture
- Artifact state is managed via React context (`useArtifacts`) providing: `artifacts` (file list), `open`/`setOpen` (panel visibility), `selectedArtifact` (currently viewed file), `select`/`deselect`, and `autoOpen`/`autoSelect` flags for streaming auto-open behavior (`frontend/src/components/workspace/artifacts/context.tsx`)
- Content loading uses a dual-path strategy: server fetch via `loadArtifactContent` for persisted files, and in-memory extraction via `loadArtifactContentFromToolCall` for files being written during streaming (`frontend/src/core/artifacts/loader.ts`)
- The artifact panel is integrated into `ChatBox` via `ResizablePanelGroup` — when an artifact is selected, the panel animates from 0% to 40% width (`frontend/src/components/workspace/chats/chat-box.tsx`)

## Patterns
- `write_file` and `str_replace` tool calls in `MessageGroup` auto-select the artifact and open the panel when they are the last tool call during streaming (`frontend/src/components/workspace/messages/message-group.tsx`)
- The artifact file list is also rendered inline in messages when the agent uses `present_files` — this uses the same `ArtifactFileList` component but outside the resizable panel (`frontend/src/components/workspace/messages/message-list.tsx`)
- Artifact URLs are constructed via `urlOfArtifact` which handles both real API paths and mock paths for static/demo mode (`frontend/src/core/artifacts/utils.ts`)

## Dependencies
- `@tanstack/react-query` — Used for artifact content fetching with caching
- `@/components/ai-elements/conversation` — Empty state component for artifact panel
- `@/components/ui/resizable` — Resizable panel group for chat/artifact split
