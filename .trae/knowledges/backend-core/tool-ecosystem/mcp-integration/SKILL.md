---
name: knowledge-backend-core-tool-ecosystem-mcp-integration
description: >
  Covers MCP (Model Context Protocol) integration: MultiServerMCPClient, MCPSessionPool
  with owner-task pattern, MCP tools cache with mtime-based staleness, OAuth interceptor
  support, custom interceptor loading, and persistent session management for stdio transports.
  Navigate when: adding MCP servers, debugging session pool issues, configuring MCP server
  connections, troubleshooting tool loading, or working on OAuth interceptors. This is a
  component-like module consumed by tool ecosystem, agent orchestration, and runtime engine.
  Excludes: builtin tools (see ../builtin-tools/), community tools (see ../community-tools/).
  Keywords: MCP, Model Context Protocol, MultiServerMCPClient, MCPSessionPool, session_pool,
  owner_task, LRU eviction, anyio cancel-scope, mtime cache, OAuth interceptor,
  custom interceptor, stdio transport, persistent session, build_server_params,
  build_servers_config, get_mcp_tools, MCP tools cache.
---

## Module Structure

MCP integration connects DeerFlow agents to external tools via the Model Context Protocol.
It manages persistent session pools for stdio transports, caches tool schemas with mtime-based
staleness detection, and supports OAuth and custom interceptors.

### Directory Layout
- `backend/packages/harness/deerflow/mcp/__init__.py` — Public API: cache, client, tools
- `backend/packages/harness/deerflow/mcp/tools.py` — `get_mcp_tools()` loads tools via MultiServerMCPClient
- `backend/packages/harness/deerflow/mcp/client.py` — `build_server_params()`, `build_servers_config()`
- `backend/packages/harness/deerflow/mcp/session_pool.py` — MCPSessionPool with owner-task pattern, LRU eviction
- `backend/packages/harness/deerflow/mcp/cache.py` — MCP tools cache with mtime-based staleness
- `backend/packages/harness/deerflow/tools/mcp_metadata.py` — MCP tool metadata tagging

### Key Entry Points
- `get_mcp_tools()` in `backend/packages/harness/deerflow/mcp/tools.py` — Load all MCP tools
- `MCPSessionPool` in `backend/packages/harness/deerflow/mcp/session_pool.py` — Persistent session management
- `build_server_params()` in `backend/packages/harness/deerflow/mcp/client.py` — Build MCP server connection params
- `MCPToolsCache` in `backend/packages/harness/deerflow/mcp/cache.py` — Tool schema cache

## API Surface

### MCPSessionPool
- `get_session(server_name)` — Acquire or create a session for a server, tied to the calling task
- `release_session(server_name)` — Release a session back to the pool
- `cleanup()` — Close all sessions and clear the pool
- `evict_lru()` — Evict least-recently-used sessions when pool exceeds cap (256)

### MCPToolsCache
- `get_tools()` — Get cached tools, refreshing if mtime indicates staleness
- `reset()` — Clear the cache and cleanup session pool
- `lazy_init` — Defer initialization until first access

### build_server_params
- `build_server_params(server_config)` — Build `ServerParameters` for a single MCP server
- `build_servers_config(app_config)` — Build the full servers config dict for MultiServerMCPClient

## Usage Examples

### Loading MCP tools
```python
from deerflow.mcp.tools import get_mcp_tools

tools = await get_mcp_tools(app_config=app_config)
```

### Building server connection parameters
```python
from deerflow.mcp.client import build_server_params

params = build_server_params(server_config)
# Returns ServerParameters with command, args, env for stdio transport
```

## Gotchas
- MCPSessionPool uses an owner-task pattern for anyio cancel-scope compliance — sessions are tied to the creating asyncio task and must be released by the same task (`backend/packages/harness/deerflow/mcp/session_pool.py`)
- Session pool has LRU eviction with cap 256 — exceeding this causes the least-recently-used session to be closed and evicted (`backend/packages/harness/deerflow/mcp/session_pool.py`)
- Cross-loop session management: sessions created in one event loop cannot be reused in another — the pool handles this by detecting loop mismatches (`backend/packages/harness/deerflow/mcp/session_pool.py`)
- MCP tools cache uses mtime-based staleness detection — if the MCP server config file hasn't changed, cached tools are returned without reconnecting (`backend/packages/harness/deerflow/mcp/cache.py`)
- Inflight creation deduplication: if two tasks request a session for the same server simultaneously, only one creates the session while the other waits (`backend/packages/harness/deerflow/mcp/session_pool.py`)

## Architecture
- MCP tools are loaded via `MultiServerMCPClient` from `langchain_mcp_adapters`, which handles the MCP protocol handshake (`backend/packages/harness/deerflow/mcp/tools.py`)
- Stdio transport tools are wrapped with persistent session pooling — the session is kept alive across multiple tool calls rather than reconnecting each time (`backend/packages/harness/deerflow/mcp/tools.py`)
- OAuth interceptor support: MCP servers can use OAuth authentication with custom token refresh logic (`backend/packages/harness/deerflow/mcp/tools.py`)
- Custom interceptors can be loaded from config for advanced request/response manipulation (`backend/packages/harness/deerflow/mcp/tools.py`)

## Decisions
- Persistent session pooling was chosen over per-call connections to reduce latency for stdio-based MCP servers (`backend/packages/harness/deerflow/mcp/session_pool.py`)
- Owner-task pattern was adopted for anyio cancel-scope compliance — sessions are scoped to the creating task to prevent leaks on cancellation (`backend/packages/harness/deerflow/mcp/session_pool.py`)
- Mtime-based caching was chosen over TTL-based caching because MCP server configs change infrequently and mtime provides a reliable staleness signal (`backend/packages/harness/deerflow/mcp/cache.py`)

## Patterns
- Session pool lifecycle: `get_session()` → use → `release_session()` → (optional) `cleanup()` (`backend/packages/harness/deerflow/mcp/session_pool.py`)
- Cache staleness: check mtime of config file → if changed, reconnect and refresh tools → cache new tools with new mtime (`backend/packages/harness/deerflow/mcp/cache.py`)
- Lazy initialization: `MCPToolsCache` defers server connection until `get_tools()` is first called (`backend/packages/harness/deerflow/mcp/cache.py`)

## Consumer Analysis
- Tool ecosystem (tools/tools.py) — primary consumer: calls `get_mcp_tools()` during `get_available_tools()` assembly
- Agent orchestration (agents/lead_agent/agent.py) — consumes MCP tools indirectly via `get_available_tools()` → `assemble_deferred_tools()`
- Deferred tool search (tools/builtins/tool_search.py) — consumes MCP tools via `DeferredToolCatalog` for runtime discovery
- Runtime engine — uses MCP tools cache reset during provider reconfiguration

## Conventions
- MCP server configs are defined in the app config under `mcp_servers` (`backend/packages/harness/deerflow/mcp/client.py`)
- MCP tools are tagged with `deerflow_mcp` metadata for identification by the deferred tool system (`backend/packages/harness/deerflow/tools/mcp_metadata.py`)
- Session pool capacity is hardcoded at 256 (`backend/packages/harness/deerflow/mcp/session_pool.py`)

## Dependencies
- `langchain_mcp_adapters` for `MultiServerMCPClient` (`backend/packages/harness/deerflow/mcp/tools.py`)
- `mcp` SDK for low-level MCP protocol types (`backend/packages/harness/deerflow/mcp/client.py`)
- `deerflow.config.app_config` for MCP server configuration (`backend/packages/harness/deerflow/mcp/client.py`)
