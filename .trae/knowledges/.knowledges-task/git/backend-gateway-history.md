## 80e210f5 2026-04-18 Hinotobi
[security] fix(uploads): require explicit opt-in for host-side document conversion (#2332)

* fix: disable host-side upload conversion by default

* fix: address PR review comments on upload conversion gate

- `backend/app/gateway/routers/uploads.py`
  L62: """Read a value from the uploads config, supporting dict and attribute access."""
  L71: """Return whether automatic host-side document conversion is enabled.
  L75: """

## 4e724101 2026-04-23 JerryChaox
fix(gateway): bound lifespan shutdown hooks to prevent worker hang under uvicorn reload (#2331)

* fix(gateway): bound lifespan shutdown hooks to prevent worker hang

Gateway worker can hang indefinitely in `uvicorn --reload` mode with
the listening socket still bound — all /api/* requests return 504,
and SIGKILL is the only recovery.

Root cause (py-spy dump from a reproduction showed 16+ stacked frames
of signal_handler -> Event.set -> threading.Lock.__enter__ on the
main thread): CPython's `threading.Event` uses `Condition(Lock())`
where the inner Lock is non-reentrant. uvicorn's BaseReload signal
handler calls `should_exit.set()` directly from signal context; if a
second signal (SIGTERM/SIGHUP from the reload supervisor, or
watchfiles-triggered reload) arrives while the first handler holds
the Lock, the reentrant call deadlocks on itself.

The reload supervisor keeps sending those signals only when the
worker fails to exit promptly. DeerFlow's lifespan currently awaits
`stop_channel_service()` with no timeout; if a channel's `stop()`
stalls (e.g. Feishu/Slack WebSocket waiting for an ack), the worker
can't exit, the supervisor keeps signaling, and the deadlock becomes
reachable.

This is a defense-in-depth fix — it does not repair the upstream
uvicorn/CPython issue, but it ensures DeerFlow's lifespan exits
within a bounded window so the supervisor has no reason to keep
firing signals. No behavior change on the happy path.

Wraps the shutdown hook in `asyncio.wait_for(timeout=5.0)` and logs
a warning on timeout before proceeding to worker exit.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* Update backend/app/gateway/app.py

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* style: apply make format (ruff) to test assertions

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- `backend/app/gateway/app.py`
  L36: # Upper bound (seconds) each lifespan shutdown hook is allowed to run.
  L37: # Bounds worker exit time so uvicorn's reload supervisor does not keep
  L38: # firing signals into a worker that is stuck waiting for shutdown cleanup.
  L72: # Stop channel service on shutdown (bounded to prevent worker hang)

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

- `backend/app/gateway/routers/agents.py`
  L280: # Use model_fields_set to distinguish "field omitted" from "explicitly set to null".
  L281: # This is critical for skills where None means "inherit all" (not "don't change").
  L298: # skills: None = inherit all, [] = no skills, ["a","b"] = whitelist

## 11f557a2 2026-04-24 Airene Fang
feat(trace):Add run_name to the trace info for system agents. (#2492)

* feat(trace): Add `run_name` to the trace info for suggestions and memory.

before(in langsmith):
CodexChatModel
CodexChatModel
lead_agent
after:
suggest_agent
memory_agent
lead_agent

feat(trace): Add `run_name` to the trace info for suggestions and memory.

before(in langsmith):
CodexChatModel
CodexChatModel
lead_agent
after:
suggest_agent
memory_agent
lead_agent

* feat(trace): Add `run_name` to the trace info for system agents.

before(in langsmith):
CodexChatModel
CodexChatModel
CodexChatModel
CodexChatModel
lead_agent
after:
suggest_agent
title_agent
security_agent
memory_agent
lead_agent

* chore(code format):code format

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/app/gateway/routers/suggestions.py`

## b9709934 2026-04-24 DanielWalnut
fix: read lead agent options from context (#2515)

* fix: read lead agent options from context

* fix: validate runtime context config

- `backend/app/gateway/services.py`
  L168: # Honour an explicit agent_name in the active runtime options container.

## 410f0c48 2026-04-25 ming1523
fix(channels): accept single slack allowed user (#2481)

* fix(channels): accept single slack allowed user

* docs: address Slack allowed_users review notes

* ci: rerun backend unit tests

* docs: clarify Slack allowed_users config

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/app/channels/slack.py`

## 9dc25987 2026-04-26 Willem Jiang
fix(channles):update the logger for the channel config (#2524)

* fix(channles):update the logger for the channel config

* fix(channels): normalize credential values and add tests for disabled-but-configured warning

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/dfc0a566-aa59-49f9-a74d-610292fb0a63

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* fix the backend lint error

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

- `backend/app/channels/service.py`
  L26: # Keys that indicate a user has configured credentials for a channel.

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

- `backend/app/gateway/app.py`
  L217: # Feedback API is mounted at /api/threads/{thread_id}/runs/{run_id}/feedback
- `backend/app/gateway/deps.py`
  L38: # Initialize persistence engine BEFORE checkpointer so that
  L39: # auto-create-database logic runs first (postgres backend).
  L46: # Initialize repositories — one get_session_factory() call for all.
  L64: # Run event store (has its own factory with config-driven backend selection)
  L68: # RunManager with store backing for persistence
  L78: # Getters -- called by routers per-request
  L83: """Create a FastAPI dependency that returns ``app.state.<attr>`` or 503."""
  L112: """Build a :class:`RunContext` from ``app.state`` singletons.
  L118: """
  L131: """Extract user identity from request.
  L135: """
- `backend/app/gateway/routers/feedback.py`
  L1: """Feedback endpoints — create, list, stats, delete.
  L5: """
  L21: # ---------------------------------------------------------------------------
  L22: # Request / response models
  L23: # ---------------------------------------------------------------------------
  L50: # ---------------------------------------------------------------------------
  L51: # Endpoints
  L52: # ---------------------------------------------------------------------------
  L62: """Submit feedback (thumbs-up/down) for a run."""
  L68: # Validate run exists and belongs to thread
  L93: """List all feedback for a run."""
  L104: """Get aggregated feedback stats (positive/negative counts) for a run."""
  L116: """Delete a feedback record."""
  L118: # Verify feedback belongs to the specified thread/run before deleting
- `backend/app/gateway/routers/thread_runs.py`
  L271: # ---------------------------------------------------------------------------
  L272: # Messages / Events / Token usage endpoints
  L273: # ---------------------------------------------------------------------------
  L284: """Return displayable messages for a thread (across all runs)."""
  L291: """Return displayable messages for a specific run."""
  L304: """Return the full event stream for a run (debug/audit)."""
  L312: """Thread-level token usage aggregation."""
- `backend/app/gateway/routers/threads.py`
  L189: # Remove thread_meta row (best-effort) — required for sqlite backend
  L190: # so the deleted thread no longer appears in /threads/search.
  L215: # Idempotency: return existing record when already present
  L226: # Write thread_meta so the thread appears in /threads/search immediately
  L311: # Re-read to get the merged metadata + refreshed updated_at
  L348: # If the thread exists in the checkpointer but not in thread_meta (e.g.
  L349: # legacy data created before thread_meta adoption), synthesize a minimal
  L350: # record from the checkpoint metadata.
  L497: # Sync title changes through the ThreadMetaStore abstraction so /threads/search
  L498: # reflects them immediately in both sqlite and memory backends.
  L518: """Get checkpoint history for a thread.
  L525: """
  L548: # Build values from checkpoint channel_values
  L555: # Attach messages from checkpointer only for the latest checkpoint
  L566: # Strip LangGraph internal keys from metadata
  L568: # Keep step for ordering context
- `backend/app/gateway/services.py`
  L216: # Resolve follow_up_to_run_id: explicit from request, or auto-detect from latest successful run
  L227: # Enrich base context with per-run field
  L246: # Upsert thread metadata so the thread appears in /threads/search,
  L247: # even for threads that were never explicitly created via POST /threads
  L248: # (e.g. stateless runs).
  L307: # Title sync is handled by worker.py's finally block which reads the
  L308: # title from the checkpoint and calls thread_meta_repo.update_display_name
  L309: # after the run completes.
- `backend/app/gateway/utils.py`
  L1: """Shared utility helpers for the Gateway layer."""
  L5: """Strip control characters to prevent log injection."""

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

- `backend/app/gateway/app.py`
  L50: """Auto-create the admin user on first boot if no users exist.
  L67: """
  L74: """Write the password to a 0600 file and log the path (never the secret)."""
  L95: # Admin exists but setup never completed — reset password so operator
  L96: # can always find it in the console without needing the CLI.
  L97: # Multi-worker guard: if admin was created less than 30s ago, another
  L98: # worker just created it and will print the password — skip reset.
  L118: # LangGraph store orphan migration — non-fatal.
  L119: # This covers the "no-auth → with-auth" upgrade path for users
  L120: # whose existing LangGraph thread metadata has no owner_id set.
  L132: """Paginated async iterator over a LangGraph store namespace.
  L138: """
  L152: """Migrate LangGraph store threads with no owner_id to the given admin.
  L156: """
  L187: # Ensure admin user exists (auto-create on first boot)
  L188: # Must run AFTER langgraph_runtime so app.state.store is available for thread migration
  L310: # Auth: reject unauthenticated requests to non-public paths (fail-closed safety net)
  L313: # CSRF: Double Submit Cookie pattern for state-changing requests
  L316: # CORS: when GATEWAY_CORS_ORIGINS is set (dev without nginx), add CORS middleware.
  L317: # In production, nginx handles CORS and no middleware is needed.
  ... (truncated)
- `backend/app/gateway/auth/__init__.py`
  L1: """Authentication module for DeerFlow.
  L7: """
  L19: # Config
  L23: # Errors
  L27: # JWT
  L31: # Password
  L34: # Models
  L37: # Providers
  L40: # Repository
- `backend/app/gateway/auth/config.py`
  L1: """Authentication configuration for DeerFlow."""
  L16: """JWT and auth-related configuration. Parsed once at startup.
  L22: """
  L37: """Get the global AuthConfig instance. Parses from env on first call."""
  L55: """Set the global AuthConfig instance (for testing)."""
- `backend/app/gateway/auth/credential_file.py`
  L1: """Write initial admin credentials to a restricted file instead of logs.
  L9: """
  L22: """Write the admin email + password to ``{base_dir}/admin_initial_credentials.txt``.
  L33: """
  L41: # Atomic 0600 create-or-truncate. O_TRUNC (not O_EXCL) so the
  L42: # reset-password path can rewrite an existing file without a
  L43: # separate unlink-then-create dance.
- `backend/app/gateway/auth/errors.py`
  L1: """Typed error definitions for auth module.
  L6: """
  L14: """Exhaustive list of auth error conditions."""
  L26: """Exhaustive list of JWT decode failure reasons."""
  L34: """Structured error response — replaces bare `detail` strings."""
  L41: """Map TokenError to AuthErrorCode — single source of truth."""
- `backend/app/gateway/auth/jwt.py`
  L1: """JWT token creation and verification."""
  L13: """JWT token payload."""
  L22: """Create a JWT access token.
  L31: """
  L41: """Decode and validate a JWT token.
  L45: """
- `backend/app/gateway/auth/local_provider.py`
  L1: """Local email/password authentication provider."""
  L10: """Email/password authentication provider using local database."""
  L13: """Initialize with a UserRepository.
  L17: """
  L21: """Authenticate with email and password.
  L28: """
  L40: # OAuth user without local password
  L49: """Get user by ID."""
  L53: """Create a new local user.
  L63: """
  L74: """Get user by OAuth provider and ID."""
  L78: """Return total number of registered users."""
  L82: """Update an existing user."""
  L86: """Get user by email."""
- `backend/app/gateway/auth/models.py`
  L1: """User Pydantic models for authentication."""
  L11: """Return current UTC time (timezone-aware)."""
  L16: """Internal user representation."""
  L26: # OAuth linkage (optional)
  L30: # Auth lifecycle
  L36: """Response model for user info endpoint."""
- `backend/app/gateway/auth/password.py`
  L1: """Password hashing utilities using bcrypt directly."""
  L9: """Hash a password using bcrypt."""
  L14: """Verify a password against its hash."""
  L19: """Hash a password using bcrypt (non-blocking).
  L23: """
  L28: """Verify a password against its hash (non-blocking).
  L32: """
- `backend/app/gateway/auth/providers.py`
  L1: """Auth provider abstraction."""
  L7: """Abstract base class for authentication providers."""
  L11: """Authenticate user with given credentials.
  L14: """
  L19: """Retrieve user by ID."""
  L23: # Import User at runtime to avoid circular imports
- `backend/app/gateway/auth/repositories/base.py`
  L1: """User repository interface for abstracting database operations."""
  L9: """Raised when a user repository operation targets a non-existent row.
  L15: """
  L19: """Abstract interface for user data storage.
  L23: """
  L27: """Create a new user.
  L37: """
  L42: """Get user by ID.
  L49: """
  L54: """Get user by email.
  L61: """
  L66: """Update an existing user.
  L78: """
  L83: """Return total number of registered users."""
  L88: """Get user by OAuth provider and ID.
  L96: """
- `backend/app/gateway/auth/repositories/sqlite.py`
  L1: """SQLAlchemy-backed UserRepository implementation.
  L11: """
  L28: """Async user repository backed by the shared SQLAlchemy engine."""
  L33: # ── Converters ────────────────────────────────────────────────────
  L42: # SQLite loses tzinfo on read; reattach UTC so downstream
  L43: # code can compare timestamps reliably.
  L65: # ── CRUD ──────────────────────────────────────────────────────────
  L68: """Insert a new user. Raises ``ValueError`` on duplicate email."""
  L95: # Hard fail on concurrent delete: callers (reset_admin,
  L96: # password change handlers, _ensure_admin_user) all
  L97: # fetched the user just before this call, so a missing
  L98: # row here means the row vanished underneath us. Silent
  L99: # success would let the caller log "password reset" for
  L100: # a row that no longer exists.
- `backend/app/gateway/auth/reset_admin.py`
  L1: """CLI tool to reset an admin password.
  L10: """
  L48: # Find first admin via direct SELECT — repository does not
  L49: # expose a "first admin" helper and we do not want to add
  L50: # one just for this CLI.
- `backend/app/gateway/auth_middleware.py`
  L1: """Global authentication middleware — fail-closed safety net.
  L10: """
  L23: # Paths that never require authentication.
  L31: # Exact auth paths that are public (login/register/status check).
  L32: # /api/v1/auth/me, /api/v1/auth/change-password etc. are NOT public.
  L51: """Strict auth gate: reject requests without a valid session.
  L68: """
  L77: # Non-public path: require session cookie
  L89: # Strict JWT validation: reject junk/expired tokens with 401
  L90: # right here instead of silently passing through. This closes
  L91: # the "junk cookie bypass" gap (AUTH_TEST_PLAN test 7.5.8):
  L92: # without this, non-isolation routes like /api/models would
  L93: # accept any cookie-shaped string as authentication.
  L94: #
  L95: # We call the *strict* resolver so that fine-grained error
  L96: # codes (token_expired, token_invalid, user_not_found, …)
  L97: # propagate from AuthErrorCode, not get flattened into one
  L98: # generic code. BaseHTTPMiddleware doesn't let HTTPException
  L99: # bubble up, so we catch and render it as JSONResponse here.
  L107: # Stamp both request.state.user (for the contextvar pattern)
  ... (truncated)
- `backend/app/gateway/authz.py`
  L1: """Authorization decorators and context for DeerFlow.
  L17: # User is authenticated and has threads:read permission
  L28: """
  L45: # Permission constants
  L47: """Permission constants for resource:action format."""
  L49: # Threads
  L54: # Runs
  L61: """Authentication context for the current request.
  L68: """
  L78: """Check if user is authenticated."""
  L82: """Check if context has permission for resource:action.
  L90: """
  L95: """Get user or raise 401.
  L99: """
  L106: """Get AuthContext from request state."""
  L121: """Authenticate request and return AuthContext.
  L125: """
  L132: # In future, permissions could be stored in user record
  L137: """Decorator that authenticates the request and sets AuthContext.
  L151: """
  ... (truncated)
- `backend/app/gateway/csrf_middleware.py`
  L1: """CSRF protection middleware for FastAPI.
  L5: """
  L21: """Detect whether the original client request was made over HTTPS."""
  L26: """Generate a secure random CSRF token."""
  L31: """Determine if a request needs CSRF validation.
  L35: """
  L40: # Exempt /api/v1/auth/me endpoint
  L56: """Check if the request is to an auth endpoint.
  L59: """
  L64: """Middleware that implements CSRF protection using Double Submit Cookie pattern."""
  L90: # For auth endpoints that set up session, also set CSRF cookie
  L92: # Generate a new CSRF token for the session
  L107: """Get the CSRF token from the current request's cookies.
  L111: """
- `backend/app/gateway/deps.py`
  L135: # ---------------------------------------------------------------------------
  L136: # Auth helpers (used by authz.py and auth middleware)
  L137: # ---------------------------------------------------------------------------
  L139: # Cached singletons to avoid repeated instantiation per request
  L145: """Get or create the cached LocalAuthProvider singleton.
  L149: """
  L167: """Get the current authenticated user from the request cookie.
  L170: """
  L196: # Token version mismatch → password was changed, token is stale
  L207: """Get optional authenticated user from request.
  L210: """
  L218: """Extract user_id from request cookie, or None if not authenticated.
- `backend/app/gateway/langgraph_auth.py`
  L1: """LangGraph Server auth handler — shares JWT logic with Gateway.
  L11: """
  L23: # Methods that require CSRF validation (state-changing per RFC 7231).
  L28: """Enforce Double Submit Cookie CSRF check for state-changing requests.
  L32: """
  L55: """Validate the session cookie, decode JWT, and check token_version.
  L60: """
  L61: # CSRF check before authentication so forged cross-site requests
  L62: # are rejected early, even if the cookie carries a valid JWT.
  L96: """Inject owner_id metadata on writes; filter by owner_id on reads.
  L100: """
  L101: # On create/update: stamp owner_id into metadata
  L105: # Return filter dict — LangGraph applies it to search/read/delete
- `backend/app/gateway/routers/artifacts.py`
- `backend/app/gateway/routers/auth.py`
  L1: """Authentication endpoints."""
  L26: # ── Request/Response Models ──────────────────────────────────────────────
  L30: """Response model for login — token only lives in HttpOnly cookie."""
  L36: # Top common-password blocklist. Drawn from the public SecLists "10k worst
  L37: # passwords" set, lowercased + length>=8 only (shorter ones already fail
  L38: # the min_length check). Kept tight on purpose: this is the **lower bound**
  L39: # defense, not a full HIBP / passlib check, and runs in-process per request.
  L83: """Case-insensitive blocklist check.
  L89: """
  L94: """Pydantic field-validator body shared by Register + ChangePassword.
  L100: """
  L107: """Request model for user registration."""
  L116: """Request model for password change (also handles setup flow)."""
  L126: """Generic message response."""
  L131: # ── Helpers ───────────────────────────────────────────────────────────────
  L135: """Set the access_token HttpOnly cookie on the response."""
  L148: # ── Rate Limiting ────────────────────────────────────────────────────────
  L149: # In-process dict — not shared across workers. Sufficient for single-worker deployments.
  L154: # ip → (fail_count, lock_until_timestamp)
  L159: """Parse ``AUTH_TRUSTED_PROXIES`` env var into a list of ip_network objects.
  ... (truncated)
- `backend/app/gateway/routers/feedback.py`
- `backend/app/gateway/routers/suggestions.py`
- `backend/app/gateway/routers/thread_runs.py`
- `backend/app/gateway/routers/threads.py`
  L33: # Metadata keys that the server controls; clients are not allowed to set
  L34: # them. Pydantic ``@field_validator("metadata")`` strips them on every
  L35: # inbound model below so a malicious client cannot reflect a forged
  L36: # owner identity through the API surface. Defense-in-depth — the
  L37: # row-level invariant is still ``threads_meta.owner_id`` populated from
  L38: # the auth contextvar; this list closes the metadata-blob echo gap.
  L43: """Return ``metadata`` with server-controlled keys removed."""
  L236: # ``body.metadata`` is already stripped of server-reserved keys by
  L237: # ``ThreadCreateRequest._strip_reserved`` — see the model definition.
  L330: # ``body.metadata`` already stripped by ``ThreadPatchRequest._strip_reserved``.
- `backend/app/gateway/routers/uploads.py`

## 848ace98 2026-04-11 Copilot
feat: replace auto-admin creation with secure interactive first-boot setup (#2063)

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

* feat: replace auto-admin creation with interactive setup flow

On first boot, instead of auto-creating admin@deerflow.dev with a
random password written to a credential file, DeerFlow now redirects
to /setup where the user creates the admin account interactively.

Backend:
- Remove auto admin creation from _ensure_admin_user (now only runs
  orphan thread migration when an admin already exists)
- Add POST /api/v1/auth/initialize endpoint (public, only callable
  when 0 users exist; auto-logs in after creation)
- Add /api/v1/auth/initialize to public paths in auth_middleware.py
  and CSRF exempt paths in csrf_middleware.py
- Update test_ensure_admin.py to match new behavior
- Add test_initialize_admin.py with 8 tests for the new endpoint

Frontend:
- Add system_setup_required to AuthResult type
- getServerSideUser() checks setup-status when unauthenticated
- Auth layout allows system_setup_required (renders children)
- Workspace layout redirects system_setup_required → /setup
- Login page redirects to /setup when system not initialized
- Setup page detects mode via isAuthenticated: unauth = create-admin
  form (calls /initialize), auth = change-password form (existing)

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/9c2471c5-d6e9-4ada-9192-61b56007b8d7

Co-authored-by: foreleven <4785594+foreleven@users.noreply.github.com>

* fix: add cleanup flags to useEffect async fetches in setup/login pages

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/9c2471c5-d6e9-4ada-9192-61b56007b8d7

Co-authored-by: foreleven <4785594+foreleven@users.noreply.github.com>

* fix: address reviewer feedback on /initialize endpoint security and robustness

1. Concurrency/register-blocking: switch setup-status and /initialize to
   check admin_count (via new count_admin_users()) instead of total
   user_count — /register can no longer block admin initialization

2. Dedicated error code: add SYSTEM_ALREADY_INITIALIZED to AuthErrorCode
   and use it in /initialize 409 responses; add to frontend types

3. Init token security: generate a one-time token at startup (logged to
   stdout) and require it in the /initialize request body — prevents
   an attacker from claiming admin on an exposed first-boot instance

4. Setup-status fetch timeout: apply SSR_AUTH_TIMEOUT_MS abort-controller
   pattern to the setup-status fetch in server.ts (same as /auth/me)

Backend repo/provider: add count_admin_users() to base, SQLite, and
LocalAuthProvider. Tests updated + new token-validation/register-blocking
test cases added.

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/b9f531fc-8ed3-41db-b416-237f243b45fd

Co-authored-by: foreleven <4785594+foreleven@users.noreply.github.com>

* fix: address code review nits — move secrets import, add INVALID_INIT_TOKEN error code, fix test assertions

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/b9f531fc-8ed3-41db-b416-237f243b45fd

Co-authored-by: foreleven <4785594+foreleven@users.noreply.github.com>

* refactor: remove init_token generation and validation from admin setup flow

* fix: re-apply init_token security for /initialize endpoint

Re-adds the one-time init_token requirement to the /initialize endpoint,
building on the human's UI improvements in 5eeeb09. This addresses the
two remaining unresolved review threads:

1. Dedicated error code (SYSTEM_ALREADY_INITIALIZED + INVALID_INIT_TOKEN)
2. Init token security gate — requires the token logged at startup

Changes:
- errors.py: re-add INVALID_INIT_TOKEN error code
- routers/auth.py: re-add `import secrets`, `init_token` field,
  token validation with secrets.compare_digest, and token consumption
- app.py: re-add token generation/logging and app.state.init_token = None
- setup/page.tsx: re-add initToken state + input field (human's UI kept)
- types.ts: re-add invalid_init_token error code
- test_initialize_admin.py: restore full token test coverage
- test_ensure_admin.py: restore init_token assertions

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/646fb5c0-ec09-41aa-9fe9-e6f7c32364e8

Co-authored-by: foreleven <4785594+foreleven@users.noreply.github.com>

* fix: make init_token optional (403 not 422 on missing), don't consume token on error paths

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/646fb5c0-ec09-41aa-9fe9-e6f7c32364e8

Co-authored-by: foreleven <4785594+foreleven@users.noreply.github.com>

* refactor: remove redundant skill-related functions and documentation

---------

Co-authored-by: rayhpeng <rayhpeng@gmail.com>
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
Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: foreleven <4785594+foreleven@users.noreply.github.com>
Co-authored-by: jiangfeng.11 <jiangfeng.11@bytedance.com>

- `backend/app/gateway/app.py`
  L49: """Startup hook: generate init token on first boot; migrate orphan threads otherwise.
  L89: # Admin already exists — run orphan thread migration for any
  L90: # LangGraph thread metadata that pre-dates the auth module.
  L375: # Ensure init_token always exists on app.state (None until lifespan sets it
  L376: # if no admin is found).  This prevents AttributeError in tests that don't
  L377: # run the full lifespan.
- `backend/app/gateway/auth/errors.py`
- `backend/app/gateway/auth/local_provider.py`
  L82: """Return number of admin users."""
- `backend/app/gateway/auth/repositories/base.py`
  L88: """Return number of users with system_role == 'admin'."""
- `backend/app/gateway/auth/repositories/sqlite.py`
- `backend/app/gateway/auth_middleware.py`
- `backend/app/gateway/csrf_middleware.py`
- `backend/app/gateway/routers/auth.py`
  L382: """Check if an admin account exists. Returns needs_setup=True when no admin exists."""
  L388: """Request model for first-boot admin account creation."""
  L399: """Create the first admin account on initial system setup.
  L407: """
  L408: # Validate the one-time initialization token.  The token is generated
  L409: # at startup and stored in app.state.init_token; it is consumed here on
  L410: # the first successful call so it cannot be replayed.
  L411: # Using str | None allows a missing/null token to return 403 (not 422),
  L412: # giving a consistent error response regardless of whether the token is
  L413: # absent or incorrect.
  L424: # Do NOT consume the token on this error path — consuming it here
  L425: # would allow an attacker to exhaust the token by calling with the
  L426: # correct token when admin already exists (denial-of-service).
  L435: # DB unique-constraint race: another concurrent request beat us.
  L436: # Do NOT consume the token here for the same reason as above.
  L442: # Consume the token only after successful initialization — this is the
  L443: # single place where one-time use is enforced.

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

- `backend/app/gateway/app.py`
  L110: # This covers the "no-auth → with-auth" upgrade path for users
  L111: # whose existing LangGraph thread metadata has no user_id set.
  L143: """Migrate LangGraph store threads with no user_id to the given admin.
- `backend/app/gateway/authz.py`
  L236: # ``user_id`` is NULL (shared / pre-auth data), so this is
  L238: # row with a *different* user_id triggers 404.
- `backend/app/gateway/deps.py`
  L83: # Getters – called by routers per-request
  L114: """Return the thread metadata store (SQL or memory-backed)."""
- `backend/app/gateway/langgraph_auth.py`
  L96: """Inject user_id metadata on writes; filter by user_id on reads.
  L101: # On create/update: stamp user_id into metadata
- `backend/app/gateway/routers/feedback.py`
  L69: """Create or update feedback for a run (idempotent)."""
  L99: """Delete the current user's feedback for a run."""
- `backend/app/gateway/routers/thread_runs.py`
  L294: """Return displayable messages for a thread (across all runs), with feedback attached."""
  L298: # Attach feedback to the last AI message of each run
  L303: # Find the last ai_message per run_id
  L309: # Attach feedback field
- `backend/app/gateway/routers/threads.py`
  L38: # row-level invariant is still ``threads_meta.user_id`` populated from
  L406: # ---------------------------------------------------------------------------
  L407: # Event-store-backed message loader
  L408: # ---------------------------------------------------------------------------
  L417: """Recover the inner ToolMessage text from a legacy ``str(Command(...))`` repr.
  L424: """
  L432: """Load the full message stream for ``thread_id`` from the event store.
  L478: """
  L492: # Batch by page_size to keep memory bounded for very long threads.
  L512: # Build the message list; track the final ``ai_message`` index per run so
  L513: # feedback can be attached at the right position (matches thread_runs.py).
  L535: # Attach feedback to the final ai_message of each run. If the feedback
  L536: # subsystem is unavailable, leave the ``feedback`` field absent entirely
  L537: # so the frontend hides the button rather than showing it over a broken
  L538: # write path.
  L605: # Prefer event-store messages: append-only, immune to summarization.
  L729: # Load the full event-store message stream once; attach to the latest
  L730: # checkpoint entry only (matching the prior semantics). The event store
  L731: # is append-only and immune to summarization.
  L757: # Attach messages only to the latest checkpoint. Prefer the
  ... (truncated)
- `backend/app/gateway/services.py`
  L308: # title from the checkpoint and calls thread_store.update_display_name

## 00a90bbd 2026-04-12 foreleven
refactor: Remove init_token handling from admin initialization logic and related tests

- `backend/app/gateway/app.py`
  L49: """Startup hook: handle first boot and migrate orphan threads otherwise.
- `backend/app/gateway/auth/errors.py`
- `backend/app/gateway/routers/auth.py`

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

- `backend/app/channels/feishu.py`
- `backend/app/channels/manager.py`
- `backend/app/gateway/path_utils.py`
- `backend/app/gateway/routers/memory.py`
- `backend/app/gateway/routers/runs.py`
  L91: # ---------------------------------------------------------------------------
  L92: # Run-scoped read endpoints
  L93: # ---------------------------------------------------------------------------
  L97: """Fetch run by run_id with user ownership check. Raises 404 if not found."""
  L114: """Return paginated messages for a run (cursor-based).
  L122: """
  L139: """Return all feedback for a run."""
- `backend/app/gateway/routers/thread_runs.py`
  L336: """Return paginated messages for a specific run.
  L339: """
- `backend/app/gateway/routers/threads.py`
  L590: # Attach messages only to the latest checkpoint entry.
- `backend/app/gateway/routers/uploads.py`

## db5ad863 2026-04-19 JeffJiang
feat: enhance chat history loading with new hooks and UI components (#2338)

* Refactor API fetch calls to use a unified fetch function; enhance chat history loading with new hooks and UI components

- Replaced `fetchWithAuth` with a generic `fetch` function across various API modules for consistency.
- Updated `useThreadStream` and `useThreadHistory` hooks to manage chat history loading, including loading states and pagination.
- Introduced `LoadMoreHistoryIndicator` component for better user experience when loading more chat history.
- Enhanced message handling in `MessageList` to accommodate new loading states and history management.
- Added support for run messages in the thread context, improving the overall message handling logic.
- Updated translations for loading indicators in English and Chinese.

* Fix test assertions for run ordering in RunManager tests

- Updated assertions in `test_list_by_thread` to reflect correct ordering of runs.
- Modified `test_list_by_thread_is_stable_when_timestamps_tie` to ensure stable ordering when timestamps are tied.

- `backend/app/gateway/deps.py`
- `backend/app/gateway/routers/runs.py`
- `backend/app/gateway/routers/thread_runs.py`
- `backend/app/gateway/routers/uploads.py`
- `backend/app/gateway/services.py`

## 3b71e2d3 2026-04-26 JeffJiang
feat: add request parameter to generate_suggestions endpoint for enhanced context

Co-authored-by: Copilot <copilot@github.com>

- `backend/app/gateway/routers/suggestions.py`

## 829e82a9 2026-04-26 Willem Jiang
fix the lint error in backend

- `backend/app/gateway/routers/threads.py`
- `backend/app/gateway/services.py`

## 653b7ae1 2026-04-26 Willem Jiang
Apply the code reviewer suggestion of abstractmethod

- `backend/app/gateway/auth/providers.py`
- `backend/app/gateway/auth/repositories/base.py`

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

- `backend/app/channels/__init__.py`
- `backend/app/channels/manager.py`
  L1: """ChannelManager — consumes inbound messages and dispatches them to the DeerFlow agent via Gateway."""
  L672: """Create a new thread through Gateway and store the mapping."""
  L889: # Create a new thread through Gateway

## ac18b9c4 2026-04-26 Willem Jiang
Apply the code reviewer suggestion of abstractmethod

- `backend/app/gateway/auth/repositories/base.py`

## eba6c0ea 2026-04-26 Willem Jiang
fix unit tests of test_upload_files and test_shutdown

- `backend/app/gateway/app.py`
  L78: # Auth persistence may not be initialized in some test/boot paths.
  L79: # Skip admin migration work rather than failing gateway startup.
- `backend/app/gateway/authz.py`
  L123: """Create a minimal request-like object for direct unit calls.
  L127: """
  L168: # Unit tests may call decorated handlers directly without a
  L169: # FastAPI Request object. Inject a minimal request stub when
  L170: # the wrapped function declares `request`.
  L234: # Unit tests may call decorated route handlers directly without
  L235: # constructing a FastAPI Request object. Inject a minimal stub
  L236: # when the wrapped function declares `request`.

## da174dfd 2026-04-26 JeffJiang
feat: implement process-local internal authentication for Gateway and enhance CSRF handling

- `backend/app/channels/manager.py`
- `backend/app/gateway/app.py`
- `backend/app/gateway/auth_middleware.py`
- `backend/app/gateway/internal_auth.py`
  L1: """Process-local authentication for Gateway internal callers."""
  L15: """Return headers that authenticate same-process Gateway internal calls."""
  L20: """Return True when *token* matches the process-local internal token."""
  L25: """Return the synthetic user used for trusted internal channel calls."""

## ed9ebfac 2026-04-26 JeffJiang
fix: enforce 'request' parameter requirement in require_auth decorator

- `backend/app/gateway/authz.py`

## b8bc4826 2026-04-28 greatmengqi
refactor: root release config in gateway runtime (#2611)

Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>

- `backend/app/channels/service.py`
- `backend/app/gateway/app.py`
- `backend/app/gateway/deps.py`
  L34: """Return the app-scoped ``AppConfig`` stored on ``app.state``."""

## 4e4e4f92 2026-04-28 Willem Jiang
fix(security): harden auth system and fix run journal logic bug (#2593)

* fix(security): harden auth system and fix run journal logic bug

  - Fix inverted condition in RunJournal.on_chat_model_start that prevented
    first human message capture (not messages → messages)
  - Pre-hash passwords with SHA-256 before bcrypt to avoid silent 72-byte
    truncation vulnerability
  - Move load_dotenv() from module scope into get_auth_config() to prevent
    import-time os.environ mutation breaking test isolation
  - Return generic ‘Invalid token’ instead of exposing specific error
    variants (expired, malformed, invalid_signature) to clients
  - Make @require_auth independently enforce 401 instead of silently
    passing through when AuthMiddleware is absent
  - Rate-limit /setup-status endpoint with per-IP cooldown to mitigate
    initialization-state information leak
  - Document in-process rate limiter limitation for multi-worker deployments

* fix(security): return 429+Retry-After on setup-status rate limit, bound cooldown dict

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/070d0be8-99a5-46c8-85bb-6b81b5284021

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* fix(security): add versioned password hashes with auto-migration on login

  The SHA-256 pre-hash change silently broke verification for any existing
  bcrypt-only password hashes. Introduce a <N>$ prefix scheme so hashes
  are self-describing:

  - v2 (current): bcrypt(b64(sha256(password))) with $ prefix
  - v1 (legacy): plain bcrypt, prefixed $ or bare (no prefix)

  verify_password auto-detects the version and falls back to v1 for older
  hashes. LocalAuthProvider.authenticate() now rehashes legacy hashes to v2
  on successful login via needs_rehash(), so existing users upgrade
  transparently without a dedicated migration step.

* fix(auth): harden verify_password, best-effort rehash, update require_auth docstring, downgrade journal logging

- password.py: wrap bcrypt.checkpw in try/except → return False for malformed/corrupt hashes instead of crashing
- local_provider.py: wrap auto-rehash update_user() in try/except so transient DB errors don't fail valid logins
- authz.py: update require_auth docstring to reflect independent 401 enforcement
- journal.py: downgrade on_chat_model_start from INFO to DEBUG, log only metadata (batch_count, message_counts) instead of full serialized/messages content

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/48c5cf31-a4ab-418a-982a-6343c37bb299

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* fix(auth): address code review - narrow ValueError catch, add rehash warning log, rename num_batches

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/48c5cf31-a4ab-418a-982a-6343c37bb299

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>

- `backend/app/gateway/auth/config.py`
- `backend/app/gateway/auth/local_provider.py`
  L55: # Rehash is an opportunistic upgrade; a transient DB error must not
  L56: # prevent an otherwise-valid login from succeeding.
- `backend/app/gateway/auth/password.py`
  L1: """Password hashing utilities with versioned hash format.
  L14: """
  L28: """SHA-256 pre-hash to bypass bcrypt's 72-byte limit."""
  L33: """Hash a password (current version: v2 — SHA-256 + bcrypt)."""
  L39: """Verify a password, auto-detecting the hash version.
  L43: """
  L56: # bcrypt raises ValueError for malformed or corrupt hashes (e.g., invalid salt).
  L57: # Fail closed rather than crashing the request.
  L62: """Return True if the hash uses an older version and should be rehashed."""
- `backend/app/gateway/authz.py`
  L148: """Decorator that authenticates the request and enforces authentication.
- `backend/app/gateway/langgraph_auth.py`
- `backend/app/gateway/routers/auth.py`
  L149: # In-process dict — not shared across workers.
  L150: #
  L151: # **Limitation**: with multi-worker deployments (e.g., gunicorn -w N), each
  L152: # worker maintains its own lockout table, so an attacker effectively gets
  L153: # N × _MAX_LOGIN_ATTEMPTS guesses before being locked out everywhere. For
  L154: # production multi-worker setups, replace this with a shared store (Redis,
  L155: # database-backed counter) to enforce a true per-IP limit.
  L404: # Evict stale entries when dict grows too large to bound memory usage.
  L410: # If still too large after evicting expired entries, remove oldest half.

## 707ed328 2026-04-28 DanielWalnut
fix(skills): scan skill archives before install (#2561)

* fix(skills): scan skill archives before install

Fixes #2536

* fix(skills): scan archive support files before install

* style(skills): format archive installer

* fix(skills): address archive install review comments

- `backend/app/gateway/routers/skills.py`

## e82940c0 2026-04-28 greatmengqi
refactor: thread release config through lead path (#2612)

Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>

- `backend/app/gateway/deps.py`
- `backend/app/gateway/routers/models.py`
- `backend/app/gateway/routers/skills.py`
- `backend/app/gateway/routers/suggestions.py`
- `backend/app/gateway/routers/uploads.py`

## 64f4dc16 2026-04-28 Willem Jiang
fixed the CI build errors

- `backend/app/gateway/routers/skills.py`

## 11afd324 2026-04-28 Willem Jiang
Fix the log Injection error of skills.py

- `backend/app/gateway/routers/skills.py`

## 0691c4dd 2026-04-30 sunsine
fix(security): allow disabling API docs in production via GATEWAY_ENABLE_DOCS (#2651)

* fix(security): allow disabling API docs in production via GATEWAY_ENABLE_DOCS

Expose /docs, /redoc, and /openapi.json only when GATEWAY_ENABLE_DOCS=true
(default). Setting GATEWAY_ENABLE_DOCS=false disables all three endpoints,
preventing unauthorized API surface discovery in production deployments.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* test(security): add unit tests and docs for GATEWAY_ENABLE_DOCS

Add 7 tests covering default behavior, env var parsing (case-insensitive,
fail-closed), endpoint visibility, and health endpoint independence.
Update CONFIGURATION.md and CLAUDE.md with the new toggle.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* style(security): apply ruff formatting to gateway app.py

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/app/gateway/app.py`
- `backend/app/gateway/config.py`

## 08afdcb9 2026-04-30 He Wang
feat(channels): add DingTalk channel integration (#2628)

* feat(channels): add DingTalk channel integration

Add a new DingTalk messaging channel using the dingtalk-stream SDK
with Stream Push (WebSocket), requiring no public IP. Supports both
plain sampleMarkdown replies and optional AI Card streaming for a
typewriter effect when card_template_id is configured.

- Add DingTalkChannel implementation with token management, message
  routing, allowed_users filtering, and markdown adaptation
- Register dingtalk in channel service registry and capability map
- Propagate inbound metadata to outbound messages in ChannelManager
  for DingTalk sender context (sender_staff_id, conversation_type)
- Add dingtalk-stream dependency to pyproject.toml
- Add configuration examples in config.example.yaml and .env.example
- Update all README translations with setup instructions
- Add comprehensive test suite (test_dingtalk_channel.py) and
  metadata propagation test in test_channels.py
- Update backend CLAUDE.md to document DingTalk channel

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* fix(channels): address PR review feedback for DingTalk integration

- Replace runtime mutation of CHANNEL_CAPABILITIES with a
  `supports_streaming` property on the Channel base class, overridden
  by DingTalkChannel, FeishuChannel, and WeComChannel
- Store stream client reference and attempt graceful disconnect in
  stop(); guard _on_chatbot_message with _running check to prevent
  post-stop message processing
- Use msg.chat_id as the primary routing key in send/send_file via
  a shared _resolve_routing helper, with metadata as fallback
- Fix process() return type annotation from tuple[str, str] to
  tuple[int, str] to match AckMessage.STATUS_OK
- Protect _incoming_messages with threading.Lock for cross-thread
  safety between the Stream Push thread and the asyncio loop
- Re-add Docker Compose URL guidance removed during DingTalk setup
  docs addition in README.md
- Fix incomplete sentence in README_zh.md (missing verb "启用")

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* fix(docs): restore plain paragraph format for Docker Compose note

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* fix(channels): fix isinstance TypeError and add file size guard in DingTalk channel

Use tuple syntax for isinstance() type check to avoid runtime TypeError
with PEP 604 union types. Add upload size limit (20MB) before reading
files into memory. Narrow exception handlers to specific types.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* fix(channels): propagate markdown fallback errors and validate access token response

- Re-raise exceptions in _send_markdown_fallback to prevent partial
  deliveries (files sent without accompanying text)
- Validate _get_access_token response: reject non-dict bodies, empty
  tokens, and coerce invalid expireIn to a safe default
- Add tests for both fixes

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* fix(channels): validate upload response and broaden send_file exception handling

- Validate _upload_media JSON response: handle JSONDecodeError and
  non-dict payloads gracefully by returning None
- Broaden send_file exception tuple to include TypeError and
  AttributeError for unexpected JSON shapes

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* fix(channels): fix streaming race on channel registration and slim outbound metadata

- Register channel in service before calling start() to avoid race
  where background receiver publishes inbound before registration,
  causing manager to fall back to static CHANNEL_CAPABILITIES
- Strip known-large metadata keys (raw_message, ref_msg) from outbound
  messages to prevent memory bloat from propagated inbound payloads

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* Update service.py

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* Update CLAUDE.md

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- `backend/app/channels/base.py`
- `backend/app/channels/dingtalk.py`
  L1: """DingTalk channel implementation."""
  L33: """Normalize ``conversationType`` to ``"1"`` (P2P) or ``"2"`` (group).
  L36: """
  L82: # DingTalk sampleMarkdown does not render pipe-delimited tables.
  L88: # Detect table: header row followed by separator row
  L105: """Adapt markdown for DingTalk's limited sampleMarkdown renderer."""
  L122: """DingTalk IM channel using Stream Push (WebSocket, no public IP needed)."""
  L205: """Return (conversation_type, sender_staff_id, conversation_id).
  L208: """
  L222: # Card mode: stream update to existing AI card
  L226: # ``card_template_id`` enables ``runs.stream`` (non-final + final outbounds).
  L227: # If card creation failed, skip non-final chunks to avoid duplicate messages.
  L250: # Non-card mode: send sampleMarkdown with retry
  L352: # -- stream client (runs in dedicated thread) --------------------------
  L405: # P2P: topic_id=None (single thread per user, like Telegram private chat)
  L406: # Group: topic_id=msg_id (each new message starts a new topic, like Feishu)
  L409: # chat_id uses conversation_id for groups, sender_staff_id for P2P
  L455: # Running reply must finish before publish_inbound so AI card tracks are
  L456: # registered before the manager emits streaming outbounds.
  L489: # -- DingTalk API helpers ----------------------------------------------
  ... (truncated)
- `backend/app/channels/feishu.py`
- `backend/app/channels/manager.py`
  L56: """Return a shallow copy of *meta* with known-large keys removed."""
- `backend/app/channels/service.py`
- `backend/app/channels/wecom.py`

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

- `backend/app/gateway/app.py`
  L37: # Default logging; lifespan overrides from config.yaml log_level.

## 1ad1420e 2026-05-01 Xun
refactor(skills): Unified skill storage capability (#2613)

- `backend/app/gateway/routers/skills.py`

## 78633c69 2026-05-01 yangzheli
fix(agents): propagate agent_name into ToolRuntime.context for setup_agent (#2679)

* fix(agents): propagate agent_name into ToolRuntime.context for setup_agent (#2677)

When creating a custom agent via the web UI, SOUL.md was always written
to the global base_dir/SOUL.md instead of agents/<name>/SOUL.md.

Root cause: the bootstrap flow sends agent_name via body.context, but
two layers were broken:

1. services.py only forwarded body.context keys into config["configurable"];
   config["context"] was never populated.
2. worker.py constructed the parent Runtime with a hard-coded
   {thread_id, run_id} context, ignoring config["context"] entirely.

After the langgraph >= 1.1.9 bump (#98a5b34f), ToolRuntime.context no
longer falls back to configurable, so setup_agent's
runtime.context.get("agent_name") returned None and the tool's silent
agent_name=None -> base_dir fallback kicked in, overwriting the global
SOUL.md.

Fix:
- services.py: extract merge_run_context_overrides() and write the
  whitelisted context keys into both configurable (legacy readers) and
  context (langgraph 1.1+ ToolRuntime consumers).
- worker.py: extract _build_runtime_context() and merge config["context"]
  into the Runtime's context (without letting callers override
  thread_id/run_id).

The base_dir fallback in setup_agent_tool.py is left in place because
the IM /bootstrap channel command depends on it. That code path can
be tightened in a follow-up.

Adds regression tests covering both helpers.

* Apply suggestions from code review

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- `backend/app/gateway/services.py`
  L101: # Whitelist of run-context keys that the langgraph-compat layer forwards from
  L102: # ``body.context`` into the run config. ``config["context"]`` exists in
  L103: # LangGraph >=0.6, but these values must be written to both ``configurable``
  L104: # (for legacy ``_get_runtime_config`` consumers) and ``context`` because
  L105: # LangGraph >=1.1.9 no longer makes ``ToolRuntime.context`` fall back to
  L106: # ``configurable`` for consumers like ``setup_agent``.
  L123: """Merge whitelisted keys from ``body.context`` into both ``config['configurable']``
  L286: # Merge DeerFlow-specific context overrides into both ``configurable`` and ``context``.

## 8939ccae 2026-05-01 KiteEater
fix(uploads): enforce streaming upload limits in gateway (#2589)

* fix: enforce gateway upload limits

* fix: acquire sandbox before upload writes

* Fix upload limit config wiring

* Sanitize upload size error filenames

* test: call upload routes unwrapped

* fix: guard upload limits endpoint

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/app/gateway/routers/uploads.py`
  L48: """Application-level upload limits exposed to clients."""
  L273: """Return upload limits used by the gateway for this thread."""

## 17447fcc 2026-05-02 KiteEater
fix(runtime): make rollback restore checkpoint supersede newer checkpoints (#2582)

* Restore rollback checkpoints with fresh ids

* Tighten rollback checkpoint tests and imports

* Update test_run_worker_rollback.py

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/app/gateway/routers/threads.py`

## ca3332f8 2026-05-02 Xinmin Zeng
fix(gateway): return ISO 8601 timestamps from threads endpoints (#2599)

* fix(gateway): return ISO 8601 timestamps from threads endpoints (#2594)

ThreadResponse documents created_at / updated_at as ISO timestamps,
matching the LangGraph Platform schema (langgraph_sdk.schema.Thread
exposes them as datetime, JSON-encoded as ISO 8601). The gateway
threads router was instead emitting str(time.time()) — unix-second
floats — breaking frontend new Date() parsing and producing a mixed
ISO/unix wire format that also corrupted the search sort order.

Centralize timestamp generation in deerflow.utils.time:
- now_iso()       — datetime.now(UTC).isoformat()
- coerce_iso(x)   — heals legacy unix-timestamp strings on read so the
                    store converges to ISO without a one-shot migration

threads.py: replace 6 time.time() call sites with now_iso(); wrap all
read paths and Phase-2 checkpoint metadata with coerce_iso(); _store_upsert
opportunistically heals legacy created_at on update; drop unused time import.

thread_runs.py: reuse now_iso() instead of a private duplicate _now_iso(),
preventing future drift between the two timestamp call sites.

Tests: 9 unit tests for the helper; 5 integration tests pinning the ISO
contract for create/get/patch/search and the legacy-healing path on the
internal store upsert. Full suite: 2144 passed, 15 skipped, 0 failed.

Closes #2594

* fix(gateway): coerce checkpoint metadata timestamps to ISO on read

After the merge with main, three additional read paths in ``threads.py``
were still emitting raw ``str(metadata.get("created_at", ""))`` —
``get_thread_state``, ``update_thread_state``, and ``get_thread_history``.

Same root cause as #2594: when the checkpoint metadata's ``created_at``
is a unix-second float (legacy data, or a checkpoint written by an older
Gateway version), ``str(float)`` produces ``"1777252410.411327"`` and the
frontend's ``new Date(...)`` returns ``Invalid Date``. The fix on the
``/threads/{id}`` GET path was already in place; these three sibling
endpoints needed the same treatment.

All four call sites now flow through ``coerce_iso``, so:
- legacy float metadata heals to ISO on the way out,
- ISO metadata passes through unchanged,
- ``datetime`` instances (which the new ``coerce_iso`` branch handles
  explicitly) emit with the ``T`` separator instead of falling through
  to the space-separated ``str(datetime)`` form.

Coverage added for the two endpoints not already pinned by the merge:
- ``test_get_thread_state_returns_iso_for_legacy_checkpoint_metadata``
- ``test_get_thread_history_returns_iso_for_legacy_checkpoint_metadata``

Both pre-seed a checkpoint whose metadata carries the literal float
from the issue body and assert the wire format is ISO.

- `backend/app/gateway/routers/threads.py`
  L309: # ``coerce_iso`` heals legacy unix-second values that
  L310: # ``MemoryThreadMetaStore`` historically wrote with ``time.time()``;
  L311: # SQL-backed rows already arrive as ISO strings and pass through.

## e543bbf5 2026-05-02 Hinotobi
[security] fix(upload): reject symlinked upload destinations (#2623)

* fix: reject symlinked upload destinations

* test: harden upload destination checks

* fix: address PR feedback for #2623

* test: cover safe upload re-uploads

* fix: preserve upload limit checks after rebase

* fix(upload): stream safe HTTP upload writes

- `backend/app/channels/manager.py`
- `backend/app/gateway/routers/uploads.py`

## 8e48b7e8 2026-05-04 Willem Jiang
fix(channels): preserve clarification conversation history across follow-up turns (#2444)

* fix(channels): preserve clarification conversation history across follow-up turns

Pin channel-triggered runs to the root checkpoint namespace and ensure thread_id is always present in configurable run config so follow-up replies resume the same conversation state.

Add regression coverage to channel tests:

assert checkpoint_ns/thread_id are passed in wait and stream paths
add an integration-style clarification flow test that verifies the second user reply continues prior context instead of starting a new session
This addresses history loss after ask_clarification interruptions (issue #2425).

* Apply suggestions from code review

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

* fix(channels): copy configurable dict before injecting run-scoped fields

  When configurable was already a plain dict, _resolve_run_params mutated
  it in place, leaking checkpoint_ns and thread_id back into the shared
  session config. Always copy via dict() before mutating to prevent
  cross-user or cross-channel config pollution.

---------

Co-authored-by: Copilot <175728472+Copilot@users.noreply.github.com>

- `backend/app/channels/manager.py`
  L598: # Pin channel-triggered runs to the root graph namespace so follow-up
  L599: # turns continue from the same conversation checkpoint.

## e8675f26 2026-05-05 Nan Gao
fix(loop-detection): keep tool-call pairing on warn injection (#2724) (#2725)

* fix(loop-detection): keep tool-call pairing on warn injection (#2724)

* make format

* fix(loop-detection): avoid IMMessage leak to downstream consumer

* fix(channels): filter loop warning text from IM replies

- `backend/app/channels/manager.py`
  L150: """Remove middleware-authored loop warning lines from display text."""

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

- `backend/app/gateway/routers/agents.py`
  L151: # Treat the name as taken if either the per-user path or the legacy shared
  L152: # path holds an agent — picking a name that collides with an unmigrated
  L153: # legacy agent would shadow the legacy entry once migration runs.

## 1336872b 2026-05-06 Eilen Shin
fix(channels): authenticate gateway command requests (#2742)

- `backend/app/channels/manager.py`

## 2b0e62f6 2026-05-07 Hinotobi
[security] fix(auth): reject cross-site auth POSTs (#2740)

* fix(security): reject cross-site auth posts

* fix(auth): align secure cookie proxy scheme handling

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/app/gateway/csrf_middleware.py`
  L67: """Return normalized host[:port], omitting default ports."""
  L78: """Return a normalized scheme://host[:port] origin, or None for invalid input."""
  L89: # Browser Origin is only scheme/host/port. Reject URL-shaped or credentialed values.
  L97: """Return explicit configured browser origins that may call auth routes."""
  L110: """Return the first value from a comma-separated proxy header."""
  L118: """Extract a parameter from the first RFC 7239 Forwarded header entry."""
  L131: """Resolve the original request scheme from trusted proxy headers."""
  L137: """Build the origin for the URL the browser is targeting."""
  L149: """Allow auth POSTs only from the same origin or explicit configured origins.
  L156: """

## 7a3c58a7 2026-05-09 ChenglongZ
Fix duplicate gateway upload filenames (#2789)

- `backend/app/gateway/routers/uploads.py`
  L196: # Track filenames within this request so duplicate form parts do not
  L197: # silently truncate each other. Existing uploads keep the historical
  L198: # overwrite behavior for a single replacement upload.

## 41741608 2026-05-09 YuJitang
fix: use backend thread token usage for header total (#2800)

* fix: use backend thread token usage for header total

* Refactor thread token usage fetch

- `backend/app/gateway/routers/thread_runs.py`

## 1c96a6af 2026-05-09 Eilen Shin
fix: keep new agent bootstrap in user scope (#2784)

- `backend/app/gateway/services.py`
  L140: """Stamp the authenticated user into the run context for background tools.
  L145: """

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

- `backend/app/gateway/app.py`
  L313: # CORS: the unified nginx endpoint is same-origin by default. Split-origin
  L314: # browser clients must opt in with this explicit Gateway allowlist so CORS
  L315: # and CSRF origin checks share the same source of truth.
- `backend/app/gateway/config.py`
- `backend/app/gateway/csrf_middleware.py`
  L110: """Return normalized explicit browser origins from GATEWAY_CORS_ORIGINS."""

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

- `backend/app/gateway/services.py`
  L274: # Coerce non-string model_name values to str before truncation.
  L278: # Validate model against the allowlist when a model_name is provided.

## f734e14d 2026-05-12 greatmengqi
docs: document auth design and user isolation (#2913)

* docs: document auth design and user isolation

* docs: align auth docs with current storage and reset behavior

---------

Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>

- `backend/app/gateway/app.py`
  L180: # Check admin bootstrap state and migrate orphan threads after admin exists.
- `backend/app/gateway/auth/models.py`
- `backend/app/gateway/routers/auth.py`

## 506be8bf 2026-05-12 AochenShen99
docs: clarify LangGraph compatibility entrypoints (#2914)

- `backend/app/gateway/langgraph_auth.py`
  L1: """LangGraph compatibility auth handler — shares JWT logic with Gateway.

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

- `backend/app/gateway/routers/threads.py`
  L96: """Reject filter entries the SQL backend cannot compile.
  L100: """

## 7a2670ea 2026-05-15 Hinotobi
fix(gateway): cap skill artifact preview size (#2963)

- `backend/app/gateway/routers/artifacts.py`
  L51: """Read a .skill archive member while enforcing an uncompressed size cap."""

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

- `backend/app/channels/discord.py`
  L49: # Session tracking: channel_id -> Discord thread_id (in-memory, persisted to JSON).
  L50: # Uses a dedicated JSON file separate from ChannelStore, which maps IM
  L51: # conversations to DeerFlow thread IDs — a different concern.
  L53: # Reverse-lookup set for O(1) thread ID checks (avoids O(n) scan of _active_threads.values()).
  L55: # Lock protecting _active_threads and the JSON file from concurrent access.
  L56: # _run_client (Discord loop thread) and the main thread both read/write.
  L64: # Typing indicator management
  L113: """Restore Discord thread mappings from the dedicated JSON file on startup."""
  L131: """Persist a Discord thread mapping to the dedicated JSON file."""
  L139: # Update reverse-lookup set
  L152: # Cancel all active typing indicator tasks
  L178: # Stop typing indicator once we're sending the response
  L216: """Starts a loop to send periodic typing indicators."""
  L236: """Stops the typing loop for a specific target."""
  L244: """Add a checkmark reaction to acknowledge the message was received."""
  L272: # Determine whether the bot is mentioned in this message
  L284: # Strip mention from text for processing
  L287: # Don't return early if text is empty — still process the mention (e.g., create thread)
  L289: # --- Determine thread/channel routing and typing target ---
  L295: # --- Message already inside a thread ---
  ... (truncated)
- `backend/app/channels/manager.py`
- `backend/app/channels/service.py`

## 6d611c2b 2026-05-16 Willem Jiang
fix(auth): persist auto-generated JWT secret to survive restarts (#2933)

* fix(auth): persist auto-generated JWT secret to survive restarts

  When AUTH_JWT_SECRET is not set, the auto-generated secret is now
  written to .deer-flow/.jwt_secret (mode 0600) and reused on subsequent
  starts. This prevents session invalidation on every restart while still
  allowing explicit AUTH_JWT_SECRET in .env to take precedence.

* Apply suggestions from code review

Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>

* Apply suggestions from code review

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* fix the lint errors of backend

---------

Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/app/gateway/auth/config.py`
  L36: """Load persisted JWT secret from ``{base_dir}/.jwt_secret``, or generate and persist a new one."""

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

- `backend/app/gateway/routers/thread_runs.py`

## b5108e35 2026-05-18 Willem Jiang
fix(auth): replace setup-status 429 rate limit with cached response (#2915)

* fix(auth): replace setup-status 429 rate limit with cached response

  The /api/v1/auth/setup-status endpoint had a 60-second cooldown that
  returned HTTP 429 for all but the first request per IP. When the service
  restarted with multiple browser tabs open, all tabs hit this endpoint
  simultaneously from the same source IP, causing a storm of 429 errors
  that blocked the login flow.

  Replace the cooldown-with-429 model with a per-IP response cache that
  returns the previously computed result within the TTL. The database
  query (count_admin_users) still only runs once per IP per 60 seconds,
  preserving the original performance goal while eliminating spurious
  429 errors on multi-tab reconnection.

  Fixes #2902

* fix(auth): address setup-status cache review issues

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/439a0e8c-8b64-41d4-a3cd-fe9a00eec534

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* test(auth): improve readability of setup-status concurrency assertion

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/439a0e8c-8b64-41d4-a3cd-fe9a00eec534

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* Apply suggestions from code review

Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>

* fix the unit test error

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: Copilot Autofix powered by AI <223894421+github-code-quality[bot]@users.noreply.github.com>

- `backend/app/gateway/routers/auth.py`
  L386: # Per-IP cache: ip → (timestamp, result_dict).
  L387: # Returns the cached result within the TTL instead of 429, because
  L388: # the answer (whether an admin exists) rarely changes and returning
  L389: # 429 breaks multi-tab / post-restart reconnection storms.
  L403: # Return cached result when within TTL — avoids 429 on multi-tab reconnection.
  L411: # Recheck cache after waiting for the inflight guard.
  L421: # Evict stale entries when dict grows too large to bound memory usage.
  L446: # Cache only the stable "initialized" result to avoid stale setup redirects.

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

- `backend/app/gateway/routers/thread_runs.py`

## 7ec8d3a6 2026-05-21 sunsine
fix(security): mask sensitive values in MCP config API responses (#2667)

* fix(security): mask sensitive values in MCP config API responses

GET /api/mcp/config previously returned plaintext secrets including
env dict values (API keys), headers (auth tokens), and OAuth
client_secret/refresh_token. Any authenticated user could read all
MCP service credentials.

This commit masks sensitive fields in GET/PUT responses while
preserving the key structure so the frontend round-trip (GET masked
→ toggle enabled → PUT) correctly preserves existing secrets.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

* fix(security): address Copilot review on MCP config masking

- Load raw JSON (un-resolved $VAR placeholders) as merge source instead
  of resolved config, preventing plaintext secrets from replacing
  $VAR placeholders on disk (Comment 2)
- Preserve all top-level keys (e.g. mcpInterceptors) in PUT, not just
  mcpServers/skills (Comment 1)
- Reject masked value '***' for new keys that don't exist in existing
  config, returning 400 with actionable error (Comment 3)
- Allow empty string '' to explicitly clear OAuth secrets, while None
  means 'preserve existing' for safe round-trip (Comment 4)
- Add 3 new tests for rejection, clearing, and edge cases (18 total)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.6 <noreply@anthropic.com>

- `backend/app/gateway/routers/mcp.py`
  L70: """Return a copy of server config with sensitive fields masked.
  L74: """
  L98: """Merge incoming config with existing, preserving secrets masked by GET.
  L112: """
  L141: # None = preserve (masked round-trip), "" = explicitly clear, else = new value
  L239: # Load current config to preserve skills
  L242: # Load raw (un-resolved) JSON from disk to use as the merge source.
  L243: # This preserves $VAR placeholders in env values and top-level keys
  L244: # like mcpInterceptors that would otherwise be lost.
  L251: # Preserve any top-level keys beyond mcpServers/skills
  L256: # Merge incoming server configs with raw on-disk secrets
  L268: # Build config data preserving all top-level keys from the original file

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

- `backend/app/channels/manager.py`

## 923f516d 2026-05-21 Airene Fang
feat(trace):LangGraph -> lead_agent and set custom agent_name to run_name (#3101)

* feat(trace):LangGraph -> lead_agent and set user custom agent name to run_name

* feat(trace):follow github copilot suggest

* feat(trace):Refactor run_name resolution and improve test coverage

- `backend/app/gateway/services.py`

## 9c03a71a 2026-05-21 Xinmin Zeng
fix(gateway): preserve message additional_kwargs in normalize_input (#3132) (#3136)

* fix(gateway): preserve message additional_kwargs in normalize_input (#3132)

The gateway's hand-rolled dict→message coercion only forwarded `content`
and collapsed every role to `HumanMessage`, silently dropping the
frontend's `additional_kwargs.files` payload (along with `id`, `name`,
and ai/system/tool roles).

Effect on issue #3132:

- `UploadsMiddleware` saw no `files` on the last human message, so the
  just-uploaded file got bucketed under "previous messages" while the
  current turn was reported as `(empty)`.
- The persisted human message had no `files`, so the attachment chip on
  the message disappeared the moment the optimistic UI cleared.

Delegate the conversion to `langchain_core.messages.utils.convert_to_messages`
so `additional_kwargs`, `id`, `name`, and non-human roles round-trip
unchanged.

* fix(gateway): convert malformed-message ValueError into HTTP 400

normalize_input now sits at the request boundary, so a malformed
input.messages[N] dict (missing role/type/content, unsupported role,
etc.) should surface as 400 with the offending index — not bubble out
of FastAPI as 500.

Per Copilot review on #3136.

- `backend/app/gateway/services.py`
  L80: """Convert LangGraph Platform input format to LangChain state dict.
  L92: """

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

- `backend/app/gateway/app.py`
  L164: # Load config and check necessary environment variables at startup.
  L165: # `startup_config` is a local snapshot used only for one-shot bootstrap
  L166: # work (logging level, langgraph_runtime engines, channels). Request-time
  L167: # config resolution always routes through `get_app_config()` in
  L168: # `app/gateway/deps.py::get_config()` so `config.yaml` edits become
  L169: # visible without a process restart. We deliberately do NOT cache this
  L170: # snapshot on `app.state` to keep that contract enforceable.
- `backend/app/gateway/deps.py`
  L46: """Return the freshest ``AppConfig`` for the current request.
  L63: """
  L131: # Run event store. The store and the matching ``run_events_config`` are
  L132: # both frozen at startup so ``get_run_context`` does not combine a
  L133: # freshly-reloaded ``AppConfig.run_events`` with a store still bound to
  L134: # the previous backend.

## 2eeb5979 2026-05-22 Lawrance_YXLiao
fix(runs): expose active progress counters (#3148)

* fix(runs): expose active progress counters

* fix(runs): avoid delayed progress flush on completion

* fix(runs): tighten progress snapshot semantics

* fix(runs): preserve omitted progress fields

* chore(runs): remove duplicate journal initialization

- `backend/app/gateway/routers/thread_runs.py`

## 66d6a6a4 2026-05-23 AochenShen99
fix: harden run finalization persistence (#3155)

* fix: harden run finalization persistence

* style: format gateway recovery test

* fix: align run repository return types

* fix: harden completion recovery follow-up

- `backend/app/gateway/deps.py`
  L51: """Mark thread status as error only when its newest run was recovered."""
  L169: # Startup-only recovery: clean shutdowns return no active rows and
  L170: # the thread-status update below becomes a no-op.

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

- `backend/app/gateway/routers/uploads.py`
  L78: """Ensure uploaded files are readable by the sandbox process.
  L85: """
  L298: # Uploaded files are created with 0o600 permissions (owner read/write only).
  L299: # In Docker sandbox deployments the gateway writes as root but the sandbox
  L300: # process runs as a non-root user (typically UID 1000).  Without group/other
  L301: # read bits the sandbox cannot access the files — whether the uploads
  L302: # directory is bind-mounted into the container or synced via
  L303: # sandbox.update_file.  Always add group/other read bits so every sandbox
  L304: # configuration can read the uploaded content.

## b00749a8 2026-05-26 Stellar鱼
fix(auth): share internal gateway token across workers (#3184)

* fix(auth): share internal gateway token across workers

* fix: restore deploy script executable bit

* Update deploy.sh

to skip the auth_token setup for the down command

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/app/gateway/internal_auth.py`
  L1: """Authentication for trusted Gateway internal callers."""
  L26: """Return headers that authenticate trusted Gateway internal calls."""
  L31: """Return True when *token* matches this Gateway worker's internal token."""

## a5599c10 2026-05-28 AochenShen99
fix(gateway): honour on_disconnect on /wait endpoints (#3267)

* fix(gateway): honour on_disconnect on /wait endpoints (#3265)

The non-streaming /threads/{tid}/runs/wait and /runs/wait handlers used
to await record.task directly with no disconnect handling and silently
swallow CancelledError. When a long tool call (e.g. pip install inside
a custom skill) kept the connection idle long enough for an
intermediate HTTP layer to time out, the handler would still read the
in-progress checkpoint and return it as if the run had completed
normally -- masking a half-finished run as a successful response.

Add wait_for_run_completion in app.gateway.services that mirrors
sse_consumer's bridge-consumption pattern: subscribe to the stream
bridge until END_SENTINEL, poll request.is_disconnected on every
wake-up, and on real client disconnect cancel the background run when
record.on_disconnect is "cancel". Wire it into both wait endpoints.

The streaming path was unaffected because sse_consumer already has
this loop; this just brings /wait to parity.

* fix(gateway): skip checkpoint serialization on /wait disconnect

Copilot review on #3267 caught a follow-on of the same #3265 bug: when
the client disconnects, wait_for_run_completion breaks out of the bridge
loop and cancels the run, but the /wait endpoint then continues to read
the checkpointer and serializes whatever partial checkpoint exists as a
normal 200 response.

Have the helper return a bool — True only when END_SENTINEL was observed
— and skip the checkpoint serialization path on False. Also reorder the
inner check so END_SENTINEL is honoured even when is_disconnected() flips
true in the same iteration; the run truly finished so the real final
checkpoint is still valid.

- `backend/app/gateway/routers/runs.py`
- `backend/app/gateway/routers/thread_runs.py`
- `backend/app/gateway/services.py`
  L413: """Block until the run publishes ``END_SENTINEL``, honouring on_disconnect.
  L435: """
  L439: # END_SENTINEL means the run reached a terminal state; honour it
  L440: # even if the client just disconnected so the caller still serializes
  L441: # the real final checkpoint.
  L447: # Heartbeats and regular events: keep waiting for END_SENTINEL.

## 37451500 2026-05-28 Lucy Shen
fix(gateway): split stream_existing_run into per-method routes for unique OpenAPI operationIds (#3228)

* fix(gateway): split stream_existing_run into per-method routes for unique OpenAPI operationIds

`@router.api_route("/.../stream", methods=["GET", "POST"])` registers a
single FastAPI route that holds both methods. FastAPI's auto-generated
`operationId` is computed once per route from a single method picked out
of `route.methods`, so when OpenAPI generation iterates over every method
on that route both end up sharing the same `operationId`. That triggers
`UserWarning: Duplicate Operation ID stream_existing_run_..._stream_(get|post) for function stream_existing_run`
during `app.openapi()` and produces an invalid OpenAPI spec for SDK /
codegen consumers.

Register GET and POST as two separate routes on the same handler so each
method gets a distinct auto-generated `operationId` ("..._stream_get" and
"..._stream_post"). Behavior is otherwise unchanged: same handler, same
`require_permission` decoration, same response.

Add `tests/test_openapi_operation_ids.py` to lock in the invariant:
no duplicate-operationId warnings during spec generation, globally unique
operationIds across the spec, and distinct GET / POST operationIds on the
stream endpoint specifically. Reverted the source change locally and
confirmed all three tests fail before the fix.

* test(runtime): widen CancelledError catch in _ScriptedAgent to fix cancel-race flake

`_ScriptedAgent.astream()` previously only caught `asyncio.CancelledError`
inside the inner `if self.block_after_first_chunk:` while-loop. Cancellation
arriving during any earlier `await` in the same body
(`self.model.ainvoke`, `_write_checkpoint`, the `yield`) would propagate
without setting `controller.cancelled`, so callers waiting on
`controller.cancelled.wait(5)` after `POST /cancel` returned 204 could race
and time out.

`test_cancel_interrupt_stops_running_background_run` waits only for the
`started` event (set on the first line of `astream`) before issuing cancel,
so its race window spans all three pre-loop `await`s. On a clean `main`
checkout, stress-running the test 20× reproduces the failure 6/20
(~30%). `test_cancel_rollback_restores_pre_run_checkpoint`, which waits
for the later `checkpoint_written` event, passes 20/20 — confirming the
race lives entirely in the gap between `started.set()` and the
cancellation-aware block.

Widen the try/except to cover the entire `astream` body so any
`CancelledError` sets the controller event; the non-cancel path is
unchanged (no exception means no event set). After this change the
previously flaky test passes 50/50, the rollback test still passes 30/30,
and the full backend suite remains at 3649 passed / 19 skipped.

Test-only change — `backend/tests/test_runtime_lifecycle_e2e.py` is the
only file touched; the production cancel pipeline is unaffected.

- `backend/app/gateway/routers/thread_runs.py`
  L281: # Register GET and POST as separate routes so each method gets a unique OpenAPI
  L282: # operationId. ``api_route(methods=["GET", "POST"])`` shares one route registration
  L283: # across both methods, which makes FastAPI emit the same ``operationId`` twice and
  L284: # warn about a duplicate operation id during OpenAPI generation.

## 872079b8 2026-05-29 Eilen Shin
docs: clean standalone LangGraph server remnants (#3301)

- `backend/app/gateway/routers/mcp.py`
  L279: # Reload the Gateway configuration and update the global cache. The
  L280: # agent runtime lives in Gateway, so this keeps API reads and tool
  L281: # execution aligned after extensions_config.json changes.

## e8e9edcb 2026-05-29 Ryker_Feng
fix(channels): ignore hidden control messages when extracting replies (#3219) (#3270)

- `backend/app/channels/manager.py`
  L333: """Return whether a human message is an internal control message hidden from UI."""

## 46ddc346 2026-05-31 kia
fix(channels): preserve Feishu clarification thread continuity (#3285)

* fix(channels): preserve Feishu clarification thread continuity

* fix(channels): address Feishu clarification review feedback

---------

Co-authored-by: zzp1221 <zzp1221@users.noreply.github.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `backend/app/channels/feishu.py`
  L637: # Plain-message clarification continuity is a short-lived in-memory
  L638: # hint; explicit Feishu replies are still covered by persisted
  L639: # message-id mappings.
  L831: # Prefer any platform message id that already maps to a DeerFlow
  L832: # thread. This keeps replies to bot clarification cards in the
  L833: # original conversation even when Feishu reports the card as root.
- `backend/app/channels/manager.py`
  L236: """Return True only when the current turn's final result is clarification."""
- `backend/app/channels/message_bus.py`

## 019bd16a 2026-06-01 Eilen Shin
fix: load paginated run history messages (#3305)

- `backend/app/gateway/pagination.py`
  L1: """Shared pagination helpers for gateway routers."""
  L7: """Trim a ``limit + 1`` run-message page while preserving page boundaries."""
- `backend/app/gateway/routers/runs.py`
- `backend/app/gateway/routers/thread_runs.py`

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

- `backend/app/channels/manager.py`
  L674: # ``user_id`` drives user-scoped filesystem buckets that only accept
  L675: # ``[A-Za-z0-9_-]``, so normalize the channel id and keep the raw value
  L676: # under ``channel_user_id`` for platform-facing lookups.
- `backend/app/gateway/internal_auth.py`
- `backend/app/gateway/services.py`
  L151: """

## 1aac408d 2026-06-06 Nan Gao
fix upload file size contract (#3408)

- `backend/app/gateway/routers/uploads.py`
  L43: """Uploaded file metadata exposed by upload and list APIs."""
  L69: """Response model for uploaded file listing."""

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

- `backend/app/gateway/deps.py`
  L37: # Upper bound (seconds) for draining in-flight runs during shutdown, before the
  L38: # AsyncExitStack tears down the checkpointer (and its connection pool). Kept
  L39: # local to avoid an app -> deps -> app import cycle. This is a *separate* budget
  L40: # from ``app.gateway.app._SHUTDOWN_HOOK_TIMEOUT_SECONDS`` (currently also 5.0s,
  L41: # which bounds channel-service stop): the two govern independent teardown steps
  L42: # and may diverge, but both count toward the lifespan shutdown window — revisit
  L43: # them together if their sum must stay within the server's graceful-shutdown
  L44: # timeout.
  L49: """Drain in-flight runs before the checkpointer is torn down (issue #3373).
  L58: """
  L63: # Re-shield so this second wait does not abandon the in-flight drain;
  L64: # it is bounded, so this cannot hang. Then re-raise to honour shutdown.
  L218: # Drain in-flight run tasks BEFORE the AsyncExitStack tears down the
  L219: # checkpointer (and its connection pool). A run still mid-graph would
  L220: # otherwise leak into asyncio.run() shutdown, where langgraph's
  L221: # _checkpointer_put_after_previous aput races the closed pool and
  L222: # raises PoolClosed (issue #3373).

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

- `backend/app/gateway/deps.py`

## 40a371b8 2026-06-08 greatmengqi
fix(security): harden MCP config endpoint (#3425)

* fix(security): harden MCP config endpoint

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/app/gateway/routers/mcp.py`
  L76: """Require the authenticated caller to be an admin user.
  L82: """
  L97: """Return executable names allowed for API-managed stdio MCP servers."""
  L107: """Normalize and validate a stdio command field from the API boundary."""
  L126: """Validate API-submitted MCP config before it is persisted.
  L131: """

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

- `backend/app/gateway/app.py`
  L182: # Pre-warm tiktoken encoding cache so the first memory-injection request
  L183: # never blocks on the BPE data download (which hits an OpenAI/Azure URL
  L184: # that may be unreachable in restricted networks — see issue #3402).

## 3b105d1e 2026-06-08 DanielWalnut
fix(suggestions): strip inline <think> reasoning before parsing follow-up questions (#3435)

Reasoning models such as MiniMax-M3 inline their chain-of-thought into the
message content as <think>...</think> (reasoning_split defaults to false)
instead of a separate reasoning_content field. The follow-up-suggestions
endpoint extracted the JSON array via find('[') / rfind(']'), which silently
broke whenever the reasoning text contained '[' or ']' — or when long thinking
hit max_tokens and truncated before the array was emitted — returning empty
suggestions.

- Add _strip_think_blocks() and apply it before JSON extraction; it removes
  complete <think>...</think> blocks (case-insensitive) and drops an unclosed
  <think> left by max_tokens truncation.
- Document the MiniMax thinking toggle in config.example.yaml
  (when_thinking_enabled: adaptive / when_thinking_disabled: disabled) so
  thinking_enabled=False actually disables reasoning on M3; note that M2.x
  models always think and rely on the defensive strip above.
- Tests cover complete/unclosed think blocks, brackets-inside-think, think +
  code-fence, and an end-to-end suggestions case reproducing the empty-result
  bug.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

- `backend/app/gateway/routers/suggestions.py`
  L34: # Matches a complete <think>...</think> block (case-insensitive, spans newlines).
  L36: # Matches a dangling, unclosed <think> (model truncated at max_tokens mid-thought).
  L41: """Remove reasoning-model ``<think>...</think>`` blocks from the response.
  L50: """
  L52: # Drop any unclosed <think> (and everything after it) left by truncation.

## 3c2b60aa 2026-06-08 Xun
fix(threads): assign new checkpoint ID in update_thread_state (#2391)

* async

* add test

* test(threads): assert aput preserves endpoint-assigned checkpoint id

Confirm the update_thread_state fix is real, not a no-op: all supported
savers (InMemorySaver, AsyncSqliteSaver, AsyncPostgresSaver) persist and
echo checkpoint["id"] verbatim rather than minting their own. Add
assertions that each POST /state response's checkpoint_id round-tripped
into persisted history and kept its uuid6 time-ordering through aput,
and document the verified contract in the router.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

- `backend/app/gateway/routers/threads.py`
  L539: # Assign a new checkpoint ID so aput performs an INSERT rather than an
  L540: # in-place REPLACE of the existing row.  Use uuid6 (time-ordered) rather
  L541: # than uuid4 (random) so the new ID is always lexicographically greater
  L542: # than the previous one — LangGraph's checkpointers determine the "latest"
  L543: # checkpoint by max(checkpoint_ids) string order, matching the uuid6 epoch.
  L547: # read (which always includes checkpoint_ns=""). The fresh checkpoint ID is
  L548: # assigned above via checkpoint["id"]; keep checkpoint_id out of the config so
  L549: # the write is keyed by the new checkpoint payload rather than the prior read.
  L550: # All supported savers (InMemorySaver, AsyncSqliteSaver, AsyncPostgresSaver)
  L551: # persist and echo back checkpoint["id"] verbatim — none mint their own — so
  L552: # the new_config below carries the uuid6 we assigned here. (Regression-locked
  L553: # by test_update_thread_state_inserts_new_checkpoint_each_call.)

## b62c5a7b 2026-06-09 ly-wang19
fix(agents): offload blocking filesystem IO in the custom-agent router off the event loop (#3457)

* fix(agents): offload blocking filesystem IO in delete_agent off the event loop

delete_agent is an async route handler but resolved the agent directory (Paths.base_dir -> Path.resolve), probed it (Path.exists), and removed it (shutil.rmtree) directly on the event loop, blocking it for the duration of every delete. Surfaced by 'make detect-blocking-io'.

Move the resolve/exists/rmtree sequence into a sync helper run via asyncio.to_thread, mapping its outcome back to the existing 404/409/500 responses (behavior unchanged). Adds a tests/blocking_io/ regression anchor under the strict Blockbuster gate, mirroring test_skills_load.py (#1917).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* fix(agents): offload blocking filesystem IO in create_agent_endpoint too

Like delete_agent, the async create_agent_endpoint resolved and created the agent directory and wrote config.yaml + SOUL.md (with rmtree cleanup on failure) directly on the event loop. Move the whole create-or-409 sequence into a sync helper run via asyncio.to_thread; behavior is unchanged (201 / 409 / 500). Extends the blocking_io regression anchor to cover create as well as delete and renames it to test_agents_router.py.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

* Apply suggestions from code review

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: ly-wang19 <ly-wang19@users.noreply.github.com>
Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `backend/app/gateway/routers/agents.py`
  L218: # Worker thread: base-dir resolution, existence checks, directory/file
  L219: # creation, read-back, and failure cleanup are all blocking filesystem
  L220: # IO that must stay off the event loop.
  L232: # Write config.yaml
  L247: # Write SOUL.md
  L256: # Clean up partial state on failure before surfacing the error.
  L447: # Runs in a worker thread: resolving the base dir, probing the directory
  L448: # (`exists`), and removing it (`rmtree`) are all blocking filesystem IO
  L449: # that must stay off the event loop.

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

- `backend/app/channels/commands.py`
  L24: """Return whether text starts with a registered channel control command."""
- `backend/app/channels/dingtalk.py`
- `backend/app/channels/discord.py`
- `backend/app/channels/feishu.py`
- `backend/app/channels/manager.py`
  L134: """Raised when IM slash-skill command resolution cannot complete safely."""
- `backend/app/channels/slack.py`
- `backend/app/channels/telegram.py`
  L70: # Slash skill commands are dynamic and cannot all be pre-registered
  L71: # with Telegram, so route unknown slash commands through chat handling.
- `backend/app/channels/wechat.py`
- `backend/app/channels/wecom.py`

## 2b795265 2026-06-10 DanielWalnut
fix: align auth-disabled mode and mock history loading (#3471)

* fix: align auth-disabled mode and mock history loading

* fix: address auth-disabled review feedback

* test: cover auth-disabled backend contract

* style: format frontend tests

* fix: address follow-up review comments

- `backend/app/gateway/app.py`
- `backend/app/gateway/auth_disabled.py`
  L1: """Shared helpers for local/E2E auth-disabled mode."""
- `backend/app/gateway/auth_middleware.py`
  L98: # Strict JWT validation: reject junk/expired tokens with 401
  L99: # right here instead of silently passing through. This closes
  L100: # the "junk cookie bypass" gap (AUTH_TEST_PLAN test 7.5.8):
  L101: # without this, non-isolation routes like /api/models would
  L102: # accept any cookie-shaped string as authentication.
  L103: #
  L104: # We call the *strict* resolver so that fine-grained error
  L105: # codes (token_expired, token_invalid, user_not_found, …)
  L106: # propagate from AuthErrorCode, not get flattened into one
  L107: # generic code. BaseHTTPMiddleware doesn't let HTTPException
  L108: # bubble up, so we catch and render it as JSONResponse here.
- `backend/app/gateway/csrf_middleware.py`
- `backend/app/gateway/deps.py`
- `backend/app/gateway/langgraph_auth.py`
- `backend/app/gateway/routers/auth.py`

## ba9cc5e9 2026-06-10 Xinmin Zeng
fix(gateway): enforce thread ownership on stateless run endpoints (#3473)

POST /api/runs/stream and /api/runs/wait accept thread_id in the request
body but performed no owner authorization, letting any authenticated user
start runs on -- and read /wait checkpoint channel_values from -- another
user's thread (cross-user IDOR, #3472).

The @require_permission(owner_check=True) decorator resolves ownership from
the thread_id *path* param, so it cannot cover these body-param endpoints.
Enforce ownership inside start_run() before create_or_reject via
ThreadMetaStore.check_access: missing rows (auto-created temp threads) and
NULL-owner rows stay accessible, while a thread owned by another user
returns 404 (matching thread_runs.py). The internal system role (IM
channels acting for platform users) is exempt.

Closes #3472

- `backend/app/gateway/services.py`
  L318: # Stateless run endpoints carry thread_id in the request *body*, so the
  L319: # @require_permission(owner_check=True) decorator -- which resolves ownership
  L320: # from the path param -- cannot protect them. Enforce thread ownership here,
  L321: # before any run is created, so one user cannot start runs on (or read /wait
  L322: # checkpoint state from) another user's thread. Missing rows (auto-created
  L323: # temp threads) and NULL-owner rows (shared / pre-auth data) stay accessible
  L324: # via check_access; only a thread already owned by another user is rejected
  L325: # with 404, matching thread_runs.py's anti-enumeration behaviour. Internal
  L326: # channel runs act on behalf of IM users they do not own (see
  L327: # inject_authenticated_user_context), so the internal system role is exempt.

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

- `backend/app/gateway/app.py`
  L187: # When memory.token_counting is "char", token counting never touches
  L188: # tiktoken, so skip the warm-up entirely (avoids even the 5s probe in
  L189: # network-restricted deployments — see issue #3429).
- `backend/app/gateway/routers/memory.py`

