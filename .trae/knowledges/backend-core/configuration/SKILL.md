---
name: knowledge-backend-core-configuration
description: >
  Covers configuration: AppConfig with 25+ sub-config models, Paths with centralized
  directory layout, config file resolution, mtime-based auto-reload, ContextVar-based
  runtime overrides, environment variable resolution, and singleton config propagation.
  Navigate when: adding new config sections, modifying config loading, debugging config
  resolution, working on path management, or understanding config reload behavior.
  This is a cross-cutting module whose configuration choices partition behavior across
  agent orchestration, sandbox execution, tool ecosystem, memory system, model integration,
  skills management, and runtime engine.
  Keywords: AppConfig, get_app_config, config.yaml, Paths, VIRTUAL_PATH_PREFIX,
  ContextVar, mtime reload, config_version, resolve_env_variables, singleton config,
  runtime override, push_current_app_config, pop_current_app_config, set_app_config,
  reload_app_config, reset_app_config, DEER_FLOW_CONFIG_PATH.
---

## Module Structure

Configuration is the central nervous system of DeerFlow. A single `AppConfig` Pydantic model
holds 25+ sub-config sections. It is loaded from `config.yaml`, auto-reloaded on mtime change,
and supports ContextVar-based runtime overrides for request-scoped configuration injection.

### Decision Entry
- `get_app_config()` in `backend/packages/harness/deerflow/config/app_config.py` — Returns the singleton AppConfig, auto-reloading on mtime change
- `AppConfig.from_file()` in `backend/packages/harness/deerflow/config/app_config.py` — Loads and validates config from YAML
- `Paths` in `backend/packages/harness/deerflow/config/paths.py` — Centralized directory layout with user/thread isolation

### Directory Layout
- `backend/packages/harness/deerflow/config/__init__.py` — Public API: get_app_config, ExtensionsConfig, LoopDetectionConfig, MemoryConfig, Paths, SkillsConfig
- `backend/packages/harness/deerflow/config/app_config.py` — AppConfig with 25+ sub-config models, singleton management
- `backend/packages/harness/deerflow/config/paths.py` — Paths class with centralized directory layout, VIRTUAL_PATH_PREFIX
- `backend/packages/harness/deerflow/config/model_config.py` — ModelConfig per-provider configuration
- `backend/packages/harness/deerflow/config/sandbox_config.py` — Sandbox provider configuration
- `backend/packages/harness/deerflow/config/tool_config.py` — Tool and ToolGroup configuration
- `backend/packages/harness/deerflow/config/skills_config.py` — Skills storage and container path config
- `backend/packages/harness/deerflow/config/memory_config.py` — Memory subsystem configuration
- `backend/packages/harness/deerflow/config/summarization_config.py` — Summarization middleware config
- `backend/packages/harness/deerflow/config/title_config.py` — Title generation config
- `backend/packages/harness/deerflow/config/loop_detection_config.py` — Loop detection config
- `backend/packages/harness/deerflow/config/safety_finish_reason_config.py` — Safety filter config
- `backend/packages/harness/deerflow/config/tool_search_config.py` — Deferred tool search config
- `backend/packages/harness/deerflow/config/tool_output_config.py` — Tool output budget config
- `backend/packages/harness/deerflow/config/token_usage_config.py` — Token usage tracking config
- `backend/packages/harness/deerflow/config/checkpointer_config.py` — Checkpointer backend config
- `backend/packages/harness/deerflow/config/database_config.py` — Database backend config
- `backend/packages/harness/deerflow/config/run_events_config.py` — Run event store config
- `backend/packages/harness/deerflow/config/stream_bridge_config.py` — Stream bridge config
- `backend/packages/harness/deerflow/config/guardrails_config.py` — Guardrail middleware config
- `backend/packages/harness/deerflow/config/subagents_config.py` — Subagent runtime config
- `backend/packages/harness/deerflow/config/skill_evolution_config.py` — Skill self-evolution config
- `backend/packages/harness/deerflow/config/extensions_config.py` — MCP servers and skills state config
- `backend/packages/harness/deerflow/config/agents_api_config.py` — Custom agent management API config
- `backend/packages/harness/deerflow/config/acp_config.py` — ACP-compatible agent config
- `backend/packages/harness/deerflow/config/agents_config.py` — Per-agent config (SOUL.md, tool_groups, skills)
- `backend/packages/harness/deerflow/config/runtime_paths.py` — Runtime path resolution utilities
- `backend/packages/harness/deerflow/config/reload_boundary.py` — Config reload boundary utilities

