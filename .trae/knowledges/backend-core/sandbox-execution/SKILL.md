---
name: knowledge-backend-core-sandbox-execution
description: >
  Covers sandbox execution: abstract Sandbox/SandboxProvider interfaces, LocalSandbox
  with path mapping, AioSandbox (Docker-based), sandbox middleware, sandbox tools,
  and security gating. Navigate when: adding a sandbox provider, debugging sandbox
  path resolution, modifying sandbox tools, configuring sandbox behavior, or
  troubleshooting file operation locking. This is a component-like module consumed
  by agent orchestration, tool ecosystem, and subagent delegation.
  Excludes: tool assembly (see ../tool-ecosystem/), agent factory (see ../agent-orchestration/).
  Keywords: Sandbox, SandboxProvider, LocalSandbox, AioSandbox, LocalSandboxProvider,
  AioSandboxProvider, SandboxMiddleware, PathMapping, VIRTUAL_PATH_PREFIX, sandbox tools,
  bash, read_file, write_file, str_replace, glob, grep, list_dir, is_host_bash_allowed.
---

## Module Structure

The sandbox system provides isolated execution environments for agent tools. It defines
abstract interfaces (Sandbox, SandboxProvider) with two concrete implementations: a local
filesystem-based sandbox and a Docker-based AIO sandbox. A middleware layer manages sandbox
lifecycle, and a comprehensive tool suite provides file and command operations.

### Directory Layout
- `backend/packages/harness/deerflow/sandbox/__init__.py` — Public API: Sandbox, SandboxProvider, get_sandbox_provider
- `backend/packages/harness/deerflow/sandbox/sandbox.py` — Abstract Sandbox ABC with file/command operations
- `backend/packages/harness/deerflow/sandbox/sandbox_provider.py` — Abstract SandboxProvider ABC with singleton lifecycle
- `backend/packages/harness/deerflow/sandbox/middleware.py` — SandboxMiddleware with lazy_init, state persistence
- `backend/packages/harness/deerflow/sandbox/tools.py` — All sandbox tool implementations (bash, read_file, write_file, etc.)
- `backend/packages/harness/deerflow/sandbox/security.py` — Host bash gating: is_host_bash_allowed(), uses_local_sandbox_provider()
- `backend/packages/harness/deerflow/sandbox/local/local_sandbox.py` — LocalSandbox with PathMapping, shell detection
- `backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py` — LocalSandboxProvider with dual-track cache
- `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py` — AioSandbox using agent_sandbox SDK
- `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py` — AioSandboxProvider with pluggable backends

### Key Entry Points
- `Sandbox` ABC in `backend/packages/harness/deerflow/sandbox/sandbox.py` — Abstract sandbox interface
- `SandboxProvider` ABC in `backend/packages/harness/deerflow/sandbox/sandbox_provider.py` — Abstract provider with acquire/get/release/reset
- `get_sandbox_provider()` in `backend/packages/harness/deerflow/sandbox/sandbox_provider.py` — Singleton provider accessor
- `SandboxMiddleware` in `backend/packages/harness/deerflow/sandbox/middleware.py` — Lifecycle management middleware

## API Surface

### Sandbox (ABC)
- `execute_command(command, workdir)` — Execute a shell command, return stdout/stderr/exit_code
- `read_file(path)` — Read file contents from sandbox
- `write_file(path, content)` — Write content to a file in sandbox
- `download_file(path)` — Download a file from sandbox
- `list_dir(path)` — List directory contents
- `glob(pattern, path)` — Glob pattern matching in sandbox
- `grep(pattern, path)` — Grep search in sandbox
- `update_file(path, old_str, new_str)` — String replacement in file

### SandboxProvider (ABC)
- `acquire(thread_id)` — Acquire a sandbox for a thread
- `get(thread_id)` — Get existing sandbox without creating
- `release(thread_id)` — Release a sandbox
- `reset(thread_id)` — Reset sandbox to clean state

### SandboxMiddleware
- `lazy_init` — Defer sandbox acquisition until first tool call
- State persistence via `Command(update=...)` pattern

## Usage Examples

### Using the sandbox provider singleton
```python
from deerflow.sandbox import get_sandbox_provider

provider = get_sandbox_provider()
sandbox = await provider.acquire(thread_id)
result = await sandbox.execute_command("ls -la", workdir="/mnt/user-data")
```

### Adding a new sandbox provider
```python
from deerflow.sandbox.sandbox_provider import SandboxProvider
from deerflow.sandbox.sandbox import Sandbox

class MySandbox(Sandbox):
    async def execute_command(self, command, workdir): ...

class MySandboxProvider(SandboxProvider):
    async def acquire(self, thread_id): ...
    async def release(self, thread_id): ...
```

