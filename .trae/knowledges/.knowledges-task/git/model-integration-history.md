## c99865f5 2026-04-19 Admire
fix(token-usage): enable stream usage for openai-compatible models (#2217)

* fix(token-usage): enable stream usage for openai-compatible models

* fix(token-usage): narrow stream_usage default to ChatOpenAI

- `backend/packages/harness/deerflow/models/factory.py`
  L34: """Enable stream usage for OpenAI-compatible models unless explicitly configured.
  L40: """

## 2bb1a2df 2026-04-25 pyp0327
feat(models): Provider for MindIE model engine (#2483)

* feat(models): 适配 MindIE引擎的模型

* test: add unit tests for MindIEChatModel adapter and fix PR review comments

* chore: update uv.lock with pytest-asyncio

* build: add pytest-asyncio to test dependencies

* fix: address PR review comments (lazy import, cache clients, safe newline escape, strict xml regex)

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/models/factory.py`
  L134: # For MindIE models: enforce conservative retry defaults.
  L135: # Timeout normalization is handled inside MindIEChatModel itself.
  L137: # Enforce max_retries constraint to prevent cascading timeouts.
- `backend/packages/harness/deerflow/models/mindie_provider.py`
  L14: """Sanitize incoming messages for MindIE compatibility.
  L20: """
  L23: # Flatten content if it's a list of blocks
  L35: # Convert AIMessage with tool_calls to raw XML text format
  L45: # Wrap tool execution results in XML tags and convert to HumanMessage
  L51: # Fallback to prevent completely empty message content
  L61: """Parse XML-style tool calls from model output into LangChain dicts.
  L69: """
  L91: # Attempt to deserialize string values into native Python types
  L92: # to satisfy downstream Pydantic validation.
  L112: """Iterate `<tool_call>...</tool_call>` blocks and tolerate nesting."""
  L138: """Decode literal `\\n` outside fenced code blocks."""
  L151: """Chat model adapter for MindIE engine.
  L159: """
  L162: """Normalize timeout kwargs without creating long-lived clients."""
  L180: """Apply post-generation fixes to the model result."""
  L185: # Keep escaped newlines inside fenced code blocks untouched.
  L207: # Route standard queries to native streaming for lower TTFB
  L215: # Fallback for tool-enabled requests:
  L216: # MindIE currently drops choices when stream=True and tools are present.
  ... (truncated)

## 1f59e945 2026-04-25 Octopus
fix: cap prompt caching breakpoints at 4 to prevent API 400 errors (#2449)

* fix: cap prompt caching breakpoints at 4 to prevent API 400 errors (fixes #2448)

The previous _apply_prompt_caching() attached cache_control to every text
block in the system prompt, every content block in the last N messages, and
the last tool definition. In multi-turn conversations with structured content
blocks this easily exceeded the 4-breakpoint hard limit enforced by both the
Anthropic API and AWS Bedrock, producing a 400 Bad Request (or a silent
"No generations found in stream" when streaming).

Fix: collect all candidate blocks in document order, then apply cache_control
only to the last MAX_CACHE_BREAKPOINTS (4) of them. Later breakpoints cover a
larger prefix and therefore yield better cache hit rates, making this the
optimal placement strategy as well as the safe one.

Adds 13 unit tests covering the budget cap, edge cases, and correct
last-candidate placement.

* docs: clarify _apply_prompt_caching docstring includes tool definitions

Per Copilot review: the implementation also caches the last tool definition
(see the candidates list at lines 202-205), so the docstring summary should
explicitly mention tools alongside system and recent messages.

* Fix the lint error

* style: fix ruff format check for test_claude_provider_prompt_caching.py

Add the missing blank line before the 'Edge cases' section comment so
that ruff format --check passes in CI.

---------

Co-authored-by: octo-patch <octo-patch@github.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/models/claude_provider.py`
  L193: """Apply ephemeral cache_control to system, recent messages, and last tool definition.
  L199: """
  L202: # Collect candidate blocks in document order:
  L203: #   1. system text blocks
  L204: #   2. content blocks of the last prompt_cache_size messages
  L205: #   3. the last tool definition
  L208: # 1. System blocks
  L219: # 2. Recent message blocks
  L236: # 3. Last tool definition
  L241: # Apply cache_control only to the last MAX_CACHE_BREAKPOINTS candidates
  L242: # to stay within the API limit.

## d8ecaf46 2026-04-07 rayhpeng
feat(persistence): add unified persistence layer with event store, token tracking, and feedback (#1930)

* feat(persistence): add SQLAlchemy 2.0 async ORM scaffold

Introduce a unified database configuration (DatabaseConfig) that
controls both the LangGraph checkpointer and the DeerFlow application
persistence layer from a single `database:` config section.

New modules:
- deerflow.config.database_config — Pydantic config with memory/sqlite/postgres backends
- deerflow.persistence — async engine lifecycle, DeclarativeBase with to_dict mixin, Alembic skeleton
- deerflow.runtime.runs.store — RunStore ABC + MemoryRunStore implementation

Gateway integration initializes/tears down the persistence engine in
the existing langgraph_runtime() context manager. Legacy checkpointer
config is preserved for backward compatibility.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(persistence): add RunEventStore ABC + MemoryRunEventStore

Phase 2-A prerequisite for event storage: adds the unified run event
stream interface (RunEventStore) with an in-memory implementation,
RunEventsConfig, gateway integration, and comprehensive tests (27 cases).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(persistence): add ORM models, repositories, DB/JSONL event stores, RunJournal, and API endpoints

Phase 2-B: run persistence + event storage + token tracking.

- ORM models: RunRow (with token fields), ThreadMetaRow, RunEventRow
- RunRepository implements RunStore ABC via SQLAlchemy ORM
- ThreadMetaRepository with owner access control
- DbRunEventStore with trace content truncation and cursor pagination
- JsonlRunEventStore with per-run files and seq recovery from disk
- RunJournal (BaseCallbackHandler) captures LLM/tool/lifecycle events,
  accumulates token usage by caller type, buffers and flushes to store
- RunManager now accepts optional RunStore for persistent backing
- Worker creates RunJournal, writes human_message, injects callbacks
- Gateway deps use factory functions (RunRepository when DB available)
- New endpoints: messages, run messages, run events, token-usage
- ThreadCreateRequest gains assistant_id field
- 92 tests pass (33 new), zero regressions

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(persistence): add user feedback + follow-up run association

Phase 2-C: feedback and follow-up tracking.

- FeedbackRow ORM model (rating +1/-1, optional message_id, comment)
- FeedbackRepository with CRUD, list_by_run/thread, aggregate stats
- Feedback API endpoints: create, list, stats, delete
- follow_up_to_run_id in RunCreateRequest (explicit or auto-detected
  from latest successful run on the thread)
- Worker writes follow_up_to_run_id into human_message event metadata
- Gateway deps: feedback_repo factory + getter
- 17 new tests (14 FeedbackRepository + 3 follow-up association)
- 109 total tests pass, zero regressions

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* test+config: comprehensive Phase 2 test coverage + deprecate checkpointer config

- config.example.yaml: deprecate standalone checkpointer section, activate
  unified database:sqlite as default (drives both checkpointer + app data)
- New: test_thread_meta_repo.py (14 tests) — full ThreadMetaRepository coverage
  including check_access owner logic, list_by_owner pagination
- Extended test_run_repository.py (+4 tests) — completion preserves fields,
  list ordering desc, limit, owner_none returns all
- Extended test_run_journal.py (+8 tests) — on_chain_error, track_tokens=false,
  middleware no ai_message, unknown caller tokens, convenience fields,
  tool_error, non-summarization custom event
- Extended test_run_event_store.py (+7 tests) — DB batch seq continuity,
  make_run_event_store factory (memory/db/jsonl/fallback/unknown)
- Extended test_phase2b_integration.py (+4 tests) — create_or_reject persists,
  follow-up metadata, summarization in history, full DB-backed lifecycle
- Fixed DB integration test to use proper fake objects (not MagicMock)
  for JSON-serializable metadata
- 157 total Phase 2 tests pass, zero regressions

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* config: move default sqlite_dir to .deer-flow/data

Keep SQLite databases alongside other DeerFlow-managed data
(threads, memory) under the .deer-flow/ directory instead of a
top-level ./data folder.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* refactor(persistence): remove UTFJSON, use engine-level json_serializer + datetime.now()

- Replace custom UTFJSON type with standard sqlalchemy.JSON in all ORM
  models. Add json_serializer=json.dumps(ensure_ascii=False) to all
  create_async_engine calls so non-ASCII text (Chinese etc.) is stored
  as-is in both SQLite and Postgres.
- Change ORM datetime defaults from datetime.now(UTC) to datetime.now(),
  remove UTC imports.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* refactor(gateway): simplify deps.py with getter factory + inline repos

- Replace 6 identical getter functions with _require() factory.
- Inline 3 _make_*_repo() factories into langgraph_runtime(), call
  get_session_factory() once instead of 3 times.
- Add thread_meta upsert in start_run (services.py).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(docker): add UV_EXTRAS build arg for optional dependencies

Support installing optional dependency groups (e.g. postgres) at
Docker build time via UV_EXTRAS build arg:
  UV_EXTRAS=postgres docker compose build

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* refactor(journal): fix flush, token tracking, and consolidate tests

RunJournal fixes:
- _flush_sync: retain events in buffer when no event loop instead of
  dropping them; worker's finally block flushes via async flush().
- on_llm_end: add tool_calls filter and caller=="lead_agent" guard for
  ai_message events; mark message IDs for dedup with record_llm_usage.
- worker.py: persist completion data (tokens, message count) to RunStore
  in finally block.

Model factory:
- Auto-inject stream_usage=True for BaseChatOpenAI subclasses with
  custom api_base, so usage_metadata is populated in streaming responses.

Test consolidation:
- Delete test_phase2b_integration.py (redundant with existing tests).
- Move DB-backed lifecycle test into test_run_journal.py.
- Add tests for stream_usage injection in test_model_factory.py.
- Clean up executor/task_tool dead journal references.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(events): widen content type to str|dict in all store backends

Allow event content to be a dict (for structured OpenAI-format messages)
in addition to plain strings. Dict values are JSON-serialized for the DB
backend and deserialized on read; memory and JSONL backends handle dicts
natively. Trace truncation now serializes dicts to JSON before measuring.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(events): use metadata flag instead of heuristic for dict content detection

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(converters): add LangChain-to-OpenAI message format converters

Pure functions langchain_to_openai_message, langchain_to_openai_completion,
langchain_messages_to_openai, and _infer_finish_reason for converting
LangChain BaseMessage objects to OpenAI Chat Completions format, used by
RunJournal for event storage. 15 unit tests added.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(converters): handle empty list content as null, clean up test

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(events): human_message content uses OpenAI user message format

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(events): ai_message uses OpenAI format, add ai_tool_call message event

- ai_message content now uses {"role": "assistant", "content": "..."} format
- New ai_tool_call message event emitted when lead_agent LLM responds with tool_calls
- ai_tool_call uses langchain_to_openai_message converter for consistent format
- Both events include finish_reason in metadata ("stop" or "tool_calls")

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(events): add tool_result message event with OpenAI tool message format

Cache tool_call_id from on_tool_start keyed by run_id as fallback for on_tool_end,
then emit a tool_result message event (role=tool, tool_call_id, content) after each
successful tool completion.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(events): summary content uses OpenAI system message format

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(events): replace llm_start/llm_end with llm_request/llm_response in OpenAI format

Add on_chat_model_start to capture structured prompt messages as llm_request events.
Replace llm_end trace events with llm_response using OpenAI Chat Completions format.
Track llm_call_index to pair request/response events.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(events): add record_middleware method for middleware trace events

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* test(events): add full run sequence integration test for OpenAI content format

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(events): align message events with checkpoint format and add middleware tag injection

- Message events (ai_message, ai_tool_call, tool_result, human_message) now use
  BaseMessage.model_dump() format, matching LangGraph checkpoint values.messages
- on_tool_end extracts tool_call_id/name/status from ToolMessage objects
- on_tool_error now emits tool_result message events with error status
- record_middleware uses middleware:{tag} event_type and middleware category
- Summarization custom events use middleware:summarize category
- TitleMiddleware injects middleware:title tag via get_config() inheritance
- SummarizationMiddleware model bound with middleware:summarize tag
- Worker writes human_message using HumanMessage.model_dump()

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(threads): switch search endpoint to threads_meta table and sync title

- POST /api/threads/search now queries threads_meta table directly,
  removing the two-phase Store + Checkpointer scan approach
- Add ThreadMetaRepository.search() with metadata/status filters
- Add ThreadMetaRepository.update_display_name() for title sync
- Worker syncs checkpoint title to threads_meta.display_name on run completion
- Map display_name to values.title in search response for API compatibility

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(threads): history endpoint reads messages from event store

- POST /api/threads/{thread_id}/history now combines two data sources:
  checkpointer for checkpoint_id, metadata, title, thread_data;
  event store for messages (complete history, not truncated by summarization)
- Strip internal LangGraph metadata keys from response
- Remove full channel_values serialization in favor of selective fields

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix: remove duplicate optional-dependencies header in pyproject.toml

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(middleware): pass tagged config to TitleMiddleware ainvoke call

Without the config, the middleware:title tag was not injected,
causing the LLM response to be recorded as a lead_agent ai_message
in run_events.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix: resolve merge conflict in .env.example

Keep both DATABASE_URL (from persistence-scaffold) and WECOM
credentials (from main) after the merge.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(persistence): address review feedback on PR #1851

- Fix naive datetime.now() → datetime.now(UTC) in all ORM models
- Fix seq race condition in DbRunEventStore.put() with FOR UPDATE
  and UNIQUE(thread_id, seq) constraint
- Encapsulate _store access in RunManager.update_run_completion()
- Deduplicate _store.put() logic in RunManager via _persist_to_store()
- Add update_run_completion to RunStore ABC + MemoryRunStore
- Wire follow_up_to_run_id through the full create path
- Add error recovery to RunJournal._flush_sync() lost-event scenario
- Add migration note for search_threads breaking change
- Fix test_checkpointer_none_fix mock to set database=None

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* chore: update uv.lock

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(persistence): address 22 review comments from CodeQL, Copilot, and Code Quality

Bug fixes:
- Sanitize log params to prevent log injection (CodeQL)
- Reset threads_meta.status to idle/error when run completes
- Attach messages only to latest checkpoint in /history response
- Write threads_meta on POST /threads so new threads appear in search

Lint fixes:
- Remove unused imports (journal.py, migrations/env.py, test_converters.py)
- Convert lambda to named function (engine.py, Ruff E731)
- Remove unused logger definitions in repos (Ruff F841)
- Add logging to JSONL decode errors and empty except blocks
- Separate assert side-effects in tests (CodeQL)
- Remove unused local variables in tests (Ruff F841)
- Fix max_trace_content truncation to use byte length, not char length

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* style: apply ruff format to persistence and runtime files

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* Potential fix for pull request finding 'Statement has no effect'

Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>

* refactor(runtime): introduce RunContext to reduce run_agent parameter bloat

Extract checkpointer, store, event_store, run_events_config, thread_meta_repo,
and follow_up_to_run_id into a frozen RunContext dataclass. Add get_run_context()
in deps.py to build the base context from app.state singletons. start_run() uses
dataclasses.replace() to enrich per-run fields before passing ctx to run_agent.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* refactor(gateway): move sanitize_log_param to app/gateway/utils.py

Extract the log-injection sanitizer from routers/threads.py into a shared
utils module and rename to sanitize_log_param (public API). Eliminates the
reverse service → router import in services.py.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* perf: use SQL aggregation for feedback stats and thread token usage

Replace Python-side counting in FeedbackRepository.aggregate_by_run with
a single SELECT COUNT/SUM query. Add RunStore.aggregate_tokens_by_thread
abstract method with SQL GROUP BY implementation in RunRepository and
Python fallback in MemoryRunStore. Simplify the thread_token_usage
endpoint to delegate to the new method, eliminating the limit=10000
truncation risk.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* docs: annotate DbRunEventStore.put() as low-frequency path

Add docstring clarifying that put() opens a per-call transaction with
FOR UPDATE and should only be used for infrequent writes (currently
just the initial human_message event). High-throughput callers should
use put_batch() instead.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(threads): fall back to Store search when ThreadMetaRepository is unavailable

When database.backend=memory (default) or no SQL session factory is
configured, search_threads now queries the LangGraph Store instead of
returning 503. Returns empty list if neither Store nor repo is available.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* refactor(persistence): introduce ThreadMetaStore ABC for backend-agnostic thread metadata

Add ThreadMetaStore abstract base class with create/get/search/update/delete
interface. ThreadMetaRepository (SQL) now inherits from it. New
MemoryThreadMetaStore wraps LangGraph BaseStore for memory-mode deployments.

deps.py now always provides a non-None thread_meta_repo, eliminating all
`if thread_meta_repo is not None` guards in services.py, worker.py, and
routers/threads.py. search_threads no longer needs a Store fallback branch.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* refactor(history): read messages from checkpointer instead of RunEventStore

The /history endpoint now reads messages directly from the
checkpointer's channel_values (the authoritative source) instead of
querying RunEventStore.list_messages(). The RunEventStore API is
preserved for other consumers.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(persistence): address new Copilot review comments

- feedback.py: validate thread_id/run_id before deleting feedback
- jsonl.py: add path traversal protection with ID validation
- run_repo.py: parse `before` to datetime for PostgreSQL compat
- thread_meta_repo.py: fix pagination when metadata filter is active
- database_config.py: use resolve_path for sqlite_dir consistency

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* Implement skill self-evolution and skill_manage flow (#1874)

* chore: ignore .worktrees directory

* Add skill_manage self-evolution flow

* Fix CI regressions for skill_manage

* Address PR review feedback for skill evolution

* fix(skill-evolution): preserve history on delete

* fix(skill-evolution): tighten scanner fallbacks

* docs: add skill_manage e2e evidence screenshot

* fix(skill-manage): avoid blocking fs ops in session runtime

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

* fix(config): resolve sqlite_dir relative to CWD, not Paths.base_dir

resolve_path() resolves relative to Paths.base_dir (.deer-flow),
which double-nested the path to .deer-flow/.deer-flow/data/app.db.
Use Path.resolve() (CWD-relative) instead.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* Feature/feishu receive file (#1608)

* feat(feishu): add channel file materialization hook for inbound messages

- Introduce Channel.receive_file(msg, thread_id) as a base method for file materialization; default is no-op.
- Implement FeishuChannel.receive_file to download files/images from Feishu messages, save to sandbox, and inject virtual paths into msg.text.
- Update ChannelManager to call receive_file for any channel if msg.files is present, enabling downstream model access to user-uploaded files.
- No impact on Slack/Telegram or other channels (they inherit the default no-op).

* style(backend): format code with ruff for lint compliance

- Auto-formatted packages/harness/deerflow/agents/factory.py and tests/test_create_deerflow_agent.py using `ruff format`
- Ensured both files conform to project linting standards
- Fixes CI lint check failures caused by code style issues

* fix(feishu): handle file write operation asynchronously to prevent blocking

* fix(feishu): rename GetMessageResourceRequest to _GetMessageResourceRequest and remove redundant code

* test(feishu): add tests for receive_file method and placeholder replacement

* fix(manager): remove unnecessary type casting for channel retrieval

* fix(feishu): update logging messages to reflect resource handling instead of image

* fix(feishu): sanitize filename by replacing invalid characters in file uploads

* fix(feishu): improve filename sanitization and reorder image key handling in message processing

* fix(feishu): add thread lock to prevent filename conflicts during file downloads

* fix(test): correct bad merge in test_feishu_parser.py

* chore: run ruff and apply formatting cleanup
fix(feishu): preserve rich-text attachment order and improve fallback filename handling

* fix(docker): restore gateway env vars and fix langgraph empty arg issue (#1915)

Two production docker-compose.yaml bugs prevent `make up` from working:

1. Gateway missing DEER_FLOW_CONFIG_PATH and DEER_FLOW_EXTENSIONS_CONFIG_PATH
   environment overrides. Added in fb2d99f (#1836) but accidentally reverted
   by ca2fb95 (#1847). Without them, gateway reads host paths from .env via
   env_file, causing FileNotFoundError inside the container.

2. Langgraph command fails when LANGGRAPH_ALLOW_BLOCKING is unset (default).
   Empty $${allow_blocking} inserts a bare space between flags, causing
   ' --no-reload' to be parsed as unexpected extra argument. Fix by building
   args string first and conditionally appending --allow-blocking.

Co-authored-by: cooper <cooperfu@tencent.com>

* fix(frontend): resolve invalid HTML nesting and tabnabbing vulnerabilities (#1904)

* fix(frontend): resolve invalid HTML nesting and tabnabbing vulnerabilities

Fix `<button>` inside `<a>` invalid HTML in artifact components and add
missing `noopener,noreferrer` to `window.open` calls to prevent reverse
tabnabbing.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* fix(frontend): address Copilot review on tabnabbing and double-tab-open

Remove redundant parent onClick on web_fetch ChainOfThoughtStep to
prevent opening two tabs on link click, and explicitly null out
window.opener after window.open() for defensive tabnabbing hardening.

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

* refactor(persistence): organize entities into per-entity directories

Restructure the persistence layer from horizontal "models/ + repositories/"
split into vertical entity-aligned directories. Each entity (thread_meta,
run, feedback) now owns its ORM model, abstract interface (where applicable),
and concrete implementations under a single directory with an aggregating
__init__.py for one-line imports.

Layout:
  persistence/thread_meta/{base,model,sql,memory}.py
  persistence/run/{model,sql}.py
  persistence/feedback/{model,sql}.py

models/__init__.py is kept as a facade so Alembic autogenerate continues to
discover all ORM tables via Base.metadata. RunEventRow remains under
models/run_event.py because its storage implementation lives in
runtime/events/store/db.py and has no matching repository directory.

The repositories/ directory is removed entirely. All call sites in
gateway/deps.py and tests are updated to import from the new entity
packages, e.g.:

    from deerflow.persistence.thread_meta import ThreadMetaRepository
    from deerflow.persistence.run import RunRepository
    from deerflow.persistence.feedback import FeedbackRepository

Full test suite passes (1690 passed, 14 skipped).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(gateway): sync thread rename and delete through ThreadMetaStore

The POST /threads/{id}/state endpoint previously synced title changes
only to the LangGraph Store via _store_upsert. In sqlite mode the search
endpoint reads from the ThreadMetaRepository SQL table, so renames never
appeared in /threads/search until the next agent run completed (worker.py
syncs title from checkpoint to thread_meta in its finally block).

Likewise the DELETE /threads/{id} endpoint cleaned up the filesystem,
Store, and checkpointer but left the threads_meta row orphaned in sqlite,
so deleted threads kept appearing in /threads/search.

Fix both endpoints by routing through the ThreadMetaStore abstraction
which already has the correct sqlite/memory implementations wired up by
deps.py. The rename path now calls update_display_name() and the delete
path calls delete() — both work uniformly across backends.

Verified end-to-end with curl in gateway mode against sqlite backend.
Existing test suite (1690 passed) and focused router/repo tests pass.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* refactor(gateway): route all thread metadata access through ThreadMetaStore

Following the rename/delete bug fix in PR1, migrate the remaining direct
LangGraph Store reads/writes in the threads router and services to the
ThreadMetaStore abstraction so that the sqlite and memory backends behave
identically and the legacy dual-write paths can be removed.

Migrated endpoints (threads.py):
- create_thread: idempotency check + write now use thread_meta_repo.get/create
  instead of dual-writing the LangGraph Store and the SQL row.
- get_thread: reads from thread_meta_repo.get; the checkpoint-only fallback
  for legacy threads is preserved.
- patch_thread: replaced _store_get/_store_put with thread_meta_repo.update_metadata.
- delete_thread_data: dropped the legacy store.adelete; thread_meta_repo.delete
  already covers it.

Removed dead code (services.py):
- _upsert_thread_in_store — redundant with the immediately following
  thread_meta_repo.create() call.
- _sync_thread_title_after_run — worker.py's finally block already syncs
  the title via thread_meta_repo.update_display_name() after each run.

Removed dead code (threads.py):
- _store_get / _store_put / _store_upsert helpers (no remaining callers).
- THREADS_NS constant.
- get_store import (router no longer touches the LangGraph Store directly).

New abstract method:
- ThreadMetaStore.update_metadata(thread_id, metadata) merges metadata into
  the thread's metadata field. Implemented in both ThreadMetaRepository (SQL,
  read-modify-write inside one session) and MemoryThreadMetaStore. Three new
  unit tests cover merge / empty / nonexistent behaviour.

Net change: -134 lines. Full test suite: 1693 passed, 14 skipped.
Verified end-to-end with curl in gateway mode against sqlite backend
(create / patch / get / rename / search / delete).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>
Co-authored-by: DanielWalnut <45447813+hetaoBackend@users.noreply.github.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: JilongSun <965640067@qq.com>
Co-authored-by: jie <49781832+stan-fu@users.noreply.github.com>
Co-authored-by: cooper <cooperfu@tencent.com>
Co-authored-by: yangzheli <43645580+yangzheli@users.noreply.github.com>

- `backend/packages/harness/deerflow/models/factory.py`
  L140: # Ensure stream_usage is enabled so that token usage metadata is available
  L141: # in streaming responses.  LangChain's BaseChatOpenAI only defaults
  L142: # stream_usage=True when no custom base_url/api_base is set, so models
  L143: # hitting third-party endpoints (e.g. doubao, deepseek) silently lose
  L144: # usage data.  We default it to True unless explicitly configured.

## e82940c0 2026-04-28 greatmengqi
refactor: thread release config through lead path (#2612)

Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>

- `backend/packages/harness/deerflow/models/factory.py`

## 395c1435 2026-04-28 pyp0327
chore(adpator):Adapt MindIE engine model and improve testing and fixes (#2523)

* feat(models): 适配 MindIE引擎的模型

* test: add unit tests for MindIEChatModel adapter and fix PR review comments

* chore: update uv.lock with pytest-asyncio

* build: add pytest-asyncio to test dependencies

* fix: address PR review comments (lazy import, cache clients, safe newline escape, strict xml regex)

* fix(mindie): preserve string args without JSON quotes in XML tool call serialization

* fix(mindie): preserve string args without JSON quotes in XML tool call serialization

* test_mindie_provider:format

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* fix(mindie): prevent nested tool_call params from leaking into outer args

* fixed by escaping XML entities in _fix_messages and unescaping during parse, with regression tests added.

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/models/mindie_provider.py`
  L86: # Ignore nested tool blocks when extracting parameters for this call.
  L87: # Nested `<tool_call>` sections represent separate invocations and
  L88: # their `<parameter>` tags must not leak into the current call args.

## 866d1ca4 2026-05-02 KiteEater
Populate Codex usage metadata for token accounting (#2585)

- `backend/packages/harness/deerflow/models/openai_codex_provider.py`

## bb8b234d 2026-05-02 Willem Jiang
chroe(2585): keep polishing the code of codex token usage (#2689)

- `backend/packages/harness/deerflow/models/openai_codex_provider.py`
  L33: """Convert Codex/Responses API usage dict to LangChain usage_metadata format.
  L38: """

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

- `backend/packages/harness/deerflow/models/claude_provider.py`

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

- `backend/packages/harness/deerflow/models/factory.py`

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

- `backend/packages/harness/deerflow/models/patched_minimax.py`
  L122: """Drop the per-message ``name`` field from user-role messages.
  L130: """

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

