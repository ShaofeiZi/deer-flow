## 7de9b582 2026-05-08 He Wang
fix(tools): introduce Runtime type alias to eliminate Pydantic serialization warning (#2774)

* fix(tools): introduce Runtime type alias to eliminate Pydantic serialization warning

Add deerflow/tools/types.py with:

    Runtime = ToolRuntime[dict[str, Any], ThreadState]

Replace every runtime: ToolRuntime[ContextT, ThreadState] and
runtime: ToolRuntime[dict[str, Any], ThreadState] annotation in
sandbox/tools.py, present_file_tool.py, task_tool.py, view_image_tool.py,
and skill_manage_tool.py with the new Runtime alias.

The unbound ContextT TypeVar (default None) caused
PydanticSerializationUnexpectedValue warnings on every tool call because
LangChain's BaseTool._parse_input calls model_dump() on the auto-generated
args_schema while DeerFlow passes a dict as runtime context.
Binding the context to dict[str, Any] aligns Pydantic's serialization
expectations with reality and removes the noise from all run modes.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
Co-authored-by: Cursor <cursoragent@cursor.com>

* fix(tools): extend Runtime alias to setup_agent and update_agent tools

Replace bare ToolRuntime annotations in setup_agent_tool.py and
update_agent_tool.py with the shared Runtime alias introduced in the
previous commit, and add both tools to the Pydantic serialization
warning regression test (13 cases total).

Co-authored-by: Cursor <cursoragent@cursor.com>

* test(tools): loosen Pydantic warning filter to avoid version-specific format

Replace the brittle "field_name='context'" substring check with a looser
"context" match so the assertion stays valid if Pydantic changes its
internal warning format across versions.

Co-authored-by: Cursor <cursoragent@cursor.com>

* test(tools): simplify warning filter and clean up docstring

Remove the "context" substring condition from the Pydantic warning
filter — asserting that no PydanticSerializationUnexpectedValue fires
at all is both simpler and more comprehensive, since the test payload
contains only the tool's own args plus runtime.

Also update the module docstring to remove the version-specific warning
format example that was inconsistent with the looser filter.

Co-authored-by: Cursor <cursoragent@cursor.com>

---------

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>
Co-authored-by: Cursor <cursoragent@cursor.com>

- `backend/packages/harness/deerflow/sandbox/tools.py`
- `backend/packages/harness/deerflow/tools/builtins/present_file_tool.py`
- `backend/packages/harness/deerflow/tools/builtins/setup_agent_tool.py`
- `backend/packages/harness/deerflow/tools/builtins/task_tool.py`
- `backend/packages/harness/deerflow/tools/builtins/update_agent_tool.py`
- `backend/packages/harness/deerflow/tools/builtins/view_image_tool.py`
- `backend/packages/harness/deerflow/tools/skill_manage_tool.py`
- `backend/packages/harness/deerflow/tools/types.py`
  L7: # Concrete runtime type used by all DeerFlow tools.
  L8: # Using dict[str, Any] for the context parameter instead of the unbound ContextT
  L9: # TypeVar prevents PydanticSerializationUnexpectedValue warnings when LangChain
  L10: # calls model_dump() on a tool's auto-generated args_schema.

## 2b1fcb3e 2026-05-08 DanielWalnut
fix(task): remove max_turns parameter from task tool interface (#2783)

* fix(task): remove max_turns parameter from task tool interface

Subagents should always use their configured max_turns value. Exposing
this parameter allowed callers to override the admin-configured limit,
which is undesirable. The value is now exclusively driven by subagent
config (per-agent overrides and global defaults in config.yaml).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/tools/builtins/task_tool.py`

## c1b7f1d1 2026-05-09 DanielWalnut
feat: static system prompt with DynamicContextMiddleware for prefix-cache optimization (#2801)

* feat(middleware): inject dynamic context via DynamicContextMiddleware

Move memory and current date out of the system prompt and into a
dedicated <system-reminder> HumanMessage injected once per session
(frozen-snapshot pattern) via a new DynamicContextMiddleware.

This keeps the system prompt byte-exact across all users and sessions,
enabling maximum Anthropic/Bedrock prefix-cache reuse.

Key design decisions:
- ID-swap technique: reminder takes the first HumanMessage's ID
  (replacing it in-place via add_messages), original content gets a
  derived `{id}__user` ID (appended after). Preserves correct ordering.
- hide_from_ui: True on reminder messages so frontend filters them out.
- Midnight crossing: date-update reminder injected before the current
  turn's HumanMessage when the conversation spans midnight.
- INFO-level logging for production diagnostics.

Also adds prompt-caching breakpoint budget enforcement tests and
updates ClaudeChatModel docs to reference the new pattern.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(token-usage): log input/output token detail breakdown in middleware

Extend the LLM token usage log line to include input_token_details and
output_token_details (cache_creation, cache_read, reasoning, audio, etc.)
when present. Adds tests covering Anthropic cache detail logging from
both usage_metadata and response_metadata.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* fix: fix nginx

* fix(middleware): always inject date; gate memory on injection_enabled

Date injection is now unconditional — it is part of the static system
prompt replacement and should always be present. Memory injection
remains gated by `memory.injection_enabled` in the app config.

Previously the entire DynamicContextMiddleware was skipped when
injection_enabled was False, which also suppressed the date.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* fix(lint): format files and correct test assertions for token usage middleware

- ruff format dynamic_context_middleware.py and test_claude_provider_prompt_caching.py
- Remove unused pytest import from test_dynamic_context_middleware.py
- Fix two tests that asserted response_metadata fallback logic that
  doesn't exist: replace with tests that match actual middleware behavior

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* fix(middleware): address Copilot review comments on DynamicContextMiddleware

- Use additional_kwargs flag for reminder detection instead of content
  substring matching, so user messages containing '<system-reminder>'
  are not mistakenly treated as injected reminders
- Generate stable UUID when original HumanMessage.id is None to prevent
  ambiguous 'None__user' derived IDs and message collisions
- Downgrade per-turn no-op log to DEBUG; keep actual injection events at INFO
- Add two new tests: missing-id UUID fallback and user-text false-positive

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

---------

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
  L261: # Always inject current date (and optionally memory) as <system-reminder> into the
  L262: # first HumanMessage to keep the system prompt fully static for prefix-cache reuse.
- `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`
  L809: # Build and return the fully static system prompt.
  L810: # Memory and current date are injected per-turn via DynamicContextMiddleware
  L811: # as a <system-reminder> in the first HumanMessage, keeping this prompt
  L812: # identical across users and sessions for maximum prefix-cache reuse.
- `backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py`
  L1: """Middleware to inject dynamic context (memory, current date) as a system-reminder.
  L27: """
  L51: """Return the first <current_date> value found in *content*, or None."""
  L57: """Scan messages in reverse and return the most recently injected date.
  L62: """
  L71: """Inject memory and current date into HumanMessages as a <system-reminder>.
  L86: """
  L96: # Memory injection is gated by injection_enabled; date is always included.
  L122: """Return (reminder_msg, user_msg) using the ID-swap technique.
  L130: """
  L160: # ── First turn: inject full reminder as a separate HumanMessage ─────
  L175: # ── Same day: nothing to do ──────────────────────────────────────────
  L178: # ── Midnight crossed: inject date-update reminder as a separate HumanMessage ──
- `backend/packages/harness/deerflow/agents/middlewares/token_usage_middleware.py`
- `backend/packages/harness/deerflow/models/claude_provider.py`

## 7caf03e9 2026-05-09 KiteEater
fix(packaging): add postgres extra for store/checkpointer supportFix postgres extra install guidance (#2584)

* Fix postgres extra install guidance

* Fix postgres install message lint

* Format postgres install messages

* Fix postgres install guidance and config docs

- `backend/packages/harness/deerflow/config/checkpointer_config.py`
- `backend/packages/harness/deerflow/persistence/engine.py`
- `backend/packages/harness/deerflow/runtime/checkpointer/provider.py`
- `backend/packages/harness/deerflow/runtime/store/provider.py`

## 0d1053ca 2026-05-09 yangyufan
fix(uploads): add Windows support for safe symlink-protected uploads (#2794)

* fix(uploads): add Windows support for safe symlink-protected uploads

* fix(uploads): update tests and translate comments;

- `backend/packages/harness/deerflow/uploads/manager.py`
  L146: # POSIX: O_NOFOLLOW makes open() fail with ELOOP if dest is a symlink.
  L170: # Windows: no O_NOFOLLOW available. Uses a second lstat immediately before open()
  L171: # to narrow the TOCTOU window, then fstat after open() as a further defence.
  L172: # Note: a narrow race window remains between the pre-open lstat and open(); the
  L173: # path-traversal check mitigates escapes from base_dir but cannot prevent an
  L174: # attacker who can atomically replace dest with a symlink after the check.

## f76e4e35 2026-05-09 DanielWalnut
fix title generation with dynamic context reminder (#2830)

- `backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py`
  L57: """Return whether *message* is a hidden dynamic-context reminder."""
- `backend/packages/harness/deerflow/agents/middlewares/title_middleware.py`

## 881ff712 2026-05-09 DanielWalnut
fix(harness): preserve dynamic context across summarization (#2823)

- `backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py`
  L77: """Return whether *message* is a hidden dynamic-context reminder."""
  L82: """Return whether *message* can receive a dynamic-context reminder."""
- `backend/packages/harness/deerflow/agents/middlewares/summarization_middleware.py`
  L190: """Keep hidden dynamic-context reminders out of summary compression.
  L195: """

## 1c96a6af 2026-05-09 Eilen Shin
fix: keep new agent bootstrap in user scope (#2784)

- `backend/packages/harness/deerflow/tools/builtins/setup_agent_tool.py`

## 08ee7ade 2026-05-09 DanielWalnut
fix(lint): remove duplicate is_dynamic_context_reminder definition (#2837)

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>

- `backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py`

## 5127f08e 2026-05-10 YuJitang
enable token usage by default (#2841)

- `backend/packages/harness/deerflow/config/token_usage_config.py`

## 94da8f67 2026-05-10 Xinmin Zeng
fix(scripts): preserve uv extras across `make dev` restarts (#2754) (#2767)

`make dev` ran `uv sync` unconditionally on every restart, wiping any
optional extras the user had installed manually with
`uv sync --all-packages --extra postgres`. The Docker image-build path
already solved this via the `UV_EXTRAS` build-arg in backend/Dockerfile;
the local serve.sh path and the docker-compose-dev startup command
were the remaining outliers.

`scripts/serve.sh` now resolves extras before `uv sync`:
  1. honors `UV_EXTRAS` (parity with backend/Dockerfile and
     docker/docker-compose.yaml — no new convention introduced);
  2. falls back to parsing config.yaml — `database.backend: postgres`
     or legacy `checkpointer.type: postgres` auto-pins
     `--extra postgres`, so the common case needs zero extra config.
  3. detector stderr is no longer suppressed, so whitelist warnings or
     crashes surface to the dev terminal (review feedback).

Detection lives in `scripts/detect_uv_extras.py` (stdlib-only — has to
run before the venv exists). Extra names are validated against
`^[A-Za-z][A-Za-z0-9_-]*$` so a stray shell metacharacter in `.env`
cannot reach `uv sync` downstream (defense in depth).

`docker/docker-compose-dev.yaml`'s startup command is now extracted to
`docker/dev-entrypoint.sh` (review feedback — the inline command had
grown to a ~350-char one-liner). The script:
  - parses comma/whitespace-separated UV_EXTRAS, applying the same
    `^[A-Za-z][A-Za-z0-9_-]*$` whitelist as the local detector;
  - emits one `--extra X` flag per token, so `UV_EXTRAS=postgres,ollama`
    works in Docker dev too (harmonized with local — review feedback);
  - calls `uv sync --all-packages` (PR #2584) so workspace member
    extras (deerflow-harness's postgres extra) are installed;
  - keeps the existing self-heal `(uv sync || (recreate venv && retry))`
    branch;
  - exposes `--print-extras` for dry-run testing.

The compose file mounts the script read-only at runtime, so script
edits take effect on `make docker-restart` without an image rebuild.

The `--no-sync` alternative (a separate suggestion in the issue thread)
was considered but rejected for dev paths because it would drop the
self-heal branch and the auto-pickup of new pyproject deps. `--no-sync`
is already in use for the production CMD (`backend/Dockerfile:101`)
where it's appropriate.

Updates the asyncpg-missing error message to include the
`--all-packages` flag (matching #2584) plus the persistent install flow,
and expands `config.example.yaml` so all three install paths
(local / docker dev / docker image build) are documented with their
multi-extra capabilities.

Tests:
  - `tests/test_detect_uv_extras.py` (21 tests) — local-path env parsing,
    YAML edge cases, env-vs-config precedence, whitelist rejection of
    shell metacharacters.
  - `tests/test_dev_entrypoint.py` (15 tests) — docker-path validation
    via `--print-extras`, multi-extra parsing, metacharacter abort.
  - `tests/test_persistence_scaffold.py` (22 tests, unchanged) — passes
    with the merged `--all-packages --extra postgres` error message.

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/persistence/engine.py`

## 9892a7d4 2026-05-10 YuJitang
fix: bucket subagent token usage into parent run totals (#2838)

* fix: bucket subagent token usage into RunRow.subagent_tokens

Add caller-bucketed token tracking to RunJournal so subagent and
middleware LLM calls are written to the correct RunRow columns instead
of all falling into lead_agent_tokens (default 0).

- RunJournal: accumulate _lead_agent_tokens / _subagent_tokens /
  _middleware_tokens in on_llm_end, deduped by langchain run_id.
  Add record_external_llm_usage_records() for external sources
  (respects track_token_usage flag). Return caller buckets from
  get_completion_data().
- SubagentTokenCollector: new lightweight callback handler that
  collects LLM usage within subagent execution.
- SubagentExecutor: wire collector into subagent run_config and sync
  records to SubagentResult on every chunk (timeout/cancel safe).
- SubagentResult: add token_usage_records and usage_reported fields.
- task_tool: report subagent usage to parent RunJournal on every
  terminal status (COMPLETED/FAILED/CANCELLED/TIMED_OUT), including
  the CancelledError path, guarded against double-reporting.

No DB migration needed — RunRow columns already exist.

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* fix: address token usage review feedback

* Address review follow-ups

---------

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/runtime/journal.py`
  L66: # Caller-bucketed token accumulators
  L71: # Dedup: LangChain may fire on_llm_end multiple times for the same run_id
  L226: # Token accumulation (dedup by langchain run_id to avoid double-counting
  L227: # when the callback fires more than once for the same response)
  L355: """Record token usage from external sources (e.g., subagents).
  L363: """
- `backend/packages/harness/deerflow/subagents/executor.py`
  L423: # Token collector for subagent LLM calls
- `backend/packages/harness/deerflow/subagents/token_collector.py`
  L1: """Callback handler that collects LLM token usage within a subagent.
  L6: """
  L16: """Lightweight callback handler that collects LLM token usage within a subagent."""
  L62: """Return a copy of the accumulated usage records."""
- `backend/packages/harness/deerflow/tools/builtins/task_tool.py`
  L31: """Return whether a background subagent result is safe to clean up."""
  L36: """Poll until the background subagent reaches a terminal status or we run out of polls."""
  L48: """Keep polling a cancelled subagent until it can be safely removed."""
  L80: """Find a callback handler with ``record_external_llm_usage_records`` in the runtime config."""
  L96: """Report subagent token usage to the parent RunJournal, if available.
  L99: """
  L360: # Wait (shielded) for the subagent to reach a terminal state so the
  L361: # final token usage snapshot is reported to the parent RunJournal
  L362: # before the parent worker persists get_completion_data().
  L369: # Report whatever the subagent collected (even if we timed out).

## 30a58462 2026-05-10 Maz Benoscar
fix(tools): make write_file append discoverable in model-facing schema (#2843)

* fix: make tool argument behavior discoverable

The write_file tool already supported append=false by default with append=true for end-of-file writes, but the parsed docstring did not describe append in the model-facing schema. This records the overwrite default and append path in the tool description, adds resilient schema regression coverage, and keeps backend sandbox docs aligned.

The regression now also checks that every public parameter in the existing tool schema test matrix has a description. Enabling docstring parsing on setup_agent and update_agent fills the two existing gaps with their existing Args docs instead of duplicating descriptions elsewhere.

Constraint: Issue #2831 asks for a small docstring/schema discoverability fix without changing runtime file-writing behavior
Rejected: Changing write_file defaults | would alter existing overwrite semantics and broaden the fix beyond schema discoverability
Rejected: Exact phrase assertions | too brittle for future docstring rewording while testing the same behavior
Confidence: high
Scope-risk: narrow
Directive: Keep model-facing tool parameters documented through parsed docstrings or equivalent schema descriptions
Tested: cd backend && uv run pytest tests/test_setup_agent_tool.py tests/test_update_agent_tool.py tests/test_tool_args_schema_no_pydantic_warning.py tests/test_sandbox_tools_security.py::test_str_replace_and_append_on_same_path_should_preserve_both_updates -q
Tested: cd backend && uv run ruff check packages/harness/deerflow/sandbox/tools.py packages/harness/deerflow/tools/builtins/setup_agent_tool.py packages/harness/deerflow/tools/builtins/update_agent_tool.py tests/test_tool_args_schema_no_pydantic_warning.py
Not-tested: Full backend test suite
Co-authored-by: OmX <omx@oh-my-codex.dev>

* Fix the lint error

---------

Co-authored-by: OmX <omx@oh-my-codex.dev>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/sandbox/tools.py`
  L1502: """Write text content to a file. By default this overwrites the target file; set append to true to add content to the end without replacing existing content.
- `backend/packages/harness/deerflow/tools/builtins/setup_agent_tool.py`
- `backend/packages/harness/deerflow/tools/builtins/update_agent_tool.py`

## 2b5bece7 2026-05-11 KiteEater
fix(harness): reset local sandbox singleton with provider lifecycle (#2834)

* Fix local sandbox singleton reset on provider lifecycle

* Fix local sandbox singleton reset on provider reset

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`
  L124: # reset_sandbox_provider() must also clear the module singleton.
  L129: # LocalSandboxProvider has no extra resources beyond the shared
  L130: # singleton, so shutdown uses the same cleanup path as reset.
- `backend/packages/harness/deerflow/sandbox/sandbox_provider.py`
  L41: """Clear cached state that survives provider instance replacement."""

## 813d3c94 2026-05-11 Willem Jiang
fix(subagents): consolidate system_prompt and skills into single SystemMessage (#2701)

* fix(subagents): consolidate system_prompt and skills into single SystemMessage

  Some LLM APIs (vLLM, Xinference, Chinese LLM providers) reject multiple
  system messages with \”System message must be at the beginning.\” The
  subagent executor was sending separate SystemMessages for the configured
  system_prompt and each loaded skill, which caused failures when calling
  task tool with sub-agents.

  Merge system_prompt and all skill content into one SystemMessage in the
  initial state, and pass system_prompt=None to create_agent() so the
  factory doesn't prepend a second one.

Fixes #2693

* fix(subagents): update SubagentConfig.system_prompt to str | None and add astream regression test

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/2ee03a26-e19b-4106-abc5-c76a2906383b

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* fixed the lint error

* fix the lint error in the backend

* fix the unit test error of test_subagent_executor

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/subagents/config.py`
- `backend/packages/harness/deerflow/subagents/executor.py`
  L289: # system_prompt is included in initial state messages (see _build_initial_state)
  L290: # to avoid multiple SystemMessages which some LLM APIs don't support.
  L376: # Combine system_prompt and skills into a single SystemMessage.
  L377: # Some LLM APIs reject multiple SystemMessages with
  L378: # "System message must be at the beginning."

## 2eb11f97 2026-05-11 Nan Gao
fix(runtime): persist run message summaries (#2850)

* fix(runtime): persist run message summaries (#2849)

* fix(runtime): dedupe run message summaries

- `backend/packages/harness/deerflow/runtime/journal.py`
  L93: """Extract displayable text from a message's mixed content shape."""
  L123: """Update run-level convenience fields for persisted run rows."""
  L126: # ``last_ai_message`` should represent the lead agent's user-facing
  L127: # answer. Middleware/subagent model calls and empty tool-call-only
  L128: # AI messages must not overwrite the last useful assistant text.

## de253e4a 2026-05-11 Yi Tang
feat(run): Propagates `model_name` from the gateway request through the runtime and persistence stack to the SQLite database. (#2775)

* feat(run): propagate model_name from gateway request context to persistence layer

Pass model_name through the full run creation pipeline — from
RunCreateRequest.context in the gateway, through RunManager, to the
RunStore interface and SQL persistence. This enables client-specified
model selection to be recorded per-run in the database.

* feat(run): add model allowlist validation and effective model name capture

- Validate model_name against allowlist in gateway services.py using
  get_app_config().get_model_config()
- Truncate model_name to 128 chars to match DB column constraint
- In worker.py, capture effective model name from agent.metadata after
  agent creation and persist if resolved differently than requested

* feat(run): add defense-in-depth model_name normalization and round-trip persistence tests

- Add _normalize_model_name() to RunRepository for whitespace stripping
  and 128-char truncation before DB writes.
- Add round-trip unit tests for model_name creation and default None
  in test_run_manager.py.

* fix(run): coerce non-string model_name values before strip/truncate in _normalize_model_name

* fix(gateway): add runtime type guard for model_name coercion in gateway services

Add isinstance check and str() coercion before calling .strip() to prevent
AttributeError when non-string types (int, None, etc.) flow through the
gateway. Paired with SQL integration test for end-to-end model_name
persistence across gateway → langgraph → persistence layer.

* fix(run): drop Alembic migration for model_name (no-op) and expose public update method on RunManager

- Drop a1b2c3d4e5f6 migration: model_name already exists in RunRow schema
  and is auto-created via Base.metadata.create_all() at startup
- Add update_model_name() public method to RunManager to replace the private
  _persist_to_store call in worker.py, preserving internal locking/persistence

- `backend/packages/harness/deerflow/persistence/run/sql.py`
  L28: """Normalize model_name for storage: strip whitespace, truncate to 128 chars."""
- `backend/packages/harness/deerflow/runtime/runs/manager.py`
  L143: """Update the model name for a run."""
- `backend/packages/harness/deerflow/runtime/runs/store/base.py`
- `backend/packages/harness/deerflow/runtime/runs/store/memory.py`
- `backend/packages/harness/deerflow/runtime/runs/worker.py`
  L233: # Capture the effective (resolved) model name from the agent's metadata.
  L234: # _resolve_model_name in agent.py may return the default model if the
  L235: # requested name is not in the allowlist — this update ensures the
  L236: # persisted model_name reflects the actual model used.

## bedbf229 2026-05-11 AochenShen99
fix(harness): wrap async-only config tools for sync client execution (#2878)

* fix(harness): wrap async-only config tools for sync clients

* refactor(tools): share async tool sync wrapper

- `backend/packages/harness/deerflow/mcp/tools.py`
- `backend/packages/harness/deerflow/tools/skill_manage_tool.py`
- `backend/packages/harness/deerflow/tools/sync.py`
  L1: """Utilities for invoking async tools from synchronous agent paths."""
  L12: # Shared thread pool for sync tool invocation in async environments.
  L19: """Build a synchronous wrapper for an asynchronous tool coroutine."""
- `backend/packages/harness/deerflow/tools/tools.py`
  L38: """Attach a sync wrapper to async-only tools used by sync agent callers."""

## 20d2d2b3 2026-05-12 Nan Gao
fix(middleware): Handle invalid tool calls in dangling pairing middleware (#2890) (#2891)

- `backend/packages/harness/deerflow/agents/middlewares/dangling_tool_call_middleware.py`
  L39: """Return normalized tool calls from structured fields or raw provider payloads.
  L47: """

## 68d8caec 2026-05-12 Xinmin Zeng
fix(agents): make update_agent honor runtime.context user_id like setup_agent (#2867)

* fix(agents): make update_agent honor runtime.context user_id like setup_agent

PR #2784 hardened setup_agent to prefer runtime.context["user_id"] (set by
inject_authenticated_user_context from the auth-validated request) over the
contextvar, so an agent created during the bootstrap flow always lands under
users/<auth_uid>/agents/<name>. update_agent was left calling
get_effective_user_id() unconditionally — the same class of bug that produced
issues #2782 / #2862 still applies whenever the contextvar is not available
on the executing task (background work, future cross-process drivers,
checkpoint resume on a different task). In that regime update_agent silently
routes writes to users/default/agents/<name>, corrupting the shared default
bucket and losing the user's edit.

Extract the resolution policy into a shared resolve_runtime_user_id helper
on deerflow.runtime.user_context and route both setup_agent and update_agent
through it so the two halves of the lifecycle stay in lockstep.

Add load-bearing end-to-end tests that drive a real langchain.agents
create_agent graph with a fake LLM, exercising the full pipeline:

  HTTP wire format
    -> app.gateway.services.start_run config-assembly
    -> deerflow.runtime.runs.worker._build_runtime_context
    -> langchain.agents create_agent graph
    -> ToolNode dispatch (sync + async + sub-graph + ContextThreadPoolExecutor)
    -> setup_agent / update_agent

The negative-control tests intentionally land in users/default/ to prove the
positive tests are actually load-bearing rather than vacuously passing.

The new test_update_agent_e2e_user_isolation suite included a test that
failed against main and now passes after this fix.

* style: ruff format on new e2e tests

* test(e2e): real-server HTTP test driving setup_agent through the full ASGI stack

Adds tests/test_setup_agent_http_e2e_real_server.py — a single load-bearing
test that drives the entire FastAPI gateway through starlette.testclient.
TestClient with no mocks above the LLM:

  - lifespan boots (config, sqlite engine, LangGraph runtime, channels)
  - POST /api/v1/auth/register (real password hash, real sqlite write,
    issues access_token + csrf_token cookies)
  - POST /api/threads (real thread_meta + checkpoint creation)
  - POST /api/threads/{id}/runs/stream with the exact wire shape the React
    frontend sends (assistant_id + input + config + context with
    agent_name/is_bootstrap)
  - AuthMiddleware -> CSRFMiddleware -> require_permission ->
    start_run -> inject_authenticated_user_context ->
    asyncio.create_task(run_agent) -> worker._build_runtime_context ->
    Runtime injection -> ToolNode dispatch -> real setup_agent
  - Asserts SOUL.md is under users/<authenticated_uid>/agents/<name>/
    and NOT under users/default/agents/<name>/.

DEER_FLOW_HOME and the sqlite path are redirected into tmp_path so the test
never touches the real .deer-flow directory or developer database. The only
patch above the LLM boundary is replacing create_chat_model with a fake that
emits a single setup_agent tool_call.

This is the "真实验证" answer: it reproduces what curl-against-uvicorn would
do, minus the network socket layer.

* test: address Copilot review on user-isolation e2e tests

- Drop "currently expected to FAIL" wording from update_agent e2e docstring
  and header (Copilot review): the fix is in this PR, the test pins the
  corrected behaviour rather than driving a future change.
- Rephrase the assertion failure messages from "BUG:" to "REGRESSION:" to
  match the test's role on the fixed branch.
- Bound _drain_stream with a wall-clock timeout, a max-bytes cap, and an
  early break on the "event: end" SSE frame (Copilot review). Stops the
  test from hanging on a stuck run or runaway heartbeat loop.
- Replace the misleading "patch both module aliases" comment with an
  explanation of why patching lead_agent.agent.create_chat_model is the
  only correct target (Copilot review): lead_agent rebinds the symbol
  into its own namespace at import time, so patching deerflow.models is
  too late.

* test(refactor): address WillemJiang review on user-isolation e2e tests

- Extract the duplicated FakeToolCallingModel (and a
  build_single_tool_call_model helper) into tests/_agent_e2e_helpers.py.
  All three e2e files now import from the shared module instead of
  redefining the shim locally.
- Convert the manual p.start() / p.stop() try/finally blocks in
  test_update_agent_e2e_user_isolation.py to contextlib.ExitStack so
  patch lifecycle is Pythonic and exception-safe.
- Lift the isolated_app fixture's private-attribute resets into a
  named _reset_process_singletons helper with a comment block
  explaining why each singleton has to be invalidated for true e2e
  isolation, and why raising=False is intentional. Makes the
  fragility visible and the intent self-documenting rather than
  leaving the resets inline as opaque monkeypatch calls.

Net change: -59 lines (143 -> 84) across the three test files, with
every assertion intact. Full suite remains 69 passed / lint clean.

* test(e2e): make real-server test self-supply its config

CI's actions/checkout only ships config.example.yaml (the real config.yaml
is gitignored), so the production config-discovery search
(./config.yaml -> ../config.yaml -> $DEER_FLOW_CONFIG_PATH) finds nothing
and the test fails at lifespan boot with FileNotFoundError. The dev-machine
run passed only because a local config.yaml happened to exist.

Write a minimal AppConfig-valid yaml into tmp_path and pin
DEER_FLOW_CONFIG_PATH to it. The yaml carries just what the schema requires
(a single fake-test-model entry, LocalSandboxProvider, sqlite database).
The LLM never gets instantiated because the test patches create_chat_model
on the lead agent module, so the api_key/base_url stay placeholders.

Verified by hiding the local config.yaml to mirror the CI checkout — the
test now passes in both environments.

- `backend/packages/harness/deerflow/runtime/user_context.py`
  L113: """Single source of truth for a tool/middleware's effective user_id.
  L131: """
- `backend/packages/harness/deerflow/tools/builtins/setup_agent_tool.py`
- `backend/packages/harness/deerflow/tools/builtins/update_agent_tool.py`
  L121: # ``resolve_runtime_user_id`` prefers ``runtime.context["user_id"]`` (set by
  L122: # the gateway from the auth-validated request) and falls back to the
  L123: # contextvar, then DEFAULT_USER_ID. This matches setup_agent so a user
  L124: # creating an agent and later refining it always touches the same files,
  L125: # even if the contextvar gets lost across an async/thread boundary
  L126: # (issue #2782 / #2862 class of bugs).

## e9deb6c2 2026-05-12 He Wang
perf(harness): push thread metadata filters into SQL (#2865)

* perf(harness): push thread metadata filters into SQL

Replace Python-side metadata filtering (5x overfetch + in-memory match)
with database-side json_extract predicates so LIMIT/OFFSET pagination
is exact regardless of match density.

Co-Authored-By: Claude Opus 4 <noreply@anthropic.com>

* fix(harness): add dialect-aware JsonMatch compiler for type-safe metadata SQL filters

Replace SQLAlchemy JSON index/comparator APIs with a custom JsonMatch
ColumnElement that compiles to json_type/json_extract on SQLite and
jsonb_typeof/->>/-> on PostgreSQL. Tighten key validation regex to
single-segment identifiers, handle None/bool/numeric value types with
json_type-based discrimination, and strengthen test coverage for edge
cases and discriminability.

Co-Authored-By: Claude Opus 4 <noreply@anthropic.com>

* fix(harness): address Copilot review comments on JSON metadata filters

- Use json_typeof instead of jsonb_typeof in PostgreSQL compiler; the
  metadata_json column is JSON not JSONB so jsonb_typeof would error at
  runtime on any PostgreSQL backend
- Align _is_safe_json_key with json_match's _KEY_CHARSET_RE so keys
  containing hyphens or leading digits are not silently skipped
- Add thread_id as secondary ORDER BY in search() to make pagination
  deterministic when updated_at values collide; remove asyncio.sleep
  from the pagination regression test

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>

* fix(harness): address remaining review comments on metadata SQL filters

- Remove _is_safe_json_key() and reuse json_match ValueError to avoid
  validator drift (Copilot #3217603895, #3217411616)
- Raise ValueError when all metadata keys are rejected so callers never
  get silent unfiltered results (WillemJiang)
- Fix integer precision: split int/float branches, bind int as Integer()
  with INTEGER/BIGINT CAST instead of float() coercion (Copilot #3217603972)
- Fix jsonb_typeof -> json_typeof on JSON column (Copilot #3217411579)
- Replace manual _cleanup() calls with async yield fixture so teardown
  always runs (Copilot #3217604019)
- Remove asyncio.sleep(0.01) pagination ordering; use thread_id secondary
  sort instead (Copilot #3217411636)
- Add type annotations to _bind/_build_clause/_compile_* and remove EOL
  comments from _Dialect fields (coding.mdc)
- Expand test coverage: boolean/null/mixed-type/large-int precision,
  partial unsafe-key skip with caplog assertion

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* fix(harness): address third-round Copilot review comments on JsonMatch

- Reject unsupported value types (list, dict, ...) in JsonMatch.__init__
  with TypeError so inherit_cache=True never receives an unhashable value
  and callers get an explicit error instead of silent str() coercion
  (Copilot #3217933201)
- Upgrade int bindparam from Integer() to BigInteger() to align with
  BIGINT CAST and avoid overflow on large integers (Copilot #3217933252)
- Catch TypeError alongside ValueError in search() so non-string metadata
  keys are warned and skipped rather than raising unexpectedly
  (Copilot #3217933300)
- Add three tests: json_match rejects unsupported value types, search()
  warns and raises on non-string key, search() warns and raises on
  unsupported value type

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* fix(harness): address fourth-round Copilot review comments on JsonMatch

- Add CASE WHEN guard for PostgreSQL integer matching: json_typeof returns
  'number' for both ints and floats; wrap CAST in CASE with regex guard
  '^-?[0-9]+$' so float rows never trigger CAST error (Copilot #3218413860)
- Validate isinstance(key, str) before regex match in JsonMatch.__init__
  so non-string keys raise ValueError consistently instead of TypeError
  from re.match (Copilot #3218413900)
- Include exception message in metadata filter skip warning so callers
  can distinguish invalid key from unsupported value type (Copilot #3218413924)
- Update tests: assert CASE WHEN guard in PG int compilation, cover
  non-string key ValueError in test_json_match_rejects_unsafe_key

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* fix(harness): align ThreadMetaStore.search() signature with sql.py implementation

Use `dict[str, Any]` for `metadata` and `list[dict[str, Any]]` as return
type in base class and MemoryThreadMetaStore to resolve an LSP signature
mismatch; also correct a test docstring that cited the wrong exception type.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* fix(harness): surface InvalidMetadataFilterError as HTTP 400 in search endpoint

Replace bare ValueError with a domain-specific InvalidMetadataFilterError
(subclass of ValueError) so the Gateway handler can catch it and return
HTTP 400 instead of letting it bubble up as a 500.

Co-Authored-By: Claude Opus 4 <noreply@anthropic.com>

* fix(harness): sanitize metadata keys in log output to prevent log injection

Use ascii() instead of %r to escape control characters in client-supplied
metadata keys before logging, preventing multiline/forged log entries.

Co-Authored-By: Claude Opus 4 <noreply@anthropic.com>

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* fix(harness): validate metadata filters at API boundary and dedupe key/value rules

- Add Pydantic ``field_validator`` on ``ThreadSearchRequest.metadata`` so
  unsafe keys / unsupported value types are rejected with HTTP 422 from
  both SQL and memory backends (closes Copilot review 3218830849).
- Export ``validate_metadata_filter_key`` / ``validate_metadata_filter_value``
  (and ``ALLOWED_FILTER_VALUE_TYPES``) from ``json_compat`` and have
  ``JsonMatch.__init__`` reuse them — the Gateway-side validator and the
  SQL-side ``JsonMatch`` constructor now share one admission rule and
  cannot drift.
- Format ``InvalidMetadataFilterError`` rejected-keys list as a
  comma-separated plain string instead of a Python list repr so the
  surfaced HTTP 400 detail is readable (closes Copilot review 3218830899).
- Update router tests to cover both 422 boundary paths plus the 400
  defense-in-depth path when a backend still raises the error.

Co-authored-by: Cursor <cursoragent@cursor.com>

* fix(harness): harden JsonMatch compile-time key validation against __init__ bypass

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>

* fix: address review feedback on metadata filter SQL push-down

- Add signed 64-bit range check to validate_metadata_filter_value; give
  out-of-range ints a distinct TypeError message.

- Replace assert guards in _compile_sqlite/_compile_pg with explicit
  if/raise so they survive python -O optimisation.

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4 <noreply@anthropic.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>
Co-authored-by: Cursor <cursoragent@cursor.com>

- `backend/packages/harness/deerflow/persistence/json_compat.py`
  L1: """Dialect-aware JSON value matching for SQLAlchemy (SQLite + PostgreSQL)."""
  L16: # Key is interpolated into compiled SQL; restrict charset to prevent injection.
  L19: # Allowed value types for metadata filter values (same set accepted by JsonMatch).
  L22: # SQLite raises an overflow when binding values outside signed 64-bit range;
  L23: # PostgreSQL overflows during BIGINT cast. Reject at validation time instead.
  L29: """Return True if *key* is safe for use as a JSON metadata filter key.
  L35: """
  L40: """Return True if *value* is an allowed type for a JSON metadata filter.
  L51: """
  L61: """Dialect-portable ``column[key] == value`` for JSON columns.
  L69: """
  L96: """Per-dialect names used when emitting JSON type/value comparisons."""
  L103: # None for SQLite where json_type already returns 'integer'/'real';
  L104: # regex literal for PostgreSQL where json_typeof returns 'number' for
  L105: # both ints and floats, so an extra guard prevents CAST errors on floats.
  L150: # bool check must precede int check — bool is a subclass of int in Python
  L158: # CASE prevents CAST error when json_typeof = 'number' also matches floats
- `backend/packages/harness/deerflow/persistence/thread_meta/__init__.py`
- `backend/packages/harness/deerflow/persistence/thread_meta/base.py`
  L24: """Raised when all client-supplied metadata filter keys are rejected."""
- `backend/packages/harness/deerflow/persistence/thread_meta/memory.py`
- `backend/packages/harness/deerflow/persistence/thread_meta/sql.py`
  L138: # Comma-separated plain string (no list repr / nested
  L139: # quoting) so the 400 detail surfaced by the Gateway is
  L140: # easy for clients to read. Sorted for determinism.

## 2a1ac06b 2026-05-13 Eilen Shin
fix(persistence): reuse token usage model grouping expression (#2910)

- `backend/packages/harness/deerflow/persistence/run/sql.py`

## f1a0ab69 2026-05-13 Xinmin Zeng
fix(tools): preserve tool_search promotions across re-entrant get_available_tools (#2885)

* fix(tools): preserve tool_search promotions across re-entrant get_available_tools

Closes #2884.

``get_available_tools`` used to unconditionally call
``reset_deferred_registry()`` and rebuild a fresh ``DeferredToolRegistry``
on every invocation. That works for the first call of a request (the
ContextVar starts at its default of ``None``), but any RE-ENTRANT call
during the same async context — e.g. ``task_tool`` building a subagent's
toolset, or a custom middleware that rebuilds tools mid-run — wiped any
``tool_search`` promotions the parent agent had already made. The
``DeferredToolFilterMiddleware`` would then re-hide those tools from the
next model call, leaving the agent able to see a tool's name (via the
prior ``tool_search`` result that's still in conversation history) but
unable to invoke it.

Fix: when the ContextVar already holds a registry, reuse it instead of
rebuilding. Fresh requests still get a fresh registry because each new
graph run starts in a new asyncio task with the ContextVar at ``None``.

## Verification

- Unit-level reproduction (``test_get_available_tools_resets_registry_wiping_promotion``):
  promote a tool in the registry, call ``get_available_tools`` again, assert
  the promotion is preserved. Fails on main, passes on this branch.

- Graph-execution reproduction (two tests): drive a real
  ``langchain.agents.create_agent`` graph with the real
  ``DeferredToolFilterMiddleware`` through two model turns, including one
  that issues a re-entrant ``get_available_tools`` call to simulate the
  task_tool subagent path.

- Real-LLM end-to-end (``test_deferred_tool_promotion_real_llm.py``,
  opt-in via ``ONEAPI_E2E=1``): drives the same flow against a real
  OpenAI-compatible model (verified on GPT-5.4-mini through the one-api
  gateway), watches the model call the promoted ``fake_calculator``
  through the deferred-filter middleware, and asserts the right arithmetic
  result. Passes against the fixed branch.

- Companion update to ``test_tool_deduplication.py``: dropped the
  ``@patch("deerflow.tools.tools.reset_deferred_registry")`` decorators
  because the symbol is no longer imported there.

- Test fixtures in the new files patch ``deerflow.tools.tools.get_app_config``
  with a minimal ``model_construct``-ed ``AppConfig`` instead of calling
  the real loader, so they never trigger ``_apply_singleton_configs`` and
  never leak ``_memory_config``/``_title_config``/… mutations into the
  rest of the suite.

Full backend suite: 3208 passed / 14 skipped / 0 failed. ruff check + format clean.

* fix(tools): address Copilot review on #2885

- tools.py: rewrite the reuse-path comment to spell out (a) why we don't
  reconcile the registry against the current ``mcp_tools`` snapshot — the
  MCP cache doesn't refresh mid-graph-run, the lead agent's ``ToolNode``
  is already bound to the previous tool set anyway, and ``promote()``
  drops the entry so a naive re-sync misclassifies promotions as new
  tools — and (b) why the log uses ``max(0, …)`` to avoid negative
  counts when the cache shrinks between snapshots.
- Replace direct ``ts_mod._registry_var.set(None)`` in test fixtures with
  the public ``reset_deferred_registry()`` helper so tests don't couple
  to module internals.
- Correct the docstring path in ``test_deferred_tool_registry_promotion.py``
  to match the actual monkeypatch target (``deerflow.mcp.cache.get_cached_mcp_tools``).
- Rename
  ``test_get_available_tools_resets_registry_wiping_promotion`` to
  ``test_get_available_tools_preserves_promotions_across_reentrant_calls``
  so the test name describes the contract being asserted, not the bug it
  originally reproduced.

Full backend suite: 3208 passed / 14 skipped. Real-LLM e2e: 1 passed.

- `backend/packages/harness/deerflow/tools/tools.py`
  L136: # Reuse the existing registry if one is already set for
  L137: # this async context. ``get_available_tools`` is
  L138: # re-entered whenever a subagent is spawned
  L139: # (``task_tool`` calls it to build the child agent's
  L140: # toolset), and previously we used to unconditionally
  L141: # rebuild the registry — wiping out the parent agent's
  L142: # tool_search promotions. The
  L143: # ``DeferredToolFilterMiddleware`` then re-hid those
  L144: # tools from subsequent model calls, leaving the agent
  L145: # able to see a tool's name but unable to invoke it
  L146: # (issue #2884). ``contextvars`` already gives us the
  L147: # lifetime semantics we want: a fresh request / graph
  L148: # run starts in a new asyncio task with the
  L149: # ContextVar at its default of ``None``, so reuse is
  L150: # only triggered for re-entrant calls inside one run.
  L151: #
  L152: # Intentionally NOT reconciling against the current
  L153: # ``mcp_tools`` snapshot. The MCP cache only refreshes
  L154: # on ``extensions_config.json`` mtime changes, which
  L155: # in practice happens between graph runs — not inside
  ... (truncated)

## eab7ae3d 2026-05-13 YuJitang
feat: stream subagent token usage to header via terminal task events    (#2882)

* feat: real-time subagent token usage display in header and per-turn

Backend:
- Persist subagent token usage to AIMessage.usage_metadata via
  TokenUsageMiddleware, so accumulateUsage() naturally includes
  subagent tokens without frontend state management
- Cache subagent usage by tool_call_id in task_tool, write back
  to the dispatching AIMessage on next model response
- Emit subagent token usage on all terminal task events
  (task_completed, task_failed, task_cancelled, task_timed_out)
- Report subagent usage to parent RunJournal for API totals
- Search backward from ToolMessage to find dispatching AIMessage
  for correct multi-tool-call attribution

Frontend:
- Remove subagentUsage state, custom event handling, and prop
  threading — subagent tokens are now embedded in message metadata
- Simplify selectHeaderTokenUsage (no subagentUsage parameter)
- Per-turn inline badges show turn-specific usage via message
  accumulation
- Remove isLoading guard from MessageTokenUsageList for dynamic
  updates during streaming

* fix: prevent header token double counting from baseline reset race

onFinish, onError, and thread-switch useEffect all reset
pendingUsageBaselineMessageIdsRef to an empty Set. If
thread.isLoading is still true on the next render, all messages
pass the getMessagesAfterBaseline filter and their tokens are
added to backendUsage (which already includes them), causing
the header to display up to 2× the actual token count.

Capture current message IDs instead of using an empty Set so
that getMessagesAfterBaseline correctly returns no pending
messages even if thread.isLoading lags behind the stream end.

* fix: write back subagent tokens for all concurrent task tool calls

TokenUsageMiddleware only processed messages[-2], so when a
single model response dispatched multiple task tool calls only
the last ToolMessage had its cached subagent usage written back
to the dispatch AIMessage.usage_metadata. Earlier tasks' usage
stayed in _subagent_usage_cache indefinitely (leak) and never
appeared in the per-turn inline token display.

Walk backward through all consecutive ToolMessages before the
new AIMessage, and accumulate updates targeting the same
dispatch message into one state update so overlapping writes
don't clobber each other.

* fix: clean up subagent usage cache entry on task cancellation

When a task_tool invocation is cancelled via CancelledError, any
cached subagent usage entry leaked because the TokenUsageMiddleware
writeback path never fires after cancellation. Pop the cache entry
before re-raising to prevent unbounded growth of the module-level
_subagent_usage_cache dict.

* fix: address token usage review feedback

* fix: handle missing config for subagent usage cache

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/agents/middlewares/token_usage_middleware.py`
  L221: """Return True if the AIMessage contains a tool_call with the given id."""
  L275: # Annotate subagent token usage onto the AIMessage that dispatched it.
  L276: # When a task tool completes, its usage is cached by tool_call_id.  Detect
  L277: # the ToolMessage → search backward for the corresponding AIMessage → merge.
  L278: # Walk backward through consecutive ToolMessages before the new AIMessage
  L279: # so that multiple concurrent task tool calls all get their subagent tokens
  L280: # written back to the same dispatch message (merging into one update).
  L293: # Search backward from the ToolMessage to find the AIMessage
  L294: # that dispatched it.  A single model response can dispatch
  L295: # multiple task tool calls, so we can't assume a fixed offset.
  L300: # Accumulate into an existing update for the same
  L301: # AIMessage (multiple task calls in one response),
  L302: # or merge fresh from the original message.
- `backend/packages/harness/deerflow/tools/builtins/task_tool.py`
  L29: # Cache subagent token usage by tool_call_id so TokenUsageMiddleware can
  L30: # write it back to the triggering AIMessage's usage_metadata.
  L118: """Summarize token usage records into a compact dict for SSE events."""

## 722c690f 2026-05-15 LawranceLiao
fix(memory): isolate queued memory updates by agent (#2941)

* fix(memory): isolate queued memory updates by agent

* fix(memory): include user in queue identity

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* Fix the lint error

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/agents/memory/queue.py`
  L49: """Return the debounce identity for a memory update target."""
- `backend/packages/harness/deerflow/agents/memory/summarization_hook.py`

## 45060a9f 2026-05-15 Nan Gao
fix(runtime): avoid postgres aggregate row lock (#2962)

- `backend/packages/harness/deerflow/runtime/events/store/db.py`
  L91: """Return the current max seq while serializing writers per thread.
  L97: """

## 181d8365 2026-05-15 LawranceLiao
fix(middleware): normalize tool result adjacency before model calls (#2939)

* normalizing tool-call transcripts before invocation

* test(middleware): cover tool result regrouping edge cases

- `backend/packages/harness/deerflow/agents/middlewares/dangling_tool_call_middleware.py`
  L107: """Return messages with tool results grouped after their tool-call AIMessage.

## 0c37509b 2026-05-15 Nan Gao
fix(middleware): Prevent todo completion reminder IMMessage leak (#2907)

* fix(middleware): Prevent todo completion reminder IMMessage leak (#2892)

* make format

* fix(middleware): Clear stale todo reminder counts (#2892)

* add size guard for _completion_reminder_counts and add a integration test

- `backend/packages/harness/deerflow/agents/middlewares/todo_middleware.py`
  L63: """Format a completion reminder for incomplete todo items."""
  L80: """Return True when an AIMessage is not a clean final answer.
  L86: """
  L93: # Backward/provider compatibility: some integrations preserve raw or legacy
  L94: # tool-call intent in additional_kwargs even when structured tool_calls is
  L95: # empty. If this helper changes, update the matching sentinel test
  L96: # `TestToolCallIntentOrError.test_langchain_ai_message_tool_fields_are_explicitly_handled`;
  L97: # if that test fails after a LangChain upgrade, review this helper so new
  L98: # tool-call/error fields are not silently treated as clean final answers.
  L166: # Hard cap for per-run reminder bookkeeping in long-lived middleware instances.
  L284: # 2. Only intervene when the agent wants to exit cleanly. Tool-call
  L285: # intent or tool-call parse errors should be handled by the tool path
  L286: # instead of being masked by todo reminders.
  L301: # 5. Queue a reminder for the next model request and jump back. We must
  L302: # not persist this control prompt as a normal HumanMessage, otherwise it
  L303: # can leak into user-visible message streams and saved transcripts.

## 380255f7 2026-05-17 Xinmin Zeng
fix(sandbox): uphold /mnt/user-data contract at Sandbox API boundary (#2873) (#2881)

* fix(sandbox): uphold /mnt/user-data contract at Sandbox API boundary (#2873)

LocalSandboxProvider used a process-wide singleton with no /mnt/user-data
mapping, forcing every caller to translate virtual paths via tools.py
before invoking the public Sandbox API. AIO already exposes /mnt/user-data
natively (per-thread bind mounts), so the same code path behaved
differently across implementations — and direct callers like
uploads.py:282 / feishu.py:389 only worked thanks to the
`uses_thread_data_mounts` workaround flag.

Switch the provider to a dual-track cache: keep the `"local"` singleton
for legacy acquire(None) callers (backward-compat for existing tests and
scripts), and create a per-thread LocalSandbox with id `"local:{tid}"`
for acquire(thread_id). Each per-thread instance carries PathMapping
entries for /mnt/user-data, its three subdirs, and /mnt/acp-workspace,
mirroring how AioSandboxProvider mounts those paths into its container.

is_local_sandbox() now recognises both id formats. `_agent_written_paths`
becomes per-thread (it was a process-wide set that leaked across
threads — a latent isolation bug also fixed by this change).

Verified via TDD: a new contract test suite hits the public Sandbox API
directly (write/read/list/exec/glob/grep/update + per-thread isolation +
lifecycle). 3212 backend tests still pass, ruff is clean.

* fix(sandbox): address Copilot review on #2881

Three follow-ups from Copilot's review of the LocalSandboxProvider refactor:

1. Synchronisation: ``acquire`` / ``get`` / ``reset`` mutated the cache without
   any lock, so concurrent acquire of the same ``thread_id`` could create two
   ``LocalSandbox`` instances and lose one's ``_agent_written_paths`` state.
   Add a provider-wide ``threading.Lock`` (matching ``AioSandboxProvider``) and
   build per-thread mappings outside the lock to avoid holding it during the
   ``ensure_thread_dirs`` filesystem touch.

2. Memory bound: ``_thread_sandboxes`` grew monotonically. Replace the plain
   dict with an ``OrderedDict`` LRU capped at
   ``DEFAULT_MAX_CACHED_THREAD_SANDBOXES`` (256, configurable per provider
   instance). ``get`` promotes touched threads to the MRU end so an active
   thread isn't evicted under load. Eviction is graceful: the next ``acquire``
   rebuilds a fresh sandbox; only ``_agent_written_paths`` (reverse-resolve
   hint) is lost.

3. Docs: update ``CLAUDE.md`` to reflect the new per-thread architecture, the
   LRU cap, and that ``is_local_sandbox`` recognises both id formats.

New regression tests:
- Concurrent ``acquire("alpha")`` from 8 threads yields a single instance
  (slow-init injection forces the race window wide open).
- Concurrent ``acquire`` of distinct thread_ids yields distinct instances.
- The cache evicts the least-recently-used thread once the cap is exceeded.
- ``get`` promotes recency so a polled thread survives a later acquire-storm.

- `backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`
  L12: # Module-level alias kept for backward compatibility with older callers/tests
  L13: # that reach into ``local_sandbox_provider._singleton`` directly. New code reads
  L14: # the provider instance attributes (``_generic_sandbox`` / ``_thread_sandboxes``)
  L15: # instead.
  L18: # Virtual prefixes that must be reserved by the per-thread mappings created in
  L19: # ``acquire`` — custom mounts from ``config.yaml`` may not overlap with these.
  L23: # Default upper bound on per-thread LocalSandbox instances retained in memory.
  L24: # Each cached instance is cheap (a small Python object with a list of
  L25: # PathMapping and a set of agent-written paths used for reverse resolve), but
  L26: # in a long-running gateway the number of distinct thread_ids is unbounded.
  L27: # When the cap is exceeded the least-recently-used entry is dropped; the next
  L28: # ``acquire(thread_id)`` for that thread simply rebuilds the sandbox at the
  L29: # cost of losing its accumulated ``_agent_written_paths`` (read_file falls
  L30: # back to no reverse resolution, which is the same behaviour as a fresh run).
  L35: """Local-filesystem sandbox provider with per-thread path scoping.
  L63: """
  L68: """Initialize the local sandbox provider with static path mappings.
  L74: """
  L172: """Build per-thread path mappings for /mnt/user-data and /mnt/acp-workspace.
  L177: """
  ... (truncated)
- `backend/packages/harness/deerflow/sandbox/tools.py`

## a814ab50 2026-05-17 Willem Jiang
fix(skills): make security scanner JSON parsing robust for LLM output variations (#2987)

The moderation model's response was silently falling through to a
  conservative block when LLMs wrapped structured output in markdown
  code fences, added prose around the JSON, returned case-variant
  decisions (e.g. "Allow"), or included nested braces in the reason
  field. The greedy `\{.*\}` regex also over-matched on nested braces.

  - Rewrite _extract_json_object() with markdown fence stripping and
    brace-balanced string-aware extraction
  - Normalize decision field to lowercase for case-insensitive matching
  - Distinguish "model unavailable" from "unparseable output" in fallback
  - Strengthen system prompt to explicitly forbid code fences and prose
  - Add 15 tests covering all reported scenarios

  Fixes #2985

- `backend/packages/harness/deerflow/skills/security_scanner.py`
  L27: # Strip markdown code fences (```json ... ``` or ``` ... ```)
  L37: # Brace-balanced extraction with string-awareness

## e74e126e 2026-05-17 魔力鸟
fix(sandbox): scope provisioner PVC data by user (#2973)

* fix(sandbox): scope provisioner PVC data by user

* Address provisioner PVC review feedback

- `backend/packages/harness/deerflow/community/aio_sandbox/remote_backend.py`

## 39f901d3 2026-05-17 Willem Jiang
fix(runs): restore historical runs from persistent store after gateway restart (#2989)

* fix(runs): restore historical runs from persistent store after gateway restart

  RunManager.list_by_thread() and get() only queried the in-memory _runs
  dict, returning empty results after a restart even when PostgreSQL had
  the records. Add store fallback to both read paths and a new async
  aget() for the API endpoint, keeping sync get() for internal callers
  that need live task/abort_event state.

    Fixes #2984

* Apply suggestions from code review

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* fix(runs): scope run store fallback reads by user id

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/e73daada-1215-4bc1-ab7d-7117826c5013

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* test(runs): clarify ordering expectation and mock store filters

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/e73daada-1215-4bc1-ab7d-7117826c5013

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* test(runs): make user filter fallback assertions explicit

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/e73daada-1215-4bc1-ab7d-7117826c5013

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* test(runs): verify user-isolated fallback behavior with memory store

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/e73daada-1215-4bc1-ab7d-7117826c5013

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* update the code with feedback from issue-2984

---------

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>
Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/runtime/runs/manager.py`
  L114: """Return an in-memory run record by ID, or ``None``."""
  L118: """Return a run record by ID, checking the persistent store as fallback."""
  L132: """Convert a store dict back to a RunRecord for read-only use."""
  L149: """Return all runs for a given thread, oldest first."""
- `backend/packages/harness/deerflow/runtime/runs/store/base.py`
- `backend/packages/harness/deerflow/runtime/runs/store/memory.py`

## 3acca126 2026-05-18 KiteEater
fix(subagents): make subagent timeout terminal state atomic (#2583)

* Guard subagent terminal state transitions

* fix: publish subagent terminal status last

* Fix subagent timeout test to avoid blocking event loop

* Fix subagent timeout test tracking

* Refine subagent terminal state handling

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/subagents/executor.py`
  L103: """Set a terminal status exactly once.
  L108: """

## c810e9f8 2026-05-18 He Wang
fix(harness)!: hydrate runs from RunStore and persist interrupted status (#2932)

* fix(harness): hydrate run history from RunStore and persist cancellation status

fix:
- Make RunManager.get() async and hydrate from RunStore when in-memory record is missing
- Merge store rows into list_by_thread() with in-memory precedence for active runs
- Persist interrupted status to RunStore in cancel() and create_or_reject(interrupt|rollback)
- Extract _persist_status() to reuse the best-effort store update pattern
- Await run_mgr.get() in all gateway endpoints
- Return 409 with distinct message for store-only runs not active on current worker

Closes #2812, Closes #2813

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

* fix(harness): consistent sort and guarded hydration in RunManager

fix:
- list_by_thread() now sorts by created_at desc (newest first) even when
  no RunStore is configured, matching the store-backed code path
- guard _record_from_store() call sites in get() and list_by_thread()
  with best-effort error handling so a single malformed store row cannot
  turn read paths into 500s

test:
- update test_list_by_thread assertion to expect newest-first order
- seed MemoryRunStore via public put() API instead of writing to _runs

* fix(harness): guard store-only runs from streaming and fix get() TOCTOU

Add RunRecord.store_only flag set by _record_from_store so callers can
distinguish hydrated history from live in-memory runs.  join_run and
stream_existing_run (action=None) now return 409 instead of hanging
forever on an empty MemoryStreamBridge channel.

Re-check _runs under lock after the store await in RunManager.get() so a
concurrent create() that lands between the two checks returns the
authoritative in-memory record rather than a stale store-hydrated copy.

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>

* fix(harness): reorder bridge fetch in join_run and make list_by_thread limit explicit

Move get_stream_bridge() after the store_only guard in join_run so a
missing bridge cannot produce 503 for historical runs before the 409
guard fires.

Add limit parameter to RunManager.list_by_thread (default 100, matching
the store's page size) and pass it explicitly to the store call.
Update docstring to document the limit instead of claiming all runs are
returned.

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>

* fix(harness): cap list_by_thread result to limit after merge

Apply [:limit] to all return paths in list_by_thread so the method
consistently returns at most limit records regardless of how many
in-memory runs exist, making the limit parameter a true upper bound
on the response size rather than just a store-query hint.

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>

* fix `list_by_thread` docstring

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* fix(runtime): add update_model_name to RunStore to prevent SQL integrity errors

RunManager.update_model_name() was calling _persist_to_store() which uses
RunStore.put(), but RunRepository.put() is insert-only. This caused integrity
errors when updating model_name for existing runs in SQL-backed stores.

fix:
- Add abstract update_model_name method to RunStore base class
- Implement update_model_name in MemoryRunStore
- Implement update_model_name in RunRepository with proper normalization
- Add _persist_model_name helper in RunManager
- Update RunManager.update_model_name to use the new method

test:
- Add tests for update_model_name functionality
- Add integration tests for RunManager with SQL-backed store

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

* fix(runtime): handle NULL status/on_disconnect in _record_from_store

`dict.get(key, default)` only uses the default when the key is absent,
so a SQL row with an explicit NULL status would pass `None` to
`RunStatus(None)` and raise, breaking hydration for otherwise valid rows.
Switch to `row.get(...) or fallback` so both missing and NULL values
get a safe default. Add tests for get() and list_by_thread() with a
NULL status row to prevent regression.

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>

* fix(runs): address PR review feedback on store consistency changes

- Fix list_by_thread limit semantics: pass store_limit = max(0, limit - len(memory_records)) to store so newer store records are not crowded out by in-memory records
- Remove dead code: cancelled guard after raise is always True, simplify to if wait and record.task
- Document _record_from_store NULL fallback policy (status→pending, on_disconnect→cancel) in docstring

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.7 <noreply@anthropic.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/persistence/run/sql.py`
- `backend/packages/harness/deerflow/runtime/runs/manager.py`
  L76: """Best-effort persist a status transition to the backing store."""
  L86: """Build a read-only runtime record from a serialized store row.
  L90: """
  L147: """Return a run record by ID, or ``None``.
  L152: """
  L164: # Re-check after store await: a concurrent create() may have inserted the
  L165: # in-memory record while the store call was in flight.
  L179: """Return a run record by ID, checking the persistent store as fallback.
  L182: """
  L186: """Return runs for a given thread, newest first, at most ``limit`` records.
  L196: """
  L198: # Dict insertion order gives deterministic results when timestamps tie.
  L233: """Best-effort persist model_name update to the backing store."""
- `backend/packages/harness/deerflow/runtime/runs/store/base.py`
  L75: """Update the model_name field for an existing run."""
- `backend/packages/harness/deerflow/runtime/runs/store/memory.py`

## 3599b570 2026-05-19 AochenShen99
fix(harness): wrap all async-only tools for sync clients (#2935)

- `backend/packages/harness/deerflow/tools/sync.py`
  L23: """Return the coroutine parameter that expects LangChain RunnableConfig."""
  L39: """Build a synchronous wrapper for an asynchronous tool coroutine.
  L61: """
- `backend/packages/harness/deerflow/tools/tools.py`

## e37912e2 2026-05-20 Xun
feat(sandbox) Adds download file interface in Sandbox (#3038)

* Add download interface in Sandbox

* fix

* fix

* del invalidate test

* fix

* safe download

* improve

- `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`
  L110: """Download file bytes from the sandbox.
  L116: """
  L117: # Reject path traversal before sending to the container API.
  L118: # LocalSandbox gets this implicitly via _resolve_path;
  L119: # here the path is forwarded verbatim so we must check explicitly.
- `backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`
  L400: # TOCTOU note: the file could grow between getsize() and read(); accepted
  L401: # tradeoff since this is a controlled sandbox environment.
  L405: # Re-raise with the original path for clearer error messages, hiding internal resolved paths
- `backend/packages/harness/deerflow/sandbox/sandbox.py`
  L44: """Download the binary content of a file.
  L58: """

## 9b19cca9 2026-05-20 john lee
fix(runtime): make RunManager.cancel() idempotent for already-interrupted runs (#3055) (#3058)

A second cancel() call on an interrupted run returned False, causing the
cancel and stream_existing_run router endpoints to raise 409 on double-stop.

Fix: return True inside the lock when record.status == RunStatus.interrupted.
This covers both the POST /cancel and POST /join endpoints without any
re-fetch or extra get() call — the idempotency lives at the source.

Also fixes stream_existing_run (the LangGraph SDK stop-button path), which
had the identical cancel() → 409 pattern and was not covered by the
original PR.  Both endpoints share the fix automatically.

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>

- `backend/packages/harness/deerflow/runtime/runs/manager.py`

## b6b3650e 2026-05-20 Airene Fang
fix(trace):memory 中文 in trace info is unicode escape sequence. (#3104)

* fix(trace):memory 中文 in trace is unicode

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/agents/memory/updater.py`

## 9afeaf66 2026-05-20 Yuyi Ao
Fix env resolution in MCP config lists (#2556)

* Fix env resolution in MCP config lists

* fix:unset env variable and consistent function

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/config/extensions_config.py`
  L168: # Unresolved placeholder — store empty string so downstream
  L169: # consumers (e.g. MCP servers) don't receive the literal "$VAR"
  L170: # token as an actual environment value.

## e19bec14 2026-05-21 InitBoy
fix(task-tool): cancel and schedule deferred cleanup on polling safety timeout (#3097)

When the poll loop's safety-net timeout fires (poll_count > max_poll_count),
the background subagent task was abandoned without cancellation or cleanup,
leaving a stale entry in _background_tasks indefinitely.

The original code had a comment promising "the cleanup will happen when the
executor completes", but run_task() in executor.py never calls
cleanup_background_task after reaching a terminal state -- the promise was
never implemented.

This change mirrors the asyncio.CancelledError path: signal cooperative
cancellation via request_cancel_background_task and schedule
_deferred_cleanup_subagent_task to remove the entry once the background
thread reaches a terminal state.

Direct cleanup at poll-timeout time would introduce a race: run_task() could
remove the entry while the poll loop is still mid-iteration, causing a
spurious "Task disappeared" error. The deferred approach avoids this by
waiting for terminal state before removal.

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>

- `backend/packages/harness/deerflow/tools/builtins/task_tool.py`
  L393: # The task may still be running in the background. Signal cooperative
  L394: # cancellation and schedule deferred cleanup to remove the entry from
  L395: # _background_tasks once the background thread reaches a terminal state.

## dcc6f1e6 2026-05-21 Nan Gao
feat(loop-detection): defer warning injection (#2752)

* fix(loop-detection): defer warn injection to wrap_model_call

The warn branch in LoopDetectionMiddleware injected a HumanMessage
into state from after_model. The tools node had not yet produced
ToolMessage responses to the previous AIMessage(tool_calls=...), so
the new HumanMessage landed *between* the assistant's tool_calls and
their responses. OpenAI/Moonshot reject the next request with
"tool_call_ids did not have response messages" because their
validators require tool_calls to be followed immediately by tool
messages.

Detection now runs in after_model as before, but only enqueues the
warning into a per-thread list. Injection happens in wrap_model_call,
where every prior ToolMessage is already present in request.messages.
The warning is appended at the end as HumanMessage(name="loop_warning")
— pairing intact, AIMessage semantics untouched, no SystemMessage
issues for Anthropic.

Closes #2029, addresses #2255 #2293 #2304 #2511.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

* fix(channels): remove loop warning display filter

* feat(loop-detection): scope pending warnings by run

* docs(loop-detection): update docs

* test(loop-detection): assert deferred warnings are queued

* fix(loop-detection): cap transient warning state

* docs: update docs

* add async awrap_model_call test coverage

* docs(loop-detection): document transient warnings

---------

Co-authored-by: Claude Opus 4.7 <noreply@anthropic.com>

- `backend/packages/harness/deerflow/agents/middlewares/loop_detection_middleware.py`
  L228: # Per-thread/run queue of warnings to inject at the next model call.
  L229: # Populated by ``after_model`` (detection) and drained by
  L230: # ``wrap_model_call`` (injection); see module docstring.
  L256: """Extract run_id from runtime context for per-run warning scoping."""
  L263: """Return the pending-warning key for the current thread/run."""
  L282: """Drop all pending-warning bookkeeping for one thread/run key.
  L285: """
  L290: """Mark a pending-warning key as recently used.
  L293: """
  L298: """Cap pending-warning state across abnormal or concurrent runs.
  L301: """
  L311: """Queue one transient warning for the current thread/run with caps."""
  L481: # Strip tool_calls from the last AIMessage to force text output.
  L482: # Once tool_calls are stripped, the AIMessage no longer requires
  L483: # matching ToolMessage responses, so mutating it in place here
  L484: # is safe for OpenAI/Moonshot pairing validators.
  L492: # Defer injection to the next model call. We must NOT alter the
  L493: # AIMessage(tool_calls=...) here (would put framework words in
  L494: # the model's mouth, polluting downstream consumers like
  L495: # MemoryMiddleware), nor insert a separate non-tool message
  ... (truncated)

## 8b697245 2026-05-21 AochenShen99
fix(sandbox): avoid blocking sandbox readiness polling (#2822)

* fix(sandbox): offload async sandbox acquisition

Run blocking sandbox provider acquisition through the async provider hook so eager sandbox setup does not stall the event loop.

* fix(sandbox): add async readiness polling

Introduce an async sandbox readiness poller using httpx and asyncio.sleep while preserving the existing synchronous API.

* test(sandbox): cover async readiness polling

Lock in non-blocking readiness behavior so the async helper does not regress to requests.get or time.sleep.

* fix(sandbox): allow anonymous backend creation

* fix(sandbox): use async readiness in provider acquisition

* fix(sandbox): use async acquisition for lazy tools

* test(sandbox): cover anonymous remote creation

* fix(sandbox): clamp async readiness timeout budget

* fix(sandbox): offload async lock file handling

* fix(sandbox): delegate async middleware fallthrough

* docs(sandbox): document async acquisition path

* fix(sandbox): offload async sandbox release

* docs(sandbox): mention async release hook

* fix(sandbox): address async lock review

Reduce duplicate sync/async sandbox acquisition state handling and move async thread-lock waits onto a dedicated executor with cancellation-safe cleanup.

* chore: retrigger ci

Retrigger GitHub Actions after upstream main fixed the stale PR merge lint failure.

* test(sandbox): sync backend unit fixtures

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`
  L79: """Acquire a threading.Lock without polling or using the default executor."""
  L94: """Release a lock acquired after its awaiting coroutine was cancelled."""
  L459: """Return deterministic IDs for thread sandboxes and random IDs otherwise."""
  L463: """Reuse an active in-process sandbox for a thread if one is still tracked."""
  L482: """Promote a warm-pool sandbox back to active tracking if available."""
  L502: """Re-check in-memory caches after acquiring the cross-process file lock."""
  L506: """Track a sandbox discovered through the backend."""
  L518: """Track a newly-created sandbox in the active maps."""
  L531: """Return configured replicas and currently tracked sandbox count."""
  L538: """Log the result of enforcing the warm-pool replica budget."""
  L543: # All slots are occupied by active sandboxes — proceed anyway and log.
  L544: # The replicas limit is a soft cap; we never forcibly stop a container
  L545: # that is actively serving a thread.
  L573: """Acquire a sandbox environment without blocking the event loop.
  L578: """
  L619: """Async counterpart to ``_acquire_internal``."""
  L624: # Deterministic ID for thread-specific, random for anonymous
  L627: # ── Layer 1.5: Warm pool (container still running, no cold-start) ──
  L632: # ── Layer 2: Backend discovery + create (protected by cross-process lock) ──
  L671: """Async counterpart to ``_discover_or_create_with_lock``."""
  ... (truncated)
- `backend/packages/harness/deerflow/community/aio_sandbox/backend.py`
  L41: """Async variant of sandbox readiness polling.
  L46: """
- `backend/packages/harness/deerflow/community/aio_sandbox/local_backend.py`
- `backend/packages/harness/deerflow/community/aio_sandbox/remote_backend.py`
- `backend/packages/harness/deerflow/sandbox/middleware.py`
  L79: # Skip acquisition if lazy_init is enabled
  L83: # Eager initialization (original behavior), but use the async provider
  L84: # hook so blocking sandbox startup/polling runs outside the event loop.
  L127: # No sandbox to release
- `backend/packages/harness/deerflow/sandbox/sandbox_provider.py`
  L24: """Acquire a sandbox without blocking the event loop.
  L30: """
- `backend/packages/harness/deerflow/sandbox/tools.py`
  L1117: """Async counterpart to ``ensure_sandbox_initialized`` for tool runtimes.
  L1122: """
  L1164: """Initialize lazily via async provider, then run sync tool body off-thread."""

## 923f516d 2026-05-21 Airene Fang
feat(trace):LangGraph -> lead_agent and set custom agent_name to run_name (#3101)

* feat(trace):LangGraph -> lead_agent and set user custom agent name to run_name

* feat(trace):follow github copilot suggest

* feat(trace):Refactor run_name resolution and improve test coverage

- `backend/packages/harness/deerflow/runtime/runs/naming.py`
  L1: """Run naming helpers for LangChain/LangSmith tracing."""
- `backend/packages/harness/deerflow/runtime/runs/worker.py`
  L228: # Resolve after runtime context installation so context/configurable reflect
  L229: # the agent name that this run will actually execute.

## 31513c2c 2026-05-21 Xinmin Zeng
fix(persistence): emit tz-aware timestamps from SQLite-backed stores (#3130)

SQLAlchemy's DateTime(timezone=True) is a no-op on SQLite (the backend
has no native tz type), so values round-tripped through the DB come
back as naive datetimes. The four SQL _row_to_dict helpers were calling
.isoformat() directly on those naive values, shipping timezone-less
strings like "2026-05-20T06:10:22.970977" out of the API. The browser's
new Date(...) then parses them as local time, shifting recent threads
in /threads/search by the local UTC offset (about 8h in Asia/Shanghai).

Route the four call sites through coerce_iso() instead — it already
normalizes naive values as UTC and emits "+00:00" so the wire format
always carries tz. No data migration is needed; existing SQLite rows
read back via the corrected serializer.

PostgreSQL deployments are unaffected because timestamptz preserves
tzinfo end-to-end.

Closes #3120

- `backend/packages/harness/deerflow/persistence/feedback/sql.py`
  L28: # SQLite drops tzinfo on read; normalize via ``coerce_iso`` so output is always tz-aware.
- `backend/packages/harness/deerflow/persistence/run/sql.py`
  L72: # Convert datetime to ISO string for consistency with MemoryRunStore.
  L73: # SQLite drops tzinfo on read despite ``DateTime(timezone=True)`` —
  L74: # ``coerce_iso`` normalizes naive datetimes as UTC.
- `backend/packages/harness/deerflow/persistence/thread_meta/sql.py`
  L32: # SQLite drops tzinfo despite ``DateTime(timezone=True)``;
  L33: # ``coerce_iso`` normalizes naive values as UTC so the wire format always carries tz.
- `backend/packages/harness/deerflow/runtime/events/store/db.py`
  L36: # SQLite drops tzinfo on read despite ``DateTime(timezone=True)``;
  L37: # ``coerce_iso`` normalizes naive datetimes as UTC.

## df951542 2026-05-21 Xinmin Zeng
fix(tracing): propagate session_id and user_id into Langfuse traces (#2944)

* fix(tracing): propagate session_id and user_id into Langfuse traces

Adds Langfuse v4 reserved trace attributes (langfuse_session_id,
langfuse_user_id, langfuse_trace_name, langfuse_tags) to
RunnableConfig.metadata inside the run worker, so the langchain
CallbackHandler can lift them onto the root trace.

- New deerflow.tracing.metadata.build_langfuse_trace_metadata() returns
  the reserved keys when Langfuse is in the enabled providers, else {}.
- worker.run_agent merges them with setdefault so caller-supplied keys
  win, allowing per-request overrides from upstream metadata.
- session_id mirrors the LangGraph thread_id; user_id reads
  get_effective_user_id() (falls back to "default" in no-auth mode).
- trace_name defaults to "lead-agent"; tags carry env and model name
  when DEER_FLOW_ENV (or ENVIRONMENT) and a model name are present.

Closes #2930

* fix(tracing): attach Langfuse callback at graph root so metadata propagates

The first commit injected ``langfuse_session_id`` / ``langfuse_user_id`` /
``langfuse_trace_name`` / ``langfuse_tags`` into ``RunnableConfig.metadata``,
but on ``main`` the Langfuse callback is attached at *model* level
(``models/factory.py``). LangChain still threads ``parent_run_id`` through
the contextvar, so the handler sees the model as a nested observation and
``__on_llm_action`` strips the ``langfuse_*`` keys
(``keep_langfuse_trace_attributes=False``). The trace's top-level
``sessionId`` / ``userId`` therefore stayed empty in deer-flow's LangGraph
runtime — confirmed live against a real Langfuse instance.

This commit moves the callback to the **graph invocation root** so the
handler fires ``on_chain_start(parent_run_id=None)`` and runs the
``propagate_attributes`` path that actually lifts ``session_id`` /
``user_id`` onto the trace:

- ``models/factory.py``: add ``attach_tracing`` keyword (default ``True``)
  so standalone callers (``MemoryUpdater``, etc.) keep their direct
  model-level tracing.
- ``agents/lead_agent/agent.py``: call ``build_tracing_callbacks()`` once
  inside ``_make_lead_agent`` and append the result to
  ``config["callbacks"]``; the four in-graph ``create_chat_model`` sites
  (bootstrap, default agent, sync + async summarization) pass
  ``attach_tracing=False`` to avoid duplicate spans.
- ``agents/middlewares/title_middleware.py``: same ``attach_tracing=False``
  for the title-generation model, since it inherits the graph's
  RunnableConfig via ``_get_runnable_config``.

Test updates:

- ``tests/test_lead_agent_model_resolution.py`` and
  ``tests/test_title_middleware_core_logic.py``: extend the fake
  ``create_chat_model`` signatures / mock assertions to accept the new
  ``attach_tracing`` kwarg.
- ``tests/test_worker_langfuse_metadata.py``: switch the no-user fallback
  test from direct ContextVar mutation to ``monkeypatch.setattr`` on
  ``get_effective_user_id`` to avoid pollution across the langfuse OTel
  global tracer provider.
- ``tests/conftest.py``: add an autouse fixture that resets
  ``deerflow.config.title_config._title_config`` to its pristine default
  after every test. Any test that loads the real ``config.yaml`` (via
  ``get_app_config()``) calls ``load_title_config_from_dict`` and mutates
  the module-level singleton, which previously poisoned the
  title-middleware suite when run after, e.g., the new
  ``test_worker_langfuse_metadata.py`` cases. The fixture is independent
  of this PR's main change but unblocks the cross-file test run.

Live verification (same Langfuse instance as before):

- Drove ``worker.run_agent`` against the real ``make_lead_agent`` +
  ``gpt-4o-mini`` for three distinct ``user_context`` identities
  (``fancy-engineer``, ``alice-pm``, ``bob-designer``).
- Each run produced one ``lead-agent`` trace whose top-level
  ``sessionId`` / ``userId`` / ``tags`` carry the expected values, e.g.
  ``session=e2e-2930-8f347c-alice-pm user=alice-pm name='lead-agent'
  tags=['model:gpt-4o-mini']``.

Refs #2930.

* fix(tracing): extend root-callback + metadata injection to the embedded client

Addresses Copilot review on PR #2944.

Commit 2 disabled model-level tracing for ``TitleMiddleware`` and
``_create_summarization_middleware`` because ``_make_lead_agent`` now
attaches the tracing callbacks at the graph invocation root. But the
embedded ``DeerFlowClient`` does not call ``_make_lead_agent`` — it
calls ``_build_middlewares`` directly and never appends the tracing
handlers to its ``RunnableConfig``. So under the embedded path,
title-generation and summarization LLM calls were left untraced —
a regression introduced by this PR.

This commit mirrors the gateway worker's injection in
``DeerFlowClient.stream``:

- Append ``build_tracing_callbacks()`` to ``config["callbacks"]`` so
  the Langfuse handler sees ``on_chain_start(parent_run_id=None)`` at
  the graph root and runs the ``propagate_attributes`` path.
- Merge ``build_langfuse_trace_metadata(...)`` into
  ``config["metadata"]`` with ``setdefault`` so caller-supplied keys
  still win.
- ``_ensure_agent`` now creates its main model with
  ``attach_tracing=False`` to avoid duplicate spans now that the
  callback lives at the graph root.

Docs:
- ``backend/CLAUDE.md`` Tracing section rewritten to describe the
  graph-root attachment model (replacing the inaccurate
  "at model-creation time" wording).
- ``README.md`` Langfuse section now lists both injection points
  (worker + client) instead of only the worker path.

Tests:
- ``tests/test_client_langfuse_metadata.py`` (new, 3 cases):
  callbacks + metadata are injected when Langfuse is enabled,
  caller-supplied metadata overrides win via ``setdefault``, and the
  injection is inert when Langfuse is disabled.

Live verification on the real Langfuse instance:

  === user=fancy-client ===
    id=cbd22847..  session=client-2930-6b9491-fancy-client  user=fancy-client  name='lead-agent'
  === user=alice-client ===
    id=b4f6f576..  session=client-2930-6b9491-alice-client  user=alice-client  name='lead-agent'

Refs #2930.

* refactor(tracing): address maintainer review on PR #2944

Addresses @WillemJiang's 5 comments.

1. Duplicated metadata-injection code between worker.py and client.py
   New ``deerflow.tracing.inject_langfuse_metadata(config, ...)`` helper
   takes the 10-line build + merge + setdefault logic that was duplicated
   in ``runtime/runs/worker.py`` and ``client.py``. Both callers now share
   a single source of truth, so the two paths cannot drift.

2. Direct private-attribute mutation in conftest.py and tests
   Added public ``reset_tracing_config()`` / ``reset_title_config()``
   functions. ``tests/conftest.py`` and every test that previously did
   ``tracing_module._tracing_config = None`` or
   ``title_module._title_config = TitleConfig()`` now goes through the
   public API. A future internal rename will surface as an ImportError
   instead of a silent no-op.

3. client.py reading os.environ directly
   ``DeerFlowClient.__init__`` grows an optional ``environment`` parameter
   so programmatic callers can pass the deployment label explicitly.
   ``stream()`` consults ``self._environment`` first and only falls back
   to ``DEER_FLOW_ENV`` / ``ENVIRONMENT`` env vars when nothing was
   passed in. Backwards compatible — env-var behaviour preserved for
   callers that opt to keep using it.

4. build_tracing_callbacks() cached on hot path
   Not implemented. Inspected the langfuse v4 ``langchain.CallbackHandler``
   constructor: it only resolves the module-level singleton client via
   ``get_client()`` and initialises a few dicts (no I/O, no env parsing
   at construction time). The build is essentially free. Caching would
   trade a non-measurable speedup for two real risks: handler instances
   carry per-run state internally (``_run_states``, ``_root_run_states``,
   ``last_trace_id``), and tracing config can be reloaded by env-var
   changes between runs. Will revisit if profiling ever shows it as
   a hot spot.

5. attach_tracing=False easy to forget at new in-graph call sites
   - Module docstring at the top of ``lead_agent/agent.py`` documents
     the invariant ("every in-graph ``create_chat_model`` MUST pass
     ``attach_tracing=False``") and enumerates the current sites.
   - New regression test
     ``test_make_lead_agent_attaches_tracing_callbacks_at_graph_root`` in
     ``tests/test_lead_agent_model_resolution.py`` locks both halves of
     the invariant: ``config["callbacks"]`` carries the tracing handler
     after ``_make_lead_agent``, AND every ``create_chat_model`` call
     captured by the test passes ``attach_tracing=False``. A future
     in-graph site that forgets the flag will fail this test.

Lint clean. Full touched-suite bundle: 246 passed.

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
  L1: """Lead agent factory.
  L19: """
  L97: # attach_tracing=False because the graph-level RunnableConfig (set in
  L98: # ``_make_lead_agent``) already carries tracing callbacks; binding them
  L99: # again at the model level would emit duplicate spans and break
  L100: # ``session_id`` / ``user_id`` propagation.
  L436: # Inject tracing callbacks at the graph invocation root so a single LangGraph
  L437: # run produces one trace with all node / LLM / tool calls as child spans,
  L438: # AND so the Langfuse handler sees ``on_chain_start(parent_run_id=None)`` and
  L439: # actually propagates ``langfuse_session_id`` / ``langfuse_user_id`` from
  L440: # ``config["metadata"]`` onto the trace. Without root-level attachment the
  L441: # model is a nested observation and the handler strips ``langfuse_*`` keys.
- `backend/packages/harness/deerflow/agents/middlewares/title_middleware.py`
  L163: # attach_tracing=False because ``_get_runnable_config()`` inherits
  L164: # the graph-level RunnableConfig (set in ``_make_lead_agent``) whose
  L165: # callbacks already carry tracing handlers; binding them again at
  L166: # the model level would emit duplicate spans.
- `backend/packages/harness/deerflow/client.py`
  L241: # attach_tracing=False because ``stream()`` injects tracing
  L242: # callbacks at the graph invocation root so a single embedded run
  L243: # produces one trace with correct session_id / user_id propagation.
  L244: # Attaching them again on the model would emit duplicate spans.
  L589: # Inject tracing callbacks and Langfuse trace metadata at the graph
  L590: # invocation root so the embedded client matches the gateway worker's
  L591: # behaviour: a single ``stream()`` produces one trace with all node /
  L592: # LLM / tool calls nested under it, and the trace carries the reserved
  L593: # ``langfuse_session_id`` / ``langfuse_user_id`` keys that the Langfuse
  L594: # CallbackHandler lifts onto the root trace's ``sessionId`` / ``userId``.
- `backend/packages/harness/deerflow/config/title_config.py`
  L57: """Restore the title configuration to its pristine ``TitleConfig()`` default.
  L64: """
- `backend/packages/harness/deerflow/config/tracing_config.py`
  L153: """Discard the cached :class:`TracingConfig` so the next call rebuilds it.
  L158: """
- `backend/packages/harness/deerflow/models/factory.py`
- `backend/packages/harness/deerflow/runtime/runs/worker.py`
  L231: # Inject Langfuse trace-attribute metadata so the langchain CallbackHandler
  L232: # can lift session_id / user_id / trace_name / tags onto the root trace.
  L233: # Shared helper with ``DeerFlowClient.stream`` so both entry points stay
  L234: # in sync; caller-provided metadata wins via setdefault inside the helper.
- `backend/packages/harness/deerflow/tracing/__init__.py`
- `backend/packages/harness/deerflow/tracing/metadata.py`
  L1: """Langfuse trace-attribute metadata builders.
  L15: """
  L23: # Lazy-imported below to avoid a circular import: ``deerflow.runtime`` eagerly
  L24: # imports the run worker, which in turn needs ``deerflow.tracing``.
  L36: """Return Langfuse trace-attribute metadata for ``RunnableConfig.metadata``.
  L50: """
  L82: """Merge Langfuse trace-attribute metadata into ``config["metadata"]``.
  L91: """

## 1c5c5857 2026-05-21 Lawrance_YXLiao
fix(runtime): bound write_file execution-failure observations (#3133)

* fix(runtime): bound write_file execution-failure observations

* fix(runtime): preserve write_file error prefixes

* test(runtime): trim write_file prefix assertions

* refactor(runtime): drop redundant exception suffix for permission/directory write errors

Address Copilot review on #3133: the PermissionError and IsADirectoryError
branches now return self-contained, non-redundant messages (e.g.
"Error: Permission denied writing to file: /mnt/...") via direct
truncation, instead of going through _format_write_file_error which
appended a duplicate ": PermissionError: permission denied" suffix.

OSError, SandboxError and the generic Exception branches keep the
unified "Failed to write file '{path}': {ExceptionType}: {detail}"
format so the model still sees a stable, machine-readable error class.

Removes the now-unused message= parameter from _format_write_file_error,
keeping a single code path. Truncation contract (<= 2000 chars) and
host-path sanitization unchanged.

* fix(runtime): handle write_file sandbox init errors

Initialize the requested path before sandbox setup so early sandbox failures can still return a bounded write_file error.

Add a regression test for sandbox initialization failures.

* style(test): format sandbox security tests

- `backend/packages/harness/deerflow/sandbox/tools.py`
  L440: """Middle-truncate write_file error details, preserving the head and tail."""
  L464: """Return a bounded, sanitized error string for write_file failures."""

## e93f6584 2026-05-21 Xinmin Zeng
fix(stability): resolve P0 blockers from v2.0-m1-rc1 stability audit (#3107) (#3131)

* fix(task-tool): unwrap callback manager when locating usage recorder

`config["callbacks"]` may arrive as a `BaseCallbackManager` (e.g. the
`AsyncCallbackManager` LangChain hands to async tool runs), not just a plain
list. The previous `for cb in callbacks` loop raised
`TypeError: 'AsyncCallbackManager' object is not iterable`, which
`ToolErrorHandlingMiddleware` then converted into a failed `task` ToolMessage
even though the subagent had completed internally — Ultra mode lost subagent
results and the lead agent fell back to redoing the work.

Unwrap `BaseCallbackManager.handlers` before searching for the recorder.

Refs: bytedance/deer-flow#3107 (BUG-002)

* fix(frontend): treat any task tool error as a terminal subtask failure

The subtask card status machine matched only three English prefixes (`Task
Succeeded. Result:`, `Task failed.`, `Task timed out`). Anything else fell
through to `in_progress`, so a `task` tool error wrapped by
`ToolErrorHandlingMiddleware` (`Error: Tool 'task' failed ...`) left the card
spinning forever even after the run had ended.

Extract the prefix logic into `parseSubtaskResult` and recognise any leading
`Error:` token as a terminal failure. The extracted function is unit-tested
against the legacy prefixes plus the `AsyncCallbackManager` regression
captured in the upstream issue.

Refs: bytedance/deer-flow#3107 (BUG-007)

* fix(frontend): exclude hidden, reasoning, and tool payloads from chat export

`formatThreadAsMarkdown` / `formatThreadAsJSON` iterated raw messages without
running the UI-level `isHiddenFromUIMessage` filter. Exported transcripts
therefore included `hide_from_ui` system reminders, memory injections,
provider `reasoning_content`, tool calls, and tool result messages — content
that is intentionally hidden in the chat view.

Filter the export to the user-visible transcript by default and gate
reasoning / tool calls / tool messages / hidden messages behind explicit
`ExportOptions` flags so a future debug export can opt back in without
forking the formatter.

Refs: bytedance/deer-flow#3107 (BUG-006)

* fix(gateway): route get_config through get_app_config for mtime hot reload

`get_config(request)` returned the `app.state.config` snapshot captured at
startup. The worker / lead-agent path then threaded that frozen `AppConfig`
through `RunContext` and `agent_factory`, so per-run fields edited in
`config.yaml` (notably `max_tokens`) were ignored until the gateway process
was restarted — even though `get_app_config()` already does mtime-based
reload at the bottom layer.

Route the request dependency through `get_app_config()` directly. Runtime
`ContextVar` overrides (`push_current_app_config`) and test-injected
singletons (`set_app_config`) keep working; `app.state.config` is now only
read at startup for one-shot bootstrap (logging level, IM channels,
`langgraph_runtime` engines).

`tests/test_gateway_deps_config.py` encoded the old snapshot contract and is
removed; `tests/test_gateway_config_freshness.py` replaces it with mtime,
ContextVar, and `set_app_config` coverage. `test_skills_custom_router.py` and
`test_uploads_router.py` now inject test configs via FastAPI
`dependency_overrides[get_config]` instead of mutating `app.state.config`.

Document the hot-reload boundary in `backend/CLAUDE.md` so reviewers know
which fields are picked up on the next request vs. which still require a
restart (`database`, `checkpointer`, `run_events`, `stream_bridge`,
`sandbox.use`, `log_level`, `channels.*`).

Refs: bytedance/deer-flow#3107 (BUG-001)

* fix(gateway): broaden get_config 503 to any config-load failure

Address review feedback on the previous commit:

1. Narrow exception catch removed. The old contract returned 503 whenever
   `app.state.config is None`. The first cut only mapped
   `FileNotFoundError`, leaving `PermissionError`, YAML parse errors, and
   pydantic `ValidationError` to bubble up as 500. At the request boundary
   we treat any inability to materialise the config as "configuration not
   available" (503) and log the original exception so the operator still
   has the stack.

2. Removed the unused `request: Request` parameter and the matching
   `# noqa: ARG001`. FastAPI's `Depends()` does not require the dependency
   to accept `Request`; the only call site uses the no-arg form.

3. `backend/CLAUDE.md` boundary now lists the *reason* each field is
   restart-required (engine binding, singleton caching, one-shot
   `apply_logging_level`, etc.), not just the field name, so reviewers do
   not have to reverse-engineer the boundary themselves.

Tests parametrise four exception classes (`FileNotFoundError`,
`PermissionError`, `ValueError`, `RuntimeError`) and assert 503 for each.

Refs: bytedance/deer-flow#3107 (BUG-001)

* fix(task-tool): defend _find_usage_recorder against non-list callbacks

Address review feedback. The previous commit handled the two common shapes
LangChain hands to async tool runs — a plain `list[BaseCallbackHandler]` and
a `BaseCallbackManager` subclass — but iterated any other shape directly,
which would still raise `TypeError` if e.g. a single handler instance leaked
through without a list wrapper.

Treat any non-list, non-manager `config["callbacks"]` value as "no recorder"
rather than crash. Docstring now lists all four shapes explicitly. New tests
cover the single-handler-object case, `runtime is None`, `callbacks is None`,
and `runtime.config` being a non-dict — all required to be silent no-ops.

Refs: bytedance/deer-flow#3107 (BUG-002)

* fix(frontend): drop dead identity ternary and add opt-in export tests

Address review feedback on the previous export commit:

1. Removed the no-op `typeof msg.content === "string" ? msg.content : msg.content`
   expression in `formatThreadAsJSON`. Both branches returned the same value;
   the message content now flows through unchanged whether it is a string or
   the rich `MessageContent[]` shape (LangChain JSON-serialises the array
   structure correctly already).

2. Expanded the JSDoc on `ExportOptions` to make it clearer that the four
   flags are not currently wired to any UI control — callers wanting a debug
   export must build the options object explicitly. The default behaviour
   continues to match the explicit prescription in
   bytedance/deer-flow#3107 BUG-006.

3. Added opt-in coverage. The previous tests only exercised the
   `options = {}` default path; the new cases verify each flag flips the
   corresponding payload back into the export so a future debug-export
   surface does not silently break the contract.

Refs: bytedance/deer-flow#3107 (BUG-006)

* fix(frontend): export subtask prefix constants and document fallback intent

Address review feedback on the previous BUG-007 commit:

1. `SUCCESS_PREFIX`, `FAILURE_PREFIX`, `TIMEOUT_PREFIX`, and the
   `ERROR_WRAPPER_PATTERN` regex are now exported. The JSDoc explicitly
   pins them as part of the backend↔frontend contract defined in
   `task_tool.py` and `tool_error_handling_middleware.py`, so any future
   structured-status migration (e.g. backend writing
   `additional_kwargs.subagent_status` instead of leading text) can
   reference these from one canonical place rather than redefine them.

2. The `in_progress` fallback now carries a docstring explaining the
   deliberate choice — LangChain only ever emits a `ToolMessage` once the
   tool itself has returned, so unrecognised content means the contract
   has drifted and "still running" is the right operator signal (eagerly
   marking it terminal-failed would mask the drift).

No behaviour change; this is documentation and an API export.

Refs: bytedance/deer-flow#3107 (BUG-007)

* fix(gateway): drop app.state.config snapshot and freeze run_events_config

Address @ShenAC-SAC's BUG-001 review on #3131. The previous cut still
stored an ``AppConfig`` snapshot on ``app.state.config`` for startup
bootstrap. Two follow-on hazards from that:

1. Future code touching the gateway lifespan could accidentally start
   reading ``app.state.config`` again, silently regressing the request
   hot path back to a stale snapshot.
2. ``get_run_context()`` paired a freshly-reloaded ``AppConfig`` with the
   startup-bound ``event_store`` and a *live* ``run_events_config``
   field — so an operator who edited ``run_events.backend`` mid-flight
   would have produced a run context whose ``event_store`` and
   ``run_events_config`` referred to different backends.

Clean approach (aligned with the direction in PR #3128):

- ``lifespan()`` keeps a local ``startup_config`` variable and passes it
  explicitly into ``langgraph_runtime(app, startup_config)`` and into
  ``start_channel_service``. No ``app.state.config`` attribute is set at
  any point.
- ``langgraph_runtime`` now accepts ``startup_config`` as a required
  parameter, removing the ``getattr(app.state, "config", None)`` lookup
  and the "config not initialised" runtime error.
- The matching ``run_events_config`` is frozen onto ``app.state`` next
  to ``run_event_store`` so ``get_run_context`` reads the two from the
  same startup-time source. ``app_config`` continues to be resolved
  live via ``get_app_config()``.
- ``backend/CLAUDE.md`` boundary explanation updated to spell out the
  ``startup_config`` / ``get_app_config()`` split.

New regression test ``test_run_context_app_config_reflects_yaml_edit``
exercises the worker-feeding path: it asserts that ``ctx.app_config``
follows a mid-flight ``config.yaml`` edit while
``ctx.run_events_config`` stays frozen to the startup snapshot the
event store was built from.

Refs: bytedance/deer-flow#3107 (BUG-001), bytedance/deer-flow#3131 review

* fix(frontend): parse Task cancelled and polling timed out as terminal

Address @ShenAC-SAC's BUG-007 review on #3131. `task_tool.py` actually
emits five terminal strings:

- `Task Succeeded. Result: …`
- `Task failed. …`
- `Task timed out. …`
- `Task cancelled by user.`               ← previously matched none
- `Task polling timed out after N minutes …` ← previously matched none

The previous cut handled three; the last two fell through to the
"unknown content" branch and pushed the subtask card back to
`in_progress` even though the backend had already reached a terminal
state. Add explicit matches plus regression tests for both. The
`in_progress` fallback is now reserved for genuinely unrecognised
output (i.e. contract drift), as documented.

Refs: bytedance/deer-flow#3107 (BUG-007), bytedance/deer-flow#3131 review

* fix(frontend): sanitize JSON export content via the Markdown content path

Address @ShenAC-SAC's BUG-006 review and the Copilot inline comment on
#3131. The previous cut filtered hidden/tool messages out of the JSON
export but still serialised `msg.content` verbatim, so:

- inline `<think>…</think>` wrappers stayed in the exported `content`
  even with `includeReasoning: false`,
- content-array thinking blocks leaked the `thinking` field,
- `<uploaded_files>…</uploaded_files>` markers leaked the workspace
  paths a user uploaded files to.

JSON now goes through the same sanitiser the Markdown path uses
(`extractContentFromMessage` + `stripUploadedFilesTag`). Reasoning and
tool_calls remain gated behind their `ExportOptions` flags. AI / human
rows that sanitise to empty content with no opted-in reasoning or tool
calls are dropped so the JSON matches the Markdown path's `continue`
on empty assistant fragments.

New regression tests cover the three leak shapes the reviewer called
out plus the empty-content-drop case.

Refs: bytedance/deer-flow#3107 (BUG-006), bytedance/deer-flow#3131 review

* test(gateway): align lifespan stub with langgraph_runtime two-arg signature

Codex round-3 review of c0bc7a06 flagged this: changing
`langgraph_runtime` to require `startup_config` as a second positional
argument broke the one-arg stub `_noop_langgraph_runtime(_app)` in
`test_gateway_lifespan_shutdown.py`, which is patched into
`app.gateway.app.langgraph_runtime` by the lifespan shutdown bounded-timeout
regression. Lifespan would then call the stub with two args and raise
`TypeError` before the bounded-shutdown assertion ran.

Update the stub to match the new signature. The shutdown test itself is
unaffected — it only cares about the channel `stop_channel_service` hang
path.

Refs: bytedance/deer-flow#3107 (BUG-001), bytedance/deer-flow#3131 review

* fix(frontend): strip every known backend marker in export, not just uploads

Codex round-3 review of 258ca800 and the matching maintainer feedback on
PR #3131 made the same point: the JSON export now ran the
Markdown-side sanitiser, but that sanitiser only stripped
`<uploaded_files>`. The full set of payloads middleware embeds inside
message `content` is larger:

- `<uploaded_files>` — `UploadsMiddleware`
- `<system-reminder>` — `DynamicContextMiddleware`
- `<memory>` — `DynamicContextMiddleware` (nested inside system-reminder)
- `<current_date>` — `DynamicContextMiddleware`

The primary protection is still `isHiddenFromUIMessage`: the
`<system-reminder>` HumanMessage is marked `hide_from_ui: true` and never
reaches the formatter. This commit adds the second line of defence so a
regression that drops the `hide_from_ui` flag — or any future middleware
that injects the same tag vocabulary into a visible HumanMessage —
cannot leak the payload into the export file.

Concrete changes:

- New `INTERNAL_MARKER_TAGS` constant + `stripInternalMarkers(content)`
  helper in `core/messages/utils.ts`. The constant doubles as
  documentation for the backend↔frontend contract.
- `formatMessageContent` in `export.ts` now calls `stripInternalMarkers`
  instead of `stripUploadedFilesTag`. UI render paths
  (`message-list-item.tsx`) keep using the narrower function so a user
  legitimately typing `<memory>` in a meta-discussion is preserved.
- The "drop empty rows" guard in `buildJSONMessage` switched from
  `=== undefined` to truthy `!` checks. Codex spotted the asymmetry: when
  `extractReasoningContentFromMessage` returned the empty string (which it
  legitimately can), the JSON path emitted `{reasoning: ""}` while the
  Markdown path's `!reasoning` `continue` correctly dropped the row.

New regression tests cover the defence-in-depth strip with a
`<system-reminder><memory><current_date>` payload deliberately *not*
marked `hide_from_ui`; tool-message sanitization under
`includeToolMessages: true`; the mixed-content-array case
(`thinking + text + image_url`); and the opted-in empty-reasoning drop.

Live verification on a real Ultra-mode thread that uploaded a PDF
(`曾鑫民-薪资交易流水.pdf`): backend state's first HumanMessage carries the
`<uploaded_files>` block (with `/mnt/user-data/uploads/...` paths) as part
of a content-array. The Markdown and JSON export blobs both come back
free of `<uploaded_files>`, `<system-reminder>`, `<current_date>`,
`tool_calls`, and reasoning — while preserving the user's `这是什么 ？`
prompt and the assistant's visible answer.

Refs: bytedance/deer-flow#3107 (BUG-006), bytedance/deer-flow#3131 review

* test(frontend): cover trim, varied N, and pre-execution Error: prefixes

Codex round-3 review of 50e2c257 flagged three coverage gaps in the
subtask-status parser:

1. `Task cancelled by user.` and `Task polling timed out` previously had
   no whitespace-trim coverage — the original trim test only exercised
   the success prefix. Streaming chunks can arrive with leading/trailing
   newlines; the regex needed an explicit assertion.
2. The polling-timeout case was tested only at one `N` (15 minutes). The
   backend interpolates the live `timeout_seconds // 60` value, so the
   matcher must hold for any positive integer. Now we run the case for
   1, 5, and 60 minutes.
3. `task_tool.py` also emits three `Error:` strings for pre-execution
   failures — unknown subagent type, host-bash disabled, and "task
   disappeared from background tasks". They are intentionally handled by
   `ERROR_WRAPPER_PATTERN` rather than dedicated prefixes (the wrapper
   already produces the right terminal-failed shape) but had no test
   coverage proving that wiring. Codex was right that a refactor splitting
   one of them off into its own prefix would silently break things.

The JSDoc on the constants block now spells the three pre-execution
errors out so the relationship between `task_tool.py` returns and the
prefix vocabulary is explicit.

No production code change beyond the docstring — this commit is pure
coverage hardening for the contract that already exists.

Refs: bytedance/deer-flow#3107 (BUG-007), bytedance/deer-flow#3131 review

- `backend/packages/harness/deerflow/tools/builtins/task_tool.py`
  L103: """Find a callback handler with ``record_external_llm_usage_records`` in the runtime config.
  L115: """

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

## be0eae98 2026-05-22 Xinmin Zeng
fix(runtime): suppress tool execution when provider safety-terminates with tool_calls (#3035)

* fix(runtime): suppress tool execution when provider safety-terminates with tool_calls

When a provider stops generation for safety reasons (OpenAI/Moonshot
finish_reason=content_filter, Anthropic stop_reason=refusal, Gemini
finish_reason=SAFETY/BLOCKLIST/PROHIBITED_CONTENT/SPII/RECITATION/
IMAGE_SAFETY/...), the response may still carry truncated tool_calls.
LangChain's tool router treats any non-empty tool_calls as executable,
so partial arguments (e.g. write_file with a half-finished markdown)
get dispatched and the agent loops on retry.

Add SafetyFinishReasonMiddleware at after_model: detect safety
termination via a pluggable detector registry, clear both structured
tool_calls and raw additional_kwargs.tool_calls / function_call,
preserve response_metadata.finish_reason for downstream observers,
stamp additional_kwargs.safety_termination for traces, append a
user-facing explanation to message content (list-aware for thinking
blocks), and emit a safety_termination custom stream event so SSE
consumers can reconcile any "tool starting..." UI.

Default detectors cover OpenAI-compatible content_filter, Anthropic
refusal, and Gemini safety enums (text + image). Custom providers are
added via reflection (same pattern as guardrails). Wired into both
lead-agent and subagent runtimes.

Closes #3028

* fix(runtime): persist safety_termination as a middleware audit event

Address review on #3035: the SSE custom event is great for live
consumers but invisible to post-run audit. RunEventStore should carry
its own row so operators can answer "which runs were safety-suppressed
today?" from a single SQL query without joining the message body.

Worker now exposes the run-scoped RunJournal via
runtime.context["__run_journal"] (sentinel key, internal channel).
SafetyFinishReasonMiddleware calls the previously-unused
RunJournal.record_middleware, which emits

  event_type = "middleware:safety_termination"
  category   = "middleware"
  content    = {name, hook, action, changes={
                  detector, reason_field, reason_value,
                  suppressed_tool_call_count,
                  suppressed_tool_call_names,
                  suppressed_tool_call_ids,
                  message_id, extras}}

Tool *arguments* are deliberately excluded — those are the very content
the provider filtered and persisting them would defeat the purpose of
the safety filter (per review note in #3035).

Graceful skips when journal is absent (subagent runtime, unit tests,
no-event-store local dev). Journal exceptions never propagate into the
agent loop.

Refs #3028

* fix(runtime): satisfy ruff format + address Copilot review

- ruff format on safety_finish_reason_config.py and e2e demo (CI lint
  failed on ruff format --check; backend Makefile lint target runs
  ruff check AND ruff format --check).
- Docstring on SafetyFinishReasonConfig now says resolve_variable to
  match the actual loader used in from_config (the wording was
  resolve_class previously; behavior is unchanged — resolve_variable
  mirrors how guardrails.provider is loaded).
- Switch the AIMessage type check in SafetyFinishReasonMiddleware._apply
  from getattr(last, "type") == "ai" to isinstance(last, AIMessage),
  matching TokenUsageMiddleware / TodoMiddleware / ViewImageMiddleware
  / SummarizationMiddleware which are the dominant pattern.

Refs #3028

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
  L342: # SafetyFinishReasonMiddleware — suppress tool execution when the provider
  L343: # safety-terminated the response. Registered after custom middlewares so
  L344: # that LangChain's reverse-order after_model dispatch runs Safety first;
  L345: # cleared tool_calls then flow through Loop/Subagent accounting without
  L346: # firing extra alarms. See safety_finish_reason_middleware.py docstring.
- `backend/packages/harness/deerflow/agents/middlewares/safety_finish_reason_middleware.py`
  L1: """Suppress tool execution when the provider safety-terminated the response.
  L33: """
  L68: """Strip tool_calls from AIMessages flagged by a SafetyTerminationDetector."""
  L72: # Copy so caller mutations after construction don't leak into us.
  L77: """Construct from validated Pydantic config, honouring the
  L83: """
  L102: # ----- detection -------------------------------------------------------
  L115: # ----- message rewriting ----------------------------------------------
  L119: """Append a plain-text explanation to AIMessage content.
  L124: """
  L146: # clone_ai_message_with_tool_calls handles structured tool_calls,
  L147: # raw additional_kwargs.tool_calls, and function_call in one shot.
  L148: # It only rewrites finish_reason when the old value was "tool_calls",
  L149: # which is not our case — content_filter / refusal / SAFETY stay put
  L150: # so downstream SSE / converters keep seeing the real provider reason.
  L153: # Re-clone additional_kwargs so we don't accidentally mutate the
  L154: # dict returned by clone_ai_message_with_tool_calls (which already
  L155: # made a shallow copy, but downstream model_copy still references
  L156: # it). Then stamp the observability record.
  L168: # ----- observability ---------------------------------------------------
  ... (truncated)
- `backend/packages/harness/deerflow/agents/middlewares/safety_termination_detectors.py`
  L1: """Detectors for provider-side safety termination signals.
  L13: """
  L25: """A detected safety-related termination signal.
  L37: """
  L47: """Strategy interface for provider safety termination detection."""
  L52: """Return a SafetyTermination if *message* indicates provider safety
  L57: """
  L62: """Read a string-typed value from either ``response_metadata`` or
  L71: """
  L83: """OpenAI-compatible content_filter signal.
  L92: """
  L106: # Azure OpenAI ships a structured content_filter_results block; carry it
  L107: # through so operators can see *what* was filtered without re-tracing.
  L123: """Anthropic ``stop_reason == "refusal"`` signal.
  L128: """
  L148: """Gemini / Vertex AI safety-related finish reasons.
  L179: """
  L184: # Text safety
  L190: # Image safety (multimodal generation)
  L208: # Gemini surfaces per-category scoring under safety_ratings.
  ... (truncated)
- `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py`
  L167: # Same provider safety-termination guard the lead agent uses — subagents
  L168: # are equally exposed to truncated tool_calls returned with
  L169: # finish_reason=content_filter (and friends), and the bad call would then
  L170: # propagate back to the lead agent via the task tool result.
- `backend/packages/harness/deerflow/config/app_config.py`
- `backend/packages/harness/deerflow/config/safety_finish_reason_config.py`
  L1: """Configuration for SafetyFinishReasonMiddleware.
  L7: """
  L15: """One detector entry under ``safety_finish_reason.detectors``."""
  L27: """Configuration for the SafetyFinishReasonMiddleware.
  L33: """
- `backend/packages/harness/deerflow/runtime/runs/worker.py`
  L222: # Expose the run-scoped journal under a sentinel key so middleware can
  L223: # write audit events (e.g. SafetyFinishReasonMiddleware recording
  L224: # suppressed tool calls). Double-underscore prefix marks it as a
  L225: # runtime-internal channel; user code must not depend on the key name.

## 2eeb5979 2026-05-22 Lawrance_YXLiao
fix(runs): expose active progress counters (#3148)

* fix(runs): expose active progress counters

* fix(runs): avoid delayed progress flush on completion

* fix(runs): tighten progress snapshot semantics

* fix(runs): preserve omitted progress fields

* chore(runs): remove duplicate journal initialization

- `backend/packages/harness/deerflow/persistence/run/sql.py`
  L245: """Update token usage + convenience fields while a run is still active."""
- `backend/packages/harness/deerflow/runtime/journal.py`
  L508: """Best-effort throttled progress snapshot for active run visibility."""
- `backend/packages/harness/deerflow/runtime/runs/manager.py`
  L145: """Persist a running token/message snapshot without changing status."""
- `backend/packages/harness/deerflow/runtime/runs/store/base.py`
  L113: """Persist a best-effort running snapshot without changing run status."""
- `backend/packages/harness/deerflow/runtime/runs/store/memory.py`
- `backend/packages/harness/deerflow/runtime/runs/worker.py`

## f0bae286 2026-05-22 Nan Gao
fix(middleware): handle repeated tool call ids (#3143)

* fix(middleware): handle repeated tool call ids

* add tests

* refactor(middleware): rely on tool result queues

- `backend/packages/harness/deerflow/agents/middlewares/dangling_tool_call_middleware.py`

## 66d6a6a4 2026-05-23 AochenShen99
fix: harden run finalization persistence (#3155)

* fix: harden run finalization persistence

* style: format gateway recovery test

* fix: align run repository return types

* fix: harden completion recovery follow-up

- `backend/packages/harness/deerflow/persistence/run/sql.py`
  L97: """Insert or update a run row.
  L102: """
  L202: """Return persisted active runs for startup recovery."""
  L238: """Update status + token usage + convenience fields on run completion.
  L241: """
- `backend/packages/harness/deerflow/runtime/runs/manager.py`
  L35: """Return True for transient SQLite persistence failures.
  L41: """
  L66: """Bounded retry policy for short run-store writes."""
  L145: """Run a short store operation with bounded retries for SQLite pressure."""
  L170: """Best-effort persist a previously captured run snapshot."""
  L185: """Best-effort persist run record to backing store."""
  L548: """Mark persisted active runs as failed when no local task owns them.
  L556: """
- `backend/packages/harness/deerflow/runtime/runs/store/base.py`
  L63: """Update a run status.
  L67: """
  L101: """Persist final completion fields.
  L104: """
  L131: """Return persisted runs that are still ``pending`` or ``running``."""
- `backend/packages/harness/deerflow/runtime/runs/store/memory.py`

## 0fb05825 2026-05-23 rayhpeng
fix(runtime): make run creation persistence atomic (#3152)

* fix runtime run creation persistence atomicity

* fix run creation cancellation rollback

* fix run manager test cleanup await

* clarify run creation rollback on cancellation

* document new run persistence rollback boundary

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/runtime/runs/manager.py`
  L185: """Persist a newly created run record to the backing store.
  L192: """
  L349: # Also covers cancellation, which bypasses ``except Exception``.
  L562: # Also covers cancellation, which bypasses ``except Exception``.

## 8785658a 2026-05-23 Huixin615
fix(agents): preserve todos state across node updates (#3180)

* fix(agents): preserve todos state across node updates

ThreadState.todos had no reducer, so any downstream node returning a
partial state without todos was implicitly setting it to None, which
LangGraph then used to overwrite the previously streamed value. This
caused the to-do list to render correctly during streaming but vanish
once streaming completed.

Add a merge_todos reducer that keeps the last non-None value, mirroring
the merge_artifacts pattern already used in the same file. An explicit
empty list is still respected so that 'user cleared todos' works.

Tests: 10 new unit tests in tests/test_thread_state_reducers.py covering
merge_todos plus regression coverage for merge_artifacts and
merge_viewed_images. All 69 thread-related tests pass locally.

Closes #3123

* test(agents): add annotation binding regression guard

Address Copilot review feedback on #3123:

- Add TestThreadStateAnnotations asserting that ThreadState.todos is
  Annotated with merge_todos. Without this guard, reverting the
  Annotated[list | None, merge_todos] binding would silently regress
  #3123 while all existing reducer unit tests continue to pass.

- Align test imports to 'from deerflow.agents.thread_state import ...'
  matching the rest of the backend test suite.

- `backend/packages/harness/deerflow/agents/thread_state.py`
  L49: """Reducer for todos list - keeps the last non-None value.
  L55: """

## f9b70713 2026-05-25 Willem Jiang
fix(sandbox): add group/other read permissions to uploaded files for Docker sandbox (#3127) (#3134)

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

  fixes #3127

* fix(uploads): unconditionally adjust file permissions for sandbox access

  The conditional check  meant uploaded files retained 0o600
  permissions in some Docker sandbox configurations, preventing the
  sandbox process (UID 1000) from reading them. Always add group/other
  read bits so every sandbox setup can access uploaded content. Also add
  read bits to the sync-path writable helper as defense in depth.

- `backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`
- `backend/packages/harness/deerflow/sandbox/sandbox_provider.py`

## e344be8d 2026-05-26 AochenShen99
feat(tests): add Blockbuster runtime gate for event-loop blocking IO (#3229)

* feat(tests): add Blockbuster runtime gate for event-loop blocking IO

Adds a strict runtime gate that fails CI when sync blocking IO calls run
on the asyncio event loop thread through DeerFlow business code.

Components:
- backend/tests/support/detectors/blocking_io_runtime.py — Blockbuster
  context scoped to `app.*` and `deerflow.*` so test infrastructure,
  pytest internals, and third-party libraries stay silent.
- backend/tests/blocking_io/conftest.py — pytest_runtest_protocol
  hookwrapper that wraps every item (setup + call + teardown) with the
  strict context. Respects `@pytest.mark.allow_blocking_io` opt-out.
- backend/tests/blocking_io/test_skills_load.py — regression anchor for
  the #1917 fix (asyncio.to_thread offload around
  LocalSkillStorage.load_skills).
- backend/tests/blocking_io/test_sqlite_lifespan.py — regression anchor
  for the #1912 fix (asyncio.to_thread offload around
  ensure_sqlite_parent_dir).
- backend/tests/blocking_io/test_gate_smoke.py — meta-test asserting the
  gate actually catches unoffloaded blocking IO and that the
  `@pytest.mark.allow_blocking_io` opt-out works.
- backend/Makefile — `make test-blocking-io` target.
- .github/workflows/backend-blocking-io-tests.yml — hard-fail PR gate on
  ubuntu-latest. Windows matrix deferred to follow-up.

Dependencies:
- blockbuster>=1.5.26,<1.6 added to dev group.

Coverage boundary (called out in PR body): the gate only catches blocking
IO on code paths the test suite actually exercises. Static AST inventory
(separate, informational) is the complementary coverage tool. Three blind
spot categories — untested paths, mocked-away paths, env-mismatched paths
— are documented in the PR description.

Findings surfaced while authoring this PR:
- resolve_sqlite_conn_str in runtime/store/_sqlite_utils.py:19 does sync
  Path.resolve() -> os.path.abspath on the lifespan loop thread, ahead of
  the #1912 fix. Not addressed here; tracked as follow-up.

Tests: 4 passed locally (`make test-blocking-io`).
Lint/format: clean (`ruff check` and `ruff format --check`).

* fix(tests): scope Blockbuster gate to blocking-io suite

* fix(tests): harden Blockbuster runtime gate

* test(blocking-io): add project rule extension point

* test(blocking-io): address review cleanup

- `backend/packages/harness/deerflow/runtime/checkpointer/async_provider.py`

## 92905e9e 2026-05-26 QY
fix(todo): reuse thread state schema (#3206)

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/agents/middlewares/todo_middleware.py`

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

## 3cb75887 2026-05-28 Lawrance_YXLiao
fix(memory): parse wrapped memory update json responses (#3252)

* fix(memory): parse wrapped memory update json responses

* test(memory): format wrapped response coverage

* fix(memory): guard malformed nested memory facts

* fix(memory): require full update object when parsing responses

* fix(memory): fail closed on unsafe partial removals

* style(memory): format updater tests

- `backend/packages/harness/deerflow/agents/memory/updater.py`
  L234: """Normalize a single fact entry from a model-produced memory update."""
  L282: """Coerce parsed memory update data into the shape consumed by _apply_updates."""
  L314: """Parse the first valid memory-update JSON object from an LLM response.
  L319: """

## 8decfd32 2026-05-28 AochenShen99
Fix custom skill install permissions (#3241)

* Fix custom skill install permissions

* Fix skill upload test portability

* Keep custom skill writes sandbox readable

* Clear sandbox write bits on skill permissions

* Limit custom skill write permission updates

- `backend/packages/harness/deerflow/skills/installer.py`
- `backend/packages/harness/deerflow/skills/permissions.py`
  L1: """Filesystem permission helpers for installed skill trees."""
- `backend/packages/harness/deerflow/skills/storage/local_skill_storage.py`

## 44677c5e 2026-05-28 AochenShen99
feat(provider) Add patched MiMo reasoning content support (#3298)

* Add patched MiMo reasoning content support

* Clarify MiMo patched model coverage

* Remove unused MiMo payload index

* Address MiMo review nits

- `backend/packages/harness/deerflow/models/patched_mimo.py`
  L1: """Patched ChatOpenAI adapter for Xiaomi MiMo reasoning_content replay.
  L8: """
  L24: """Return reasoning_content from a dict/Pydantic object, preserving empty strings."""
  L65: """ChatOpenAI with ``reasoning_content`` preservation for MiMo thinking mode."""

## cbf8b194 2026-05-29 john lee
fix(runtime): harden JSONL async I/O and DB put_batch thread validation (#3084)

* fix(runtime): harden JSONL async I/O and DB put_batch thread validation (#2816)

- JsonlRunEventStore: offload all file I/O to asyncio.to_thread() so the
  event loop is never blocked; add per-thread asyncio.Lock to serialise
  concurrent puts and prevent interleaved JSONL lines
- Split _ensure_seq_loaded into a sync _compute_max_seq (runs in thread)
  and an async wrapper; seq counter is recovered from disk on fresh store init
- DbRunEventStore.put_batch: raise ValueError when events span multiple
  thread_ids (previously silently assumed same thread)
- Add test_jsonl_event_store_async_io.py: 12 tests covering lock reuse,
  concurrent seq monotonicity, disk recovery, and mixed-thread batch rejection

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* fix: address Copilot review comments

- delete_by_thread: pop _write_locks after releasing the lock to prevent
  unbounded growth when threads are repeatedly created and deleted
- tests: add regression guard asserting asyncio.to_thread is called for
  _write_record in put(); assert _write_locks entry removed on delete

* fix(lint): move patch import to local scope to fix ruff I001

* fix(lint): apply ruff check+format fixes to test file

* fix(runtime): address review feedback for JSONL async I/O hardening (#2816)

Use setdefault for atomic lock init in _get_write_lock; pop _write_locks
inside the held lock scope in delete_by_thread; update test docstring
and assert lock entry also cleared on delete.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

---------

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>
Co-authored-by: rayhpeng <rayhpeng@gmail.com>

- `backend/packages/harness/deerflow/runtime/events/store/db.py`
  L153: # All events belong to the same thread (validated above).
- `backend/packages/harness/deerflow/runtime/events/store/jsonl.py`
  L43: # Per-thread asyncio.Lock — serialises concurrent writes within one process.
  L69: """Scan all run files for a thread and return the current max seq (blocking I/O)."""
  L83: """Load max seq from existing files into the in-memory counter (non-blocking)."""
  L96: """Read all events for a thread, sorted by seq (blocking I/O)."""
  L113: """Read events for a specific run file (blocking I/O)."""
  L206: # Pop the lock inside the held scope to minimise the window where a new caller
  L207: # could obtain a fresh lock while a waiting coroutine still holds the old one.
  L208: # Note: coroutines that already acquired a reference to this lock before the
  L209: # delete will still proceed after we release — this is an accepted narrow race.

## 872079b8 2026-05-29 Eilen Shin
docs: clean standalone LangGraph server remnants (#3301)

- `backend/packages/harness/deerflow/mcp/cache.py`

## e683ed6a 2026-05-29 Nan Gao
fix(runtime): guide malformed write_file recovery (#3040)

* fix(runtime): guide malformed write_file recovery

* fix(runtime): align write_file recovery guidance

- `backend/packages/harness/deerflow/agents/middlewares/dangling_tool_call_middleware.py`
  L29: # Workaround for issue #2894: malformed write_file calls can carry huge Markdown
  L30: # payloads in invalid tool-call args. Keep recovery error details short so the
  L31: # synthetic ToolMessage does not echo large or malformed content back to the model.
  L109: # Workaround for issue #2894: malformed write_file calls can carry huge Markdown
  L110: # payloads in invalid tool-call args. Keep recovery guidance actionable without
  L111: # echoing large or malformed content back to the model.

## ca487578 2026-05-29 Xinmin Zeng
feat(agent): add ToolOutputBudgetMiddleware for oversized tool output protection (#3303)

* feat(agent): add ToolOutputBudgetMiddleware for oversized tool output protection

Closes #3289. Adds a unified middleware that enforces per-result budgets
on ALL tool outputs (MCP, sandbox, community, custom), preventing
oversized external tool results from blowing the model context window.

Design informed by claude-code (persistToolResult), hermes-agent
(tool_result_storage), and pi (OutputAccumulator) — the three most
mature implementations in production coding-agent frameworks.

Key features:
- Disk externalization: oversized outputs written to thread-local
  .tool-results/ directory, replaced with compact preview + file
  reference. Model can read full output via read_file with offset/limit.
- Fallback truncation: head+tail truncation when disk is unavailable
  (no thread_data, write failure), ensuring the context is always
  protected.
- read_file exemption: prevents persist-read-persist infinite loops
  (independently discovered by claude-code, hermes-agent, and pi).
- Per-tool threshold overrides via config.
- Line-boundary-aware truncation (no partial lines in previews).
- Multimodal content passthrough (images/structured blocks skip budget).
- Historical ToolMessage patching in wrap_model_call for checkpoint
  recovery scenarios.

Related: #3222 (design RFC), #1844 (comprehensive context management),
#3137 (write_file args compaction), #1677 (sandbox tool truncation).

* test: add MCP content_and_artifact format coverage

Add 5 tests for MCP tool output format (list of content blocks):
- text content blocks are extracted and budgeted
- multiple text blocks are joined and budgeted
- image content blocks are skipped (multimodal passthrough)
- mixed text+image blocks are skipped
- small text blocks pass through unchanged

Total test count: 59 (was 54).

* fix(agent): address Codex review findings for ToolOutputBudgetMiddleware

Three issues identified by Codex code review, all fixed:

1. `enabled` config field was unused — middleware now checks
   `config.enabled` and skips all processing when disabled.

2. `_build_fallback` could exceed `fallback_max_chars` — the marker
   text itself (~139 chars) was not deducted from the budget. Now
   pre-computes marker overhead and falls back to hard slice when
   max_chars is smaller than the marker.

3. Sync file I/O in async path — `awrap_tool_call` now delegates
   `_patch_result` to `asyncio.to_thread` to avoid blocking the
   event loop during disk writes.

Tests updated to use realistic fallback_max_chars values (500+)
that can accommodate the marker overhead, plus two new tests:
- `test_result_never_exceeds_max_chars` (parametric across sizes)
- `test_very_small_max_chars_does_not_crash`

* fix(agent): address Copilot review — path traversal, async perf, shared config

1. Path traversal defense: sanitize tool_name via _sanitize_tool_name()
   (strips separators, .., absolute paths), validate storage_subdir is
   relative, and verify resolved filepath stays inside storage_dir.

2. Async hot-path optimization: add _needs_budget() cheap check before
   asyncio.to_thread offload — small outputs (99% of calls) skip the
   thread overhead entirely.

3. Replace shared module-level _DEFAULT_CONFIG with _default_config()
   factory to prevent cross-instance mutation of mutable fields.

12 new tests: TestSanitizeToolName (5), TestExternalizePathTraversal (3),
TestNeedsBudget (4).

* fix(agent): correct preview hint to match read_file actual API

read_file uses start_line/end_line (1-indexed line numbers), not
offset/limit. The previous wording was copied from hermes-agent
which has a different read_file interface.

* perf(agent): hoist hot-path imports, add model-call pre-scan (review #3303)

Address maintainer review feedback:

1. Hoist inline imports to module level — `import asyncio` (was in
   awrap_tool_call hot path) and `from dataclasses import replace`
   (was in _patch_result) now live at module top.

2. Add a cheap pre-scan to _patch_model_messages so the historical
   message list is not rebuilt on every model call when nothing is
   oversized (the common case once results are budgeted at tool-call
   time). Also adds the same _needs_budget gate to the sync
   wrap_tool_call for symmetry with awrap_tool_call.

The pre-scan is refactored into per-tool-aware helpers
(_effective_trigger / _tool_message_over_budget) that mirror the exact
trigger conditions in _budget_content — including tool_overrides — so
the fast-path can never produce a false negative (silently skipping
budgeting for a tool with a low per-tool threshold).

7 new regression tests lock the per-tool-override-through-pre-scan path
and the model-call early return.

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py`
- `backend/packages/harness/deerflow/agents/middlewares/tool_output_budget_middleware.py`
  L1: """Middleware that enforces a per-result budget on tool outputs.
  L7: """
  L35: # ---------------------------------------------------------------------------
  L36: # Text helpers
  L37: # ---------------------------------------------------------------------------
  L41: """Extract a plain-text representation from a ToolMessage content field.
  L45: """
  L64: """Return *pos* or the nearest preceding newline+1, whichever is closer.
  L69: """
  L79: # ---------------------------------------------------------------------------
  L80: # Disk persistence
  L81: # ---------------------------------------------------------------------------
  L91: """Strip path separators and traversal components from a tool name."""
  L105: """Write *content* to disk and return the virtual path, or ``None`` on failure."""
  L133: # ---------------------------------------------------------------------------
  L134: # Preview / fallback builders
  L135: # ---------------------------------------------------------------------------
  L146: """Build a preview with a file reference for externalized output."""
  L174: """Build a head+tail truncation when disk persistence is unavailable.
  L177: """
  ... (truncated)
- `backend/packages/harness/deerflow/config/app_config.py`
- `backend/packages/harness/deerflow/config/tool_output_config.py`
  L1: """Configuration for tool output budget protection."""
  L9: """Config section for tool-result output budget enforcement.
  L15: """

## 4093c833 2026-05-29 AochenShen99
refactor(provider): share assistant payload replay matching (#3307)

* Share assistant payload replay matching

* fix(provider): recover assistant field when ordinal AI index is taken

The mismatch-length fallback in `_match_ai_message` only tried the exact
`fallback_ordinal` AI index. When serialization drops or reorders an
assistant message, a unique signature match can consume a non-ordinal
index, leaving a later ambiguous payload's ordinal already used — so its
provider field (e.g. `reasoning_content`) was silently dropped.

Scan forward from the ordinal for the next unused `AIMessage` (wrapping to
earlier indices) to preserve the positional bias while still recovering
the field. Forward scanning avoids a naive min-unused pick that could
restore the wrong field after a leading message is dropped.

Add a regression test for the dropped-leading-message case.

* fix(provider): avoid earlier assistant fallback replay

- `backend/packages/harness/deerflow/models/assistant_payload_replay.py`
  L1: """Helpers for replaying provider-specific assistant message fields.
  L7: """
  L25: """Restore provider-specific fields onto serialized assistant payloads."""
  L43: """Copy a provider-specific ``additional_kwargs`` field onto a payload message."""
  L50: """Copy provider reasoning content onto a serialized assistant payload."""
  L76: """Return the next unused AI index at or after ``start``.
  L83: """
- `backend/packages/harness/deerflow/models/patched_deepseek.py`
- `backend/packages/harness/deerflow/models/patched_mimo.py`
- `backend/packages/harness/deerflow/models/patched_openai.py`

## 9f3be2a9 2026-05-30 AochenShen99
fix(agents): offload UploadsMiddleware uploads scan off the event loop (#3311)

UploadsMiddleware defines only the sync `before_agent` hook. LangChain wires a
sync-only hook as `RunnableCallable(before_agent, None)`, and LangGraph's
`ainvoke` runs it directly on the event loop when `afunc is None` — so the
per-message uploads-directory scan (`exists`/`iterdir`/`stat` plus reading
sibling `.md` outlines) blocks the asyncio event loop on every message that has
an uploads directory.

Add `abefore_agent` that offloads the scan to a worker thread via
`run_in_executor`; it copies the current context, preserving the `user_id`
contextvar read by `get_effective_user_id()`.

Add a runtime anchor under `tests/blocking_io/` that drives the real
`create_agent` graph via `ainvoke` under the strict Blockbuster gate, so a
regression back onto the event loop fails CI. Update blocking-IO docs.

- `backend/packages/harness/deerflow/agents/middlewares/uploads_middleware.py`
  L300: """Async hook that offloads the synchronous uploads scan off the event loop.
  L308: """

## 79cc2279 2026-05-31 Nan Gao
fix(middleware): fix LLM fallback run status (#3321)

* Fix LLM fallback run status

* optimize LLM fallback maker extraction in streaming path

- `backend/packages/harness/deerflow/agents/middlewares/llm_error_handling_middleware.py`
- `backend/packages/harness/deerflow/runtime/journal.py`
- `backend/packages/harness/deerflow/runtime/runs/worker.py`
  L579: """Try to extract fallback marker from a single message object or dict."""
  L592: """Find LLM fallback markers in streamed LangGraph chunks.
  L596: """
  L597: # Fast path: large state chunks produced by stream_mode="values" have a
  L598: # top-level "messages" list. Scanning only that list avoids expensive deep
  L599: # recursion into large state dicts.
  L607: # Fallback marker is attached to an AI message in the messages
  L608: # channel; it will never appear elsewhere in a values chunk.
  L610: # No top-level "messages" — this is likely an "updates" chunk (small
  L611: # dict keyed by node name). Fall through to deep walk, which is cheap
  L612: # for these payloads.
  L614: # Deep walk for updates / messages / tuple / list modes. Payloads are
  L615: # small, so full recursion is acceptable here.

## 031d6fbc 2026-06-01 Willem Jiang
fix(checkpointer): use AsyncConnectionPool for postgres to prevent stale connection errors (#3223) (#3226)

* fix(checkpointer): use AsyncConnectionPool for postgres to prevent stale connection errors (#3223)

  Replace AsyncPostgresSaver.from_conn_string() with an explicit
  AsyncConnectionPool that has check_connection enabled, so dead idle
  connections are detected and replaced on checkout instead of raising
  OperationalError.

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* Fixed the unit test error and lint error

* fix(checkpointer): add TCP keepalive to postgres connection pool (#3254)

  Enable TCP keepalive probes on the AsyncConnectionPool to prevent
  idle postgres connections from being dropped by the server or network
  middleware. Combined with the existing check_connection callback, this
  provides defense-in-depth against stale connection errors.

  Fixes #3254

* Changed the code as review suggestion

---------

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/runtime/checkpointer/async_provider.py`
  L51: """Build an AsyncConnectionPool with TCP keepalive and connection checking."""
  L71: """Import and return (AsyncPostgresSaver, AsyncConnectionPool), raising ImportError on failure."""

## d9f47249 2026-06-02 AochenShen99
fix(tool-search): reliably hide deferred MCP schemas by removing the ContextVar (closures + graph state) (#3342)

* feat(tool-search): add hash-scoped promoted state to ThreadState

* feat(tool-search): add immutable DeferredToolCatalog with stable hash

* feat(tool-search): add build_deferred_tool_setup + Command-writing tool_search

* refactor(tool-search): replace deferred-tool ContextVar with closures + graph state (#3272)

Build the deferred catalog + tool_search tool per agent from the policy-filtered
tool list (after skill allowed-tools), pass deferred_names + catalog_hash
explicitly to DeferredToolFilterMiddleware and the prompt, and record promotions
in ThreadState.promoted (scoped by catalog_hash) via a Command-returning
tool_search. Removes DeferredToolRegistry and the _registry_var ContextVar so
deferral no longer depends on build/execute sharing an async context. MCP tools
are tagged with metadata[deerflow_mcp]; client.py assembles deferral the same way.

Catalog is built AFTER tool-policy filtering (no policy-excluded tool can leak via
tool_search) and assembly is fail-closed. Migrate tests off the deleted registry
APIs; delete the obsolete ContextVar-based #2884 regression (re-covered by
state-based tests in a follow-up).

* test(tool-search): lock tool_search promotion into next model turn via graph state

* test(tool-search): cross-context, policy-leak, fail-closed, #2884 isolation regressions

* test(tool-search): align real-LLM e2e with closure-based deferred setup

* docs: update DeferredToolFilterMiddleware description for closure+state design

* style(tests): drop unused import in test_deferred_setup (ruff)

* test(tool-search): harden merge_promoted + replace tautological catalog test

From independent code review:
- merge_promoted: use existing.get("catalog_hash") so a forward-incompatible
  or externally-injected persisted promoted dict triggers a replace instead of
  a KeyError crash; add regression test for the malformed-existing case.
- test_deferred_catalog: replace the `== [] or True` tautology (a test that
  could never fail) with a deterministic invalid-regex->literal-fallback check
  (positive match on calc + negative empty match).
- DeferredToolCatalog: comment why frozen-without-slots is required for the
  cached_property hash/names fields (adding slots=True would break them).

* fix(tool-search): read tool_search.enabled from self._app_config in client

DeerFlowClient._ensure_agent called get_app_config() directly to read
tool_search.enabled, but the client already resolves and stores its config as
self._app_config at construction (and uses it everywhere else). The bare call
re-resolves config from disk at agent-build time, which raises FileNotFoundError
in environments without a config.yaml (CI) — test_client.py's fixture only
patches get_app_config during __init__, so the later call hit the real loader.
Use self._app_config, matching the rest of the client.

* test(tool-search): lock tool_search post-policy append ordering

tool_search is appended after skill-allowlist filtering, so the allowlist
can no longer deny it by name. Lock the intended contract: it only appears
when allowed MCP tools survive the filter, and its catalog (derived from the
already policy-filtered list) can never expose a denied tool. Addresses the
ordering observation from the Copilot review on #3342.

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
  L322: # Hide deferred tool schemas from model binding until tool_search promotes them.
  L323: # The deferred set + catalog hash come from the build-time setup (assembled
  L324: # after tool-policy filtering); promotion is read from graph state.
  L360: """Build the final tool list + deferred setup from a policy-filtered list.
  L366: """
- `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`
  L688: """Generate <available-deferred-tools> from an explicit deferred-name set.
- `backend/packages/harness/deerflow/agents/middlewares/deferred_tool_filter_middleware.py`
  L30: """Hide deferred tool schemas from the bound model until promoted.
- `backend/packages/harness/deerflow/agents/thread_state.py`
  L67: """Reducer for deferred-tool promotions, scoped by catalog hash.
  L73: """
- `backend/packages/harness/deerflow/client.py`
- `backend/packages/harness/deerflow/tools/builtins/tool_search.py`
  L36: # ── Catalog ──
  L39: # NOTE: frozen=True without slots=True keeps __dict__, which is what lets the
  L40: # @cached_property fields below cache (they write to instance.__dict__, bypassing
  L41: # the frozen __setattr__). Do NOT add slots=True or hash/names break at runtime.
  L44: """Immutable catalog of deferred tools. Pure search, no mutation."""
  L92: # ── Setup / tool ──
  L111: """Fetches full schema definitions for deferred tools so they can be called.
  L122: """
  L140: """Build the deferred-tool setup from a POLICY-FILTERED tool list.
- `backend/packages/harness/deerflow/tools/tools.py`
  L129: # Tag MCP-sourced tools so deferred-tool assembly (done at
  L130: # the agent construction site, AFTER tool-policy filtering)
  L131: # can identify them. No ContextVar / registry is built here;
  L132: # the deferred catalog + tool_search tool are assembled per
  L133: # agent from the policy-filtered tool list.

## 5dc2d6cb 2026-06-02 Ryker_Feng
fix(sandbox): close AioSandbox HTTP client during provider teardown (#2872) (#3245)

* fix(sandbox): close AioSandbox HTTP client during provider teardown (#2872)

AioSandbox allocates a host-side agent_sandbox client (wrapping an
httpx.Client) in __init__, but AioSandboxProvider.release/destroy/shutdown
only popped provider state and tore down the backend container — the
client/transport owned by each cached AioSandbox was never explicitly
closed, accumulating unreclaimed sockets in long-running services.

- Add AioSandbox.close(): best-effort, idempotent close of the wrapped
  httpx_client (falls back to top-level client.close()); errors are
  logged but never raised so backend cleanup is never blocked.
- AioSandboxProvider.release()/destroy() now close the cached AioSandbox
  before dropping it; shutdown() inherits this via destroy().

* fix(sandbox): close the real httpx.Client owned by AioSandbox (#2872)

The previous close() only walked one level (wrapper.httpx_client), which resolves to the Fern-generated HttpClient wrapper that has no close(). The real socket-owning httpx.Client lives one level deeper at _client_wrapper.httpx_client.httpx_client, so the close path never fired and host-side sockets still leaked.

Resolve the real httpx.Client with graceful degradation; clear self._client under the lock for use-after-close and concurrent double-close safety; mark provider release()/destroy() try/except as defense-in-depth; rewrite TestClose against the real nested structure to lock down the original no-op bug.

- `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`
  L49: """Best-effort close of the host-side HTTP client owned by this sandbox.
  L67: """
  L73: # Drop the reference under the lock for use-after-close safety: any
  L74: # later command on this instance fails loudly instead of reusing a
  L75: # half-closed client.
  L81: # Walk from the real httpx.Client up to the top-level client, picking the
  L82: # first object that actually exposes close().
- `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`
  L817: # Defense-in-depth: close() already swallows its own errors; this
  L818: # guard only protects against a future close() that misbehaves, so
  L819: # host-side client cleanup can never block parking in the warm pool.
  L858: # Defense-in-depth: close() already swallows its own errors; this
  L859: # guard only protects against a future close() that misbehaves, so
  L860: # host-side client cleanup can never block container destruction.

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

- `backend/packages/harness/deerflow/config/paths.py`
  L38: """Normalize an external identity into the user-id charset (``[A-Za-z0-9_-]``).
  L44: """
- `backend/packages/harness/deerflow/mcp/tools.py`
  L141: # Preserve interceptor-injected headers for stdio MCP calls by
  L142: # forwarding them through MCP call meta.

## 8fca56cf 2026-06-03 Ryker_Feng
fix(mcp): accept transport field as alias for type (#3238) (#3243)

The official MCP configuration schema uses `transport` to specify the
transport mechanism (stdio/sse/http), but `McpServerConfig` only honored
`type` and defaulted to `stdio`. Remote MCP servers configured with just
`transport: sse` were therefore misidentified as stdio and failed with
"with stdio transport requires 'command' field".

Add a model validator that promotes `transport` to `type` when only
`transport` is provided, while keeping `type` authoritative when both
are set. This matches the MCP-spec field name without breaking existing
configurations.

Fixes #3238

- `backend/packages/harness/deerflow/config/extensions_config.py`
  L53: """Accept the MCP-spec ``transport`` field as an alias for ``type``.
  L61: """

## 89ae74d4 2026-06-03 Huixin615
fix(skills): surface offending line and quoting hint on SKILL.md YAML… (#3335)

* fix(skills): surface offending line and quoting hint on SKILL.md YAML errors

When a SKILL.md front-matter fails to parse, the existing log only
echoes PyYAML's raw message, leaving authors to grep the file for the
offending line. This is especially painful for the very common
LLM-authored mistake of an unquoted scalar containing ': '
(e.g. 'description: foo: bar'), which fails with
'mapping values are not allowed here' and silently drops the skill.

Enrich the error log with:
  - the source line PyYAML pointed at via problem_mark
  - a targeted, copy-pasteable quoting hint when (and only when) the
    error is the well-known 'mapping values are not allowed' scanner
    error on an unquoted value

The skill is still rejected (no semantics are guessed or rewritten);
only the diagnostic is improved.

Fixes #3333

* improve(skills): address CR feedback on SKILL.md YAML error diagnostics

Per review on #3335:

- Log the file line number (mark.line + 2) instead of the
  front-matter-internal line number, so authors land on the right
  row in their editor.
- Use exc.problem == "mapping values are not allowed here" for a
  tighter match than substring-scanning str(exc).
- Preserve the offending key's leading whitespace in the quoting
  hint so nested mappings stay nested when authors paste the fix
  back.
- Rewrite the regression test to actually exercise the new
  behaviour: PyYAML's own message already echoes the offending
  line (and truncates it with "..."), so the old assertion
  passed on main. New assertions pin (a) the file-line number,
  (b) the full untruncated line, and (c) the copy-pasteable hint.
- Add a guard test for nested-key indentation so the
  partition()/strip() shape cannot regress silently.

Refs #3333, #3335

* fix(skills): escape backslashes in YAML quoting hint

The hint emitted by _format_yaml_error previously escaped only double
quotes, so values containing backslashes (e.g. Windows paths like
C:\Temp or regex escapes like \d) produced a suggested scalar that
was either invalid YAML or silently re-interpreted by PyYAML's
double-quoted escape rules when pasted back. Escape order matters:
backslashes first, then double quotes.

Adds two regression tests covering Windows-path and regex-style
backslashes.

Address Copilot CR feedback on PR #3335.

- `backend/packages/harness/deerflow/skills/parser.py`
  L13: """Render a developer-friendly explanation of a YAML front-matter error."""
  L22: # mark.line is 0-based within the front-matter body; +1 makes it
  L23: # 1-based, +1 more accounts for the leading `---` fence that the
  L24: # front-matter regex strips before yaml.safe_load sees it. The
  L25: # result matches the line number an author sees in their editor.
  L29: # Targeted hint for the most common authoring mistake: an unquoted
  L30: # scalar value whose body contains ``: ``. We only surface the hint
  L31: # when we are confident it applies, to avoid misleading authors who
  L32: # hit unrelated YAML errors.

## 28b1da21 2026-06-04 Eilen Shin
fix(agents): harden update_agent null-like args (#3237)

* fix(agents): harden update_agent null-like args

* docs: mention undefined null-like update args

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`
- `backend/packages/harness/deerflow/tools/builtins/update_agent_tool.py`

## 2bbc7879 2026-06-05 AochenShen99
refactor(tool-search): consolidate MCP metadata tag and harden deferred-tool setup (#3370)

Follow-up to #3342 (deferred MCP tool loading). Maintainability cleanup plus
hardening of malformed/empty tool_search queries; no change to the deferral
mechanism or search ranking.

- Add deerflow/tools/mcp_metadata.py as the single source of truth for the
  "deerflow_mcp" tag (MCP_TOOL_METADATA_KEY + tag_mcp_tool + public
  is_mcp_tool). Removes the duplicated magic string and the private,
  cross-module _is_mcp_tool import.
- tool_search.search: never raise on model-generated input. Extract
  _compile_catalog_regex (shared compile-with-literal-fallback); return empty
  for empty/whitespace queries and a bare "+" instead of matching everything
  or raising IndexError.
- DeferredToolSetup: document the empty-vs-populated invariant.
- build_deferred_tool_setup: comment the two distinct empty-return branches.
- _assemble_deferred: add return type, rename local to deferred_setup, build
  the final list with an explicit append.
- Tests: use tag_mcp_tool instead of per-file tag helpers; cover empty and
  bare-"+" queries.

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- `backend/packages/harness/deerflow/tools/builtins/tool_search.py`
  L39: """Compile ``pattern`` case-insensitively, falling back to a literal match.
  L43: """
  L111: """Result of assembling deferred-tool support for one agent build.
  L123: """
  L174: # Deferral disabled: defer nothing; the model binds every tool as before.
  L178: # Enabled, but no MCP tool to defer: same empty result, different reason.
- `backend/packages/harness/deerflow/tools/mcp_metadata.py`
  L1: """Single source of truth for the MCP-tool metadata tag.
  L12: """
  L22: """Mark ``tool`` as MCP-sourced. Mutates in place and returns it for chaining."""
  L28: """True when ``tool`` carries the MCP-source tag written by :func:`tag_mcp_tool`."""
- `backend/packages/harness/deerflow/tools/tools.py`

## 1aac408d 2026-06-06 Nan Gao
fix upload file size contract (#3408)

- `backend/packages/harness/deerflow/client.py`
- `backend/packages/harness/deerflow/uploads/manager.py`
  L300: """Add virtual paths and artifact URLs on a listing result.

## 268fdd69 2026-06-07 Xinmin Zeng
fix(gateway): drain in-flight runs before closing checkpointer on shutdown (#3381)

* fix(gateway): drain in-flight runs before closing checkpointer on shutdown

Chat runs execute in fire-and-forget background asyncio tasks that write
checkpoints through a shared checkpointer. On shutdown, langgraph_runtime's
AsyncExitStack tore down the checkpointer's postgres connection pool while
those run tasks were still mid-graph. langgraph's
AsyncPregelLoop._checkpointer_put_after_previous then ran its
`finally: await checkpointer.aput(...)` against the closed pool, raising
psycopg_pool.PoolClosed. Because that put runs in a langgraph-internal task
(not on run_agent's call stack), run_agent's try/except cannot catch it and it
surfaces as "unhandled exception during asyncio.run() shutdown".

Add RunManager.shutdown() to cancel and bounded-await all in-flight runs, and
call it from langgraph_runtime BEFORE the AsyncExitStack closes the
checkpointer, so the final checkpoint write lands while the pool is still open.
The drain is bounded by a timeout so a stuck run cannot hang worker shutdown,
and is shielded so a second shutdown signal cannot abandon it mid-drain and
reopen the race.

Closes #3373

* fix(gateway): address review — preserve completed-run status, bound drain persistence

Addresses Copilot review on #3381:

- RunManager.shutdown(): decide run status AFTER the drain. Under the lock it
  now only requests cancellation; after asyncio.wait it marks/persists
  `interrupted` only for runs still pending or ended cancelled. A run that
  completes (e.g. `success`) during the drain window keeps its real terminal
  status instead of being unconditionally overwritten.
- Bound the trailing status persistence within the timeout budget
  (deadline = loop.time()+timeout; gather wrapped in asyncio.wait_for) so a slow
  store backing off under DB pressure cannot push shutdown past the deadline.
- deps: use asyncio.create_task instead of asyncio.ensure_future.
- tests: wait deterministically for the run to be in-flight (poll the first
  checkpoint) instead of a fixed sleep; init shutdown_calls explicitly in the
  recovery test double; add regression test asserting a run completing during
  the drain keeps its status (in memory and in the store).

* fix(gateway): address maintainer review — surface failed drain persists, clarify timeout constant

Addresses @WillemJiang review on #3381:

- shutdown(): inspect the gather result of the trailing interrupted-status
  persistence. _persist_status is best-effort (it catches + logs its own
  failure with exc_info and returns False, so it never raises out of the
  gather), but the aggregate result was never checked — a partial failure had
  no shutdown-level visibility. Now any escaped Exception is logged, and any
  False (a persist that did not confirm) is logged with the run_id. Added
  regression test test_shutdown_surfaces_failed_interrupted_persist.
- deps: clarify the _RUN_DRAIN_TIMEOUT_SECONDS comment — state the actual value
  of _SHUTDOWN_HOOK_TIMEOUT_SECONDS (5.0s) and that both count toward the
  lifespan shutdown window. Kept as two separate constants (independent teardown
  steps that may diverge) rather than one shared "must match" value.
- Verified no other test fake needs the shutdown stub: _FakeRunManager in
  test_worker_langfuse_metadata.py is a run_agent() argument (worker path),
  never injected into langgraph_runtime, so it never receives shutdown().

- `backend/packages/harness/deerflow/runtime/runs/manager.py`
  L649: """Cancel and bounded-await all in-flight runs on process shutdown.
  L674: """
  L684: # Status is decided AFTER the drain (below), not here: a run that
  L685: # completes on its own during the drain must keep its real status.
  L693: # Only mark/persist ``interrupted`` for runs that did not settle on their
  L694: # own (still pending after the timeout, or ended cancelled). A run that
  L695: # finished normally during the drain keeps the status it set for itself.
  L701: # Completed on its own — retrieve any surfaced exception so it
  L702: # is not reported as "never retrieved", and keep its status.
  L710: # Bound the trailing status persistence within the remaining budget so a
  L711: # slow store (``_call_store_with_retry`` can back off under DB pressure)
  L712: # cannot push shutdown past ``timeout``.
  L726: # ``_persist_status`` is best-effort: it catches and logs its
  L727: # own failures, returning ``False``. Inspect the aggregate so a
  L728: # partial failure is surfaced at shutdown level (with the
  L729: # run_id) instead of being silently swallowed by the gather.

## 88e36d96 2026-06-07 Huixin615
fix(#3189): prevent write_file streaming timeout on long reports (#3195)

* fix(#3189): prevent write_file streaming timeout on long reports

Adds a layered defense against StreamChunkTimeoutError caused by oversized
single-shot write_file tool calls:

- factory: default stream_chunk_timeout to 240s for OpenAI-compatible
  clients (overridable via ModelConfig.stream_chunk_timeout in config.yaml)
- sandbox/tools: server-side 80 KB length guard on non-append write_file
  calls (configurable via DEERFLOW_WRITE_FILE_MAX_BYTES env var, 0 disables);
  rejects oversized payloads with a structured error pointing the model at
  str_replace or append=True
- middleware: classify StreamChunkTimeoutError as transient but cap retries
  at 1 via per-exception _RETRY_BUDGET_OVERRIDES (same-payload retry on a
  chunk-gap timeout buffers the same way upstream; full 3-attempt loop
  would stack 6-12 min of dead air)
- middleware: surface an actionable user-facing message for stream-drop
  exceptions instead of leaking the raw langchain stack
- prompts: add a routing-style File Editing Workflow hint to both lead_agent
  and general_purpose subagent prompts, pointing the model at str_replace
  for incremental edits (mirrors Claude Code's Edit / Codex's apply_patch)
- tests: behavioural coverage for size guard, retry budget override,
  stream-drop user message, factory default injection

Refs #3189

* fix(#3189): drop stream_chunk_timeout for non-OpenAI providers

Address CR feedback on PR #3195:

- factory: pop `stream_chunk_timeout` from kwargs for any model_use_path other than `langchain_openai:ChatOpenAI` instead of returning early. `ModelConfig.stream_chunk_timeout` is part of the shared schema, so a user-supplied value on a non-OpenAI provider would otherwise be forwarded to its constructor and raise `TypeError: unexpected keyword argument`.

- factory: rewrite docstring to describe the actual `exclude_none=True` behaviour (explicit null is excluded and falls back to the default) instead of the misleading "None falling out via exclude_none=True keeps its value".

- tests: add regression coverage asserting the kwarg is stripped before reaching a non-OpenAI provider's constructor.

Refs: bytedance#3189

* fix(#3189): restrict stream-drop user copy to StreamChunkTimeoutError only

Per CR on #3195: narrow _STREAM_DROP_EXCEPTIONS to StreamChunkTimeoutError. Generic httpx RemoteProtocolError / ReadError fall back to the standard 'temporarily unavailable' copy, since they routinely fire on transient network blips where the 'split the output' guidance is misleading. Retry/backoff classification is unchanged — both remain transient/retriable. Tests updated to reflect new copy, plus a symmetric regression test for ReadError.

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`
- `backend/packages/harness/deerflow/agents/middlewares/llm_error_handling_middleware.py`
  L65: # Per-exception retry budget overrides.
  L66: #
  L67: # Some transient errors are retriable in principle but expensive to retry at
  L68: # the default budget. StreamChunkTimeoutError in particular fires after the
  L69: # upstream provider has already stalled for `stream_chunk_timeout` seconds
  L70: # (typically 120-240s); a full 3-attempt loop can therefore stack 6-12 minutes
  L71: # of dead air before surfacing the failure to the user. We keep exactly one
  L72: # retry (cheap reconnect that catches genuine transient TCP blips) and then
  L73: # fail fast — the same buffered payload is overwhelmingly likely to fail
  L74: # again at the upstream provider for the same reason.
  L75: #
  L76: # Keys are exception class *names* (not classes) so we don't introduce
  L77: # import-time coupling on optional dependencies like langchain-openai. The
  L78: # value is the absolute max attempt count, NOT additional retries — so a
  L79: # value of 2 means "1 first attempt + 1 retry" (the CR-requested
  L80: # "keep one retry" behavior).
  L85: # Exception class names that indicate the upstream stream-chunk watchdog
  L86: # fired because the model stalled mid-flight. These deserve a more specific
  L87: # user-facing message than the generic "temporarily unavailable" copy,
  L88: # because the typical root cause is a long tool-call serialization stalling
  ... (truncated)
- `backend/packages/harness/deerflow/config/model_config.py`
- `backend/packages/harness/deerflow/models/factory.py`
  L50: # Default chunk-gap budget for OpenAI-compatible streaming responses.
  L51: #
  L52: # langchain-openai raises ``StreamChunkTimeoutError`` after this many seconds
  L53: # without receiving a chunk. Its own default is 60s, which is too aggressive for
  L54: # reasoning models (DeepSeek-R1, Doubao-thinking, GPT-5) whose first chunk can
  L55: # legitimately take 90~150s. We default to 240s so the streaming layer rarely
  L56: # trips on long thinking pauses; the LLMErrorHandlingMiddleware still retries
  L57: # (budget=2) if a real stall happens. Users can override per-model in config.yaml.
  L62: """Inject a generous ``stream_chunk_timeout`` for OpenAI-compatible clients.
  L73: """
- `backend/packages/harness/deerflow/sandbox/tools.py`
  L48: # Maximum bytes accepted in a single non-append write_file call (issue #3189).
  L49: # Oversized single-shot writes correlate with LLM streaming chunk-gap timeouts
  L50: # because the tool-call JSON payload (which the model must emit as one
  L51: # continuous stream) grows past the safe window. 80 KB ≈ 20K tokens, a
  L52: # comfortable headroom under the factory-default 240s stream_chunk_timeout.
  L53: # Deployments can override via env var DEERFLOW_WRITE_FILE_MAX_BYTES; set to
  L54: # 0 (or negative) to disable the guard entirely.
  L1686: """Return the active size cap for non-append write_file calls.
  L1692: """
  L1710: """Write text content to a file. By default this overwrites the target file; set append=True to add content to the end without replacing existing content.
- `backend/packages/harness/deerflow/subagents/builtins/general_purpose.py`

## d133b111 2026-06-07 Ryker_Feng
fix(summarization): tag summary LLM calls nostream to stop phantom stream messages (#2503) (#3378)

* fix(summarization): tag summary LLM calls nostream to stop phantom stream messages (#2503)

The SummarizationMiddleware runs its summary LLM call inside a before_model
hook. Without a nostream tag the summary tokens were captured by LangGraph's
messages-tuple stream callback and broadcast to the frontend as a phantom AI
message.

Generate a dedicated summary model copy tagged with "nostream" (merged on top
of any existing tags such as "middleware:summarize" so RunJournal attribution
is preserved) and override _create_summary / _acreate_summary to invoke it
directly. This avoids temporarily swapping the shared self.model, which would
otherwise leak the RunnableBinding across concurrent runs and break parent
logic that inspects the raw model (profile / _get_ls_params).

Add regression tests covering nostream tagging, concurrent-run isolation, raw
model preservation, and existing-tag merge.

* fix(summarization): address nostream review feedback

- `backend/packages/harness/deerflow/agents/middlewares/summarization_middleware.py`
  L120: # The summary LLM call runs inside a LangGraph middleware hook, so its token
  L121: # stream would otherwise be captured by the messages-tuple stream callback and
  L122: # broadcast to the frontend as a phantom AI message. Tag a dedicated model copy
  L123: # with TAG_NOSTREAM so the streaming handler skips it.
  L124: # Keep self.model untagged so the parent's profile / ls_params inspection still works.
  L125: #
  L126: # Preserve any tags already bound on the model (e.g. "middleware:summarize" set in
  L127: # lead_agent/agent.py for RunJournal attribution): RunnableBinding.with_config does a
  L128: # shallow merge that would otherwise overwrite the existing tags list entirely.
  L142: """Mirror the parent ``_create_summary`` but invoke the nostream-tagged model.
  L148: """
  L164: """Async counterpart of :meth:`_summarize_with` using the nostream model."""
  L180: """Build the summary prompt, returning ``None`` when trimming leaves nothing."""
  L184: # Format messages to avoid token inflation from metadata when str() is called on
  L185: # message objects.

## befe334f 2026-06-07 Xinmin Zeng
fix(config): make the reload boundary discoverable from code (#3144) (#3153)

* fix(config): make the reload boundary discoverable from code, not just docs

Closes #3144.

The hot-reload contract — per-run fields are resolved through
`get_app_config()` on every request, infrastructure fields snapshot at
gateway startup — landed in `backend/CLAUDE.md` as part of #3131. A
maintainer reading `get_config()` or an `AppConfig` field still had to
context-switch to that document to know which fields require a process
restart, and there was no enforcement that the prose list stayed in
sync with the code.

This commit moves the boundary to a machine-readable single source of
truth and surfaces it where the code lives:

- New `deerflow.config.reload_boundary` module owns the registry of
  restart-required fields (`STARTUP_ONLY_FIELDS`) and a tiny helper
  API (`is_startup_only_field`, `iter_startup_only_field_paths`,
  `format_field_description`). The standardised `"startup-only:"`
  prefix is exported as `STARTUP_ONLY_PREFIX` so future scanners /
  lint hooks / doc generators can pivot off it without re-parsing
  prose.
- `AppConfig`'s `database`, `checkpointer`, `run_events`,
  `stream_bridge`, `sandbox`, and `log_level` fields now build their
  `Field(description=...)` from `format_field_description(...)`. The
  same text shows up in IDE hover (Pydantic v2 exposes `description`
  via `model_fields[...]`).
- `channels` is restart-required too but lives outside the AppConfig
  Pydantic schema (the config section is consumed directly by
  `start_channel_service`). The registry owns it so the boundary is
  not split between two places.
- `get_config()` docstring points to the registry instead of leaving
  the reader to find `CLAUDE.md`. The `CLAUDE.md` table collapses to
  a one-liner pointing back at `reload_boundary.py` so the boundary
  has one canonical location, not two.

Drift coverage in `tests/test_reload_boundary.py`:

- Every registered field has a non-trivial reason.
- Iterator / membership helpers stay in sync with the dict.
- Every registry entry that maps to an `AppConfig` field also carries
  the `"startup-only:"` prefix in the schema (catches "forgot to
  update the schema").
- Reverse drift: any AppConfig field whose description starts with
  the prefix must be registered (catches "marked restart-required in
  the schema but forgot the registry").
- The runtime introspection that IDE hover depends on
  (`AppConfig.model_fields["database"].description`) is pinned, so a
  future Pydantic upgrade or schema swap that breaks the hover surface
  shows up as a test failure rather than a silent regression.

Refs: bytedance/deer-flow#3138 (split summary), #3107 (origin), #3131
(prior boundary fix in prose form).

* fix(config): preserve field doc and correct log_level reload reason

Two follow-ups on the PR #3153 review:

1. The `log_level` STARTUP_ONLY_FIELDS reason previously claimed
   `apply_logging_level()` mutates the root logger level. It does not:
   only the `deerflow` / `app` logger levels are set, and root handler
   thresholds are conditionally lowered so messages from those loggers
   can propagate. Reword to match the actual behavior so operators
   reading IDE hover get accurate restart guidance.

2. `format_field_description(field_path)` was the sole `Field(description=)`
   for every restart-required field, which silently overwrote the
   original human-facing documentation — most visibly the `log_level`
   field that used to list debug/info/warning/error and clarify that
   third-party libraries are not affected. Extend the helper with a
   keyword-only `field_doc` parameter that composes the startup-only
   marker with the original prose so IDE hover documents both *why*
   the field is restart-required and *what* it actually accepts.
   Updated all six restart-required AppConfig fields (`log_level`,
   `database`, `sandbox`, `run_events`, `checkpointer`, `stream_bridge`)
   to pass their original descriptions through the helper.

Tests: two new cases in `test_reload_boundary.py` pin (a) the helper
composition and (b) every AppConfig restart-required field still
surfaces a recognisable substring of its original documentation.

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/config/app_config.py`
- `backend/packages/harness/deerflow/config/reload_boundary.py`
  L1: """Single source of truth for the config hot-reload boundary.
  L26: """
  L32: #: The standardised prefix every restart-required field description starts
  L33: #: with. ``test_reload_boundary`` enforces both directions: registered
  L34: #: fields must use this prefix in the schema, and any schema field using
  L35: #: this prefix must be in the registry.
  L39: #: Restart-required field paths mapped to the human-readable reason.
  L40: #:
  L41: #: The reason text is what surfaces in ``Field(description=...)``, so it
  L42: #: must explain *what* code captures the snapshot — not just that the
  L43: #: field is restart-required — so an operator changing the value knows
  L44: #: which subsystem to restart.
  L54: # Not part of the AppConfig Pydantic schema — channel credentials are
  L55: # consumed directly by ``start_channel_service()`` once at lifespan
  L56: # startup and the live channel clients are not rebuilt on
  L57: # config.yaml edits.
  L63: """Yield every registered restart-required field path."""
  L68: """Return ``True`` when *field_path* is registered as restart-required.
  L73: """
  L78: """Build the standardised description for a registered field.
  ... (truncated)

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

## 8d2e55a0 2026-06-07 Xinmin Zeng
fix(subagent): structured subagent_status field over text parsing (#3146) (#3154)

* fix(subagent): structured subagent_status field over text parsing

Closes #3146.

## Why

The frontend used to derive subtask card state by string-matching the
leading text of the `task` tool's result. That contract surface was
fragile — `#3107` BUG-007 and the `#3131` review both surfaced cases
where new backend wording (`Task cancelled by user.`,
`Task polling timed out after N minutes`, `ToolErrorHandlingMiddleware`
exception wrappers) silently broke the card lifecycle. The frontend
fallback kept growing more prefixes; any future rewording would break
it again.

## Design

1. **Backend → frontend contract**: `ToolMessage.additional_kwargs`
   carries `subagent_status` (one of `completed | failed | cancelled |
   timed_out | polling_timed_out`) and an optional `subagent_error`
   blob. The frontend prefers it over parsing `content`.

2. **Centralised stamping, not 8 sprinkled stamps**: rather than have
   each of `task_tool.py`'s 5 normal-return + 3 pre-execution `Error:`
   paths remember to set `additional_kwargs`, `ToolErrorHandlingMiddleware`
   stamps the field after every task-tool call. Adding a new return
   path in `task_tool.py` cannot now skip the stamp.

3. **Cross-language contract fixture**: the prefix→status mapping is
   the one piece both sides must agree on. The shared fixture at
   `contracts/subagent_status_contract.json` lists every backend return
   string, the expected status, and what the error substring should
   contain. Backend test (`backend/tests/test_subagent_status_contract.py`)
   and frontend test (`frontend/tests/unit/core/tasks/subtask-result.test.ts`)
   both load that fixture and assert the same cases. A wording drift on
   either side fails the matching language's test.

4. **Round-trip serialisation pinned**: the round-trip test asserts
   `ToolMessage.model_dump_json()` → `model_validate_json()` preserves
   `additional_kwargs.subagent_status`. Catches the case where a future
   LangChain or Pydantic upgrade silently strips unknown kwargs.

5. **Frontend status collapse documented**: the backend has five status
   values, the frontend card has three (`completed | failed |
   in_progress`). `cancelled` / `timed_out` / `polling_timed_out` all
   collapse to `failed` with the original status preserved in `error`.
   `parseSubtaskResult` returns `in_progress` for unknown values so a
   backend that ships a new enum variant before the frontend upgrades
   degrades to the legacy prefix fallback instead of getting pinned.

## Changes

Backend:
- `deerflow.subagents.status_contract` — new module exporting
  `SUBAGENT_STATUS_KEY`, `SUBAGENT_ERROR_KEY`,
  `SUBAGENT_STATUS_VALUES`, `extract_subagent_status(content)`, and
  `make_subagent_additional_kwargs(status, error)`.
- `ToolErrorHandlingMiddleware`: new `_stamp_task_subagent_status`
  helper centralises the stamp; `wrap_tool_call` / `awrap_tool_call`
  stamp on the success path; `_build_error_message` stamps on the
  wrapper path (carrying `ExcClass: detail` into `subagent_error`).
  Non-task tools are untouched.
- New tests: `test_subagent_status_contract.py` (19 cases from the
  shared fixture + status-enum / blank-error / unknown-status
  rejection) and `test_tool_error_handling_subagent_stamp.py`
  (middleware integration: terminal-content stamps, non-terminal
  doesn't, non-task tools untouched, async path mirrors sync,
  existing additional_kwargs survive, JSON round-trip preserved).

Frontend:
- `parseSubtaskResult(text, additionalKwargs?)` — prefers the
  structured stamp; falls back to the legacy prefix matcher for
  historical threads / unknown future status values.
- `STRUCTURED_STATUS_TO_SUBTASK` documents the five→three collapse.
- `message-list.tsx` passes `message.additional_kwargs` through.
- `subtask-result.test.ts` adds a structured-status block + a
  fixture-driven contract block; legacy prefix tests stay green for
  the fallback path.

Contract:
- `contracts/subagent_status_contract.json` — single source of truth
  both languages load. Whitespace variants, varied N for polling
  timeouts, the 3 pre-execution `Error:` returns task_tool produces,
  and the middleware wrapper shape are all in there.

## Test plan
- `make lint` clean (backend + frontend).
- `pytest tests/test_subagent_status_contract.py
   tests/test_tool_error_handling_subagent_stamp.py` → 37 passed.
- `pnpm test --run` → 103 passed (was 76, +27 new).

## Migration / fallback retirement

The text-prefix fallback stays in place until backend telemetry shows
the frontend never hits it for newly produced messages. At that point
a follow-up PR can drop the prefix branches and keep only the
structured-status branch.

Refs: bytedance/deer-flow#3138 (split summary), #3107 (origin), #3131
(prior prefix-only fix), #3146 (this issue).

* fix(subtask): back-fill result/error from text when structured status present

Three follow-ups on the PR #3154 review:

1. `readStructuredStatus` no longer short-circuits the prefix parse.
   The backend currently stamps only the `subagent_status` enum value;
   the human-facing `result` body and wrapped-error message still live
   in `ToolMessage.content`. Dropping the text parse meant successful
   tasks rendered empty completed pills and wrapped failures lost their
   diagnostic. Now both shapes get composed: structured status wins,
   `result`/`error` come from text when both sides agree, and a lying
   success body under a `failed` stamp is dropped instead of leaking.

2. Replace the ESM-incompatible `__dirname` fixture lookup in
   subtask-result.test.ts with `fileURLToPath(new URL(..., import.meta.url))`.
   The frontend package is `"type": "module"`, so the previous path
   would have thrown at runtime if anything ever changed under the
   contract directory.

3. Drop the `$schema` reference from contracts/subagent_status_contract.json
   pointing at a file that doesn't exist in the tree.

Three new tests cover the structured + text composition: completed
back-fills the success body, failed back-fills the wrapper text, and
unrecognised content under a `failed` stamp stays empty rather than
echoing noise.

- `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py`
  L27: """Centralised stamping of ``additional_kwargs.subagent_status``.
  L39: """
  L45: # Non-terminal streaming chunks or unrecognised shapes leave the
  L46: # field unset so the frontend can keep the card on its in-progress
  L47: # placeholder until a real terminal frame arrives.
  L73: # Stamp the structured subagent status on the wrapper too: the
  L74: # frontend would otherwise have to fall back to prefix-matching
  L75: # ``Error: Tool 'task' failed ...`` on the wire. The ``subagent_error``
  L76: # carries the same ``ExcClass: detail`` shape the wrapper string
  L77: # uses so debugging artifacts stay aligned.
  L83: """Apply the subagent stamp to successful task tool returns.
  L87: """
- `backend/packages/harness/deerflow/subagents/status_contract.py`
  L1: """Backend↔frontend contract for the structured subagent status.
  L21: """
  L38: #: Enumeration of every value ``subagent_status`` may take. Mirrors the
  L39: #: ``valid_status_values`` array in the shared fixture; the contract test
  L40: #: pins them against each other.
  L49: # Prefix table — ordered most-specific-first because some prefixes are
  L50: # substrings of others ("Task timed out" vs "Task polling timed out", "Task
  L51: # failed" vs "Task failed. Error: ..."). The "Task " prefixes come from
  L52: # ``task_tool.py``'s 5 normal-return strings; the bare ``Error:`` prefix
  L53: # catches both the 3 ``Error:`` pre-execution returns and the wrapper
  L54: # produced by ``ToolErrorHandlingMiddleware`` for any task tool exception.
  L66: """Infer the structured status for a ``task`` tool result string.
  L73: """
  L86: """Build the ``additional_kwargs`` payload the middleware stamps.
  L96: """

## 10c1d9f4 2026-06-08 Nan Gao
fix(search): fix DDGS Wikipedia region handling (#3423)

- `backend/packages/harness/deerflow/community/ddg_search/tools.py`
  L50: """Pick a valid Wikipedia language region when DDGS' worldwide region is used."""
  L69: """
  L72: """
  L150: # Override tool call defaults from config if set.

## f725a963 2026-06-08 Nan Gao
fix(runtime): protect sync singleton init and reset (#3413)

* fix(runtime): protect sync singleton init/reset with threading.Lock

* fix(runtime): serialize sync singleton init and reset

* make format

* test(runtime): assert store reset creates new singleton

* Apply suggestions from code review

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* fix(runtime): load config outside singleton locks

* fix(runtime): share checkpointer config loading helper

---------

Co-authored-by: GODDiao <diaoshengjia@gmail.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/config/checkpointer_config.py`
  L45: """Lazily load app config when checkpointer config has not been initialized."""
- `backend/packages/harness/deerflow/runtime/checkpointer/provider.py`
  L121: # Config loading can reset both persistence singletons. Keep it outside
  L122: # this provider lock to avoid cross-provider lock-order inversion.
- `backend/packages/harness/deerflow/runtime/store/provider.py`
  L123: # Config loading can reset both persistence singletons. Keep it outside
  L124: # this provider lock to avoid cross-provider lock-order inversion.

## 51920072 2026-06-08 Willem Jiang
fix(middleware): offload memory injection off event loop to prevent tiktoken blocking (#3402) (#3411)

* fix(middleware): offload memory injection off event loop to prevent tiktoken blocking (#3402)

  DynamicContextMiddleware.abefore_agent() called _inject() synchronously
  on the asyncio event loop.  The first time memory is injected (second
  request), _inject() → format_memory_for_injection() → _count_tokens()
  → tiktoken.get_encoding("cl100k_base") needs to download the BPE data
  from openaipublic.blob.core.windows.net.  In network-restricted
  environments this download blocks until the OS TCP timeout (~26 min),
  starving ALL concurrent handlers including /api/v1/auth/me.

  Fix:
  - abefore_agent now uses asyncio.to_thread(self._inject, state) so
    file I/O and tiktoken never block the event loop.
  - Extract _get_tiktoken_encoding() with a module-level cache so
    tiktoken.get_encoding() is called at most once per encoding name.
  - Add warm_tiktoken_cache() startup helper; gateway lifespan pre-warms
    the cache via asyncio.to_thread so the first request never triggers a
    cold download.
  - _count_tokens falls back to len(text) // 4 on any encoding failure.

  Tests:
  - tests/test_tiktoken_cache_and_count_tokens.py (12 tests): cache
    hit/miss, fallback paths, warm-up helper.
  - tests/blocking_io/test_dynamic_context_middleware.py (2 tests):
    Blockbuster gate verifies abefore_agent does not block the event
    loop; async/sync parity check.

  Fixes #3402

* Apply suggestions from code review

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* fix the lint error

* fix(memory): use future annotations to avoid NameError when tiktoken is absent

Add `from __future__ import annotations` to prompt.py so that
tiktoken.Encoding type hints are never evaluated at runtime.  Without
this, environments where tiktoken is not installed could raise NameError
on the module-level cache and function return annotations.

Addresses Copilot review comment on PR #3411.

* fix(middleware): bound abefore_agent injection with timeout to prevent hung requests

Wrap the asyncio.to_thread(self._inject) offload in asyncio.wait_for()
with a 5-second cap.  If the startup warm-up failed silently (e.g.
network blip during deploy), a cold tiktoken BPE download on the first
request can block until the OS TCP timeout (~26 min).  The bounded
timeout ensures the request degrades gracefully (no memory/date context
for that turn) rather than hanging.

Adds test_abefore_agent_returns_none_on_timeout to the blocking-IO
regression anchors.

Addresses review feedback from xg-gh-25 on PR #3411.

---------

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/agents/memory/prompt.py`
  L168: # Module-level tiktoken encoding cache.  Populated lazily on first use;
  L169: # subsequent calls are a dict lookup (no network I/O).  Pre-warming at
  L170: # startup via :func:`warm_tiktoken_cache` avoids blocking a request on the
  L171: # (potentially slow) first ``get_encoding`` call.
  L176: """Return a cached tiktoken encoding, or ``None`` on failure / unavailability.
  L184: """
  L214: # or the encoding failed to load.
  L225: """Pre-warm the tiktoken encoding cache.
  L231: """
- `backend/packages/harness/deerflow/agents/middlewares/dynamic_context_middleware.py`
  L47: # Upper bound (seconds) for a single _inject() offload.  If the warm-up at
  L48: # gateway startup failed silently, the first request may still hit a cold
  L49: # tiktoken BPE download that blocks until the OS TCP timeout (~26 min).
  L50: # This cap ensures the request degrades gracefully instead of hanging.
  L211: # _inject() performs synchronous file I/O (memory JSON loading) and
  L212: # potentially blocking network calls (tiktoken encoding download on
  L213: # first use).  Offload to a thread so the event loop is never blocked
  L214: # — a blocking call here starves all concurrent HTTP handlers (auth,
  L215: # SSE heartbeats, etc.).  See issue #3402.
  L216: #
  L217: # Bounded timeout: if startup warm-up failed silently (e.g. network
  L218: # blip during deploy), the first request's cold tiktoken download can
  L219: # block for tens of minutes (OS TCP timeout).  Time-box injection so
  L220: # the request degrades gracefully (no memory context) rather than
  L221: # hanging.

## 64d923b0 2026-06-08 Huixin615
fix(middleware): externalize oversized tool output into sandbox for non-mounted sandboxes (#3417)

* fix(middleware): externalize oversized tool output into sandbox for non-mounted sandboxes

ToolOutputBudgetMiddleware persisted oversized tool results to the host
filesystem and returned a /mnt/user-data/outputs virtual path. For sandboxes
that do not use thread-data mounts (e.g. remote AIO sandbox), that virtual
path does not exist inside the sandbox, so the model's read_file tool could
not read it back and reported 'file not found'.

Branch on SandboxProvider.uses_thread_data_mounts:

- Mounted sandboxes (local Docker, AIO + LocalContainerBackend) keep the
  original host-disk path; the host outputs dir is bind-mounted to the same
  virtual path inside the sandbox, so behavior is unchanged.

- Non-mounted (remote) sandboxes externalize into the sandbox itself via
  execute_command('mkdir -p ...') + write_file + 'test -s' validation. The
  validation step is required because AIO sandbox execute_command returns
  'Error: ...' as a string on failure instead of raising, so a silent mkdir
  failure would otherwise leak through.

Any failure (rejected subdir, mkdir/write/validate error) falls back to the
existing inline head+tail truncation, so an unreadable path is never returned
to the model.

The sandbox resolver reads the sandbox_id that SandboxMiddleware already
writes into runtime.state['sandbox']; it never calls provider.acquire(),
keeping the tool-call hot path free of blocking I/O. Tools that do not use a
sandbox (web_search, MCP, ...) resolve to None and fall through to inline
truncation, which is the safe behavior for them.

Fixes #3416

* fix(middleware): address Copilot review feedback on sandbox externalization

- Make get_sandbox_provider() lookup best-effort in _budget_content: only
  query when outputs_path or sandbox is available, and fall back to inline
  truncation if provider initialization raises rather than propagating
  the error. A resolved sandbox instance is sufficient on its own to take
  the non-mounted externalization branch.
- Strict-match the sandbox post-write validation echo
  (check.strip() == 'OK') to avoid false positives if execute_command
  ever surfaces unrelated stdout/stderr containing 'OK' as a substring.

Refs: #3417

* test: fix flaky tests relying on /nonexistent/... path under container root

Two tests in this module (test_returns_none_on_invalid_path and
test_fallback_when_disk_write_fails) used paths like
'/nonexistent/impossible/path' to trigger _externalize's OSError
fallback. These paths are creatable when the test process runs as root
inside the CI container: os.makedirs(..., exist_ok=True) successfully
creates the entire chain under /, so the OSError branch is never hit
and the tests fail. Reproducible on main independently of this PR.

Switch to '/dev/null/cannot-mkdir-here'. /dev/null is a character
device on both Linux and macOS, so os.makedirs always fails with
NotADirectoryError regardless of privileges, reliably exercising the
OSError fallback.

* fix(tool-output-budget): only consult sandbox provider when a sandbox is resolved

The previous revision called get_sandbox_provider() whenever externalization
was triggered, including on the legacy host-disk path. Environments without
a configured sandbox -- in particular CI runners without a config.yaml --
would raise FileNotFoundError there, get caught, and silently fall back to
inline truncation. That defeated the host-disk externalization path that
predates this PR and was the root cause of the regressing legacy tests.

Restructure the branching so the provider is only consulted when a sandbox
has actually been resolved for the current tool call:

  - sandbox resolved + provider.uses_thread_data_mounts: host-disk write
    (bind-mounted into the sandbox, equivalent to a sandbox-side write).
  - sandbox resolved + non-mounted provider:             sandbox write (#3416).
  - no sandbox + outputs_path:                           host-disk write
    (legacy / non-sandbox tools, no provider call at all).
  - otherwise:                                           inline fallback.

No test changes; the legacy externalization tests are provider-agnostic by
construction and now pass without monkeypatching.

Refs: #3416

* test(tool-output-budget): assert legacy path does not call sandbox provider

Lock in the contract introduced by d6e2d25b: when no sandbox is resolved
for a tool call, _budget_content must externalize to the host outputs
directory without consulting get_sandbox_provider(). Regressing this would
re-break legacy / non-sandbox tools in environments without a configured
sandbox (e.g. CI without config.yaml), which is the failure mode #3416's
fix avoids.

The test injects a get_sandbox_provider that raises on call, so any
future refactor that moves the provider lookup out of the sandbox-only
branch will fail loudly.

Refs: #3416

- `backend/packages/harness/deerflow/agents/middlewares/tool_output_budget_middleware.py`
  L35: # Virtual outputs root inside the sandbox. Host-mounted sandboxes map this to
  L36: # the thread outputs dir on the host; for non-mounted (remote) sandboxes the
  L37: # same path is written directly into the sandbox filesystem so the model's
  L38: # ``read_file`` tool can read it back (issue #3416).
  L109: """Build the on-disk filename for an externalized tool output.
  L113: """
  L160: """Write *content* into the sandbox filesystem and return the virtual path.
  L167: """
  L174: # AIO sandbox write_file does NOT create parent directories, so create
  L175: # them explicitly before writing. execute_command returns its stdout
  L176: # verbatim (including an "Error: ..." string on failure) rather than
  L177: # raising, so we cannot rely on exception propagation here.
  L180: # Validate the file landed: execute_command may have silently failed
  L181: # to create the directory, and write_file backends differ. Refuse to
  L182: # hand the model an unreadable read_file path.
  L299: """Resolve the active sandbox for the current tool call, or ``None``.
  L307: """
  L343: # Decide persistence target based on what's available, without touching
  L344: # the sandbox provider unless a sandbox was actually resolved for this
  L345: # call. This keeps the legacy host-disk path provider-free, so callers
  ... (truncated)

## cd5bedaa 2026-06-08 DanielWalnut
feat: MiniMax provider for image/video/podcast skills + new music-generation skill (#3437)

* docs(spec): MiniMax integration for generation skills + new music skill

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* docs(plan): MiniMax generation providers implementation plan

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* test(skills): add importlib loader + FakeResp for skill tests

* test(skills): register loaded module in sys.modules; raise requests.HTTPError in FakeResp

* feat(image-generation): add MiniMax provider with env auto-detect

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* refactor(image-generation): guard unknown provider, derive ref MIME, strengthen tests

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* feat(video-generation): add MiniMax provider with async poll/download

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* refactor(video-generation): surface base_resp errors while polling; add timeout test

* feat(podcast-generation): add MiniMax t2a_v2 provider with env auto-detect

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* refactor(podcast-generation): restore TTS credential guard; add volcengine + voice tests

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(music-generation): new MiniMax music skill via skill-creator

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* refactor(music-generation): treat empty lyrics as absent; test no-audio-data path

* refactor(skills): add request timeouts to MiniMax network calls

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* Potential fix for pull request finding 'Explicit returns mixed with implicit (fall through) returns'

Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>

* fix(models): strip inconsistent user-message names for MiniMax chat

DeerFlow middlewares tag user messages with provenance names (user-input, summary, loop_warning); langchain serializes them into the OpenAI-compatible payload and MiniMax rejects mismatched user-message names with "user name must be consistent (2013)". PatchedChatMiniMax now drops the per-message name from user-role messages. Point the config.example MiniMax models at PatchedChatMiniMax so they also get reasoning_content mapping.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* feat(image-generation): MiniMax sends JSON prompt field, guard 1500-char limit

MiniMax image-01 takes one text string capped at 1500 chars, but the skill was sending the whole structured JSON. The MiniMax provider now extracts the JSON `prompt` field (relying on prompt_optimizer to expand it) and fails fast with a clear error before calling the API when that field exceeds 1500 chars. Authoring stays provider-agnostic; Gemini still receives the full JSON.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* feat(podcast-generation): per-provider TTS concurrency and retry/backoff

Each TTS provider owns its concurrency internally — MiniMax runs single-threaded to reduce rate-limit failures, Volcengine keeps 4 workers — with automatic retry and backoff on transient HTTP and base_resp errors. No caller-facing concurrency knob.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* fix(skills): address Copilot review comments on generation skills

- video: add raise_for_status + timeout to the Gemini download/POST/poll calls so non-2xx responses surface as clear HTTP errors instead of JSON/KeyError or hangs
- video: check the task Fail status before the generic base_resp check so the failure keeps its task_id context
- video/image: create the output file parent directory before writing (matching music-generation) so nested output paths do not raise FileNotFoundError
- music: require a non-empty prompt and fail fast with ValueError instead of sending an empty prompt to the API

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* fix(scripts): reclaim dev ports across worktrees in make stop/dev

All deer-flow worktrees (main checkout + linked worktrees) hardcode the same dev ports (8001/3000/2026), so a service started from any worktree must be reclaimable from another. stop_all now resolves the set of worktree roots (DEERFLOW_ROOTS) and treats a process as deer-flow-owned when its open files live under any of them. It also force-kills survivors on 2026 alongside 8001/3000, fixing `make dev` aborting on the nginx port preflight when a prior nginx lingered on 2026.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* fix(view-image): hide the injected image-context message from the UI

ViewImageMiddleware injects a HumanMessage (text + base64 images) so the vision model can see viewed images, but it was the only internal injector that set neither hide_from_ui nor a hidden name, so it leaked into the chat UI (and IM channels) as a user bubble reading "Here are the images you've viewed:". Mark it with additional_kwargs={"hide_from_ui": True}, matching todo/dynamic_context injections, which the frontend isHiddenFromUIMessage and the channel sender already honor. The model still receives the full content.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* fix(minimax): mark M2.7 models as text-only (no vision)

MiniMax M2.7 / M2.7-highspeed do not support vision; only M3 does. The
provider config asserted vision support for M2.7 in four places.

- config.example.yaml: 4 M2.7 entries -> supports_vision: false
- backend/docs/CONFIGURATION.md: M2.7 + highspeed -> supports_vision: false
- wizard: add LLMProvider.model_vision_overrides + extra_config_for() so
  selecting an M2.7 model writes supports_vision: false while M3 (default)
  keeps vision; wire it through setup_wizard.py
- tests: M2.7-highspeed fixture -> supports_vision=False; add
  test_minimax_vision_is_per_model

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>

- `backend/packages/harness/deerflow/agents/middlewares/view_image_middleware.py`
  L182: # Create a new human message with mixed content (text + images). This is
  L183: # internal context for the model only, so hide it from the chat UI and IM
  L184: # channels (matches the other middleware-injected context messages).
- `backend/packages/harness/deerflow/models/patched_minimax.py`
  L122: """Drop the per-message ``name`` field from user-role messages.
  L130: """

## 3b6dd0a4 2026-06-08 AochenShen99
feat(subagents): extend deferred MCP tool loading to subagents (#3432)

* feat(subagents): extend deferred MCP tool loading to subagents (#3341)

Subagents now reuse the lead agent's deferred-tool path: when
tool_search.enabled, MCP tool schemas are withheld from the model and
surfaced by name in <available-deferred-tools>, fetched on demand via the
generated tool_search helper. DeferredToolFilterMiddleware deterministically
rewrites request.tools to hide the deferred schemas (the prompt section is
discovery only, not enforcement).

Consolidates the assembly into deerflow.tools.builtins.tool_search, now the
single home for both assemble_deferred_tools (centralized fail-closed guard,
replacing the lead-only private _assemble_deferred) and the relocated
get_deferred_tools_prompt_section. Shared by every build path: lead agent,
embedded client, and subagent executor.

tool_search is appended after the subagent's name-level tool policy and is
treated as infrastructure: its catalog is built from the already
policy-filtered list, so it can never surface a tool the policy denied.

Follow-up to #3370. Fixes #3341.

* test(subagents): assert the real middleware builder emits a working deferred filter (#3341)

The existing recipe test hand-constructs DeferredToolFilterMiddleware, so it
cannot catch a regression in how build_subagent_runtime_middlewares (the call
executor._create_agent actually makes) wires the deferred setup into the
filter. Add a test that sources the filter from the real builder given a real
setup and runs it through a graph: a wrong catalog hash would silently stop
promotion, a dropped filter would stop hiding — both now caught.

Running the full real middleware stack is intentionally avoided (the other
runtime middlewares need sandbox/thread infra to execute, which would make the
test flaky); their attachment + ordering before Safety stays locked in
test_tool_error_handling_middleware.py.

* test(subagents): keep executor tests config-free in CI

* chore: trigger ci

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
- `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`
- `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py`
  L229: # Hide deferred (MCP) tool schemas from the subagent's model binding until
  L230: # tool_search promotes them. This is the same wiring the lead agent gets. The deferred
  L231: # set + catalog hash come from the build-time setup (assembled after
  L232: # tool-policy filtering); promotion is read from graph state. Empty/None
  L233: # setup (deferral disabled or no MCP tool survived) is a pure no-op.
- `backend/packages/harness/deerflow/client.py`
- `backend/packages/harness/deerflow/subagents/executor.py`
  L32: # Imported lazily at runtime inside _build_initial_state: importing
  L33: # tool_search eagerly would run tools/builtins/__init__ -> task_tool ->
  L34: # `from deerflow.subagents import SubagentExecutor`, which re-enters this
  L35: # still-initializing package. Type-only here keeps the annotation precise.
  L330: """Create the agent instance.
  L335: """
  L431: # Lazy import: see the TYPE_CHECKING note at the top of this module -
  L432: # importing tool_search runs tools/builtins/__init__, which would
  L433: # re-enter this package during its own initialization.
  L439: # Assemble deferred tool_search AFTER policy filtering (fail-closed),
  L440: # mirroring the lead path so subagents stop binding full MCP schemas.
  L441: # The generated tool_search helper is intentionally not subject to the
  L442: # subagent's name-level allow/deny (config.tools / disallowed_tools):
  L443: # its catalog is built from the already-filtered list, so it can never
  L444: # surface a tool the policy denied. This matches the lead agent.
  L457: # Name the deferred MCP tools in the prompt; their schemas stay withheld
  L458: # until tool_search promotes them. Empty set -> "" -> appends nothing.
- `backend/packages/harness/deerflow/tools/builtins/tool_search.py`
  L185: """Build the final tool list + deferred setup from a POLICY-FILTERED list.
  L194: """
  L204: # Prompt rendering
  L208: """Generate <available-deferred-tools> from an explicit deferred-name set.
  L217: """

## f92a26d5 2026-06-08 Ryker_Feng
fix(web_fetch): support proxy for Jina reader in restricted networks (#3418) (#3430)

* fix(web_fetch): support proxy for Jina reader in restricted networks

The web_fetch tool built a bare httpx.AsyncClient() with no proxy
awareness, so users behind a corporate proxy / in Docker / WSL could
not reach https://r.jina.ai and web_fetch timed out.

- Add optional `proxy` / `trust_env` params to JinaClient.crawl and
  wire them from the `web_fetch` tool config (with type coercion for
  YAML string values).
- Pass internal service hostnames through NO_PROXY in both compose
  files so proxy env inherited via env_file does not break in-cluster
  calls (gateway/provisioner/etc).
- Load proxy vars from .env into the shell in scripts/docker.sh so the
  NO_PROXY interpolation can merge user-provided values on `make` path.
- Document proxy/trust_env options in config.example.yaml.

Closes #3418

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/community/jina_ai/jina_client.py`
- `backend/packages/harness/deerflow/community/jina_ai/tools.py`

## 0fb18e36 2026-06-09 AochenShen99
refactor(lead-agent): make build_middlewares public to drop the last cross-module private import (#3458)

`client.py` imported the private `_build_middlewares` from `agent.py` across a
module boundary and called it as public API. Because the `_` name signals
"module-private, no external callers", any future rename or signature change
silently breaks the embedded `DeerFlowClient` path — and the test suite even
monkeypatched `deerflow.client._build_middlewares`, baking the leak in.

`DeerFlowClient` is a lead-agent variant that genuinely needs the lead agent's
full middleware composition, so make the dependency honest: promote the helper
to a documented public entry point `build_middlewares` and update every in-repo
caller. Found during #3341 review; #3341 already removed one such leak
(`_assemble_deferred` -> public `assemble_deferred_tools`) and left this one out
of scope on purpose.

- agent.py: rename def + both internal call sites; expand the docstring into a
  public-entry-point contract and document the previously-undocumented
  model_name / app_config / deferred_setup params
- client.py: import + call site now use the public name (removes the last
  cross-module private import)
- scripts/tool-error-degradation-detection.sh: update its import + call site
- tests (5 files): update monkeypatch/patch targets and direct calls
- docs (backend/CLAUDE.md, plan_mode_usage.md, middlewares.mdx): sync the live
  references that describe the symbol as current API

Pure mechanical rename, no behavior change. Historical design docs (rfc,
superpowers spec) intentionally keep the old name as point-in-time records.

Closes #3431

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
  L277: """Build the lead-agent middleware chain based on runtime configuration.
- `backend/packages/harness/deerflow/client.py`

## 8db16bb3 2026-06-09 ly-wang19
fix(config): coerce null config.yaml list sections to empty list (#3434)

Copying config.example.yaml to config.yaml and starting DeerFlow crashed with `pydantic ValidationError: models — Input should be a valid list [input_value=None]`, because the example ships every entry under `models:` commented out, so PyYAML parses the key as null. Reported in #1444.

Add a field_validator(mode="before") on AppConfig that coerces null models/tools/tool_groups to [] (matching their default_factory=list), and emit an actionable warning from from_file when no models are configured (pointing to config.example.yaml / make setup). Adds regression tests.

Closes #1444

Co-authored-by: ly-wang19 <ly-wang19@users.noreply.github.com>
Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/config/app_config.py`
  L154: """Treat a present-but-empty config section as an empty list.
  L163: """

## 37337b77 2026-06-09 hataa
feat(models): add StepFun reasoning model adapter (#3461)

Add PatchedChatStepFun adapter for StepFun reasoning models (step-3.7-flash,
step-3.5-flash). Captures reasoning from both streaming and non-streaming
responses and replays it on historical assistant messages for multi-turn
tool-call conversations.

- New: PatchedChatStepFun adapter with streaming/non-streaming reasoning capture
- Support both reasoning and reasoning_content field names
- 17 unit tests covering all response paths
- Updated: config.example.yaml with StepFun configuration example

- `backend/packages/harness/deerflow/models/patched_stepfun.py`
  L1: """Patched ChatOpenAI adapter for StepFun reasoning models.
  L29: """Return reasoning content from a dict/Pydantic object.
  L33: """
  L35: # Check reasoning_content first (deepseek-style), then reasoning (default)
  L41: # Pydantic / SDK object attributes
  L47: # Some SDK versions store extra fields in model_extra
  L58: """Return a copy of *message* with reasoning_content stored in additional_kwargs."""
  L66: """Extract the SDK-typed choice message at *index*, if available."""
  L77: """ChatOpenAI with full reasoning support for StepFun models.
  L82: """
  L92: # --- Request payload replay ---
  L101: """Restore ``reasoning_content`` on historical assistant messages."""
  L113: # --- Streaming reasoning capture ---
  L121: """Capture ``reasoning`` / ``reasoning_content`` from streaming deltas."""
  L142: # --- Non-streaming reasoning capture ---
  L149: """Extract ``reasoning`` / ``reasoning_content`` from non-streaming responses."""

## 16391e35 2026-06-09 DanielWalnut
fix(skills): harden slash skill activation across chat channels (#3466)

* support slash skill activation

* format slash skill activation

* Preserve slash skill activation with uploads

* Address slash skill review feedback

* Address slash skill follow-up review

* Fix lazy slash skill storage resolution

* Keep slash skill activation out of system prompt

* Address slash skill review issues

* fix: harden slash skill command handling

* feat(frontend): add slash skill autocomplete

* fix: address slash skill review feedback

* fix: preserve slash skill text for IM uploads

- `backend/packages/harness/deerflow/agents/lead_agent/agent.py`
  L308: # Deterministically load a full SKILL.md when the user starts the turn with
  L309: # /skill-name. This keeps the base system prompt metadata-only while giving
  L310: # explicit user activation priority over model-side relevance guessing.
  L488: # Keep the bootstrap skill set intentionally narrow so agent creation
  L489: # remains deterministic before the custom agent's own config exists.
- `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`
- `backend/packages/harness/deerflow/agents/middlewares/skill_activation_middleware.py`
  L1: """Middleware for explicit slash skill activation."""
  L52: """Return whether a message is hidden slash-skill activation context."""
  L67: """Inject full SKILL.md content when the user explicitly types /skill-name."""
- `backend/packages/harness/deerflow/agents/middlewares/uploads_middleware.py`
- `backend/packages/harness/deerflow/client.py`
- `backend/packages/harness/deerflow/skills/slash.py`
  L14: """Parsed slash-skill command with the skill name and remaining task text."""
  L22: """Slash-skill activation resolved against enabled runtime-visible skills."""
  L30: """Parse strict `/skill-name task` syntax, ignoring reserved control commands."""
  L50: """Resolve text into an enabled, whitelisted skill activation if possible."""
- `backend/packages/harness/deerflow/utils/messages.py`
  L10: """Extract text from LangChain message content shapes."""
  L27: """Return pre-middleware user text when available, otherwise content text."""

## ae9e8bc0 2026-06-09 Lucy Shen
fix(sandbox): make missing sandbox.mounts host_path a loud ERROR (#3244) (#3250)

In Docker production deployments, LocalSandboxProvider runs inside the
deer-flow-gateway container, so any `sandbox.mounts[].host_path` from
config.yaml is resolved against the gateway container's filesystem — not
the host machine. When the path isn't also bind-mounted into the gateway
service, the mount was silently dropped with only a WARNING log, leaving
agents reading an empty directory in production while the same config
worked under `make dev`.

Escalate the missing-host_path branch to logger.error with explicit
guidance about Docker bind mounts and docker-compose, so the failure is
hard to miss in default log configurations. Skip behaviour is preserved
to avoid breaking existing deployments.

Also clarify the misleading `VolumeMountConfig.host_path` field
description so it documents reality for both providers:

  - LocalSandboxProvider checks host_path from inside the gateway process
    (host in `make dev`, container in `make up`).
  - AioSandboxProvider (DooD) passes host_path straight to `docker -v`
    for the sandbox container, where the host Docker daemon resolves it
    from the host machine's perspective.

config.example.yaml's `sandbox.mounts` comment gets a Note: block
pointing operators at the docker-compose bind-mount requirement so the
Docker-mode gotcha is discoverable from the canonical template.

Adds a regression test that:
  - confirms missing host_path is still skipped (no behaviour break);
  - asserts an ERROR record is emitted referencing the offending paths;
  - asserts the message contains actionable Docker/gateway/docker-compose
    keywords so future refactors can't quietly downgrade it.

Refs: https://github.com/bytedance/deer-flow/issues/3244

- `backend/packages/harness/deerflow/config/sandbox_config.py`
- `backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`
  L150: # Ensure the host path exists before adding mapping.
  L151: #
  L152: # ``host_path`` is resolved against the filesystem of the
  L153: # process running this provider — for ``make dev`` that is
  L154: # the host machine, but for ``make up`` it is the
  L155: # ``deer-flow-gateway`` container, so any host path that
  L156: # isn't bind-mounted into the gateway image will be missing
  L157: # here. Skipping silently makes this a high-cost-to-debug
  L158: # silent failure (sandbox skill / tool reads an empty dir
  L159: # instead of the configured mount), so escalate to ERROR
  L160: # and include actionable guidance. See #3244.

## a57d05fe 2026-06-10 Nan Gao
fix runtime journal run lifecycle events (#3470)

- `backend/packages/harness/deerflow/runtime/journal.py`
  L175: # Nested chain ends fire for internal graph nodes; only the root chain
  L176: # represents the user-visible run lifecycle.

## 167ef451 2026-06-10 Ryker_Feng
feat(memory): add memory.token_counting config to avoid tiktoken network dependency (#3429) (#3465)

* feat(memory): add memory.token_counting config to avoid tiktoken network dependency (#3429)

Add a `memory.token_counting` option (`tiktoken` | `char`) so deployments in
network-restricted environments can opt out of tiktoken entirely. In `char`
mode the memory-injection budget uses a network-free character-based estimate
and never triggers the BPE download from openaipublic.blob.core.windows.net,
which could otherwise block for tens of minutes (see #3402).

Also harden the default `tiktoken` path:
- cache an in-flight LOADING sentinel so concurrent callers fall back
  immediately instead of spawning more blocking get_encoding threads when the
  first load is still running (e.g. under the 5s startup warm-up timeout);
- cache failures with a timestamp and retry after a cooldown so a transient
  network outage self-heals back to accurate counting without a restart;
- skip startup warm-up entirely in char mode.

The new config is surfaced via the memory config API and config.example.yaml
(config_version bumped). Default remains `tiktoken`, so existing deployments
are unaffected.

* fix(memory): use CJK-aware char token estimate and address review feedback

- Replace the flat len(text)//4 fallback with a CJK-aware estimate so
  Chinese/Japanese/Korean memory content does not over-fill the injection budget
- Document the internal tiktoken retry cooldown and char-mode escape hatch
- Sync CLAUDE.md / config.example.yaml / MEMORY_IMPROVEMENTS.md wording
- Fix MemoryConfigResponse mocks/assertions and add CJK estimate tests

- `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`
- `backend/packages/harness/deerflow/agents/memory/prompt.py`
  L174: #
  L175: # A *failed* load is cached as a ``(None, monotonic_timestamp)`` tuple so that
  L176: # a network-restricted environment does not re-attempt the blocking BPE
  L177: # download on every subsequent call.  After ``_TIKTOKEN_RETRY_COOLDOWN_S`` the
  L178: # failure is allowed to expire so a transient network outage can self-heal back
  L179: # to accurate tiktoken counting without a process restart.  A load already in
  L180: # progress is cached as ``_TIKTOKEN_ENCODING_LOADING`` so concurrent callers
  L181: # fall back immediately instead of spawning more blocking
  L182: # ``tiktoken.get_encoding`` threads.  Use the ``memory.token_counting: char``
  L183: # config to skip tiktoken entirely.
  L186: # Cooldown before a *failed* tiktoken load is re-attempted. This is an internal
  L187: # tuning constant rather than a user-facing config: it only affects how quickly
  L188: # the default ``tiktoken`` mode self-heals after a transient network outage.
  L189: # Deployments that want to avoid tiktoken's network dependency entirely should
  L190: # set ``memory.token_counting: char`` instead of tuning this value.
  L221: # Cached failure: (None, failed_at). Retry only after cooldown.
  L244: """Network-free token estimate that accounts for CJK density.
  L252: """
  L281: # Fallback to CJK-aware character estimation if tiktoken is not
  L282: # available or the encoding failed to load.
  ... (truncated)
- `backend/packages/harness/deerflow/client.py`
- `backend/packages/harness/deerflow/config/memory_config.py`

## b3c2cc42 2026-06-10 hataa
fix(agents): require config.yaml in resolve_agent_dir to skip memory-only directories (#3390) (#3481)

When memory is enabled, the first conversation with a legacy shared agent
creates a per-user agent directory containing only memory.json (no
config.yaml). On the second turn, resolve_agent_dir() returned this
incomplete directory, causing load_agent_config() to fail with
"Agent config not found".

Require config.yaml to exist alongside the directory for both the
per-user and legacy paths, so that memory-only directories fall
through correctly. This aligns resolve_agent_dir with the existing
config.yaml check in list_custom_agents.

Refs: https://github.com/bytedance/deer-flow/issues/3390

- `backend/packages/harness/deerflow/config/agents_config.py`
  L70: # Require config.yaml to confirm this is a genuine agent directory,
  L71: # not a leftover from memory/storage writes (see #3390).

## 919d8bc2 2026-06-11 Huixin615
fix(sandbox): persist lazily-acquired sandbox state via Command (#3464)

* fix(sandbox): persist lazily-acquired sandbox state via Command

ensure_sandbox_initialized mutates runtime.state in place, which is local
to the current tool invocation and is not picked up by LangGraph's channel
reducer. Subsequent graph steps and downstream consumers (such as
ToolOutputBudgetMiddleware and the sub-agent task_tool) therefore cannot
observe the sandbox id from state.

Wrap tool calls in SandboxMiddleware (wrap_tool_call / awrap_tool_call) to
detect fresh lazy initialization by diffing runtime.state before and after
the handler, and emit a proper state update via Command(update=...):

- ToolMessage results are wrapped into Command(update={sandbox, messages})
- Command results with a dict update are merged on the sandbox key while
  preserving messages / goto / graph / resume
- Command results with non-dict updates are left untouched to avoid silent
  data loss on unknown update shapes

Tests:
- 7 new unit tests cover lazy-init emit, passthrough, dict-update merge,
  non-dict-update passthrough (sync and async)
- Refresh replay golden write_read_file.ultra.events.json: SSE 'values'
  events now correctly carry the 'sandbox' key in their keys list, which
  is the direct evidence that the fix is effective

Closes #3463

* refactor(sandbox): use dataclasses.replace to preserve Command fields

Address Copilot review on #3464: replace manual field-copy with
dataclasses.replace so any current or future Command fields are
preserved automatically when merging sandbox_update.

Also add a regression test that constructs a Command with non-None
graph/goto/resume to lock this behavior in.

- `backend/packages/harness/deerflow/sandbox/middleware.py`
  L135: # ------------------------------------------------------------------
  L136: # Tool-call wrappers: persist lazily-acquired sandbox state into the
  L137: # graph state via Command(update=...).
  L138: #
  L139: # Background:
  L140: #   ``ensure_sandbox_initialized*`` in ``deerflow.sandbox.tools`` mutates
  L141: #   ``runtime.state["sandbox"]`` directly. That mutation is local to the
  L142: #   current tool invocation and is NOT picked up by LangGraph's channel
  L143: #   reducer, so subsequent graph steps (and downstream consumers such as
  L144: #   ``ToolOutputBudgetMiddleware`` and the sub-agent ``task_tool``)
  L145: #   cannot observe the sandbox id. Wrapping the tool call lets us detect
  L146: #   a fresh lazy init by diffing the state snapshot before/after the
  L147: #   handler and emit a proper state update via ``Command``.
  L148: # ------------------------------------------------------------------
  L162: """Wrap or merge ``result`` so that ``sandbox.sandbox_id`` is persisted.
  L169: """
  L183: """Read sandbox_id from runtime.state (where ensure_sandbox_initialized writes)."""

## f401e7ba 2026-06-11 DanielWalnut
[codex] Fix stale AIO sandbox cache reuse (#3494)

* Fix stale AIO sandbox cache reuse

* Address AIO sandbox review feedback

* Distinguish sandbox health check failures

* Keep local discovery recoverable when the runtime check fails

LocalContainerBackend.discover() shares _is_container_running, which now
raises on transient daemon errors instead of returning False. Discovery has
no exception handling in _discover_or_create_with_lock(_async), so a brief
Docker hiccup turned a recoverable "could not verify, create instead" into a
hard acquire failure. Catch the check failure inside discover() and return
None so an unverifiable container is simply not adopted, restoring the
pre-change fall-through while keeping raise-on-unknown semantics protecting
the destroy path.

Reported by fancy-agent on PR #3494.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

* Narrow the not-found match in container inspect error handling

A bare "not found" substring also matches transient failures like "command
not found" or "context not found", which would misclassify a check error as
"container definitely gone" and bypass the raise-on-unknown contract. Keep
Docker's specific "No such object"/"No such container" phrases, and only
trust a generic "not found" (Apple Container) when the message names the
inspected container or refers to a container/object.

Reported by WillemJiang on PR #3494.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>

---------

Co-authored-by: Claude Fable 5 <noreply@anthropic.com>

- `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`
  L564: """Return whether a tracked sandbox appears alive, or None if unknown."""
  L577: """Remove a sandbox from in-process tracking maps.
  L583: """
  L607: """Remove and destroy a sandbox after a definitive failed health check."""
- `backend/packages/harness/deerflow/community/aio_sandbox/local_backend.py`
  L173: """Return True only when stderr definitively says the container does not exist.
  L181: """
- `backend/packages/harness/deerflow/community/aio_sandbox/remote_backend.py`