## Gotchas
- `Command(update=...)` is the required pattern for persisting sandbox state across middleware — direct state mutation is not propagated (`backend/packages/harness/deerflow/sandbox/middleware.py`, `git:380255f7`)
- LocalSandboxProvider uses a dual-track cache: generic singleton + per-thread LRU (cap 256) — sharing a sandbox across concurrent threads causes race conditions (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`, `git:380255f7`)
- Host bash is gated by sandbox provider type: `is_host_bash_allowed()` returns False for local sandbox, so bash commands are only available with AioSandboxProvider (`backend/packages/harness/deerflow/sandbox/security.py`)
- AioSandbox uses `threading.Lock` for command serialization — concurrent commands on the same sandbox are serialized, not truly parallel (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`)
- File operations in sandbox tools use a locking mechanism to prevent concurrent read/write races (`backend/packages/harness/deerflow/sandbox/tools.py`)

## Architecture
- Abstract Sandbox ABC defines the interface; concrete implementations (LocalSandbox, AioSandbox) provide the execution backend (`backend/packages/harness/deerflow/sandbox/sandbox.py`)
- SandboxProvider follows a singleton lifecycle pattern: `get_sandbox_provider()` returns the global instance, `reset_sandbox_provider()` and `shutdown_sandbox_provider()` manage lifecycle (`backend/packages/harness/deerflow/sandbox/sandbox_provider.py`)
- SandboxMiddleware uses lazy_init: sandbox is not acquired until the first tool call, reducing resource usage for threads that never use sandbox tools (`backend/packages/harness/deerflow/sandbox/middleware.py`)
- LocalSandbox uses PathMapping to translate between container paths (`/mnt/user-data/...`) and local filesystem paths (`backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`)

## Decisions
- LocalSandboxProvider was refactored to per-thread sandbox instances to prevent cross-thread contamination (`backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`, `git:380255f7`)
- AioSandboxProvider supports pluggable backends (local container vs remote/K8s) for deployment flexibility (`backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`)
- Sandbox tools use a `_resolve_path()` pattern that maps container paths to local filesystem paths via PathMapping for all file operations (`backend/packages/harness/deerflow/sandbox/tools.py`)

## Patterns
- All sandbox tools use `_resolve_path()` to translate container paths to local paths before file operations (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Sandbox state is persisted via `Command(update={"sandbox": sandbox_state})` — never mutate state directly (`backend/packages/harness/deerflow/sandbox/middleware.py`)
- Provider lifecycle: `get_sandbox_provider()` → `acquire(thread_id)` → use → `release(thread_id)` → `shutdown_sandbox_provider()` (`backend/packages/harness/deerflow/sandbox/sandbox_provider.py`)

## Conventions
- Container paths use `VIRTUAL_PATH_PREFIX = "/mnt/user-data"` as the root (`backend/packages/harness/deerflow/config/paths.py`)
- Sandbox tools are registered with names matching Unix commands: `bash`, `read_file`, `write_file`, `str_replace`, `glob`, `grep`, `list_dir` (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Read-only mounts are enforced for local sandbox to prevent unintended filesystem modifications (`backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`)

## Consumer Analysis
- Agent orchestration (lead_agent/agent.py) — consumes SandboxMiddleware for lifecycle management, gated by RuntimeFeatures.sandbox flag
- Tool ecosystem (tools/tools.py) — consumes sandbox tools via `get_available_tools()`, gated by sandbox provider type for bash
- Subagent delegation (tools/builtins/task_tool.py) — consumes `is_host_bash_allowed()` to gate bash subagent availability
- Memory system (agents/memory/) — uses sandbox for file operations during memory processing

## Dependencies
- `agent_sandbox` SDK for AioSandbox Docker-based execution (`backend/packages/harness/deerflow/community/aio_sandbox/`)
- LangGraph `Command` for state persistence across middleware (`backend/packages/harness/deerflow/sandbox/middleware.py`)
- `deerflow.config.paths` for VIRTUAL_PATH_PREFIX and path resolution (`backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`)

## Child Knowledge Nodes
- `./local-sandbox/SKILL.md` — LocalSandbox with PathMapping, shell detection, read-only mounts
- `./docker-sandbox/SKILL.md` — AioSandbox with agent_sandbox SDK, pluggable backends, threading
- `./sandbox-tools/SKILL.md` — Sandbox tool implementations, path resolution, file locking, security
