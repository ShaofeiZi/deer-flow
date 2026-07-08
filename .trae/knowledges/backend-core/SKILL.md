---
name: knowledge-backend-core
description: >
  Covers the DeerFlow backend core: LangGraph-based agent orchestration, sandbox execution,
  tool ecosystem, memory system, model integration, skills management, runtime engine, and
  configuration. Navigate when: understanding the agent architecture, modifying middleware
  chains, adding sandbox providers, integrating new tools or MCP servers, debugging memory
  updates, configuring models, managing skill installations, or working on runtime/streaming.
  Excludes: gateway/API layer (see backend-gateway/), frontend (see frontend/), platform
  infrastructure (see platform/), skill content definitions (see skills/).
  Keywords: deerflow, langgraph, agent, middleware, sandbox, MCP, memory, skills, runtime,
  streaming, checkpointer, store, lead_agent, create_deerflow_agent, ThreadState, RuntimeFeatures,
  SandboxProvider, create_chat_model, SkillStorage, RunManager, StreamBridge.
---

## Module Structure

The backend core is the central agent runtime built on LangGraph. It assembles an agent
from configurable middleware, sandbox providers, tool registries, memory storage, model
backends, and skill packs — all wired through a unified configuration system.

### Directory Layout
- `backend/packages/harness/deerflow/agents/` — Agent factory, lead agent, prompt, thread state, middlewares, memory
  - `lead_agent/agent.py` — `make_lead_agent()` and `build_middlewares()` — full agent assembly
  - `lead_agent/prompt.py` — SYSTEM_PROMPT_TEMPLATE with dynamic skill/subagent sections
  - `middlewares/` — 20+ middleware classes (clarification, memory, sandbox, title, etc.)
  - `memory/` — Memory storage, updater, queue, message processing
- `backend/packages/harness/deerflow/sandbox/` — Abstract sandbox + local/Docker providers + tools
- `backend/packages/harness/deerflow/tools/` — Tool assembly, MCP integration, builtins, community tools
- `backend/packages/harness/deerflow/models/` — Multi-provider model factory
- `backend/packages/harness/deerflow/skills/` — Skill parser, installer, storage, tool policy
- `backend/packages/harness/deerflow/runtime/` — Run management, streaming, checkpointer, store, events
- `backend/packages/harness/deerflow/config/` — AppConfig with 25+ sub-config models, paths

### Key Entry Points
- `create_deerflow_agent()` in `backend/packages/harness/deerflow/agents/factory.py` — Pure-argument agent factory
- `make_lead_agent()` in `backend/packages/harness/deerflow/agents/lead_agent/agent.py` — LangGraph graph factory
- `get_available_tools()` in `backend/packages/harness/deerflow/tools/tools.py` — Tool assembly entry point
- `create_chat_model()` in `backend/packages/harness/deerflow/models/factory.py` — Model creation entry point
- `get_app_config()` in `backend/packages/harness/deerflow/config/__init__.py` — Config loading entry point

