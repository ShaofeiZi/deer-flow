## 30d619de 2026-04-23 Xinmin Zeng
feat(subagents): support per-subagent skill loading and custom subagent types (#2253)

* feat(subagents): support per-subagent skill loading and custom subagent types (#2230)

Add per-subagent skill configuration and custom subagent type registration,
aligned with Codex's role-based config layering and per-session skill injection.

Backend:
- SubagentConfig gains `skills` field (None=all, []=none, list=whitelist)
- New CustomSubagentConfig for user-defined subagent types in config.yaml
- SubagentsAppConfig gains `custom_agents` section and `get_skills_for()`
- Registry resolves custom agents with three-layer config precedence
- SubagentExecutor loads skills per-session as conversation items (Codex pattern)
- task_tool no longer appends skills to system_prompt
- Lead agent system prompt dynamically lists all registered subagent types
- setup_agent tool accepts optional skills parameter
- Gateway agents API transparently passes skills in CRUD operations

Frontend:
- Agent/CreateAgentRequest/UpdateAgentRequest types include skills field
- Agent card displays skills as badges alongside tool_groups

Config:
- config.example.yaml documents custom_agents and per-agent skills override

Tests:
- 40 new tests covering all skill config, custom agents, and registry logic
- Existing tests updated for new get_skills_prompt_section signature

Closes #2230

* fix: address review feedback on skills PR

- Remove stale get_skills_prompt_section monkeypatches from test_task_tool_core_logic.py
  (task_tool no longer imports this function after skill injection moved to executor)
- Add key prefixes (tg:/sk:) to agent-card badges to prevent React key collisions
  between tool_groups and skills

* fix(ci): resolve lint and test failures

- Format agent-card.tsx with prettier (lint-frontend)
- Remove stale "Skills Appendix" system_prompt assertion — skills are now
  loaded per-session by SubagentExecutor, not appended to system_prompt

* fix(ci): sort imports in test_subagent_skills_config.py (ruff I001)

* fix(ci): use nullish coalescing in agent-card badge condition (eslint)

* fix: address review feedback on skills PR

- Use model_fields_set in AgentUpdateRequest to distinguish "field omitted"
  from "explicitly set to null" — fixes skills=None ambiguity where None
  means "inherit all" but was treated as "don't change"
- Move lazy import of get_subagent_config outside loop in
  _build_available_subagents_description to avoid repeated import overhead

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/config/subagents_config.py`
  L35: """User-defined subagent type declared in config.yaml."""
  L131: """Get the skills override for a specific agent.
  L138: """

## f9ff3a69 2026-04-24 Nan Gao
fix(middleware): avoid rescuing non-skill tool outputs during summarization (#2458)

* fix(middelware): narrow skill rescue to skill-related tool outputs

* fix(summarization): address skill rescue review feedback

* fix: wire summarization skill rescue config

* fix: remove dead skill tool helper

* fix(lint): fix format

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/config/summarization_config.py`

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

- `backend/packages/harness/deerflow/config/app_config.py`
- `backend/packages/harness/deerflow/config/database_config.py`
  L1: """Unified database backend configuration.
  L26: """
  L63: # -- Derived helpers (not user-configured) --
  L67: """Resolve sqlite_dir to an absolute path (relative to CWD)."""
  L74: """SQLite file path for the LangGraph checkpointer."""
  L79: """SQLite file path for application ORM data."""
  L84: """SQLAlchemy async URL for the application ORM engine."""
- `backend/packages/harness/deerflow/config/run_events_config.py`
  L1: """Run event storage configuration.
  L12: """

## 56d5fa33 2026-04-12 rayhpeng
feat(persistence):Unified persistence layer with event store, feedback, and rebase cleanup (#2134)

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

- `backend/packages/harness/deerflow/config/database_config.py`
  L78: """Unified SQLite file path shared by checkpointer and app."""
  L81: # Backward-compatible aliases
  L84: """SQLite file path for the LangGraph checkpointer (alias for sqlite_path)."""
  L89: """SQLite file path for application ORM data (alias for sqlite_path)."""

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

- `backend/packages/harness/deerflow/config/memory_config.py`
- `backend/packages/harness/deerflow/config/paths.py`
  L27: """Validate a user ID before using it in filesystem paths."""
  L146: """Directory for a specific user: `{base_dir}/users/{user_id}/`."""
  L150: """Per-user memory file: `{base_dir}/users/{user_id}/memory.json`."""
  L154: """Per-user per-agent memory: `{base_dir}/users/{user_id}/agents/{name}/memory.json`."""

## 35ef8b7c 2026-04-26 JeffJiang
feat: add default database configuration for AppConfig and update example config

- `backend/packages/harness/deerflow/config/app_config.py`
  L181: """Apply config.yaml defaults for persistence when the section is absent."""

## b8bc4826 2026-04-28 greatmengqi
refactor: root release config in gateway runtime (#2611)

Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>

- `backend/packages/harness/deerflow/config/app_config.py`
  L295: # Compatibility singleton layer for code paths that have not yet been
  L296: # migrated to explicit ``AppConfig`` threading. New composition roots should
  L297: # prefer constructing ``AppConfig`` once and passing it down directly.

## eba3b9e1 2026-04-30 He Wang
fix(config): unify log_level from config.yaml across Gateway and debug entry points (#2601)

Centralize log level parsing in `logging_level_from_config()` and
application in `apply_logging_level()` within `deerflow.config.app_config`.

- Gateway lifespan applies configured log level on startup
- `debug.py` uses shared helpers instead of local duplicates
- `apply_logging_level()` targets only `deerflow`/`app` logger hierarchies
  so third-party library verbosity is not affected; root handler levels
  are only lowered (never raised) to allow configured loggers through
  without suppressing third-party output; root logger level is not modified
- Config field description updated to clarify scope
- Tests save/restore global logging state to avoid test pollution

Co-authored-by: Claude Opus 4.7 <noreply@anthropic.com>

- `backend/packages/harness/deerflow/config/app_config.py`
  L57: """Map ``config.yaml`` ``log_level`` string to a :mod:`logging` level constant."""
  L63: """Resolve *name* to a logging level and apply it to the ``deerflow``/``app`` logger hierarchies.
  L71: """

## 1ad1420e 2026-05-01 Xun
refactor(skills): Unified skill storage capability (#2613)

- `backend/packages/harness/deerflow/config/skills_config.py`
  L42: # Default: <repo_root>/skills

## c09c3345 2026-05-01 Nan Gao
fix(harness): resolve runtime paths from project root (#2642)

* fix(harness): resolve runtime paths from project root

* docs(config): update

* fix(config): address runtime path review feedback

* test(config): fix skills path e2e root

* test(config): cover legacy config fallback when project root lacks config files

Verifies that when DEER_FLOW_PROJECT_ROOT is unset and cwd has no
config.yaml/extensions_config.json, AppConfig and ExtensionsConfig fall back
to the legacy backend/repo-root candidates — the backward-compat path
requested in PR #2642 review.

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/config/app_config.py`
  L51: """Return source-tree config.yaml locations for monorepo compatibility."""
- `backend/packages/harness/deerflow/config/extensions_config.py`
- `backend/packages/harness/deerflow/config/paths.py`
  L16: """Return the caller project's writable DeerFlow state directory."""
- `backend/packages/harness/deerflow/config/runtime_paths.py`
  L1: """Runtime path resolution for standalone harness usage."""
  L8: """Return the caller project root for runtime-owned files."""
  L20: """Return the writable DeerFlow state directory."""
  L27: """Resolve absolute paths as-is and relative paths against the project root."""
  L35: """Return the first existing named file under the project root."""
- `backend/packages/harness/deerflow/config/skills_config.py`
  L33: # Use configured path (can be absolute or relative to project root)

## 8ba01dfd 2026-05-02 greatmengqi
refactor: thread app_config through lead and subagent task path (#2666)

* refactor: thread app config through lead prompt

* fix: honor explicit app config across runtime paths

* style: format subagent executor tests

* fix: thread resolved app config and guard subagents-only fallback

Address two PR review findings:

1. _create_summarization_middleware passed the original (possibly None)
   app_config into create_chat_model, forcing the model factory back to
   ambient get_app_config() and risking config drift between the
   middleware's resolved view and the model's view. Pass the resolved
   AppConfig instance through end-to-end.

2. get_available_subagent_names accepted Any-typed config and forwarded
   it to is_host_bash_allowed, which reads ``.sandbox``. A
   SubagentsAppConfig (also accepted upstream as a sum-type input) has
   no ``.sandbox`` attribute and would be silently treated as "no
   sandbox configured", incorrectly disabling the bash subagent. Guard
   on hasattr and fall back to ambient lookup otherwise.

Adds regression tests for both paths.

* chore: simplify hasattr guard and tighten regression tests

- Collapse if/else into ternary in get_available_subagent_names; hasattr(None, ...) is False so the explicit None check was redundant.
- Drop comments that narrate the change rather than explain non-obvious WHY (test names already convey intent).
- Replace stringly-typed sentinel "no-arg" in regression test with direct args tuple comparison.

---------

Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>

- `backend/packages/harness/deerflow/config/app_config.py`

## f80ac961 2026-05-03 Nan Gao
fix(harness): restore legacy skills path fallback (#2694) (#2696)

* fix(harness): restore legacy skills path fallback (#2694)

* fix(format): make format

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/packages/harness/deerflow/config/skills_config.py`
  L10: """Return source-tree skills locations for monorepo compatibility."""

## 59c4a3f0 2026-05-05 yangzheli
feat(agent): add custom-agent self-updates with user isolation (#2713)

* feat(agent): add update_agent tool for in-chat custom-agent self-updates (#2616)

Custom agents had no built-in way to persist updates to their own SOUL.md /
config.yaml from a normal chat — `setup_agent` was only bound during the
bootstrap flow, so when the user asked the agent to refine its description
or personality, the agent would shell out via bash/write_file and the edits
landed in a temporary sandbox/tool workspace instead of
`{base_dir}/agents/{agent_name}/`.

Changes:
- New `update_agent` builtin tool with partial-update semantics (only the
  fields you pass are written) and atomic temp-file + os.replace writes so
  a failed update never corrupts existing SOUL.md / config.yaml.
- Lead agent now binds `update_agent` in the non-bootstrap path whenever
  `agent_name` is set in the runtime context. Default agent (no
  agent_name) and bootstrap flow are unchanged.
- New `<self_update>` system-prompt section is injected for custom agents,
  instructing them to use `update_agent` — and explicitly NOT bash /
  write_file — to persist self-updates.
- Tests: 11 new cases in `tests/test_update_agent_tool.py` covering
  validation (missing/invalid agent_name, unknown agent, no fields),
  partial updates (soul-only, description-only, skills=[] vs omitted),
  no-op detection, atomic-write safety, and AgentConfig round-tripping;
  plus 2 new cases in `tests/test_lead_agent_prompt.py` covering the
  self-update prompt section.
- Docs: updated backend/CLAUDE.md builtin tools list and tools.mdx
  (en/zh) with the new tool description.

* feat(agent): isolate custom agents per user

Store custom agent definitions under the effective user, keep legacy agents readable until migration, and cover API/tool/migration behavior with tests.

Co-authored-by: Cursor <cursoragent@cursor.com>

* feat: consistent write/delete targets & add --user-id to migration

---------

Co-authored-by: Cursor <cursoragent@cursor.com>

- `backend/packages/harness/deerflow/config/agents_config.py`
  L1: """Configuration and loaders for custom agents.
  L8: """
  L53: """Return the on-disk directory for an agent, preferring the per-user layout.
  L66: """
- `backend/packages/harness/deerflow/config/paths.py`
  L135: """Legacy root for shared (pre user-isolation) custom agents: `{base_dir}/agents/`.
  L140: """
  L144: """Legacy per-agent directory (no user isolation): `{base_dir}/agents/{name}/`."""
  L148: """Legacy per-agent memory file: `{base_dir}/agents/{name}/memory.json`."""
  L160: """Per-user root for that user's custom agents: `{base_dir}/users/{user_id}/agents/`."""
  L164: """Per-user per-agent directory: `{base_dir}/users/{user_id}/agents/{name}/`."""

## 4ead2c6b 2026-05-06 KiteEater
fix(config): reset config-backed singletons on hot reload (#2588)

* Fix stale config singletons on reload

* fix(config): update checkpointer imports after runtime move

* Fix config reload singleton mutation on validation failure

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/config/app_config.py`
  L201: # These runtime singletons derive their backend from checkpointer config.
  L202: # Keep imports local to avoid cycles: both providers import get_app_config.
- `backend/packages/harness/deerflow/config/checkpointer_config.py`
- `backend/packages/harness/deerflow/config/stream_bridge_config.py`
- `backend/packages/harness/deerflow/config/subagents_config.py`

## daa3ffc2 2026-05-07 Tao Liu
feat(loop-detection): make loop detection configurable with per-tool frequency overrides (#2711)

* Make loop detection configurable

Expose LoopDetectionMiddleware thresholds through config.yaml while preserving existing defaults and allowing the middleware to be disabled.

Refs bytedance/deer-flow#2517

* feat(loop-detection): add per-tool tool_freq_overrides to Phase 1

Adds ToolFreqOverride model and tool_freq_overrides field to
LoopDetectionConfig, wires it through LoopDetectionMiddleware, and
documents the option in config.example.yaml.

Resolves the gap flagged in the #2586 review: without per-tool overrides,
users hit by #2510/#2511 (RNA-seq workflows exceeding the bash hard limit)
had no way to raise thresholds for one tool without loosening the global
limit for every tool.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* docs(loop-detection): document tool_freq_overrides in LoopDetectionMiddleware docstring

Add the missing Args entry for tool_freq_overrides, explaining the
(warn, hard_limit) tuple structure and how per-tool thresholds supersede
the global tool_freq_warn / tool_freq_hard_limit for named tools.
Also run ruff format on the three files flagged by the lint check.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* fix(loop-detection): validate LoopDetectionMiddleware __init__ params eagerly

Raise clear ValueError at construction time instead of crashing at
unpack-time inside _track_and_check when bad values are passed:
- tool_freq_overrides: must be 2-tuples of positive ints with hard_limit >= warn
- scalar thresholds: warn_threshold, hard_limit, tool_freq_warn,
  tool_freq_hard_limit must be >= 1 and hard limits must >= their warn pairs
- window_size, max_tracked_threads must be >= 1

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* fix(test): isolate credential loader directory-path test from real ~/.claude

The test didn't monkeypatch HOME, so on any machine with real Claude Code
credentials at ~/.claude/.credentials.json the function fell through to
those credentials and the assertion failed. Adding HOME redirect ensures
the default credential path doesn't exist during the test.

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* style(test): add blank lines after import pytest in TestInitValidation

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* refactor(loop-detection): collapse dual validation to LoopDetectionConfig

Modifications
  - LoopDetectionMiddleware.__init__: stripped of all ValueError raises;
    becomes a plain field-assignment constructor.
  - LoopDetectionMiddleware.from_config: classmethod that builds the
    middleware from a Pydantic-validated LoopDetectionConfig and handles
    the ToolFreqOverride -> tuple[int, int] conversion.
  - agents/factory.py: SDK construction routed through
    LoopDetectionMiddleware.from_config(LoopDetectionConfig()) so the
    defaults path is Pydantic-validated too.
  - agents/lead_agent/agent.py: uses from_config instead of unpacking
    config fields by hand.
  - tests/test_loop_detection_middleware.py: deleted TestInitValidation
    (16 methods exercising the removed __init__ checks); added
    TestFromConfig (4 tests: scalar field mapping, override tuple
    conversion, empty overrides, behavioral smoke test).

Result: one validation layer (Pydantic), zero duplication, no __new__
hacks. Both production construction sites flow through LoopDetectionConfig.

Test results
  make test   -> 2977 passed, 18 skipped, 0 failed (137s)
  make format -> All checks passed; 411 files left unchanged

* feat(agents): make loop_detection configurable in create_deerflow_agent

Adds a `loop_detection: bool | AgentMiddleware = True` field to
RuntimeFeatures, mirroring the existing pattern used by `sandbox`,
`memory`, and `vision`. SDK users can now disable LoopDetectionMiddleware
or replace it with a custom instance built from their own
LoopDetectionConfig — e.g.
`LoopDetectionMiddleware.from_config(my_cfg)` — instead of being stuck
with the hardcoded defaults previously installed by the SDK factory.

The lead-agent path (which already reads AppConfig.loop_detection) is
unchanged, and the default `True` preserves prior always-on behavior for
all existing callers.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

---------

Co-authored-by: knight0940 <631532668@qq.com>
Co-authored-by: Claude Opus 4.7 <noreply@anthropic.com>
Co-authored-by: Amorend <142649913+knight0940@users.noreply.github.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/packages/harness/deerflow/config/__init__.py`
- `backend/packages/harness/deerflow/config/app_config.py`
- `backend/packages/harness/deerflow/config/loop_detection_config.py`
  L1: """Configuration for loop detection middleware."""
  L7: """Per-tool frequency threshold override.
  L12: """
  L25: """Configuration for repetitive tool-call loop detection."""
  L68: """Ensure hard stop cannot happen before the warning threshold."""

## 7caf03e9 2026-05-09 KiteEater
fix(packaging): add postgres extra for store/checkpointer supportFix postgres extra install guidance (#2584)

* Fix postgres extra install guidance

* Fix postgres install message lint

* Format postgres install messages

* Fix postgres install guidance and config docs

- `backend/packages/harness/deerflow/config/checkpointer_config.py`

## 5127f08e 2026-05-10 YuJitang
enable token usage by default (#2841)

- `backend/packages/harness/deerflow/config/token_usage_config.py`

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

- `backend/packages/harness/deerflow/config/title_config.py`
  L57: """Restore the title configuration to its pristine ``TitleConfig()`` default.
  L64: """
- `backend/packages/harness/deerflow/config/tracing_config.py`
  L153: """Discard the cached :class:`TracingConfig` so the next call rebuilds it.
  L158: """

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

- `backend/packages/harness/deerflow/config/app_config.py`
- `backend/packages/harness/deerflow/config/safety_finish_reason_config.py`
  L1: """Configuration for SafetyFinishReasonMiddleware.
  L7: """
  L15: """One detector entry under ``safety_finish_reason.detectors``."""
  L27: """Configuration for the SafetyFinishReasonMiddleware.
  L33: """

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

- `backend/packages/harness/deerflow/config/app_config.py`
- `backend/packages/harness/deerflow/config/tool_output_config.py`
  L1: """Configuration for tool output budget protection."""
  L9: """Config section for tool-result output budget enforcement.
  L15: """

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

- `backend/packages/harness/deerflow/config/model_config.py`

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

