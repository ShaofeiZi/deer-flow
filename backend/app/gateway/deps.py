"""Centralized accessors for singleton objects stored on ``app.state``.

**Getters** (used by routers): raise 503 when a required dependency is
missing, except ``get_store`` which returns ``None``.

``AppConfig`` is intentionally *not* cached on ``app.state``. Routers and the
run path resolve it through :func:`deerflow.config.app_config.get_app_config`,
which performs mtime-based hot reload, so edits to ``config.yaml`` take
effect on the next request without a process restart. The engines created in
:func:`langgraph_runtime` (stream bridge, persistence, checkpointer, store,
run-event store) accept a ``startup_config`` snapshot — they are
restart-required by design and stay bound to that snapshot to keep the live
process consistent with itself.

Initialization is handled directly in ``app.py`` via :class:`AsyncExitStack`.
| ``app.state`` 上存储的单例对象的集中访问器。

**Getters**（由路由器使用）：当所需依赖缺失时抛出 503，除了 ``get_store`` 返回 ``None``。

``AppConfig`` 有意 *不* 缓存在 ``app.state`` 上。路由器和运行路径通过
:func:`deerflow.config.app_config.get_app_config` 解析它，
该函数执行基于 mtime 的热重载，因此对 ``config.yaml`` 的编辑在下一个请求时生效，
无需进程重启。在 :func:`langgraph_runtime` 中创建的引擎
（stream bridge、persistence、checkpointer、store、run-event store）
接受 ``startup_config`` 快照 — 它们按设计需要重启，并绑定到该快照以保持活动进程自身一致。

初始化直接在 ``app.py`` 中通过 :class:`AsyncExitStack` 处理。
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import AsyncExitStack, asynccontextmanager
from typing import TYPE_CHECKING, TypeVar, cast

from fastapi import FastAPI, HTTPException, Request
from langgraph.types import Checkpointer

from deerflow.config.app_config import AppConfig, get_app_config
from deerflow.persistence.feedback import FeedbackRepository
from deerflow.runtime import RunContext, RunManager, StreamBridge
from deerflow.runtime.events.store.base import RunEventStore
from deerflow.runtime.runs.store.base import RunStore

logger = logging.getLogger(__name__)

# Upper bound (seconds) for draining in-flight runs during shutdown, before the
# AsyncExitStack tears down the checkpointer (and its connection pool). Kept
# local to avoid an app -> deps -> app import cycle. This is a *separate* budget
# from ``app.gateway.app._SHUTDOWN_HOOK_TIMEOUT_SECONDS`` (currently also 5.0s,
# which bounds channel-service stop): the two govern independent teardown steps
# and may diverge, but both count toward the lifespan shutdown window — revisit
# them together if their sum must stay within the server's graceful-shutdown
# timeout.
# | 关闭期间排空进行中运行的上限（秒），在 AsyncExitStack 拆除 checkpointer（及其连接池）之前。
# 保持为局部变量以避免 app -> deps -> app 的导入循环。这是一个 *独立* 的预算，
# 与 ``app.gateway.app._SHUTDOWN_HOOK_TIMEOUT_SECONDS``（目前也是 5.0s，用于限制 channel-service 停止）不同：
# 两者管理独立的拆除步骤，可能有所不同，但都计入 lifespan 关闭窗口 —
# 如果它们的总和必须保持在服务器的优雅关闭超时内，请一起重新审视。
_RUN_DRAIN_TIMEOUT_SECONDS = 5.0


async def _drain_inflight_runs(run_manager: RunManager) -> None:
    """Drain in-flight runs before the checkpointer is torn down (issue #3373).

    Shields the (internally-bounded) drain so that even if the lifespan
    coroutine is itself cancelled mid-shutdown — a second SIGINT or the server's
    graceful-shutdown timeout, i.e. the same signal storm behind #3373 — the
    checkpointer pool is not closed while run tasks are still writing
    checkpoints. On such a cancellation we let the already-running drain finish
    (it is bounded by ``RunManager.shutdown``'s own timeout) and then propagate
    the cancellation.

    在 checkpointer 被拆除之前排空进行中的运行（issue #3373）。
    保护（内部有界的）排空操作，即使 lifespan 协程本身在关闭过程中被取消 —
    第二次 SIGINT 或服务器的优雅关闭超时，即 #3373 背后的同一信号风暴 —
    checkpointer 池不会在运行任务仍在写入检查点时被关闭。
    在这种取消情况下，我们让已经在运行的排空操作完成
    （它受 ``RunManager.shutdown`` 自身超时的限制），然后传播取消。
    """
    drain = asyncio.create_task(run_manager.shutdown(timeout=_RUN_DRAIN_TIMEOUT_SECONDS))
    try:
        await asyncio.shield(drain)
    except asyncio.CancelledError:
        # Re-shield so this second wait does not abandon the in-flight drain;
        # it is bounded, so this cannot hang. Then re-raise to honour shutdown.
        # | 重新 shield，使第二次等待不会放弃进行中的排空操作；
        # 它是有界的，所以不会挂起。然后重新抛出以遵守关闭。
        try:
            await asyncio.shield(drain)
        except Exception:
            logger.exception("In-flight run drain failed after shutdown cancellation")
        raise
    except Exception:
        logger.exception("Failed to drain in-flight runs during shutdown")


if TYPE_CHECKING:
    from app.gateway.auth.local_provider import LocalAuthProvider
    from app.gateway.auth.repositories.sqlite import SQLiteUserRepository
    from deerflow.persistence.thread_meta.base import ThreadMetaStore
    from deerflow.runtime import RunRecord


T = TypeVar("T")


async def _mark_latest_recovered_threads_error(
    run_manager: RunManager,
    thread_store: ThreadMetaStore,
    recovered_runs: list[RunRecord],
) -> None:
    """Mark thread status as error only when its newest run was recovered.

    仅当线程的最新运行被恢复时，才将线程状态标记为 error。
    """
    recovered_by_thread: dict[str, set[str]] = {}
    for record in recovered_runs:
        recovered_by_thread.setdefault(record.thread_id, set()).add(record.run_id)

    for thread_id, recovered_run_ids in recovered_by_thread.items():
        try:
            latest_runs = await run_manager.list_by_thread(thread_id, user_id=None, limit=1)
        except Exception:
            logger.warning("Failed to find latest run for thread %s during run reconciliation", thread_id, exc_info=True)
            continue
        if not latest_runs or latest_runs[0].run_id not in recovered_run_ids:
            continue
        try:
            await thread_store.update_status(thread_id, "error", user_id=None)
        except Exception:
            logger.warning("Failed to mark thread %s as error during run reconciliation", thread_id, exc_info=True)


def get_config() -> AppConfig:
    """Return the freshest ``AppConfig`` for the current request.

    Routes through :func:`deerflow.config.app_config.get_app_config`, which
    honours runtime ``ContextVar`` overrides and reloads ``config.yaml`` from
    disk when its mtime changes. ``AppConfig`` is not cached on ``app.state``
    at all — the only startup-time snapshot lives as a local
    ``startup_config`` variable inside ``lifespan()`` and is passed
    explicitly into :func:`langgraph_runtime` for the engines that are
    restart-required by design. Routing every request through
    :func:`get_app_config` closes the bytedance/deer-flow issue #3107 BUG-001
    split-brain where the worker / lead-agent thread saw a stale startup
    snapshot.

    Hot-reload boundary: fields backed by startup-time singletons
    (engines, sandbox provider, IM channels, logging handler) require a
    process restart to change at runtime. The authoritative list lives in
    :mod:`deerflow.config.reload_boundary` and is mirrored by the
    standardised ``"startup-only:"`` prefix on the matching
    ``Field(description=...)`` in :class:`AppConfig` — IDE hover on those
    fields will surface the boundary inline. See
    ``backend/CLAUDE.md`` "Config Hot-Reload Boundary" for the operator
    summary.

    Any failure to materialise the config (missing file, permission denied,
    YAML parse error, validation error) is reported as 503 — semantically
    "the gateway cannot serve requests without a usable configuration" — and
    logged with the original exception so operators have something to debug.

    返回当前请求的最新 ``AppConfig``。
    通过 :func:`deerflow.config.app_config.get_app_config` 路由，
    该函数遵循运行时 ``ContextVar`` 覆盖，并在 ``config.yaml`` 的 mtime 变化时从磁盘重新加载。
    ``AppConfig`` 完全不缓存在 ``app.state`` 上 — 唯一的启动时快照
    作为局部 ``startup_config`` 变量存在于 ``lifespan()`` 内部，
    并显式传递给 :func:`langgraph_runtime` 用于按设计需要重启的引擎。
    每个请求都通过 :func:`get_app_config` 路由，修复了 bytedance/deer-flow issue #3107 BUG-001
    的分裂脑问题，即 worker / lead-agent 线程看到的是过时的启动快照。

    热重载边界：由启动时单例支持的字段（引擎、sandbox provider、IM channels、logging handler）
    需要进程重启才能在运行时更改。权威列表位于
    :mod:`deerflow.config.reload_boundary`，并通过 :class:`AppConfig` 中
    匹配的 ``Field(description=...)`` 上的标准化 ``"startup-only:"`` 前缀镜像 —
    在这些字段上 IDE 悬停将内联显示边界。参见
    ``backend/CLAUDE.md`` "Config Hot-Reload Boundary" 了解运维摘要。

    任何无法获取配置的失败（文件缺失、权限拒绝、YAML 解析错误、验证错误）
    都报告为 503 — 语义上表示"网关没有可用配置无法服务请求" —
    并记录原始异常以便运维人员调试。
    """
    try:
        return get_app_config()
    except Exception as exc:  # noqa: BLE001 - request boundary: log and degrade gracefully
        logger.exception("Failed to load AppConfig at request time")
        raise HTTPException(status_code=503, detail="Configuration not available") from exc


@asynccontextmanager
async def langgraph_runtime(app: FastAPI, startup_config: AppConfig) -> AsyncGenerator[None, None]:
    """Bootstrap and tear down all LangGraph runtime singletons.

    ``startup_config`` is the ``AppConfig`` snapshot taken once during
    ``lifespan()`` for one-shot infrastructure bootstrap. The engines and
    stores constructed here (stream bridge, persistence engine, checkpointer,
    store, run-event store) are restart-required by design — they hold live
    connections, file handles, or singleton providers — so they bind to this
    snapshot and survive across `config.yaml` edits. Request-time consumers
    must still go through :func:`get_config` for any field that should be
    hot-reloadable. See ``backend/CLAUDE.md`` "Config Hot-Reload Boundary".

    The matching ``run_events_config`` is frozen onto ``app.state`` so
    :func:`get_run_context` pairs a freshly-loaded ``AppConfig`` with the
    *startup-time* run-events configuration the underlying ``event_store``
    was built from — otherwise the runtime could end up combining a live
    new ``run_events_config`` with an event store still bound to the
    previous backend.

    Usage in ``app.py``::

        async with langgraph_runtime(app, startup_config):
            yield

    启动和拆除所有 LangGraph 运行时单例。
    ``startup_config`` 是在 ``lifespan()`` 期间获取一次的 ``AppConfig`` 快照，
    用于一次性基础设施启动。此处构建的引擎和存储
    （stream bridge、persistence engine、checkpointer、store、run-event store）
    按设计需要重启 — 它们持有活跃连接、文件句柄或单例 provider —
    因此它们绑定到此快照并在 `config.yaml` 编辑后继续存在。
    请求时消费者仍必须通过 :func:`get_config` 获取任何应可热重载的字段。
    参见 ``backend/CLAUDE.md`` "Config Hot-Reload Boundary"。

    匹配的 ``run_events_config`` 被冻结到 ``app.state`` 上，
    以便 :func:`get_run_context` 将新加载的 ``AppConfig`` 与底层 ``event_store``
    构建时所基于的 *启动时* run-events 配置配对 —
    否则运行时可能最终将活跃的新 ``run_events_config``
    与仍绑定到先前后端的 event store 组合在一起。

    ``app.py`` 中的用法::

        async with langgraph_runtime(app, startup_config):
            yield
    """
    from deerflow.persistence.engine import close_engine, get_session_factory, init_engine_from_config
    from deerflow.runtime import make_store, make_stream_bridge
    from deerflow.runtime.checkpointer.async_provider import make_checkpointer
    from deerflow.runtime.events.store import make_run_event_store

    async with AsyncExitStack() as stack:
        config = startup_config

        app.state.stream_bridge = await stack.enter_async_context(make_stream_bridge(config))

        # Initialize persistence engine BEFORE checkpointer so that
        # auto-create-database logic runs first (postgres backend).
        # | 在 checkpointer 之前初始化 persistence engine，
        # 以便 auto-create-database 逻辑先运行（postgres 后端）。
        await init_engine_from_config(config.database)

        app.state.checkpointer = await stack.enter_async_context(make_checkpointer(config))
        app.state.store = await stack.enter_async_context(make_store(config))

        # Initialize repositories — one get_session_factory() call for all.
        # | 初始化 repositories — 一次 get_session_factory() 调用供所有使用。
        sf = get_session_factory()
        if sf is not None:
            from deerflow.persistence.feedback import FeedbackRepository
            from deerflow.persistence.run import RunRepository

            app.state.run_store = RunRepository(sf)
            app.state.feedback_repo = FeedbackRepository(sf)
        else:
            from deerflow.runtime.runs.store.memory import MemoryRunStore

            app.state.run_store = MemoryRunStore()
            app.state.feedback_repo = None

        from deerflow.persistence.thread_meta import make_thread_store

        app.state.thread_store = make_thread_store(sf, app.state.store)

        # Run event store. The store and the matching ``run_events_config`` are
        # both frozen at startup so ``get_run_context`` does not combine a
        # freshly-reloaded ``AppConfig.run_events`` with a store still bound to
        # the previous backend.
        # | Run event store。store 和匹配的 ``run_events_config`` 都在启动时冻结，
        # 以便 ``get_run_context`` 不会将新重载的 ``AppConfig.run_events``
        # 与仍绑定到先前后端的 store 组合在一起。
        run_events_config = getattr(config, "run_events", None)
        app.state.run_events_config = run_events_config
        app.state.run_event_store = make_run_event_store(run_events_config)

        # RunManager with store backing for persistence
        # | RunManager 带 store 支持持久化
        app.state.run_manager = RunManager(store=app.state.run_store)
        if getattr(config.database, "backend", None) == "sqlite":
            from deerflow.utils.time import now_iso

            # Startup-only recovery: clean shutdowns return no active rows and
            # the thread-status update below becomes a no-op.
            # | 仅启动时恢复：干净关闭不会返回活跃行，
            # 下面的 thread-status 更新将变为空操作。
            recovered_runs = await app.state.run_manager.reconcile_orphaned_inflight_runs(
                error="Gateway restarted before this run reached a durable final state.",
                before=now_iso(),
            )
            await _mark_latest_recovered_threads_error(app.state.run_manager, app.state.thread_store, recovered_runs)

        try:
            yield
        finally:
            # Drain in-flight run tasks BEFORE the AsyncExitStack tears down the
            # checkpointer (and its connection pool). A run still mid-graph would
            # otherwise leak into asyncio.run() shutdown, where langgraph's
            # _checkpointer_put_after_previous aput races the closed pool and
            # raises PoolClosed (issue #3373).
            # | 在 AsyncExitStack 拆除 checkpointer（及其连接池）*之前* 排空进行中的运行任务。
            # 否则仍在图中的运行会泄漏到 asyncio.run() 关闭中，
            # 在那里 langgraph 的 _checkpointer_put_after_previous aput 与已关闭的池竞争
            # 并引发 PoolClosed（issue #3373）。
            run_manager = getattr(app.state, "run_manager", None)
            if run_manager is not None:
                await _drain_inflight_runs(run_manager)
            await close_engine()


# ---------------------------------------------------------------------------
# Getters – called by routers per-request
# | Getters – 由路由器按请求调用
# ---------------------------------------------------------------------------


def _require(attr: str, label: str) -> Callable[[Request], T]:
    """Create a FastAPI dependency that returns ``app.state.<attr>`` or 503.

    创建一个 FastAPI 依赖项，返回 ``app.state.<attr>`` 或 503。
    """

    def dep(request: Request) -> T:
        val = getattr(request.app.state, attr, None)
        if val is None:
            raise HTTPException(status_code=503, detail=f"{label} not available")
        return cast(T, val)

    dep.__name__ = dep.__qualname__ = f"get_{attr}"
    return dep


get_stream_bridge: Callable[[Request], StreamBridge] = _require("stream_bridge", "Stream bridge")
get_run_manager: Callable[[Request], RunManager] = _require("run_manager", "Run manager")
get_checkpointer: Callable[[Request], Checkpointer] = _require("checkpointer", "Checkpointer")
get_run_event_store: Callable[[Request], RunEventStore] = _require("run_event_store", "Run event store")
get_feedback_repo: Callable[[Request], FeedbackRepository] = _require("feedback_repo", "Feedback")
get_run_store: Callable[[Request], RunStore] = _require("run_store", "Run store")


def get_store(request: Request):
    """Return the global store (may be ``None`` if not configured).

    返回全局 store（如果未配置则可能为 ``None``）。
    """
    return getattr(request.app.state, "store", None)


def get_thread_store(request: Request) -> ThreadMetaStore:
    """Return the thread metadata store (SQL or memory-backed).

    返回线程元数据存储（SQL 或内存支持）。
    """
    val = getattr(request.app.state, "thread_store", None)
    if val is None:
        raise HTTPException(status_code=503, detail="Thread metadata store not available")
    return val


def get_run_context(request: Request) -> RunContext:
    """Build a :class:`RunContext` from ``app.state`` singletons.

    Returns a *base* context with infrastructure dependencies. The
    ``app_config`` field is resolved live so per-run fields (e.g.
    ``models[*].max_tokens``) follow ``config.yaml`` edits; the
    ``event_store`` / ``run_events_config`` pair stays frozen to the snapshot
    captured in :func:`langgraph_runtime` so callers never see a store bound
    to one backend paired with a config pointing at another.

    从 ``app.state`` 单例构建 :class:`RunContext`。
    返回带有基础设施依赖的 *基础* 上下文。
    ``app_config`` 字段是实时解析的，因此每次运行的字段（例如
    ``models[*].max_tokens``）会跟随 ``config.yaml`` 的编辑；
    ``event_store`` / ``run_events_config`` 对保持冻结到
    :func:`langgraph_runtime` 中捕获的快照，因此调用者永远不会看到
    绑定到一个后端的 store 与指向另一个后端的 config 配对。
    """
    return RunContext(
        checkpointer=get_checkpointer(request),
        store=get_store(request),
        event_store=get_run_event_store(request),
        run_events_config=getattr(request.app.state, "run_events_config", None),
        thread_store=get_thread_store(request),
        app_config=get_config(),
    )


# ---------------------------------------------------------------------------
# Auth helpers (used by authz.py and auth middleware)
# | Auth 辅助函数（由 authz.py 和 auth middleware 使用）
# ---------------------------------------------------------------------------

# Cached singletons to avoid repeated instantiation per request
# | 缓存的单例，避免每次请求重复实例化
_cached_local_provider: LocalAuthProvider | None = None
_cached_repo: SQLiteUserRepository | None = None


def get_local_provider() -> LocalAuthProvider:
    """Get or create the cached LocalAuthProvider singleton.

    Must be called after ``init_engine_from_config()`` — the shared
    session factory is required to construct the user repository.

    获取或创建缓存的 LocalAuthProvider 单例。
    必须在 ``init_engine_from_config()`` 之后调用 — 需要共享的 session factory 来构建用户 repository。
    """
    global _cached_local_provider, _cached_repo
    if _cached_repo is None:
        from app.gateway.auth.repositories.sqlite import SQLiteUserRepository
        from deerflow.persistence.engine import get_session_factory

        sf = get_session_factory()
        if sf is None:
            raise RuntimeError("get_local_provider() called before init_engine_from_config(); cannot access users table")
        _cached_repo = SQLiteUserRepository(sf)
    if _cached_local_provider is None:
        from app.gateway.auth.local_provider import LocalAuthProvider

        _cached_local_provider = LocalAuthProvider(repository=_cached_repo)
    return _cached_local_provider


async def get_current_user_from_request(request: Request):
    """Get the current authenticated user from the request cookie.

    Raises HTTPException 401 if not authenticated.

    从请求 cookie 中获取当前已认证用户。
    如果未认证则抛出 HTTPException 401。
    """
    state = getattr(request, "state", None)
    state_user = getattr(state, "user", None)
    from app.gateway.auth_disabled import AUTH_SOURCE_AUTH_DISABLED, AUTH_SOURCE_INTERNAL, AUTH_SOURCE_SESSION

    if state_user is not None and getattr(state, "auth_source", None) in {
        AUTH_SOURCE_SESSION,
        AUTH_SOURCE_AUTH_DISABLED,
        AUTH_SOURCE_INTERNAL,
    }:
        return state_user

    from app.gateway.auth import decode_token
    from app.gateway.auth.errors import AuthErrorCode, AuthErrorResponse, TokenError, token_error_to_code

    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=401,
            detail=AuthErrorResponse(code=AuthErrorCode.NOT_AUTHENTICATED, message="Not authenticated").model_dump(),
        )

    payload = decode_token(access_token)
    if isinstance(payload, TokenError):
        raise HTTPException(
            status_code=401,
            detail=AuthErrorResponse(code=token_error_to_code(payload), message=f"Token error: {payload.value}").model_dump(),
        )

    provider = get_local_provider()
    user = await provider.get_user(payload.sub)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail=AuthErrorResponse(code=AuthErrorCode.USER_NOT_FOUND, message="User not found").model_dump(),
        )

    # Token version mismatch → password was changed, token is stale
    # | Token 版本不匹配 → 密码已更改，token 已过期
    if user.token_version != payload.ver:
        raise HTTPException(
            status_code=401,
            detail=AuthErrorResponse(code=AuthErrorCode.TOKEN_INVALID, message="Token revoked (password changed)").model_dump(),
        )

    return user


async def get_optional_user_from_request(request: Request):
    """Get optional authenticated user from request.

    Returns None if not authenticated.

    从请求中获取可选的已认证用户。
    如果未认证则返回 None。
    """
    try:
        return await get_current_user_from_request(request)
    except HTTPException:
        return None


async def get_current_user(request: Request) -> str | None:
    """Extract user_id from request cookie, or None if not authenticated.

    Thin adapter that returns the string id for callers that only need
    identification (e.g., ``feedback.py``). Full-user callers should use
    ``get_current_user_from_request`` or ``get_optional_user_from_request``.

    从请求 cookie 中提取 user_id，如果未认证则返回 None。
    薄适配器，为只需要标识的调用者（例如 ``feedback.py``）返回字符串 id。
    需要完整用户信息的调用者应使用 ``get_current_user_from_request`` 或 ``get_optional_user_from_request``。
    """
    user = await get_optional_user_from_request(request)
    return str(user.id) if user else None