## Gotchas
- Tracing callbacks must be attached at the graph invocation root in `_make_lead_agent()`, not at individual `create_chat_model()` calls — duplicate attachment emits double spans and breaks `session_id`/`user_id` propagation (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- The `Runtime` type alias (`ToolRuntime[dict[str, Any], ThreadState]`) is required to prevent Pydantic serialization warnings on tool state fields (`backend/packages/harness/deerflow/tools/types.py`, `git:7de9b582`)
- Memory updater uses a synchronous LLM path to avoid cross-loop connection reuse issues with async model clients (`backend/packages/harness/deerflow/agents/memory/updater.py`, `git:722c690f`)
- `Command(update=...)` is the required pattern for persisting sandbox state across middleware — direct state mutation is not propagated (`backend/packages/harness/deerflow/sandbox/middleware.py`, `git:380255f7`)
- Tool search promotions must be preserved across re-entrant graph calls; promotion state rides on per-thread graph state, not ContextVar (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`, `git:f1a0ab69`)

## Architecture
- Agent assembly follows a pure-argument factory pattern: `create_deerflow_agent()` receives `RuntimeFeatures` and assembles a middleware chain with `@Next`/`@Prev` positioning decorators (`backend/packages/harness/deerflow/agents/factory.py`)
- Middleware chain ordering is deterministic and documented: ThreadData → DynamicContext → SkillActivation → Summarization → TodoList → TokenUsage → Title → Memory → ViewImage → DeferredToolFilter → SubagentLimit → LoopDetection → Custom → SafetyFinishReason → Clarification (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Sandbox providers follow an abstract interface with singleton lifecycle management via `get_sandbox_provider()` / `reset_sandbox_provider()` / `shutdown_sandbox_provider()` (`backend/packages/harness/deerflow/sandbox/sandbox_provider.py`)
- MCP tools use a session pool with owner-task pattern for anyio cancel-scope compliance, LRU eviction (cap 256), and cross-loop session management (`backend/packages/harness/deerflow/mcp/session_pool.py`)
- Memory system uses a pipeline: MemoryMiddleware queues messages → MemoryUpdater processes with LLM → FileMemoryStorage persists with atomic writes (`backend/packages/harness/deerflow/agents/memory/`)

## Decisions
- System prompt is kept fully static for prefix-cache reuse; dynamic content (current date, memory) is injected as `<system-reminder>` HumanMessages via DynamicContextMiddleware (`backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py`, `git:c1b7f1d1`)
- Subagent token usage is bucketed separately from lead agent tokens for cost attribution (`backend/packages/harness/deerflow/tools/builtins/task_tool.py`, `git:9892a7d4`)
- LocalSandboxProvider uses a dual-track cache: generic singleton + per-thread LRU (cap 256) to avoid sandbox reuse across concurrent threads (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`, `git:380255f7`)
- Model name is propagated through the runtime and persisted in run records for traceability (`backend/packages/harness/deerflow/runtime/runs/manager.py`, `git:de253e4a`)
- Memory queue is isolated by agent name to prevent cross-agent memory contamination (`backend/packages/harness/deerflow/agents/memory/updater.py`, `git:722c690f`)

## Patterns
- All middleware classes extend `AgentMiddleware[StateType]` and override `before_model`/`after_model` hooks (`backend/packages/harness/deerflow/agents/middlewares/`)
- Sandbox tools use a `_resolve_path()` pattern that maps container paths to local filesystem paths via PathMapping (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Config models use Pydantic with nested sub-configs; `get_app_config()` is the singleton accessor with lazy initialization (`backend/packages/harness/deerflow/config/app_config.py`)
- Factory functions accept explicit `app_config` parameters to support request-scoped config injection without global state (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Conventions
- File organization follows domain grouping: each subdomain has its own package with `__init__.py` exporting public API (`backend/packages/harness/deerflow/`)
- `from __future__ import annotations` is used consistently across all modules for PEP 604-style type hints (`backend/packages/harness/deerflow/`)
- Logging uses module-level `logger = logging.getLogger(__name__)` pattern (`backend/packages/harness/deerflow/`)
- Type aliases for runtime are defined in `tools/types.py` to avoid circular imports (`backend/packages/harness/deerflow/tools/types.py`)

## Dependencies
- LangGraph is the core framework — agent graphs, checkpointer, store, and streaming all depend on it (`backend/packages/harness/deerflow/`)
- LangChain provides `create_agent`, `AgentMiddleware`, and tool abstractions (`backend/packages/harness/deerflow/agents/`)
- Pydantic is used for all configuration models and state schemas (`backend/packages/harness/deerflow/config/`, `backend/packages/harness/deerflow/agents/thread_state.py`)
- `agent_sandbox` SDK is required for AioSandbox (Docker-based sandbox provider) (`backend/packages/harness/deerflow/community/aio_sandbox/`)

## Child Knowledge Nodes
- `./agent-orchestration/SKILL.md` — Agent factory, lead agent assembly, prompt template, thread state
- `./sandbox-execution/SKILL.md` — Sandbox abstraction, local/Docker providers, sandbox tools
- `./tool-ecosystem/SKILL.md` — Tool assembly, builtins, community tools, MCP integration
- `./memory-system/SKILL.md` — Memory storage, updater, queue, message processing
- `./model-integration/SKILL.md` — Multi-provider model factory with thinking mode support
- `./skills-management/SKILL.md` — Skill parsing, installation, storage, tool policy
- `./runtime-engine/SKILL.md` — Run management, streaming, state persistence, events
- `./configuration/SKILL.md` — AppConfig, paths, agent config, cross-cutting configuration
