---
name: knowledge-backend-core-sandbox-execution-sandbox-tools
description: >
  Covers sandbox tool implementations: bash, read_file, write_file, str_replace, glob,
  grep, list_dir, and other file/command tools. Includes path resolution, security checks,
  file operation locking, and tool registration. Navigate when: adding sandbox tools,
  modifying tool behavior, debugging path resolution, or troubleshooting file locking.
  Excludes: sandbox providers (see ../local-sandbox/, ../docker-sandbox/).
  Keywords: sandbox tools, bash, read_file, write_file, str_replace, glob, grep, list_dir,
  _resolve_path, PathMapping, file locking, tool registration, sandbox security,
  host_bash_gating, VIRTUAL_PATH_PREFIX.
---

## Module Structure

Sandbox tools provide the agent with filesystem and command execution capabilities within
the sandbox environment. Each tool resolves container paths to local paths, applies security
checks, and uses file operation locking to prevent races.

### Directory Layout
- `backend/packages/harness/deerflow/sandbox/tools.py` — All sandbox tool implementations (1500+ lines)
- `backend/packages/harness/deerflow/sandbox/security.py` — `is_host_bash_allowed()`, `uses_local_sandbox_provider()`
- `backend/packages/harness/deerflow/sandbox/middleware.py` — SandboxMiddleware that provides sandbox to tools
- `backend/packages/harness/deerflow/sandbox/sandbox.py` — Abstract Sandbox ABC defining tool interfaces

### Key Entry Points
- `bash` tool in `backend/packages/harness/deerflow/sandbox/tools.py` — Shell command execution
- `read_file` tool in `backend/packages/harness/deerflow/sandbox/tools.py` — File reading with line range support
- `write_file` tool in `backend/packages/harness/deerflow/sandbox/tools.py` — File writing with directory creation
- `str_replace` tool in `backend/packages/harness/deerflow/sandbox/tools.py` — String replacement in files
- `glob` tool in `backend/packages/harness/deerflow/sandbox/tools.py` — Glob pattern matching
- `grep` tool in `backend/packages/harness/deerflow/sandbox/tools.py` — Content search with regex

## Gotchas
- All sandbox tools use `_resolve_path()` to translate container paths to local paths — passing a raw local path will fail because the sandbox expects container paths (`backend/packages/harness/deerflow/sandbox/tools.py`)
- File operations use a locking mechanism to prevent concurrent read/write races — two tools operating on the same file will be serialized (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Host bash is gated: `is_host_bash_allowed()` returns False for local sandbox — bash commands are only available with AioSandboxProvider (`backend/packages/harness/deerflow/sandbox/security.py`)
- `str_replace` requires an exact match of `old_str` — if the string has changed since the last read, the replacement fails (`backend/packages/harness/deerflow/sandbox/tools.py`)
- `read_file` supports line ranges (offset/limit) but the offset is 1-based, not 0-based (`backend/packages/harness/deerflow/sandbox/tools.py`)

## Architecture
- Each tool is a standalone async function decorated with `@tool` from LangChain, accepting `Runtime` for state access (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Path resolution is centralized: `_resolve_path()` maps container paths (`/mnt/user-data/...`) to local filesystem paths using the sandbox's PathMapping (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Security checks are applied at tool entry: `is_host_bash_allowed()` gates bash, path traversal is prevented, read-only mounts are enforced (`backend/packages/harness/deerflow/sandbox/tools.py`, `backend/packages/harness/deerflow/sandbox/security.py`)
- Sandbox instance is obtained from graph state via `state["sandbox"]`, which is populated by SandboxMiddleware (`backend/packages/harness/deerflow/sandbox/tools.py`)

## Decisions
- File operation locking was added to prevent concurrent read/write races when multiple tools access the same file (`backend/packages/harness/deerflow/sandbox/tools.py`)
- `str_replace` was chosen over `sed` for file editing because it provides exact-match semantics that are safer for LLM-generated edits (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Host bash gating is based on sandbox provider type, not a config flag — this ensures bash is only available when the execution environment supports it (`backend/packages/harness/deerflow/sandbox/security.py`)

## Patterns
- Tool function signature: `async def tool_name(args, runtime: Runtime) -> str` — all tools follow this pattern (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Path resolution: `resolved = await sandbox._resolve_path(path)` before any file operation (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Error handling: tools catch exceptions and return error messages as strings rather than raising — this prevents the agent from crashing on tool errors (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Directory creation: `write_file` automatically creates parent directories if they don't exist (`backend/packages/harness/deerflow/sandbox/tools.py`)

## Conventions
- Tool names match Unix command names: `bash`, `read_file`, `write_file`, `str_replace`, `glob`, `grep`, `list_dir` (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Tool descriptions include parameter documentation and usage examples in the docstring (`backend/packages/harness/deerflow/sandbox/tools.py`)
- File paths in tool arguments use container paths (starting with `/mnt/user-data/`) (`backend/packages/harness/deerflow/sandbox/tools.py`)

## Security Considerations
- `is_host_bash_allowed()` returns False when using local sandbox — bash is only available with isolated Docker sandbox (`backend/packages/harness/deerflow/sandbox/security.py`)
- Path traversal protection: tools reject paths that attempt to escape the sandbox root (`backend/packages/harness/deerflow/sandbox/tools.py`)
- Read-only mounts are enforced at the sandbox level and checked by tools before write operations (`backend/packages/harness/deerflow/sandbox/tools.py`)

## Dependencies
- LangChain `@tool` decorator for tool registration (`backend/packages/harness/deerflow/sandbox/tools.py`)
- `deerflow.tools.types.Runtime` for typed runtime access (`backend/packages/harness/deerflow/sandbox/tools.py`)
- `deerflow.sandbox.sandbox.Sandbox` for the abstract sandbox interface (`backend/packages/harness/deerflow/sandbox/tools.py`)
