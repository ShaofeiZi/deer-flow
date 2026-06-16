## 24fe5fbd 2026-04-18 imhaoran
fix(mcp): prevent RuntimeError from escaping except block in get_cach… (#2252)

* fix(mcp): prevent RuntimeError from escaping except block in get_cached_mcp_tools

When `asyncio.get_event_loop()` raises RuntimeError and the fallback
`asyncio.run()` also fails, the exception escapes unhandled because
Python does not route exceptions raised inside an `except` block to
sibling `except` clauses. Wrap the fallback call in its own try/except
so failures are logged and the function returns [] as intended.

* fix: use logger.exception to preserve stack traces on MCP init failure

- `backend/packages/harness/deerflow/mcp/cache.py`

## f394c0d8 2026-04-25 IECspace
feat(mcp): support custom tool interceptors via extensions_config.json (#2451)

* feat(mcp): support custom tool interceptors via extensions_config.json

Add a generic extension point for registering custom MCP tool
interceptors through `extensions_config.json`. This allows downstream
projects to inject per-request header manipulation, auth context
propagation, or other cross-cutting concerns without modifying
DeerFlow source code.

Interceptors are declared as Python callable paths in a new
`mcpInterceptors` array field and loaded via the existing
`resolve_variable` reflection mechanism:

```json
{
  "mcpInterceptors": [
    "my_package.mcp.auth:build_auth_interceptor"
  ]
}
```

Each entry must resolve to a no-arg builder function that returns an
async interceptor compatible with `MultiServerMCPClient`'s
`tool_interceptors` interface.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* test(mcp): add unit tests for custom tool interceptors

Cover all branches of the mcpInterceptors loading logic:

- valid interceptor loaded and appended to tool_interceptors
- multiple interceptors loaded in declaration order
- builder returning None is skipped
- resolve_variable ImportError logged and skipped
- builder raising exception logged and skipped
- absent mcpInterceptors field is safe (no-op)
- custom interceptors coexist with OAuth interceptor

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* fix(mcp): validate mcpInterceptors type and fix lint warnings

Address review feedback:

1. Validate mcpInterceptors config value before iterating:
   - Accept a single string and normalize to [string]
   - Ignore None silently
   - Log warning and skip for non-list/non-string types

2. Fix ruff F841 lint errors in tests:
   - Rename _make_mock_env to _make_patches, embed mock_client
   - Remove unused `as mock_cls` bindings where not needed
   - Extract _get_interceptors() helper to reduce repetition

3. Add two new test cases for type validation:
   - test_mcp_interceptors_single_string_is_normalized
   - test_mcp_interceptors_invalid_type_logs_warning

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(mcp): validate interceptor return type and fix import mock path

Address review feedback:

1. Validate builder return type with callable() check:
   - callable interceptor → append to tool_interceptors
   - None → silently skip (builder opted out)
   - non-callable → log warning with type name and skip

2. Fix test mock path: resolve_variable is a top-level import in
   tools.py, so mock deerflow.mcp.tools.resolve_variable instead of
   deerflow.reflection.resolve_variable to correctly intercept calls.

3. Add test_custom_interceptor_non_callable_return_logs_warning to
   cover the new non-callable validation branch.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* docs(mcp): add mcpInterceptors example and documentation

- Add mcpInterceptors field to extensions_config.example.json
- Add "Custom Tool Interceptors" section to MCP_SERVER.md with
  configuration format, example interceptor code, and edge case
  behavior notes

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: IECspace <IECspace@users.noreply.github.com>
Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/mcp/tools.py`
  L99: # Load custom interceptors declared in extensions_config.json
  L100: # Format: "mcpInterceptors": ["pkg.module:builder_func", ...]

## bedbf229 2026-05-11 AochenShen99
fix(harness): wrap async-only config tools for sync client execution (#2878)

* fix(harness): wrap async-only config tools for sync clients

* refactor(tools): share async tool sync wrapper

- `backend/packages/harness/deerflow/mcp/tools.py`

## c881d958 2026-05-21 Willem Jiang
fix(mcp): persist MCP sessions across tool calls for stateful servers (#3089)

* fix(mcp): persist MCP sessions across tool calls for stateful servers

  MCP tools loaded via langchain-mcp-adapters created a new session on
  every call, causing stateful servers like Playwright to lose browser
  state (pages, forms) between consecutive tool invocations within the
  same thread.

  Add MCPSessionPool that maintains persistent sessions scoped by
  (server_name, thread_id). Tool calls within the same thread now reuse
  the same MCP session, preserving server-side state. Sessions are evicted
  in LRU order (max 256) and cleaned up on cache invalidation.

  Fixes #3054

* fix(sandbox): add group/other read permissions to uploaded files for Docker sandbox (#3127)

  When using AIO sandbox with LocalContainerBackend, uploaded files are
  created with 0o600 (owner-only) permissions by the gateway process
  running as root. The sandbox process inside the Docker container runs
  as a non-root user and cannot read these bind-mounted files, causing
  a "Permission denied" error on read_file.

  Add `needs_upload_permission_adjustment` attribute to SandboxProvider
  (default True) to indicate that uploaded files need chmod adjustment.
  LocalSandboxProvider opts out (same user). A new `_make_file_sandbox_readable`
  function adds S_IRGRP | S_IROTH bits after files are written, changing
  permissions from 0o600 to 0o644 so the sandbox can read the uploads.

* fix(mcp): address review comments on session pool and tools

- _extract_thread_id: return "default" instead of stringifying None
  when get_config() returns no thread_id
- call_with_persistent_session: fix **arguments annotation from
  dict[str,Any] to Any
- Replace private _convert_call_tool_result import with a local
  implementation that handles all MCP content block types
- _make_session_pool_tool: accept tool_interceptors and apply the
  configured interceptor chain on every call (preserving OAuth and
  custom interceptors)
- MCPSessionPool: replace asyncio.Lock with threading.Lock; restructure
  get/close methods to never await while holding the lock; add
  close_all_sync() that closes sessions on their owning event loops
- reset_mcp_tools_cache: use pool.close_all_sync() instead of
  asyncio.run-in-thread to close sessions deterministically
- test: add test_session_pool_tool_sync_wrapper_path_is_safe covering
  tool invocation via the sync wrapper (tool.func) path

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/9e7f9e7f-1d2b-464a-b3b7-7f1649b74122

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* fix(mcp): extract SESSION_CLOSE_TIMEOUT to class constant

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/9e7f9e7f-1d2b-464a-b3b7-7f1649b74122

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* Potential fix for pull request finding 'Empty except'

Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>

- `backend/packages/harness/deerflow/mcp/cache.py`
  L145: # Close persistent sessions – they will be recreated by the next
  L146: # get_mcp_tools() call with the (possibly updated) connection config.
- `backend/packages/harness/deerflow/mcp/session_pool.py`
  L1: """Persistent MCP session pool for stateful tool calls.
  L11: """
  L27: """Manages persistent MCP sessions scoped by ``(server_name, scope_key)``."""
  L38: # threading.Lock is not bound to any event loop, so it is safe to
  L39: # acquire from both async paths and sync/worker-thread paths.
  L48: """Get or create a persistent MCP session.
  L61: """
  L65: # Phase 1: inspect/mutate the registry under the thread lock (no awaits).
  L73: # Session belongs to a different event loop – evict it.
  L79: # Evict LRU entries when at capacity.
  L87: # Phase 2: async cleanup outside the lock so we never await while holding it.
  L100: # Phase 3: register the new session under the lock.
  L107: # ------------------------------------------------------------------
  L108: # Cleanup helpers
  L109: # ------------------------------------------------------------------
  L112: """Close a single context manager (must be called WITHOUT the lock)."""
  L119: """Close all sessions for a given scope (e.g. thread_id)."""
  L130: """Close all sessions for a given server."""
  L141: """Close every managed session."""
  L150: """Close all sessions using their owning event loops (synchronous).
  ... (truncated)
- `backend/packages/harness/deerflow/mcp/tools.py`
  L1: """Load MCP tools using langchain-mcp-adapters with persistent sessions."""
  L23: """Extract thread_id from the injected tool runtime or LangGraph config."""
  L41: """Convert an MCP CallToolResult to the LangChain ``content_and_artifact`` format.
  L45: """
  L51: # Pass ToolMessage through directly (interceptor short-circuit).
  L55: # Pass LangGraph Command through directly when langgraph is installed.
  L62: # langgraph is optional; if unavailable, continue with standard MCP content conversion.
  L65: # Convert MCP content blocks to LangChain content blocks.
  L112: """Wrap an MCP tool so it reuses a persistent session from the pool.
  L120: """
  L121: # Strip the server-name prefix to recover the original MCP tool name.
  L248: # Get all tools from all servers (discovers tool definitions via
  L249: # temporary sessions – the persistent-session wrapping is applied below).
  L253: # Wrap each tool with persistent-session logic.
  L267: # Patch tools to support sync invocation, as deerflow client streams synchronously

## 162fb214 2026-05-27 Willem Jiang
fix(mcp): skip session pooling for HTTP/SSE transports to avoid anyioRuntimeError (#3203) (#3224)

* fix(mcp): skip session pooling for HTTP/SSE transports to avoid anyio RuntimeError (#3203)

  HTTP/SSE transports use anyio.TaskGroup internally for streamable
  connections. These task groups have cancel scopes bound to the async task
  that created them, so closing a pooled session from a different task
  raises RuntimeError. Restrict session pooling to stdio transports only.

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* docs: clarify MCP pooling applies only to stdio tools

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/2dd9881d-54c6-45fd-90bc-154a09e29841

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

---------

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>
Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/mcp/tools.py`
  L1: """Load MCP tools using langchain-mcp-adapters with stdio session pooling."""
  L256: # Only pool stdio sessions. HTTP/SSE transports use anyio TaskGroups
  L257: # internally which cannot be closed from a different async task, so
  L258: # pooling them causes RuntimeError on cleanup (see #3203).

## 872079b8 2026-05-29 Eilen Shin
docs: clean standalone LangGraph server remnants (#3301)

- `backend/packages/harness/deerflow/mcp/cache.py`

## 3ae82dc6 2026-06-03 zhongli-sz
fix(mcp): add auth interceptor with channel user_id and keep header propagation to mcp tools (#3294)

* 修复channel中的user_id传递到interceptor中的bug, mcp可通过header传递user_id到mcp工具

Co-authored-by: Cursor <cursoragent@cursor.com>

* fix(channel,mcp,gateway): normalize channel user_id and add regression tests

Normalize external channel user ids into filesystem-safe runtime context while preserving raw channel_user_id, and document gateway user_id propagation semantics. Add regression coverage for channel user_id context mapping, gateway user_id precedence/internal-role behavior, and MCP interceptor header forwarding via meta.headers.

Co-authored-by: Cursor <cursoragent@cursor.com>

* fix(auth,mcp): harden user id normalization and header handling

Increase sanitized user-id digest suffix to 16 hex chars, replace internal system role magic string with a shared constant, and harden MCP header forwarding with Mapping type checks. Add regression tests for empty channel user_id handling, unsupported header types, and updated digest length behavior.

Co-authored-by: Cursor <cursoragent@cursor.com>

---------

Co-authored-by: zhongli <335302680@qq.com>
Co-authored-by: Cursor <cursoragent@cursor.com>

- `backend/packages/harness/deerflow/mcp/tools.py`
  L141: # Preserve interceptor-injected headers for stdio MCP calls by
  L142: # forwarding them through MCP call meta.

## d8b728f7 2026-06-07 Ryker_Feng
fix(mcp): close stdio sessions on their owning loop to avoid cross-task cancel-scope error (#3379) (#3392)

* fix(mcp): close stdio sessions on their owning loop to avoid cross-task cancel-scope error (#3379)

Adopt an owner-task lifecycle for pooled MCP ClientSessions so each
session is entered, initialized, and exited within a single asyncio task
on its owning event loop. This eliminates the anyio "Attempted to exit
cancel scope in a different task than it was entered in" RuntimeError
that surfaced when stdio MCP tools were used via the sync tool wrapper
(which spins up and tears down event loops across tasks).

Also harden the pool lifecycle:
- track in-flight session creation per (server, scope) to dedupe
  concurrent get_session() calls for the same key
- make close_scope/close_server/close_all/close_all_sync cover both
  established entries and in-flight creations so sessions cannot be
  resurrected or leaked after close
- handle cross-loop preemption of an in-flight creation by cancelling
  the stale owner task instead of only signalling it
- define close_all_sync() semantics for a running loop on the current
  thread (signal-only, async completion) and route reset_mcp_tools_cache
  through a deterministic async close in that case

* fix(mcp): avoid reset deadlock on running loop cache reset

* fix(mcp): address session pool review feedback

- `backend/packages/harness/deerflow/mcp/__init__.py`
- `backend/packages/harness/deerflow/mcp/cache.py`
  L146: #
  L147: # close_all_sync() already picks the correct strategy per owning loop:
  L148: #   * sessions owned by the *current* running loop are only *signalled*
  L149: #     (their owner task runs __aexit__ once the loop regains control –
  L150: #     this is correct and leak-free, since the loop keeps the task alive),
  L151: #   * sessions on other threads' loops are torn down deterministically,
  L152: #   * idle/closed loops are handled or skipped.
  L153: # We deliberately do NOT try to synchronously wait for the current running
  L154: # loop to finish teardown here: that is a self-deadlock (the loop can only
  L155: # run the teardown after this synchronous call returns control to it).
- `backend/packages/harness/deerflow/mcp/session_pool.py`
  L54: # Each entry: (session, owning_loop, owner_task, close_event).
  L64: # In-flight creations, keyed by (server, scope). Lets concurrent callers
  L65: # on the same loop share a single creation instead of each spawning a
  L66: # duplicate session. Value: (loop, ready_future, owner_task, close_event).
  L80: # ------------------------------------------------------------------
  L81: # Session owner task
  L82: # ------------------------------------------------------------------
  L90: """Own a single MCP session for its entire lifetime.
  L96: """
  L103: # Never entered the cancel scope, so there is nothing to exit.
  L108: # The context manager is now entered. From here on __aexit__ MUST run in
  L109: # this task — on init failure, on cancellation, or on the close signal —
  L110: # to satisfy anyio's same-task cancel-scope requirement and to avoid
  L111: # leaking the session/subprocess.
  L150: # Decide one of three outcomes atomically: return an existing session,
  L151: # join an in-flight creation, or become the creator for this key.
  L152: # Each item: (loop, owner_task, close_event, cancel). ``cancel`` is True
  L153: # for in-flight creations, whose owner may be blocked inside
  L154: # ``initialize()`` where close_evt cannot wake it — it must be cancelled.
  L166: # Session belongs to a different/closed event loop – evict it.
  ... (truncated)