### Key Entry Points
- `get_app_config()` in `backend/packages/harness/deerflow/config/app_config.py` — Singleton config accessor with auto-reload
- `AppConfig.from_file(config_path)` in `backend/packages/harness/deerflow/config/app_config.py` — Config loading and validation
- `Paths(base_dir)` in `backend/packages/harness/deerflow/config/paths.py` — Directory layout for agents, threads, users
- `push_current_app_config()` / `pop_current_app_config()` in `backend/packages/harness/deerflow/config/app_config.py` — Runtime config override stack

## Branching Table

| Dimension | Memory Backend | SQLite Backend | PostgreSQL Backend |
|-----------|---------------|----------------|-------------------|
| Checkpointer | `MemorySaver` — no persistence across restarts | `SqliteSaver` — file-based persistence | `PostgresSaver` — connection-pool persistence |
| Store | `InMemoryStore` — volatile, no durability | SQLite store — file-based durability | PostgreSQL store — connection-pool durability |
| Run events | `MemoryRunEventStore` — lost on restart | SQLite event store — queryable history | Not directly supported (use DB backend) |
| Run records | In-memory only — lost on restart | SQLite RunStore — survives restarts | PostgreSQL RunStore — survives restarts |
| Concurrency | Single-process only | Single-process (SQLite lock contention) | Multi-process (connection pooling) |
| Setup complexity | Zero config | File path only | Connection string + pool config |

| Dimension | Local Sandbox | Docker AIO Sandbox |
|-----------|--------------|-------------------|
| Bash availability | Disabled (`is_host_bash_allowed()` returns False) | Enabled (isolated container) |
| Path mapping | Container paths → local filesystem via PathMapping | Container paths → Docker volume mounts |
| Thread safety | Per-thread LRU cache (cap 256) + generic singleton fallback | Thread-lock executor for command serialization |
| Subagent bash | Not available | Available (isolated shell access) |
| Setup | Zero config (filesystem only) | Requires Docker + agent_sandbox SDK |

| Dimension | Thinking Enabled | Thinking Disabled |
|-----------|-----------------|-------------------|
| Model behavior | Extended reasoning with thinking tokens | Standard chat completion |
| Token usage | Higher (thinking tokens included) | Lower (response tokens only) |
| Provider support | Only models with `supports_thinking=True` | All models |
| Fallback | Silently disabled with warning if unsupported | Always works |

## Affected Scope
- `backend/packages/harness/deerflow/agents/` — Agent factory reads models, tools, skills, memory, summarization, loop_detection, safety, token_usage, tool_search configs (15+ call sites)
- `backend/packages/harness/deerflow/sandbox/` — Sandbox provider selection, path mapping, security gating from sandbox config (5+ call sites)
- `backend/packages/harness/deerflow/tools/` — Tool assembly reads tools, tool_groups, tool_search, tool_output configs (3+ call sites)
- `backend/packages/harness/deerflow/mcp/` — MCP server connections from extensions config (3+ call sites)
- `backend/packages/harness/deerflow/models/` — Model creation reads models config for provider, API key, capabilities (2+ call sites)
- `backend/packages/harness/deerflow/skills/` — Skills storage path, container path from skills config (3+ call sites)
- `backend/packages/harness/deerflow/runtime/` — Checkpointer, store, stream_bridge, run_events, database backends from respective configs (8+ call sites)
- `backend/packages/harness/deerflow/subagents/` — Subagent runtime config, custom agent definitions (3+ call sites)
- `backend/packages/harness/deerflow/agents/middlewares/` — Middleware behavior gated by loop_detection, safety, guardrails, title, summarization configs (10+ call sites)

## Gotchas
- `get_app_config()` auto-reloads when the config file mtime changes — runtime behavior can change mid-process without explicit reload (`backend/packages/harness/deerflow/config/app_config.py`)
- Config file resolution has 4-tier priority: explicit `config_path` arg → `DEER_FLOW_CONFIG_PATH` env var → project root search → legacy backend/repo root fallback (`backend/packages/harness/deerflow/config/app_config.py`)
- Environment variables in config values (prefixed with `$`) are resolved recursively — missing env vars raise `ValueError` rather than silently using empty strings (`backend/packages/harness/deerflow/config/app_config.py`)
- Commenting out all entries under a YAML key (e.g., `models:`) makes PyYAML parse it as `None` — the `_coerce_null_list_sections` validator converts this to `[]` to prevent crashes (`backend/packages/harness/deerflow/config/app_config.py`)
- Changing checkpointer config triggers automatic reset of both checkpointer and store singletons — in-flight runs may lose state (`backend/packages/harness/deerflow/config/app_config.py`)

