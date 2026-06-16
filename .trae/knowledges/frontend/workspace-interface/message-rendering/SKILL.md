---
name: knowledge-frontend-message-rendering
description: >
  Covers message rendering: message list, message grouping, tool call visualization,
  markdown content rendering, streamdown plugin configurations, token usage display,
  and message utility functions.
  Navigate when: modifying how messages appear, adding new tool call renderers, changing
  markdown rendering behavior, adjusting streamdown plugins, or modifying message grouping logic.
  Excludes: thread data fetching (see ../../core-services/thread-client/), artifact display
  (see ../artifact-display/).
  Keywords: message, MessageList, MessageGroup, MarkdownContent, streamdown, tool call,
  ChainOfThought, reasoning, rehype, remark, token usage, message grouping, streaming.
---

## Module Structure

Message rendering handles the display of chat messages: grouping messages into turns,
rendering AI reasoning and tool calls as ChainOfThought steps, streaming markdown with
word animation, and displaying token usage inline.

### Directory Layout
- `frontend/src/components/workspace/messages/` — Message rendering components
  - `message-list.tsx` — Main message list: groups messages, renders each group by type
  - `message-group.tsx` — ChainOfThought rendering for AI reasoning + tool calls
  - `message-list-item.tsx` — Individual message item (human or AI)
  - `markdown-content.tsx` — Streaming markdown renderer using streamdown
  - `context.ts` — Thread context provider for messages
  - `skeleton.tsx` — Loading skeleton for message list
  - `message-token-usage.tsx` — Inline token usage display (per-turn or debug)
  - `subtask-card.tsx` — Subtask progress card for subagent tool calls
  - `index.ts` — Barrel exports
- `frontend/src/components/workspace/citations/` — Citation/artifact link components
  - `artifact-link.tsx` — Link to open an artifact
  - `citation-link.tsx` — Citation link in messages
- `frontend/src/core/streamdown/` — Markdown streaming plugin configs
  - `plugins.ts` — Plugin sets: streamdownPlugins, reasoningPlugins, humanMessagePlugins
  - `index.ts` — Re-exports
  - `mermaid.ts` — Mermaid diagram support
  - `preprocess.ts` — Markdown preprocessing before rendering
- `frontend/src/core/messages/` — Message utility functions
  - `utils.ts` — Message content extraction, grouping, file detection, reasoning extraction
  - `usage.ts` — Token count formatting
  - `usage-model.ts` — Token usage debug step model
- `frontend/src/core/rehype/` — Rehype plugin for word animation
  - `index.ts` — `rehypeSplitWordsIntoSpans` plugin

### Key Entry Points
- `MessageList` in `frontend/src/components/workspace/messages/message-list.tsx` — Main message rendering entry
- `MessageGroup` in `frontend/src/components/workspace/messages/message-group.tsx` — AI reasoning + tool call rendering
- `streamdownPlugins` in `frontend/src/core/streamdown/plugins.ts` — Plugin configurations for different content types
- `getMessageGroups` in `frontend/src/core/messages/utils.ts` — Groups raw messages into display groups

## Gotchas
- `reasoningPlugins` intentionally excludes `rehypeRaw` to prevent LLM-hallucinated HTML tags (e.g. `<simd>`) from rendering as DOM elements — this was a shipped bug fix (`frontend/src/core/streamdown/plugins.ts`, `git:7c87dc5b`)
- `humanMessagePlugins` excludes remark-gfm's autolink extension to prevent URLs from bleeding into adjacent text in human messages (`frontend/src/core/streamdown/plugins.ts`)
- The `streamdownPluginsWithWordAnimation` set excludes `rehypeRaw` — word animation and raw HTML are mutually exclusive because splitting words into spans breaks HTML structure (`frontend/src/core/streamdown/plugins.ts`)
- Tool call results are parsed as JSON first, falling back to raw string — malformed JSON in tool results silently becomes a string, which may cause rendering issues in tool-specific renderers (`frontend/src/components/workspace/messages/message-group.tsx`)
- The `task` tool call is explicitly skipped in `convertToSteps` — subagent tasks are rendered separately via `SubtaskCard`, not as regular tool calls (`frontend/src/components/workspace/messages/message-group.tsx`)
- Message deduplication uses identity keys (`message:id` or `tool:tool_call_id`) — hidden messages sharing an identity with a visible message are treated as control messages and dropped from display (`frontend/src/core/threads/hooks.ts`)

## Architecture
- Messages are grouped by `getMessageGroups` into types: `human`, `assistant`, `assistant:clarification`, `assistant:present-files`, `assistant:subagent`, and generic (reasoning/tool calls) (`frontend/src/core/messages/utils.ts`)
- AI reasoning and tool calls are rendered as `ChainOfThought` steps — reasoning becomes expandable thinking sections, tool calls become typed renderers (web_search, write_file, bash, etc.) with specific icons and layouts (`frontend/src/components/workspace/messages/message-group.tsx`)
- The `MessageGroup` component implements "show above" toggle for tool calls before the last one, and "show last thinking" toggle for the final reasoning step — both default to collapsed except in static website mode (`frontend/src/components/workspace/messages/message-group.tsx`)
- History messages are loaded via cursor pagination through run events, filtering out middleware-tagged messages (`caller` starts with `middleware:`) (`frontend/src/core/threads/hooks.ts`)
- Token usage can be displayed in three modes: `off`, `per_turn` (aggregate per assistant turn), and `step_debug` (per-message breakdown with shared attribution detection) (`frontend/src/components/workspace/messages/message-list.tsx`)

## Patterns
- Each tool call type has a dedicated renderer in the `ToolCall` component — unknown tool calls fall back to a generic wrench icon with the tool name (`frontend/src/components/workspace/messages/message-group.tsx`)
- `write_file` and `str_replace` tool calls auto-open the artifact panel when they are the last tool call during streaming — this uses a `setTimeout` to avoid React batching issues (`frontend/src/components/workspace/messages/message-group.tsx`)
- The `FlipDisplay` component wraps the last tool call to animate transitions when the last tool call changes during streaming (`frontend/src/components/workspace/messages/message-group.tsx`)

## Dependencies
- `streamdown` — Streaming markdown renderer with remark/rehype plugin support
- `remark-gfm`, `remark-math` — GitHub Flavored Markdown and math support
- `rehype-raw`, `rehype-katex` — Raw HTML passthrough and KaTeX math rendering
- `@/components/ai-elements/chain-of-thought` — ChainOfThought UI primitives for reasoning display
- `@/components/ai-elements/code-block` — Code block with syntax highlighting
