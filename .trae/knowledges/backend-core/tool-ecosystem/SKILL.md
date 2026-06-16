---
name: knowledge-backend-core-tool-ecosystem
description: >
  Covers the tool ecosystem: tool assembly, builtin tools, community tools, MCP integration,
  tool search, deferred tool discovery, and tool policy filtering. Navigate when: adding
  new tools, integrating MCP servers, debugging tool availability, configuring tool groups,
  or working on deferred tool search.
  Excludes: sandbox tools (see ../sandbox-execution/sandbox-tools/), skill tools (see ../skills-management/).
  Keywords: get_available_tools, tool assembly, MCP, MultiServerMCPClient, MCPSessionPool,
  tool_search, DeferredToolCatalog, deferred tools, tool groups, community tools,
  builtin tools, ACP agents, tool deduplication.
---

## Module Structure

The tool ecosystem assembles and manages all tools available to the agent. Tools come from
three sources: builtins (bundled with DeerFlow), community integrations (third-party APIs),
and MCP servers (Model Context Protocol). A deferred tool search system allows the agent to
discover MCP tools at runtime without bloating the model context.

### Directory Layout
- `backend/packages/harness/deerflow/tools/__init__.py` — Public API: get_available_tools
- `backend/packages/harness/deerflow/tools/tools.py` — `get_available_tools()` assembles tools from all sources
- `backend/packages/harness/deerflow/tools/types.py` — Runtime type alias to prevent Pydantic warnings
- `backend/packages/harness/deerflow/tools/sync.py` — Sync wrapper for async tools
- `backend/packages/harness/deerflow/tools/skill_manage_tool.py` — Skill management tool
- `backend/packages/harness/deerflow/tools/mcp_metadata.py` — MCP tool metadata tagging
- `backend/packages/harness/deerflow/tools/builtins/` — Builtin tools (clarification, task, tool_search, etc.)
- `backend/packages/harness/deerflow/mcp/` — MCP integration (client, session pool, cache, tools)
- `backend/packages/harness/deerflow/community/` — Community tool integrations (ddg_search, exa, firecrawl, etc.)

### Key Entry Points
- `get_available_tools()` in `backend/packages/harness/deerflow/tools/tools.py` — Main tool assembly function
- `get_mcp_tools()` in `backend/packages/harness/deerflow/mcp/tools.py` — MCP tool loading
- `build_tool_search_tool()` in `backend/packages/harness/deerflow/tools/builtins/tool_search.py` — Deferred tool search
- `filter_tools_by_skill_allowed_tools()` in `backend/packages/harness/deerflow/skills/tool_policy.py` — Skill-based tool filtering

## Gotchas
- The `Runtime` type alias (`ToolRuntime[dict[str, Any], ThreadState]`) is required to prevent Pydantic serialization warnings on tool state fields (`backend/packages/harness/deerflow/tools/types.py`, `git:7de9b582`)
- Tool deduplication is by name — if a builtin and an MCP tool share the same name, only one survives (`backend/packages/harness/deerflow/tools/tools.py`)
- Host bash tools are gated by sandbox provider type — they are excluded from `get_available_tools()` when using local sandbox (`backend/packages/harness/deerflow/tools/tools.py`)
- MCP tools use a persistent session pool with owner-task pattern — sessions must be properly released or they leak (`backend/packages/harness/deerflow/mcp/session_pool.py`)
- Tool search promotions must be preserved across re-entrant graph calls; promotion state rides on per-thread graph state, not ContextVar (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`, `git:f1a0ab69`)

## Architecture
- Tool assembly pipeline: config-defined tools → MCP cache tools → ACP agent tools → deduplication by name → host bash gating → sync wrapper attachment (`backend/packages/harness/deerflow/tools/tools.py`)
- MCP integration uses `MultiServerMCPClient` from langchain_mcp_adapters with persistent session pooling for stdio transports (`backend/packages/harness/deerflow/mcp/tools.py`)
- Deferred tool discovery: MCP tools are hidden from the model until it searches for them via `tool_search`, which promotes them into graph state (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`)
- Tool groups allow per-agent tool filtering via `agent_config.tool_groups` (`backend/packages/harness/deerflow/tools/tools.py`)

## Decisions
- Deferred tool search was introduced to avoid bloating the model context with hundreds of MCP tool schemas (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`)
- MCP session pooling uses owner-task pattern for anyio cancel-scope compliance — sessions are tied to the creating task (`backend/packages/harness/deerflow/mcp/session_pool.py`)
- Community tools are organized by provider (ddg_search, exa, firecrawl, etc.) with each provider in its own package (`backend/packages/harness/deerflow/community/`)

## Patterns
- Tool functions use `@tool` decorator from LangChain with `Runtime` type annotation for state access (`backend/packages/harness/deerflow/tools/builtins/`)
- MCP tools are tagged with `deerflow_mcp` metadata for identification by the deferred tool system (`backend/packages/harness/deerflow/tools/mcp_metadata.py`)
- Sync wrappers are attached to async tools for compatibility with sync execution paths (`backend/packages/harness/deerflow/tools/sync.py`)

## Conventions
- Builtin tools live in `tools/builtins/`, community tools in `community/<provider>/` (`backend/packages/harness/deerflow/tools/`, `backend/packages/harness/deerflow/community/`)
- Tool names are lowercase with underscores: `tool_search`, `task`, `ask_clarification` (`backend/packages/harness/deerflow/tools/builtins/`)
- MCP tool metadata uses a `deerflow_mcp` tag dict on the tool object (`backend/packages/harness/deerflow/tools/mcp_metadata.py`)

## Dependencies
- `langchain_mcp_adapters` for MCP client integration (`backend/packages/harness/deerflow/mcp/tools.py`)
- LangChain `@tool` decorator and `BaseTool` for tool definitions (`backend/packages/harness/deerflow/tools/`)
- `deerflow.sandbox.security` for host bash gating (`backend/packages/harness/deerflow/tools/tools.py`)

## Child Knowledge Nodes
- `./builtin-tools/SKILL.md` — Builtin tools: task, tool_search, clarification, setup_agent, update_agent, etc.
- `./community-tools/SKILL.md` — Community integrations: ddg_search, exa, firecrawl, serper, tavily, etc.
- `./mcp-integration/SKILL.md` — MCP client, session pool, tool loading, OAuth interceptors