## Architecture
- Singleton pattern with mtime-based auto-reload: `get_app_config()` caches the config and re-reads it when the file modification time changes (`backend/packages/harness/deerflow/config/app_config.py`)
- ContextVar-based runtime override stack: `push_current_app_config()` / `pop_current_app_config()` allow request-scoped config injection without affecting other requests (`backend/packages/harness/deerflow/config/app_config.py`)
- Config versioning: `config_version` field compared against `config.example.yaml` to warn users about outdated configs (`backend/packages/harness/deerflow/config/app_config.py`)
- Singleton config propagation: certain sub-configs (title, summarization, memory, checkpointer, etc.) are loaded into module-level singletons via `_apply_singleton_configs()` (`backend/packages/harness/deerflow/config/app_config.py`)
- Paths class provides centralized directory layout: `{base_dir}/agents/{name}/`, `{base_dir}/threads/{id}/user-data/`, `{base_dir}/users/{id}/` (`backend/packages/harness/deerflow/config/paths.py`)

## Decisions
- Mtime-based auto-reload was chosen over file watchers for simplicity — it avoids inotify/fanotify platform differences (`backend/packages/harness/deerflow/config/app_config.py`)
- ContextVar stack was chosen over thread-local for runtime overrides because it works correctly with asyncio task propagation (`backend/packages/harness/deerflow/config/app_config.py`)
- Config versioning with `config.example.yaml` comparison was added to help users detect when their config is outdated after upgrades (`backend/packages/harness/deerflow/config/app_config.py`)
- `VIRTUAL_PATH_PREFIX = "/mnt/user-data"` is hardcoded as the sandbox root path seen by agents (`backend/packages/harness/deerflow/config/paths.py`)

## Patterns
- Sub-config models are Pydantic `BaseModel` classes with `Field(default_factory=...)` for sensible defaults (`backend/packages/harness/deerflow/config/`)
- Config loading pipeline: `resolve_config_path()` → `yaml.safe_load()` → `_check_config_version()` → `resolve_env_variables()` → `_apply_database_defaults()` → `model_validate()` → `_apply_singleton_configs()` (`backend/packages/harness/deerflow/config/app_config.py`)
- Thread/user ID validation: regex-based validation before using IDs in filesystem paths to prevent path traversal (`backend/packages/harness/deerflow/config/paths.py`)
- Windows path preservation: `_join_host_path()` detects Windows-style paths and uses `PureWindowsPath` to preserve backslash separators for Docker Desktop compatibility (`backend/packages/harness/deerflow/config/paths.py`)

## Conventions
- Config file is named `config.yaml` and lives in the project root or backend directory (`backend/packages/harness/deerflow/config/app_config.py`)
- Environment variables in config use `$VAR_NAME` syntax (e.g., `$OPENAI_API_KEY`) (`backend/packages/harness/deerflow/config/app_config.py`)
- Sub-config modules are named `*_config.py` and live in `config/` (`backend/packages/harness/deerflow/config/`)
- Logging level from config only affects `deerflow` and `app` loggers — third-party library verbosity is not changed (`backend/packages/harness/deerflow/config/app_config.py`)

## Branching Behavior
- Checkpointer backend selection gates whether agent state survives process restarts — memory backend loses all state on restart (`backend/packages/harness/deerflow/runtime/checkpointer/provider.py`)
- Sandbox provider type gates bash tool availability — local sandbox disables all bash/subagent-bash functionality (`backend/packages/harness/deerflow/sandbox/security.py`)
- Thinking mode toggle gates whether models use extended reasoning — silently disabled for models that don't support it (`backend/packages/harness/deerflow/agents/lead_agent/agent.py`)
- Memory injection toggle (`memory.injection_enabled`) gates whether user memory facts are included in the system-reminder (`backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py`)
- Tool search toggle (`tool_search.enabled`) gates whether MCP tools are deferred or directly bound to the model (`backend/packages/harness/deerflow/tools/builtins/tool_search.py`)

## Dependencies
- Pydantic for all config model validation (`backend/packages/harness/deerflow/config/app_config.py`)
- PyYAML for config file parsing (`backend/packages/harness/deerflow/config/app_config.py`)
- `python-dotenv` for `.env` file loading at import time (`backend/packages/harness/deerflow/config/app_config.py`)
- `contextvars` for runtime config override propagation (`backend/packages/harness/deerflow/config/app_config.py`)
