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

- `backend/app/gateway/auth/errors.py`
- `backend/app/gateway/auth/local_provider.py`
  L82: """Return number of admin users."""
- `backend/app/gateway/auth/repositories/base.py`
  L88: """Return number of users with system_role == 'admin'."""
- `backend/app/gateway/auth/repositories/sqlite.py`

## 00a90bbd 2026-04-12 foreleven
refactor: Remove init_token handling from admin initialization logic and related tests

- `backend/app/gateway/auth/errors.py`

## 653b7ae1 2026-04-26 Willem Jiang
Apply the code reviewer suggestion of abstractmethod

- `backend/app/gateway/auth/providers.py`
- `backend/app/gateway/auth/repositories/base.py`

## ac18b9c4 2026-04-26 Willem Jiang
Apply the code reviewer suggestion of abstractmethod

- `backend/app/gateway/auth/repositories/base.py`

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

## f734e14d 2026-05-12 greatmengqi
docs: document auth design and user isolation (#2913)

* docs: document auth design and user isolation

* docs: align auth docs with current storage and reset behavior

---------

Co-authored-by: greatmengqi <chenmengqi.0376@bytedance.com>

- `backend/app/gateway/auth/models.py`

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

