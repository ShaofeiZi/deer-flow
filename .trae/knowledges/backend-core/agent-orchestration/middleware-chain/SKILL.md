---
name: knowledge-backend-core-agent-orchestration-middleware-chain
description: >
  Covers the middleware chain: ordering, individual middleware behaviors, chain assembly,
  and the AgentMiddleware extension pattern. Navigate when: adding a new middleware,
  debugging middleware ordering issues, understanding middleware lifecycle hooks,
  modifying existing middleware behavior, or troubleshooting state propagation.
  Excludes: sandbox middleware (see ../../sandbox-execution/), memory middleware (see ../../memory-system/).
  Keywords: AgentMiddleware, build_middlewares, before_model, after_model, wrap_model_call,
  DynamicContextMiddleware, SkillActivationMiddleware, ClarificationMiddleware,
  DeferredToolFilterMiddleware, LoopDetectionMiddleware, SafetyFinishReasonMiddleware,
  TitleMiddleware, TodoMiddleware, TokenUsageMiddleware, ViewImageMiddleware,
  SubagentLimitMiddleware, DanglingToolCallMiddleware, ThreadDataMiddleware,
  UploadsMiddleware, ToolErrorHandlingMiddleware, ToolOutputBudgetMiddleware.
---

## Module Structure

The middleware chain is the extensibility backbone of the agent. Each middleware hooks into
the agent lifecycle (before model call, after model call, wrap model call) and can inspect
or modify state, messages, and tool calls. The chain is assembled deterministically with
documented ordering constraints.

### Directory Layout
- `backend/packages/harness/deerflow/agents/middlewares/__init__.py` — Public middleware exports
- `backend/packages/harness/deerflow/agents/middlewares/clarification_middleware.py` — Intercepts `ask_clarification` tool calls, presents questions to user
- `backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py` — Injects current date and memory as `<system-reminder>` HumanMessages
- `backend/packages/harness/deerflow/agents/middlewares/skill_activation_middleware.py` — Loads full SKILL.md on `/skill-name` slash commands
- `backend/packages/harness/deerflow/agents/middlewares/deferred_tool_filter_middleware.py` — Hides deferred tool schemas from model until promoted via tool_search
- `backend/packages/harness/deerflow/agents/middlewares/loop_detection_middleware.py` — Detects and breaks repetitive tool call loops
- `backend/packages/harness/deerflow/agents/middlewares/safety_finish_reason_middleware.py` — Suppresses tool execution when provider safety-terminated the response
- `backend/packages/harness/deerflow/agents/middlewares/title_middleware.py` — Generates conversation title after first exchange
- `backend/packages/harness/deerflow/agents/middlewares/todo_middleware.py` — Provides `write_todos` tool for plan-mode task tracking
- `backend/packages/harness/deerflow/agents/middlewares/token_usage_middleware.py` — Tracks and buckets token usage (lead agent, subagent, middleware)
- `backend/packages/harness/deerflow/agents/middlewares/view_image_middleware.py` — Injects image details into messages for vision-capable models
- `backend/packages/harness/deerflow/agents/middlewares/subagent_limit_middleware.py` — Truncates excess parallel task calls beyond concurrency limit
- `backend/packages/harness/deerflow/agents/middlewares/dangling_tool_call_middleware.py` — Patches missing ToolMessages before model sees history
- `backend/packages/harness/deerflow/agents/middlewares/thread_data_middleware.py` — Ensures thread_id is available in state
- `backend/packages/harness/deerflow/agents/middlewares/uploads_middleware.py` — Processes uploaded files
- `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py` — Converts tool exceptions to ToolMessages
- `backend/packages/harness/deerflow/agents/middlewares/tool_output_budget_middleware.py` — Truncates oversized tool outputs
- `backend/packages/harness/deerflow/agents/middlewares/safety_termination_detectors.py` — Detects safety-related response terminations
- `backend/packages/harness/deerflow/agents/middlewares/tool_call_metadata.py` — Attaches metadata to tool calls
- `backend/packages/harness/deerflow/agents/middlewares/sandbox_audit_middleware.py` — Audits sandbox operations
- `backend/packages/harness/deerflow/agents/middlewares/llm_error_handling_middleware.py` — Handles LLM call errors

