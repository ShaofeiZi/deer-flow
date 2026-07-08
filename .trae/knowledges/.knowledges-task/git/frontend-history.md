## 7c87dc5b 2026-04-19 Xun
fix(reasoning): prevent LLM-hallucinated HTML tags from rendering as DOM elements (#2321)

* fix

* add test

* fix

- `frontend/src/components/ai-elements/reasoning.tsx`
- `frontend/src/core/streamdown/plugins.ts`
  L31: // Plugins for reasoning/thinking content — derived from streamdownPlugins but without rehypeRaw,
  L32: // to prevent LLM-hallucinated HTML tags (e.g. <simd>) from being rendered as DOM elements.

## f2013f47 2026-04-20 Eilen Shin
fix command palette hydration mismatch (#2301)

* fix command palette hydration mismatch

* style: format command dialog description

- `frontend/src/components/ui/command.tsx`

## ef041741 2026-04-21 Copilot
Fix invalid HTML nesting in reasoning trigger during complex task rendering (#2382)

* Initial plan

* fix(frontend): avoid invalid paragraph nesting in reasoning trigger

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/4c9eb0c2-ff29-4629-a61c-4e33d736d918

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

* test(frontend): strengthen reasoning trigger DOM nesting assertion

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/4c9eb0c2-ff29-4629-a61c-4e33d736d918

Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

---------

Co-authored-by: copilot-swe-agent[bot] <198982749+Copilot@users.noreply.github.com>
Co-authored-by: WillemJiang <219644+WillemJiang@users.noreply.github.com>

- `frontend/src/components/ai-elements/reasoning.tsx`

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

- `frontend/src/components/workspace/agents/agent-card.tsx`
- `frontend/src/core/agents/types.ts`

## c2332bb7 2026-04-24 Admire
fix memory settings layout overflow (#2420)

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `frontend/src/components/workspace/settings/memory-settings-page.tsx`
- `frontend/src/components/workspace/settings/settings-dialog.tsx`

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

- `frontend/src/app/(auth)/layout.tsx`
  L22: // Allow access to setup page
- `frontend/src/app/(auth)/login/page.tsx`
  L12: /**
  L13: * Validate next parameter
  L14: * Prevent open redirect attacks
  L15: * Per RFC-001: Only allow relative paths starting with /
  L16: */
  L22: // Need start with / (relative path)
  L27: // Disallow protocol-relative URLs
  L36: // Disallow URLs with different protocols (e.g., javascript:, data:, etc)
  L41: // Valid relative path
  L56: // Get next parameter for validated redirect
  L60: // Redirect if already authenticated (client-side, post-login)
  L98: // Both login and register set a cookie — redirect to workspace
- `frontend/src/app/(auth)/setup/page.tsx`
- `frontend/src/app/workspace/layout.tsx`
- `frontend/src/app/workspace/workspace-content.tsx`
- `frontend/src/components/workspace/input-box.tsx`
- `frontend/src/components/workspace/settings/account-settings-page.tsx`
- `frontend/src/components/workspace/settings/settings-dialog.tsx`
- `frontend/src/core/agents/api.ts`
- `frontend/src/core/api/api-client.ts`
  L10: /**
  L11: * SDK ``onRequest`` hook that mints the ``X-CSRF-Token`` header from the
  L12: * live ``csrf_token`` cookie just before each outbound fetch.
  L13: *
  L14: * Reading the cookie per-request (rather than baking it into the SDK's
  L15: * ``defaultHeaders`` at construction) handles login / logout / password
  L16: * change cookie rotation transparently. Both the ``/langgraph-compat/*``
  L17: * SDK path and the direct REST endpoints in ``fetcher.ts:fetchWithAuth``
  L18: * share :func:`readCsrfCookie` and :const:`STATE_CHANGING_METHODS` so
  L19: * the contract stays in lockstep.
  L20: */
- `frontend/src/core/api/fetcher.ts`
  L3: /** HTTP methods that the gateway's CSRFMiddleware checks. */
  L10: /** Mirror of the gateway's ``should_check_csrf`` decision. */
  L19: /**
  L20: * Read the ``csrf_token`` cookie set by the gateway at login.
  L21: *
  L22: * SSR-safe: returns ``null`` when ``document`` is undefined so the same
  L23: * helper can be imported from server components without a guard.
  L24: *
  L25: * Uses `String.split` instead of a regex to side-step ESLint's
  L26: * `prefer-regexp-exec` rule and the cookie value's reliable `; `
  L27: * separator (set by the gateway, not the browser, so format is stable).
  L28: */
  L39: /**
  L40: * Fetch with credentials and automatic CSRF protection.
  L41: *
  L42: * Two centralized contracts every API call needs:
  L43: *
  L44: * 1. ``credentials: "include"`` so the HttpOnly access_token cookie
  L45: *    accompanies cross-origin SSR-routed requests.
  L46: * 2. ``X-CSRF-Token`` header on state-changing methods (POST/PUT/
  ... (truncated)
- `frontend/src/core/auth/AuthProvider.tsx`
  L15: // Re-export for consumers
  L18: /**
  L19: * Authentication context provided to consuming components
  L20: */
  L36: /**
  L37: * AuthProvider - Unified authentication context for the application
  L38: *
  L39: * Per RFC-001:
  L40: * - Only holds display information (user), never JWT or tokens
  L41: * - initialUser comes from server-side guard, avoiding client flicker
  L42: * - Provides logout and refresh capabilities
  L43: */
  L52: /**
  L53: * Fetch current user from FastAPI
  L54: * Used when initialUser might be stale (e.g., after tab was inactive)
  L55: */
  L67: // Session expired or invalid
  L69: // Redirect to login if on a protected route
  L82: /**
  L83: * Logout - call FastAPI logout endpoint and clear local state
  ... (truncated)
- `frontend/src/core/auth/gateway-config.ts`
- `frontend/src/core/auth/proxy-policy.ts`
  L2: /** Allowed upstream path prefixes */
  L4: /** Request headers to strip before forwarding */
  L6: /** Response headers to strip before returning */
  L8: /** Credential mode: which cookie to forward */
  L10: /** Timeout in ms */
  L12: /** CSRF: required for non-GET/HEAD */
- `frontend/src/core/auth/server.ts`
  L8: /**
  L9: * Fetch the authenticated user from the gateway using the request's cookies.
  L10: * Returns a tagged AuthResult — callers use exhaustive switch, no try/catch.
  L11: */
- `frontend/src/core/auth/types.ts`
  L3: // ── User schema (single source of truth) ──────────────────────────
  L14: // ── SSR auth result (tagged union) ────────────────────────────────
  L31: // ── Backend error response parsing ────────────────────────────────
  L56: // Try top-level {code, message} first
  L60: // Unwrap FastAPI's {detail: {code, message}} envelope
  L65: // Legacy string-detail responses
- `frontend/src/core/i18n/locales/en-US.ts`
- `frontend/src/core/i18n/locales/types.ts`
- `frontend/src/core/i18n/locales/zh-CN.ts`
- `frontend/src/core/mcp/api.ts`
- `frontend/src/core/memory/api.ts`
- `frontend/src/core/skills/api.ts`
- `frontend/src/core/threads/hooks.ts`
- `frontend/src/core/uploads/api.ts`
- `frontend/src/env.js`

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

- `frontend/src/app/(auth)/layout.tsx`
- `frontend/src/app/(auth)/login/page.tsx`
  L70: // Redirect to setup if the system has no users yet
  L82: // Ignore errors; user stays on login page
- `frontend/src/app/(auth)/setup/page.tsx`
  L22: // --- Shared state ---
  L29: // --- Init-admin mode only ---
  L32: // --- Change-password mode only ---
  L41: // Check if the system has no users yet
  L49: // System already set up and user is not logged in — go to login
  L57: // Authenticated but needs_setup is false — already set up
  L66: // ── Init-admin handler ─────────────────────────────────────────────
  L104: // ── Change-password handler ────────────────────────────────────────
  L159: // ── Admin initialization form ──────────────────────────────────────
  L248: // ── Change-password form (needs_setup after login) ─────────────────
- `frontend/src/app/workspace/layout.tsx`
- `frontend/src/components/workspace/settings/account-settings-page.tsx`
- `frontend/src/core/auth/server.ts`
  L24: // No session — check whether the system has been initialised yet.
  L47: // If setup-status is unreachable/times out, fall through to unauthenticated.
- `frontend/src/core/auth/types.ts`
  L78: // Handle list of error details (e.g. from Pydantic validation)

## 716cae20 2026-04-11 copilot-swe-agent[bot]
docs: fix review feedback - source-map paths, memory API routes, supports_thinking, checkpointer callout

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/fb75dc8c-18a4-4a23-9229-25b3c5e545cf

Co-authored-by: foreleven <4785594+foreleven@users.noreply.github.com>

- `frontend/src/content/en/application/agents-and-threads.mdx`
  L3: DeerFlow App supports multiple named agents and maintains conversation state across sessions through threads and checkpointing.
  L4: 
  L5: ## Agents
  L6: 
  L7: ### The default agent
  L8: 
  L9: The default agent is the Lead Agent with no custom configuration. It loads all globally enabled skills, has access to all configured tools, and uses the first model in `config.yaml` as its default.
  L10: 
  L11: ### Custom agents
  L12: 
  L13: Custom agents are named variants of the Lead Agent. Each one can have:
  L14: 
  L15: - a **display name** and an auto-derived ASCII slug (the `name` used internally)
  L16: - a specific **model** to use by default
  L17: - a restricted set of **skills** (or all globally enabled skills if unspecified)
  L18: - a restricted set of **tool groups**
  L19: - a custom **system prompt** or agent-specific instructions
  L20: 
  L21: Custom agents are created and managed through:
  L22: 
  ... (truncated)
- `frontend/src/content/en/reference/api-gateway-reference.mdx`
  L3: <Callout type="info">
  L4: DeerFlow Gateway is built on FastAPI and provides interactive API
  L5: documentation at <code>http://localhost:8001/docs</code>.
  L6: </Callout>
  L7: 
  L8: ## Base URL
  L9: 
  L10: ```
  L11: http://localhost:8001
  L12: ```
  L13: 
  L14: Via nginx proxy:
  L15: 
  L16: ```
  L17: http://localhost:2026/api
  L18: ```
  L19: 
  L20: ## Core endpoints
  L21: 
  L22: ### System
  ... (truncated)
- `frontend/src/content/en/reference/configuration-reference.mdx`
  L3: This page is the complete reference for all top-level fields in `config.yaml`.
  L4: 
  L5: <Callout type="info">
  L6: See <code>config.example.yaml</code> in the repository root for a fully
  L7: commented example with all available options.
  L8: </Callout>
  L9: 
  L10: ## Top-level fields
  L11: 
  L12: | Field                  | Type          | Description                                     |
  L13: | ---------------------- | ------------- | ----------------------------------------------- |
  L14: | `config_version`       | `int`         | Config schema version (current: 6)              |
  L15: | `log_level`            | `str`         | Log verbosity: `debug`/`info`/`warning`/`error` |
  L16: | `models`               | `list`        | Available LLM model configurations              |
  L17: | `image_generate_model` | `str \| list` | Model name to use for image generation          |
  L18: | `token_usage`          | `object`      | Token usage tracking config                     |
  L19: | `tools`                | `list`        | Available tool configurations                   |
  L20: | `tool_groups`          | `list`        | Named groupings of tools                        |
  L21: | `tool_search`          | `object`      | Deferred tool loading config                    |
  L22: | `sandbox`              | `object`      | Sandbox provider and options                    |
  ... (truncated)
- `frontend/src/content/en/reference/runtime-flags-and-modes.mdx`
  L3: This page documents the runtime flags and modes that affect DeerFlow Harness and agent runtime behavior.
  L4: 
  L5: ## Per-request configurable options
  L6: 
  L7: These options are passed via `config.configurable` (for programmatic use) or selected in the web UI (for application use):
  L8: 
  L9: | Flag                       | Type          | Default                | Description                                      |
  L10: | -------------------------- | ------------- | ---------------------- | ------------------------------------------------ |
  L11: | `model_name`               | `str \| None` | First configured model | Model to use for the request                     |
  L12: | `agent_name`               | `str \| None` | `None`                 | Load a custom agent configuration                |
  L13: | `thinking_enabled`         | `bool`        | `True`                 | Enable extended thinking (model must support it) |
  L14: | `reasoning_effort`         | `str \| None` | `None`                 | Reasoning effort level (model-specific)          |
  L15: | `is_plan_mode`             | `bool`        | `False`                | Enable TodoList middleware                       |
  L16: | `subagent_enabled`         | `bool`        | `False`                | Allow subagent delegation                        |
  L17: | `max_concurrent_subagents` | `int`         | `3`                    | Maximum parallel subagent calls per turn         |
  L18: 
  L19: ## Environment variables
  L20: 
  L21: | Variable                | Default         | Description                                      |
  L22: | ----------------------- | --------------- | ------------------------------------------------ |
  ... (truncated)
- `frontend/src/content/en/reference/source-map.mdx`
  L3: This page maps DeerFlow's core concepts to where they are implemented in the codebase, helping you quickly locate specific features.
  L4: 
  L5: ## Backend core paths
  L6: 
  L7: ```
  L8: backend/
  L9: ├── app/
  L10: │   └── gateway/              # FastAPI Gateway API
  L11: │       ├── routers/
  L12: │       │   ├── agents.py     # Custom agent CRUD
  L13: │       │   ├── extensions.py # MCP/skill enable/disable
  L14: │       │   ├── memory.py     # Memory read/clear
  L15: │       │   ├── threads.py    # Thread management
  L16: │       │   └── uploads.py    # File uploads
  L17: │       └── app.py            # FastAPI app entry point (create_app())
  L18: │
  L19: └── packages/harness/deerflow/
  L20: ├── agents/
  L21: │   ├── lead_agent/
  L22: │   │   ├── agent.py      # make_lead_agent() factory
  ... (truncated)

## 814a488b 2026-04-11 copilot-swe-agent[bot]
docs: complete all English and Chinese documentation pages

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/a5f192e7-8034-4e46-af22-60b90ee27d40

Co-authored-by: foreleven <4785594+foreleven@users.noreply.github.com>

- `frontend/src/content/en/harness/customization.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L5: <Callout type="info" emoji="🔧">
  L6: DeerFlow is designed to be adapted. You can extend agent behavior by writing
  L7: custom middlewares, adding new tools, building skill packs, and replacing any
  L8: built-in component through the config.yaml <code>use:</code> field.
  L9: </Callout>
  L10: 
  L11: DeerFlow's pluggable architecture means most parts of the system can be replaced or extended without forking the core. This page maps the extension points and explains how to use each one.
  L12: 
  L13: ## Custom middlewares
  L14: 
  L15: Middlewares are the primary extension point for adding behavior to the Lead Agent. They wrap every LLM turn and can read and modify the agent's state before or after the model call.
  L16: 
  L17: To add a custom middleware:
  L18: 
  L19: 1. Implement the `AgentMiddleware` interface from `langchain.agents.middleware`.
  L20: 2. Pass your middleware to the `custom_middlewares` parameter when building the agent.
  L21: 
  L22: ```python
  ... (truncated)
- `frontend/src/content/en/harness/integration-guide.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L5: <Callout type="info" emoji="🔌">
  L6: DeerFlow Harness can be embedded into any Python application. This guide
  L7: covers the integration patterns for using DeerFlow as a library inside your
  L8: own system.
  L9: </Callout>
  L10: 
  L11: DeerFlow Harness is not only a standalone application. It is a Python library you can import and use inside your own backend, API server, automation system, or multi-agent orchestrator.
  L12: 
  L13: ## Embedding DeerFlowClient
  L14: 
  L15: The primary integration point is `DeerFlowClient`. It wraps the LangGraph runtime and exposes a clean API for sending messages and streaming responses from any Python application.
  L16: 
  L17: ```python
  L18: from deerflow.client import DeerFlowClient
  L19: from deerflow.config import load_config
  L20: 
  L21: # Load configuration (reads config.yaml or DEER_FLOW_CONFIG_PATH)
  L22: load_config()
  ... (truncated)
- `frontend/src/content/en/harness/quick-start.mdx`
  L1: import { Callout, Cards, Steps } from "nextra/components";
  L2: 
  L5: <Callout type="info" emoji="🚀">
  L6: This guide shows you how to use the DeerFlow Harness programmatically — not
  L7: through the App UI, but by importing and calling the harness directly in
  L8: Python.
  L9: </Callout>
  L10: 
  L11: The DeerFlow Harness is the Python SDK and runtime foundation. This quick start walks you through the key APIs for running an agent, streaming its output, and working with threads.
  L12: 
  L13: ## Prerequisites
  L14: 
  L15: DeerFlow Harness requires Python 3.12 or later. The package is part of the `deerflow` repository under `backend/packages/harness`.
  L16: 
  L17: If you are working from the repository clone:
  L18: 
  L19: ```bash
  L20: cd backend
  L21: uv sync
  L22: ```
  ... (truncated)
- `frontend/src/content/en/reference/api-gateway-reference.mdx`
  L1: import { Callout } from "nextra/components";
  L2: 
  L44: | Method   | Path                       | Description               |
  L45: | -------- | -------------------------- | ------------------------- |
  L46: | `GET`    | `/api/threads`             | List threads              |
  L47: | `DELETE` | `/api/threads/{thread_id}` | Delete a thread           |
  L48: | `GET`    | `/api/memory`              | Get global memory         |
  L49: | `GET`    | `/api/memory/{agent_name}` | Get agent-specific memory |
  L50: | `DELETE` | `/api/memory`              | Clear global memory       |
- `frontend/src/content/en/reference/concepts-glossary.mdx`
  L1: import { Callout } from "nextra/components";
  L2: 
  L5: This glossary defines the core terms used throughout the DeerFlow documentation.
  L6: 
  L7: ---
  L8: 
  L9: ## Agent
  L10: 
  L11: In DeerFlow, an agent is the primary processing unit that receives user messages, decides what actions to take (tool calls or direct responses), and generates output. DeerFlow uses a two-tier architecture with a **Lead Agent** and **Subagents**.
  L12: 
  L13: ## Artifact
  L14: 
  L15: A file produced by the agent — a report, chart, code file, or other deliverable. Artifacts are exposed via the `present_files` tool and persisted in the thread's user-data directory.
  L16: 
  L17: ## Checkpoint
  L18: 
  L19: A persisted snapshot of thread state, saved after each agent turn. Checkpoints allow conversations to resume after server restarts and support state management for long-horizon tasks.
  L20: 
  L21: ## Context Engineering
  L22: 
  ... (truncated)
- `frontend/src/content/en/reference/configuration-reference.mdx`
  L1: import { Callout } from "nextra/components";
  L2: 
  L48: supports_vision: true # Whether to enable vision capabilities
  L49: thinking_enabled: false # Whether to enable extended thinking
- `frontend/src/content/en/reference/runtime-flags-and-modes.mdx`
  L33: | Flag               | Type   | Description                           |
  L34: | ------------------ | ------ | ------------------------------------- |
  L35: | `supports_vision`  | `bool` | Model accepts image inputs            |
  L36: | `thinking_enabled` | `bool` | Model supports extended thinking mode |
- `frontend/src/content/en/reference/source-map.mdx`
  L17: │       └── main.py           # FastAPI app entry point
  L88: | Gateway main router        | `app/gateway/main.py`         |
- `frontend/src/content/en/tutorials/create-your-first-harness.mdx`
  L1: import { Callout, Steps } from "nextra/components";
  L2: 
  L5: This tutorial shows you how to use the DeerFlow Harness programmatically — importing and using DeerFlow directly in your Python code rather than through the web interface.
  L6: 
  L7: ## Prerequisites
  L8: 
  L9: - Python 3.12+
  L10: - `uv` installed
  L11: - DeerFlow repository cloned
  L12: 
  L13: ## Install
  L14: 
  L15: ```bash
  L16: cd deer-flow/backend
  L17: uv sync
  L18: ```
  L19: 
  L20: ## Create configuration
  L21: 
  L22: Create a minimal `config.yaml`:
  ... (truncated)
- `frontend/src/content/en/tutorials/deploy-your-own-deerflow.mdx`
  L1: import { Callout, Steps } from "nextra/components";
  L2: 
  L5: This tutorial guides you through deploying DeerFlow to a production environment using Docker Compose for multi-user access.
  L6: 
  L7: ## Prerequisites
  L8: 
  L9: - Docker and Docker Compose installed
  L10: - A server or VM (Linux recommended)
  L11: - LLM API key
  L12: 
  L13: ## Steps
  L14: 
  L15: <Steps>
  L16: 
  L17: ### Clone the repository
  L18: 
  L19: ```bash
  L20: git clone https://github.com/bytedance/deer-flow.git
  L21: cd deer-flow
  L22: ```
  ... (truncated)
- `frontend/src/content/en/tutorials/first-conversation.mdx`
  L1: import { Callout, Steps } from "nextra/components";
  L2: 
  L5: This tutorial walks you through your first complete agent conversation in DeerFlow — from launching the app to getting meaningful work done with the agent.
  L6: 
  L7: ## Prerequisites
  L8: 
  L9: - DeerFlow app is running (see [Quick Start](/docs/application/quick-start))
  L10: - At least one model is configured in `config.yaml`
  L11: 
  L12: ## Steps
  L13: 
  L14: <Steps>
  L15: 
  L16: ### Open the workspace
  L17: 
  L18: Open [http://localhost:2026](http://localhost:2026) in your browser. You will see the conversation workspace.
  L19: 
  L20: ### Send your first message
  L21: 
  L22: Type a question in the input box, for example:
  ... (truncated)
- `frontend/src/content/en/tutorials/use-tools-and-skills.mdx`
  L1: import { Callout } from "nextra/components";
  L2: 
  L5: This tutorial shows you how to configure and use tools and skills in DeerFlow to give the agent access to web search, file operations, and domain-specific capabilities.
  L6: 
  L7: ## Configuring tools
  L8: 
  L9: Add tools to `config.yaml`:
  L10: 
  L11: ```yaml
  L12: tools:
  L13: # Web search
  L14: - use: deerflow.community.ddg_search.tools:web_search_tool
  L15: 
  L16: # Web content fetching
  L17: - use: deerflow.community.jina_ai.tools:web_fetch_tool
  L18: 
  L19: # Sandbox file operations
  L20: - use: deerflow.sandbox.tools:ls_tool
  L21: - use: deerflow.sandbox.tools:read_file_tool
  L22: - use: deerflow.sandbox.tools:write_file_tool
  ... (truncated)
- `frontend/src/content/en/tutorials/work-with-memory.mdx`
  L1: import { Callout } from "nextra/components";
  L2: 
  L5: This tutorial shows you how to enable and use DeerFlow's memory system so the agent remembers important information about you across multiple sessions.
  L6: 
  L7: ## Enable memory
  L8: 
  L9: In `config.yaml`:
  L10: 
  L11: ```yaml
  L12: memory:
  L13: enabled: true
  L14: injection_enabled: true
  L15: max_injection_tokens: 2000
  L16: debounce_seconds: 30
  L17: ```
  L18: 
  L19: ## How memory works
  L20: 
  L21: Memory works automatically through `MemoryMiddleware`:
  L22: 
  ... (truncated)
- `frontend/src/content/zh/_meta.ts`
- `frontend/src/content/zh/application/_meta.ts`
- `frontend/src/content/zh/application/agents-and-threads.mdx`
  L1: import { Callout, Cards, Steps } from "nextra/components";
  L2: 
  L3: # Agent 与线程
  L4: 
  L5: <Callout type="info" emoji="🤖">
  L6: Agent 是配置单元——它们定义了一组能力。线程是对话实例，带有持久化状态和历史记录。
  L7: </Callout>
  L8: 
  L9: ## 自定义 Agent
  L10: 
  L11: DeerFlow 允许你创建多个具有不同专业领域的自定义 Agent。每个 Agent 使用 DeerFlow Harness 相同的 Lead Agent 运行时，但具有不同的：
  L12: 
  L13: - 模型（例如为一个 Agent 使用 GPT-4o，为另一个使用 Claude）
  L14: - 系统提示和指令
  L15: - 技能（例如专注于数据分析的 Agent 只加载数据分析技能）
  L16: - 工具访问（通过工具组）
  L17: 
  L18: ### 创建自定义 Agent
  L19: 
  L20: <Steps>
  ... (truncated)
- `frontend/src/content/zh/application/configuration.mdx`
  L1: import { Callout, Cards, Tabs } from "nextra/components";
  L2: 
  L3: # 配置
  L4: 
  L5: 本页面涵盖 DeerFlow 应用的所有配置层——`config.yaml`、前端环境变量、`extensions_config.json` 和运行时环境变量。
  L6: 
  L7: ## config.yaml
  L8: 
  L9: `config.yaml` 是 DeerFlow 的主要配置文件。所有 Agent 行为、模型选择、工具加载和运行时功能都由它控制。
  L10: 
  L11: 参见[配置](/docs/harness/configuration)参考页面了解文件格式和每个章节的详细说明。
  L12: 
  L13: ### 模型提供商
  L14: 
  L15: <Tabs items={["OpenAI", "Claude", "Gemini", "DeepSeek", "Ollama（本地）"]}>
  L16: <Tabs.Tab>
  L17: ```yaml
  L18: models:
  L19: - name: gpt-4o
  L20: use: langchain_openai:ChatOpenAI
  ... (truncated)
- `frontend/src/content/zh/application/deployment-guide.mdx`
  L1: import { Callout, Cards, Steps, Tabs } from "nextra/components";
  L2: 
  L3: # 部署指南
  L4: 
  L5: 本指南涵盖 DeerFlow 应用所有支持的部署方式：本地开发、Docker Compose 以及使用 Kubernetes 管理沙箱的生产环境。
  L6: 
  L7: ## 本地开发部署
  L8: 
  L9: 本地工作流是运行 DeerFlow 最快的方式，所有服务作为原生进程在你的机器上运行。
  L10: 
  L11: <Tabs items={["启动", "停止", "日志"]}>
  L12: <Tabs.Tab>
  L13: ```bash
  L14: make dev
  L15: ```
  L16: 
  L17: 启动的服务：
  L18: 
  L19: | 服务 | 端口 | 描述 |
  L20: |---|---|---|
  ... (truncated)
- `frontend/src/content/zh/application/index.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # DeerFlow 应用
  L4: 
  L5: <Callout type="info" emoji="🚀">
  L6: DeerFlow 应用是构建在 DeerFlow Harness 之上的完整 Super Agent 应用。它将运行时能力打包成一个可部署的产品，包含 Web 界面、API Gateway 和运维工具。
  L7: </Callout>
  L8: 
  L9: DeerFlow 应用是 DeerFlow 生产体验的参考实现。它将 Harness 运行时、基于 Web 的对话工作区、API Gateway 和反向代理组合成一个可部署的完整系统。
  L10: 
  L11: ## 应用提供什么
  L12: 
  L13: | 能力 | 描述 |
  L14: |---|---|
  L15: | **Web 工作区** | 浏览器对话界面，支持线程、产出物、文件上传和技能选择 |
  L16: | **自定义 Agent** | 创建和管理具有不同模型、技能和工具集的命名 Agent |
  L17: | **线程管理** | 带检查点和历史记录的持久化对话线程 |
  L18: | **流式响应** | 实时 token 流式传输，带思考步骤和工具调用可见性 |
  L19: | **产出物查看器** | Agent 生成文件和输出的浏览器内预览和下载 |
  L20: | **扩展界面** | 无需编辑配置文件即可启用/禁用 MCP 服务器和技能 |
  ... (truncated)
- `frontend/src/content/zh/application/operations-and-troubleshooting.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # 运维与排障
  L4: 
  L5: 本页面涵盖运行 DeerFlow 应用的操作信息：日志记录、常见问题和维护任务。
  L6: 
  L7: ## 日志
  L8: 
  L9: DeerFlow 应用在 `logs/` 目录中写入每个服务的日志：
  L10: 
  L11: | 文件 | 内容 |
  L12: |---|---|
  L13: | `logs/langgraph.log` | Agent 运行时、工具调用、LangGraph 错误 |
  L14: | `logs/gateway.log` | API 请求/响应、Gateway 错误 |
  L15: | `logs/frontend.log` | Next.js 服务器日志 |
  L16: | `logs/nginx.log` | 代理访问和错误日志 |
  L17: 
  L18: **实时追踪日志**：
  L19: 
  L20: ```bash
  ... (truncated)
- `frontend/src/content/zh/application/quick-start.mdx`
  L1: import { Callout, Cards, Steps } from "nextra/components";
  L2: 
  L3: # 快速上手
  L4: 
  L5: <Callout type="info" emoji="⚡">
  L6: 大约 10 分钟即可在本地运行 DeerFlow 应用。你需要一台安装了 Python 3.12+、Node.js 22+ 的机器，以及至少一个 LLM API Key。
  L7: </Callout>
  L8: 
  L9: 本指南引导你使用 `make dev` 工作流在本地机器上启动 DeerFlow 应用。所有四个服务（LangGraph、Gateway、前端、nginx）一起启动，通过单个 URL 访问。
  L10: 
  L11: ## 前置条件
  L12: 
  L13: 检查所有必需工具是否已安装：
  L14: 
  L15: ```bash
  L16: make check
  L17: ```
  L18: 
  L19: 必需工具：
  L20: 
  ... (truncated)
- `frontend/src/content/zh/application/workspace-usage.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # 工作区使用
  L4: 
  L5: <Callout type="info" emoji="💬">
  L6: DeerFlow 工作区是你与 Agent 交互的地方。本页面涵盖主要用户界面工作流——创建对话、上传文件、查看产出物和使用技能。
  L7: </Callout>
  L8: 
  L9: DeerFlow 工作区是一个基于浏览器的对话界面，你可以在其中向 Agent 发送消息、上传文件、查看中间步骤，以及下载生成的产出物。
  L10: 
  L11: ## 新建对话
  L12: 
  L13: 1. 打开 [http://localhost:2026](http://localhost:2026)。
  L14: 2. 在主界面点击 **New Thread**（新建线程）按钮，或直接在输入框中输入消息。
  L15: 3. 输入你的第一条消息并发送。
  L16: 
  L17: 每个对话是一个**线程**，有独立的历史记录、产出物和检查点。
  L18: 
  L19: ## 选择模型
  L20: 
  ... (truncated)
- `frontend/src/content/zh/harness/_meta.ts`
- `frontend/src/content/zh/harness/configuration.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # 配置
  L4: 
  L5: <Callout type="info" emoji="⚙️">
  L6: 所有 DeerFlow Harness 行为都由 <code>config.yaml</code> 驱动。一个文件控制哪些模型可用、沙箱如何运行、加载哪些工具，以及每个子系统的行为。
  L7: </Callout>
  L8: 
  L9: DeerFlow 的配置系统围绕一个目标设计：每一个有意义的行为都应该可以在配置文件中表达，而不是硬编码在应用程序中。这使部署可重现、可审计，并且易于按环境定制。
  L10: 
  L11: ## 配置文件位置
  L12: 
  L13: DeerFlow 使用以下优先级顺序解析 `config.yaml`：
  L14: 
  L15: 1. 显式传递给 `AppConfig.from_file(config_path)` 的路径。
  L16: 2. `DEER_FLOW_CONFIG_PATH` 环境变量。
  L17: 3. `backend/config.yaml`（相对于后端目录）。
  L18: 4. 仓库根目录中的 `config.yaml`。
  L19: 
  L20: 如果这些路径都不存在，应用程序在启动时会报错。
  ... (truncated)
- `frontend/src/content/zh/harness/customization.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # 自定义与扩展
  L4: 
  L5: <Callout type="info" emoji="🔧">
  L6: DeerFlow 设计为可适配的。你可以通过编写自定义中间件、添加新工具、构建技能包以及通过 config.yaml 的 <code>use:</code> 字段替换任何内置组件来扩展 Agent 行为。
  L7: </Callout>
  L8: 
  L9: DeerFlow 的可插拔架构意味着系统的大多数部分都可以在不 fork 核心的情况下被替换或扩展。本页面列举了扩展点，并解释如何使用每一个。
  L10: 
  L11: ## 自定义中间件
  L12: 
  L13: 中间件是为 Lead Agent 添加行为的主要扩展点。它们包裹每次 LLM 调用，可以在模型调用前后读取和修改 Agent 的状态。
  L14: 
  L15: 添加自定义中间件：
  L16: 
  L17: 1. 实现 `langchain.agents.middleware` 中的 `AgentMiddleware` 接口。
  L18: 2. 在构建 Agent 时通过 `custom_middlewares` 参数传入你的中间件。
  L19: 
  L20: ```python
  ... (truncated)
- `frontend/src/content/zh/harness/design-principles.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # 设计理念
  L4: 
  L5: <Callout type="info" emoji="🏗️">
  L6: DeerFlow 围绕一个核心思想构建：Agent 行为应该由小型、可观察、可替换的组件组合而成——而不是硬编码到固定的工作流图中。
  L7: </Callout>
  L8: 
  L9: 了解 DeerFlow Harness 背后的设计理念，有助于你有效地使用它、自信地扩展它，并推断 Agent 在生产环境中的行为方式。
  L10: 
  L11: ## 为什么是 Harness，而非 Framework
  L12: 
  L13: 框架提供抽象和构建块，你负责组装各部分并编写连接它们的胶水代码。
  L14: 
  L15: **Harness** 更进一步。它打包了一个有主张的、可直接运行的运行时，让 Agent 无需你每次重建相同的基础设施就能完成真实工作。
  L16: 
  L17: DeerFlow 之所以是 Harness，是因为它内置了：
  L18: 
  L19: - 带有工具路由的 Lead Agent
  L20: - 包裹每次 LLM 调用的中间件链
  ... (truncated)
- `frontend/src/content/zh/harness/index.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # 安装 DeerFlow Harness
  L4: 
  L5: <Callout type="info" emoji="📦">
  L6: DeerFlow Harness Python 包将以 <code>deerflow</code> 名称发布。目前尚未正式发布，安装方式<strong>即将推出</strong>。
  L7: </Callout>
  L8: 
  L9: DeerFlow Harness 是构建自己 Super Agent 系统的 Python SDK 和运行时基础。
  L10: 
  L11: 如果你想在自己的产品或工作流中整合技能、记忆、工具、沙箱和子 Agent 等 Agent 能力，这正是你需要的 DeerFlow 组件。
  L12: 
  L13: ## 包名称
  L14: 
  L15: 包名将是：
  L16: 
  L17: ```bash
  L18: pip install deerflow
  L19: ```
  L20: 
  ... (truncated)
- `frontend/src/content/zh/harness/integration-guide.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # 集成指南
  L4: 
  L5: <Callout type="info" emoji="🔌">
  L6: DeerFlow Harness 可以嵌入任何 Python 应用程序。本指南涵盖在你自己的系统中将 DeerFlow 作为库使用的集成模式。
  L7: </Callout>
  L8: 
  L9: DeerFlow Harness 不仅仅是一个独立应用程序——它是一个可以导入并在你自己的后端、API 服务器、自动化系统或多 Agent 协调器中使用的 Python 库。
  L10: 
  L11: ## 嵌入 DeerFlowClient
  L12: 
  L13: 主要集成点是 `DeerFlowClient`。它封装了 LangGraph 运行时，并提供一个简洁的 API，用于在任何 Python 应用中发送消息和流式传输响应。
  L14: 
  L15: ```python
  L16: from deerflow.client import DeerFlowClient
  L17: from deerflow.config import load_config
  L18: 
  L19: # 加载配置（读取 config.yaml 或 DEER_FLOW_CONFIG_PATH）
  L20: load_config()
  ... (truncated)
- `frontend/src/content/zh/harness/lead-agent.mdx`
  L1: import { Callout, Cards, Steps } from "nextra/components";
  L2: 
  L3: # Lead Agent
  L4: 
  L5: <Callout type="info" emoji="🧠">
  L6: Lead Agent 是每个 DeerFlow 线程中的主要推理和编排单元。它决定要做什么、调用工具、委派子 Agent，并返回产出物。
  L7: </Callout>
  L8: 
  L9: Lead Agent 是 DeerFlow 线程中的核心执行者。每个对话、任务和工作流都通过它进行。理解它的工作方式有助于你有效地配置它，并在需要时扩展它。
  L10: 
  L11: ## Lead Agent 的职责
  L12: 
  L13: Lead Agent 负责：
  L14: 
  L15: - 接收用户消息并维护对话状态
  L16: - 推断接下来要做什么（规划、工具选择、委派）
  L17: - 调用工具——内置工具、社区工具、MCP 工具或技能工具
  L18: - 通过 `task` 工具将子任务委派给子 Agent
  L19: - 管理产出物（文件、输出、交付物）
  L20: - 在计划模式下更新待办列表
  ... (truncated)
- `frontend/src/content/zh/harness/mcp.mdx`
  L1: import { Callout, Cards, Steps } from "nextra/components";
  L2: 
  L3: # MCP 集成
  L4: 
  L5: <Callout type="info" emoji="🔌">
  L6: Model Context Protocol（MCP）让 DeerFlow 能够连接任何外部工具服务器。连接后，MCP 工具与内置工具一样对 Lead Agent 可用。
  L7: </Callout>
  L8: 
  L9: **Model Context Protocol（MCP）** 是连接语言模型与外部工具和数据源的开放标准。DeerFlow 的 MCP 集成允许你用任何实现了 MCP 协议的工具服务器扩展 Agent——无需修改 Harness 本身。
  L10: 
  L11: ## 配置
  L12: 
  L13: MCP 服务器在 `extensions_config.json` 中配置，这个文件独立于 `config.yaml`。这种分离允许 MCP 和技能配置独立管理，并在运行时通过 Gateway API 更新。
  L14: 
  L15: 默认位置是项目根目录（与 `config.yaml` 同一目录）。
  L16: 
  L17: ```json
  L18: {
  L19: "mcpServers": {
  L20: "my-server": {
  ... (truncated)
- `frontend/src/content/zh/harness/memory.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # 记忆系统
  L4: 
  L5: <Callout type="info" emoji="💾">
  L6: 记忆让 DeerFlow 在多个会话中保留有用信息。Agent 记住用户偏好、项目背景和反复出现的事实，这样它可以在不每次从零开始的情况下给出更好的响应。
  L7: </Callout>
  L8: 
  L9: 记忆是 DeerFlow Harness 的一个运行时功能。它不是简单的对话日志，而是跨多个独立会话持久化、在未来对话中影响 Agent 行为的结构化事实和上下文摘要存储。
  L10: 
  L11: ## 记忆存储什么
  L12: 
  L13: 记忆存储包含几类信息：
  L14: 
  L15: - **工作上下文**：用户正在进行的项目摘要、目标和反复出现的话题。
  L16: - **个人上下文**：Agent 学到的偏好、沟通风格和其他用户特定细节。
  L17: - **近期关注**：最近的关注领域和活跃任务。
  L18: - **历史**：近几个月的上下文、早期背景和长期事实。
  L19: - **事实**：Agent 从对话中提取的离散具体事实（例如偏好的工具、团队名称、项目约束）。
  L20: 
  ... (truncated)
- `frontend/src/content/zh/harness/middlewares.mdx`
  L1: import { Callout } from "nextra/components";
  L2: 
  L3: # 中间件
  L4: 
  L5: <Callout type="info" emoji="🔌">
  L6: 中间件包裹 Lead Agent 中的每次 LLM 调用。它们是添加跨领域行为（如记忆、摘要压缩、澄清和 token 追踪）的主要扩展点。
  L7: </Callout>
  L8: 
  L9: 每次 Lead Agent 调用 LLM 时，都会先后执行一条**中间件链**。中间件可以读取和修改 Agent 的状态、向系统提示注入内容、拦截工具调用，并对模型输出做出反应。
  L10: 
  L11: 这种设计使 Agent 核心保持简单稳定，同时允许丰富的可组合行为分层叠加。
  L12: 
  L13: ## 链的工作方式
  L14: 
  L15: 中间件链在每次 Agent 调用时根据当前配置和请求参数构建一次。中间件按定义的顺序运行：
  L16: 
  L17: 1. 运行时中间件（错误处理、线程数据、上传、悬空工具调用修补）
  L18: 2. `SummarizationMiddleware` — 上下文压缩（如果启用）
  L19: 3. `TodoMiddleware` — 任务列表管理（仅计划模式）
  L20: 4. `TokenUsageMiddleware` — token 追踪（如果启用）
  ... (truncated)
- `frontend/src/content/zh/harness/quick-start.mdx`
  L1: import { Callout, Cards, Steps } from "nextra/components";
  L2: 
  L3: # 快速上手
  L4: 
  L5: <Callout type="info" emoji="🚀">
  L6: 本指南介绍如何以编程方式使用 DeerFlow Harness——不是通过应用界面，而是直接在 Python 中导入和调用 Harness。
  L7: </Callout>
  L8: 
  L9: DeerFlow Harness 是 Python SDK 和运行时基础。本快速上手指南将带你了解运行 Agent、流式传输输出和使用线程的核心 API。
  L10: 
  L11: ## 前置条件
  L12: 
  L13: DeerFlow Harness 需要 Python 3.12 或更高版本。该包是 `deerflow` 代码库的一部分，位于 `backend/packages/harness` 下。
  L14: 
  L15: 如果你从仓库克隆开始：
  L16: 
  L17: ```bash
  L18: cd backend
  L19: uv sync
  L20: ```
  ... (truncated)
- `frontend/src/content/zh/harness/sandbox.mdx`
  L1: import { Callout, Cards, Tabs } from "nextra/components";
  L2: 
  L3: # 沙箱
  L4: 
  L5: <Callout type="info" emoji="📦">
  L6: 沙箱是 Agent 进行文件和命令操作的隔离工作区。它让 DeerFlow 能够采取真实行动，而不仅仅是对话。
  L7: </Callout>
  L8: 
  L9: 沙箱为 Lead Agent 提供一个受控环境，在其中可以读取文件、写入输出、运行 Shell 命令并生成产出物。没有沙箱，Agent 只能生成文本；有了沙箱，它可以编写和执行代码、处理数据文件、生成图表并构建交付物。
  L10: 
  L11: ## 沙箱模式
  L12: 
  L13: DeerFlow 支持三种沙箱模式，选择适合你部署的一种：
  L14: 
  L15: ### LocalSandbox（默认）
  L16: 
  L17: 命令直接在主机机器的文件系统上运行，没有容器隔离。
  L18: 
  L19: - **适合**：受信任的单用户本地开发工作流。
  L20: - **风险**：Agent 可以访问主机文件系统。默认使用 `allow_host_bash: false` 防止任意命令执行。
  ... (truncated)
- `frontend/src/content/zh/harness/skills.mdx`
  L1: import { Callout, Cards, FileTree, Steps } from "nextra/components";
  L2: 
  L3: # 技能
  L4: 
  L5: <Callout type="info" emoji="🎯">
  L6: 技能是面向任务的能力包，教会 Agent 如何完成特定类型的工作。基础 Agent 保持通用；技能在需要时提供专业化。
  L7: </Callout>
  L8: 
  L9: 技能不仅仅是提示词。它是一个自包含的能力包，可以包含结构化指令、分步工作流、领域最佳实践、支撑资源和工具配置。技能按需加载——在任务需要时注入内容，否则不影响上下文。
  L10: 
  L11: ## 技能包含什么
  L12: 
  L13: 每个技能位于 `skills/public/`（或用户创建技能的 `skills/custom/`）下自己的子目录中。目录包含一个 `SKILL.md` 文件，定义技能的元数据、指令和工作流。
  L14: 
  L15: <FileTree>
  L16: <FileTree.Folder name="skills/" defaultOpen>
  L17: <FileTree.Folder name="public/" defaultOpen>
  L18: <FileTree.Folder name="deep-research/" defaultOpen>
  L19: <FileTree.File name="SKILL.md" />
  L20: </FileTree.Folder>
  ... (truncated)
- `frontend/src/content/zh/harness/subagents.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # 子 Agent
  L4: 
  L5: <Callout type="info" emoji="👥">
  L6: 子 Agent 是 Lead Agent 委派子任务的专注执行者。它们以隔离的上下文运行，在处理并行或专业工作的同时保持主对话清晰。
  L7: </Callout>
  L8: 
  L9: 当一个任务对单个推理线程来说太宽泛，或者部分任务可以并行完成时，Lead Agent 将工作委派给**子 Agent**。子 Agent 是一个独立的 Agent 调用，接收特定任务、执行并返回结果。
  L10: 
  L11: ## 为什么子 Agent 很重要
  L12: 
  L13: 子 Agent 解决了长时序工作流中的两个关键问题：
  L14: 
  L15: 1. **上下文隔离**：子 Agent 只看到完成其任务所需的信息，而不是整个父对话。这保持了每个 Agent 的工作上下文专注且可控。
  L16: 2. **并行性**：多个子 Agent 可以并发运行，允许任务的独立部分（例如同时研究多个话题）并行处理。
  L17: 
  L18: ## 内置子 Agent
  L19: 
  L20: DeerFlow 内置两个子 Agent：
  ... (truncated)
- `frontend/src/content/zh/harness/tools.mdx`
  L1: import { Callout, Cards, Tabs } from "nextra/components";
  L2: 
  L3: # 工具
  L4: 
  L5: <Callout type="info" emoji="🔧">
  L6: 工具是 Lead Agent 可以采取的行动。DeerFlow 提供内置工具、社区集成、MCP 工具和技能工具——全部通过 <code>config.yaml</code> 控制。
  L7: </Callout>
  L8: 
  L9: Lead Agent 是一个工具调用 Agent。工具是它与世界交互的方式：搜索网络、读写文件、运行命令、委派任务以及向用户呈现输出。
  L10: 
  L11: DeerFlow 将工具分为四类：
  L12: 
  L13: 1. **内置工具** — 核心运行时能力，始终对 Agent 可用
  L14: 2. **社区工具** — 与外部搜索、抓取和图像服务的集成
  L15: 3. **MCP 工具** — 由外部 Model Context Protocol 服务器提供的工具
  L16: 4. **技能工具** — 与特定技能包捆绑的工具
  L17: 
  L18: ## 内置工具
  L19: 
  L20: 内置工具是 Harness 的一部分，无需配置即可使用。
  ... (truncated)
- `frontend/src/content/zh/index.mdx`
  L2: title: DeerFlow 文档
  L6: # DeerFlow 文档
  L7: 
  L8: DeerFlow 是一个用于构建和运行 Agent 系统的框架。它提供了一个运行时 Harness，可以将 Agent 与记忆、工具、技能、沙箱和子 Agent 组合在一起；同时还提供了一个应用层，将这些能力转化为可用的产品体验。
  L9: 
  L10: 本文档围绕这两个部分组织：
  L11: 
  L12: - **DeerFlow Harness**：用于构建 Agent 系统的核心 SDK 和运行时层。
  L13: - **DeerFlow 应用**：构建在 Harness 之上的参考应用，用于部署、运维和终端用户工作流。
  L14: 
  L15: 如果你想了解 DeerFlow 的工作原理，从简介开始阅读。如果你想基于核心运行时进行开发，请查阅 Harness 文档。如果你想将 DeerFlow 作为应用部署和使用，请查阅应用文档。
  L16: 
  L17: ## 从这里开始
  L18: 
  L19: ### 如果你是 DeerFlow 新手
  L20: 
  L21: 先从概念概述开始。
  L22: 
  L23: - [简介](/docs/introduction)
  L24: - [为什么选择 DeerFlow](/docs/introduction/why-deerflow)
  ... (truncated)
- `frontend/src/content/zh/introduction/_meta.ts`
- `frontend/src/content/zh/introduction/core-concepts.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # 核心概念
  L4: 
  L5: <Callout type="important" emoji="🧠">
  L6: 如果你将 DeerFlow 理解为一个长时序 Agent 的运行时，而不仅仅是聊天界面或工作流图，它将最易于理解。
  L7: </Callout>
  L8: 
  L9: 在深入了解 DeerFlow 之前，先建立一些贯穿整个系统的核心概念。这些概念解释了 DeerFlow 的优化目标以及其架构设计的原因。
  L10: 
  L11: ## Harness
  L12: 
  L13: 在 DeerFlow 中，**Harness** 是为 Agent 提供所需运行环境的运行时层，让 Agent 能够真正完成工作。
  L14: 
  L15: 框架通常提供抽象和构建块。Harness 更进一步：它打包了一套有主张的运行时能力，让 Agent 无需每次重建相同基础设施，就能在真实环境中进行规划、行动、使用工具、管理文件和处理长时序任务。
  L16: 
  L17: 在实践中，DeerFlow 的 Harness 包括：
  L18: 
  L19: - 工具访问
  L20: - 技能加载
  ... (truncated)
- `frontend/src/content/zh/introduction/harness-vs-app.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # Harness 与应用
  L4: 
  L5: <Callout type="info" emoji="⚙️">
  L6: DeerFlow 应用是构建在 DeerFlow Harness 之上的最佳实践 Super Agent 应用，而 DeerFlow Harness 是构建自己 Agent 系统的 Python SDK 和运行时基础。
  L7: </Callout>
  L8: 
  L9: DeerFlow 有两个紧密相关但服务于不同目的的层次：
  L10: 
  L11: - **DeerFlow Harness** 是运行时基础层。
  L12: - **DeerFlow 应用** 是构建在该基础之上的最佳实践应用。
  L13: 
  L14: 理解这一区别，能让其余文档更易于阅读。
  L15: 
  L16: ## Harness 是运行时层
  L17: 
  L18: **DeerFlow Harness** 是用于构建和运行长时序 Agent 的可复用系统。
  L19: 
  L20: 它提供：长时序任务的规划和执行、工具调用和沙箱执行、技能加载和上下文注入、记忆和跨会话持久化、子 Agent 协调、以及完整的配置和扩展系统。
  ... (truncated)
- `frontend/src/content/zh/introduction/why-deerflow.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # 为什么选择 DeerFlow
  L4: 
  L5: <Callout type="info" emoji="🦌">
  L6: DeerFlow 起源于深度研究，但逐渐演化为一个通用的长时序 Agent 运行时——支持技能、记忆、工具和协作调度。
  L7: </Callout>
  L8: 
  L9: DeerFlow 的诞生是因为现代 Agent 系统需要的不仅仅是一个聊天循环。一个真正有用的 Agent 必须能够进行长时序规划、将任务拆解为子任务、使用工具、操作文件、安全地运行代码，并在复杂任务中保持足够的上下文连贯性。DeerFlow 正是为提供这样的运行时基础而构建的。
  L10: 
  L11: ## 从深度研究起步
  L12: 
  L13: DeerFlow 的第一个版本围绕一个具体目标设计：生成真正有深度的研究产出，而不是轻量级聊天机器人的概要总结。核心思路是让 AI 系统像研究团队一样工作：制定计划、收集来源、交叉验证发现，并输出有实际深度的结构化结果。
  L14: 
  L15: 这个定位是有效的，但项目很快揭示了更重要的东西。团队不仅将 DeerFlow 用于研究——他们将其应用于数据分析、报告生成、内部自动化、运营工作流，以及其他同样需要多步骤执行的任务。
  L16: 
  L17: 共同点是清晰的：有价值的部分不仅仅是研究工作流本身，而是其背后的运行时能力。
  L18: 
  L19: ## 研究是第一个技能，而非整个系统
  L20: 
  ... (truncated)
- `frontend/src/content/zh/reference/_meta.ts`
- `frontend/src/content/zh/reference/api-gateway-reference.mdx`
  L1: import { Callout } from "nextra/components";
  L2: 
  L3: # API / Gateway 参考
  L4: 
  L5: <Callout type="info">
  L6: DeerFlow Gateway 是基于 FastAPI 构建的，提供交互式 API 文档，可通过 <code>http://localhost:8001/docs</code> 访问。
  L7: </Callout>
  L8: 
  L9: ## 基础 URL
  L10: 
  L11: ```
  L12: http://localhost:8001
  L13: ```
  L14: 
  L15: 通过 nginx 代理：
  L16: 
  L17: ```
  L18: http://localhost:2026/api
  L19: ```
  L20: 
  ... (truncated)
- `frontend/src/content/zh/reference/concepts-glossary.mdx`
  L1: import { Callout } from "nextra/components";
  L2: 
  L3: # 概念词汇表
  L4: 
  L5: 本词汇表定义了 DeerFlow 文档中使用的核心术语。
  L6: 
  L7: ---
  L8: 
  L9: ## Agent
  L10: 
  L11: 在 DeerFlow 中，Agent 是接收用户消息、决定采取什么行动（工具调用或直接响应），并生成输出的主要处理单元。DeerFlow 使用 **Lead Agent** 和**子 Agent** 两级架构。
  L12: 
  L13: ## Artifact（产出物）
  L14: 
  L15: Agent 生成的文件——报告、图表、代码或其他交付物。产出物通过 `present_files` 工具暴露，并持久化存储在线程的用户数据目录中。
  L16: 
  L17: ## Checkpoint（检查点）
  L18: 
  L19: 线程状态的持久化快照，在每次 Agent 轮次后保存。检查点允许服务器重启后恢复对话，并支持长时序任务的状态管理。
  L20: 
  ... (truncated)
- `frontend/src/content/zh/reference/configuration-reference.mdx`
  L1: import { Callout } from "nextra/components";
  L2: 
  L3: # 配置参考
  L4: 
  L5: 本页面提供 `config.yaml` 中所有顶层字段的完整参考。
  L6: 
  L7: <Callout type="info">
  L8: 查看仓库根目录中的 <code>config.example.yaml</code> 获取带注释的完整配置示例。
  L9: </Callout>
  L10: 
  L11: ## 顶层字段
  L12: 
  L13: | 字段 | 类型 | 说明 |
  L14: |---|---|---|
  L15: | `config_version` | `int` | 配置 schema 版本（当前：6） |
  L16: | `log_level` | `str` | 日志级别：`debug`/`info`/`warning`/`error` |
  L17: | `models` | `list` | 可用的 LLM 模型配置 |
  L18: | `image_generate_model` | `str \| list` | 图像生成使用的模型名称 |
  L19: | `token_usage` | `object` | Token 使用追踪配置 |
  L20: | `tools` | `list` | 可用工具配置 |
  ... (truncated)
- `frontend/src/content/zh/reference/runtime-flags-and-modes.mdx`
  L1: # 运行时标志与模式
  L2: 
  L3: 本页面记录影响 DeerFlow Harness 和 Agent 运行时行为的运行时标志和模式。
  L4: 
  L5: ## 每次请求的可配置选项
  L6: 
  L7: 这些选项通过 `config.configurable` 字典传递（用于程序化使用）或在 Web UI 中选择（用于应用使用）：
  L8: 
  L9: | 标志 | 类型 | 默认值 | 描述 |
  L10: |---|---|---|---|
  L11: | `model_name` | `str \| None` | 配置的第一个模型 | 请求使用的模型 |
  L12: | `agent_name` | `str \| None` | `None` | 加载自定义 Agent 配置 |
  L13: | `thinking_enabled` | `bool` | `True` | 启用扩展思考（模型必须支持） |
  L14: | `reasoning_effort` | `str \| None` | `None` | 推理努力程度（模型特定） |
  L15: | `is_plan_mode` | `bool` | `False` | 启用 TodoList 中间件 |
  L16: | `subagent_enabled` | `bool` | `False` | 允许子 Agent 委派 |
  L17: | `max_concurrent_subagents` | `int` | `3` | 最大并行子 Agent 调用数 |
  L18: 
  L19: ## 环境变量
  L20: 
  ... (truncated)
- `frontend/src/content/zh/reference/source-map.mdx`
  L1: # 代码映射
  L2: 
  L3: 本页面将 DeerFlow 的核心概念映射到其在代码库中的实现位置，帮助你快速定位特定功能的代码。
  L4: 
  L5: ## 后端核心路径
  L6: 
  L7: ```
  L8: backend/
  L9: ├── app/
  L10: │   └── gateway/              # FastAPI Gateway API
  L11: │       ├── routers/
  L12: │       │   ├── agents.py     # 自定义 Agent CRUD
  L13: │       │   ├── extensions.py # MCP/技能启用禁用
  L14: │       │   ├── memory.py     # 记忆读取/清除
  L15: │       │   ├── threads.py    # 线程管理
  L16: │       │   └── uploads.py    # 文件上传
  L17: │       └── main.py           # FastAPI 应用入口
  L18: │
  L19: └── packages/harness/deerflow/
  L20: ├── agents/
  ... (truncated)
- `frontend/src/content/zh/tutorials/_meta.ts`
- `frontend/src/content/zh/tutorials/create-your-first-harness.mdx`
  L1: # 创建你的第一个 Harness
  L2: 
  L3: 本教程介绍如何以编程方式使用 DeerFlow Harness Python SDK——直接在你的 Python 代码中导入和使用 DeerFlow，而不是通过 Web 界面。
  L4: 
  L5: ## 前置条件
  L6: 
  L7: - Python 3.12+
  L8: - 已安装 `uv`
  L9: - 已克隆 DeerFlow 仓库
  L10: 
  L11: ## 安装
  L12: 
  L13: ```bash
  L14: cd deer-flow/backend
  L15: uv sync
  L16: ```
  L17: 
  L18: ## 创建配置
  L19: 
  L20: 创建一个最小的 `config.yaml`：
  ... (truncated)
- `frontend/src/content/zh/tutorials/deploy-your-own-deerflow.mdx`
  L1: # 部署你的 DeerFlow
  L2: 
  L3: 本教程引导你将 DeerFlow 部署到生产环境，使用 Docker Compose 进行多用户访问。
  L4: 
  L5: ## 前置条件
  L6: 
  L7: - 已安装 Docker 和 Docker Compose
  L8: - 服务器或 VM（Linux 推荐）
  L9: - LLM API Key
  L10: 
  L11: ## 步骤
  L12: 
  L13: ### 1. 克隆仓库
  L14: 
  L15: ```bash
  L16: git clone https://github.com/bytedance/deer-flow.git
  L17: cd deer-flow
  L18: ```
  L19: 
  L20: ### 2. 创建配置文件
  ... (truncated)
- `frontend/src/content/zh/tutorials/first-conversation.mdx`
  L1: # 第一次对话
  L2: 
  L3: 本教程引导你在 DeerFlow 中完成第一次完整的 Agent 对话，从启动应用到与 Agent 进行实质性任务交互。
  L4: 
  L5: ## 前置条件
  L6: 
  L7: - DeerFlow 应用已运行（参见[快速上手](/docs/application/quick-start)）
  L8: - 至少在 `config.yaml` 中配置了一个模型
  L9: 
  L10: ## 步骤
  L11: 
  L12: ### 1. 打开工作区
  L13: 
  L14: 在浏览器中访问 [http://localhost:2026](http://localhost:2026)，你将看到对话工作区。
  L15: 
  L16: ### 2. 发送第一条消息
  L17: 
  L18: 在输入框中输入问题，例如：
  L19: 
  L20: ```
  ... (truncated)
- `frontend/src/content/zh/tutorials/use-tools-and-skills.mdx`
  L1: # 使用工具和技能
  L2: 
  L3: 本教程介绍如何在 DeerFlow 中配置和使用工具（Tools）与技能（Skills），让 Agent 能够访问搜索、文件操作和特定领域能力。
  L4: 
  L5: ## 配置工具
  L6: 
  L7: 在 `config.yaml` 中添加工具：
  L8: 
  L9: ```yaml
  L10: tools:
  L11: # 网络搜索
  L12: - use: deerflow.community.ddg_search.tools:web_search_tool
  L13: 
  L14: # 网页内容抓取
  L15: - use: deerflow.community.jina_ai.tools:web_fetch_tool
  L16: 
  L17: # 沙箱文件操作
  L18: - use: deerflow.sandbox.tools:ls_tool
  L19: - use: deerflow.sandbox.tools:read_file_tool
  L20: - use: deerflow.sandbox.tools:write_file_tool
  ... (truncated)
- `frontend/src/content/zh/tutorials/work-with-memory.mdx`
  L1: # 使用记忆系统
  L2: 
  L3: 本教程介绍如何在 DeerFlow 中启用和使用记忆系统，让 Agent 在多次会话中记住关于你的重要信息。
  L4: 
  L5: ## 启用记忆
  L6: 
  L7: 在 `config.yaml` 中启用记忆：
  L8: 
  L9: ```yaml
  L10: memory:
  L11: enabled: true
  L12: injection_enabled: true
  L13: max_injection_tokens: 2000
  L14: debounce_seconds: 30
  L15: ```
  L16: 
  L17: ## 记忆的工作方式
  L18: 
  L19: 记忆通过 `MemoryMiddleware` 自动工作：
  L20: 
  ... (truncated)

## 88f822a8 2026-04-11 copilot-swe-agent[bot]
docs: fill all TBD documentation pages and add new harness module pages

Agent-Logs-Url: https://github.com/bytedance/deer-flow/sessions/ff389ed8-31c9-430c-85ff-cc1b52b8239c

Co-authored-by: foreleven <4785594+foreleven@users.noreply.github.com>

- `frontend/src/content/en/application/agents-and-threads.mdx`
  L1: import { Callout, Cards, Steps } from "nextra/components";
  L2: 
  L109: The LangGraph Server manages its own state separately. The
  L110: <code>checkpointer</code> setting in <code>config.yaml</code> applies to the
  L111: embedded <code>DeerFlowClient</code> (used in direct Python integrations), not
  L112: to the LangGraph Server deployment used by DeerFlow App.
- `frontend/src/content/en/application/configuration.mdx`
  L1: import { Callout, Cards, Tabs } from "nextra/components";
  L2: 
  L5: DeerFlow App is configured through two files and a set of environment variables. This page covers the application-level configuration that most operators need to set up before deploying.
  L6: 
  L7: ## Configuration files
  L8: 
  L9: | File | Purpose |
  L10: |---|---|
  L11: | `config.yaml` | Backend configuration: models, sandbox, tools, skills, memory, and all Harness settings |
  L12: | `extensions_config.json` | MCP servers and skill enable/disable state (managed by the App UI and Gateway API) |
  L13: 
  L14: Frontend environment variables control the Next.js build and runtime behavior.
  L15: 
  L16: ## config.yaml
  L17: 
  L18: Start by copying the example:
  L19: 
  L20: ```bash
  L21: cp config.example.yaml config.yaml
  L22: ```
  ... (truncated)
- `frontend/src/content/en/application/deployment-guide.mdx`
  L1: import { Callout, Cards, Steps, Tabs } from "nextra/components";
  L2: 
  L5: This guide covers all supported deployment methods for DeerFlow App: local development, Docker Compose, and production with Kubernetes-managed sandboxes.
  L6: 
  L7: ## Local development deployment
  L8: 
  L9: The local workflow is the fastest way to run DeerFlow. All services run as native processes on your machine.
  L10: 
  L11: <Tabs items={["Start", "Stop", "Logs"]}>
  L12: <Tabs.Tab>
  L13: ```bash
  L14: make dev
  L15: ```
  L16: 
  L17: Services started:
  L18: 
  L19: | Service | Port | Description |
  L20: |---|---|---|
  L21: | LangGraph | 2024 | DeerFlow Harness runtime |
  L22: | Gateway API | 8001 | FastAPI backend |
  ... (truncated)
- `frontend/src/content/en/application/index.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L5: <Callout type="info" emoji="🚀">
  L6: DeerFlow App is a complete Super Agent application built on top of DeerFlow
  L7: Harness. It packages the runtime capabilities into a ready-to-deploy product
  L8: with a web UI, API gateway, and operational tooling.
  L9: </Callout>
  L10: 
  L11: DeerFlow App is the reference implementation of what a production DeerFlow experience looks like. It assembles the Harness runtime, a web-based conversation workspace, an API gateway, and a reverse proxy into a single deployable system.
  L12: 
  L13: ## What the App provides
  L14: 
  L15: | Capability | Description |
  L16: |---|---|
  L17: | **Web workspace** | Browser-based conversation UI with support for threads, artifacts, file uploads, and skill selection |
  L18: | **Custom agents** | Create and manage named agents with different models, skills, and tool sets |
  L19: | **Thread management** | Persistent conversation threads with checkpointing and history |
  L20: | **Streaming responses** | Real-time token streaming with thinking steps and tool call visibility |
  L21: | **Artifact viewer** | In-browser preview and download of files and outputs produced by the agent |
  L22: | **Extensions UI** | Enable/disable MCP servers and skills without editing config files |
  ... (truncated)
- `frontend/src/content/en/application/operations-and-troubleshooting.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L5: This page covers day-to-day operational tasks and solutions to common problems when running DeerFlow App.
  L6: 
  L7: ## Log files
  L8: 
  L9: All services write logs to the `logs/` directory when started with `make dev`:
  L10: 
  L11: | File | Service |
  L12: |---|---|
  L13: | `logs/langgraph.log` | LangGraph / DeerFlow Harness runtime |
  L14: | `logs/gateway.log` | FastAPI Gateway API |
  L15: | `logs/frontend.log` | Next.js frontend dev server |
  L16: | `logs/nginx.log` | nginx reverse proxy |
  L17: 
  L18: Tail logs in real time:
  L19: 
  L20: ```bash
  L21: tail -f logs/langgraph.log
  L22: tail -f logs/gateway.log
  ... (truncated)
- `frontend/src/content/en/application/quick-start.mdx`
  L1: import { Callout, Cards, Steps } from "nextra/components";
  L2: 
  L5: <Callout type="info" emoji="⚡">
  L6: Get DeerFlow App running locally in about 10 minutes. You need a machine with
  L7: Python 3.12+, Node.js 22+, and at least one LLM API key.
  L8: </Callout>
  L9: 
  L10: This guide walks you through starting DeerFlow App on your local machine using the `make dev` workflow. All four services (LangGraph, Gateway, Frontend, nginx) start together and are accessible through a single URL.
  L11: 
  L12: ## Prerequisites
  L13: 
  L14: Check that all required tools are installed:
  L15: 
  L16: ```bash
  L17: make check
  L18: ```
  L19: 
  L20: Required:
  L21: 
  L22: | Tool | Minimum version |
  ... (truncated)
- `frontend/src/content/en/application/workspace-usage.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L5: The DeerFlow App workspace is a browser-based interface for having multi-turn conversations with the agent, tracking task progress, viewing artifacts, and managing files.
  L6: 
  L7: ## Starting a conversation
  L8: 
  L9: Open the app at `http://localhost:2026` (or your deployment URL). The workspace is split into:
  L10: 
  L11: - **Sidebar** (left): thread list, new thread button, and navigation to agents and settings.
  L12: - **Conversation area** (center): the active thread's message history.
  L13: - **Input bar** (bottom): text input, skill selector, model selector, and attachment controls.
  L14: 
  L15: To start a new thread, click **New Thread** in the sidebar or use the keyboard shortcut. Each thread is independent — it has its own conversation history, artifacts, and state.
  L16: 
  L17: ## Selecting a model
  L18: 
  L19: Use the model picker in the input bar to choose which configured model to use for the current request. Models listed here correspond to the `models:` entries in your `config.yaml`.
  L20: 
  L21: The selected model applies to the next message only. You can switch models between messages in the same thread.
  L22: 
  ... (truncated)
- `frontend/src/content/en/harness/_meta.ts`
- `frontend/src/content/en/harness/configuration.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L5: <Callout type="info" emoji="⚙️">
  L6: All DeerFlow Harness behaviors are driven by <code>config.yaml</code>. One
  L7: file controls which models are available, how the sandbox runs, what tools are
  L8: loaded, and how each subsystem behaves.
  L9: </Callout>
  L10: 
  L11: DeerFlow's configuration system is designed around one goal: every meaningful behavior should be expressible in a config file, not hardcoded in the application. This makes deployments reproducible, auditable, and easy to customize per environment.
  L12: 
  L13: ## Config file location
  L14: 
  L15: DeerFlow resolves `config.yaml` using the following priority order:
  L16: 
  L17: 1. The path passed to `AppConfig.from_file(config_path)` explicitly.
  L18: 2. The `DEER_FLOW_CONFIG_PATH` environment variable.
  L19: 3. `backend/config.yaml` (relative to the backend directory).
  L20: 4. `config.yaml` in the repository root.
  L21: 
  L22: If none of these paths exist, the application raises an error at startup.
  ... (truncated)
- `frontend/src/content/en/harness/design-principles.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L5: <Callout type="info" emoji="🏗️">
  L6: DeerFlow is built around one central idea: agent behavior should be composed
  L7: from small, observable, replaceable pieces — not hardcoded into a fixed
  L8: workflow graph.
  L9: </Callout>
  L10: 
  L11: Understanding the design principles behind DeerFlow Harness helps you use it effectively, extend it confidently, and reason about how your agents will behave in production.
  L12: 
  L13: ## Why a harness, not a framework
  L14: 
  L15: A framework gives you abstractions and building blocks. You assemble the parts and write the glue code that connects them.
  L16: 
  L17: A **harness** goes further. It packages an opinionated, ready-to-run runtime so that agents can do real work without you rebuilding the same infrastructure every time.
  L18: 
  L19: DeerFlow is a harness because it bundles:
  L20: 
  L21: - a lead agent with tool routing,
  L22: - a middleware chain that wraps every LLM turn,
  ... (truncated)
- `frontend/src/content/en/harness/lead-agent.mdx`
  L1: import { Callout, Cards, Steps } from "nextra/components";
  L2: 
  L3: # Lead Agent
  L4: 
  L5: <Callout type="info" emoji="🧠">
  L6: The Lead Agent is the primary reasoning and orchestration unit in every
  L7: DeerFlow thread. It decides what to do, calls tools, delegates to subagents,
  L8: and returns artifacts.
  L9: </Callout>
  L10: 
  L11: The Lead Agent is the central executor in a DeerFlow thread. Every conversation, task, and workflow flows through it. Understanding how it works helps you configure it effectively and extend it when needed.
  L12: 
  L13: ## What the Lead Agent does
  L14: 
  L15: The Lead Agent is responsible for:
  L16: 
  L17: - receiving user messages and maintaining conversation state,
  L18: - reasoning about what to do next (planning, tool selection, delegation),
  L19: - calling tools — built-in, community, MCP, or skill tools,
  L20: - delegating subtasks to subagents via the `task` tool,
  ... (truncated)
- `frontend/src/content/en/harness/mcp.mdx`
  L1: import { Callout, Cards, Steps } from "nextra/components";
  L2: 
  L3: # MCP Integration
  L4: 
  L5: <Callout type="info" emoji="🔌">
  L6: Model Context Protocol (MCP) lets DeerFlow connect to any external tool
  L7: server. Once connected, MCP tools are available to the Lead Agent exactly like
  L8: built-in tools.
  L9: </Callout>
  L10: 
  L11: The **Model Context Protocol (MCP)** is an open standard for connecting language models to external tools and data sources. DeerFlow's MCP integration allows you to extend the agent with any tool server that implements the MCP protocol — without modifying the harness itself.
  L12: 
  L13: ## Configuration
  L14: 
  L15: MCP servers are configured in `extensions_config.json`, a file separate from `config.yaml`. This separation allows MCP and skill configurations to be managed independently and updated at runtime through the Gateway API.
  L16: 
  L17: The default location is the project root (same directory as `config.yaml`). The path is determined by `ExtensionsConfig.resolve_config_path()`.
  L18: 
  L19: ```json
  L20: {
  ... (truncated)
- `frontend/src/content/en/harness/memory.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L5: <Callout type="info" emoji="💾">
  L6: Memory lets DeerFlow carry useful information across sessions. The agent
  L7: remembers user preferences, project context, and recurring facts so it can
  L8: give better responses without starting from zero every time.
  L9: </Callout>
  L10: 
  L11: Memory is a runtime feature of the DeerFlow Harness. It is not a simple conversation log — it is a structured store of facts and context summaries that persist across separate sessions and inform the agent's behavior in future conversations.
  L12: 
  L13: ## What memory stores
  L14: 
  L15: The memory store holds several categories of information:
  L16: 
  L17: - **Work context**: summaries of ongoing projects, goals, and recurring topics the user works on.
  L18: - **Personal context**: preferences, communication style, and other user-specific details the agent has learned.
  L19: - **Top of mind**: the most recent focus areas and active tasks.
  L20: - **History**: recent months' context, earlier background, and long-term facts.
  L21: - **Facts**: discrete, specific facts the agent has extracted from conversations (e.g., preferred tools, team names, project constraints).
  L22: 
  ... (truncated)
- `frontend/src/content/en/harness/middlewares.mdx`
  L1: import { Callout } from "nextra/components";
  L2: 
  L3: # Middlewares
  L4: 
  L5: <Callout type="info" emoji="🔌">
  L6: Middlewares wrap every LLM turn in the Lead Agent. They are the primary
  L7: extension point for adding cross-cutting behaviors like memory, summarization,
  L8: clarification, and token tracking.
  L9: </Callout>
  L10: 
  L11: Every time the Lead Agent calls the LLM, it runs through a **middleware chain** before and after the model call. Middlewares can read and modify the agent's state, inject content into the system prompt, intercept tool calls, and react to model outputs.
  L12: 
  L13: This design keeps the agent core simple and stable while allowing rich, composable behaviors to be layered in.
  L14: 
  L15: ## How the chain works
  L16: 
  L17: The middleware chain is built once per agent invocation, based on the current configuration and request parameters. The middlewares run in a defined order:
  L18: 
  L19: 1. Runtime middlewares (error handling, thread data, uploads, dangling tool call patching)
  L20: 2. `SummarizationMiddleware` — context compression (if enabled)
  ... (truncated)
- `frontend/src/content/en/harness/sandbox.mdx`
  L1: import { Callout, Cards, Tabs } from "nextra/components";
  L2: 
  L5: <Callout type="info" emoji="📦">
  L6: The sandbox is the isolated workspace where the agent does file and
  L7: command-based work. It is what makes DeerFlow capable of real action, not
  L8: just conversation.
  L9: </Callout>
  L10: 
  L11: The sandbox gives the Lead Agent a controlled environment where it can read files, write outputs, run shell commands, and produce artifacts. Without a sandbox, the agent can only generate text. With a sandbox, it can write and execute code, process data files, generate charts, and build deliverables.
  L12: 
  L13: ## Sandbox modes
  L14: 
  L15: DeerFlow supports three sandbox modes. Choose the one that fits your deployment:
  L16: 
  L17: ### LocalSandbox (default)
  L18: 
  L19: Commands run directly on the host machine's filesystem. There is no container isolation.
  L20: 
  L21: - **Best for**: trusted, single-user local development workflows.
  L22: - **Risk**: the agent has access to the host filesystem. Use `allow_host_bash: false` (default) to prevent arbitrary command execution.
  ... (truncated)
- `frontend/src/content/en/harness/skills.mdx`
  L1: import { Callout, Cards, FileTree, Steps } from "nextra/components";
  L2: 
  L5: <Callout type="info" emoji="🎯">
  L6: Skills are task-oriented capability packages that teach the agent how to do a
  L7: specific class of work. The base agent stays general; skills provide
  L8: specialization only when needed.
  L9: </Callout>
  L10: 
  L11: A skill is more than a prompt. It is a self-contained capability package that can include structured instructions, step-by-step workflows, domain-specific best practices, supporting resources, and tool configurations. Skills are loaded on demand — they inject their content when a task calls for them and stay out of the context otherwise.
  L12: 
  L13: ## What a skill contains
  L14: 
  L15: Each skill lives in its own subdirectory under `skills/public/` (or `skills/custom/` for user-created skills). The directory contains a `SKILL.md` file that defines the skill's metadata, instructions, and workflow.
  L16: 
  L17: <FileTree>
  L18: <FileTree.Folder name="skills/" defaultOpen>
  L19: <FileTree.Folder name="public/" defaultOpen>
  L20: <FileTree.Folder name="deep-research/" defaultOpen>
  L21: <FileTree.File name="SKILL.md" />
  L22: </FileTree.Folder>
  ... (truncated)
- `frontend/src/content/en/harness/subagents.mdx`
  L1: import { Callout, Cards } from "nextra/components";
  L2: 
  L3: # Subagents
  L4: 
  L5: <Callout type="info" emoji="👥">
  L6: Subagents are focused workers that the Lead Agent delegates subtasks to. They
  L7: run with isolated context, keeping the main conversation clean while handling
  L8: parallel or specialized work.
  L9: </Callout>
  L10: 
  L11: When a task is too broad for a single reasoning thread, or when parts of it can be done in parallel, the Lead Agent delegates work to **subagents**. A subagent is a self-contained agent invocation that receives a specific task, executes it, and returns the result.
  L12: 
  L13: ## Why subagents matter
  L14: 
  L15: Subagents solve two key problems in long-horizon workflows:
  L16: 
  L17: 1. **Context isolation**: a subagent only sees the information it needs for its piece of the task, not the entire parent conversation. This keeps each agent's working context focused and tractable.
  L18: 2. **Parallelism**: multiple subagents can run concurrently, allowing independent parts of a task (e.g., researching multiple topics simultaneously) to be processed in parallel.
  L19: 
  L20: ## Built-in subagents
  ... (truncated)
- `frontend/src/content/en/harness/tools.mdx`
  L1: import { Callout, Cards, Tabs } from "nextra/components";
  L2: 
  L5: <Callout type="info" emoji="🔧">
  L6: Tools are the actions the Lead Agent can take. DeerFlow provides built-in
  L7: tools, community integrations, MCP tools, and skill tools — all controlled
  L8: through <code>config.yaml</code>.
  L9: </Callout>
  L10: 
  L11: The Lead Agent is a tool-calling agent. Tools are how it interacts with the world: searching the web, reading and writing files, running commands, delegating tasks, and presenting outputs to the user.
  L12: 
  L13: DeerFlow organizes tools into four categories:
  L14: 
  L15: 1. **Built-in tools** — core runtime capabilities always available to the agent
  L16: 2. **Community tools** — integrations with external search, fetch, and image services
  L17: 3. **MCP tools** — tools provided by external Model Context Protocol servers
  L18: 4. **Skill tools** — tools bundled with specific skill packs
  L19: 
  L20: ## Built-in tools
  L21: 
  L22: Built-in tools are part of the harness and do not require configuration to be available.
  ... (truncated)

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

- `frontend/src/components/workspace/messages/message-list-item.tsx`
  L82: // Revert on error — feedback state unchanged on catch
- `frontend/src/components/workspace/messages/message-list.tsx`
- `frontend/src/core/api/feedback.ts`
- `frontend/src/core/threads/hooks.ts`
  L686: /** Per-message enrichment data attached by the backend ``/history`` helper. */
  L689: /** ``undefined`` = not feedback-eligible; ``null`` = eligible but unrated. */
  L693: /**
  L694: * Fetch ``/history`` once and index feedback + run_id by message id.
  L695: *
  L696: * Replaces the old ``useThreadFeedback`` hook which keyed by AI-message
  L697: * ordinal position — an inherently fragile mapping that broke whenever
  L698: * ``ai_tool_call`` messages were interleaved with ``ai_message`` messages.
  L699: * Keying by ``message.id`` is stable regardless of run count, tool-call
  L700: * chains, or summarization.
  L701: *
  L702: * The ``/history`` response is refreshed on every stream completion via
  L703: * ``invalidateQueries(["thread-message-enrichment"])`` in ``onFinish``.
  L704: */
  L736: // Preserve presence: "feedback" key absent → ineligible; present with
  L737: // null → eligible but unrated; present with object → rated.

## 44d9953e 2026-04-12 JeffJiang
feat: Add metadata and descriptions to various documentation pages in Chinese

- Added titles and descriptions to workspace usage, configuration, customization, design principles, installation, integration guide, lead agent, MCP integration, memory system, middleware, quick start, sandbox, skills, subagents, and tools documentation.
- Removed outdated API/Gateway reference and concepts glossary pages.
- Updated configuration reference to reflect current structure and removed unnecessary sections.
- Introduced new model provider documentation for Ark and updated the index page for model providers.
- Enhanced tutorials with titles and descriptions for better clarity and navigation.

- `frontend/src/app/[lang]/docs/layout.tsx`
  L37: className="sticky max-w-full px-10"
  L44: footer={<Footer className="mt-0" />}
- `frontend/src/components/landing/footer.tsx`
- `frontend/src/content/en/_meta.ts`
- `frontend/src/content/en/application/agents-and-threads.mdx`
  L1: ---
  L2: title: Agents and Threads
  L3: description: DeerFlow App supports multiple named agents and maintains conversation state across sessions through threads and checkpointing.
  L4: ---
  L5: 
- `frontend/src/content/en/application/configuration.mdx`
  L1: ---
  L2: title: Configuration
  L3: description: DeerFlow App is configured through two files and a set of environment variables. This page covers the application-level configuration that most operators need to set up before deploying.
  L4: ---
  L5: 
- `frontend/src/content/en/application/deployment-guide.mdx`
  L1: ---
  L2: title: Deployment Guide
  L3: description: "This guide covers all supported deployment methods for DeerFlow App: local development, Docker Compose, and production with Kubernetes-managed sandboxes."
  L4: ---
  L5: 
  L24: | Service     | Port | Description              |
  L25: | ----------- | ---- | ------------------------ |
  L26: | LangGraph   | 2024 | DeerFlow Harness runtime |
  L27: | Gateway API | 8001 | FastAPI backend          |
  L28: | Frontend    | 3000 | Next.js UI               |
  L29: | nginx       | 2026 | Unified reverse proxy    |
  L32: 
  L40: 
  L51: 
  L55: 
  L115: | Sandbox                                | Use case                                   |
  L116: | -------------------------------------- | ------------------------------------------ |
  L117: | `LocalSandboxProvider`                 | Single-user, trusted local workflows       |
  L118: | `AioSandboxProvider` (Docker)          | Multi-user, moderate isolation requirement |
  L119: | `AioSandboxProvider` + K8s Provisioner | Production, strong isolation, multi-user   |
  ... (truncated)
- `frontend/src/content/en/application/index.mdx`
  L1: ---
  L2: title: DeerFlow App
  L3: description: DeerFlow App is the reference implementation of what a production DeerFlow experience looks like. It assembles the Harness runtime, a web-based conversation workspace, an API gateway, and a reverse proxy into a single deployable system.
  L4: ---
  L5: 
- `frontend/src/content/en/application/operations-and-troubleshooting.mdx`
  L1: ---
  L2: title: Operations and Troubleshooting
  L3: description: This page covers day-to-day operational tasks and solutions to common problems when running DeerFlow App.
  L4: ---
  L5: 
- `frontend/src/content/en/application/quick-start.mdx`
  L1: ---
  L2: title: Quick Start
  L3: description: This guide walks you through starting DeerFlow App on your local machine using the `make dev` workflow. All four services (LangGraph, Gateway, Frontend, nginx) start together and are accessible through a single URL.
  L4: ---
  L5: 
- `frontend/src/content/en/application/workspace-usage.mdx`
  L1: ---
  L2: title: Workspace Usage
  L3: description: The DeerFlow App workspace is a browser-based interface for having multi-turn conversations with the agent, tracking task progress, viewing artifacts, and managing files.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/configuration.mdx`
  L1: ---
  L2: title: Configuration
  L3: description: "DeerFlow's configuration system is designed around one goal: every meaningful behavior should be expressible in a config file, not hardcoded in the application. This makes deployments reproducible, auditable, and easy to customize per environment."
  L4: ---
  L5: 
- `frontend/src/content/en/harness/customization.mdx`
  L1: ---
  L2: title: Customization
  L3: description: DeerFlow's pluggable architecture means most parts of the system can be replaced or extended without forking the core. This page maps the extension points and explains how to use each one.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/design-principles.mdx`
  L1: ---
  L2: title: Design Principles
  L3: description: Understanding the design principles behind DeerFlow Harness helps you use it effectively, extend it confidently, and reason about how your agents will behave in production.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/index.mdx`
  L1: ---
  L2: title: Install DeerFlow Harness
  L3: description: The DeerFlow Harness is the Python SDK and runtime foundation for building your own Super Agent systems.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/integration-guide.mdx`
  L1: ---
  L2: title: Integration Guide
  L3: description: DeerFlow Harness is not only a standalone application. It is a Python library you can import and use inside your own backend, API server, automation system, or multi-agent orchestrator.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/lead-agent.mdx`
  L1: ---
  L2: title: Lead Agent
  L3: description: The Lead Agent is the central executor in a DeerFlow thread. Every conversation, task, and workflow flows through it. Understanding how it works helps you configure it effectively and extend it when needed.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/mcp.mdx`
  L1: ---
  L2: title: MCP Integration
  L3: description: The **Model Context Protocol (MCP)** is an open standard for connecting language models to external tools and data sources. DeerFlow's MCP integration allows you to extend the agent with any tool server that implements the MCP protocol — without modifying the harness itself.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/memory.mdx`
  L1: ---
  L2: title: Memory
  L3: description: Memory is a runtime feature of the DeerFlow Harness. It is not a simple conversation log — it is a structured store of facts and context summaries that persist across separate sessions and inform the agent's behavior in future conversations.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/middlewares.mdx`
  L1: ---
  L2: title: Middlewares
  L3: description: Every time the Lead Agent calls the LLM, it runs through a **middleware chain** before and after the model call. Middlewares can read and modify the agent's state, inject content into the system prompt, intercept tool calls, and react to model outputs.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/quick-start.mdx`
  L1: ---
  L2: title: Quick Start
  L3: description: Learn how to create and run a DeerFlow agent with create_deerflow_agent, from model setup to streaming responses.
  L4: ---
  L5: 
  L11: This guide shows you how to build and run a DeerFlow agent in Python with
  L12: <code>create_deerflow_agent</code>.
  L15: The fastest way to understand DeerFlow Harness is to create an agent directly in code. This quick start walks through model setup, agent creation, and streaming a response.
  L28: You will also need a chat model instance from the LangChain provider package you want to use.
  L30: ## Create your first agent
  L34: ### Import the factory and model
  L37: from deerflow.agents import create_deerflow_agent
  L38: from langchain_openai import ChatOpenAI
  L39: ```
  L41: ### Create a model
  L43: ```python
  L44: model = ChatOpenAI(
  L45: model="gpt-4o",
  L46: api_key="YOUR_OPENAI_API_KEY",
  L47: )
  ... (truncated)
- `frontend/src/content/en/harness/sandbox.mdx`
  L1: ---
  L2: title: Sandbox
  L3: description: The sandbox gives the Lead Agent a controlled environment where it can read files, write outputs, run shell commands, and produce artifacts. Without a sandbox, the agent can only generate text. With a sandbox, it can write and execute code, process data files, generate charts, and build deliverables.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/skills.mdx`
  L1: ---
  L2: title: Skills
  L3: description: A skill is more than a prompt. It is a self-contained capability package that can include structured instructions, step-by-step workflows, domain-specific best practices, supporting resources, and tool configurations. Skills are loaded on demand — they inject their content when a task calls for them and stay out of the context otherwise.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/subagents.mdx`
  L1: ---
  L2: title: Subagents
  L3: description: When a task is too broad for a single reasoning thread, or when parts of it can be done in parallel, the Lead Agent delegates work to **subagents**. A subagent is a self-contained agent invocation that receives a specific task, executes it, and returns the result.
  L4: ---
  L5: 
- `frontend/src/content/en/harness/tools.mdx`
  L1: ---
  L2: title: Tools
  L3: description: "The Lead Agent is a tool-calling agent. Tools are how it interacts with the world: searching the web, reading and writing files, running commands, delegating tasks, and presenting outputs to the user."
  L4: ---
  L5: 
- `frontend/src/content/en/introduction/core-concepts.mdx`
  L1: ---
  L2: title: Core Concepts
  L3: description: Before you go deeper into DeerFlow, it helps to anchor on a few concepts that appear throughout the system. These concepts explain what DeerFlow is optimizing for and why its architecture looks the way it does.
  L4: ---
  L5: 
- `frontend/src/content/en/introduction/harness-vs-app.mdx`
  L1: ---
  L2: title: Harness vs App
  L3: description: "DeerFlow has two layers that are closely related but serve different purposes."
  L4: ---
  L5: 
- `frontend/src/content/en/introduction/why-deerflow.mdx`
  L1: ---
  L2: title: Why DeerFlow
  L3: description: DeerFlow exists because modern agent systems need more than a chat loop. A useful agent must plan over long horizons, break work into sub-tasks, use tools, manipulate files, run code safely, and preserve enough context to stay coherent across a complex task. DeerFlow was built to provide that runtime foundation.
  L4: ---
  L5: 
- `frontend/src/content/en/reference/_meta.ts`
- `frontend/src/content/en/reference/model-providers/_meta.ts`
- `frontend/src/content/en/reference/model-providers/ark.mdx`
  L1: ---
  L2: title: Volcano Ark
  L3: description: Integration guide for the Volcano Ark model provider.
  L4: ---
  L5: 
  L6: # Volcano Ark
  L7: 
  L8: ## Coding Plan
- `frontend/src/content/en/reference/model-providers/index.mdx`
  L1: ---
  L2: title: Model providers
  L3: description: Integration references for supported model provider services.
  L4: asIndexPage: true
  L5: ---
  L6: 
  L7: # Model providers
- `frontend/src/content/en/tutorials/create-your-first-harness.mdx`
  L1: ---
  L2: title: Create Your First Harness
  L3: description: This tutorial shows you how to use the DeerFlow Harness programmatically — importing and using DeerFlow directly in your Python code rather than through the web interface.
  L4: ---
  L5: 
- `frontend/src/content/en/tutorials/deploy-your-own-deerflow.mdx`
  L1: ---
  L2: title: Deploy Your Own DeerFlow
  L3: description: This tutorial guides you through deploying DeerFlow to a production environment using Docker Compose for multi-user access.
  L4: ---
  L5: 
- `frontend/src/content/en/tutorials/first-conversation.mdx`
  L1: ---
  L2: title: First Conversation
  L3: description: This tutorial walks you through your first complete agent conversation in DeerFlow — from launching the app to getting meaningful work done with the agent.
  L4: ---
  L5: 
- `frontend/src/content/en/tutorials/use-tools-and-skills.mdx`
  L1: ---
  L2: title: Use Tools and Skills
  L3: description: This tutorial shows you how to configure and use tools and skills in DeerFlow to give the agent access to web search, file operations, and domain-specific capabilities.
  L4: ---
  L5: 
- `frontend/src/content/en/tutorials/work-with-memory.mdx`
  L1: ---
  L2: title: Work with Memory
  L3: description: This tutorial shows you how to enable and use DeerFlow's memory system so the agent remembers important information about you across multiple sessions.
  L4: ---
  L5: 
- `frontend/src/content/zh/_meta.ts`
- `frontend/src/content/zh/application/agents-and-threads.mdx`
  L1: ---
  L2: title: Agent 与线程
  L3: description: 了解 DeerFlow 中 Agent 与线程的关系，以及如何管理自定义 Agent 和对话线程。
  L4: ---
  L5: 
- `frontend/src/content/zh/application/configuration.mdx`
  L1: ---
  L2: title: 配置
  L3: description: 本页面涵盖 DeerFlow 应用的所有配置层——`config.yaml`、前端环境变量、`extensions_config.json` 和运行时环境变量。
  L4: ---
  L5: 
- `frontend/src/content/zh/application/deployment-guide.mdx`
  L1: ---
  L2: title: 部署指南
  L3: description: 本指南涵盖 DeerFlow 应用所有支持的部署方式：本地开发、Docker Compose 以及使用 Kubernetes 管理沙箱的生产环境。
  L4: ---
  L5: 
- `frontend/src/content/zh/application/index.mdx`
  L1: ---
  L2: title: DeerFlow 应用
  L3: description: DeerFlow 应用是 DeerFlow 生产体验的参考实现。它将 Harness 运行时、基于 Web 的对话工作区、API Gateway 和反向代理组合成一个可部署的完整系统。
  L4: ---
  L5: 
- `frontend/src/content/zh/application/operations-and-troubleshooting.mdx`
  L1: ---
  L2: title: 运维与排障
  L3: description: 本页面涵盖运行 DeerFlow 应用的操作信息：日志记录、常见问题和维护任务。
  L4: ---
  L5: 
- `frontend/src/content/zh/application/quick-start.mdx`
  L1: ---
  L2: title: 快速上手
  L3: description: 本指南引导你使用 `make dev` 工作流在本地机器上启动 DeerFlow 应用。所有四个服务（LangGraph、Gateway、前端、nginx）一起启动，通过单个 URL 访问。
  L4: ---
  L5: 
- `frontend/src/content/zh/application/workspace-usage.mdx`
  L1: ---
  L2: title: 工作区使用
  L3: description: DeerFlow 工作区是一个基于浏览器的对话界面，你可以在其中向 Agent 发送消息、上传文件、查看中间步骤，以及下载生成的产出物。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/configuration.mdx`
  L1: ---
  L2: title: 配置
  L3: description: DeerFlow 的配置系统围绕一个目标设计：每一个有意义的行为都应该可以在配置文件中表达，而不是硬编码在应用程序中。这使部署可重现、可审计，并且易于按环境定制。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/customization.mdx`
  L1: ---
  L2: title: 自定义与扩展
  L3: description: DeerFlow 的可插拔架构意味着系统的大多数部分都可以在不 fork 核心的情况下被替换或扩展。本页面列举了扩展点，并解释如何使用每一个。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/design-principles.mdx`
  L1: ---
  L2: title: 设计理念
  L3: description: 了解 DeerFlow Harness 背后的设计理念，有助于你有效地使用它、自信地扩展它，并推断 Agent 在生产环境中的行为方式。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/index.mdx`
  L1: ---
  L2: title: 安装 DeerFlow Harness
  L3: description: DeerFlow Harness 是构建自己 Super Agent 系统的 Python SDK 和运行时基础。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/integration-guide.mdx`
  L1: ---
  L2: title: 集成指南
  L3: description: DeerFlow Harness 不仅仅是一个独立应用程序——它是一个可以导入并在你自己的后端、API 服务器、自动化系统或多 Agent 协调器中使用的 Python 库。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/lead-agent.mdx`
  L1: ---
  L2: title: Lead Agent
  L3: description: Lead Agent 是 DeerFlow 线程中的核心执行者。每个对话、任务和工作流都通过它进行。理解它的工作方式有助于你有效地配置它，并在需要时扩展它。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/mcp.mdx`
  L1: ---
  L2: title: MCP 集成
  L3: description: Model Context Protocol（MCP） 是连接语言模型与外部工具和数据源的开放标准。DeerFlow 的 MCP 集成允许你用任何实现了 MCP 协议的工具服务器扩展 Agent——无需修改 Harness 本身。
  L4: ---
  L5: 
  L11: Model Context Protocol（MCP）让 DeerFlow
  L12: 能够连接任何外部工具服务器。连接后，MCP 工具与内置工具一样对 Lead Agent 可用。
  L46: 
  L91: 
- `frontend/src/content/zh/harness/memory.mdx`
  L1: ---
  L2: title: 记忆系统
  L3: description: 记忆是 DeerFlow Harness 的一个运行时功能。它不是简单的对话日志，而是跨多个独立会话持久化、在未来对话中影响 Agent 行为的结构化事实和上下文摘要存储。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/middlewares.mdx`
  L1: ---
  L2: title: 中间件
  L3: description: 每次 Lead Agent 调用 LLM 时，都会先后执行一条**中间件链**。中间件可以读取和修改 Agent 的状态、向系统提示注入内容、拦截工具调用，并对模型输出做出反应。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/quick-start.mdx`
  L1: ---
  L2: title: 快速上手
  L3: description: 学习如何使用 create_deerflow_agent 创建并运行 DeerFlow Agent，从模型初始化到流式响应。
  L4: ---
  L5: 
  L11: 本指南介绍如何在 Python 中通过 <code>create_deerflow_agent</code>
  L12: 创建并运行一个 DeerFlow Agent。
  L15: 理解 DeerFlow Harness 的最快方式，是直接在代码里创建一个 Agent。本快速上手指南将带你完成模型初始化、Agent 创建，以及响应流式输出。
  L28: 你还需要准备一个来自对应 LangChain Provider 包的聊天模型实例。
  L30: ## 创建第一个 Agent
  L34: ### 导入工厂函数与模型类
  L37: from deerflow.agents import create_deerflow_agent
  L38: from langchain_openai import ChatOpenAI
  L39: ```
  L41: ### 创建模型
  L43: ```python
  L44: model = ChatOpenAI(
  L45: model="gpt-4o",
  L46: api_key="YOUR_OPENAI_API_KEY",
  L47: )
  ... (truncated)
- `frontend/src/content/zh/harness/sandbox.mdx`
  L1: ---
  L2: title: 沙箱
  L3: description: 沙箱为 Lead Agent 提供一个受控环境，在其中可以读取文件、写入输出、运行 Shell 命令并生成产出物。没有沙箱，Agent 只能生成文本；有了沙箱，它可以编写和执行代码、处理数据文件、生成图表并构建交付物。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/skills.mdx`
  L1: ---
  L2: title: 技能
  L3: description: 技能不仅仅是提示词。它是一个自包含的能力包，可以包含结构化指令、分步工作流、领域最佳实践、支撑资源和工具配置。技能按需加载——在任务需要时注入内容，否则不影响上下文。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/subagents.mdx`
  L1: ---
  L2: title: 子 Agent
  L3: description: 当一个任务对单个推理线程来说太宽泛，或者部分任务可以并行完成时，Lead Agent 将工作委派给**子 Agent**。子 Agent 是一个独立的 Agent 调用，接收特定任务、执行并返回结果。
  L4: ---
  L5: 
- `frontend/src/content/zh/harness/tools.mdx`
  L1: ---
  L2: title: 工具
  L3: description: Lead Agent 是一个工具调用 Agent。工具是它与世界交互的方式：搜索网络、读写文件、运行命令、委派任务以及向用户呈现输出。
  L4: ---
  L5: 
- `frontend/src/content/zh/introduction/core-concepts.mdx`
  L1: ---
  L2: title: 核心概念
  L3: description: 在深入了解 DeerFlow 之前，先建立一些贯穿整个系统的核心概念。这些概念解释了 DeerFlow 的优化目标以及其架构设计的原因。
  L4: ---
  L5: 
- `frontend/src/content/zh/introduction/harness-vs-app.mdx`
  L1: ---
  L2: title: Harness 与应用
  L3: description: DeerFlow 有两个紧密相关但服务于不同目的的层次：.
  L4: ---
  L5: 
- `frontend/src/content/zh/introduction/why-deerflow.mdx`
  L1: ---
  L2: title: 为什么选择 DeerFlow
  L3: description: DeerFlow 的诞生是因为现代 Agent 系统需要的不仅仅是一个聊天循环。一个真正有用的 Agent 必须能够进行长时序规划、将任务拆解为子任务、使用工具、操作文件、安全地运行代码，并在复杂任务中保持足够的上下文连贯性。DeerFlow 正是为提供这样的运行时基础而构建的。
  L4: ---
  L5: 
- `frontend/src/content/zh/reference/_meta.ts`
- `frontend/src/content/zh/reference/model-providers/_meta.ts`
- `frontend/src/content/zh/reference/model-providers/ark.mdx`
  L1: ---
  L2: title: 火山方舟
  L3: description: 火山方舟模型接入指南。
  L4: ---
  L5: 
  L6: # 火山方舟
  L7: 
  L8: ## Coding Plan
- `frontend/src/content/zh/reference/model-providers/index.mdx`
  L1: ---
  L2: title: 模型厂商服务接入
  L3: description: 已支持模型厂商服务的接入参考文档。
  L4: asIndexPage: true
  L5: ---
  L6: 
  L7: # 更多模型厂商服务接入
- `frontend/src/content/zh/tutorials/create-your-first-harness.mdx`
  L1: ---
  L2: title: 创建你的第一个 Harness
  L3: description: 本教程介绍如何以编程方式使用 DeerFlow Harness Python SDK——直接在你的 Python 代码中导入和使用 DeerFlow，而不是通过 Web 界面。
  L4: ---
  L5: 
- `frontend/src/content/zh/tutorials/deploy-your-own-deerflow.mdx`
  L1: ---
  L2: title: 部署你的 DeerFlow
  L3: description: 本教程引导你将 DeerFlow 部署到生产环境，使用 Docker Compose 进行多用户访问。
  L4: ---
  L5: 
- `frontend/src/content/zh/tutorials/first-conversation.mdx`
  L1: ---
  L2: title: 第一次对话
  L3: description: 本教程引导你在 DeerFlow 中完成第一次完整的 Agent 对话，从启动应用到与 Agent 进行实质性任务交互。
  L4: ---
  L5: 
- `frontend/src/content/zh/tutorials/use-tools-and-skills.mdx`
  L1: ---
  L2: title: 使用工具和技能
  L3: description: 本教程介绍如何在 DeerFlow 中配置和使用工具（Tools）与技能（Skills），让 Agent 能够访问搜索、文件操作和特定领域能力。
  L4: ---
  L5: 
- `frontend/src/content/zh/tutorials/work-with-memory.mdx`
  L1: ---
  L2: title: 使用记忆系统
  L3: description: 本教程介绍如何在 DeerFlow 中启用和使用记忆系统，让 Agent 在多次会话中记住关于你的重要信息。
  L4: ---
  L5: 

## 00a90bbd 2026-04-12 foreleven
refactor: Remove init_token handling from admin initialization logic and related tests

- `frontend/src/app/(auth)/setup/page.tsx`
- `frontend/src/core/auth/types.ts`
- `frontend/src/core/threads/hooks.ts`

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

- `frontend/src/app/workspace/agents/[agent_name]/chats/[thread_id]/page.tsx`
- `frontend/src/app/workspace/chats/[thread_id]/page.tsx`
- `frontend/src/components/workspace/input-box.tsx`
- `frontend/src/components/workspace/messages/message-list.tsx`
- `frontend/src/components/workspace/settings/account-settings-page.tsx`
- `frontend/src/core/agents/api.ts`
- `frontend/src/core/api/feedback.ts`
- `frontend/src/core/api/fetcher.ts`
- `frontend/src/core/i18n/locales/en-US.ts`
- `frontend/src/core/i18n/locales/types.ts`
- `frontend/src/core/i18n/locales/zh-CN.ts`
- `frontend/src/core/mcp/api.ts`
- `frontend/src/core/memory/api.ts`
- `frontend/src/core/messages/utils.ts`
- `frontend/src/core/skills/api.ts`
- `frontend/src/core/threads/hooks.ts`
  L52: // The overlap is a contiguous suffix of historyMessages (newest history == oldest thread).
  L53: // Scan from the end: shrink cutoff while messages are already in thread, stop as soon as
  L54: // we hit one that isn't — everything before that point is non-overlapping.
  L499: // Cache the latest thread messages in a ref to compare against incoming history messages for deduplication,
  L500: // and to allow access to the full message list in onUpdateEvent without causing re-renders.
  L511: // Merge history, live stream, and optimistic messages for display
  L512: // History messages may overlap with thread.messages; thread.messages take precedence
- `frontend/src/core/threads/types.ts`
- `frontend/src/core/uploads/api.ts`

## 28381e13 2026-04-26 Willem Jiang
fix the lint errors in frontend

- `frontend/src/content/en/application/configuration.mdx`
  L14: | File                     | Purpose                                                                                 |
  L15: | ------------------------ | --------------------------------------------------------------------------------------- |
  L16: | `config.yaml`            | Backend configuration: models, sandbox, tools, skills, memory, and all Harness settings |
  L17: | `extensions_config.json` | MCP servers and skill enable/disable state (managed by the App UI and Gateway API)      |
  L147: 
  L165: - use: deerflow.community.ddg_search.tools:web_search_tool # default, no key required
  L192: connection_string: checkpoints.db # stored in backend/.deer-flow/
  L228: | Variable              | Required                   | Description                                                      |
  L229: | --------------------- | -------------------------- | ---------------------------------------------------------------- |
  L230: | `BETTER_AUTH_SECRET`  | **Required** in production | Secret for session signing. Use `openssl rand -base64 32`.       |
  L231: | `BETTER_AUTH_URL`     | Recommended                | Public-facing base URL (e.g., `https://your-domain.com`)         |
  L232: | `SKIP_ENV_VALIDATION` | Optional                   | Set to `1` to skip env validation during build (not recommended) |
  L233: | `NEXT_PUBLIC_API_URL` | Optional                   | Override the API base URL for the frontend                       |
  L272: <Cards.Card
  L273: title="Deployment Guide"
  L274: href="/docs/application/deployment-guide"
  L275: />
  L276: <Cards.Card
  L277: title="Harness Configuration"
  L278: href="/docs/harness/configuration"
  ... (truncated)
- `frontend/src/content/en/application/deployment-guide.mdx`
  L2: title: Deployment Guide
- `frontend/src/content/en/application/index.mdx`
  L20: | Capability              | Description                                                                                          |
  L21: | ----------------------- | ---------------------------------------------------------------------------------------------------- |
  L22: | **Web workspace**       | Browser-based conversation UI with support for threads, artifacts, file uploads, and skill selection |
  L23: | **Custom agents**       | Create and manage named agents with different models, skills, and tool sets                          |
  L24: | **Thread management**   | Persistent conversation threads with checkpointing and history                                       |
  L25: | **Streaming responses** | Real-time token streaming with thinking steps and tool call visibility                               |
  L26: | **Artifact viewer**     | In-browser preview and download of files and outputs produced by the agent                           |
  L27: | **Extensions UI**       | Enable/disable MCP servers and skills without editing config files                                   |
  L28: | **Gateway API**         | FastAPI-based REST API that bridges the frontend and the LangGraph runtime                           |
  L61: | Layer             | Technology                                                           |
  L62: | ----------------- | -------------------------------------------------------------------- |
  L63: | Frontend          | Next.js 16, React 19, TypeScript, pnpm                               |
  L64: | Gateway           | FastAPI, Python 3.12, uvicorn                                        |
  L65: | Agent runtime     | LangGraph, LangChain, DeerFlow Harness                               |
  L66: | Reverse proxy     | nginx                                                                |
  L71: <Cards.Card
  L72: title="Deployment Guide"
  L73: href="/docs/application/deployment-guide"
  L74: />
- `frontend/src/content/en/application/operations-and-troubleshooting.mdx`
  L16: | File                 | Service                              |
  L17: | -------------------- | ------------------------------------ |
  L19: | `logs/gateway.log`   | FastAPI Gateway API                  |
  L20: | `logs/frontend.log`  | Next.js frontend dev server          |
  L21: | `logs/nginx.log`     | nginx reverse proxy                  |
  L33: log_level: debug # debug | info | warning | error
  L174: <Cards.Card
  L175: title="Deployment Guide"
  L176: href="/docs/application/deployment-guide"
  L177: />
- `frontend/src/content/en/application/quick-start.mdx`
  L27: | Tool    | Minimum version    |
  L28: | ------- | ------------------ |
  L29: | Python  | 3.12               |
  L30: | uv      | latest             |
  L31: | Node.js | 22                 |
  L32: | pnpm    | 10                 |
  L33: | nginx   | any recent version |
  L90: 
  L114: | Service   | Log file             |
  L115: | --------- | -------------------- |
  L117: | Gateway   | `logs/gateway.log`   |
  L118: | Frontend  | `logs/frontend.log`  |
  L119: | nginx     | `logs/nginx.log`     |
  L128: <Cards.Card
  L129: title="Deployment Guide"
  L130: href="/docs/application/deployment-guide"
  L131: />
- `frontend/src/content/en/application/workspace-usage.mdx`
  L77: <Cards.Card
  L78: title="Agents and Threads"
  L79: href="/docs/application/agents-and-threads"
  L80: />
- `frontend/src/content/en/harness/configuration.mdx`
  L84: some_provider_specific_option: value # passed through to ChatOpenAI constructor
  L107: | Section           | Description                                      | Documentation                                            |
  L108: | ----------------- | ------------------------------------------------ | -------------------------------------------------------- |
  L109: | `log_level`       | Logging level (`debug`/`info`/`warning`/`error`) | —                                                        |
  L110: | `models`          | Available LLM models                             | [Lead Agent](/docs/harness/lead-agent)                   |
  L111: | `token_usage`     | Token tracking per model call                    | [Middlewares](/docs/harness/middlewares)                 |
  L112: | `tools`           | Available agent tools                            | [Tools](/docs/harness/tools)                             |
  L113: | `tool_groups`     | Named groups of tools                            | [Tools](/docs/harness/tools)                             |
  L114: | `tool_search`     | Deferred/on-demand tool loading                  | [Tools](/docs/harness/tools)                             |
  L115: | `sandbox`         | Sandbox provider and options                     | [Sandbox](/docs/harness/sandbox)                         |
  L116: | `skills`          | Skills directory and container path              | [Skills](/docs/harness/skills)                           |
  L117: | `skill_evolution` | Agent-managed skill creation                     | [Skills](/docs/harness/skills)                           |
  L118: | `subagents`       | Subagent timeouts and max turns                  | [Subagents](/docs/harness/subagents)                     |
  L119: | `acp_agents`      | External ACP agent integrations                  | [Subagents](/docs/harness/subagents)                     |
  L120: | `memory`          | Cross-session memory storage                     | [Memory](/docs/harness/memory)                           |
  L121: | `summarization`   | Conversation summarization                       | [Middlewares](/docs/harness/middlewares)                 |
  L122: | `title`           | Automatic thread title generation                | [Middlewares](/docs/harness/middlewares)                 |
  L123: | `checkpointer`    | Thread state persistence                         | [Agents & Threads](/docs/application/agents-and-threads) |
  L124: | `guardrails`      | Tool call authorization                          | —                                                        |
  L125: | `stream_bridge`   | Streaming configuration                          | —                                                        |
  ... (truncated)
- `frontend/src/content/en/harness/customization.mdx`
  L173: <Cards.Card
  L174: title="Integration Guide"
  L175: href="/docs/harness/integration-guide"
  L176: />
- `frontend/src/content/en/harness/design-principles.mdx`
  L113: | Principle                   | What it means in practice                                      |
  L114: | --------------------------- | -------------------------------------------------------------- |
  L115: | Harness, not framework      | Ready-to-run runtime with all the infrastructure already wired |
  L116: | Long-horizon first          | Architecture assumes multi-step, multi-tool, multi-turn tasks  |
  L117: | Middleware over inheritance | Behavior is composed from small, isolated plugins              |
  L118: | Skills for specialization   | Domain capability injected on demand, keeping the base clean   |
  L119: | Sandbox for execution       | Isolated workspace for real file and command work              |
  L120: | Context engineering         | Active management of what the agent sees to stay effective     |
  L121: | Config-driven               | All key behaviors are controlled through `config.yaml`         |
- `frontend/src/content/en/harness/lead-agent.mdx`
  L144: When a custom agent is selected in a thread, the Lead Agent loads that agent's
  L145: config at runtime. Switching models or skills for a specific agent does not
  L146: require restarting the server.
- `frontend/src/content/en/harness/mcp.mdx`
  L47: 
  L96: 
- `frontend/src/content/en/harness/middlewares.mdx`
  L92: model_name: null # use default model
  L162: - type: tokens # trigger when context exceeds N tokens
  L172: value: 10 # keep the 10 most recent messages
  L185: 
  L193: 
- `frontend/src/content/en/harness/quick-start.mdx`
  L88: | Parameter          | Description                                     |
  L89: | ------------------ | ----------------------------------------------- |
  L90: | `tools`            | Additional tools available to the agent         |
  L91: | `system_prompt`    | Custom system prompt                            |
  L92: | `features`         | Enable or replace built-in runtime features     |
  L94: | `plan_mode`        | Enable Todo-style task tracking                 |
  L95: | `checkpointer`     | Persist agent state across runs                 |
  L96: | `name`             | Logical agent name                              |
  L112: <Cards.Card
  L113: title="Design Principles"
  L114: href="/docs/harness/design-principles"
  L115: />
- `frontend/src/content/en/harness/sandbox.mdx`
  L12: command-based work. It is what makes DeerFlow capable of real action, not just
  L13: conversation.
  L32: allow_host_bash: false # default; set to true only for fully trusted workflows
  L86: | Host path                                   | Container path                               | Access     |
  L87: | ------------------------------------------- | -------------------------------------------- | ---------- |
  L88: | `skills/` (from `skills.path`)              | `/mnt/skills` (from `skills.container_path`) | Read-only  |
  L89: | `.deer-flow/threads/{thread_id}/user-data/` | `/mnt/user-data/`                            | Read-write |
  L139: allow_host_bash: true # Dangerous: grants the agent shell access to your machine
- `frontend/src/content/en/harness/skills.mdx`
  L47: | Skill                          | Description                                                                      |
  L48: | ------------------------------ | -------------------------------------------------------------------------------- |
  L49: | `deep-research`                | Multi-step research with source gathering, cross-checking, and structured output |
  L50: | `data-analysis`                | Data exploration, statistical analysis, and insight generation                   |
  L51: | `chart-visualization`          | Chart and graph creation from data                                               |
  L52: | `ppt-generation`               | Presentation slide generation                                                    |
  L53: | `image-generation`             | AI image generation workflows                                                    |
  L54: | `code-documentation`           | Automated code documentation generation                                          |
  L55: | `newsletter-generation`        | Newsletter content creation                                                      |
  L56: | `podcast-generation`           | Podcast script and outline generation                                            |
  L57: | `academic-paper-review`        | Structured academic paper analysis                                               |
  L58: | `consulting-analysis`          | Business consulting frameworks and analysis                                      |
  L59: | `systematic-literature-review` | Literature review methodology and synthesis                                      |
  L60: | `github-deep-research`         | Repository and code deep-dive research                                           |
  L61: | `frontend-design`              | Frontend design and UI workflow                                                  |
  L62: | `web-design-guidelines`        | Web design standards and review                                                  |
  L63: | `video-generation`             | Video content planning and generation                                            |
  L142: enabled: false # Set to true to allow agent-managed skill creation
  L143: moderation_model_name: null # Model for security scanning (null = use default)
- `frontend/src/content/en/harness/subagents.mdx`
  L78: timeout_seconds: 1800 # 30 minutes for complex tasks
  L81: timeout_seconds: 300 # 5 minutes for quick commands
  L125: `codex` commands) are not ACP-compatible by default — use the adapter packages
  L126: listed above or a compatible ACP wrapper.
- `frontend/src/content/en/harness/tools.mdx`
  L81: | Tool          | Description                                                                       |
  L82: | ------------- | --------------------------------------------------------------------------------- |
  L83: | `ls`          | List files in a directory                                                         |
  L84: | `read_file`   | Read file contents                                                                |
  L85: | `glob`        | Find files matching a pattern                                                     |
  L86: | `grep`        | Search file contents                                                              |
  L87: | `write_file`  | Write content to a file                                                           |
  L88: | `str_replace` | Replace a string in a file                                                        |
  L89: | `bash`        | Execute a shell command (requires `allow_host_bash: true` or a container sandbox) |
  L101: - use: deerflow.sandbox.tools:bash_tool # requires host bash or container sandbox
  L127: 
  L138: 
  L157: 
  L165: ```yaml tools: - use: deerflow.community.jina_ai.tools:web_fetch_tool
  L166: api_key: $JINA_API_KEY # optional; anonymous usage has rate limits ```
  L167: Converts web pages to clean Markdown. Works without an API key at reduced
  L168: rate limits.
  L171: ```yaml tools: - use: deerflow.community.exa.tools:web_fetch_tool api_key:
  L172: $EXA_API_KEY ```
  L175: ```yaml tools: - use: deerflow.community.infoquest.tools:web_fetch_tool
  ... (truncated)
- `frontend/src/content/en/tutorials/first-conversation.mdx`
  L38: 
  L46: 
  L56: 
- `frontend/src/content/en/tutorials/use-tools-and-skills.mdx`
  L36: 
- `frontend/src/content/en/tutorials/work-with-memory.mdx`
  L35: 
  L43: 
- `frontend/src/content/zh/application/agents-and-threads.mdx`
  L11: Agent
  L12: 是配置单元——它们定义了一组能力。线程是对话实例，带有持久化状态和历史记录。
  L119: <Cards.Card
  L120: title="运维与排障"
  L121: href="/docs/application/operations-and-troubleshooting"
  L122: />
- `frontend/src/content/zh/application/configuration.mdx`
  L49: - name: claude-extended-thinking
  L50: use: langchain_anthropic:ChatAnthropic
  L51: model: claude-sonnet-4-5
  L52: api_key: $ANTHROPIC_API_KEY
  L53: max_tokens: 16000
  L54: thinking_enabled: true
  L55: extra_body:
  L56: thinking:
  L57: type: enabled
  L58: budget_tokens: 10000
  L60: 
  L107: 
  L167: | 变量                  | 必需       | 描述                                               |
  L168: | --------------------- | ---------- | -------------------------------------------------- |
  L169: | `BETTER_AUTH_SECRET`  | 是（生产） | 会话管理的密钥（最少 32 个字符）                   |
  L170: | `BETTER_AUTH_URL`     | 推荐       | 你的应用公开 URL（例如 `https://your-domain.com`） |
  L171: | `SKIP_ENV_VALIDATION` | 否         | 设为 `1` 跳过构建时环境变量验证                    |
  L181: 不要在生产中使用 <code>SKIP_ENV_VALIDATION=1</code>。为{" "}
  L182: <code>BETTER_AUTH_SECRET</code> 设置一个真实值。
  L213: | 变量                    | 默认值           | 描述                                             |
  ... (truncated)
- `frontend/src/content/zh/application/deployment-guide.mdx`
  L24: | 服务        | 端口 | 描述                    |
  L25: | ----------- | ---- | ----------------------- |
  L26: | LangGraph   | 2024 | DeerFlow Harness 运行时 |
  L27: | Gateway API | 8001 | FastAPI 后端            |
  L28: | 前端        | 3000 | Next.js 界面            |
  L29: | nginx       | 2026 | 统一反向代理            |
  L32: 
  L40: 
  L51: 
  L55: 
  L93: 在部署前始终将 <code>BETTER_AUTH_SECRET</code>{" "}
  L94: 设置为强随机字符串。没有它，前端构建会使用一个公开已知的默认值。
  L112: | 沙箱                                   | 使用场景                   |
  L113: | -------------------------------------- | -------------------------- |
  L114: | `LocalSandboxProvider`                 | 单用户、受信任的本地工作流 |
  L115: | `AioSandboxProvider`（Docker）         | 多用户、中等隔离需求       |
  L116: | `AioSandboxProvider` + K8s Provisioner | 生产环境、强隔离、多用户   |
  L161: | 变量                 | 默认值           | 描述                          |
  L162: | -------------------- | ---------------- | ----------------------------- |
  L163: | `LANGGRAPH_UPSTREAM` | `langgraph:2024` | LangGraph 服务地址            |
  ... (truncated)
- `frontend/src/content/zh/application/index.mdx`
  L11: DeerFlow 应用是构建在 DeerFlow Harness 之上的完整 Super Agent
  L12: 应用。它将运行时能力打包成一个可部署的产品，包含 Web 界面、API Gateway
  L13: 和运维工具。
  L20: | 能力             | 描述                                                  |
  L21: | ---------------- | ----------------------------------------------------- |
  L22: | **Web 工作区**   | 浏览器对话界面，支持线程、产出物、文件上传和技能选择  |
  L23: | **自定义 Agent** | 创建和管理具有不同模型、技能和工具集的命名 Agent      |
  L24: | **线程管理**     | 带检查点和历史记录的持久化对话线程                    |
  L25: | **流式响应**     | 实时 token 流式传输，带思考步骤和工具调用可见性       |
  L26: | **产出物查看器** | Agent 生成文件和输出的浏览器内预览和下载              |
  L27: | **扩展界面**     | 无需编辑配置文件即可启用/禁用 MCP 服务器和技能        |
  L28: | **Gateway API**  | 桥接前端和 LangGraph 运行时的基于 FastAPI 的 REST API |
  L61: | 层次         | 技术                                                    |
  L62: | ------------ | ------------------------------------------------------- |
  L63: | 前端         | Next.js 16、React 19、TypeScript、pnpm                  |
  L64: | Gateway      | FastAPI、Python 3.12、uvicorn                           |
  L65: | Agent 运行时 | LangGraph、LangChain、DeerFlow Harness                  |
  L66: | 反向代理     | nginx                                                   |
  L67: | 状态持久化   | LangGraph Server（默认）+ 可选 SQLite/PostgreSQL 检查点 |
- `frontend/src/content/zh/application/operations-and-troubleshooting.mdx`
  L16: | 文件                 | 内容                                   |
  L17: | -------------------- | -------------------------------------- |
  L19: | `logs/gateway.log`   | API 请求/响应、Gateway 错误            |
  L20: | `logs/frontend.log`  | Next.js 服务器日志                     |
  L21: | `logs/nginx.log`     | 代理访问和错误日志                     |
  L34: log_level: debug # debug | info | warning | error
  L69: 
  L76: 
  L88: 
  L95: 
  L107: 
  L124: 
  L131: 
  L143: 
  L151: 
- `frontend/src/content/zh/application/quick-start.mdx`
  L11: 大约 10 分钟即可在本地运行 DeerFlow 应用。你需要一台安装了 Python
  L12: 3.12+、Node.js 22+ 的机器，以及至少一个 LLM API Key。
  L27: | 工具    | 最低版本     |
  L28: | ------- | ------------ |
  L29: | Python  | 3.12         |
  L30: | uv      | 最新版       |
  L31: | Node.js | 22           |
  L32: | pnpm    | 10           |
  L33: | nginx   | 任何近期版本 |
  L90: 
  L114: | 服务      | 日志文件             |
  L115: | --------- | -------------------- |
  L117: | Gateway   | `logs/gateway.log`   |
  L118: | 前端      | `logs/frontend.log`  |
  L119: | nginx     | `logs/nginx.log`     |
  L122: 如果有问题，先检查日志文件。大多数启动错误（缺失 API
  L123: Key、配置解析失败）会出现在 <code>logs/langgraph.log</code> 或{" "}
  L124: <code>logs/gateway.log</code> 中。
- `frontend/src/content/zh/application/workspace-usage.mdx`
  L11: DeerFlow 工作区是你与 Agent
  L12: 交互的地方。本页面涵盖主要用户界面工作流——创建对话、上传文件、查看产出物和使用技能。
  L45: 
  L52: 上传大文件时，告诉 Agent
  L53: 文件的具体内容，以便获得更好的结果（例如"分析这个包含季度销售数据的 CSV"）。
  L78: 
  L94: <Cards.Card
  L95: title="Agent 与线程"
  L96: href="/docs/application/agents-and-threads"
  L97: />
  L98: <Cards.Card
  L99: title="运维与排障"
  L100: href="/docs/application/operations-and-troubleshooting"
  L101: />
- `frontend/src/content/zh/harness/configuration.mdx`
  L11: 所有 DeerFlow Harness 行为都由 <code>config.yaml</code>{" "}
  L12: 驱动。一个文件控制哪些模型可用、沙箱如何运行、加载哪些工具，以及每个子系统的行为。
  L83: some_provider_specific_option: value # 传递给 ChatOpenAI 构造函数
  L106: | 章节              | 描述                                         | 文档                                                 |
  L107: | ----------------- | -------------------------------------------- | ---------------------------------------------------- |
  L108: | `log_level`       | 日志级别（`debug`/`info`/`warning`/`error`） | —                                                    |
  L109: | `models`          | 可用的 LLM 模型                              | [Lead Agent](/docs/harness/lead-agent)               |
  L110: | `token_usage`     | 每次模型调用的 token 追踪                    | [中间件](/docs/harness/middlewares)                  |
  L111: | `tools`           | 可用的 Agent 工具                            | [工具](/docs/harness/tools)                          |
  L112: | `tool_groups`     | 工具的命名分组                               | [工具](/docs/harness/tools)                          |
  L113: | `tool_search`     | 延迟/按需工具加载                            | [工具](/docs/harness/tools)                          |
  L114: | `sandbox`         | 沙箱提供者和选项                             | [沙箱](/docs/harness/sandbox)                        |
  L115: | `skills`          | 技能目录和容器路径                           | [技能](/docs/harness/skills)                         |
  L116: | `skill_evolution` | Agent 管理的技能创建                         | [技能](/docs/harness/skills)                         |
  L117: | `subagents`       | 子 Agent 超时和最大轮次                      | [子 Agent](/docs/harness/subagents)                  |
  L118: | `acp_agents`      | 外部 ACP Agent 集成                          | [子 Agent](/docs/harness/subagents)                  |
  L119: | `memory`          | 跨会话记忆存储                               | [记忆系统](/docs/harness/memory)                     |
  L120: | `summarization`   | 对话摘要压缩                                 | [中间件](/docs/harness/middlewares)                  |
  L121: | `title`           | 自动生成线程标题                             | [中间件](/docs/harness/middlewares)                  |
  L122: | `checkpointer`    | 线程状态持久化                               | [Agent 与线程](/docs/application/agents-and-threads) |
  ... (truncated)
- `frontend/src/content/zh/harness/customization.mdx`
  L11: DeerFlow
  L12: 设计为可适配的。你可以通过编写自定义中间件、添加新工具、构建技能包以及通过
  L13: config.yaml 的 <code>use:</code> 字段替换任何内置组件来扩展 Agent 行为。
- `frontend/src/content/zh/harness/design-principles.mdx`
  L11: DeerFlow 围绕一个核心思想构建：Agent
  L12: 行为应该由小型、可观察、可替换的组件组合而成——而不是硬编码到固定的工作流图中。
  L105: | 设计原则               | 实践含义                                 |
  L106: | ---------------------- | ---------------------------------------- |
  L108: | 长时序优先             | 架构假设多步骤、多工具、多轮次任务       |
  L109: | 中间件优于继承         | 行为由小型、隔离的插件组合而成           |
  L110: | 技能提供专业化         | 领域能力按需注入，保持基础干净           |
  L111: | 沙箱用于执行           | 真实文件和命令操作的隔离工作区           |
  L112: | 上下文工程             | 主动管理 Agent 所见内容以保持有效性      |
  L113: | 配置驱动               | 所有关键行为通过 `config.yaml` 控制      |
- `frontend/src/content/zh/harness/index.mdx`
  L11: DeerFlow Harness Python 包将以 <code>deerflow</code>{" "}
  L12: 名称发布。目前尚未正式发布，安装方式<strong>即将推出</strong>。
- `frontend/src/content/zh/harness/integration-guide.mdx`
  L11: DeerFlow Harness 可以嵌入任何 Python 应用程序。本指南涵盖在你自己的系统中将
  L12: DeerFlow 作为库使用的集成模式。
- `frontend/src/content/zh/harness/lead-agent.mdx`
  L11: Lead Agent 是每个 DeerFlow
  L12: 线程中的主要推理和编排单元。它决定要做什么、调用工具、委派子
  L13: Agent，并返回产出物。
  L127: 当在线程中选择自定义 Agent 时，Lead Agent 在运行时加载该 Agent 的配置。为特定
  L128: Agent 切换模型或技能不需要重启服务器。
- `frontend/src/content/zh/harness/memory.mdx`
  L11: 记忆让 DeerFlow 在多个会话中保留有用信息。Agent
  L12: 记住用户偏好、项目背景和反复出现的事实，这样它可以在不每次从零开始的情况下给出更好的响应。
- `frontend/src/content/zh/harness/middlewares.mdx`
  L11: 中间件包裹 Lead Agent 中的每次 LLM
  L12: 调用。它们是添加跨领域行为（如记忆、摘要压缩、澄清和 token
  L13: 追踪）的主要扩展点。
  L92: model_name: null # 使用默认模型
  L154: - type: tokens # 当上下文超过 N 个 token 时触发
  L164: value: 10 # 保留最近 10 条消息
  L177: 
  L183: 
- `frontend/src/content/zh/harness/quick-start.mdx`
  L88: | 参数               | 说明                       |
  L89: | ------------------ | -------------------------- |
  L90: | `tools`            | 提供给 Agent 的额外工具    |
  L91: | `system_prompt`    | 自定义系统提示词           |
  L92: | `features`         | 启用或替换内置运行时能力   |
  L94: | `plan_mode`        | 启用 Todo 风格的任务跟踪   |
  L95: | `checkpointer`     | 为多轮运行持久化状态       |
  L96: | `name`             | Agent 的逻辑名称           |
- `frontend/src/content/zh/harness/sandbox.mdx`
  L11: 沙箱是 Agent 进行文件和命令操作的隔离工作区。它让 DeerFlow
  L12: 能够采取真实行动，而不仅仅是对话。
  L31: allow_host_bash: false # 默认；仅对完全受信任的工作流设置为 true
  L76: | 主机路径                                    | 容器路径                                      | 访问权限 |
  L77: | ------------------------------------------- | --------------------------------------------- | -------- |
  L78: | `skills/`（来自 `skills.path`）             | `/mnt/skills`（来自 `skills.container_path`） | 只读     |
  L79: | `.deer-flow/threads/{thread_id}/user-data/` | `/mnt/user-data/`                             | 读写     |
  L98: <code>/mnt/skills</code>、<code>/mnt/acp-workspace</code> 或{" "}
  L99: <code>/mnt/user-data</code>。
  L130: allow_host_bash: true # 危险：授予 Agent 对你机器的 Shell 访问权限
- `frontend/src/content/zh/harness/skills.mdx`
  L11: 技能是面向任务的能力包，教会 Agent 如何完成特定类型的工作。基础 Agent
  L12: 保持通用；技能在需要时提供专业化。
  L43: | 技能                           | 描述                                         |
  L44: | ------------------------------ | -------------------------------------------- |
  L45: | `deep-research`                | 带来源收集、交叉验证和结构化输出的多步骤研究 |
  L46: | `data-analysis`                | 数据探索、统计分析和洞察生成                 |
  L47: | `chart-visualization`          | 从数据创建图表和可视化                       |
  L48: | `ppt-generation`               | 演示文稿幻灯片生成                           |
  L49: | `image-generation`             | AI 图像生成工作流                            |
  L50: | `code-documentation`           | 自动化代码文档生成                           |
  L51: | `newsletter-generation`        | 新闻简报内容创作                             |
  L52: | `podcast-generation`           | 播客脚本和大纲生成                           |
  L53: | `academic-paper-review`        | 结构化学术论文分析                           |
  L54: | `consulting-analysis`          | 商业咨询框架和分析                           |
  L55: | `systematic-literature-review` | 文献综述方法论和综合                         |
  L56: | `github-deep-research`         | 仓库和代码深度研究                           |
  L57: | `frontend-design`              | 前端设计和 UI 工作流                         |
  L58: | `web-design-guidelines`        | 网页设计标准和审查                           |
  L59: | `video-generation`             | 视频内容规划和生成                           |
  L136: enabled: false # 设为 true 允许 Agent 管理技能创建
  ... (truncated)
- `frontend/src/content/zh/harness/subagents.mdx`
  L11: 子 Agent 是 Lead Agent
  L12: 委派子任务的专注执行者。它们以隔离的上下文运行，在处理并行或专业工作的同时保持主对话清晰。
  L77: timeout_seconds: 1800 # 复杂任务 30 分钟
  L80: timeout_seconds: 300 # 快速命令 5 分钟
  L119: ACP Agent 作为 DeerFlow 管理的子进程运行，通过 ACP 协议通信。标准 CLI
  L120: 工具（如原始的 `claude` 或 `codex` 命令）默认不兼容
  L121: ACP——请使用上面列出的适配器包或兼容的 ACP 封装器。
- `frontend/src/content/zh/harness/tools.mdx`
  L11: 工具是 Lead Agent 可以采取的行动。DeerFlow 提供内置工具、社区集成、MCP
  L12: 工具和技能工具——全部通过 <code>config.yaml</code> 控制。
  L78: | 工具          | 描述                                                       |
  L79: | ------------- | ---------------------------------------------------------- |
  L80: | `ls`          | 列出目录中的文件                                           |
  L81: | `read_file`   | 读取文件内容                                               |
  L82: | `glob`        | 查找匹配模式的文件                                         |
  L83: | `grep`        | 搜索文件内容                                               |
  L84: | `write_file`  | 向文件写入内容                                             |
  L85: | `str_replace` | 替换文件中的字符串                                         |
  L86: | `bash`        | 执行 Shell 命令（需要 `allow_host_bash: true` 或容器沙箱） |
  L124: 
  L135: 
  L151: ```yaml tools: - use: deerflow.community.jina_ai.tools:web_fetch_tool
  L152: api_key: $JINA_API_KEY # 可选；匿名使用有速率限制 ``` 将网页转换为干净的
  L153: Markdown。无 API Key 也可使用，但有更严格的速率限制。
  L156: ```yaml tools: - use: deerflow.community.exa.tools:web_fetch_tool api_key:
  L157: $EXA_API_KEY ```
- `frontend/src/content/zh/index.mdx`
- `frontend/src/content/zh/introduction/core-concepts.mdx`
  L11: 如果你将 DeerFlow 理解为一个长时序 Agent
  L12: 的运行时，而不仅仅是聊天界面或工作流图，它将最易于理解。
- `frontend/src/content/zh/introduction/harness-vs-app.mdx`
  L11: DeerFlow 应用是构建在 DeerFlow Harness 之上的最佳实践 Super Agent 应用，而
  L12: DeerFlow Harness 是构建自己 Agent 系统的 Python SDK 和运行时基础。
- `frontend/src/content/zh/introduction/why-deerflow.mdx`
  L11: DeerFlow 起源于深度研究，但逐渐演化为一个通用的长时序 Agent
  L12: 运行时——支持技能、记忆、工具和协作调度。
- `frontend/src/content/zh/tutorials/first-conversation.mdx`
  L34: 
  L42: 
- `frontend/src/content/zh/tutorials/work-with-memory.mdx`
  L33: 
  L41: 

## 9eca429a 2026-04-26 Willem Jiang
fix the lint errors in the frontend

- `frontend/src/app/workspace/agents/new/page.tsx`
- `frontend/src/core/threads/hooks.ts`

## 3f88045b 2026-04-26 Willem Jiang
try to fix the frontend e2e test errors

- `frontend/src/app/workspace/agents/new/page.tsx`
- `frontend/src/content/en/harness/tools.mdx`
  L165: ```yaml
  L166: tools:
  L167: - use: deerflow.community.jina_ai.tools:web_fetch_tool
  L168: api_key: $JINA_API_KEY # optional; anonymous usage has rate limits
  L169: ```
  L170: Converts web pages to clean Markdown. Works without an API key at reduced rate
  L171: limits.
  L174: ```yaml
  L175: tools:
  L176: - use: deerflow.community.exa.tools:web_fetch_tool
  L177: api_key: $EXA_API_KEY
  L178: ```
  L181: ```yaml
  L182: tools:
  L183: - use: deerflow.community.infoquest.tools:web_fetch_tool
  L184: api_key: $INFOQUEST_API_KEY
  L185: ```
  L188: ```yaml
  L189: tools:
  L190: - use: deerflow.community.firecrawl.tools:web_fetch_tool
  ... (truncated)
- `frontend/src/content/zh/harness/tools.mdx`
  L151: ```yaml
  L152: tools:
  L153: - use: deerflow.community.jina_ai.tools:web_fetch_tool
  L154: api_key: $JINA_API_KEY # 可选；匿名使用有速率限制
  L155: ```
  L156: 将网页转换为干净的 Markdown。无 API Key 也可使用，但有更严格的速率限制。
  L159: ```yaml
  L160: tools:
  L161: - use: deerflow.community.exa.tools:web_fetch_tool
  L162: api_key: $EXA_API_KEY
  L163: ```

## c5d57b45 2026-04-26 yangzheli
fix: resolve make dev and test-e2e errors (#2570)

- `frontend/src/core/auth/server.ts`

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

- `frontend/src/core/api/api-client.ts`
  L16: * change cookie rotation transparently. Both the ``/api/langgraph/*`` SDK
  L17: * path and the direct REST endpoints in ``fetcher.ts:fetchWithAuth``
- `frontend/src/core/config/index.ts`

## f7b10d42 2026-04-30 yangzheli
fix(frontend): create thread on first submit in new-agent page (#2656)

The new-agent page pre-generates a thread UUID and passed it directly
to useThreadStream, which made the LangGraph SDK POST to
/threads/{uuid}/runs/stream against a thread the backend had never
created. After PR #2566 introduced multi-tenant owner checks on the
runs endpoints, that request now 404s with "Thread not found".

Pass threadId: undefined to useThreadStream so the SDK takes the
create-then-run path. The pre-generated UUID is still forwarded via
SubmitOptions.threadId in sendMessage, so the new thread is created
with that exact id and onCreated rebinds the hook to it.

Co-authored-by: Claude Opus 4.7 <noreply@anthropic.com>

- `frontend/src/app/workspace/agents/new/page.tsx`

## 24a5a006 2026-04-30 Jsonz
fix: avoid duplicate call to extractReasoningContentFromMessage (#2661)

In convertToSteps(), the extractReasoningContentFromMessage function was
called twice for the same message - once to check if reasoning exists and
again to assign it to the step object. Reuse the already-extracted value
from the local variable instead.

- `frontend/src/components/workspace/messages/message-group.tsx`

## 222a7773 2026-05-04 Nan Gao
fix(frontend): avoid misleading error message when agent api is disable (#2697) (#2698)

- `frontend/src/app/workspace/agents/new/page.tsx`
- `frontend/src/core/agents/api.ts`
- `frontend/src/core/i18n/locales/en-US.ts`
- `frontend/src/core/i18n/locales/types.ts`
- `frontend/src/core/i18n/locales/zh-CN.ts`

## d02f762a 2026-05-04 YuJitang
feat: refine token usage display modes (#2329)

* feat: refine token usage display modes

* docs: clarify token usage accounting semantics

* fix: avoid duplicate subtask debug keys

* style: format token usage tests

* chore: address token attribution review feedback

* Update test_token_usage_middleware.py

* Update test_token_usage_middleware.py

* chore: simplify token attribution fallback

* fix token usage metadata follow-up handling

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `frontend/src/app/workspace/agents/[agent_name]/chats/[thread_id]/page.tsx`
- `frontend/src/app/workspace/chats/[thread_id]/page.tsx`
- `frontend/src/components/workspace/messages/message-group.tsx`
- `frontend/src/components/workspace/messages/message-list-item.tsx`
- `frontend/src/components/workspace/messages/message-list.tsx`
- `frontend/src/components/workspace/messages/message-token-usage.tsx`
- `frontend/src/components/workspace/token-usage-indicator.tsx`
- `frontend/src/core/i18n/locales/en-US.ts`
- `frontend/src/core/i18n/locales/types.ts`
- `frontend/src/core/i18n/locales/zh-CN.ts`
- `frontend/src/core/messages/usage-model.ts`
  L68: // Precise write_todos labels come from the backend attribution payload.
  L69: // The frontend fallback intentionally stays generic so we do not duplicate
  L70: // backend/packages/harness/deerflow/agents/middlewares/token_usage_middleware.py
  L71: //::_build_todo_actions and risk the two diffing algorithms drifting apart.
  L321: // Versioning is additive for now: the frontend should ignore unknown
  L322: // fields and fall back when required fields become incompatible.
- `frontend/src/core/messages/utils.ts`
- `frontend/src/core/settings/local.ts`

## af6e48cc 2026-05-04 Willem Jiang
fix(i18n): add Chinese translations for account settings page (#2712)

The account settings page had all user-facing strings (profile labels,
  password form placeholders, validation messages, button text) hardcoded
  in English. Replace them with i18n translation keys so the page renders
  correctly when the locale is set to Chinese.

 Fixed #2710

- `frontend/src/components/workspace/settings/account-settings-page.tsx`
- `frontend/src/core/i18n/locales/en-US.ts`
- `frontend/src/core/i18n/locales/types.ts`
- `frontend/src/core/i18n/locales/zh-CN.ts`

## aded753d 2026-05-05 Xinmin Zeng
fix(frontend): restore localhost fallback for getGatewayConfig in prod mode (#2705) (#2718)

* fix(frontend): unify gateway-config localhost fallback for prod (#2705)

`getGatewayConfig()` only fell back to localhost defaults when
`NODE_ENV === "development"`, while `next.config.js` always falls back
to `127.0.0.1:8001`. Running `make start` (which sets NODE_ENV=production
via `next start`) without `DEER_FLOW_INTERNAL_GATEWAY_BASE_URL` /
`DEER_FLOW_TRUSTED_ORIGINS` therefore caused zod to throw inside SSR
layouts and surfaced as a 500.

Drop the NODE_ENV gating and use localhost defaults everywhere — the
"force explicit config in prod" intent should be enforced by deployment
templates (docker-compose already sets both vars), not by request-time
crashes. Document the two vars in both .env.example files and add unit
coverage for the dev/prod env-unset paths.

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* Update internalGatewayUrl in gateway config tests

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `frontend/src/core/auth/gateway-config.ts`

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

- `frontend/src/content/en/harness/tools.mdx`
  L67: ### update_agent
  L68: 
  L69: Persists updates to the current custom agent's `SOUL.md` and `config.yaml`. Bound to the lead agent only when a custom agent is active (`agent_name` is set in the runtime context). Use this when the user asks the agent to refine its own description, personality, skill whitelist, tool-group whitelist, or default model — it writes directly into the per-user layout `{base_dir}/users/{user_id}/agents/{agent_name}/`, so the change is picked up automatically on the next user turn. Only the fields you explicitly pass are updated; omit a field to preserve its existing value. Pass `skills=[]` to disable all skills, or omit `skills` to keep the existing whitelist.
  L70: 
  L71: ---
  L72: 
- `frontend/src/content/zh/harness/tools.mdx`
  L64: ### update_agent
  L65: 
  L66: 将更新持久化到当前自定义 Agent 的 `SOUL.md` 和 `config.yaml`。仅当激活了自定义 Agent（运行时上下文中存在 `agent_name`）时，才会绑定到 lead agent。当用户在 Agent 内开启 chat 并要求该 Agent 调整自身的描述、人格、技能白名单、工具组白名单或默认模型时使用——它会直接写入按用户隔离的 `{base_dir}/users/{user_id}/agents/{agent_name}/` 下的真实配置文件，下一轮对话即可生效。仅显式传入的字段会被更新；省略某个字段以保留其现有值。传入 `skills=[]` 可禁用全部技能，省略 `skills` 则保留现有白名单。
  L67: 
  L68: ---
  L69: 

## 27559f36 2026-05-07 Xinmin Zeng
fix(frontend): defer thread id to onStart to avoid 404 on new chat (#2749)

* fix(frontend): defer thread id to onStart to avoid 404 on new chat

The LangGraph SDK's useStream eagerly fetches /threads/{id}/history the
moment it receives a thread id, and the local useThreadRuns issues
GET /threads/{id}/runs for the same reason. The chats page used to flip
isNewThread=false (and forward the client-generated thread id) inside
the synchronous onSend callback, before thread.submit had created the
thread on the backend. The two queries therefore raced ahead of
POST /runs/stream and returned 404 on the very first send.

Drop the onSend handler so isNewThread stays true until onStart fires
from useStream's onCreated — by then the backend has the thread, and
the SDK's submittingRef guard naturally suppresses the redundant
history fetch. The agent chat page already uses this pattern, so this
also unifies the two flows.

Adds an E2E regression that records request ordering and asserts
GET /history and GET /runs are never issued before POST /runs/stream
on the first send from /chats/new.

Closes #2746

* fix(frontend): split welcome layout from backend thread state

Removing onSend kept GET /history and GET /runs from racing ahead of
POST /runs/stream, but it also coupled the welcome layout (centered
input, hero, quick actions) to backend thread creation.  Until onCreated
returned, the user's optimistic message and the welcome hero rendered on
top of each other.

Introduce a dedicated `isWelcomeMode` UI flag, separate from
`isNewThread`:
- `isNewThread` still tracks "backend has no thread yet" and gates the
  thread id forwarded to useStream.
- `isWelcomeMode` drives the visual layout (header background, input
  box position, max width, hero, quick actions, autoFocus) and flips to
  false inside onSend so the layout animates immediately.

`isWelcomeMode` is kept in sync with `isNewThread` via an effect so
sidebar navigation and "new chat" still behave correctly.  All 15 E2E
tests pass, including the ordering regression added in the previous
commit.

* test(e2e): use monotonic sequence for thread-init ordering check

Date.now() is millisecond-resolution, so two requests emitted within
the same tick would share a timestamp and slip past the strict `<`
ordering assertions. Replace the timestamp with a monotonic counter
that increments on every observed request/requestfinished event so the
ordering check is robust regardless of scheduling.

Per PR #2749 review feedback from copilot-pull-request-reviewer.

* refactor(input-box): rename isNewThread prop to isWelcomeMode

Inside InputBox, the prop named `isNewThread` is only ever consulted
for visual layout decisions — gating follow-up suggestions, the bottom
background strip, and the welcome-mode quick-action SuggestionList. It
never reflects "the backend has created the thread", which after #2746
is tracked separately via `isNewThread` in the chat pages themselves.

Rename the prop to `isWelcomeMode` and update both call sites
(workspace chats page and agent chats page) so the prop name matches
its actual semantics. No behavior change.

Per PR #2749 review feedback from @WillemJiang.

- `frontend/src/app/workspace/agents/[agent_name]/chats/[thread_id]/page.tsx`
- `frontend/src/app/workspace/chats/[thread_id]/page.tsx`
  L38: // `isNewThread` tracks whether the backend has the thread yet — gates the
  L39: // SDK's history fetch (see issue #2746).  `isWelcomeMode` is the visual
  L40: // welcome layout (centered input, hero, quick actions); we flip it to false
  L41: // the moment the user submits so the UI animates immediately, even though
  L42: // `isNewThread` stays true until the backend actually creates the thread.
  L54: // Keep welcome layout in sync when navigating between threads (sidebar
  L55: // clicks, "new chat" button).  Submitting in /chats/new flips the layout
  L56: // via onSend below — `isNewThread` stays true until onStart, so this effect
  L57: // is harmless during the submit transition.
  L75: // onSend only animates the UI; do NOT flip `isNewThread` here — the
  L76: // LangGraph SDK eagerly fetches /history the moment it receives a
  L77: // thread id and assumes the thread exists on the backend (issue #2746).
- `frontend/src/components/workspace/input-box.tsx`
  L129: /**
  L130: * Whether to render the input in welcome layout (vertically centered,
  L131: * with hero + quick action suggestions).  This is purely a visual flag,
  L132: * decoupled from "the backend has created the thread" — see issue #2746.
  L133: */

## 6c220a9a 2026-05-07 Willem Jiang
fix(chat): prevent first user message from being swallowed in new conversations (#2731)

* fix(chat): prevent first user message from being swallowed in new conversations

  The optimistic message clearing effect cleared too eagerly — any stream
  message (including AI messages from messages-tuple events) triggered the
  clear before the server's human message had arrived via values events.
  For new threads this caused the user's first prompt to disappear permanently.

  Only clear optimistic messages once the server's human message has been
  confirmed to arrive in thread.messages, not just when any message arrives.

  Fixes #2730

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `frontend/src/core/threads/hooks.ts`
  L289: // Track human message count before sending to prevent clearing optimistic
  L290: // messages before the server's human message arrives (e.g. when AI messages
  L291: // from "messages-tuple" events arrive before the input human message from
  L292: // "values" events).
  L310: // Clear optimistic when server messages arrive.
  L311: // For messages with a human optimistic message, wait until the server's
  L312: // human message has arrived to avoid clearing before the input message
  L313: // appears in the stream (the input message may arrive via "values" events
  L314: // after individual "messages-tuple" events for AI messages).

## 530bda71 2026-05-08 YuJitang
fix: dedupe token usage aggregation by message id (#2770)

- `frontend/src/core/messages/usage.ts`
  L31: * Accumulate token usage across AI messages.
  L32: *
  L33: * UI rendering may place the same AI message in more than one group, such as
  L34: * when a message contains both reasoning and final answer content. Token usage
  L35: * is attached to the AI message itself, so a message id should only contribute
  L36: * once to any aggregate.

## 41741608 2026-05-09 YuJitang
fix: use backend thread token usage for header total (#2800)

* fix: use backend thread token usage for header total

* Refactor thread token usage fetch

- `frontend/src/app/workspace/agents/[agent_name]/chats/[thread_id]/page.tsx`
- `frontend/src/app/workspace/chats/[thread_id]/page.tsx`
- `frontend/src/components/workspace/token-usage-indicator.tsx`
- `frontend/src/core/i18n/locales/en-US.ts`
- `frontend/src/core/i18n/locales/zh-CN.ts`
- `frontend/src/core/messages/usage.ts`
- `frontend/src/core/threads/api.ts`
- `frontend/src/core/threads/hooks.ts`
  L347: // When streaming starts without a baseline (e.g. reconnection, run started
  L348: // from another client, or page reload mid-stream), snapshot the current
  L349: // messages so only *new* messages are treated as "pending" for token usage.
  L394: // Capture the current human message count before showing optimistic
  L395: // messages so we can wait for the server's copy of the user input.
- `frontend/src/core/threads/token-usage.ts`
- `frontend/src/core/threads/types.ts`

## 1c96a6af 2026-05-09 Eilen Shin
fix: keep new agent bootstrap in user scope (#2784)

- `frontend/src/app/workspace/agents/new/page.tsx`
- `frontend/src/core/i18n/locales/en-US.ts`
- `frontend/src/core/i18n/locales/zh-CN.ts`

## dfa4eb0c 2026-05-10 DanielWalnut
[codex] fix follow-up suggestions layout (#2836)

* fix follow-up suggestions layout

* fix agent chat welcome layout transition

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `frontend/src/app/workspace/agents/[agent_name]/chats/[thread_id]/page.tsx`
  L46: // `isNewThread` gates history/token-usage fetches until the backend creates
  L47: // the thread. `isWelcomeMode` controls only the centered welcome layout, so
  L48: // it can flip immediately on submit without triggering eager history loads.
- `frontend/src/app/workspace/chats/[thread_id]/page.tsx`
- `frontend/src/components/workspace/input-box.tsx`
- `frontend/src/components/workspace/messages/message-list.tsx`

## 5127f08e 2026-05-10 YuJitang
enable token usage by default (#2841)

- `frontend/src/content/en/harness/middlewares.mdx`
  L113: enabled: true
- `frontend/src/content/zh/harness/middlewares.mdx`
  L113: enabled: true

## e82b2fb4 2026-05-11 YuJitang
docs: clarify token usage accounting semantics (#2845)

- `frontend/src/content/en/application/workspace-usage.mdx`
  L70: ## Understanding token usage
  L71: 
  L72: If token usage display is enabled, DeerFlow shows one conversation-level total in
  L73: the header and optional per-turn or debug summaries in the message list.
  L74: 
  L75: - **Header total**: the persisted thread-level total from the backend. While the
  L76: current run is still streaming, the header may also include the visible
  L77: in-flight usage for that unfinished response.
  L78: - **Per-turn / debug usage**: usage derived from the assistant messages that are
  L79: currently visible in the conversation view.
  L80: 
  L81: This means the header total and the visible per-turn totals do **not** need to
  L82: add up exactly. The header is a thread ledger; the per-turn view is a rendering
  L83: of the messages you can currently see.
  L84: 
  L85: These totals may also differ from your provider's billing page. Common reasons
  L86: include retries, failed requests, cached input tokens, reasoning tokens,
  L87: provider-specific billing rules, and internal calls that do not appear as normal
  L88: chat messages.
  L89: 
- `frontend/src/content/zh/application/workspace-usage.mdx`
  L73: ## 理解 Token 用量
  L74: 
  L75: 如果启用了 Token 用量显示，DeerFlow 会在顶部显示一个对话级总量，并在消息列表中按配置显示每轮或调试级别的用量摘要。
  L76: 
  L77: - **顶部总量**：后端持久化的线程级总账。当当前回复仍在流式返回时，顶部还可能临时叠加这条未完成回复的可见进行中用量。
  L78: - **每轮 / 调试用量**：根据当前界面里可见的 assistant 消息计算出来的用量。
  L79: 
  L80: 因此，顶部总量和当前可见的每轮总和**不要求完全相等**。顶部展示的是整个线程的总账；每轮展示的是你当前能看到的消息视图。
  L81: 
  L82: 这些数字也可能与模型供应商的账单页不同。常见原因包括重试请求、失败请求、缓存输入 token、推理 token、供应商自己的计费口径，以及不会以普通聊天消息形式显示的内部调用。
  L83: 
- `frontend/src/core/i18n/locales/en-US.ts`
- `frontend/src/core/i18n/locales/zh-CN.ts`

## 84f88b66 2026-05-12 Eilen Shin
docs: align runtime docs with gateway mode (#2868)

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `frontend/src/content/en/application/agents-and-threads.mdx`
  L114: The Gateway embedded runtime uses the <code>checkpointer</code> setting in
  L115: <code>config.yaml</code>. The same setting is also used by
  L116: <code>DeerFlowClient</code> in direct Python integrations.
- `frontend/src/content/en/application/deployment-guide.mdx`
  L26: | Gateway API | 8001 | FastAPI backend + embedded agent runtime |
  L38: Stops all services. Safe to run even if a service is not running.
  L43: logs/gateway.log     # API gateway and agent runtime logs
  L51: tail -f logs/gateway.log
  L75: Services: nginx, frontend, gateway, and optionally provisioner (for K8s-managed sandboxes).
  L100: Thread data is stored in `backend/.deer-flow/threads/`. In Docker deployments, this directory is bind-mounted into the gateway container.
  L162: nginx routes all traffic to the frontend or Gateway. `/api/langgraph/*` is rewritten to Gateway's LangGraph-compatible `/api/*` routes, so no separate LangGraph upstream is required.
  L180: | Gateway + agent runtime         | 2 vCPU, 4 GB RAM | 4 vCPU, 8 GB RAM |
- `frontend/src/content/en/application/index.mdx`
  L28: | **Gateway API**         | FastAPI-based REST API with the embedded LangGraph-compatible agent runtime                          |
  L32: The DeerFlow App runs behind a single nginx reverse proxy:
  L47: - **nginx**: routes requests — `/api/*` and `/api/langgraph/*` to Gateway, and everything else to the frontend.
  L48: - **Frontend** (Next.js + React): the browser UI. Communicates with Gateway.
  L49: - **Gateway** (FastAPI): handles API operations and the embedded LangGraph-compatible runtime for thread state, agent execution, and streaming.
  L59: | State persistence | Gateway runtime + optional SQLite/PostgreSQL checkpointer             |
- `frontend/src/content/en/application/operations-and-troubleshooting.mdx`
  L18: | `logs/gateway.log`   | FastAPI Gateway API and agent runtime |
  L64: 1. Check `logs/gateway.log` for startup errors.
  L124: 1. Check `logs/gateway.log` for MCP initialization errors.
  L135: - Look for memory update errors in `logs/gateway.log` (search for "memory").
- `frontend/src/content/en/application/quick-start.mdx`
  L3: description: This guide walks you through starting DeerFlow App on your local machine using the `make dev` workflow. Gateway, Frontend, and nginx start together and are accessible through a single URL.
  L15: This guide walks you through starting DeerFlow App on your local machine using the `make dev` workflow. Gateway, Frontend, and nginx start together and are accessible through a single URL.
  L91: - Gateway API and embedded agent runtime on port `8001`
  L121: (missing API keys, config parsing failures) appear in `logs/gateway.log`.
- `frontend/src/content/en/harness/skills.mdx`
  L71: `load_skills()` in `skills/loader.py` scans both `public/` and `custom/` directories under the configured skills path. It re-reads `ExtensionsConfig.from_file()` on every call, which means enabling or disabling a skill through the Gateway API takes effect immediately in the running agent runtime without a restart.
- `frontend/src/content/zh/application/configuration.mdx`
- `frontend/src/content/zh/application/deployment-guide.mdx`
  L26: | Gateway API | 8001 | FastAPI 后端 + 嵌入式 Agent 运行时 |
  L38: 停止所有服务。即使某个服务没有运行也可以安全执行。
  L43: logs/gateway.log     # API Gateway 和 Agent 运行时日志
  L51: tail -f logs/gateway.log
  L97: 线程数据存储在 `backend/.deer-flow/threads/`。在 Docker 部署中，此目录会绑定挂载到 gateway 容器中。
  L157: nginx 将流量路由到前端或 Gateway。`/api/langgraph/*` 会被重写到 Gateway 的 LangGraph-compatible `/api/*` 路由，因此不需要单独的 LangGraph upstream。
  L175: | Gateway + Agent 运行时    | 2 vCPU、4 GB RAM | 4 vCPU、8 GB RAM |
- `frontend/src/content/zh/application/index.mdx`
  L28: | **Gateway API**  | 基于 FastAPI 的 REST API，并内置 LangGraph-compatible Agent 运行时 |
  L32: DeerFlow 应用通过单个 nginx 反向代理提供：
  L47: - **nginx**：路由请求——`/api/*` 和 `/api/langgraph/*` 到 Gateway，其余到前端。
  L48: - **前端**（Next.js + React）：浏览器界面，与 Gateway 通信。
  L49: - **Gateway**（FastAPI）：处理 API 操作，并通过内置 LangGraph-compatible 运行时管理线程状态、Agent 执行和流式传输。
  L59: | 状态持久化   | Gateway 运行时 + 可选 SQLite/PostgreSQL 检查点 |
- `frontend/src/content/zh/application/operations-and-troubleshooting.mdx`
  L18: | `logs/gateway.log`   | API 请求/响应、Agent 运行时和 Gateway 错误 |
  L25: tail -f logs/gateway.log     # 查看 API 请求和 Agent 活动
  L66: # 检查 Gateway 日志中的模型错误
  L67: grep -i "error\|apikey\|unauthorized" logs/gateway.log | tail -20
  L116: **症状**：MCP 工具未出现，`logs/gateway.log` 中有超时错误。
  L122: grep -i "mcp\|timeout" logs/gateway.log | tail -20
- `frontend/src/content/zh/application/quick-start.mdx`
  L3: description: 本指南引导你使用 `make dev` 工作流在本地机器上启动 DeerFlow 应用。Gateway、前端和 nginx 会一起启动，通过单个 URL 访问。
  L15: 本指南引导你使用 `make dev` 工作流在本地机器上启动 DeerFlow 应用。Gateway、前端和 nginx 会一起启动，通过单个 URL 访问。
  L91: - Gateway API 和嵌入式 Agent 运行时，端口 `8001`
  L121: Key、配置解析失败）会出现在 <code>logs/gateway.log</code> 中。

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

- `frontend/src/components/workspace/messages/message-token-usage.tsx`
- `frontend/src/core/messages/usage.ts`
- `frontend/src/core/threads/hooks.ts`

## 0c37509b 2026-05-15 Nan Gao
fix(middleware): Prevent todo completion reminder IMMessage leak (#2907)

* fix(middleware): Prevent todo completion reminder IMMessage leak (#2892)

* make format

* fix(middleware): Clear stale todo reminder counts (#2892)

* add size guard for _completion_reminder_counts and add a integration test

- `frontend/src/core/messages/utils.ts`

## 7c42ab3e 2026-05-15 Admire
fix(frontend): wait for async chat submit before clearing (#2940)

* fix(frontend): wait for async chat submit before clearing

* test(frontend): cover pending attachment uploads

* fix(frontend): preserve sync submit semantics

- `frontend/src/app/workspace/agents/[agent_name]/chats/[thread_id]/page.tsx`
- `frontend/src/app/workspace/chats/[thread_id]/page.tsx`
- `frontend/src/components/ai-elements/prompt-input.tsx`
- `frontend/src/components/workspace/input-box.tsx`

## 6d3cffb4 2026-05-16 Nan Gao
fix(frontend): deduplicate restored thread messages (#2958)

* fix(frontend): fix duplicate messages when reopening agent sessions (#2957)

* make format

* fix(frontend): retry pending thread history loads

- `frontend/src/core/threads/hooks.ts`

## 4538c322 2026-05-16 pereverzev
Fix type check for 'thinking' in message content (#2964)

* Fix type check for 'thinking' in message content

When Gemini via Vertex AI returns content as a string inside an array, the in operator throws TypeError because it can't be used on primitives.

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Zil6n <136249885+Zil6n@users.noreply.github.com>
Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `frontend/src/core/messages/utils.ts`

## c0233cae 2026-05-17 jinghuan-Chen
fix(frontend): resolve login page flickering and resize observer loop. (#2954)

* fix(frontend): resolve login page flickering and resize observer loop.

* fix(frontend): allow vertical scrolling on login page

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

---------

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `frontend/src/app/(auth)/login/page.tsx`
- `frontend/src/components/ui/flickering-grid.tsx`

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

- `frontend/src/content/en/harness/middlewares.mdx`
  L53: Warning interventions are queued per thread and run, then drained on the next model call as a single hidden `HumanMessage(name="loop_warning")` appended after existing tool results. This keeps provider tool-call pairing valid. Run start/end hooks clear stale or undelivered warnings, and hard stops still strip tool calls before forcing a final text response.
  L54: 
- `frontend/src/content/zh/harness/middlewares.mdx`
  L53: Warning 介入会按 thread 和 run 排队，并在下一次模型调用时合并为一条隐藏的 `HumanMessage(name="loop_warning")`，追加到已有工具结果之后。这样不会破坏 provider 对 tool-call/tool-message 配对的校验。Run 开始和结束时会清理过期或未送达的 warning；达到 hard stop 时仍会清空 tool calls 并强制生成最终文本回复。
  L54: 

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

- `frontend/src/components/workspace/messages/message-list.tsx`
- `frontend/src/core/messages/utils.ts`
  L400: /**
  L401: * Tag names that backend middlewares wrap around internal payloads before
  L402: * letting them ride along inside LangGraph message ``content``.
  L403: *
  L404: * These markers are *not* user copy — they come from:
  L405: *
  L406: * - ``UploadsMiddleware`` → ``<uploaded_files>``
  L407: * - ``DynamicContextMiddleware`` → ``<system-reminder>`` (carrying
  L408: *   ``<memory>`` / ``<current_date>`` inside)
  L409: * - ``TodoListMiddleware`` / ``LoopDetectionMiddleware`` style reminders
  L410: *   live in ``hide_from_ui`` HumanMessages, but their inner payload uses
  L411: *   the same tag vocabulary.
  L412: *
  L413: * The primary export filter is {@link isHiddenFromUIMessage}. This list is
  L414: * the defence-in-depth strip for any message that — by middleware bug,
  L415: * provider quirk, or merge-conflict regression — slips through without
  L416: * its ``hide_from_ui`` flag set.
  L417: */
  L430: /**
  L431: * Strip every known backend-injected marker from message content.
  ... (truncated)
- `frontend/src/core/tasks/subtask-result.ts`
  L11: /**
  L12: * Prefix strings the backend `task` tool writes into its result `content`.
  L13: *
  L14: * These values are not user-facing copy — they are part of the
  L15: * backend↔frontend contract defined in
  L16: * `backend/packages/harness/deerflow/tools/builtins/task_tool.py` (returned
  L17: * from the tool body) and in
  L18: * `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py`
  L19: * (wrapper for tool exceptions). Any change here must be paired with the
  L20: * matching backend change. Exported so a future structured-status migration
  L21: * can reference the same values from one place.
  L22: *
  L23: * `task_tool.py` also emits three `Error:` strings for pre-execution failures
  L24: * — unknown subagent type, host-bash disabled, and "task disappeared from
  L25: * background tasks". They are handled by {@link ERROR_WRAPPER_PATTERN}
  L26: * rather than dedicated prefixes because the wrapper already produces
  L27: * exactly the right `terminal failed` shape.
  L28: */
  L36: /**
  L37: * Map a `task` tool result string to a {@link SubtaskStatus}.
  ... (truncated)
- `frontend/src/core/threads/export.ts`
  L15: /**
  L16: * Optional debug switches for advanced exports.
  L17: *
  L18: * Bytedance/deer-flow issue #3107 BUG-006 explicitly prescribes that the
  L19: * default export includes only the user-visible transcript and excludes
  L20: * thinking/reasoning content, tool calls, tool results, hidden messages,
  L21: * memory injection, and `<system-reminder>` payloads. These options let a
  L22: * future "debug export" surface re-include any of those categories without
  L23: * forking the formatter. They are not currently wired to any UI control —
  L24: * callers that want them must construct the options object explicitly.
  L25: */
  L51: // Defence-in-depth: even if a middleware-injected marker slipped through
  L52: // the `hide_from_ui` filter, scrub every known internal tag before the
  L53: // content lands in a user-visible export file.
  L140: // Run the same sanitiser the Markdown path uses so the JSON `content`
  L141: // field never carries inline `<think>...</think>` wrappers, content-array
  L142: // thinking blocks, `<uploaded_files>` markers, or other internal payloads.
  L156: // Drop rows with no exportable payload (empty content + no opted-in
  L157: // reasoning / tool_calls). Uses falsy semantics so `reasoning: ""` (the
  L158: // empty string ``extractReasoningContentFromMessage`` can hand back) is
  ... (truncated)

## 253542ea 2026-05-22 Nan Gao
docs: discourage MCP filesystem workspace config (#3141)

- `frontend/src/content/en/harness/mcp.mdx`
  L41: <Callout type="warning">
  L42: Do not add an MCP filesystem server for DeerFlow workspace files. DeerFlow
  L43: already provides built-in file tools for thread-scoped workspace access, and
  L44: overlapping file tools with different path semantics can make LLM tool
  L45: selection and file access behavior unstable. DeerFlow does not currently
  L46: adapt MCP Roots mode for filesystem servers: it does not publish per-thread
  L47: MCP roots or map sandbox paths such as <code>/mnt/user-data/...</code> to
  L48: paths accepted by <code>@modelcontextprotocol/server-filesystem</code>.
  L49: </Callout>
  L50: 
- `frontend/src/content/zh/application/configuration.mdx`
  L196: "my-server": {
  L198: "args": ["-y", "@my-org/my-mcp-server"],
  L205: <Callout type="warning">
  L206: 不要为 DeerFlow 工作区文件引入 MCP filesystem server。它会与 DeerFlow
  L207: 内置文件工具形成路径语义不同的重复能力，让 LLM 行为不稳定。DeerFlow
  L208: 当前没有为 filesystem server 适配 MCP Roots 模式，也不会把{" "}
  L209: <code>/mnt/user-data/...</code> 这类沙箱路径映射成{" "}
  L210: <code>@modelcontextprotocol/server-filesystem</code> 可接受的路径。
  L211: </Callout>
  L212: 
- `frontend/src/content/zh/harness/mcp.mdx`
  L40: <Callout type="warning">
  L41: 不要为 DeerFlow 工作区文件引入 MCP filesystem server。DeerFlow 已提供按
  L42: thread 隔离的内置文件工具；重复引入路径语义不同的文件工具，会让 LLM
  L43: 的工具选择和文件访问行为不稳定。DeerFlow 当前没有为 filesystem server
  L44: 适配 MCP Roots 模式：不会发布按 thread 收窄的 MCP roots，也不会把{" "}
  L45: <code>/mnt/user-data/...</code> 这类沙箱路径映射成{" "}
  L46: <code>@modelcontextprotocol/server-filesystem</code> 可接受的路径。
  L47: </Callout>
  L48: 

## 914d6a4f 2026-05-22 Nan Gao
docs: add provider safety termination post (#3167)

- `frontend/src/content/en/posts/provider-safety-termination-in-tool-agents.mdx`
  L1: ---
  L2: title: Tool-Using Agents Must Handle Provider Safety Termination Signals Correctly
  L3: description: Why tool calls left in a safety-terminated model response must not be executed, and how to configure provider detectors in DeerFlow.
  L4: date: 2026-05-22
  L5: tags:
  L6: - Safety
  L7: - Agents
  L8: - Model Providers
  L9: ---
  L10: 
  L11: ## Tool-Using Agents Must Handle Provider Safety Termination Signals Correctly
  L12: 
  L13: When a large model provider decides that an input or output has triggered a safety policy, the important outcome is not merely that the model says less. The application needs to know that the current generation turn has been terminated. In a normal chat interface, this may appear as a refusal, filtered text, or an error response. For an Agent that can call tools, the risk is higher: if the provider has already stopped generation while the response still contains `tool_calls`, those tool arguments may only be partially generated.
  L14: 
  L15: These partial tool calls must not be executed as normal intent. A truncated `write_file` call may write an incomplete report. A truncated `bash` call may enter the sandbox with incomplete arguments. After seeing the failed result, the Agent may retry and trigger the same safety rule repeatedly.
  L16: 
  L17: [PR #3035](https://github.com/bytedance/deer-flow/pull/3035) addresses this boundary: when a provider stops generation with a safety signal while the response still contains tool calls, DeerFlow should suppress those tool calls first and record the turn as a safety termination event.
  L18: 
  L19: ## Why Safety Termination Needs Dedicated Handling
  L20: 
  ... (truncated)
- `frontend/src/content/zh/posts/provider-safety-termination-in-tool-agents.mdx`
  L1: ---
  L2: title: 工具型 Agent 需要正确处理模型提供商的安全中止信号
  L3: description: 当模型输出因安全策略被中止时，为什么不能继续执行残留的工具调用，以及如何在 DeerFlow 中配置 provider detector。
  L4: date: 2026-05-22
  L5: tags:
  L6: - Safety
  L7: - Agents
  L8: - Model Providers
  L9: ---
  L10: 
  L11: ## 工具型 Agent 需要正确处理模型提供商的安全中止信号
  L12: 
  L13: 当大模型提供商认为输入或输出触发了安全策略时，最理想的结果不是“模型少说了几句话”，而是应用已经明确知道这一轮生成被中止了。对于普通聊天界面，这通常表现为拒答、过滤后的文本，或者一个错误响应。对于能调用工具的 Agent，风险会更高：如果 provider 已经中止输出，但响应里仍残留了 `tool_calls`，这些工具参数很可能只生成了一半。
  L14: 
  L15: 这类半截工具调用不应被当成正常意图执行。一个被截断的 `write_file` 可能写出不完整的报告；一个被截断的 `bash` 调用可能带着残缺参数进入沙箱；Agent 看到失败结果后还可能继续重试，反复触发同一条安全规则。
  L16: 
  L17: [PR #3035](https://github.com/bytedance/deer-flow/pull/3035) 处理的就是这个边界：当 provider 用安全信号中止生成，同时响应仍带有工具调用时，DeerFlow 应先压制这些工具调用，再把这一轮作为安全中止事件记录下来。
  L18: 
  L19: ## 为什么需要单独处理安全中止
  L20: 
  ... (truncated)

## b103d1a7 2026-05-23 JeffJiang
feat(frontend): support static website demo mode (#3170)

* feat(frontend): support static website demo mode

* fix(frontend): render html artifact previews from blob content

* chore(frontend): apply pre-commit formatting

* fix(frontend): address static demo PR review comments

* Update the release information of DeerFlow

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `frontend/src/app/workspace/chats/[thread_id]/layout.tsx`
- `frontend/src/app/workspace/chats/[thread_id]/page.tsx`
- `frontend/src/app/workspace/chats/[thread_id]/providers.tsx`
- `frontend/src/app/workspace/layout.tsx`
- `frontend/src/components/workspace/artifacts/artifact-file-detail.tsx`
- `frontend/src/content/en/index.mdx`
  L23: - [Introduction](./docs/introduction)
  L24: - [Why DeerFlow](./docs/introduction/why-deerflow)
  L25: - [Harness vs App](./docs/introduction/harness-vs-app)
  L31: - [DeerFlow Harness](./docs/harness)
  L32: - [Quick Start](./docs/harness/quick-start)
  L33: - [Configuration](./docs/harness/configuration)
  L34: - [Customization](./docs/harness/customization)
  L40: - [DeerFlow App](./docs/app)
  L41: - [Quick Start](./docs/app/quick-start)
  L42: - [Deployment Guide](./docs/app/deployment-guide)
  L43: - [Workspace Usage](./docs/app/workspace-usage)
  L82: - [Tutorials](./docs/tutorials)
  L88: - [Reference](./docs/reference)
  L92: - If you are **evaluating the project**, start with [Introduction](./docs/introduction).
  L93: - If you are **building your own agent system**, start with [DeerFlow Harness](./docs/harness).
  L94: - If you are **deploying DeerFlow for users**, start with [DeerFlow App](./docs/app).
  L95: - If you want to **learn by doing**, go to [Tutorials](./docs/tutorials).
- `frontend/src/content/en/posts/releases/2_0_rc.mdx`
  L1: ---
  L2: title: DeerFlow 2.0 M1
  L3: description: DeerFlow 2.0 M1 is officially in RC. Here's what you need to know.
  L4: date: 2026-05-30
  L5: tags:
  L6: - Release
  L7: ---
  L8: 
  L9: ## DeerFlow 2.0 M1 Release
- `frontend/src/content/zh/index.mdx`
  L23: - [简介](./docs/introduction)
  L24: - [为什么选择 DeerFlow](./docs/introduction/why-deerflow)
  L25: - [Harness 与应用的区别](./docs/introduction/harness-vs-app)
  L31: - [DeerFlow Harness](./docs/harness)
  L32: - [快速上手](./docs/harness/quick-start)
  L33: - [配置](./docs/harness/configuration)
  L34: - [自定义与扩展](./docs/harness/customization)
  L40: - [DeerFlow 应用](./docs/application)
  L41: - [快速上手](./docs/application/quick-start)
  L42: - [部署指南](./docs/application/deployment-guide)
  L43: - [工作区使用](./docs/application/workspace-usage)
- `frontend/src/core/api/api-client.ts`
  L101: /* empty */
  L104: /* empty */
- `frontend/src/core/artifacts/utils.ts`
- `frontend/src/core/auth/AuthProvider.tsx`
- `frontend/src/core/auth/server.ts`
- `frontend/src/core/auth/static-user.ts`
- `frontend/src/core/models/api.ts`
- `frontend/src/core/static-mode.ts`
- `frontend/src/core/threads/static-demo.ts`

## a64a39db 2026-05-23 Nan Gao
config: raise default summarization trigger before v2.0-m1 (#3174)

* config: update summarization configuration

* docs: sync summarization trigger guidance

- `frontend/src/content/en/harness/middlewares.mdx`
  L165: value: 32000
- `frontend/src/content/zh/harness/middlewares.mdx`
  L157: value: 32000

## 604fcbb9 2026-05-23 AochenShen99
Stabilize write artifact previews (#3172)

- `frontend/src/components/workspace/artifacts/artifact-file-detail.tsx`
- `frontend/src/core/artifacts/loader.ts`
- `frontend/src/core/artifacts/preview.ts`

## d0fa37e7 2026-05-23 Admire
fix(frontend): avoid duplicate optimistic user message (#3002)

- `frontend/src/core/threads/hooks.ts`

## e7967a7f 2026-05-23 Admire
fix(frontend): hide copy for streaming assistant turn (#3176)

- `frontend/src/components/workspace/messages/message-list.tsx`
- `frontend/src/core/messages/utils.ts`

## 11dd5b06 2026-05-26 AochenShen99
fix(frontend): strip unclosed <think> tags from streaming AI content (#3218)

* fix(frontend): strip unclosed <think> tags from streaming AI content

During streaming, an opening <think> tag may arrive in one chunk
while the matching </think> arrives in a later chunk. The existing
splitInlineReasoning regex only matched fully closed pairs, so the
mid-flight reasoning was left in message.content and rendered into
the chat bubble via the markdown pipeline's rehypeRaw plugin until
the closing tag landed.

Extend splitInlineReasoning with a second pass: after stripping every
closed <think>...</think> pair, route any remaining content from a
lone opener to the reasoning slot and leave only the preceding
preamble in content. Closed-tag behavior is unchanged.

Covers every provider whose stream emits reasoning inline as <think>
tags (MiniMax streaming path, MindIE, PatchedChatOpenAI, and any
gateway-served DeepSeek/OpenAI-compatible model).

* style(frontend): apply prettier formatting to streaming reasoning tests

* fix(frontend): skip <think> split for literal think tags in inline code

Treats a `<think>` opener immediately preceded by a backtick as part of
markdown inline code rather than a streaming reasoning marker. Prevents
permanent content truncation when an AI message documents the `<think>`
tag literally (e.g. ``Use `<think>` markers``), where the streaming-safe
fallback would otherwise route the rest of the answer into the reasoning
panel because no `</think>` ever arrives.

Adds regression tests for both the post-stream and mid-stream cases.

- `frontend/src/core/messages/utils.ts`
  L275: // First pass: strip every fully closed `<think>...</think>` pair and
  L276: // collect its body as reasoning.
  L285: // Streaming-safe pass: a `<think>` opener whose `</think>` has not arrived
  L286: // yet means the rest of the chunk is reasoning in flight. Route it into the
  L287: // reasoning slot instead of letting it render as message content (the
  L288: // raw-HTML markdown pipeline would otherwise paint the inner text on
  L289: // screen until the closing tag lands).
  L290: //
  L291: // Skip when the opener sits right after a backtick — that is the model
  L292: // talking about `<think>` literally inside markdown inline code, not
  L293: // actually streaming reasoning.

## f68bcb77 2026-05-26 Admire
fix(frontend): guard message copy clipboard access (#3211)

* fix(frontend): guard message copy clipboard access

* fix(frontend): reuse clipboard guard across copy actions

- `frontend/src/components/ai-elements/code-block.tsx`
- `frontend/src/components/workspace/artifacts/artifact-file-detail.tsx`
- `frontend/src/components/workspace/copy-button.tsx`
- `frontend/src/components/workspace/recent-chat-list.tsx`
- `frontend/src/core/clipboard.ts`

## 02872407 2026-05-28 Xinmin Zeng
fix(frontend): show new thread in sidebar immediately on creation (#3276) (#3283)

When a user starts a new conversation, the sidebar list did not display
it until the AI finished streaming and generated a title. This made it
impossible to switch back to an in-progress conversation when working
with multiple threads concurrently.

Optimistically insert the new thread into the TanStack Query cache
during the `onCreated` callback so the sidebar renders a placeholder
entry ("New chat") as soon as the backend acknowledges thread creation.
The existing `onUpdateEvent` title handler and `onFinish` query
invalidation then update the entry in-place with the real title.

- `frontend/src/core/threads/hooks.ts`

## 737abc0e 2026-05-28 zgenu
fix: ignore stale run reconnect conflicts (#3284)

* fix: ignore stale run reconnect conflicts

* Potential fix for pull request finding

Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

* fix: ignore stale run reconnect conflicts

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>
Co-authored-by: Copilot Autofix powered by AI <175728472+Copilot@users.noreply.github.com>

- `frontend/src/core/api/api-client.ts`
  L55: // Match the gateway's store-only run response in
  L56: // backend/app/gateway/routers/thread_runs.py until the API exposes a
  L57: // structured error code for inactive run streams.
  L78: // Ignore storage access failures so reconnect cleanup never throws.

## 2fdfff0d 2026-05-28 Admire
fix(frontend): fix Mermaid preview failure in historical messages (#3196)

* fix(frontend): render historical mermaid diagrams

* fix(frontend): address mermaid review feedback

* Stabilize cancel lifecycle test

* fix(frontend): handle mermaid fence variants

* fix(frontend): normalize mermaid arrow spacing

* fix(frontend): handle mermaid CRLF fences

* chore: keep mermaid fix frontend-scoped

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `frontend/src/components/workspace/messages/markdown-content.tsx`
- `frontend/src/core/streamdown/index.ts`
- `frontend/src/core/streamdown/mermaid.ts`
- `frontend/src/core/streamdown/preprocess.ts`

## 2ace78d1 2026-05-28 Xinmin Zeng
fix(frontend): surface backend detail when agent name check fails (#3048)

* fix(frontend): surface backend detail when agent name check fails

The new-agent page caught AgentNameCheckError but only branched on
reason === "backend_unreachable". Everything else (notably the 422
"Invalid agent name '...'. Must match ^[A-Za-z0-9-]+$" response from
GET /api/agents/check when the user submits a name with disallowed
characters — trailing space, dot, Chinese, invisible whitespace from
copy-paste) fell through to the generic fallback "Could not verify
name availability — please try again", swallowing the detail that
already told the user exactly what to fix.

Add a request_failed branch that surfaces err.message (which
checkAgentName already populates from the backend's detail at
core/agents/api.ts). The disabled / backend_unreachable / unknown-
error paths are unchanged.

Pin the contract with unit tests covering: 200 success, fetch
rejection, 502/503/504 network errors, agents_api disabled detail,
422 validation detail carried verbatim, statusText fallback when
detail is absent, and a regression guard against misclassifying a
422 as agents_api disabled.

Closes #3041

* fix(frontend): localise the error prefix when surfacing backend detail

The previous commit surfaced the backend's raw `err.message` on the
new-agent page when the name check failed. The detail itself is
English (backend's `_validate_agent_name` text, any 5xx business
message, etc.) and dropping it bare into a zh-CN page produced a
jarring English-among-Chinese line that didn't match neighbouring
strings like "已存在同名智能体" / "无法验证名称可用性".

Add `nameStepCheckErrorWithDetail` as a templated string ("Name
check failed: {detail}" / "名称校验失败：{detail}"), mirroring the
existing `nameStepBootstrapMessage` `{name}` template pattern. The
page wraps `err.message` in it when present and falls back to the
plain `nameStepCheckError` when the detail is empty.

Rendered output (verified locally with a Console fetch mock that
returns 500 + detail):

  zh-CN: 名称校验失败：Database connection lost: SQLAlchemy connection
         pool exhausted (max 5 connections, all in use)
  en-US: Name check failed: Database connection lost: SQLAlchemy
         connection pool exhausted (max 5 connections, all in use)

The localised prefix tells the user *what operation* failed; the
raw detail tells them *why*. Translating the detail itself would
be lossy (any unbounded backend string would need a translation
table) and would break the debuggability the previous commit
delivered.

Refs #3041

* fix(frontend): distinguish backend detail from generated fallback in AgentNameCheckError

Addresses Copilot's review on #3048: the previous commits keyed off
`err.message`, but `checkAgentName` substitutes a generated fallback
string ("Failed to check agent name: ${statusText}") when the backend
sent no detail. That guaranteed `err.message` was always truthy, made
the `nameStepCheckError` fallback branch unreachable in practice, and
could surface awkward strings like "名称校验失败：Failed to check
agent name: Bad Gateway" in the UI.

Add an explicit `detail: string | null` field to AgentNameCheckError.
`checkAgentName` populates it only when the backend response actually
carried a string `detail` (defensive guard against the dict-shaped
detail that other deer-flow endpoints use for typed error codes).
The new-agent page now selects on `err.detail` instead of `err.message`
so the localised fallback wins when no real detail exists.

Also fix the prettier formatting that broke lint-frontend CI on the
previous push.

Test changes:
- The 422 carry-through test now asserts both `detail` and `message`
  hold the backend string verbatim.
- A new "falls back to statusText in message but leaves detail null"
  test pins the contract that no real detail ⇒ no UI surface leak.
- A new "treats non-string detail as null" test guards against future
  backend schema drift toward dict-shaped detail.

Refs #3041 #3048

- `frontend/src/app/workspace/agents/new/page.tsx`
  L153: // Surface the backend-provided detail (e.g. validation error) when
  L154: // one is present, wrapped in a localised prefix so zh-CN users
  L155: // don't see a bare English string next to the surrounding Chinese
  L156: // UI. Falls back to the generic localised fallback when the backend
  L157: // sent no detail — `err.message` is unreliable for this branch
  L158: // because `checkAgentName` substitutes a generated fallback string
  L159: // ("Failed to check agent name: ${statusText}") when `detail` is
  L160: // missing, so testing `err.message` would always be truthy and the
  L161: // generated fallback would leak through.
- `frontend/src/core/agents/api.ts`
  L12: /**
  L13: * Raw backend `detail` string when the failure came from a backend
  L14: * response carrying one. `null` when no detail was provided (e.g.
  L15: * network-layer failure, empty response body, unparseable body) — in
  L16: * which case `message` is a generated fallback like "Failed to check
  L17: * agent name: Bad Gateway" and the UI should prefer its own localized
  L18: * fallback instead of surfacing the generated string.
  L19: */
- `frontend/src/core/i18n/locales/en-US.ts`
- `frontend/src/core/i18n/locales/types.ts`
- `frontend/src/core/i18n/locales/zh-CN.ts`

## d46a5779 2026-05-29 Nan Gao
fix(chat): preserve messages after summarization (#3280)

* fix(chat): preserve messages after summarization

* make format

* fix(chat): address summarization review comments

- `frontend/src/core/threads/hooks.ts`
  L81: // This is a UI-display dedupe rule, not a general LangChain message-stream
  L82: // contract. Hidden messages that share an identity with a visible message are
  L83: // treated as control messages for this merged view; hidden messages carrying
  L84: // independent tracing/task semantics should use a distinct id or a custom
  L85: // stream/state channel instead of relying on message dedupe preservation.
  L127: // Only visible live messages should trim overlapping history. Hidden messages
  L128: // are UI control messages in this path, not observability records; any hidden
  L129: // message that must survive as task/tracing data should use custom events or a
  L130: // separate state channel instead of participating in this overlap heuristic.

## 019bd16a 2026-06-01 Eilen Shin
fix: load paginated run history messages (#3305)

- `frontend/src/core/threads/hooks.ts`
- `frontend/src/core/threads/types.ts`

## 9a53f9df 2026-06-03 Huixin615
fix(frontend): preserve chronological order of thread history after context compression (#3354)

* fix(frontend): preserve chronological order of thread history after context compression

Iterate runs from newest to match backend `list_by_thread` (newest-first) and the prepend semantics of the history loader, so refreshed history renders in A→B→C→D→E→F order.

Fixes #3352

* fix(frontend): auto-continue loading runs with no visible messages after context compression

- `frontend/src/core/threads/hooks.ts`

## 1aac408d 2026-06-06 Nan Gao
fix upload file size contract (#3408)

- `frontend/src/core/uploads/api.ts`

## 9a5de8d6 2026-06-06 Nan Gao
fix(ux): remove Backspace shortcut for deleting prompt attachments (#3410)

* Remove backspace attachment deletion

* Fix the lint error

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `frontend/src/components/ai-elements/prompt-input.tsx`

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

- `frontend/src/components/workspace/messages/message-list.tsx`
- `frontend/src/core/tasks/subtask-result.ts`
  L11: /**
  L12: * Structured-status keys the backend stamps onto
  L13: * ``ToolMessage.additional_kwargs`` for every ``task`` tool result.
  L14: *
  L15: * The values mirror the Python contract in
  L16: * ``backend/packages/harness/deerflow/subagents/status_contract.py``
  L17: * (``SUBAGENT_STATUS_KEY`` / ``SUBAGENT_ERROR_KEY``). The cross-language
  L18: * fixture at ``contracts/subagent_status_contract.json`` pins both sides
  L19: * to the same values.
  L20: */
  L24: /**
  L25: * Map from the backend ``subagent_status`` value to the frontend
  L26: * {@link SubtaskStatus} enum. The frontend collapses ``cancelled`` /
  L27: * ``timed_out`` / ``polling_timed_out`` into ``failed`` because the
  L28: * subtask card only renders three pill states. The richer backend
  L29: * vocabulary still survives on ``error`` for tooling that wants the
  L30: * detail.
  L31: */
  L66: * Map a `task` tool result to a {@link SubtaskStatus}.
  L67: *
  ... (truncated)

## 7679f21e 2026-06-07 Xinmin Zeng
fix(frontend): truncate overflowing text in agent cards (#3391)

* fix(frontend): truncate overflowing text in agent cards

Long custom agent names, descriptions, skills and tool-group labels
overflowed the agent card and broke its layout (issue #3389). The title
already had `truncate`, but it never took effect: an ancestor flex
container lacked `min-w-0`, so the flex item refused to shrink below its
content width.

- Restore the truncation chain by adding `min-w-0` to the title's flex
  ancestors so `truncate` can finally take effect.
- Cap and ellipsize model / skill / tool-group badges via a small
  `TruncatedBadge` (`block max-w-full truncate`).
- Reveal the full value on hover, but only when the text is actually
  clipped (`TruncatedTooltip`, width + height detection), so names,
  descriptions and labels stay readable without popping redundant
  tooltips on short cards.

* fix(frontend): wrap unbreakable strings in agent card tooltips

A long token with no break opportunity (no spaces or hyphens) could still
overflow the tooltip horizontally. Add `break-words` next to the existing
`text-wrap` so such strings wrap instead of overflowing.

Addresses Copilot review feedback on tooltip wrapping robustness.

* fix(frontend): show agent card tooltips instantly

Drop the explicit `delayDuration` so card tooltips fall back to the
provider's default 0ms delay. Instant feedback is better UX for revealing
text that is already clipped, per maintainer review.

---------

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `frontend/src/components/workspace/agents/agent-card.tsx`
  L40: /**
  L41: * Reveals the full text in a tooltip ONLY when its trigger is actually clipped.
  L42: * Clipping is measured on pointer enter against the trigger's own box, covering
  L43: * both single-line `truncate` (width) and multi-line `line-clamp` (height), so
  L44: * untruncated content never pops a redundant tooltip.
  L45: */
  L77: /**
  L78: * Long, user-controlled labels (agent model, skills, tool groups) that must
  L79: * never break the card layout: width is capped to the parent and the text is
  L80: * truncated with an ellipsis, with the full value revealed on hover.
  L81: */

## 1651d1f1 2026-06-08 DanielWalnut
fix(frontend): restructure Memory settings toolbar into two rows (#3433)

The search input, filter tabs, and four action buttons were crammed into
a single horizontal row, which squeezed the search box into an unusable
sliver and truncated the "Summaries" filter tab to "Summarie".

Split the toolbar into two rows: search + filter tabs on the first,
actions on the second. The search input now keeps a usable min width,
filter tabs use whitespace-nowrap so they never truncate, and the
destructive "Clear all memory" button is pushed to the far right
(ml-auto) to separate it from the constructive actions.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

- `frontend/src/components/workspace/settings/memory-settings-page.tsx`

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

- `frontend/src/app/mock/api/skills/route.ts`

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

- `frontend/src/content/en/harness/middlewares.mdx`
  L221: Custom middlewares are passed to `make_lead_agent` via the `custom_middlewares` parameter in `build_middlewares`. They are injected immediately before `ClarificationMiddleware` at the end of the chain.

## 5b81588b 2026-06-09 Admire
fix(frontend): fallback Streamdown clipboard copy (#3397)

* fix(frontend): fallback streamdown clipboard copy

* fix(frontend): address clipboard fallback review

* fix(frontend): normalize clipboard fallback rejection

* fix(frontend): harden clipboard fallback install

* fix(frontend): clarify clipboard fallback errors

* fix(frontend): cover clipboard fallback edge cases

* fix(frontend): tighten clipboard fallback cleanup

* fix(frontend): reduce clipboard fallback copy window

* fix(frontend): guard clipboard item fallback install

* fix(frontend): clean up clipboard fallback on selection errors

* Address clipboard fallback review feedback

* fix(frontend): guard clipboard fallback install during SSR

- `frontend/src/components/ai-elements/message.tsx`
- `frontend/src/components/ai-elements/reasoning.tsx`
- `frontend/src/components/ai-elements/streamdown.tsx`
  L10: // Only patch browser globals in client context; skip during SSR
- `frontend/src/components/workspace/artifacts/artifact-file-detail.tsx`
- `frontend/src/components/workspace/messages/subtask-card.tsx`
- `frontend/src/components/workspace/settings/about-settings-page.tsx`
- `frontend/src/components/workspace/settings/memory-settings-page.tsx`
- `frontend/src/core/clipboard.ts`
  L113: /**
  L114: * Installs browser clipboard fallbacks for Streamdown copy controls by patching
  L115: * missing navigator.clipboard methods and ClipboardItem when the host permits it.
  L116: */
  L186: // The ClipboardItem fallback below is independent from navigator.clipboard.
  L220: // The ClipboardItem fallback below is independent from navigator.clipboard.

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

- `frontend/src/components/ai-elements/prompt-input.tsx`
- `frontend/src/components/workspace/input-box.tsx`
- `frontend/src/core/messages/utils.ts`
  L495: * Strip backend-injected human context tags from message content.
  L496: * Kept under its historical name because callers use it for uploaded-file
  L497: * display cleanup.
  L512: * - ``SkillActivationMiddleware`` → ``<slash_skill_activation>``

## 2b795265 2026-06-10 DanielWalnut
fix: align auth-disabled mode and mock history loading (#3471)

* fix: align auth-disabled mode and mock history loading

* fix: address auth-disabled review feedback

* test: cover auth-disabled backend contract

* style: format frontend tests

* fix: address follow-up review comments

- `frontend/src/core/auth/auth-disabled-user.ts`
- `frontend/src/core/auth/server.ts`
- `frontend/src/core/threads/hooks.ts`

## 5819bd8a 2026-06-10 Huixin615
fix(frontend): paginate workspace chat list beyond 50 threads (#3482) (#3485)

* fix(frontend): paginate workspace chat list beyond 50 threads (#3482)

The sidebar 'Recent chats' and /workspace/chats list were hard-capped
at the first 50 threads returned by threads.search. Replace the
single-shot useThreads() consumers with useInfiniteThreads() and add
an IntersectionObserver sentinel to each list so further pages are
fetched on demand.

In search mode on the chats page, the sentinel is replaced by an
explicit 'Load more' button to prevent the observer from draining the
entire backend list while the filtered view stays empty.

- Add useInfiniteThreads + page-size constant and pure cache helpers
  (map/filterInfiniteThreadsCache, getInfiniteThreadsNextPageParam)
- Mirror rename / delete / stream-finish updates into the new
  infinite cache so optimistic UI stays consistent
- Extend the e2e mock to honour limit/offset slicing
- Unit tests for the cache helpers and pagination boundary
- Playwright e2e covering chats page + sidebar load-more, and the
  search-mode guard against runaway auto-pagination
- Add en/zh i18n entries for the search-mode load-more button

Fixes #3482

* docs(frontend): clarify infinite-threads offset semantics and test post-delete invariant

- Add docstring to getInfiniteThreadsNextPageParam explaining that TanStack
  Query freezes the returned offset into pageParams once, so optimistic cache
  mutations that shrink page lengths (filterInfiniteThreadsCache on delete)
  cannot retroactively move the offset backwards. Delete/rename paths
  reconcile against the backend via invalidateQueries in onSettled.
- Add unit test covering the post-delete invariant.
- Fix misleading comment in thread-list-infinite-scroll.spec.ts: the
  thread-search mock does not sort by updated_at; it returns the array in
  the order provided.

Addresses Copilot CR comments on #3485.

* fix(frontend): mirror onCreated upsert into infinite cache; add sidebar Load-older button

Address review feedback on #3485:

- New upsertThreadInInfiniteCache helper; useThreadStream onCreated now
  upserts into both the legacy ['threads','search'] cache and the new
  infinite cache, so a freshly created thread appears in the sidebar
  immediately during streaming instead of only after the run finishes
  and onSettled invalidates the query. Restores parity with main.
- Sidebar Recent Chats now exposes a visible 'Load older chats' button
  alongside the IntersectionObserver sentinel, so keyboard-only users
  and environments where IO is unavailable can still reach older
  conversations.
- Add zh-CN / en-US / types entry for chats.loadOlderChats.
- Cover the new helper with 3 unit tests (no-op on uninitialised cache,
  prepend new thread to first page, merge with existing entry without
  duplication).

- `frontend/src/app/workspace/chats/page.tsx`
  L44: // Sentinel-based auto load-more for the unfiltered list (issue #3482).
  L45: // In search mode we deliberately do NOT auto-paginate, otherwise an empty
  L46: // filtered view would keep the sentinel in the viewport and drain the
  L47: // entire backend list one page at a time.  Searching falls back to an
  L48: // explicit button so users can still reach older conversations on demand.
- `frontend/src/components/workspace/recent-chat-list.tsx`
- `frontend/src/core/i18n/locales/en-US.ts`
- `frontend/src/core/i18n/locales/types.ts`
- `frontend/src/core/i18n/locales/zh-CN.ts`
- `frontend/src/core/threads/hooks.ts`

## b6fbf0d1 2026-06-11 Huixin615
fix(frontend): keep workspace interactive when SSR auth probe cannot reach gateway (#3493) (#3495)

* fix(frontend): keep workspace interactive when SSR auth probe cannot reach gateway (#3493)

When the SSR auth probe at /api/v1/auth/me times out or fails, the
workspace layout used to render a static fallback page without
AuthProvider or QueryClientProvider, making logout and every other
interaction non-functional until the gateway recovered.

Render the normal WorkspaceContent in 'gateway_unavailable' mode
instead, surfacing a polite offline banner that re-probes the gateway
in the background and hides itself the moment refreshUser() returns
an authenticated user. The probe is reentrancy-guarded so a slow
gateway cannot pile up parallel /auth/me requests.

Closes #3493

* fix(workspace): silent probe in offline banner to avoid /login redirect during gateway recovery (#3493)

The banner previously delegated retry probes to AuthProvider.refreshUser(),
which treats any 401 from /api/v1/auth/me as 'session expired' and
force-redirects to /login. During gateway recovery, the first few requests
may transiently return 401 before the gateway is fully ready, which would
incorrectly kick the user out — defeating the purpose of the offline banner.

Now the banner silently fetches /api/v1/auth/me itself and only delegates
to refreshUser() on 200 OK. Non-200 responses (401 / 5xx / network) are
swallowed and retried on the next interval tick, ensuring the user stays
logged in across short gateway outages.

Verified in Docker:
- docker pause deer-flow-gateway → banner appears, page interactive
- docker unpause deer-flow-gateway → banner auto-disappears within 10s,
  user remains on /workspace/chats/new with full session restored
- All 117 unit tests pass

* fix(workspace): fix banner polling leak and persistent 401 handling (#3493)
- Stop polling immediately after user recovery: add user to effect dependencies, cleanup interval when user !== null
- Handle persistent 401: trigger login redirect after 3 consecutive unauthorized responses
- Extract decision logic to pure helper, add 8 unit tests covering all critical paths

* fix(workspace): address CR feedback on gateway offline recovery (#3493)

- gateway-offline-banner-helpers: decrement (not reset) auth-failure
  streak on transient outcomes so a flapping gateway (401 alternating
  with 5xx) still converges on session-expired
- gateway-offline-banner: reuse probe response body to apply user
  directly via new AuthProvider.applyUser, halving the recovery burst
  against an already-struggling gateway
- gateway-offline-banner: extract classifyProbe into helpers for unit
  testability; log probe failures via console.warn instead of swallowing
- gateway-offline-fallback: new shared component used by both workspace
  and (auth) layouts so auth pages recover the same way the workspace
  does, fixing the lockup where bare static HTML had no AuthProvider
- AuthProvider.logout: fall back to hard navigation when the gateway
  logout fetch fails, matching legacy form-POST behaviour and avoiding
  stale client state during outage
- tests: extend gateway-offline-banner-helpers.test with flapping
  convergence and classifyProbe branch coverage (19 cases total)

- `frontend/src/app/(auth)/layout.tsx`
  L28: // Auth pages have no banner of their own, so render one here. The
  L29: // fallback's AuthProvider replaces the bare-HTML branch that
  L30: // previously locked users out without any logout/retry capability.
- `frontend/src/app/workspace/layout.tsx`
  L31: // GatewayOfflineFallback supplies the AuthProvider; WorkspaceContent
  L32: // already mounts the banner inside its sidebar layout, so renderBanner
  L33: // stays false here to avoid double-mounting.
- `frontend/src/app/workspace/workspace-content.tsx`
- `frontend/src/components/workspace/gateway-offline-banner-helpers.ts`
  L3: /**
  L4: * Number of consecutive 401 responses before treating the session as
  L5: * expired and delegating to AuthProvider.refreshUser() for /login redirect.
  L6: *
  L7: * Threshold > 1 absorbs transient 401s that may occur in the first few
  L8: * milliseconds after a gateway becomes ready again, without indefinitely
  L9: * masking a genuinely expired cookie.
  L10: */
  L22: /** Categorised outcome of a single /auth/me probe. */
  L28: /** Next action the banner effect should take after a probe. */
  L34: /**
  L35: * Pure: classify an HTTP probe outcome into ProbeOutcome.
  L36: *
  L37: * Extracted from the banner effect so it can be unit-tested independently.
  L38: * `parsedUser` is the JSON body of a 2xx response (or null if absent/malformed);
  L39: * surfacing it through ProbeOutcome lets the caller apply it directly instead
  L40: * of paying for a second /auth/me round-trip via refreshUser().
  L41: */
  L54: /**
  L55: * Pure state machine for what to do after a probe lands.
  ... (truncated)
- `frontend/src/components/workspace/gateway-offline-banner.tsx`
  L17: /**
  L18: * True when the server-side auth probe at `/api/v1/auth/me` could not
  L19: * reach the gateway. The banner stays mounted until a client-side probe
  L20: * confirms the gateway is healthy and `user` becomes populated.
  L21: */
  L30: // Guard against piling up probe calls while the gateway is still slow.
  L32: // Count consecutive 401s so we can distinguish "transient warm-up 401"
  L33: // from "session actually expired" and avoid lying with the banner.
  L38: // Once AuthProvider has a user again the banner has served its
  L39: // purpose; tear down the polling so we don't keep probing every 10s
  L40: // for the entire lifetime of the page (gatewayUnavailable is a
  L41: // server-rendered prop and stays true until a full reload).
  L55: // Reuse the probe's own response body instead of triggering a
  L56: // second /auth/me request via refreshUser() — halves the recovery
  L57: // burst against an already-struggling gateway.
  L88: // Hand off to AuthProvider, which on 401 will /login-redirect.
- `frontend/src/components/workspace/gateway-offline-fallback.tsx`
  L8: /**
  L9: * When true, this component renders its own banner. The workspace layout
  L10: * sets this to false because WorkspaceContent already mounts the banner
  L11: * inside its sidebar layout. The (auth) layout sets it to true because
  L12: * its plain children have no banner of their own.
  L13: */
  L18: /**
  L19: * Shared fallback shown by both the workspace and (auth) layouts when the
  L20: * server-side auth probe could not reach the gateway. Wraps the children
  L21: * with an AuthProvider so the banner's probe / logout / refresh hooks work
  L22: * — fixing the `(auth)/layout.tsx` lockup where the bare static HTML had
  L23: * no AuthProvider / QueryClientProvider and the user could not recover
  L24: * without a manual reload.
  L25: */
- `frontend/src/core/auth/AuthProvider.tsx`
  L56: /**
  L57: * Apply a user value supplied by a caller (e.g. banner probe) that has
  L58: * already fetched it. Equivalent to setUser, exposed with a stable name
  L59: * so consumers don't reach into React internals.
  L60: */
  L100: *
  L101: * When the gateway is unreachable the fetch silently fails — the SPA
  L102: * router.push("/") would leave the user on "/" still holding stale
  L103: * React state and any in-flight SSE / fetch / query subscriptions.
  L104: * We therefore fall back to a hard navigation (window.location.href),
  L105: * which discards all client state the same way the legacy form-POST
  L106: * logout used to.
  L130: // Hard navigation ensures every in-flight subscription is torn down,
  L131: // matching the legacy form-POST logout behaviour during a gateway outage.
- `frontend/src/core/i18n/locales/en-US.ts`
- `frontend/src/core/i18n/locales/types.ts`
- `frontend/src/core/i18n/locales/zh-CN.ts`

## c733d3c9 2026-06-11 zgenu
fix(frontend): isolate new chat thread messages (#3508)

* fix(frontend): isolate new chat thread messages

* fix(frontend): keep live messages visible in new chat

* fix(frontend): reset thread-local message refs

- `frontend/src/app/workspace/agents/[agent_name]/chats/[thread_id]/page.tsx`
- `frontend/src/app/workspace/chats/[thread_id]/page.tsx`
- `frontend/src/components/workspace/chats/use-thread-chat.ts`
- `frontend/src/core/threads/hooks.ts`
  L411: // Optimistic messages shown before the server stream responds.

## 0367fe6c 2026-06-11 snaplap
fix(frontend): prevent user message bubble overflow with long unbreakable strings (#3488)

- Add max-w-full min-w-0 to user message wrapper div to constrain width
- Change bubble width from w-fit to w-full max-w-full for consistent layout
- Add break-words to user message content for long string wrapping
- Add overflow-x-clip as defensive overflow protection

Co-authored-by: Willem Jiang <willem.jiang@gmail.com>

- `frontend/src/components/workspace/messages/message-list-item.tsx`

