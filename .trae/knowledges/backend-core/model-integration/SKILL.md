---
name: knowledge-backend-core-model-integration
description: >
  Covers model integration: `create_chat_model()` multi-provider factory, thinking mode
  toggling, stream_usage auto-enable for OpenAI-compatible gateways, stream_chunk_timeout,
  Codex/MindIE special handling, tracing callback attachment control, and model config
  resolution. Navigate when: adding a new model provider, debugging model creation,
  configuring thinking mode, troubleshooting streaming issues, or working on tracing
  integration. This is a component-like module consumed by agent orchestration, memory
  system, subagent delegation, and runtime engine.
  Excludes: agent factory (see ../agent-orchestration/), configuration (see ../configuration/).
  Keywords: create_chat_model, model factory, thinking_enabled, reasoning_effort,
  stream_usage, stream_chunk_timeout, Codex, MindIE, OpenAI, tracing callbacks,
  attach_tracing, model config, multi-provider, ChatOpenAI, ChatAnthropic.
---

## Module Structure

The model integration module provides a unified factory for creating chat model instances
across multiple providers (OpenAI, Anthropic, Codex, MindIE, etc.). It handles provider-specific
configuration like thinking mode, streaming behavior, and tracing callback attachment.

### Directory Layout
- `backend/packages/harness/deerflow/models/__init__.py` — Public API: create_chat_model
- `backend/packages/harness/deerflow/models/factory.py` — `create_chat_model()` multi-provider factory

### Key Entry Points
- `create_chat_model()` in `backend/packages/harness/deerflow/models/factory.py` — Single entry point for all model creation

## API Surface

### create_chat_model
- `name` — Model name (resolved from config); if None, uses default model
- `thinking_enabled` — Enable extended thinking mode (provider-dependent)
- `reasoning_effort` — Reasoning effort level for models that support it
- `app_config` — Explicit AppConfig; falls back to `get_app_config()`
- `attach_tracing` — Whether to attach tracing callbacks at model level (default True; set False for in-graph models)

## Usage Examples

### Creating a model for the lead agent
```python
from deerflow.models import create_chat_model

model = create_chat_model(
    name="gpt-4o",
    thinking_enabled=True,
    reasoning_effort="high",
    attach_tracing=False,  # Graph root handles tracing
)
```

### Creating a model for middleware (e.g., summarization)
```python
model = create_chat_model(
    name=config.model_name,
    thinking_enabled=False,
    attach_tracing=False,
)
model = model.with_config(tags=["middleware:summarize"])
```

## Gotchas
- `attach_tracing=False` is mandatory for all in-graph model creation — forgetting this flag emits duplicate spans and breaks `session_id`/`user_id` propagation (`backend/packages/harness/deerflow/models/factory.py`, `backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- `stream_usage` is auto-enabled for OpenAI-compatible gateways — this ensures token usage is available in streaming mode but may cause issues with gateways that don't support it (`backend/packages/harness/deerflow/models/factory.py`)
- `stream_chunk_timeout` defaults to 240 seconds — long-running model calls may timeout if the model takes longer to generate (`backend/packages/harness/deerflow/models/factory.py`)
- Codex and MindIE providers have special handling in the factory — generic provider logic may not apply to them (`backend/packages/harness/deerflow/models/factory.py`)
- Thinking mode is provider-dependent — enabling it on a model that doesn't support it will cause the factory to silently disable it with a warning (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Architecture
- Single factory function `create_chat_model()` handles all providers — provider-specific logic is determined by model config inspection (`backend/packages/harness/deerflow/models/factory.py`)
- Model configuration comes from `app_config.models` list, with each entry specifying provider, name, API key, and capabilities (`backend/packages/harness/deerflow/config/app_config.py`)
- Tracing callback attachment is controlled by the `attach_tracing` parameter — when False, the model is created without callbacks, relying on graph-level attachment (`backend/packages/harness/deerflow/models/factory.py`)
- Provider-specific features (thinking mode, streaming behavior) are configured based on model capabilities declared in config (`backend/packages/harness/deerflow/models/factory.py`)

## Decisions
- Tracing callbacks are attached at graph root, not at model level — this ensures a single trace per run with proper parent-child span relationships (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- `stream_usage` is auto-enabled for OpenAI-compatible gateways to ensure token usage tracking works in streaming mode (`backend/packages/harness/deerflow/models/factory.py`)
- Model name is propagated through the runtime and persisted in run records for traceability (`backend/packages/harness/deerflow/runtime/runs/manager.py`, `git:de253e4a`)

## Patterns
- Factory function accepts explicit `app_config` to support request-scoped config injection (`backend/packages/harness/deerflow/models/factory.py`)
- Model tags (e.g., `["middleware:summarize"]`) are used to identify model calls from middleware vs lead agent in tracing (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- `model.with_config(tags=[...])` is the standard pattern for adding metadata to model instances (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)

## Consumer Analysis
- Agent orchestration (agents/lead_agent/agent.py) — primary consumer: creates models for lead agent, bootstrap agent, summarization middleware
- Memory system (agents/memory/updater.py) — creates models for memory fact extraction and deduplication
- Subagent delegation (subagents/executor.py) — creates models for subagent execution
- Title middleware (agents/middlewares/title_middleware.py) — creates models for title generation
- Summarization middleware (agents/middlewares/summarization_middleware.py) — creates models for conversation summarization

## Conventions
- `attach_tracing=False` for all in-graph model creation; `attach_tracing=True` (default) only for standalone usage (`backend/packages/harness/deerflow/models/factory.py`)
- Model names are resolved via `_resolve_model_name()` before passing to `create_chat_model()` (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Provider-specific configuration is read from `app_config.models[]` entries (`backend/packages/harness/deerflow/models/factory.py`)

## Dependencies
- LangChain `ChatOpenAI`, `ChatAnthropic`, and other provider-specific chat model classes (`backend/packages/harness/deerflow/models/factory.py`)
- `deerflow.config.app_config` for model configuration (`backend/packages/harness/deerflow/models/factory.py`)
- `deerflow.tracing` for tracing callback construction (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