### Key Entry Points
- `build_middlewares()` in `backend/packages/harness/deerflow/agents/lead_agent/agent.py` — Assembles the full middleware chain
- `AgentMiddleware` base class from LangChain — All middleware extends this
- `build_lead_runtime_middlewares()` in `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py` — Runtime tool error handling

## Gotchas
- Middleware ordering is critical and documented in `build_middlewares()` — changing the order can break state propagation (e.g., ThreadDataMiddleware must be before SandboxMiddleware) (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- ClarificationMiddleware must always be last in the chain — it intercepts clarification requests after all other middleware have processed (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- SafetyFinishReasonMiddleware is registered after custom middlewares so LangChain's reverse-order `after_model` dispatch runs Safety first — cleared tool_calls then flow through Loop/Subagent accounting without firing extra alarms (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- ViewImageMiddleware is only added when the resolved model supports vision — checked via `model_config.supports_vision` at build time (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- DynamicContextMiddleware injects context as a HumanMessage with a frozen-snapshot pattern — once injected, the context is not re-injected on subsequent turns unless the date changes (`backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py`)

## Architecture
- Middleware chain is assembled deterministically: ThreadData → DynamicContext → SkillActivation → Summarization → TodoList → TokenUsage → Title → Memory → ViewImage → DeferredToolFilter → SubagentLimit → LoopDetection → Custom → SafetyFinishReason → Clarification (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Each middleware extends `AgentMiddleware[StateType]` and can override `before_model`, `after_model`, or `wrap_model_call` hooks (`backend/packages/harness/deerflow/agents/middlewares/`)
- LangChain dispatches middleware in forward order for `before_model` and reverse order for `after_model` — this affects where SafetyFinishReasonMiddleware must be placed (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Conditional middleware: TodoList only added when `is_plan_mode=True`, ViewImage only when model supports vision, Summarization only when config enabled, SubagentLimit only when `subagent_enabled=True` (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Decisions
- DynamicContextMiddleware uses a frozen-snapshot pattern: context is injected once as a dedicated HumanMessage and not re-injected on subsequent turns (`backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py`, `git:c1b7f1d1`)
- SkillActivationMiddleware uses deterministic content hashing so retried slash-skill activations replace rather than append the loaded skill content (`backend/packages/harness/deerflow/agents/middlewares/skill_activation_middleware.py`)
- DeferredToolFilterMiddleware scopes promotion state by catalog hash so a stale persisted promotion cannot expose a renamed or drifted tool (`backend/packages/harness/deerflow/agents/middlewares/deferred_tool_filter_middleware.py`)

## Patterns
- Middleware that needs to persist state across turns uses `Command(update=...)` pattern — direct state mutation is not propagated (`backend/packages/harness/deerflow/sandbox/middleware.py`)
- Conditional middleware is gated by config flags checked at build time in `build_middlewares()` (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Middleware with config-driven behavior uses `from_config()` classmethod pattern (e.g., `LoopDetectionMiddleware.from_config()`, `SafetyFinishReasonMiddleware.from_config()`) (`backend/packages/harness/deerflow/agents/middlewares/loop_detection_middleware.py`, `backend/packages/harness/deerflow/agents/middlewares/safety_finish_reason_middleware.py`)

## Conventions
- Middleware files are named `*_middleware.py` and live in `agents/middlewares/` (`backend/packages/harness/deerflow/agents/middlewares/`)
- Each middleware has its own state schema class (e.g., `ClarificationMiddlewareState`) that is compatible with `ThreadState` (`backend/packages/harness/deerflow/agents/middlewares/clarification_middleware.py`)
- Middleware uses `state_schema` class attribute to declare its state type (`backend/packages/harness/deerflow/agents/middlewares/`)

## Dependencies
- LangChain `AgentMiddleware` base class with `AgentState` generic parameter (`backend/packages/harness/deerflow/agents/middlewares/`)
- LangGraph `Command` for state updates across middleware (`backend/packages/harness/deerflow/agents/middlewares/clarification_middleware.py`)
- `deerflow.config.app_config` for feature flag gating (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
