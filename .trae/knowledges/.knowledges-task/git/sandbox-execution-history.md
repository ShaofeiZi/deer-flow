## ca1b7d5f 2026-04-18 Shawn Jasper
fix(sandbox): add missing path masking in ls_tool output (#2317)

ls_tool was the only file-system tool that did not call
mask_local_paths_in_output() before returning its result, causing host
absolute paths (e.g. /Users/.../backend/.deer-flow/knowledge-base/...)
to leak to the LLM instead of the expected virtual paths
(/mnt/knowledge-base/...).

This patch:
- Adds the mask_local_paths_in_output() call to ls_tool, consistent
  with bash_tool, glob_tool and grep_tool.
- Initialises thread_data = None before the is_local_sandbox branch
  (same pattern as glob_tool) so the variable is always in scope.
- Adds three new tests covering user-data path masking, skills path
  masking and the empty-directory edge case.

- `backend/packages/harness/deerflow/sandbox/tools.py`

## 950821cb 2026-04-25 orbisai0security
fix: use subprocess instead of os.system in local_backend.py (#2494)

* fix: use subprocess instead of os.system in local_backend.py

The sandbox backend and skill evaluation scripts use subprocess

* fixing the failing test

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`

## 2e05f380 2026-04-12 rayhpeng
feat(persistence): per-user filesystem isolation, run-scoped APIs, and state/history simplification (#2153)

* feat(persistence): add unified persistence layer with event store, token tracking, and feedback (#1930)

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

* feat(auth): release-validation pass for 2.0-rc — 12 blockers + simplify follow-ups (#2008)

* feat(auth): introduce backend auth module

Port RFC-001 authentication core from PR #1728:
- JWT token handling (create_access_token, decode_token, TokenPayload)
- Password hashing (bcrypt) with verify_password
- SQLite UserRepository with base interface
- Provider Factory pattern (LocalAuthProvider)
- CLI reset_admin tool
- Auth-specific errors (AuthErrorCode, TokenError, AuthErrorResponse)

Deps:
- bcrypt>=4.0.0
- pyjwt>=2.9.0
- email-validator>=2.0.0
- backend/uv.toml pins public PyPI index

Tests: 12 pure unit tests (test_auth_config.py, test_auth_errors.py).

Scope note: authz.py, test_auth.py, and test_auth_type_system.py are
deferred to commit 2 because they depend on middleware and deps wiring
that is not yet in place. Commit 1 stays "pure new files only" as the
spec mandates.

* feat(auth): wire auth end-to-end (middleware + frontend replacement)

Backend:
- Port auth_middleware, csrf_middleware, langgraph_auth, routers/auth
- Port authz decorator (owner_filter_key defaults to 'owner_id')
- Merge app.py: register AuthMiddleware + CSRFMiddleware + CORS, add
  _ensure_admin_user lifespan hook, _migrate_orphaned_threads helper,
  register auth router
- Merge deps.py: add get_local_provider, get_current_user_from_request,
  get_optional_user_from_request; keep get_current_user as thin str|None
  adapter for feedback router
- langgraph.json: add auth path pointing to langgraph_auth.py:auth
- Rename metadata['user_id'] -> metadata['owner_id'] in langgraph_auth
  (both metadata write and LangGraph filter dict) + test fixtures

Frontend:
- Delete better-auth library and api catch-all route
- Remove better-auth npm dependency and env vars (BETTER_AUTH_SECRET,
  BETTER_AUTH_GITHUB_*) from env.js
- Port frontend/src/core/auth/* (AuthProvider, gateway-config,
  proxy-policy, server-side getServerSideUser, types)
- Port frontend/src/core/api/fetcher.ts
- Port (auth)/layout, (auth)/login, (auth)/setup pages
- Rewrite workspace/layout.tsx as server component that calls
  getServerSideUser and wraps in AuthProvider
- Port workspace/workspace-content.tsx for the client-side sidebar logic

Tests:
- Port 5 auth test files (test_auth, test_auth_middleware,
  test_auth_type_system, test_ensure_admin, test_langgraph_auth)
- 176 auth tests PASS

After this commit: login/logout/registration flow works, but persistence
layer does not yet filter by owner_id. Commit 4 closes that gap.

* feat(auth): account settings page + i18n

- Port account-settings-page.tsx (change password, change email, logout)
- Wire into settings-dialog.tsx as new "account" section with UserIcon,
  rendered first in the section list
- Add i18n keys:
  - en-US/zh-CN: settings.sections.account ("Account" / "账号")
  - en-US/zh-CN: button.logout ("Log out" / "退出登录")
  - types.ts: matching type declarations

* feat(auth): enforce owner_id across 2.0-rc persistence layer

Add request-scoped contextvar-based owner filtering to threads_meta,
runs, run_events, and feedback repositories. Router code is unchanged
— isolation is enforced at the storage layer so that any caller that
forgets to pass owner_id still gets filtered results, and new routes
cannot accidentally leak data.

Core infrastructure
-------------------
- deerflow/runtime/user_context.py (new):
  - ContextVar[CurrentUser | None] with default None
  - runtime_checkable CurrentUser Protocol (structural subtype with .id)
  - set/reset/get/require helpers
  - AUTO sentinel + resolve_owner_id(value, method_name) for sentinel
    three-state resolution: AUTO reads contextvar, explicit str
    overrides, explicit None bypasses the filter (for migration/CLI)

Repository changes
------------------
- ThreadMetaRepository: create/get/search/update_*/delete gain
  owner_id=AUTO kwarg; read paths filter by owner, writes stamp it,
  mutations check ownership before applying
- RunRepository: put/get/list_by_thread/delete gain owner_id=AUTO kwarg
- FeedbackRepository: create/get/list_by_run/list_by_thread/delete
  gain owner_id=AUTO kwarg
- DbRunEventStore: list_messages/list_events/list_messages_by_run/
  count_messages/delete_by_thread/delete_by_run gain owner_id=AUTO
  kwarg. Write paths (put/put_batch) read contextvar softly: when a
  request-scoped user is available, owner_id is stamped; background
  worker writes without a user context pass None which is valid
  (orphan row to be bound by migration)

Schema
------
- persistence/models/run_event.py: RunEventRow.owner_id = Mapped[
  str | None] = mapped_column(String(64), nullable=True, index=True)
- No alembic migration needed: 2.0 ships fresh, Base.metadata.create_all
  picks up the new column automatically

Middleware
----------
- auth_middleware.py: after cookie check, call get_optional_user_from_
  request to load the real User, stamp it into request.state.user AND
  the contextvar via set_current_user, reset in a try/finally. Public
  paths and unauthenticated requests continue without contextvar, and
  @require_auth handles the strict 401 path

Test infrastructure
-------------------
- tests/conftest.py: @pytest.fixture(autouse=True) _auto_user_context
  sets a default SimpleNamespace(id="test-user-autouse") on every test
  unless marked @pytest.mark.no_auto_user. Keeps existing 20+
  persistence tests passing without modification
- pyproject.toml [tool.pytest.ini_options]: register no_auto_user
  marker so pytest does not emit warnings for opt-out tests
- tests/test_user_context.py: 6 tests covering three-state semantics,
  Protocol duck typing, and require/optional APIs
- tests/test_thread_meta_repo.py: one test updated to pass owner_id=
  None explicitly where it was previously relying on the old default

Test results
------------
- test_user_context.py: 6 passed
- test_auth*.py + test_langgraph_auth.py + test_ensure_admin.py: 127
- test_run_event_store / test_run_repository / test_thread_meta_repo
  / test_feedback: 92 passed
- Full backend suite: 1905 passed, 2 failed (both @requires_llm flaky
  integration tests unrelated to auth), 1 skipped

* feat(auth): extend orphan migration to 2.0-rc persistence tables

_ensure_admin_user now runs a three-step pipeline on every boot:

  Step 1 (fatal):     admin user exists / is created / password is reset
  Step 2 (non-fatal): LangGraph store orphan threads → admin
  Step 3 (non-fatal): SQL persistence tables → admin
    - threads_meta
    - runs
    - run_events
    - feedback

Each step is idempotent. The fatal/non-fatal split mirrors PR #1728's
original philosophy: admin creation failure blocks startup (the system
is unusable without an admin), whereas migration failures log a warning
and let the service proceed (a partial migration is recoverable; a
missing admin is not).

Key helpers
-----------
- _iter_store_items(store, namespace, *, page_size=500):
  async generator that cursor-paginates across LangGraph store pages.
  Fixes PR #1728's hardcoded limit=1000 bug that would silently lose
  orphans beyond the first page.

- _migrate_orphaned_threads(store, admin_user_id):
  Rewritten to use _iter_store_items. Returns the migrated count so the
  caller can log it; raises only on unhandled exceptions.

- _migrate_orphan_sql_tables(admin_user_id):
  Imports the 4 ORM models lazily, grabs the shared session factory,
  runs one UPDATE per table in a single transaction, commits once.
  No-op when no persistence backend is configured (in-memory dev).

Tests: test_ensure_admin.py (8 passed)

* test(auth): port AUTH test plan docs + lint/format pass

- Port backend/docs/AUTH_TEST_PLAN.md and AUTH_UPGRADE.md from PR #1728
- Rename metadata.user_id → metadata.owner_id in AUTH_TEST_PLAN.md
  (4 occurrences from the original PR doc)
- ruff auto-fix UP037 in sentinel type annotations: drop quotes around
  "str | None | _AutoSentinel" now that from __future__ import
  annotations makes them implicit string forms
- ruff format: 2 files (app/gateway/app.py, runtime/user_context.py)

Note on test coverage additions:
- conftest.py autouse fixture was already added in commit 4 (had to
  be co-located with the repository changes to keep pre-existing
  persistence tests passing)
- cross-user isolation E2E tests (test_owner_isolation.py) deferred
  — enforcement is already proven by the 98-test repository suite
  via the autouse fixture + explicit _AUTO sentinel exercises
- New test cases (TC-API-17..20, TC-ATK-13, TC-MIG-01..07) listed
  in AUTH_TEST_PLAN.md are deferred to a follow-up PR — they are
  manual-QA test cases rather than pytest code, and the spec-level
  coverage is already met by test_user_context.py + the 98-test
  repository suite.

Final test results:
- Auth suite (test_auth*, test_langgraph_auth, test_ensure_admin,
  test_user_context): 186 passed
- Persistence suite (test_run_event_store, test_run_repository,
  test_thread_meta_repo, test_feedback): 98 passed
- Lint: ruff check + ruff format both clean

* test(auth): add cross-user isolation test suite

10 tests exercising the storage-layer owner filter by manually
switching the user_context contextvar between two users. Verifies
the safety invariant:

  After a repository write with owner_id=A, a subsequent read with
  owner_id=B must not return the row, and vice versa.

Covers all 4 tables that own user-scoped data:

TC-API-17  threads_meta  — read, search, update, delete cross-user
TC-API-18  runs          — get, list_by_thread, delete cross-user
TC-API-19  run_events    — list_messages, list_events, count_messages,
                           delete_by_thread (CRITICAL: raw conversation
                           content leak vector)
TC-API-20  feedback      — get, list_by_run, delete cross-user

Plus two meta-tests verifying the sentinel pattern itself:
- AUTO + unset contextvar raises RuntimeError
- explicit owner_id=None bypasses the filter (migration escape hatch)

Architecture note
-----------------
These tests bypass the HTTP layer by design. The full chain
(cookie → middleware → contextvar → repository) is covered piecewise:

- test_auth_middleware.py: middleware sets contextvar from cookies
- test_owner_isolation.py: repositories enforce isolation when
  contextvar is set to different users

Together they prove the end-to-end safety property without the
ceremony of spinning up a full TestClient + in-memory DB for every
router endpoint.

Tests pass: 231 (full auth + persistence + isolation suite)
Lint: clean

* refactor(auth): migrate user repository to SQLAlchemy ORM

Move the users table into the shared persistence engine so auth
matches the pattern of threads_meta, runs, run_events, and feedback —
one engine, one session factory, one schema init codepath.

New files
---------
- persistence/user/__init__.py, persistence/user/model.py: UserRow
  ORM class with partial unique index on (oauth_provider, oauth_id)
- Registered in persistence/models/__init__.py so
  Base.metadata.create_all() picks it up

Modified
--------
- auth/repositories/sqlite.py: rewritten as async SQLAlchemy,
  identical constructor pattern to the other four repositories
  (def __init__(self, session_factory) + self._sf = session_factory)
- auth/config.py: drop users_db_path field — storage is configured
  through config.database like every other table
- deps.py/get_local_provider: construct SQLiteUserRepository with
  the shared session factory, fail fast if engine is not initialised
- tests/test_auth.py: rewrite test_sqlite_round_trip_new_fields to
  use the shared engine (init_engine + close_engine in a tempdir)
- tests/test_auth_type_system.py: add per-test autouse fixture that
  spins up a scratch engine and resets deps._cached_* singletons

* refactor(auth): remove SQL orphan migration (unused in supported scenarios)

The _migrate_orphan_sql_tables helper existed to bind NULL owner_id
rows in threads_meta, runs, run_events, and feedback to the admin on
first boot. But in every supported upgrade path, it's a no-op:

  1. Fresh install: create_all builds fresh tables, no legacy rows
  2. No-auth → with-auth (no existing persistence DB): persistence
     tables are created fresh by create_all, no legacy rows
  3. No-auth → with-auth (has existing persistence DB from #1930):
     NOT a supported upgrade path — "有 DB 到有 DB" schema evolution
     is out of scope; users wipe DB or run manual ALTER

So the SQL orphan migration never has anything to do in the
supported matrix. Delete the function, simplify _ensure_admin_user
from a 3-step pipeline to a 2-step one (admin creation + LangGraph
store orphan migration only).

LangGraph store orphan migration stays: it serves the real
"no-auth → with-auth" upgrade path where a user's existing LangGraph
thread metadata has no owner_id field and needs to be stamped with
the newly-created admin's id.

Tests: 284 passed (auth + persistence + isolation)
Lint: clean

* security(auth): write initial admin password to 0600 file instead of logs

CodeQL py/clear-text-logging-sensitive-data flagged 3 call sites that
logged the auto-generated admin password to stdout via logger.info().
Production log aggregators (ELK/Splunk/etc) would have captured those
cleartext secrets. Replace with a shared helper that writes to
.deer-flow/admin_initial_credentials.txt with mode 0600, and log only
the path.

New file
--------
- app/gateway/auth/credential_file.py: write_initial_credentials()
  helper. Takes email, password, and a "initial"/"reset" label.
  Creates .deer-flow/ if missing, writes a header comment plus the
  email+password, chmods 0o600, returns the absolute Path.

Modified
--------
- app/gateway/app.py: both _ensure_admin_user paths (fresh creation
  + needs_setup password reset) now write to file and log the path
- app/gateway/auth/reset_admin.py: rewritten to use the shared ORM
  repo (SQLiteUserRepository with session_factory) and the
  credential_file helper. The previous implementation was broken
  after the earlier ORM refactor — it still imported _get_users_conn
  and constructed SQLiteUserRepository() without a session factory.

No tests changed — the three password-log sites are all exercised
via existing test_ensure_admin.py which checks that startup
succeeds, not that a specific string appears in logs.

CodeQL alerts 272, 283, 284: all resolved.

* security(auth): strict JWT validation in middleware (fix junk cookie bypass)

AUTH_TEST_PLAN test 7.5.8 expects junk cookies to be rejected with
401. The previous middleware behaviour was "presence-only": check
that some access_token cookie exists, then pass through. In
combination with my Task-12 decision to skip @require_auth
decorators on routes, this created a gap where a request with any
cookie-shaped string (e.g. access_token=not-a-jwt) would bypass
authentication on routes that do not touch the repository
(/api/models, /api/mcp/config, /api/memory, /api/skills, …).

Fix: middleware now calls get_current_user_from_request() strictly
and catches the resulting HTTPException to render a 401 with the
proper fine-grained error code (token_invalid, token_expired,
user_not_found, …). On success it stamps request.state.user and
the contextvar so repository-layer owner filters work downstream.

The 4 old "_with_cookie_passes" tests in test_auth_middleware.py
were written for the presence-only behaviour; they asserted that
a junk cookie would make the handler return 200. They are renamed
to "_with_junk_cookie_rejected" and their assertions flipped to
401. The negative path (no cookie → 401 not_authenticated)
is unchanged.

Verified:
  no cookie       → 401 not_authenticated
  junk cookie     → 401 token_invalid     (the fixed bug)
  expired cookie  → 401 token_expired

Tests: 284 passed (auth + persistence + isolation)
Lint: clean

* security(auth): wire @require_permission(owner_check=True) on isolation routes

Apply the require_permission decorator to all 28 routes that take a
{thread_id} path parameter. Combined with the strict middleware
(previous commit), this gives the double-layer protection that
AUTH_TEST_PLAN test 7.5.9 documents:

  Layer 1 (AuthMiddleware): cookie + JWT validation, rejects junk
                            cookies and stamps request.state.user
  Layer 2 (@require_permission with owner_check=True): per-resource
                            ownership verification via
                            ThreadMetaStore.check_access — returns
                            404 if a different user owns the thread

The decorator's owner_check branch is rewritten to use the SQL
thread_meta_repo (the 2.0-rc persistence layer) instead of the
LangGraph store path that PR #1728 used (_store_get / get_store
in routers/threads.py). The inject_record convenience is dropped
— no caller in 2.0 needs the LangGraph blob, and the SQL repo has
a different shape.

Routes decorated (28 total):
- threads.py: delete, patch, get, get-state, post-state, post-history
- thread_runs.py: post-runs, post-runs-stream, post-runs-wait,
  list_runs, get_run, cancel_run, join_run, stream_existing_run,
  list_thread_messages, list_run_messages, list_run_events,
  thread_token_usage
- feedback.py: create, list, stats, delete
- uploads.py: upload (added Request param), list, delete
- artifacts.py: get_artifact
- suggestions.py: generate (renamed body parameter to avoid
  conflict with FastAPI Request)

Test fixes:
- test_suggestions_router.py: bypass the decorator via __wrapped__
  (the unit tests cover parsing logic, not auth — no point spinning
  up a thread_meta_repo just to test JSON unwrapping)
- test_auth_middleware.py 4 fake-cookie tests: already updated in
  the previous commit (745bf432)

Tests: 293 passed (auth + persistence + isolation + suggestions)
Lint: clean

* security(auth): defense-in-depth fixes from release validation pass

Eight findings caught while running the AUTH_TEST_PLAN end-to-end against
the deployed sg_dev stack. Each is a pre-condition for shipping
release/2.0-rc that the previous PRs missed.

Backend hardening
- routers/auth.py: rate limiter X-Real-IP now requires AUTH_TRUSTED_PROXIES
  whitelist (CIDR/IP allowlist). Without nginx in front, the previous code
  honored arbitrary X-Real-IP, letting an attacker rotate the header to
  fully bypass the per-IP login lockout.
- routers/auth.py: 36-entry common-password blocklist via Pydantic
  field_validator on RegisterRequest + ChangePasswordRequest. The shared
  _validate_strong_password helper keeps the constraint in one place.
- routers/threads.py: ThreadCreateRequest + ThreadPatchRequest strip
  server-reserved metadata keys (owner_id, user_id) via Pydantic
  field_validator so a forged value can never round-trip back to other
  clients reading the same thread. The actual ownership invariant stays
  on the threads_meta row; this closes the metadata-blob echo gap.
- authz.py + thread_meta/sql.py: require_permission gains a require_existing
  flag plumbed through check_access(require_existing=True). Destructive
  routes (DELETE/PATCH/state-update/runs/feedback) now treat a missing
  thread_meta row as 404 instead of "untracked legacy thread, allow",
  closing the cross-user delete-idempotence gap where any user could
  successfully DELETE another user's deleted thread.
- repositories/sqlite.py + base.py: update_user raises UserNotFoundError
  on a vanished row instead of silently returning the input. Concurrent
  delete during password reset can no longer look like a successful update.
- runtime/user_context.py: resolve_owner_id() coerces User.id (UUID) to
  str at the contextvar boundary so SQLAlchemy String(64) columns can
  bind it. The whole 2.0-rc isolation pipeline was previously broken
  end-to-end (POST /api/threads → 500 "type 'UUID' is not supported").
- persistence/engine.py: SQLAlchemy listener enables PRAGMA journal_mode=WAL,
  synchronous=NORMAL, foreign_keys=ON on every new SQLite connection.
  TC-UPG-06 in the test plan expects WAL; previous code shipped with the
  default 'delete' journal.
- auth_middleware.py: stamp request.state.auth = AuthContext(...) so
  @require_permission's short-circuit fires; previously every isolation
  request did a duplicate JWT decode + users SELECT. Also unifies the
  401 payload through AuthErrorResponse(...).model_dump().
- app.py: _ensure_admin_user restructure removes the noqa F821 scoping
  bug where 'password' was referenced outside the branch that defined it.
  New _announce_credentials helper absorbs the duplicate log block in
  the fresh-admin and reset-admin branches.

* fix(frontend+nginx): rollout CSRF on every state-changing client path

The frontend was 100% broken in gateway-pro mode for any user trying to
open a specific chat thread. Three cumulative bugs each silently
masked the next.

LangGraph SDK CSRF gap (api-client.ts)
- The Client constructor took only apiUrl, no defaultHeaders, no fetch
  interceptor. The SDK's internal fetch never sent X-CSRF-Token, so
  every state-changing /api/langgraph-compat/* call (runs/stream,
  threads/search, threads/{tid}/history, ...) hit CSRFMiddleware and
  got 403 before reaching the auth check. UI symptom: empty thread page
  with no error message; the SPA's hooks swallowed the rejection.
- Fix: pass an onRequest hook that injects X-CSRF-Token from the
  csrf_token cookie per request. Reading the cookie per call (not at
  construction time) handles login / logout / password-change cookie
  rotation transparently. The SDK's prepareFetchOptions calls
  onRequest for both regular requests AND streaming/SSE/reconnect, so
  the same hook covers runs.stream and runs.joinStream.

Raw fetch CSRF gap (7 files)
- Audit: 11 frontend fetch sites, only 2 included CSRF (login/setup +
  account-settings change-password). The other 7 routed through raw
  fetch() with no header — suggestions, memory, agents, mcp, skills,
  uploads, and the local thread cleanup hook all 403'd silently.
- Fix: enhance fetcher.ts:fetchWithAuth to auto-inject X-CSRF-Token on
  POST/PUT/DELETE/PATCH from a single shared readCsrfCookie() helper.
  Convert all 7 raw fetch() callers to fetchWithAuth so the contract
  is centrally enforced. api-client.ts and fetcher.ts share
  readCsrfCookie + STATE_CHANGING_METHODS to avoid drift.

nginx routing + buffering (nginx.local.conf)
- The auth feature shipped without updating the nginx config: per-API
  explicit location blocks but no /api/v1/auth/, /api/feedback, /api/runs.
  The frontend's client-side fetches to /api/v1/auth/login/local 404'd
  from the Next.js side because nginx routed /api/* to the frontend.
- Fix: add catch-all `location /api/` that proxies to the gateway.
  nginx longest-prefix matching keeps the explicit blocks (/api/models,
  /api/threads regex, /api/langgraph/, ...) winning for their paths.
- Fix: disable proxy_buffering + proxy_request_buffering for the
  frontend `location /` block. Without it, nginx tries to spool large
  Next.js chunks into /var/lib/nginx/proxy (root-owned) and fails with
  Permission denied → ERR_INCOMPLETE_CHUNKED_ENCODING → ChunkLoadError.

* test(auth): release-validation test infra and new coverage

Test fixtures and unit tests added during the validation pass.

Router test helpers (NEW: tests/_router_auth_helpers.py)
- make_authed_test_app(): builds a FastAPI test app with a stub
  middleware that stamps request.state.user + request.state.auth and a
  permissive thread_meta_repo mock. TestClient-based router tests
  (test_artifacts_router, test_threads_router) use it instead of bare
  FastAPI() so the new @require_permission(owner_check=True) decorators
  short-circuit cleanly.
- call_unwrapped(): walks the __wrapped__ chain to invoke the underlying
  handler without going through the authz wrappers. Direct-call tests
  (test_uploads_router) use it. Typed with ParamSpec so the wrapped
  signature flows through.

Backend test additions
- test_auth.py: 7 tests for the new _get_client_ip trust model (no
  proxy / trusted proxy / untrusted peer / XFF rejection / invalid
  CIDR / no client). 5 tests for the password blocklist (literal,
  case-insensitive, strong password accepted, change-password binding,
  short-password length-check still fires before blocklist).
  test_update_user_raises_when_row_concurrently_deleted: closes a
  shipped-without-coverage gap on the new UserNotFoundError contract.
- test_thread_meta_repo.py: 4 tests for check_access(require_existing=True)
  — strict missing-row denial, strict owner match, strict owner mismatch,
  strict null-owner still allowed (shared rows survive the tightening).
- test_ensure_admin.py: 3 tests for _migrate_orphaned_threads /
  _iter_store_items pagination, covering the TC-UPG-02 upgrade story
  end-to-end via mock store. Closes the gap where the cursor pagination
  was untested even though the previous PR rewrote it.
- test_threads_router.py: 5 tests for _strip_reserved_metadata
  (owner_id removal, user_id removal, safe-keys passthrough, empty
  input, both-stripped).
- test_auth_type_system.py: replace "password123" fixtures with
  Tr0ub4dor3a / AnotherStr0ngPwd! so the new password blocklist
  doesn't reject the test data.

* docs(auth): refresh TC-DOCKER-05 + document Docker validation gap

- AUTH_TEST_PLAN.md TC-DOCKER-05: the previous expectation
  ("admin password visible in docker logs") was stale after the simplify
  pass that moved credentials to a 0600 file. The grep "Password:" check
  would have silently failed and given a false sense of coverage. New
  expectation matches the actual file-based path: 0600 file in
  DEER_FLOW_HOME, log shows the path (not the secret), reverse-grep
  asserts no leaked password in container logs.
- NEW: docs/AUTH_TEST_DOCKER_GAP.md documents the only un-executed
  block in the test plan (TC-DOCKER-01..06). Reason: sg_dev validation
  host has no Docker daemon installed. The doc maps each Docker case
  to an already-validated bare-metal equivalent (TC-1.1, TC-REENT-01,
  TC-API-02 etc.) so the gap is auditable, and includes pre-flight
  reproduction steps for whoever has Docker available.

---------

Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>

* refactor(persistence): unify SQLite to single deerflow.db and move checkpointer to runtime

Merge checkpoints.db and app.db into a single deerflow.db file (WAL mode
handles concurrent access safely). Move checkpointer module from
agents/checkpointer to runtime/checkpointer to better reflect its role
as a runtime infrastructure concern.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* refactor(persistence): rename owner_id to user_id and thread_meta_repo to thread_store

Rename owner_id to user_id across all persistence models, repositories,
stores, routers, and tests for clearer semantics. Rename thread_meta_repo
to thread_store for consistency with run_store/run_event_store naming.
Add ThreadMetaStore return type annotation to get_thread_store().

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(persistence): unify ThreadMetaStore interface with user isolation and factory

Add user_id parameter to all ThreadMetaStore abstract methods. Implement
owner isolation in MemoryThreadMetaStore with _get_owned_record helper.
Add check_access to base class and memory implementation. Add
make_thread_store factory to simplify deps.py initialization. Add
memory-backend isolation tests.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(feedback): add UNIQUE(thread_id, run_id, user_id) constraint

Add UNIQUE constraint to FeedbackRow to enforce one feedback per user per run,
enabling upsert behavior in Task 2. Update tests to use distinct user_ids for
multiple feedback records per run, and pass user_id=None to list_by_run for
admin-style queries that bypass user isolation.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(feedback): add upsert() method with UNIQUE enforcement

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(feedback): add delete_by_run() and list_by_thread_grouped()

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(feedback): add PUT upsert and DELETE-by-run endpoints

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(feedback): enrich messages endpoint with per-run feedback data

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(feedback): add frontend feedback API client

Adds upsertFeedback and deleteFeedback API functions backed by
fetchWithAuth, targeting the /api/threads/{id}/runs/{id}/feedback
endpoint.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(feedback): wire feedback data into message rendering for history echo

Adds useThreadFeedback hook that fetches run-level feedback from the
messages API and builds a runId->FeedbackData map. MessageList now calls
this hook and passes feedback and runId to each MessageListItem so
previously-submitted thumbs are pre-filled when revisiting a thread.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* fix(feedback): correct run_id mapping for feedback echo

The feedbackMap was keyed by run_id but looked up by LangGraph message ID.
Fixed by tracking AI message ordinal index to correlate event store
run_ids with LangGraph SDK messages.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(feedback): use real threadId and refresh after stream

- Pass threadId prop to MessageListItem instead of reading "new" from URL params
- Invalidate thread-feedback query on stream finish so buttons appear immediately
- Show feedback buttons always visible, copy button on hover only

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* style(feedback): group copy and feedback buttons together on the left

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* style(feedback): always show toolbar buttons without hover

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(persistence): stream hang when run_events.backend=db

DbRunEventStore._user_id_from_context() returned user.id without
coercing it to str. User.id is a Pydantic UUID, and aiosqlite cannot
bind a raw UUID object to a VARCHAR column, so the INSERT for the
initial human_message event silently rolled back and raised out of
the worker task. Because that put() sat outside the worker's try
block, the finally-clause that publishes end-of-stream never ran
and the SSE stream hung forever.

jsonl mode was unaffected because json.dumps(default=str) coerces
UUID objects transparently.

Fixes:
- db.py: coerce user.id to str at the context-read boundary (matches
  what resolve_user_id already does for the other repositories)
- worker.py: move RunJournal init + human_message put inside the try
  block so any failure flows through the finally/publish_end path
  instead of hanging the subscriber

Defense-in-depth:
- engine.py: add PRAGMA busy_timeout=5000 so checkpointer and event
  store wait for each other on the shared deerflow.db file instead
  of failing immediately under write-lock contention
- journal.py: skip fire-and-forget _flush_sync when a previous flush
  task is still in flight, to avoid piling up concurrent put_batch
  writes on the same SQLAlchemy engine during streaming; flush() now
  waits for pending tasks before draining the buffer
- database_config.py: doc-only update clarifying WAL + busy_timeout
  keep the unified deerflow.db safe for both workloads

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* chore(persistence): drop redundant busy_timeout PRAGMA

Python's sqlite3 driver defaults to a 5-second busy timeout via the
``timeout`` kwarg of ``sqlite3.connect``, and aiosqlite + SQLAlchemy's
aiosqlite dialect inherit that default. Setting ``PRAGMA busy_timeout=5000``
explicitly was a no-op — verified by reading back the PRAGMA on a fresh
connection (it already reports 5000ms without our PRAGMA).

Concurrent stress test (50 checkpoint writes + 20 event batches + 50
thread_meta updates on the same deerflow.db) still completes with zero
errors and 200/200 rows after removing the explicit PRAGMA.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(journal): unwrap Command tool results in on_tool_end

Tools that update graph state (e.g. ``present_files``) return
``Command(update={'messages': [ToolMessage(...)], 'artifacts': [...]})``.
LangGraph later unwraps the inner ``ToolMessage`` into checkpoint state,
but ``RunJournal.on_tool_end`` was receiving the ``Command`` object
directly via the LangChain callback chain and storing
``str(Command(update={...}))`` as the tool_result content.

This produced a visible divergence between the event-store and the
checkpoint for any thread that used a Command-returning tool, blocking
the event-store-backed history fix in the follow-up commit. Concrete
example from thread ``6d30913e-dcd4-41c8-8941-f66c716cf359`` (seq=48):
checkpoint had ``'Successfully presented files'`` while event_store
stored the full Command repr.

The fix detects ``Command`` in ``on_tool_end``, extracts the first
``ToolMessage`` from ``update['messages']``, and lets the existing
ToolMessage branch handle the ``model_dump()`` path. Legacy rows still
containing the Command repr are separately cleaned up by the history
helper in the follow-up commit.

Tests:
- ``test_tool_end_unwraps_command_with_inner_tool_message`` — unit test
  of the unwrap branch with a constructed Command
- ``test_tool_invoke_end_to_end_unwraps_command`` — end-to-end via
  ``CallbackManager`` + ``tool.invoke`` to exercise the real LangChain
  dispatch path that production uses, matching the repro shape from
  ``present_files``
- Counter-proof: temporarily reverted the patch, both tests failed with
  the exact ``Command(update={...})`` repr that was stored in the
  production SQLite row at seq=48, confirming LangChain does pass the
  ``Command`` through callbacks (the unwrap is load-bearing)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(threads): load history messages from event store, immune to summarize

``get_thread_history`` and ``get_thread_state`` in Gateway mode read
messages from ``checkpoint.channel_values["messages"]``. After
SummarizationMiddleware runs mid-run, that list is rewritten in-place:
pre-summarize messages are dropped and a synthetic summary-as-human
message takes position 0. The frontend then renders a chat history that
starts with ``"Here is a summary of the conversation to date:..."``
instead of the user's original query, and all earlier turns are gone.

The event store (``RunEventStore``) is append-only and never rewritten,
so it retains the full transcript. This commit adds a helper
``_get_event_store_messages`` that loads the event store's message
stream and overrides ``values["messages"]`` in both endpoints; the
checkpoint fallback kicks in only when the event store is unavailable.

Behavior contract of the helper:

- **Full pagination.** ``list_messages`` returns the newest ``limit``
  records when no cursor is given, so a fixed limit silently drops
  older messages on long threads. The helper sizes the read from
  ``count_messages()`` and pages forward with ``after_seq`` cursors.
- **Copy-on-read.** Each content dict is copied before ``id`` is
  patched so the live store object (``MemoryRunEventStore`` returns
  references) is never mutated.
- **Stable ids.** Messages with ``id=None`` (human + tool_result,
  which don't receive an id until checkpoint persistence) get a
  deterministic ``uuid5(NAMESPACE_URL, f"{thread_id}:{seq}")`` so
  React keys stay stable across requests. AI messages keep their
  LLM-assigned ``lc_run--*`` ids.
- **Legacy ``Command`` repr sanitization.** Rows captured before the
  ``journal.py`` ``on_tool_end`` fix (previous commit) stored
  ``str(Command(update={'messages': [ToolMessage(content='X', ...)]}))``
  as the tool_result content. ``_sanitize_legacy_command_repr``
  regex-extracts the inner text so old threads render cleanly.
- **Inline feedback.** When loading the stream, the helper also pulls
  ``feedback_repo.list_by_thread_grouped`` and attaches ``run_id`` to
  every message plus ``feedback`` to the final ``ai_message`` of each
  run. This removes the frontend's need to fetch a second endpoint
  and positional-index-map its way back to the right run. When the
  feedback subsystem is unavailable, the ``feedback`` field is left
  absent entirely so the frontend hides the button rather than
  rendering it over a broken write path.
- **User context.** ``DbRunEventStore`` is user-scoped by default via
  ``resolve_user_id(AUTO)``. The helper relies on the ``@require_permission``
  decorator having populated the user contextvar on both callers; the
  docstring documents this dependency explicitly so nobody wires it
  into a CLI or migration script without passing ``user_id=None``.

Real data verification against thread
``6d30913e-dcd4-41c8-8941-f66c716cf359``: checkpoint showed 12 messages
(summarize-corrupted), event store had 16. The original human message
``"最新伊美局势"`` was preserved as seq=1 in the event store and
correctly restored to position 0 in the helper output. Helper output
for AI messages was byte-identical to checkpoint for every overlapping
message; only tool_result ids differed (patched to uuid5) and the
legacy Command repr at seq=48 was sanitized.

Tests:
- ``test_thread_state_event_store.py`` — 18 tests covering
  ``_sanitize_legacy_command_repr`` (passthrough, single/double-quote
  extraction, unparseable fallback), helper happy path (all message
  types, stable uuid5, store non-mutation), multi-page pagination,
  summarize regression (recovers pre-summarize messages), feedback
  attachment (per-run, multi-run threads, repo failure graceful),
  and dependency failure fallback to ``None``.

Docs:
- ``docs/superpowers/plans/2026-04-10-event-store-history.md`` — the
  implementation plan this commit realizes, with Task 1 revised after
  the evaluation findings (pagination, copy-on-read, Command wrap
  already landed in journal.py, frontend feedback pagination in the
  follow-up commit, Standard-mode follow-up noted).
- ``docs/superpowers/specs/2026-04-11-runjournal-history-evaluation.md``
  — the Claude + second-opinion evaluation document that drove the
  plan revisions (pagination bug, dict-mutation bug, feedback hidden
  bug, Command bug).
- ``docs/superpowers/specs/2026-04-11-summarize-marker-design.md`` —
  design for a follow-up PR that visually marks summarize events in
  history, based on a verified ``adispatch_custom_event`` experiment
  (``trace=False`` middleware nodes can still forward the Pregel task
  config via explicit signature injection).

Scope: Gateway mode only (``make dev-pro``). Standard mode
(``make dev``) hits LangGraph Server directly and bypasses these
endpoints; the summarize symptom is still present there and is
tracked as a separate follow-up in the plan.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* refactor(feedback): inline feedback on history and drop positional mapping

The old ``useThreadFeedback`` hook loaded ``GET /api/threads/{id}/messages?limit=200``
and built two parallel lookup tables: ``runIdByAiIndex`` (an ordinal array of
run_ids for every ``ai_message``-typed event) and ``feedbackByRunId``. The render
loop in ``message-list.tsx`` walked the AI messages in order, incrementing
``aiMessageIndex`` on each non-human message, and used that ordinal to look up
the run_id and feedback.

This shape had three latent bugs we could observe on real threads:

1. **Fetch was capped at 200 messages.** Long or tool-heavy threads silently
   dropped earlier entries from the map, so feedback buttons could be missing
   on messages they should own.
2. **Ordinal mismatch.** The render loop counted every non-human message
   (including each intermediate ``ai_tool_call``), but ``runIdByAiIndex`` only
   pushed entries for ``event_type == "ai_message"``. A run with 3 tool_calls
   + 1 final AI message would push 1 entry while the render consumed 4
   positions, so buttons mapped to the wrong positions across multi-run
   threads.
3. **Two parallel data paths.** The ``/history`` render path and the
   ``/messages`` feedback-lookup path could drift in-between an
   ``invalidateQueries`` call and the next refetch, producing transient
   mismaps.

The previous commit moved the authoritative message source for history to
the event store and added ``run_id`` + ``feedback`` inline on each message
dict returned by ``_get_event_store_messages``. This commit aligns the
frontend with that contract:

- **Delete** ``useThreadFeedback``, ``ThreadFeedbackData``,
  ``runIdByAiIndex``, ``feedbackByRunId``, and ``fetchAllThreadMessages``.
- **Introduce** ``useThreadMessageEnrichment`` that fetches
  ``POST /history?limit=1`` once, indexes the returned messages by
  ``message.id`` into a ``Map<id, {run_id, feedback?}>``, and invalidates
  on stream completion (``onFinish`` in ``useThreadStream``). Keying by
  ``message.id`` is stable across runs, tool_call chains, and summarize.
- **Simplify** ``message-list.tsx`` to drop the ``aiMessageIndex``
  counter and read ``enrichment?.get(msg.id)`` at each render step.
- **Rewire** ``message-list-item.tsx`` so the feedback button renders
  when ``feedback !== undefined`` rather than when the message happens
  to be non-human. ``feedback`` is ``undefined`` for non-eligible
  messages (humans, non-final AI, tools), ``null`` for the final
  ai_message of an unrated run, and a ``FeedbackData`` object once
  rated — cleanly distinguishing "not eligible" from "eligible but
  unrated".

``/api/threads/{id}/messages`` is kept as a debug/export surface; no
frontend code calls it anymore but the backend router is untouched.

Validation:
- ``pnpm check`` clean (0 errors, 1 pre-existing unrelated warning)
- Live test on thread ``3d5dea4a`` after gateway restart confirmed the
  original user query is restored to position 0 and the feedback
  button behaves correctly on the final AI message.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(rebase): remove duplicate definitions and update stale module paths

Rebase left duplicate function blocks in worker.py (triple human_message
write causing 3x user messages in /history), deps.py, and prompt.py.
Also update checkpointer imports from the old deerflow.agents.checkpointer
path to deerflow.runtime.checkpointer, and clean up orphaned feedback
props in the frontend message components.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(rebase): restore FeedbackButtons component and enrichment lost during rebase

The FeedbackButtons component (defined inline in message-list-item.tsx)
was introduced in commit 95df8d13 but lost during rebase. The previous
rebase cleanup commit incorrectly removed the feedback/runId props and
enrichment hook as "orphaned code" instead of restoring the missing
component. This commit restores:

- FeedbackButtons component with thumbs up/down toggle and optimistic state
- FeedbackData/upsertFeedback/deleteFeedback imports
- feedback and runId props on MessageListItem
- useThreadMessageEnrichment hook and entry lookup in message-list.tsx

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(user-context): add DEFAULT_USER_ID and get_effective_user_id helper

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(paths): add user-aware path methods with optional user_id parameter

Add _validate_user_id(), user_dir(), user_memory_file(), user_agent_memory_file()
and optional keyword-only user_id parameter to all thread-related path methods.
When user_id is provided, paths resolve under users/{user_id}/threads/{thread_id}/;
when omitted, legacy layout is preserved for backward compatibility.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(memory): add user_id to MemoryStorage interface for per-user isolation

Thread user_id through MemoryStorage.load/reload/save abstract methods and
FileMemoryStorage, re-keying the in-memory cache from bare agent_name to a
(user_id, agent_name) tuple to prevent cross-user cache collisions.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(memory): thread user_id through memory updater layer

Add `user_id` keyword-only parameter to all public updater functions
(_save_memory_to_file, get_memory_data, reload_memory_data, import_memory_data,
clear_memory_data, create/delete/update_memory_fact) and regular keyword param
to MemoryUpdater.update_memory + update_memory_from_conversation, propagating
it to every storage load/save/reload call.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(memory): capture user_id at enqueue time for async-safe thread isolation

Add user_id field to ConversationContext and MemoryUpdateQueue.add() so the
user identity is stored explicitly at request time, before threading.Timer
fires on a different thread where ContextVar values do not propagate.
MemoryMiddleware.after_agent() now calls get_effective_user_id() at enqueue
time and passes the value through to updater.update_memory().

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(isolation): wire user_id through all Paths and memory callsites

Pass user_id=get_effective_user_id() at every callsite that invokes
Paths methods or memory functions, enabling per-user filesystem isolation
throughout the harness and app layers.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(migration): add idempotent script for per-user data migration

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* docs: update CLAUDE.md and config docs for per-user isolation

* feat(events): add pagination to list_messages_by_run on all store backends

Replicates the existing before_seq/after_seq/limit cursor-pagination pattern
from list_messages onto list_messages_by_run across the abstract interface,
MemoryRunEventStore, JsonlRunEventStore, and DbRunEventStore.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(api): add GET /api/runs/{run_id}/messages with cursor pagination

New endpoint resolves thread_id from the run record and delegates to
RunEventStore.list_messages_by_run for cursor-based pagination.
Ownership is enforced implicitly via RunStore.get() user filtering.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(api): add GET /api/runs/{run_id}/feedback

Delegates to FeedbackRepository.list_by_run via the existing _resolve_run
helper; includes tests for success, 404, empty list, and 503 (no DB).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(api): retrofit cursor pagination onto GET /threads/{tid}/runs/{rid}/messages

Replace bare list[dict] response with {data: [...], has_more: bool} envelope,
forwarding limit/before_seq/after_seq query params to the event store.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* docs: add run-level API endpoints to CLAUDE.md routers table

* refactor(threads): remove event-store message loader and feedback from state/history endpoints

State and history endpoints now return messages purely from the
checkpointer's channel_values. The _get_event_store_messages helper
(which loaded the full event-store transcript with feedback attached)
is removed along with its tests. Frontend will use the dedicated
GET /api/runs/{run_id}/messages and /feedback endpoints instead.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(persistence): add unified persistence layer with event store, token tracking, and feedback (#1930)

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

* feat(auth): release-validation pass for 2.0-rc — 12 blockers + simplify follow-ups (#2008)

* feat(auth): introduce backend auth module

Port RFC-001 authentication core from PR #1728:
- JWT token handling (create_access_token, decode_token, TokenPayload)
- Password hashing (bcrypt) with verify_password
- SQLite UserRepository with base interface
- Provider Factory pattern (LocalAuthProvider)
- CLI reset_admin tool
- Auth-specific errors (AuthErrorCode, TokenError, AuthErrorResponse)

Deps:
- bcrypt>=4.0.0
- pyjwt>=2.9.0
- email-validator>=2.0.0
- backend/uv.toml pins public PyPI index

Tests: 12 pure unit tests (test_auth_config.py, test_auth_errors.py).

Scope note: authz.py, test_auth.py, and test_auth_type_system.py are
deferred to commit 2 because they depend on middleware and deps wiring
that is not yet in place. Commit 1 stays "pure new files only" as the
spec mandates.

* feat(auth): wire auth end-to-end (middleware + frontend replacement)

Backend:
- Port auth_middleware, csrf_middleware, langgraph_auth, routers/auth
- Port authz decorator (owner_filter_key defaults to 'owner_id')
- Merge app.py: register AuthMiddleware + CSRFMiddleware + CORS, add
  _ensure_admin_user lifespan hook, _migrate_orphaned_threads helper,
  register auth router
- Merge deps.py: add get_local_provider, get_current_user_from_request,
  get_optional_user_from_request; keep get_current_user as thin str|None
  adapter for feedback router
- langgraph.json: add auth path pointing to langgraph_auth.py:auth
- Rename metadata['user_id'] -> metadata['owner_id'] in langgraph_auth
  (both metadata write and LangGraph filter dict) + test fixtures

Frontend:
- Delete better-auth library and api catch-all route
- Remove better-auth npm dependency and env vars (BETTER_AUTH_SECRET,
  BETTER_AUTH_GITHUB_*) from env.js
- Port frontend/src/core/auth/* (AuthProvider, gateway-config,
  proxy-policy, server-side getServerSideUser, types)
- Port frontend/src/core/api/fetcher.ts
- Port (auth)/layout, (auth)/login, (auth)/setup pages
- Rewrite workspace/layout.tsx as server component that calls
  getServerSideUser and wraps in AuthProvider
- Port workspace/workspace-content.tsx for the client-side sidebar logic

Tests:
- Port 5 auth test files (test_auth, test_auth_middleware,
  test_auth_type_system, test_ensure_admin, test_langgraph_auth)
- 176 auth tests PASS

After this commit: login/logout/registration flow works, but persistence
layer does not yet filter by owner_id. Commit 4 closes that gap.

* feat(auth): account settings page + i18n

- Port account-settings-page.tsx (change password, change email, logout)
- Wire into settings-dialog.tsx as new "account" section with UserIcon,
  rendered first in the section list
- Add i18n keys:
  - en-US/zh-CN: settings.sections.account ("Account" / "账号")
  - en-US/zh-CN: button.logout ("Log out" / "退出登录")
  - types.ts: matching type declarations

* feat(auth): enforce owner_id across 2.0-rc persistence layer

Add request-scoped contextvar-based owner filtering to threads_meta,
runs, run_events, and feedback repositories. Router code is unchanged
— isolation is enforced at the storage layer so that any caller that
forgets to pass owner_id still gets filtered results, and new routes
cannot accidentally leak data.

Core infrastructure
-------------------
- deerflow/runtime/user_context.py (new):
  - ContextVar[CurrentUser | None] with default None
  - runtime_checkable CurrentUser Protocol (structural subtype with .id)
  - set/reset/get/require helpers
  - AUTO sentinel + resolve_owner_id(value, method_name) for sentinel
    three-state resolution: AUTO reads contextvar, explicit str
    overrides, explicit None bypasses the filter (for migration/CLI)

Repository changes
------------------
- ThreadMetaRepository: create/get/search/update_*/delete gain
  owner_id=AUTO kwarg; read paths filter by owner, writes stamp it,
  mutations check ownership before applying
- RunRepository: put/get/list_by_thread/delete gain owner_id=AUTO kwarg
- FeedbackRepository: create/get/list_by_run/list_by_thread/delete
  gain owner_id=AUTO kwarg
- DbRunEventStore: list_messages/list_events/list_messages_by_run/
  count_messages/delete_by_thread/delete_by_run gain owner_id=AUTO
  kwarg. Write paths (put/put_batch) read contextvar softly: when a
  request-scoped user is available, owner_id is stamped; background
  worker writes without a user context pass None which is valid
  (orphan row to be bound by migration)

Schema
------
- persistence/models/run_event.py: RunEventRow.owner_id = Mapped[
  str | None] = mapped_column(String(64), nullable=True, index=True)
- No alembic migration needed: 2.0 ships fresh, Base.metadata.create_all
  picks up the new column automatically

Middleware
----------
- auth_middleware.py: after cookie check, call get_optional_user_from_
  request to load the real User, stamp it into request.state.user AND
  the contextvar via set_current_user, reset in a try/finally. Public
  paths and unauthenticated requests continue without contextvar, and
  @require_auth handles the strict 401 path

Test infrastructure
-------------------
- tests/conftest.py: @pytest.fixture(autouse=True) _auto_user_context
  sets a default SimpleNamespace(id="test-user-autouse") on every test
  unless marked @pytest.mark.no_auto_user. Keeps existing 20+
  persistence tests passing without modification
- pyproject.toml [tool.pytest.ini_options]: register no_auto_user
  marker so pytest does not emit warnings for opt-out tests
- tests/test_user_context.py: 6 tests covering three-state semantics,
  Protocol duck typing, and require/optional APIs
- tests/test_thread_meta_repo.py: one test updated to pass owner_id=
  None explicitly where it was previously relying on the old default

Test results
------------
- test_user_context.py: 6 passed
- test_auth*.py + test_langgraph_auth.py + test_ensure_admin.py: 127
- test_run_event_store / test_run_repository / test_thread_meta_repo
  / test_feedback: 92 passed
- Full backend suite: 1905 passed, 2 failed (both @requires_llm flaky
  integration tests unrelated to auth), 1 skipped

* feat(auth): extend orphan migration to 2.0-rc persistence tables

_ensure_admin_user now runs a three-step pipeline on every boot:

  Step 1 (fatal):     admin user exists / is created / password is reset
  Step 2 (non-fatal): LangGraph store orphan threads → admin
  Step 3 (non-fatal): SQL persistence tables → admin
    - threads_meta
    - runs
    - run_events
    - feedback

Each step is idempotent. The fatal/non-fatal split mirrors PR #1728's
original philosophy: admin creation failure blocks startup (the system
is unusable without an admin), whereas migration failures log a warning
and let the service proceed (a partial migration is recoverable; a
missing admin is not).

Key helpers
-----------
- _iter_store_items(store, namespace, *, page_size=500):
  async generator that cursor-paginates across LangGraph store pages.
  Fixes PR #1728's hardcoded limit=1000 bug that would silently lose
  orphans beyond the first page.

- _migrate_orphaned_threads(store, admin_user_id):
  Rewritten to use _iter_store_items. Returns the migrated count so the
  caller can log it; raises only on unhandled exceptions.

- _migrate_orphan_sql_tables(admin_user_id):
  Imports the 4 ORM models lazily, grabs the shared session factory,
  runs one UPDATE per table in a single transaction, commits once.
  No-op when no persistence backend is configured (in-memory dev).

Tests: test_ensure_admin.py (8 passed)

* test(auth): port AUTH test plan docs + lint/format pass

- Port backend/docs/AUTH_TEST_PLAN.md and AUTH_UPGRADE.md from PR #1728
- Rename metadata.user_id → metadata.owner_id in AUTH_TEST_PLAN.md
  (4 occurrences from the original PR doc)
- ruff auto-fix UP037 in sentinel type annotations: drop quotes around
  "str | None | _AutoSentinel" now that from __future__ import
  annotations makes them implicit string forms
- ruff format: 2 files (app/gateway/app.py, runtime/user_context.py)

Note on test coverage additions:
- conftest.py autouse fixture was already added in commit 4 (had to
  be co-located with the repository changes to keep pre-existing
  persistence tests passing)
- cross-user isolation E2E tests (test_owner_isolation.py) deferred
  — enforcement is already proven by the 98-test repository suite
  via the autouse fixture + explicit _AUTO sentinel exercises
- New test cases (TC-API-17..20, TC-ATK-13, TC-MIG-01..07) listed
  in AUTH_TEST_PLAN.md are deferred to a follow-up PR — they are
  manual-QA test cases rather than pytest code, and the spec-level
  coverage is already met by test_user_context.py + the 98-test
  repository suite.

Final test results:
- Auth suite (test_auth*, test_langgraph_auth, test_ensure_admin,
  test_user_context): 186 passed
- Persistence suite (test_run_event_store, test_run_repository,
  test_thread_meta_repo, test_feedback): 98 passed
- Lint: ruff check + ruff format both clean

* test(auth): add cross-user isolation test suite

10 tests exercising the storage-layer owner filter by manually
switching the user_context contextvar between two users. Verifies
the safety invariant:

  After a repository write with owner_id=A, a subsequent read with
  owner_id=B must not return the row, and vice versa.

Covers all 4 tables that own user-scoped data:

TC-API-17  threads_meta  — read, search, update, delete cross-user
TC-API-18  runs          — get, list_by_thread, delete cross-user
TC-API-19  run_events    — list_messages, list_events, count_messages,
                           delete_by_thread (CRITICAL: raw conversation
                           content leak vector)
TC-API-20  feedback      — get, list_by_run, delete cross-user

Plus two meta-tests verifying the sentinel pattern itself:
- AUTO + unset contextvar raises RuntimeError
- explicit owner_id=None bypasses the filter (migration escape hatch)

Architecture note
-----------------
These tests bypass the HTTP layer by design. The full chain
(cookie → middleware → contextvar → repository) is covered piecewise:

- test_auth_middleware.py: middleware sets contextvar from cookies
- test_owner_isolation.py: repositories enforce isolation when
  contextvar is set to different users

Together they prove the end-to-end safety property without the
ceremony of spinning up a full TestClient + in-memory DB for every
router endpoint.

Tests pass: 231 (full auth + persistence + isolation suite)
Lint: clean

* refactor(auth): migrate user repository to SQLAlchemy ORM

Move the users table into the shared persistence engine so auth
matches the pattern of threads_meta, runs, run_events, and feedback —
one engine, one session factory, one schema init codepath.

New files
---------
- persistence/user/__init__.py, persistence/user/model.py: UserRow
  ORM class with partial unique index on (oauth_provider, oauth_id)
- Registered in persistence/models/__init__.py so
  Base.metadata.create_all() picks it up

Modified
--------
- auth/repositories/sqlite.py: rewritten as async SQLAlchemy,
  identical constructor pattern to the other four repositories
  (def __init__(self, session_factory) + self._sf = session_factory)
- auth/config.py: drop users_db_path field — storage is configured
  through config.database like every other table
- deps.py/get_local_provider: construct SQLiteUserRepository with
  the shared session factory, fail fast if engine is not initialised
- tests/test_auth.py: rewrite test_sqlite_round_trip_new_fields to
  use the shared engine (init_engine + close_engine in a tempdir)
- tests/test_auth_type_system.py: add per-test autouse fixture that
  spins up a scratch engine and resets deps._cached_* singletons

* refactor(auth): remove SQL orphan migration (unused in supported scenarios)

The _migrate_orphan_sql_tables helper existed to bind NULL owner_id
rows in threads_meta, runs, run_events, and feedback to the admin on
first boot. But in every supported upgrade path, it's a no-op:

  1. Fresh install: create_all builds fresh tables, no legacy rows
  2. No-auth → with-auth (no existing persistence DB): persistence
     tables are created fresh by create_all, no legacy rows
  3. No-auth → with-auth (has existing persistence DB from #1930):
     NOT a supported upgrade path — "有 DB 到有 DB" schema evolution
     is out of scope; users wipe DB or run manual ALTER

So the SQL orphan migration never has anything to do in the
supported matrix. Delete the function, simplify _ensure_admin_user
from a 3-step pipeline to a 2-step one (admin creation + LangGraph
store orphan migration only).

LangGraph store orphan migration stays: it serves the real
"no-auth → with-auth" upgrade path where a user's existing LangGraph
thread metadata has no owner_id field and needs to be stamped with
the newly-created admin's id.

Tests: 284 passed (auth + persistence + isolation)
Lint: clean

* security(auth): write initial admin password to 0600 file instead of logs

CodeQL py/clear-text-logging-sensitive-data flagged 3 call sites that
logged the auto-generated admin password to stdout via logger.info().
Production log aggregators (ELK/Splunk/etc) would have captured those
cleartext secrets. Replace with a shared helper that writes to
.deer-flow/admin_initial_credentials.txt with mode 0600, and log only
the path.

New file
--------
- app/gateway/auth/credential_file.py: write_initial_credentials()
  helper. Takes email, password, and a "initial"/"reset" label.
  Creates .deer-flow/ if missing, writes a header comment plus the
  email+password, chmods 0o600, returns the absolute Path.

Modified
--------
- app/gateway/app.py: both _ensure_admin_user paths (fresh creation
  + needs_setup password reset) now write to file and log the path
- app/gateway/auth/reset_admin.py: rewritten to use the shared ORM
  repo (SQLiteUserRepository with session_factory) and the
  credential_file helper. The previous implementation was broken
  after the earlier ORM refactor — it still imported _get_users_conn
  and constructed SQLiteUserRepository() without a session factory.

No tests changed — the three password-log sites are all exercised
via existing test_ensure_admin.py which checks that startup
succeeds, not that a specific string appears in logs.

CodeQL alerts 272, 283, 284: all resolved.

* security(auth): strict JWT validation in middleware (fix junk cookie bypass)

AUTH_TEST_PLAN test 7.5.8 expects junk cookies to be rejected with
401. The previous middleware behaviour was "presence-only": check
that some access_token cookie exists, then pass through. In
combination with my Task-12 decision to skip @require_auth
decorators on routes, this created a gap where a request with any
cookie-shaped string (e.g. access_token=not-a-jwt) would bypass
authentication on routes that do not touch the repository
(/api/models, /api/mcp/config, /api/memory, /api/skills, …).

Fix: middleware now calls get_current_user_from_request() strictly
and catches the resulting HTTPException to render a 401 with the
proper fine-grained error code (token_invalid, token_expired,
user_not_found, …). On success it stamps request.state.user and
the contextvar so repository-layer owner filters work downstream.

The 4 old "_with_cookie_passes" tests in test_auth_middleware.py
were written for the presence-only behaviour; they asserted that
a junk cookie would make the handler return 200. They are renamed
to "_with_junk_cookie_rejected" and their assertions flipped to
401. The negative path (no cookie → 401 not_authenticated)
is unchanged.

Verified:
  no cookie       → 401 not_authenticated
  junk cookie     → 401 token_invalid     (the fixed bug)
  expired cookie  → 401 token_expired

Tests: 284 passed (auth + persistence + isolation)
Lint: clean

* security(auth): wire @require_permission(owner_check=True) on isolation routes

Apply the require_permission decorator to all 28 routes that take a
{thread_id} path parameter. Combined with the strict middleware
(previous commit), this gives the double-layer protection that
AUTH_TEST_PLAN test 7.5.9 documents:

  Layer 1 (AuthMiddleware): cookie + JWT validation, rejects junk
                            cookies and stamps request.state.user
  Layer 2 (@require_permission with owner_check=True): per-resource
                            ownership verification via
                            ThreadMetaStore.check_access — returns
                            404 if a different user owns the thread

The decorator's owner_check branch is rewritten to use the SQL
thread_meta_repo (the 2.0-rc persistence layer) instead of the
LangGraph store path that PR #1728 used (_store_get / get_store
in routers/threads.py). The inject_record convenience is dropped
— no caller in 2.0 needs the LangGraph blob, and the SQL repo has
a different shape.

Routes decorated (28 total):
- threads.py: delete, patch, get, get-state, post-state, post-history
- thread_runs.py: post-runs, post-runs-stream, post-runs-wait,
  list_runs, get_run, cancel_run, join_run, stream_existing_run,
  list_thread_messages, list_run_messages, list_run_events,
  thread_token_usage
- feedback.py: create, list, stats, delete
- uploads.py: upload (added Request param), list, delete
- artifacts.py: get_artifact
- suggestions.py: generate (renamed body parameter to avoid
  conflict with FastAPI Request)

Test fixes:
- test_suggestions_router.py: bypass the decorator via __wrapped__
  (the unit tests cover parsing logic, not auth — no point spinning
  up a thread_meta_repo just to test JSON unwrapping)
- test_auth_middleware.py 4 fake-cookie tests: already updated in
  the previous commit (745bf432)

Tests: 293 passed (auth + persistence + isolation + suggestions)
Lint: clean

* security(auth): defense-in-depth fixes from release validation pass

Eight findings caught while running the AUTH_TEST_PLAN end-to-end against
the deployed sg_dev stack. Each is a pre-condition for shipping
release/2.0-rc that the previous PRs missed.

Backend hardening
- routers/auth.py: rate limiter X-Real-IP now requires AUTH_TRUSTED_PROXIES
  whitelist (CIDR/IP allowlist). Without nginx in front, the previous code
  honored arbitrary X-Real-IP, letting an attacker rotate the header to
  fully bypass the per-IP login lockout.
- routers/auth.py: 36-entry common-password blocklist via Pydantic
  field_validator on RegisterRequest + ChangePasswordRequest. The shared
  _validate_strong_password helper keeps the constraint in one place.
- routers/threads.py: ThreadCreateRequest + ThreadPatchRequest strip
  server-reserved metadata keys (owner_id, user_id) via Pydantic
  field_validator so a forged value can never round-trip back to other
  clients reading the same thread. The actual ownership invariant stays
  on the threads_meta row; this closes the metadata-blob echo gap.
- authz.py + thread_meta/sql.py: require_permission gains a require_existing
  flag plumbed through check_access(require_existing=True). Destructive
  routes (DELETE/PATCH/state-update/runs/feedback) now treat a missing
  thread_meta row as 404 instead of "untracked legacy thread, allow",
  closing the cross-user delete-idempotence gap where any user could
  successfully DELETE another user's deleted thread.
- repositories/sqlite.py + base.py: update_user raises UserNotFoundError
  on a vanished row instead of silently returning the input. Concurrent
  delete during password reset can no longer look like a successful update.
- runtime/user_context.py: resolve_owner_id() coerces User.id (UUID) to
  str at the contextvar boundary so SQLAlchemy String(64) columns can
  bind it. The whole 2.0-rc isolation pipeline was previously broken
  end-to-end (POST /api/threads → 500 "type 'UUID' is not supported").
- persistence/engine.py: SQLAlchemy listener enables PRAGMA journal_mode=WAL,
  synchronous=NORMAL, foreign_keys=ON on every new SQLite connection.
  TC-UPG-06 in the test plan expects WAL; previous code shipped with the
  default 'delete' journal.
- auth_middleware.py: stamp request.state.auth = AuthContext(...) so
  @require_permission's short-circuit fires; previously every isolation
  request did a duplicate JWT decode + users SELECT. Also unifies the
  401 payload through AuthErrorResponse(...).model_dump().
- app.py: _ensure_admin_user restructure removes the noqa F821 scoping
  bug where 'password' was referenced outside the branch that defined it.
  New _announce_credentials helper absorbs the duplicate log block in
  the fresh-admin and reset-admin branches.

* fix(frontend+nginx): rollout CSRF on every state-changing client path

The frontend was 100% broken in gateway-pro mode for any user trying to
open a specific chat thread. Three cumulative bugs each silently
masked the next.

LangGraph SDK CSRF gap (api-client.ts)
- The Client constructor took only apiUrl, no defaultHeaders, no fetch
  interceptor. The SDK's internal fetch never sent X-CSRF-Token, so
  every state-changing /api/langgraph-compat/* call (runs/stream,
  threads/search, threads/{tid}/history, ...) hit CSRFMiddleware and
  got 403 before reaching the auth check. UI symptom: empty thread page
  with no error message; the SPA's hooks swallowed the rejection.
- Fix: pass an onRequest hook that injects X-CSRF-Token from the
  csrf_token cookie per request. Reading the cookie per call (not at
  construction time) handles login / logout / password-change cookie
  rotation transparently. The SDK's prepareFetchOptions calls
  onRequest for both regular requests AND streaming/SSE/reconnect, so
  the same hook covers runs.stream and runs.joinStream.

Raw fetch CSRF gap (7 files)
- Audit: 11 frontend fetch sites, only 2 included CSRF (login/setup +
  account-settings change-password). The other 7 routed through raw
  fetch() with no header — suggestions, memory, agents, mcp, skills,
  uploads, and the local thread cleanup hook all 403'd silently.
- Fix: enhance fetcher.ts:fetchWithAuth to auto-inject X-CSRF-Token on
  POST/PUT/DELETE/PATCH from a single shared readCsrfCookie() helper.
  Convert all 7 raw fetch() callers to fetchWithAuth so the contract
  is centrally enforced. api-client.ts and fetcher.ts share
  readCsrfCookie + STATE_CHANGING_METHODS to avoid drift.

nginx routing + buffering (nginx.local.conf)
- The auth feature shipped without updating the nginx config: per-API
  explicit location blocks but no /api/v1/auth/, /api/feedback, /api/runs.
  The frontend's client-side fetches to /api/v1/auth/login/local 404'd
  from the Next.js side because nginx routed /api/* to the frontend.
- Fix: add catch-all `location /api/` that proxies to the gateway.
  nginx longest-prefix matching keeps the explicit blocks (/api/models,
  /api/threads regex, /api/langgraph/, ...) winning for their paths.
- Fix: disable proxy_buffering + proxy_request_buffering for the
  frontend `location /` block. Without it, nginx tries to spool large
  Next.js chunks into /var/lib/nginx/proxy (root-owned) and fails with
  Permission denied → ERR_INCOMPLETE_CHUNKED_ENCODING → ChunkLoadError.

* test(auth): release-validation test infra and new coverage

Test fixtures and unit tests added during the validation pass.

Router test helpers (NEW: tests/_router_auth_helpers.py)
- make_authed_test_app(): builds a FastAPI test app with a stub
  middleware that stamps request.state.user + request.state.auth and a
  permissive thread_meta_repo mock. TestClient-based router tests
  (test_artifacts_router, test_threads_router) use it instead of bare
  FastAPI() so the new @require_permission(owner_check=True) decorators
  short-circuit cleanly.
- call_unwrapped(): walks the __wrapped__ chain to invoke the underlying
  handler without going through the authz wrappers. Direct-call tests
  (test_uploads_router) use it. Typed with ParamSpec so the wrapped
  signature flows through.

Backend test additions
- test_auth.py: 7 tests for the new _get_client_ip trust model (no
  proxy / trusted proxy / untrusted peer / XFF rejection / invalid
  CIDR / no client). 5 tests for the password blocklist (literal,
  case-insensitive, strong password accepted, change-password binding,
  short-password length-check still fires before blocklist).
  test_update_user_raises_when_row_concurrently_deleted: closes a
  shipped-without-coverage gap on the new UserNotFoundError contract.
- test_thread_meta_repo.py: 4 tests for check_access(require_existing=True)
  — strict missing-row denial, strict owner match, strict owner mismatch,
  strict null-owner still allowed (shared rows survive the tightening).
- test_ensure_admin.py: 3 tests for _migrate_orphaned_threads /
  _iter_store_items pagination, covering the TC-UPG-02 upgrade story
  end-to-end via mock store. Closes the gap where the cursor pagination
  was untested even though the previous PR rewrote it.
- test_threads_router.py: 5 tests for _strip_reserved_metadata
  (owner_id removal, user_id removal, safe-keys passthrough, empty
  input, both-stripped).
- test_auth_type_system.py: replace "password123" fixtures with
  Tr0ub4dor3a / AnotherStr0ngPwd! so the new password blocklist
  doesn't reject the test data.

* docs(auth): refresh TC-DOCKER-05 + document Docker validation gap

- AUTH_TEST_PLAN.md TC-DOCKER-05: the previous expectation
  ("admin password visible in docker logs") was stale after the simplify
  pass that moved credentials to a 0600 file. The grep "Password:" check
  would have silently failed and given a false sense of coverage. New
  expectation matches the actual file-based path: 0600 file in
  DEER_FLOW_HOME, log shows the path (not the secret), reverse-grep
  asserts no leaked password in container logs.
- NEW: docs/AUTH_TEST_DOCKER_GAP.md documents the only un-executed
  block in the test plan (TC-DOCKER-01..06). Reason: sg_dev validation
  host has no Docker daemon installed. The doc maps each Docker case
  to an already-validated bare-metal equivalent (TC-1.1, TC-REENT-01,
  TC-API-02 etc.) so the gap is auditable, and includes pre-flight
  reproduction steps for whoever has Docker available.

---------

Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>

* fix(persistence): stream hang when run_events.backend=db

DbRunEventStore._user_id_from_context() returned user.id without
coercing it to str. User.id is a Pydantic UUID, and aiosqlite cannot
bind a raw UUID object to a VARCHAR column, so the INSERT for the
initial human_message event silently rolled back and raised out of
the worker task. Because that put() sat outside the worker's try
block, the finally-clause that publishes end-of-stream never ran
and the SSE stream hung forever.

jsonl mode was unaffected because json.dumps(default=str) coerces
UUID objects transparently.

Fixes:
- db.py: coerce user.id to str at the context-read boundary (matches
  what resolve_user_id already does for the other repositories)
- worker.py: move RunJournal init + human_message put inside the try
  block so any failure flows through the finally/publish_end path
  instead of hanging the subscriber

Defense-in-depth:
- engine.py: add PRAGMA busy_timeout=5000 so checkpointer and event
  store wait for each other on the shared deerflow.db file instead
  of failing immediately under write-lock contention
- journal.py: skip fire-and-forget _flush_sync when a previous flush
  task is still in flight, to avoid piling up concurrent put_batch
  writes on the same SQLAlchemy engine during streaming; flush() now
  waits for pending tasks before draining the buffer
- database_config.py: doc-only update clarifying WAL + busy_timeout
  keep the unified deerflow.db safe for both workloads

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* chore(persistence): drop redundant busy_timeout PRAGMA

Python's sqlite3 driver defaults to a 5-second busy timeout via the
``timeout`` kwarg of ``sqlite3.connect``, and aiosqlite + SQLAlchemy's
aiosqlite dialect inherit that default. Setting ``PRAGMA busy_timeout=5000``
explicitly was a no-op — verified by reading back the PRAGMA on a fresh
connection (it already reports 5000ms without our PRAGMA).

Concurrent stress test (50 checkpoint writes + 20 event batches + 50
thread_meta updates on the same deerflow.db) still completes with zero
errors and 200/200 rows after removing the explicit PRAGMA.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* fix(rebase): remove duplicate definitions and update stale module paths

Rebase left duplicate function blocks in worker.py (triple human_message
write causing 3x user messages in /history), deps.py, and prompt.py.
Also update checkpointer imports from the old deerflow.agents.checkpointer
path to deerflow.runtime.checkpointer, and clean up orphaned feedback
props in the frontend message components.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* feat(user-context): add DEFAULT_USER_ID and get_effective_user_id helper

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(paths): add user-aware path methods with optional user_id parameter

Add _validate_user_id(), user_dir(), user_memory_file(), user_agent_memory_file()
and optional keyword-only user_id parameter to all thread-related path methods.
When user_id is provided, paths resolve under users/{user_id}/threads/{thread_id}/;
when omitted, legacy layout is preserved for backward compatibility.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(memory): add user_id to MemoryStorage interface for per-user isolation

Thread user_id through MemoryStorage.load/reload/save abstract methods and
FileMemoryStorage, re-keying the in-memory cache from bare agent_name to a
(user_id, agent_name) tuple to prevent cross-user cache collisions.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(memory): thread user_id through memory updater layer

Add `user_id` keyword-only parameter to all public updater functions
(_save_memory_to_file, get_memory_data, reload_memory_data, import_memory_data,
clear_memory_data, create/delete/update_memory_fact) and regular keyword param
to MemoryUpdater.update_memory + update_memory_from_conversation, propagating
it to every storage load/save/reload call.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(memory): capture user_id at enqueue time for async-safe thread isolation

Add user_id field to ConversationContext and MemoryUpdateQueue.add() so the
user identity is stored explicitly at request time, before threading.Timer
fires on a different thread where ContextVar values do not propagate.
MemoryMiddleware.after_agent() now calls get_effective_user_id() at enqueue
time and passes the value through to updater.update_memory().

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(isolation): wire user_id through all Paths and memory callsites

Pass user_id=get_effective_user_id() at every callsite that invokes
Paths methods or memory functions, enabling per-user filesystem isolation
throughout the harness and app layers.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(migration): add idempotent script for per-user data migration

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* docs: update CLAUDE.md and config docs for per-user isolation

* feat(events): add pagination to list_messages_by_run on all store backends

Replicates the existing before_seq/after_seq/limit cursor-pagination pattern
from list_messages onto list_messages_by_run across the abstract interface,
MemoryRunEventStore, JsonlRunEventStore, and DbRunEventStore.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(api): add GET /api/runs/{run_id}/messages with cursor pagination

New endpoint resolves thread_id from the run record and delegates to
RunEventStore.list_messages_by_run for cursor-based pagination.
Ownership is enforced implicitly via RunStore.get() user filtering.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(api): add GET /api/runs/{run_id}/feedback

Delegates to FeedbackRepository.list_by_run via the existing _resolve_run
helper; includes tests for success, 404, empty list, and 503 (no DB).

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* feat(api): retrofit cursor pagination onto GET /threads/{tid}/runs/{rid}/messages

Replace bare list[dict] response with {data: [...], has_more: bool} envelope,
forwarding limit/before_seq/after_seq query params to the event store.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

* docs: add run-level API endpoints to CLAUDE.md routers table

* refactor(threads): remove event-store message loader and feedback from state/history endpoints

State and history endpoints now return messages purely from the
checkpointer's channel_values. The _get_event_store_messages helper
(which loaded the full event-store transcript with feedback attached)
is removed along with its tests. Frontend will use the dedicated
GET /api/runs/{run_id}/messages and /feedback endpoints instead.

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
Co-authored-by: greatmengqi <chenmengqi.0376@gmail.com>
Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>

- `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`
- `backend/packages/harness/deerflow/sandbox/tools.py`

## af8c0cfb 2026-04-28 DanielWalnut
fix(harness): constrain view_image to thread data paths (#2557)

* fix(harness): constrain view_image to thread data paths

Fixes #2530

* fix(harness): address view_image review findings

* style(harness): format view_image changes

* fix(harness): address view_image review comments

- `backend/packages/harness/deerflow/sandbox/tools.py`
  L639: """Resolve a /mnt/user-data virtual path and validate it stays in bounds."""

## f7dfb88a 2026-04-28 DanielWalnut
fix(aio-sandbox): redact env values in container logs (#2562)

* fix(aio-sandbox): redact env values in container logs

Fixes #2534

* fix(aio-sandbox): address env log review comments

- `backend/packages/harness/deerflow/community/aio_sandbox/local_backend.py`
  L91: """Return a Docker/Container command with environment values redacted."""

## 39c5da94 2026-04-28 DanielWalnut
fix(sandbox): prevent local custom mount symlink escapes (#2558)

* fix(sandbox): prevent local custom mount symlink escapes

Fixes #2506

* fix(sandbox): harden custom mount symlink handling

* fix(sandbox): format internal symlink directory listings

- `backend/packages/harness/deerflow/sandbox/local/list_dir.py`
- `backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`
  L342: # Reverse resolve local paths back to container paths and preserve
  L343: # list_dir's trailing "/" marker for directories.

## 6bd88fe1 2026-04-28 DanielWalnut
fix(sandbox): block host bash traversal escapes (#2560)

* fix(sandbox): block host bash traversal escapes

Fixes #2535

* fix(sandbox): harden local bash path guards

* fix(sandbox): avoid bash cd argument false positives

* Fix the lint error

Add function to resolve and validate user data path.

* Fix the lint error

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/sandbox/tools.py`
  L678: """Return True for URL tokens that should not be interpreted as paths."""
  L716: # The shell will reject malformed quoting later; keep validation
  L717: # best-effort instead of turning syntax errors into security messages.
  L737: # Check for MCP filesystem server allowed paths
  L746: # Allow skills container path (resolved by tools.py before passing to sandbox)
  L751: # Allow ACP workspace path (path-traversal check only)
  L756: # Allow custom mount container paths
  L826: """Conservatively reject relative path escapes missed by absolute-path scanning."""

## 74081a85 2026-04-30 Hinotobi
[security] fix(sandbox): bind local Docker ports to loopback (#2633)

* fix(sandbox): bind local Docker ports to loopback

* fix(sandbox): preserve IPv6 loopback Docker binds

* fix(sandbox): log Docker bind host selection

- `backend/packages/harness/deerflow/community/aio_sandbox/local_backend.py`
  L143: """Choose the host interface for legacy Docker ``-p`` sandbox publishing.
  L152: """

## 189b8240 2026-05-01 Willem Jiang
fix(sandbox): pass no_change_timeout to exec_command to prevent 120s premature termination (#2685)

* fix(sandbox): pass no_change_timeout to exec_command to prevent 120s premature termination

  The agent_sandbox library's shell API defaults no_change_timeout to 120
  seconds. When AioSandbox.execute_command() called exec_command() without
  this parameter, commands producing no output for 120s would return with
  NO_CHANGE_TIMEOUT status even though the script was still running.

  Pass no_change_timeout=600 to all exec_command calls (matching the
  client-level HTTP timeout) so long-running commands are not cut short.

  Fixes #2668

* test(sandbox): add assertions for no_change_timeout in execute_command and list_dir

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/2f37bc72-0826-4443-a6ba-e5b78c22fb5a

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`
  L51: # Default no_change_timeout for exec_command (seconds).  Matches the
  L52: # client-level timeout so that long-running commands which produce no
  L53: # output are not prematurely terminated by the sandbox's built-in 120 s
  L54: # default.

## 680187dd 2026-05-05 Xun
fix: Supplement list_running in RemoteSandboxBackend (#2716)

* fix: Supplement list_running in RemoteSandboxBackend

* fix

* except requests.RequestException as exc:

* fix

- `backend/packages/harness/deerflow/community/aio_sandbox/remote_backend.py`
  L88: """Return all sandboxes currently managed by the provisioner.
  L96: """
  L102: """GET /api/sandboxes → list all running sandboxes."""

## bd45cb28 2026-05-08 Eilen Shin
fix(sandbox): disable msys path conversion (#2766)

- `backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`
  L47: """Return whether the selected shell is a Git Bash/MSYS shell."""

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

## e74e126e 2026-05-17 魔力鸟
fix(sandbox): scope provisioner PVC data by user (#2973)

* fix(sandbox): scope provisioner PVC data by user

* Address provisioner PVC review feedback

- `backend/packages/harness/deerflow/community/aio_sandbox/remote_backend.py`

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

