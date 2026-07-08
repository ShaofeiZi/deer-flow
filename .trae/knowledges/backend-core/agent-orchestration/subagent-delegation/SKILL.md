---
name: knowledge-backend-core-agent-orchestration-subagent-delegation
description: >
  Covers subagent delegation: SubagentConfig, SubagentExecutor, subagent registry,
  task tool, token usage bucketing, and concurrent subagent limits. Navigate when:
  adding subagent types, modifying subagent execution, debugging task delegation,
  configuring subagent concurrency, or working on subagent token tracking.
  Excludes: lead agent factory (see ../lead-agent/), middleware chain (see ../middleware-chain/).
  Keywords: subagent, task, task_tool, SubagentConfig, SubagentExecutor, SubagentResult,
  SubagentStatus, get_subagent_config, get_available_subagent_names, subagent registry,
  max_concurrent_subagents, subagent token usage, resolve_subagent_model_name.
---

## Module Structure

Subagent delegation enables the lead agent to decompose complex tasks and dispatch them
to specialized subagents for parallel execution. The system includes a configurable registry,
an executor with background task management, and a task tool that the lead agent calls.

### Directory Layout
- `backend/packages/harness/deerflow/subagents/__init__.py` — Public API: SubagentConfig, SubagentExecutor, SubagentResult, registry functions
- `backend/packages/harness/deerflow/subagents/config.py` — SubagentConfig dataclass with model resolution
- `backend/packages/harness/deerflow/subagents/executor.py` — SubagentExecutor with SubagentStatus enum, background task lifecycle
- `backend/packages/harness/deerflow/subagents/registry.py` — Subagent registry with config layering
- `backend/packages/harness/deerflow/tools/builtins/task_tool.py` — `task` tool implementation for subagent delegation

### Key Entry Points
- `get_subagent_config(name)` in `backend/packages/harness/deerflow/subagents/registry.py` — Look up subagent configuration
- `get_available_subagent_names()` in `backend/packages/harness/deerflow/subagents/registry.py` — List all registered subagent types
- `SubagentExecutor` in `backend/packages/harness/deerflow/subagents/executor.py` — Executes subagent runs
- `task` tool in `backend/packages/harness/deerflow/tools/builtins/task_tool.py` — The tool the lead agent calls to delegate work

## Gotchas
- SubagentLimitMiddleware silently discards excess `task` calls beyond the concurrency limit — the model must count its sub-tasks before launching (`backend/packages/harness/deerflow/agents/middlewares/subagent_limit_middleware.py`)
- Subagent token usage is cached by `tool_call_id` in `_subagent_usage_cache` and popped by TokenUsageMiddleware — if the middleware doesn't run, usage data is lost (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)
- Host bash is gated for subagents: `is_host_bash_allowed()` returns False for local sandbox, and the `bash` subagent type is excluded from available names when bash is unavailable (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)
- Background subagent tasks are polled with `asyncio.sleep(5)` intervals — long-running subagents may block the lead agent's response for multiples of 5 seconds (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)
- Cancelled subagents are cleaned up via a deferred background task that keeps polling until the subagent reaches a terminal state (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)

## Architecture
- Subagent registry uses config layering: built-in types → `custom_agents` config → per-agent overrides, with later layers overriding earlier ones (`backend/packages/harness/deerflow/subagents/registry.py`)
- Subagent model resolution: can inherit the lead agent's model or specify an explicit model name in SubagentConfig (`backend/packages/harness/deerflow/subagents/config.py`)
- SubagentExecutor manages background asyncio.Tasks with status tracking (PENDING → RUNNING → COMPLETED/FAILED/CANCELLED/TIMED_OUT) (`backend/packages/harness/deerflow/subagents/executor.py`)
- Token usage is bucketed separately: lead agent tokens, subagent tokens, and middleware tokens are tracked independently for cost attribution (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`, `git:9892a7d4`)

## Decisions
- Subagent token usage is bucketed separately from lead agent tokens for cost attribution (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`, `git:9892a7d4`)
- Subagent system_prompt was consolidated into the lead agent's prompt rather than injected separately to reduce token overhead (`git:813d3c94`)
- Host bash is disabled for subagents when using local sandbox — only AioSandboxProvider allows isolated shell access for subagents (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)

## Patterns
- Subagent descriptions are dynamically built from the registry, mirroring Codex's pattern where `agent_type_description` lists all registered roles (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)
- Background task lifecycle: create → poll for terminal status → cache result → cleanup (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)
- Token usage caching uses a module-level dict keyed by `tool_call_id` with pop-on-read semantics (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)

## Conventions
- Subagent type names are lowercase hyphenated: `general-purpose`, `bash`, plus custom names from config (`backend/packages/harness/deerflow/subagents/registry.py`)
- `SubagentStatus` enum values: PENDING, RUNNING, COMPLETED, FAILED, CANCELLED, TIMED_OUT (`backend/packages/harness/deerflow/subagents/executor.py`)
- `SubagentResult` is a dataclass carrying status, output, error, token usage, and timing info (`backend/packages/harness/deerflow/subagents/executor.py`)

## Dependencies
- LangGraph for subagent graph execution and streaming (`backend/packages/harness/deerflow/subagents/executor.py`)
- `deerflow.models.create_chat_model` for subagent model creation (`backend/packages/harness/deerflow/subagents/executor.py`)
- `deerflow.sandbox.security` for host bash gating (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`)
