---
name: knowledge-backend-core-agent-orchestration-lead-agent
description: >
  Covers the lead agent factory: `make_lead_agent()`, `_make_lead_agent()`, model resolution,
  prompt template assembly, skills cache management, and bootstrap agent path. Navigate when:
  modifying agent creation flow, changing system prompt, debugging model selection, adding
  runtime features, or working on skills cache behavior.
  Excludes: middleware chain (see ../middleware-chain/), subagent delegation (see ../subagent-delegation/).
  Keywords: make_lead_agent, _make_lead_agent, build_middlewares, apply_prompt_template,
  SYSTEM_PROMPT_TEMPLATE, _resolve_model_name, prime_enabled_skills_cache, bootstrap agent,
  create_agent, ThreadState, _get_runtime_config.
---

## Module Structure

The lead agent is the primary LangGraph agent graph. It resolves runtime configuration,
selects a model, assembles tools and middleware, builds the system prompt, and returns a
compiled LangGraph graph. A special bootstrap path exists for initial custom agent creation.

### Directory Layout
- `backend/packages/harness/deerflow/agents/lead_agent/agent.py` — `make_lead_agent()`, `_make_lead_agent()`, `build_middlewares()`, model resolution
- `backend/packages/harness/deerflow/agents/lead_agent/prompt.py` — SYSTEM_PROMPT_TEMPLATE, skills cache, subagent section builder, prompt assembly
- `backend/packages/harness/deerflow/agents/features.py` — RuntimeFeatures dataclass, Next/Prev decorators
- `backend/packages/harness/deerflow/agents/thread_state.py` — ThreadState schema with custom reducers

### Key Entry Points
- `make_lead_agent(config)` in `backend/packages/harness/deerflow/agents/lead_agent/agent.py` — LangGraph graph factory (public, stable signature)
- `_make_lead_agent(config, app_config)` in `backend/packages/harness/deerflow/agents/lead_agent/agent.py` — Internal factory with explicit config
- `apply_prompt_template(...)` in `backend/packages/harness/deerflow/agents/lead_agent/prompt.py` — Assembles the full system prompt
- `_resolve_model_name(requested, app_config)` in `backend/packages/harness/deerflow/agents/lead_agent/agent.py` — 3-tier model resolution

## Gotchas
- Tracing callbacks must be attached at graph root in `_make_lead_agent()`, not at individual `create_chat_model()` calls — every in-graph model creation must pass `attach_tracing=False` (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- The bootstrap agent path uses a hardcoded skill set `{"bootstrap"}` — adding skills to bootstrap requires changing `_BOOTSTRAP_SKILL_NAMES` (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- `_resolve_model_name()` silently falls back to the default model when the requested name is unknown — only logs a warning, does not raise an error (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Thinking mode is silently disabled if the resolved model does not support it — a warning is logged but execution continues (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Skills cache is primed at import time via `prime_enabled_skills_cache()` — the first request after startup may see an empty skills list if the background thread hasn't finished loading (`backend/packages/harness/deerflow/agents/__init__.py`, `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)

## Architecture
- Two-tier factory: `make_lead_agent()` is the public LangGraph Server entry point; `_make_lead_agent()` is the internal factory that accepts explicit `app_config` for request-scoped injection (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Model resolution is 3-tier: runtime request (`model_name`/`model` key) → agent config (`agent_config.model`) → global default (`app_config.models[0].name`) (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Runtime config is merged from two sources: legacy `config["configurable"]` dict and LangGraph `config["context"]` dict, with context values taking precedence (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Tool assembly pipeline: `get_available_tools()` → `filter_tools_by_skill_allowed_tools()` → `assemble_deferred_tools()` → `create_agent(tools=final_tools)` (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Decisions
- System prompt is kept fully static for prefix-cache reuse; dynamic content (current date, memory) is injected as `<system-reminder>` HumanMessages via DynamicContextMiddleware (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`, `git:c1b7f1d1`)
- Subagent system_prompt was consolidated into the lead agent's prompt rather than injected separately to reduce token overhead (`git:813d3c94`)
- Bootstrap agent uses a minimal prompt and restricted tool set (`setup_agent` only) to keep custom agent creation deterministic before config exists (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Custom agents get `update_agent` tool; the default agent (no agent_name) does not see this tool (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Patterns
- Lazy imports inside factory functions avoid circular dependencies — `get_available_tools`, `setup_agent`, `update_agent`, `assemble_deferred_tools` are all imported inside `_make_lead_agent()` (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Metadata injection into `config["metadata"]` carries `agent_name`, `model_name`, `thinking_enabled`, `reasoning_effort`, `is_plan_mode`, `subagent_enabled`, `tool_groups`, `available_skills` for tracing (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Prompt sections are built by dedicated `_build_*_section()` functions that accept runtime parameters and return formatted strings (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)

## Conventions
- Runtime config keys use snake_case: `thinking_enabled`, `is_plan_mode`, `subagent_enabled`, `max_concurrent_subagents`, `is_bootstrap` (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- `_get_runtime_config()` is the single function for merging configurable + context into one dict — all runtime config reads go through it (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Agent name is validated via `validate_agent_name()` before use; `None` means default agent (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Skills Cache Management
- Skills cache uses a background daemon thread for async loading; `_ensure_enabled_skills_cache()` returns an Event that callers can wait on (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)
- Cache invalidation increments a version counter; if a newer invalidation happens during loading, the worker loops again to converge on the latest version (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)
- Per-config caching uses `id(app_config)` as the cache key for request-scoped config injection (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)
- `get_cached_enabled_skills()` is safe to call from request paths — never blocks on disk I/O, returns empty list on cache miss (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)

## Prompt Template
- SYSTEM_PROMPT_TEMPLATE includes sections: role, thinking, clarification, skills, subagent, working_directory, response_style, citations, critical_reminders (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)
- Subagent section is dynamically built from registry with concurrency limits and per-type descriptions (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)
- Skill evolution section is conditionally included based on `skill_evolution_enabled` config flag (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)
- Deferred tool names are injected into the prompt via `<available-deferred-tools>` block when tool_search is enabled (`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`)
