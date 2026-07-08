---
name: knowledge-backend-core-agent-orchestration
description: >
  Covers agent orchestration: factory assembly, lead agent creation, middleware chain
  composition, prompt template, thread state, and subagent delegation. Navigate when:
  modifying agent creation flow, adding middleware, changing prompt templates, debugging
  agent state, or configuring subagent behavior.
  Excludes: sandbox execution (see ../sandbox-execution/), memory system (see ../memory-system/),
  tool ecosystem (see ../tool-ecosystem/).
  Keywords: create_deerflow_agent, make_lead_agent, build_middlewares, RuntimeFeatures,
  ThreadState, AgentMiddleware, Next, Prev, system_prompt, subagent, task_tool, lead_agent.
---

## Module Structure

Agent orchestration is the central assembly layer that wires together models, tools,
middleware, and prompts into a runnable LangGraph agent. Two factory entry points exist:
`create_deerflow_agent()` (pure-argument) and `make_lead_agent()` (LangGraph graph factory).

### Directory Layout
- `backend/packages/harness/deerflow/agents/__init__.py` — Public API exports; primes enabled-skills cache at import
- `backend/packages/harness/deerflow/agents/factory.py` — `create_deerflow_agent()` with RuntimeFeatures-driven assembly
- `backend/packages/harness/deerflow/agents/features.py` — RuntimeFeatures dataclass, Next/Prev positioning decorators
- `backend/packages/harness/deerflow/agents/thread_state.py` — ThreadState extending AgentState with sandbox, artifacts, todos, etc.
- `backend/packages/harness/deerflow/agents/lead_agent/agent.py` — `make_lead_agent()`, `build_middlewares()`, model resolution
- `backend/packages/harness/deerflow/agents/lead_agent/prompt.py` — SYSTEM_PROMPT_TEMPLATE, skills cache, subagent section builder
- `backend/packages/harness/deerflow/agents/middlewares/` — 20+ middleware implementations
- `backend/packages/harness/deerflow/subagents/` — Subagent config, executor, registry

### Key Entry Points
- `create_deerflow_agent()` in `backend/packages/harness/deerflow/agents/factory.py` — Pure-argument factory for custom agent assembly
- `make_lead_agent()` in `backend/packages/harness/deerflow/agents/lead_agent/agent.py` — LangGraph graph factory for LangGraph Server
- `build_middlewares()` in `backend/packages/harness/deerflow/agents/lead_agent/agent.py` — Public middleware chain builder
- `apply_prompt_template()` in `backend/packages/harness/deerflow/agents/lead_agent/prompt.py` — Prompt assembly with dynamic sections

## Gotchas
- Tracing callbacks must be attached at graph root in `_make_lead_agent()`, not at individual `create_chat_model()` calls — duplicate attachment breaks `session_id`/`user_id` propagation (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- The bootstrap agent path uses a restricted skill set (`_BOOTSTRAP_SKILL_NAMES = {"bootstrap"}`) to keep initial agent creation deterministic before custom config exists (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- `ThreadState` uses custom reducers for list fields (messages, todos, artifacts) — standard dict merge would lose items across graph steps (`backend/packages/harness/deerflow/agents/thread_state.py`)
- `_resolve_model_name()` falls back silently to the default model when the requested name is unknown — only logs a warning, does not raise (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Skills cache is primed at import time via `prime_enabled_skills_cache()` in `__init__.py` — first request may see empty skills if cache warm-up hasn't completed (`backend/packages/harness/deerflow/agents/__init__.py`)

## Architecture
- Two-tier factory pattern: `create_deerflow_agent()` is a pure-argument builder for custom assembly; `make_lead_agent()` wraps it for LangGraph Server compatibility with config-driven resolution (`backend/packages/harness/deerflow/agents/factory.py`, `backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Model resolution follows a 3-tier priority: runtime request → agent config → global default, with fallback for unknown names (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Middleware chain is assembled deterministically with documented ordering; `@Next`/`@Prev` decorators allow middleware to declare relative positioning (`backend/packages/harness/deerflow/agents/features.py`)
- Runtime configuration is merged from two sources: legacy `config["configurable"]` dict and LangGraph `config["context"]` dict, with context taking precedence (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Decisions
- System prompt is kept fully static for prefix-cache reuse; dynamic content injected as `<system-reminder>` HumanMessages (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`, `git:c1b7f1d1`)
- Subagent system_prompt was consolidated into the lead agent's prompt rather than injected separately to reduce token overhead (`git:813d3c94`)
- Bootstrap agent uses a minimal prompt and restricted tool set to keep custom agent creation deterministic (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- `build_middlewares()` is a public function (not private) because `DeerFlowClient` needs the identical middleware chain across a module boundary (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Patterns
- All middleware extends `AgentMiddleware[StateType]` and hooks into `before_model`/`after_model` lifecycle (`backend/packages/harness/deerflow/agents/middlewares/`)
- Factory functions accept explicit `app_config` parameters to support request-scoped config injection (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Prompt sections are built by dedicated `_build_*_section()` functions that accept runtime parameters (subagent_enabled, max_concurrent, available_skills) (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)
- Lazy imports are used inside factory functions to avoid circular dependencies (e.g., `get_available_tools` imported inside `_make_lead_agent`) (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Conventions
- Runtime config keys use snake_case: `thinking_enabled`, `is_plan_mode`, `subagent_enabled`, `max_concurrent_subagents` (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Metadata injection for tracing uses `config["metadata"]` dict with `agent_name`, `model_name`, `thinking_enabled` keys (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- `_get_runtime_config()` is the single function for merging configurable + context into one dict (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Dependencies
- LangGraph provides `create_agent`, graph compilation, and state management (`backend/packages/harness/deerflow/agents/`)
- LangChain provides `AgentMiddleware` base class and `RunnableConfig` (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- `deerflow.models.create_chat_model` is the sole model creation entry point for all agents (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Child Knowledge Nodes
- `./lead-agent/SKILL.md` — Lead agent factory, model resolution, prompt template, skills cache
- `./middleware-chain/SKILL.md` — Middleware ordering, individual middleware behaviors, chain assembly
- `./subagent-delegation/SKILL.md` — Subagent config, executor, registry, task tool
