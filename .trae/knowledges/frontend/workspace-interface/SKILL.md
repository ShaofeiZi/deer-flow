---
name: knowledge-frontend-workspace-interface
description: >
  Covers the workspace UI shell: sidebar, header, input box, command palette, welcome screen,
  and workspace container components. This is the outer chrome that frames chat, agent, and
  artifact views.
  Navigate when: modifying workspace layout, sidebar behavior, header breadcrumbs, input box
  mode/model selection, command palette shortcuts, or welcome/empty states.
  Excludes: chat message rendering (see chat-system/), artifact display (see artifact-display/),
  settings dialog (see settings-system/).
  Keywords: workspace, sidebar, WorkspaceSidebar, WorkspaceHeader, InputBox, CommandPalette,
  welcome, PromptInput, mode selector, model selector, chat input, breadcrumb, WorkspaceContainer.
---

## Module Structure

The workspace interface provides the application shell: collapsible sidebar with navigation,
chat list, header with breadcrumbs, the main chat input box with mode/model selection, and
global UI elements like the command palette.

### Directory Layout
- `frontend/src/components/workspace/` — Workspace shell components
  - `workspace-sidebar.tsx` — Collapsible sidebar with nav, chat list, footer menu
  - `workspace-header.tsx` — Sidebar header with brand, new chat button, sidebar trigger
  - `workspace-container.tsx` — Layout primitives: WorkspaceContainer, WorkspaceHeader (breadcrumbs), WorkspaceBody
  - `workspace-nav-chat-list.tsx` — Navigation links (Chats, Agents)
  - `workspace-nav-menu.tsx` — Footer menu (settings, GitHub, about)
  - `recent-chat-list.tsx` — Recent threads list in sidebar
  - `input-box.tsx` — Main chat input with mode/model selection, skill suggestions, followups
  - `command-palette.tsx` — Global command palette (Cmd+K)
  - `welcome.tsx` — Welcome/empty state screen
  - `agent-welcome.tsx` — Agent-specific welcome screen
  - `gateway-offline-banner.tsx` — Banner shown when gateway is unreachable
  - `gateway-offline-fallback.tsx` — AuthProvider wrapper for offline mode
  - `gateway-offline-banner-helpers.ts` — Gateway health check probe logic
  - `streaming-indicator.tsx` — Animated indicator during streaming
  - `mode-hover-guide.tsx` — Tooltip explaining input modes
  - `thread-title.tsx` — Editable thread title display
  - `copy-button.tsx` — Copy-to-clipboard button for messages
  - `export-trigger.tsx` — Thread export trigger
  - `code-editor.tsx` — Code editor component
  - `todo-list.tsx` — Todo list display
  - `token-usage-indicator.tsx` — Token usage display in header
  - `flip-display.tsx` — Animated flip display for tool calls
  - `overscroll.tsx` — Overscroll behavior wrapper
  - `tooltip.tsx` — Reusable tooltip wrapper
  - `github-icon.tsx` — GitHub icon SVG
- `frontend/src/app/workspace/` — Workspace route pages
  - `layout.tsx` — SSR auth guard, wraps in AuthProvider + WorkspaceContent
  - `workspace-content.tsx` — Client shell: QueryClientProvider, SidebarProvider, CommandPalette, Toaster
  - `page.tsx` — Workspace index (redirects to /workspace/chats)
  - `chats/` — Chat thread pages
  - `agents/` — Agent gallery and agent-specific chat pages

### Key Entry Points
- `WorkspaceSidebar` in `frontend/src/components/workspace/workspace-sidebar.tsx` — Main sidebar assembly
- `InputBox` in `frontend/src/components/workspace/input-box.tsx` — Chat input with mode/model/skill selection
- `WorkspaceContent` in `frontend/src/app/workspace/workspace-content.tsx` — Client-side shell entry
- `WorkspaceLayout` in `frontend/src/app/workspace/layout.tsx` — SSR auth guard entry

## Gotchas
- `isWelcomeMode` is a purely visual flag for centering the input — it is decoupled from whether the backend has created a thread; changing welcome behavior must not couple these (`frontend/src/components/workspace/input-box.tsx`)
- The input box auto-selects the first available model on mount if `context.model_name` doesn't match any loaded model — this effect fires before user interaction and can override stored preferences if models load asynchronously (`frontend/src/components/workspace/input-box.tsx`)
- Sidebar open state is persisted via a `sidebar_state` cookie read in the server component — the cookie must be parsed as `"true"`/`"false"` strings, not booleans (`frontend/src/app/workspace/workspace-content.tsx`)
- In static website mode, the header brand links to `/` (home); in gateway mode, it's a non-interactive text label — changing this requires checking `NEXT_PUBLIC_STATIC_WEBSITE_ONLY` (`frontend/src/components/workspace/workspace-header.tsx`)
- The `RecentChatList` component is only rendered when the sidebar is expanded (`isSidebarOpen`), not in collapsed icon mode — this prevents unnecessary data fetching (`frontend/src/components/workspace/workspace-sidebar.tsx`)
- Skill suggestions in the input box are dismissed when the user presses Escape, and the dismissed value is tracked to prevent re-showing until the input changes (`frontend/src/components/workspace/input-box.tsx`)

## Architecture
- The workspace uses a two-layer auth pattern: server component (`layout.tsx`) calls `getServerSideUser()` and wraps in `AuthProvider`, then client component (`workspace-content.tsx`) provides the UI shell (`frontend/src/app/workspace/layout.tsx`, `frontend/src/app/workspace/workspace-content.tsx`)
- The sidebar uses shadcn/ui's `SidebarProvider` with `collapsible="icon"` mode — when collapsed, only icons show; the `sidebar_state` cookie persists the preference across page loads (`frontend/src/app/workspace/workspace-content.tsx`)
- Input modes (flash/thinking/pro/ultra) map to backend context flags: `thinking_enabled`, `is_plan_mode`, `subagent_enabled`, and `reasoning_effort` — the mapping is centralized in `sendMessage` within `useThreadStream` (`frontend/src/components/workspace/input-box.tsx`, `frontend/src/core/threads/hooks.ts`)
- The command palette uses shadcn/ui's `Command` component and registers global keyboard shortcuts via `useGlobalShortcuts` (`frontend/src/components/workspace/command-palette.tsx`)

## Patterns
- Followup suggestions are fetched after each AI response completes (streaming stops), using the last 6 human/AI messages as context (`frontend/src/components/workspace/input-box.tsx`)
- When a followup suggestion would replace existing input text, a confirmation dialog is shown with options to replace or append (`frontend/src/components/workspace/input-box.tsx`)
- The input box guards against submitting before the initial model auto-selection effect has flushed — it defers submission by one microtask if model_name is stale (`frontend/src/components/workspace/input-box.tsx`)

## Dependencies
- `@/components/ui/sidebar` — shadcn/ui sidebar primitives used for the workspace shell
- `@/components/ai-elements/prompt-input` — PromptInput component family for the chat input
- `@/components/ai-elements/model-selector` — Model selector dropdown in the input footer
- `@/components/ai-elements/suggestion` — Suggestion chips for followups and welcome prompts

## Child Knowledge Nodes
- `./chat-system/SKILL.md` — Navigate when: modifying chat page, thread routing, chat box layout, or useThreadChat hook
- `./message-rendering/SKILL.md` — Navigate when: modifying message display, message grouping, tool call rendering, or streamdown plugins
- `./artifact-display/SKILL.md` — Navigate when: modifying artifact panel, file list, file detail, or artifact content loading
