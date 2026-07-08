## c6b04235 2026-04-18 yangzheli
feat(frontend): add Playwright E2E tests with CI workflow (#2279)

* feat(frontend): add Playwright E2E tests with CI workflow

Add end-to-end testing infrastructure using Playwright (Chromium only).
14 tests across 5 spec files cover landing page, chat workspace,
thread history, sidebar navigation, and agent chat — all with mocked
LangGraph/Backend APIs via network interception (zero backend dependency).

New files:
- playwright.config.ts — Chromium, 30s timeout, auto-start Next.js
- tests/e2e/utils/mock-api.ts — shared API mocks & SSE stream helpers
- tests/e2e/{landing,chat,thread-history,sidebar,agent-chat}.spec.ts
- .github/workflows/e2e-tests.yml — push main + PR trigger, paths filter

Updated: package.json, Makefile, .gitignore, CONTRIBUTING.md,
frontend/CLAUDE.md, frontend/AGENTS.md, frontend/README.md

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* fix: apply Copilot suggestions

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `.github/workflows/e2e-tests.yml`

## 12214480 2026-04-18 Airene Fang
fix(scripts): Cloud Provider Reports Security Issue（aliyun could） (#2323)

ATT&CK矩阵ID：T1059.004
数据来源：进程启动触发检测
告警原因：该进程的命令行显示出反弹shelI的特征
命令行：timeout 1 bash -c exec 3<>/dev/tcp/127.0.0.1/2024
进程路径：/usr/bin/timeout
进程链：-［337650］ /usr/sbin/sshd -D
-［397971］ /usr/sbin/sshd -D -R
-［397977］-bash
-［398903］ make dev
-［398920］ bash ./scripts/serve.sh --dev
-［399037］bash ./scripts/wait-for-port.sh 2024 60 LangGraph

- `scripts/wait-for-port.sh`

## be466350 2026-04-18 Willem Jiang
chroe(script): disable the color log of langgraph

- `scripts/serve.sh`

## 05f1da03 2026-04-19 YYMa
fix(script): use portable locale for langgraph log pipeline on macOS (#2361)

- `scripts/serve.sh`

## 4be857f6 2026-04-20 KiteEater
fix: use Apple Container image pull syntax (#2366)

- `Makefile`

## 8a044142 2026-04-26 Willem Jiang
feat(dev): add pre-commit hooks for ruff, eslint, and prettier (#2525)

* feat(dev): add pre-commit hooks for ruff, eslint, and prettier

* fix: use local uv-based ruff hooks and uv run for pre-commit install

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/a1e34cc5-0d4b-4400-9e6a-e687d964ff1e

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

- `Makefile`

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

- `docker/docker-compose.yaml`

## 94eee95f 2026-04-09 greatmengqi
feat(auth): release-validation pass for 2.0-rc — 12 blockers + simplify follow-ups (#2008)

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

- `docker/nginx/nginx.local.conf`
  L221: # Catch-all for any /api/* prefix not matched by a more specific block above.
  L222: # Covers the auth module (/api/v1/auth/login, /me, /change-password, ...),
  L223: # plus feedback / runs / token-usage routes that 2.0-rc added without
  L224: # updating this nginx config. Longest-prefix matching ensures the explicit
  L225: # blocks above (/api/models, /api/threads regex, /api/langgraph/, ...) still
  L226: # win for their paths — only truly unmatched /api/* requests land here.
  L235: # Auth endpoints set HttpOnly cookies — make sure nginx doesn't
  L236: # strip the Set-Cookie header from upstream responses.
  L254: # Disable response buffering for the frontend. Without this,
  L255: # nginx tries to spool large upstream responses (e.g. Next.js
  L256: # static chunks) into ``proxy_temp_path``, which defaults to
  L257: # the system-owned ``/var/lib/nginx/proxy`` and fails with
  L258: # ``[crit] open() ... failed (13: Permission denied)`` when
  L259: # nginx is launched as a non-root user (every dev machine
  L260: # except production root containers). The symptom on the
  L261: # client side is ``ERR_INCOMPLETE_CHUNKED_ENCODING`` and
  L262: # ``ChunkLoadError`` partway through page hydration.
  L263: #
  L264: # Streaming the response straight through avoids the
  L265: # temp-file path entirely. The frontend already sets its
  ... (truncated)

## 7bf618de 2026-04-26 JeffJiang
Refactor DeerFlow to use Gateway's LangGraph-compatible API

- Updated documentation and comments to reflect the transition from LangGraph Server to Gateway.
- Changed default URLs in ChannelManager and tests to point to Gateway.
- Removed references to LangGraph Server in deployment scripts and configurations.
- Updated Nginx configuration to route API traffic to Gateway.
- Adjusted frontend configurations to utilize Gateway's API.
- Removed LangGraph service from Docker Compose files, consolidating services under Gateway.
- Added regression tests to ensure Gateway integration works as expected.

Co-authored-by: Copilot <copilot@github.com>

- `Makefile`
- `docker/docker-compose-dev.yaml`
  L7: #   - gateway: Backend Gateway API + agent runtime (port 8001)
  L63: # Routes API traffic to gateway and (optionally) provisioner.
  L142: # DooD: AioSandboxProvider runs inside the Gateway process.
- `docker/docker-compose.yaml`
  L7: #   - gateway:     FastAPI Gateway API + agent runtime
- `docker/nginx/nginx.conf`
  L55: # LangGraph-compatible API routes served by Gateway.
  L56: # Rewrites /api/langgraph/* to /api/* before proxying to Gateway.
- `docker/nginx/nginx.local.conf`
  L47: # LangGraph-compatible API routes served by Gateway.
  L48: # Rewrites /api/langgraph/* to /api/* before proxying to Gateway.
- `scripts/deploy.sh`
  L6: #   deploy.sh                    — build + start
  L8: #   deploy.sh start              — start from pre-built images
  L14: #   deploy.sh                    # build + start
  L16: #   deploy.sh start              # start pre-built images
  L214: # Only needed for start / up — determines whether provisioner is launched.
- `scripts/docker.sh`
- `scripts/serve.sh`
  L6: #   ./scripts/serve.sh [--dev|--prod] [--daemon] [--stop|--restart]
  L19: #   ./scripts/serve.sh --dev                 # Gateway dev, hot reload
  L20: #   ./scripts/serve.sh --prod                # Gateway prod
  L21: #   ./scripts/serve.sh --dev --daemon        # Gateway dev, background
  L23: #   ./scripts/serve.sh --restart --dev       # Restart dev services
  L130: # Extra flags for uvicorn
  L223: # 1. Gateway API
  L228: # 2. Frontend
  L233: # 3. Nginx

## 88d47f67 2026-04-30 Chincherry93
fix(nginx): add catch-all /api/ location for auth routes (#2657)

The recent refactor (7bf618de) removed the langgraph upstream and added
individual /api/* prefix locations for models, memory, mcp, skills,
agents, threads, and sandboxes. However, /api/v1/auth/* routes (login,
register, setup-status, etc.) were not covered by any explicit location
block, causing them to fall through to the frontend catch-all.

In Docker production builds, Next.js rewrites are baked at build time
with http://127.0.0.1:8001 (the gateway is unreachable from the
frontend container's localhost), resulting in ECONNREFUSED errors for
all auth operations.

Adding a catch-all `location /api/` block after the more specific
prefix/regex locations ensures all gateway API routes are properly
proxied. nginx's location matching priority means the more specific
locations above still take precedence for /api/langgraph/, /api/models,
/api/memory, /api/mcp, /api/skills, /api/agents, /api/threads/*, and
/api/sandboxes.

Co-authored-by: Chincherry93 <Chincherry93@users.noreply.github.com>

- `docker/nginx/nginx.conf`
  L210: # Catch-all for /api/ routes not covered above (e.g. /api/v1/auth/*).
  L211: # More specific prefix and regex locations above still take precedence.

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

- `docker/docker-compose-dev.yaml`
- `docker/docker-compose.yaml`
  L11: #   DEER_FLOW_PROJECT_ROOT           — project root for relative runtime paths
  L12: #   DEER_FLOW_HOME                   — runtime data dir, default .deer-flow under $DEER_FLOW_PROJECT_ROOT (or cwd)
  L15: #   DEER_FLOW_SKILLS_PATH            — skills dir, default $DEER_FLOW_PROJECT_ROOT/skills

## b10eb7ba 2026-05-04 Willem Jiang
feat(github): Added container push workflow (#2709)

* feat(github):Added container push workflow

* Apply suggestions from code review

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `.github/workflows/container.yaml`

## 028493bf 2026-05-05 Willem Jiang
fix(docker):force ngix to resolve upstream names at request time (#2717)

* fix(docker):force ngix to resolve upstream names at request time

* fix(docker): set resolver valid=0s to eliminate DNS cache window for request-time re-resolution

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/07bdb872-022f-4fd2-9fa8-d800a4ce34a7

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* Update DNS resolver valid time and add upstreams

* fix the unit test error

* Remove upstream server configurations from nginx.conf

Removed upstream server configurations for gateway and frontend.

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

- `docker/nginx/nginx.conf`
  L26: # Resolve Docker service names at request time to avoid stale upstream
  L27: # IPs when containers restart and receive new addresses.

## 70737af7 2026-05-08 Willem Jiang
fix(nignx):resolve CSRF auth failure on non-standard ports (#2796)

- `docker/nginx/nginx.conf`
- `docker/nginx/nginx.local.conf`

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

- `docker/dev-entrypoint.sh`
  L1: #!/usr/bin/env sh
  L2: #
  L3: # DeerFlow gateway dev entrypoint — runs inside the docker-compose-dev gateway
  L4: # container. Extracted from docker/docker-compose-dev.yaml's inline `command:`
  L5: # (PR #2767, addressing review on Issue #2754).
  L6: #
  L7: # Responsibilities:
  L8: #   1. Resolve `--extra X` flags from UV_EXTRAS (comma- or whitespace-separated,
  L9: #      mirroring scripts/detect_uv_extras.py for parity with local `make dev`).
  L10: #   2. Validate each extra against [A-Za-z][A-Za-z0-9_-]* so a stray shell
  L11: #      metacharacter in `.env` cannot reach `uv sync`.
  L12: #   3. `uv sync --all-packages` so workspace member extras (deerflow-harness's
  L13: #      postgres extra in particular) are installed — see PR #2584.
  L14: #   4. Self-heal: if the first sync fails, recreate .venv and retry once.
  L15: #   5. Hand off to uvicorn with reload, replacing this shell so uvicorn becomes
  L16: #      PID 1 inside the container.
  L17: #
  L18: # Anchored at /bin/sh (not bash) since alpine-based base images may not ship
  L19: # bash. Uses POSIX-only constructs throughout.
  L23: # `--print-extras` is a dry-run hook: parse + validate UV_EXTRAS, print the
  ... (truncated)
- `docker/docker-compose-dev.yaml`
  L128: # Startup logic lives in docker/dev-entrypoint.sh — UV_EXTRAS validation,
  L129: # `uv sync --all-packages`, .venv self-heal, and uvicorn handoff. Keeps
  L130: # this file readable and lets the script be linted (shellcheck-clean).
  L131: # See PR #2767 / Issue #2754.
  L134: # Mount the dev entrypoint as a read-only file so edits to the script
  L135: # take effect on `make docker-restart` without requiring an image rebuild.
- `scripts/detect_uv_extras.py`
  L1: #!/usr/bin/env python3
  L2: """Resolve uv extras for local `uv sync` based on environment + config.yaml.
  L27: """
  L36: # Mirrors uv's accepted shape for extra names — keeps the eventual
  L37: # `uv sync --extra <name>` invocation free of shell metacharacters even when
  L38: # `UV_EXTRAS` comes from `.env` or another semi-trusted source.
  L56: """Split UV_EXTRAS into a list, accepting comma or whitespace separators."""
  L62: """Locate config.yaml using the same precedence as serve.sh."""
  L79: """Drop trailing `#` comments while preserving `#` inside quoted strings."""
  L105: """Return the value of `section.key` from a flat-ish YAML, or None.
  L112: """
- `scripts/serve.sh`
  L160: # Pick a Python for the extras detector. Falls back to plain `python` for
  L161: # Windows/Git Bash where only `python` is on PATH.
  L170: # Resolve uv extras (postgres, etc.) from UV_EXTRAS or config.yaml so that
  L171: # `uv sync` does not wipe out optional dependencies on every restart. See
  L172: # scripts/detect_uv_extras.py and Issue #2754 for context. The detector
  L173: # whitelists extra names against `^[A-Za-z][A-Za-z0-9_-]*$`, so the unquoted
  L174: # splat below only sees valid uv argument tokens.
  L175: #
  L176: # Stderr is intentionally NOT redirected so the user sees:
  L177: #   - whitelist warnings (e.g. "ignoring invalid UV_EXTRAS entry ';'");
  L178: #   - detector crashes (e.g. unexpected Python error).
  L179: # `|| true` keeps `set -e` from killing dev startup on a detector failure;
  L180: # the result is just an empty UV_EXTRAS_FLAGS, which means "no extras".
  L191: # `--all-packages` propagates extras into workspace members (deerflow-harness
  L192: # in particular). Required for postgres extras — see PR #2584.
  L193: # Intentionally unquoted to splat multiple `--extra X` pairs.

## c3bc6c7c 2026-05-11 AochenShen99
fix(nginx): defer CORS to gateway allowlist (#2861)

* fix(nginx): defer cors to gateway allowlist

Remove proxy-level wildcard CORS handling so browser origins are controlled by the Gateway allowlist and stay aligned with CSRF origin checks.

* docs: document gateway cors allowlist

Clarify that same-origin nginx access needs no CORS headers while split-origin or port-forwarded browser clients must opt in with GATEWAY_CORS_ORIGINS.

* docs(gateway): record cors source of truth

Document that Gateway CORSMiddleware and CSRFMiddleware share GATEWAY_CORS_ORIGINS as the split-origin source of truth.

* fix(gateway): align cors origin normalization

* docs: clarify gateway langgraph routing

* docs(gateway): update runtime routing note

- `docker/nginx/nginx.conf`
  L31: # Keep the unified nginx endpoint same-origin by default. When split
  L32: # frontend/backend or port-forwarded deployments need browser CORS,
  L33: # configure the Gateway allowlist with GATEWAY_CORS_ORIGINS so CORS and
  L34: # CSRF origin checks stay aligned instead of approving every origin at
  L35: # the proxy layer.
- `docker/nginx/nginx.local.conf`
  L31: # Keep the unified nginx endpoint same-origin by default. When split
  L32: # frontend/backend or port-forwarded deployments need browser CORS,
  L33: # configure the Gateway allowlist with GATEWAY_CORS_ORIGINS so CORS and
  L34: # CSRF origin checks stay aligned instead of approving every origin at
  L35: # the proxy layer.

## 48e038f7 2026-05-15 Yi Tang
feat(channels): enhance Discord with mention-only mode, thread routing, and typing indicators (#2842)

* feat(channels): enhance Discord with mention-only mode, thread routing, and typing indicators

Add mention_only config to only respond when bot is mentioned, with
allowed_channels override. Add thread_mode for Hermes-style auto-thread
creation. Add periodic typing indicators while bot is processing.

* fix(discord): include allowed_channels in mention_only skip condition (line 274)

* docs: fix Discord config example to match boolean thread_mode implementation

* style: format with ruff

* fix(discord): apply Copilot review fixes and resolve lint errors

- Remove unused Optional import
- Fix thread_ts type hints to str | None
- Fix has_mention logic for None values
- Implement thread_mode fallback to channel replies on thread creation failure
- Fix thread_mode docstring alignment
- Fix allowed_channels comment formatting in config.example.yaml

* fix(discord): reset context for orphaned threads in mention_only mode

When a message arrives in a thread not tracked by _active_threads,
clear thread_id and typing_target so the message falls through to
the standard channel handling pipeline, which creates a fresh thread
instead of incorrectly routing to the stale thread.

* fix(discord): create new thread on @ when channel has existing tracked thread

When mention_only is enabled and a user @-s the bot in a channel
that already has a tracked thread, create a new thread instead of
incorrectly routing to the old one.

* fix(discord): allow no-@ thread replies while skipping no-@ channel messages

The skip block for no-@ messages was too aggressive — it blocked
continuation replies within tracked threads AND incorrectly routed
no-@ channel messages to the existing thread.

Now:
- Thread message, no @ → routed to existing tracked thread
- Channel message, no @ → skipped
- Channel message, with @ → creates new thread

* feat(discord): add checkmark reaction to acknowledge received messages

* Move discord.py to optional dependency and auto-detect from config.yaml

- Add discord extra to [project.optional-dependencies] in pyproject.toml
- Update detect_uv_extras.py to map channels.discord.enabled: true -> --extra discord
- Set UV_EXTRAS=discord in docker-compose-dev.yaml gateway env

* fix(discord): persist thread-channel mappings to store for recovery after restart

Discord's _active_threads dict was purely in-memory, so all channel-to-thread
mappings were lost on server restart. This fix bridges ChannelStore into
DiscordChannel:

- Save thread mappings to store.json after every thread creation
- Restore active threads from store on DiscordChannel startup
- Pass channel_store to all channels via service.py config injection

Store keys follow the pattern: discord:<channel_id>:<thread_id>

* fix(discord): address Copilot review — fix types, typing targets, cross-thread safety, and config comments

* fix(tests): add multitask_strategy param to mock for clarification follow-up test

* fix(tests): explicitly set model_name=None for title middleware test isolation

* fix(discord): use trigger_typing() instead of typing() for typing indicators

discord.py 2.x TextChannel.typing() and Thread.typing() are async context
managers, not one-shot coroutines. Use trigger_typing() for periodic
typing indicator pings.

* fix(discord): cancel typing tasks on channel shutdown

Prevents 'Task was destroyed but it is pending' warnings when the
Discord client stops while typing indicator loops are still running.

* fix(scripts): detect nested YAML config for discord extra

section_value() only matched top-level YAML sections. Added
nested_section_value() that handles two-level nesting (e.g.,
channels.discord.enabled), so auto-detection of the discord
extra works when config uses the standard nested format.

* fix(docker): remove hard-coded UV_EXTRAS=discord from dev compose

Relies on auto-detection via detect_uv_extras.py instead of forcing
discord.py install even when channels.discord.enabled is false.
Matches production docker-compose.yaml behavior (UV_EXTRAS:-).

* refactor(nginx): move proxy_buffering/proxy_cache to server level

DRY cleanup — these directives were repeated in 14 location blocks.
Set at server level once, reducing duplication and risk of drift.

* fix(discord): use dedicated JSON file for thread persistence

Replace ChannelStore usage for Discord thread-ID persistence with a
dedicated discord_threads.json file. ChannelStore is designed to map
IM conversations to DeerFlow thread IDs — using it to persist Discord
thread IDs was semantically wrong and confusing.

Changes:
- _save_thread() now reads/writes a simple {channel_id: thread_id} JSON dict
- _load_active_threads() reads directly from the JSON file
- File path derived from ChannelStore directory (when available) or
  defaults to ~/.deer-flow/channels/discord_threads.json
- Removed unused ChannelStore import

* fix(discord): address WillemJiang's code review comments on PR #2842

1. Remove semantically incorrect message_in_thread variable. At this code
   point (after the Thread case is handled above), we're guaranteed to be in
   a channel, not a thread. Always apply mention_only check here.

2. Add _active_thread_ids reverse-lookup set for O(1) thread ID membership
   checks instead of O(n) scan of _active_threads.values(). Keep the set
   in sync with _active_threads in _load_active_threads() and _save_thread().

3. Add _thread_store_lock (threading.Lock) to protect _active_threads and
   the JSON file from concurrent access between the Discord loop thread
   (_run_client) and the main thread (_load_active_threads, _save_thread).

- `docker/nginx/nginx.conf`
  L31: # Default proxy settings for all locations (streaming/SSE support)
  L135: # Disable response buffering to avoid permission errors
  L217: # Disable buffering to avoid permission errors when nginx
  L218: # runs as a non-root user (e.g. local development).
- `docker/nginx/nginx.local.conf`
  L74: # Disable buffering to avoid permission errors when nginx
  L75: # runs as a non-root user (e.g. local development).
  L145: # Disable response buffering to avoid permission errors
  L233: # Disable buffering to avoid permission errors when nginx
  L234: # runs as a non-root user (e.g. local development).
- `scripts/detect_uv_extras.py`
  L146: """Return the value of a nested YAML key like ``channels.discord.enabled``.
  L152: """
  L171: # Top-level section match
  L184: # Track parent indent from first child
  L188: # If indent goes back to 0, we left the parent section
  L194: # Check if we're at the parent's child level (subsection)
  L196: # This could be a subsection or a direct key of parent
  L209: # We're inside the subsection — track child indent

## e74e126e 2026-05-17 魔力鸟
fix(sandbox): scope provisioner PVC data by user (#2973)

* fix(sandbox): scope provisioner PVC data by user

* Address provisioner PVC review feedback

- `docker/docker-compose-dev.yaml`
  L40: # USERDATA_PVC_NAME uses subPath (deer-flow/users/{user_id}/threads/{thread_id}/user-data) automatically.
- `docker/provisioner/README.md`
  L23: 1. **Backend Request**: When the backend needs to execute code, it sends a `POST /api/sandboxes` request with a `sandbox_id`, `thread_id`, and optional `user_id`.
  L73: "thread_id": "thread-456",
  L74: "user_id": "user-789"
  L78: `user_id` is optional for backwards compatibility and defaults to `default`. When `USERDATA_PVC_NAME` is set, the provisioner uses it to isolate PVC-backed user-data directories.
  L79: 
  L144: | `USERDATA_PVC_NAME` | empty (use hostPath) | PVC name for user-data volume; when set, uses PVC with `subPath: deer-flow/users/{user_id}/threads/{thread_id}/user-data` |
  L149: ### PVC User-Data Upgrade Note
  L150: 
  L151: Older provisioner versions mounted PVC user-data from `threads/{thread_id}/user-data`. The user-scoped layout mounts from `deer-flow/users/{user_id}/threads/{thread_id}/user-data`.
  L152: 
  L153: If an existing deployment already has PVC-backed user-data under the legacy layout, migrate the DeerFlow data directory before relying on the new PVC subPath. Mount the same PVC path that the gateway uses as its DeerFlow base directory, then run the existing user-isolation migration script:
  L154: 
  L155: ```bash
  L156: cd backend
  L157: PYTHONPATH=. python scripts/migrate_user_isolation.py --dry-run
  L158: PYTHONPATH=. python scripts/migrate_user_isolation.py --user-id <target-user-id>
  L159: ```
  L160: 
  L161: This moves legacy `threads/{thread_id}/user-data` data under `users/<target-user-id>/threads/{thread_id}/user-data`, which matches the new provisioner PVC subPath when the gateway base directory is mounted at `deer-flow/` on the PVC. Use `default` as the target user only when the legacy data should remain in the default no-auth user namespace. Run the migration while no gateway or sandbox Pods are writing to those paths.
  L162: 
  ... (truncated)
- `docker/provisioner/app.py`

## 0c223490 2026-05-20 AochenShen99
chore(dev): add async/thread boundary detector (#2936)

* chore(dev): add thread boundary detector

* chore(dev): reduce thread boundary detector false positives

- `Makefile`
- `scripts/detect_thread_boundaries.py`
  L1: #!/usr/bin/env python3
  L2: """CLI wrapper for the async/thread boundary detector."""

## 8cd4710b 2026-05-20 john lee
fix(deploy): fall back to python/openssl when python3 is absent for secret generation (#3074)

* fix(deploy): fall back to python/openssl when python3 is absent for secret generation

Bare python3 call in deploy.sh exits 49 on systems without python3 in
PATH (e.g. some Alpine/minimal containers, or Windows environments where
only 'python' is on PATH). Add a fallback chain: python3 → python →
openssl rand -hex 32. If all three are unavailable, emit a clear error
message and exit with a non-zero status instead of a cryptic recipe
failure.

Closes #2922

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Claude Sonnet 4.6 <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `scripts/deploy.sh`

## 9abe5a18 2026-05-20 DanielWalnut
fix: clean up local nginx on stop (#3005)

* fix: clean up local nginx on stop

* fix: scope local service cleanup to repo

* fix: address serve port review comments

- `scripts/serve.sh`

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

- `.github/workflows/backend-blocking-io-tests.yml`

## b00749a8 2026-05-26 Stellar鱼
fix(auth): share internal gateway token across workers (#3184)

* fix(auth): share internal gateway token across workers

* fix: restore deploy script executable bit

* Update deploy.sh

to skip the auth_token setup for the down command

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `docker/docker-compose-dev.yaml`
- `docker/docker-compose.yaml`
  L19: #   DEER_FLOW_INTERNAL_AUTH_TOKEN    — shared internal Gateway auth token for multi-worker IM channels
- `scripts/deploy.sh`
  L143: # ── DEER_FLOW_INTERNAL_AUTH_TOKEN ────────────────────────────────────────────
  L144: # Shared by all Gateway workers so channel workers can call internal Gateway
  L145: # APIs even when the request is handled by a different Uvicorn worker.

## da41701f 2026-05-26 AochenShen99
Add static blocking IO inventory (#3208)

* feat(detectors): add static blocking IO inventory

* refactor(detectors): drop superseded runtime probe; clarify static report path

- Remove the #2924 custom runtime blocking IO probe entirely:
  backend/tests/support/detectors/blocking_io.py,
  backend/tests/test_blocking_io_detector.py,
  backend/tests/test_blocking_io_probe_integration.py, and the
  pytest_addoption / pytest_runtest_call / pytest_runtest_teardown /
  pytest_sessionfinish / pytest_terminal_summary hooks plus the
  blocking_io_detector fixture from backend/tests/conftest.py.
  Its narrow DEFAULT_BLOCKING_CALL_SPECS (time.sleep, requests, httpx,
  os.walk, Path.resolve, Path.read_text, Path.write_text) cannot serve
  as a CI gate; a Blockbuster-backed runtime detector will land in a
  separate follow-up PR. Leaving the half-coverage probe alongside
  the static inventory in this PR added a redundant detect path with
  no production value.
- Address Copilot review comments on backend/README.md and
  backend/CLAUDE.md by stating explicitly that the JSON report writes
  to .deer-flow/blocking-io-findings.json at the repository root,
  whether the target is invoked from the repo root or from backend/.

Verified: pytest tests/test_detect_blocking_io_static.py (18 passed),
ruff check + format on touched files (passed), make detect-blocking-io
from both repo root and backend/ produce the same 105-finding report
at <repo-root>/.deer-flow/blocking-io-findings.json.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.7 <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `Makefile`
- `scripts/detect_blocking_io_static.py`
  L2: """CLI wrapper for the static blocking IO detector."""

## d6a604d5 2026-06-01 FallingSnowFlake
fix(makefile): extract setup-sandbox inline bash to script for Windows compatibility (#3326)

- `Makefile`
- `scripts/setup-sandbox.sh`
  L1: #!/usr/bin/env bash
  L2: # Pre-pull sandbox container image for DeerFlow
  L11: # Try to extract image from config.yaml (handles both commented and uncommented sandbox sections)
  L14: # Look for uncommented image: field under the sandbox section

## aca7acc1 2026-06-03 Xinmin Zeng
feat(ci): PR/issue auto-labeling + declarative label sync (#3360)

- .github/labels.yml: declarative source of truth (29 namespaced labels)
- scripts/sync_labels.py + label-sync.yml: idempotent label sync (self-bootstraps on merge)
- labeler.yml + pr-labeler.yml: area:* labels by changed path (actions/labeler)
- pr-triage.yml: size/*, risk:*, needs-validation, first-time-contributor, reviewing
- issue-triage.yml: needs-triage on new issues (self-healing)

All PR workflows use pull_request_target but never check out or run PR code
(read changed-file metadata via the API only).

- `.github/workflows/issue-triage.yml`
  L3: # Ensures every newly opened issue carries `needs-triage`, even blank or
  L4: # API-created ones that bypass the issue templates. Creates the label if it is
  L5: # somehow missing, so the workflow is self-healing.
- `.github/workflows/label-sync.yml`
  L3: # Keeps repository labels in sync with the declarative source of truth
  L4: # (.github/labels.yml). Runs whenever that file changes on main, and can be
  L5: # triggered manually. Additive/update-only — never deletes labels.
- `.github/workflows/pr-labeler.yml`
  L3: # Applies area:* labels based on which files a PR changes (see .github/labeler.yml).
  L4: # Uses pull_request_target so it also works on fork PRs. SAFE: actions/labeler
  L5: # only reads the changed-file list via the API — it never checks out or runs PR code.
- `.github/workflows/pr-triage.yml`
  L3: # Two responsibilities, both pure-metadata (no PR code is checked out or run):
  L4: #   1. On open/sync: apply size/* + risk:* labels, and needs-validation when the
  L5: #      PR touches the front/back contract surface (backend API, SSE, agents, or
  L6: #      the frontend streaming client). A `skip-validation` label opts out.
  L7: #   2. On maintainer review: apply the `reviewing` label.
  L8: #
  L9: # All labels are managed within their own namespace — labels outside size/*,
  L10: # risk:*, needs-validation and reviewing are never touched here.
- `scripts/sync_labels.py`
  L1: #!/usr/bin/env python3
  L2: """Sync GitHub labels from the declarative source of truth.
  L13: """

## 0d0968a3 2026-06-03 Admire
chore: add sandbox memory profiling tools (#3249)

* chore: add sandbox memory profiling tools

* chore: keep sandbox memory PR profiling-only

* Format sandbox memory profiling script

- `scripts/sandbox_memory_profile.py`
  L1: #!/usr/bin/env python3
  L2: """Collect Kubernetes sandbox pod memory snapshots for DeerFlow.
  L7: """

## 3fddc24c 2026-06-03 Eilen Shin
chore: remove stale LangGraph server runtime remnants (#3344)

* chore: remove stale langgraph server runtime remnants

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `Makefile`

## 3b4c9ff7 2026-06-08 Nan Gao
fix(setup): refresh LLM provider wizard defaults (#3421)

- `scripts/wizard/providers.py`
- `scripts/wizard/steps/llm.py`
  L35: # Model selection (show list, default to provider preference)

## 88759015 2026-06-08 Xinmin Zeng
test(e2e): deterministic record/replay front-back contract verification (#3365)

* test(e2e): record/replay front-back contract verification

Guards the front-back contract with a deterministic, key-free record/replay
harness (mirrors open-design's golden-trace approach):

- ReplayChatModel (tests/replay_provider.py): replays recorded LLM turns by a
  normalized hash of the model input. Strips <system-reminder>/date/uuid/tmp-path
  so one fixture replays across days and from both the browser and direct-POST
  paths; a miss raises loudly (no silent divergence).
- Recording is record-through-browser (scripts/record_gateway.py +
  build_fixture_from_jsonl.py + frontend/tests/e2e-record): a real run is driven
  through the real frontend so captured inputs match exactly what the browser
  sends; fixtures contain no API key.
- Layer 1 — backend golden (tests/test_replay_golden.py): replay through the real
  gateway, assert the SSE event sequence == committed golden.
- Layer 2 — full-stack render (frontend/tests/e2e-real-backend): real Next.js +
  real gateway (replay model) + Chromium; assert the replayed auto-title and
  follow-up suggestions render. DOM assertions are the gate; visual regression is
  a local dev gate (CI uploads the render as an artifact).
- CI (.github/workflows/replay-e2e.yml): both layers, triggered on EITHER side of
  the contract (frontend/** or backend gateway/harness/fixtures).

* test(e2e): multi-run render-order cross-stack scenario (#3352)

Guards the dangerous front-back class where a backend ordering change
silently breaks a frontend assumption while both sides' unit tests stay
green. Reproduces issue #3352: backend list_by_thread returns runs
newest-first (#2932) and the frontend prepended per-run pages, inverting
chronological order once the checkpoint no longer held the older messages.

- tests/seed_runs_router.py: test-only seeder, mounted on the replay
  gateway only when DEERFLOW_ENABLE_TEST_SEED=1 (never in the production
  app). Seeds a thread with >=2 runs + per-run message events and no
  checkpoint -- the #3352 precondition -- so the frontend per-run reload
  path is the sole source of truth and the prepend inversion is observable.
- frontend/tests/e2e-real-backend/multi-run-order.spec.ts: drives the real
  frontend against the real gateway, asserts the first run renders above
  the second. Reverting the #3354 fix turns it red.
- replay-e2e.yml: trigger on the new replay test-infra paths.
- docs: REPLAY_E2E.md cross-stack scenario section.

* test(e2e): address Copilot review on the replay harness

- Fix stale recorder references (scripts/record_traces.py ->
  scripts/record_gateway.py + scripts/build_fixture_from_jsonl.py) in
  replay_provider.py, test_replay_golden.py, _replay_fixture.py.
- MODE_CONTEXT['ultra']: thinking_enabled False -> True, mirroring the
  frontend's `context.mode !== 'flash'` (hooks.ts). It did not affect the
  hashed input (Layer 1 golden still green), but the table now matches the
  real frontend context it claims to mirror.
- replay_provider.py docstring: stop claiming memory is recorded-enabled;
  the replay config disables memory/summarization for determinism (title
  stays, as an in-graph deterministic call).
- record_gateway.py / run_replay_gateway.py: override DEER_FLOW_HOME instead
  of setdefault, so an outer value can't leak into the hermetic harness.
- record_gateway.py: clear error when DEERFLOW_RECORD_OUT is unset (was a
  bare KeyError).
- playwright.record.config.ts: forward OPENAI_*/DEERFLOW_RECORD_OUT only when
  set, so the gateway raises a clear 'missing env' error instead of getting ''.

* test(e2e): address Copilot review round 2

- seed_runs_router.py: constrain SeedMessage.role to Literal['human','ai']
  so a bad value is a clean 422 at the boundary instead of a 500
  (KeyError on _EVENT_TYPE).
- record-write-read-file.spec.ts: waitForCaptureStable now throws on
  timeout instead of returning the last count, so a truncated/partial
  recording can't pass silently.
- real-backend-render.spec.ts: guard the suggestions JSON.parse; a
  bracket-prefixed non-JSON turn falls back to '' so the existing
  not.toBe('') assertion fails clearly instead of a generic parse throw.

- `.github/workflows/replay-e2e.yml`
  L3: # Guards the front-back contract via record/replay (no API key in CI):
  L4: #   Layer 1 — backend golden: replay a recorded trace through the real gateway,
  L5: #             assert the SSE event sequence matches the committed golden.
  L6: #   Layer 2 — full-stack render: real Next.js frontend + real gateway (replay
  L7: #             model) + Chromium; assert the replayed turns render in the browser.
  L8: # Triggered by changes on EITHER side of the contract so a backend change can no
  L9: # longer pass without the frontend-facing checks running.

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

- `scripts/serve.sh`
  L65: # Every deer-flow worktree (the main checkout + each linked worktree) hardcodes
  L66: # the same dev ports (8001/3000/2026), so a service started from ANY of them
  L67: # must be reclaimable from here — otherwise `make stop`/`make dev` in this
  L68: # worktree can neither kill nor take over a port held by a sibling worktree.
  L69: # DEERFLOW_ROOTS is that set of roots; processes living outside all of them
  L70: # (e.g. an unrelated project on port 3000) are still never touched.
  L71: # Sorted most-specific-first (longest path first): a linked worktree lives
  L72: # under the main checkout, so both roots are substrings of its files — checking
  L73: # the deeper root first attributes a reclaimed port to the right worktree.
  L82: # True if PID has an open file/cwd under any deer-flow worktree root. The
  L83: # trailing slash keeps a sibling dir like ".../deer-flow-notes" from matching
  L84: # the ".../deer-flow" root.
  L97: # Report ports about to be reclaimed from a *different* worktree, so stopping
  L98: # (or starting, which stops first) isn't silently killing someone else's run.
  L237: # Force-kill any survivors still holding the service ports. 2026 is included
  L238: # so a lingering nginx (or any deer-flow process) that _kill_repo_nginx did
  L239: # not match by name still gets reclaimed — otherwise `make dev` fails its
  L240: # nginx port preflight.
- `scripts/setup_wizard.py`
- `scripts/wizard/providers.py`
  L22: # Per-model supports_vision overrides for providers whose models differ in
  L23: # capability (e.g. MiniMax M3 supports vision but M2.7 is text-only). The
  L24: # provider-level extra_config holds the default (default_model) capability.
  L31: """Return extra_config for a selected model, applying per-model overrides.
  L34: """

## 67ad6e23 2026-06-08 zgenu
fix(dev): exclude runtime state from gateway reload (#3426)

- `docker/dev-entrypoint.sh`
  L67: # Keep runtime-owned files out of uvicorn's reload watcher. The directory must
  L68: # exist before uvicorn starts so watchfiles treats it as an excluded directory,
  L69: # not as a plain glob pattern.
- `scripts/serve.sh`
  L288: # Runtime path defaults. Local `make dev` launches Gateway from `backend/`,
  L289: # so pin DeerFlow-owned state to the expected backend runtime directory and
  L290: # create it before uvicorn builds its reload exclude filter.

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

- `docker/docker-compose-dev.yaml`
  L175: # Proxy values (HTTP_PROXY/HTTPS_PROXY/ALL_PROXY) are inherited from ../.env via env_file.
  L176: # Only NO_PROXY is declared here so internal service hostnames are always exempt from the proxy.
- `docker/docker-compose.yaml`
  L110: # Proxy values (HTTP_PROXY/HTTPS_PROXY/ALL_PROXY) are inherited from ../.env via env_file.
  L111: # Only NO_PROXY is declared here so internal service hostnames are always exempt from the proxy.
- `scripts/docker.sh`

## 90e23bfd 2026-06-09 Xinmin Zeng
fix(ci): consolidate PR/issue labeling and fix reviewing-job crash + label thrash (#3455)

* fix(ci): consolidate PR/issue labeling into one triage.yml; fix reviewing crash & label thrash

- Replace pr-labeler + pr-triage + issue-triage with a single triage.yml; drop actions/labeler.
  Its sync-labels removed labels outside its config (clobbered size/risk/needs-validation and
  could clobber maintainer labels). Area is now computed in-script and reconciled only within
  owned namespaces (area:/size//risk:/needs-validation); first-time/reviewing are add-only.
- reviewing: gate on author_association in {OWNER,MEMBER,COLLABORATOR} + user.type==='User'
  instead of getCollaboratorPermissionLevel, which 404'd on bot reviewers ('Copilot is not a
  user') and crashed the job. Excludes all review bots with no denylist and no API call.
- Read live state (listFiles + listLabelsOnIssue) not the stale event payload, so rapid
  synchronize events converge instead of thrashing. Size churn excludes lockfiles/snapshots.

* fix(ci): read labels live via paginate in reviewing & issue-triage jobs

Address review feedback on #3455:
- reviewing: listLabelsOnIssue now paginates (per_page:100) instead of the
  default 30, matching pr-labels, so a 'reviewing' label is never missed on
  PRs with many labels.
- issue-triage: read live labels via the API instead of the event payload,
  consistent with the live-state reads documented in the header.

- `.github/workflows/triage.yml`
  L3: # One workflow for all event-driven PR/issue labeling. Replaces the former
  L4: # pr-labeler / pr-triage / issue-triage workflows (and drops actions/labeler).
  L5: #
  L6: # Design notes:
  L7: #   * All jobs are pure-metadata: they read changed-file lists / PR fields / the
  L8: #     review payload via the API and write labels. PR code is NEVER checked out
  L9: #     or executed, so pull_request_target is safe here.
  L10: #   * Each job only reconciles labels in namespaces IT owns
  L11: #     (area:* / size/* / risk:* / needs-validation). It never touches labels
  L12: #     applied by maintainers or other tools (bug, priority, etc.). first-time-
  L13: #     contributor and reviewing are add-only.
  L14: #   * State is read LIVE (listFiles + listLabelsOnIssue) at run time, not from
  L15: #     the (stale) event payload, so rapid synchronize events converge instead
  L16: #     of thrashing.
  L32: # ── PR: area / size / risk / needs-validation / first-time ─────────────────
  L141: # ── PR: reviewing label on a maintainer's human review ─────────────────────
  L186: # ── Issue: needs-triage on every new issue ────────────────────────────────

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

- `scripts/tool-error-degradation-detection.sh`

## 93e3281c 2026-06-09 AochenShen99
fix(dev): create backend/sandbox before uvicorn reload-exclude (#3459) (#3460)

* fix(dev): create backend/sandbox before uvicorn reload-exclude (#3459)

#3426 switched the dev gateway's --reload-exclude patterns to absolute
paths. uvicorn only excludes an absolute path directly when it already
exists as a directory; otherwise it globs the pattern, and Python 3.12's
pathlib raises NotImplementedError("Non-relative patterns are unsupported")
for an absolute glob pattern. serve.sh mkdir'd the .deer-flow excludes but
not backend/sandbox, so `make dev` crashed on startup on a fresh checkout
under Python 3.12 (#3454). docker/dev-entrypoint.sh had the same latent gap.

Create backend/sandbox in both launchers so every absolute exclude stays on
uvicorn's is_dir() short-circuit. Add a regression test that pins the uvicorn
mechanism (crash on missing dir, safe once created) and enforces that every
absolute --reload-exclude is mkdir'd before launch.

Closes #3459

* test(dev): harden reload-exclude invariant parser against false pass/negatives

The launcher invariant test parsed shell with a "mkdir -p" line filter and a
substring membership check. Two latent gaps (sub-threshold for this fix, but
this code guards a user-facing startup path, so close them):

- A `\`-continued multi-line `mkdir` would drop arguments on continuation
  lines, silently weakening coverage.
- Substring membership could false-pass when an exclude is a path-prefix of a
  different created dir (e.g. `/app/backend/sandbox` "found" inside
  `/app/backend/sandbox-other`).

Fold line-continuations, drop comments, and shlex-tokenize each `mkdir`
argument list into an exact set (quotes stripped, `$VAR` literal); assert exact
set membership. Same shlex handling for `--reload-exclude` values. Verified the
parser still flags the pre-fix missing `backend/sandbox` (RED preserved) and no
longer false-passes on a path-prefix.

* fix(dev): gitignore backend/sandbox runtime dir + pin mkdir-before-launch

Address two review findings on the #3459 fix:

- backend/sandbox was described as "gitignored runtime state" but no ignore
  rule actually matched it. Add an anchored `/sandbox/` to backend/.gitignore
  (anchored so it does NOT shadow the source package
  backend/packages/harness/deerflow/sandbox/) so sandbox artifacts created at
  runtime can't pollute the working tree or be committed by accident. New test
  asserts content under backend/sandbox is ignored, making the claim verifiable.

- The launcher invariant test only proved the sandbox mkdir exists somewhere,
  not that it runs before uvicorn starts. Add an order test (sandbox mkdir line
  must precede the `uv run uvicorn` launch) so a future edit can't move the
  mkdir below the launch and silently reintroduce the crash.

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* test(dev): fix reload-exclude parser to handle serve.sh's quoted flag bundle

The previous autofix tokenized each whole line with shlex, but serve.sh packs
every flag into a single double-quoted `GATEWAY_EXTRA_FLAGS="..."` assignment.
shlex collapses that into one token, so no `--reload-exclude` flag is found and
`test_launcher_precreates_every_absolute_reload_exclude[scripts/serve.sh]`
failed CI with "expected at least one absolute reload-exclude".

Parse `--reload-exclude` with a regex that matches a balanced single/double
quoted group or a bare token, so the assignment's surrounding `"` is never
swallowed into the value. This recovers all three serve.sh excludes (the prior
regex also silently dropped the last `$BACKEND_RUNTIME_HOME` because the
adjacent closing quote broke shlex) while still covering dev-entrypoint.sh and
the space-separated `--reload-exclude <value>` form.

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `docker/dev-entrypoint.sh`
  L67: # Keep runtime-owned files out of uvicorn's reload watcher. Each excluded path
  L68: # must exist before uvicorn starts so watchfiles treats it as an excluded
  L69: # directory, not as a plain glob pattern — on Python 3.12, globbing an absolute
  L70: # pattern raises NotImplementedError and crashes startup (#3459 / #3454). That
  L71: # means `sandbox` must be created here too, not just `.deer-flow`.
- `scripts/serve.sh`
  L300: # `backend/sandbox` is excluded from uvicorn's reload watcher below. uvicorn only
  L301: # excludes an absolute path directly when it already exists as a directory;
  L302: # otherwise it globs the pattern, and Python 3.12's pathlib rejects absolute glob
  L303: # patterns with NotImplementedError, crashing `make dev` on a fresh checkout
  L304: # (#3459 / #3454). Creating it here keeps every absolute exclude on the is_dir path.

## 18bbb82f 2026-06-09 tanghang97
Fix 'make dev' failure in Windows environment (#3236)

* fix: Solving the problem of "make dev" failing to start in Windows environment

* fix: revert the change to the startup_config and fix the lint errors

* fix: Address Copilot review feedback

- Validate wait-for-port input and avoid PowerShell port interpolation
- Require Python 3 in serve.sh launcher detection
- Keep Windows event loop policy setup in sitecustomize only
- Clarify sitecustomize process-wide backend behavior

- `scripts/serve.sh`
  L347: # Pick a runnable Python for the extras detector. On Windows/Git Bash,
  L348: # `python3` can resolve to the Microsoft Store alias in WindowsApps, which is
  L349: # present on PATH but not executable from Bash.
- `scripts/wait-for-port.sh`

## 05ae4467 2026-06-10 Xinmin Zeng
fix(docker): default Gateway to a single worker to prevent multi-worker breakage (#3475)

The default `make up` started the Gateway with `--workers 4`, but run state
(RunManager and the stream bridge) is held in-process and nginx uses no sticky
sessions. With the default config, same-run requests scatter across workers that
each keep their own run state, breaking run cancellation (409), SSE reconnect
(hangs on heartbeats), multitask de-duplication, and IM channels (duplicate
replies). The shared cross-worker stream bridge does not exist yet.

Default GATEWAY_WORKERS to 1 so the out-of-the-box deployment is correct,
document the single-worker boundary in the README, and add a regression test
pinning the default while keeping it overridable. This is a stop-gap, not a
multi-worker implementation; the full fix (shared run state + stream bridge) is
tracked in #3191.

Refs #3239, #3260

- `docker/docker-compose.yaml`
  L75: # Gateway hosts the agent runtime with in-process RunManager + StreamBridge
  L76: # singletons -- run state lives in this worker's memory. Default to a single
  L77: # worker: with >1 worker and no nginx sticky sessions, run cancel, SSE
  L78: # reconnect, request dedup, and per-worker IM channel services all break
  L79: # across workers until a shared (e.g. redis) stream bridge lands, which is
  L80: # not yet implemented. Override GATEWAY_WORKERS only once that is in place.

## 2d5f0787 2026-06-11 Willem Jiang
Update lint-check.yml with the job setting

- `.github/workflows/lint-check.yml`

