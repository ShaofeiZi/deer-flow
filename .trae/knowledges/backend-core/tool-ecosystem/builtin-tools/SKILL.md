---
name: knowledge-backend-core-tool-ecosystem-builtin-tools
description: >
  Covers builtin tools: task (subagent delegation), tool_search (deferred MCP tool discovery),
  clarification (ask_clarification), setup_agent, update_agent, view_image, present_file,
  invoke_acp_agent, and skill_manage_tool. Navigate when: modifying builtin tool behavior,
  adding new builtin tools, debugging tool search, or understanding task delegation flow.
  Excludes: community tools (see ../community-tools/), MCP integration (see ../mcp-integration/).
  Keywords: task, tool_search, ask_clarification, setup_agent, update_agent, view_image,
  present_file, invoke_acp_agent, skill_manage_tool, DeferredToolCatalog, assemble_deferred_tools,
  builtin tools, tool groups.
---

## Module Structure

Builtin tools are the core tools bundled with DeerFlow. They provide subagent delegation,
deferred tool discovery, user clarification, agent setup/update, image viewing, file
presentation, and ACP agent invocation.

### Directory Layout
- `backend/packages/harness/deerflow/tools/builtins/__init__.py` — Public exports for builtin tools
- `backend/packages/harness/deerflow/tools/builtins/task_tool.py` — `task` tool for subagent delegation
- `backend/packages/harness/deerflow/tools/builtins/tool_search.py` — `tool_search` for deferred MCP tool discovery
- `backend/packages/harness/deerflow/tools/builtins/clarification_tool.py` — `ask_clarification` tool
- `backend/packages/harness/deerflow/tools/builtins/setup_agent_tool.py` — `setup_agent` for bootstrap agent creation
- `backend/packages/harness/deerflow/tools/builtins/update_agent_tool.py` — `update_agent` for custom agent config updates
- `backend/packages/harness/deerflow/tools/builtins/view_image_tool.py` — `view_image` for image display
- `backend/packages/harness/deerflow/tools/builtins/present_file_tool.py` — `present_file` for file presentation
- `backend/packages/harness/deerflow/tools/builtins/invoke_acp_agent_tool.py` — `invoke_acp_agent` for ACP agent calls
- `backend/packages/harness/deerflow/tools/skill_manage_tool.py` — Skill management tool (lazy import)

### Key Entry Points
- `task` tool in `backend/packages/harness/deerflow/tools/builtins/task_tool.py` — Subagent delegation
- `build_tool_search_tool()` in `backend/packages/harness/deerflow/tools/builtins/tool_search.py` — Deferred tool search factory
- `assemble_deferred_tools()` in `backend/packages/harness/deerflow/tools/builtins/tool_search.py` — Catalog + tool assembly
- `setup_agent` in `backend/packages/harness/deerflow/tools/builtins/setup_agent_tool.py` — Bootstrap agent creation
- `update_agent` in `backend/packages/harness/deerflow/tools/builtins/update_agent_tool.py` — Custom agent config update

## Gotchas
- `tool_search` promotions are scoped by catalog hash — a stale persisted promotion from a previous deployment cannot expose a renamed or drifted tool (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`)
- `task` tool silently discards excess parallel calls beyond the concurrency limit — the model must count sub-tasks before launching (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)
- `setup_agent` is only available to the bootstrap agent — the default agent and custom agents do not see this tool (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- `update_agent` is only available to custom agents (those with an agent_name) — the default agent does not see this tool (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- `skill_manage_tool` is lazily imported to avoid circular dependencies — it's imported inside `get_available_tools()` (`backend/packages/harness/deerflow/tools/__init__.py`)

## Architecture
- DeferredToolCatalog is an immutable, frozen dataclass that holds all deferred tools and provides search via regex matching (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`)
- `assemble_deferred_tools()` splits a tool list into active tools (non-MCP) and deferred tools (MCP-tagged), builds a catalog, and creates the `tool_search` tool as a closure over the catalog (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`)
- Task tool manages background subagent execution with polling, cancellation, and cleanup lifecycle (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)
- Clarification tool is intercepted by ClarificationMiddleware before execution — the tool itself is never actually called by ToolNode (`backend/packages/harness/deerflow/tools/builtins/clarification_tool.py`)

## Decisions
- Deferred tool search was introduced to avoid bloating the model context with hundreds of MCP tool schemas (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`)
- `tool_search` supports both regex search and `select:name1,name2` exact selection for efficient tool discovery (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`)
- Subagent token usage is cached by `tool_call_id` and popped by TokenUsageMiddleware for cost attribution (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)

## Patterns
- Tool search catalog is frozen (`frozen=True` without `slots=True`) to allow `@cached_property` fields while maintaining immutability (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`)
- Promotion state is written to graph state via `Command(update={"promoted": ...})` — not via ContextVar (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`)
- Background task lifecycle: create → poll for terminal status → cache result → cleanup (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)

## Conventions
- Tool names are lowercase with underscores: `task`, `tool_search`, `ask_clarification`, `setup_agent`, `update_agent` (`backend/packages/harness/deerflow/tools/builtins/`)
- Tool functions use `@tool` decorator with `Runtime` type annotation (`backend/packages/harness/deerflow/tools/builtins/`)
- Deferred tools are identified by the `deerflow_mcp` metadata tag on the tool object (`backend/packages/harness/deerflow/tools/mcp_metadata.py`)

## Dependencies
- LangChain `@tool` decorator and `BaseTool` for tool definitions (`backend/packages/harness/deerflow/tools/builtins/`)
- LangGraph `Command` for state updates from tools (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`)
- `deerflow.subagents` for subagent execution in task tool (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)
