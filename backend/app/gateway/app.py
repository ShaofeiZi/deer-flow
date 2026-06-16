import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.gateway.auth_disabled import warn_if_auth_disabled_enabled
from app.gateway.auth_middleware import AuthMiddleware
from app.gateway.config import get_gateway_config
from app.gateway.csrf_middleware import CSRFMiddleware, get_configured_cors_origins
from app.gateway.deps import langgraph_runtime
from app.gateway.routers import (
    agents,
    artifacts,
    assistants_compat,
    auth,
    channels,
    feedback,
    mcp,
    memory,
    models,
    runs,
    skills,
    suggestions,
    thread_runs,
    threads,
    uploads,
)
from deerflow.config import app_config as deerflow_app_config
from deerflow.config.app_config import apply_logging_level

AppConfig = deerflow_app_config.AppConfig
get_app_config = deerflow_app_config.get_app_config

# Default logging; lifespan overrides from config.yaml log_level.
# | 默认日志；lifespan 从 config.yaml log_level 覆盖。
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# Upper bound (seconds) each lifespan shutdown hook is allowed to run.
# Bounds worker exit time so uvicorn's reload supervisor does not keep
# firing signals into a worker that is stuck waiting for shutdown cleanup.
# | 每个 lifespan 关闭钩子允许运行的上限（秒）。
# 限制 worker 退出时间，使 uvicorn 的重载监督器不会持续向
# 卡在等待关闭清理的 worker 发送信号。
_SHUTDOWN_HOOK_TIMEOUT_SECONDS = 5.0


async def _ensure_admin_user(app: FastAPI) -> None:
    """Startup hook: handle first boot and migrate orphan threads otherwise.

    After admin creation, migrate orphan threads from the LangGraph
    store (metadata.user_id unset) to the admin account. This is the
    "no-auth → with-auth" upgrade path: users who ran DeerFlow without
    authentication have existing LangGraph thread data that needs an
    owner assigned.
        First boot (no admin exists):
            - Does NOT create any user accounts automatically.
            - The operator must visit ``/setup`` to create the first admin.

    Subsequent boots (admin already exists):
      - Runs the one-time "no-auth → with-auth" orphan thread migration for
        existing LangGraph thread metadata that has no user_id.

    No SQL persistence migration is needed: the four user_id columns
    (threads_meta, runs, run_events, feedback) only come into existence
    alongside the auth module via create_all, so freshly created tables
    never contain NULL-owner rows.

    启动钩子：处理首次启动，否则迁移孤立线程。
    在 admin 创建后，将 LangGraph store 中的孤立线程
    （metadata.user_id 未设置）迁移到 admin 账户。这是
    "no-auth → with-auth" 升级路径：在无认证状态下运行 DeerFlow 的用户
    有现有的 LangGraph 线程数据需要分配所有者。
        首次启动（无 admin 存在）：
            - 不会自动创建任何用户账户。
            - 运维人员必须访问 ``/setup`` 创建第一个 admin。

    后续启动（admin 已存在）：
      - 对没有 user_id 的现有 LangGraph 线程元数据
        运行一次性 "no-auth → with-auth" 孤立线程迁移。

    不需要 SQL 持久化迁移：四个 user_id 列
    （threads_meta、runs、run_events、feedback）仅与 auth 模块
    一起通过 create_all 创建，因此新创建的表永远不会包含 NULL-owner 行。
    """
    from sqlalchemy import select

    from app.gateway.deps import get_local_provider
    from deerflow.persistence.engine import get_session_factory
    from deerflow.persistence.user.model import UserRow

    try:
        provider = get_local_provider()
    except RuntimeError:
        # Auth persistence may not be initialized in some test/boot paths.
        # Skip admin migration work rather than failing gateway startup.
        # | Auth 持久化可能在某些测试/启动路径中未初始化。
        # 跳过 admin 迁移工作而不是让网关启动失败。
        logger.warning("Auth persistence not ready; skipping admin bootstrap check")
        return

    sf = get_session_factory()
    if sf is None:
        return

    admin_count = await provider.count_admin_users()

    if admin_count == 0:
        logger.info("=" * 60)
        logger.info("  First boot detected — no admin account exists.")
        logger.info("  Visit /setup to complete admin account creation.")
        logger.info("=" * 60)
        return

    # Admin already exists — run orphan thread migration for any
    # LangGraph thread metadata that pre-dates the auth module.
    # | Admin 已存在 — 对任何早于 auth 模块的 LangGraph 线程元数据运行孤立线程迁移。
    async with sf() as session:
        stmt = select(UserRow).where(UserRow.system_role == "admin").limit(1)
        row = (await session.execute(stmt)).scalar_one_or_none()

    if row is None:
        return  # Should not happen (admin_count > 0 above), but be safe.
        # | 不应该发生（上面 admin_count > 0），但安全起见。

    admin_id = str(row.id)

    # LangGraph store orphan migration — non-fatal.
    # This covers the "no-auth → with-auth" upgrade path for users
    # whose existing LangGraph thread metadata has no user_id set.
    # | LangGraph store 孤立迁移 — 非致命。
    # 这覆盖了现有 LangGraph 线程元数据没有设置 user_id 的用户的
    # "no-auth → with-auth" 升级路径。
    store = getattr(app.state, "store", None)
    if store is not None:
        try:
            migrated = await _migrate_orphaned_threads(store, admin_id)
            if migrated:
                logger.info("Migrated %d orphan LangGraph thread(s) to admin", migrated)
        except Exception:
            logger.exception("LangGraph thread migration failed (non-fatal)")


async def _iter_store_items(store, namespace, *, page_size: int = 500):
    """Paginated async iterator over a LangGraph store namespace.

    Replaces the old hardcoded ``limit=1000`` call with a cursor-style
    loop so that environments with more than one page of orphans do
    not silently lose data. Terminates when a page is empty OR when a
    short page arrives (indicating the last page).

    对 LangGraph store 命名空间的分页异步迭代器。
    用游标式循环替换了旧的硬编码 ``limit=1000`` 调用，
    使拥有超过一页孤立数据的环境不会静默丢失数据。
    当页面为空或到达短页面（表示最后一页）时终止。
    """
    offset = 0
    while True:
        batch = await store.asearch(namespace, limit=page_size, offset=offset)
        if not batch:
            return
        for item in batch:
            yield item
        if len(batch) < page_size:
            return
        offset += page_size


async def _migrate_orphaned_threads(store, admin_user_id: str) -> int:
    """Migrate LangGraph store threads with no user_id to the given admin.

    Uses cursor pagination so all orphans are migrated regardless of
    count. Returns the number of rows migrated.

    将没有 user_id 的 LangGraph store 线程迁移到给定的 admin。
    使用游标分页，因此无论数量多少，所有孤立数据都会被迁移。
    返回迁移的行数。
    """
    migrated = 0
    async for item in _iter_store_items(store, ("threads",)):
        metadata = item.value.get("metadata", {})
        if not metadata.get("user_id"):
            metadata["user_id"] = admin_user_id
            item.value["metadata"] = metadata
            await store.aput(("threads",), item.key, item.value)
            migrated += 1
    return migrated


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler.

    应用程序生命周期处理器。
    """

    # Load config and check necessary environment variables at startup.
    # `startup_config` is a local snapshot used only for one-shot bootstrap
    # work (logging level, langgraph_runtime engines, channels). Request-time
    # config resolution always routes through `get_app_config()` in
    # `app/gateway/deps.py::get_config()` so `config.yaml` edits become
    # visible without a process restart. We deliberately do NOT cache this
    # snapshot on `app.state` to keep that contract enforceable.
    # | 在启动时加载配置并检查必要的环境变量。
    # `startup_config` 是仅用于一次性启动工作的本地快照
    #（日志级别、langgraph_runtime 引擎、channels）。请求时的
    # 配置解析始终通过 `app/gateway/deps.py::get_config()` 中的 `get_app_config()` 路由，
    # 因此 `config.yaml` 的编辑无需进程重启即可生效。
    # 我们有意不将此快照缓存在 `app.state` 上，以保持该契约可执行。
    try:
        startup_config = get_app_config()
        apply_logging_level(startup_config.log_level)
        logger.info("Configuration loaded successfully")
        warn_if_auth_disabled_enabled()
    except Exception as e:
        error_msg = f"Failed to load configuration during gateway startup: {e}"
        logger.exception(error_msg)
        raise RuntimeError(error_msg) from e
    config = get_gateway_config()
    logger.info(f"Starting API Gateway on {config.host}:{config.port}")

    # Pre-warm tiktoken encoding cache so the first memory-injection request
    # never blocks on the BPE data download (which hits an OpenAI/Azure URL
    # that may be unreachable in restricted networks — see issue #3402).
    # When memory.token_counting is "char", token counting never touches
    # tiktoken, so skip the warm-up entirely (avoids even the 5s probe in
    # network-restricted deployments — see issue #3429).
    # | 预热 tiktoken 编码缓存，使第一个 memory-injection 请求
    # 永远不会阻塞在 BPE 数据下载上（该下载访问 OpenAI/Azure URL，
    # 在受限网络中可能无法访问 — 参见 issue #3402）。
    # 当 memory.token_counting 为 "char" 时，token 计数永远不会触及
    # tiktoken，因此完全跳过预热（避免在受限网络部署中甚至 5 秒的探测 — 参见 issue #3429）。
    if startup_config.memory.token_counting == "char":
        logger.info("memory.token_counting='char'; skipping tiktoken warm-up (network-free token estimation)")
    else:
        try:
            from deerflow.agents.memory.prompt import warm_tiktoken_cache

            warmed = await asyncio.wait_for(
                asyncio.to_thread(warm_tiktoken_cache),
                timeout=5,
            )
            if warmed:
                logger.info("tiktoken encoding cache warmed successfully")
            else:
                logger.warning("tiktoken encoding cache warm-up failed; token counting will use character-based fallback until tiktoken loads successfully")
        except TimeoutError:
            logger.warning("tiktoken encoding cache warm-up timed out; token counting will use character-based fallback until tiktoken loads successfully")
        except Exception:
            logger.warning("tiktoken warm-up skipped", exc_info=True)

    # Initialize LangGraph runtime components (StreamBridge, RunManager, checkpointer, store)
    # | 初始化 LangGraph 运行时组件（StreamBridge、RunManager、checkpointer、store）
    async with langgraph_runtime(app, startup_config):
        logger.info("LangGraph runtime initialised")

        # Check admin bootstrap state and migrate orphan threads after admin exists.
        # Must run AFTER langgraph_runtime so app.state.store is available for thread migration
        # | 检查 admin 启动状态，并在 admin 存在后迁移孤立线程。
        # 必须在 langgraph_runtime 之后运行，以便 app.state.store 可用于线程迁移
        await _ensure_admin_user(app)

        # Start IM channel service if any channels are configured
        # | 如果配置了任何 IM channels，启动 IM channel 服务
        try:
            from app.channels.service import start_channel_service

            channel_service = await start_channel_service(startup_config)
            logger.info("Channel service started: %s", channel_service.get_status())
        except Exception:
            logger.exception("No IM channels configured or channel service failed to start")

        yield

        # Stop channel service on shutdown (bounded to prevent worker hang)
        # | 在关闭时停止 channel 服务（有界以防止 worker 挂起）
        try:
            from app.channels.service import stop_channel_service

            await asyncio.wait_for(
                stop_channel_service(),
                timeout=_SHUTDOWN_HOOK_TIMEOUT_SECONDS,
            )
        except TimeoutError:
            logger.warning(
                "Channel service shutdown exceeded %.1fs; proceeding with worker exit.",
                _SHUTDOWN_HOOK_TIMEOUT_SECONDS,
            )
        except Exception:
            logger.exception("Failed to stop channel service")

    logger.info("Shutting down API Gateway")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance.

    创建并配置 FastAPI 应用程序。

    返回：
        已配置的 FastAPI 应用程序实例。
    """
    config = get_gateway_config()
    docs_url = "/docs" if config.enable_docs else None
    redoc_url = "/redoc" if config.enable_docs else None
    openapi_url = "/openapi.json" if config.enable_docs else None

    app = FastAPI(
        title="DeerFlow API Gateway",
        description="""
## DeerFlow API Gateway

API Gateway for DeerFlow - A LangGraph-based AI agent backend with sandbox execution capabilities.

### Features

- **Models Management**: Query and retrieve available AI models
- **MCP Configuration**: Manage Model Context Protocol (MCP) server configurations
- **Memory Management**: Access and manage global memory data for personalized conversations
- **Skills Management**: Query and manage skills and their enabled status
- **Artifacts**: Access thread artifacts and generated files
- **Health Monitoring**: System health check endpoints

### Architecture

LangGraph-compatible requests are routed through nginx to this gateway.
This gateway provides runtime endpoints for agent runs plus custom endpoints for models, MCP configuration, skills, and artifacts.
        """,
        version="0.1.0",
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        openapi_tags=[
            {
                "name": "models",
                "description": "Operations for querying available AI models and their configurations",
            },
            {
                "name": "mcp",
                "description": "Manage Model Context Protocol (MCP) server configurations",
            },
            {
                "name": "memory",
                "description": "Access and manage global memory data for personalized conversations",
            },
            {
                "name": "skills",
                "description": "Manage skills and their configurations",
            },
            {
                "name": "artifacts",
                "description": "Access and download thread artifacts and generated files",
            },
            {
                "name": "uploads",
                "description": "Upload and manage user files for threads",
            },
            {
                "name": "threads",
                "description": "Manage DeerFlow thread-local filesystem data",
            },
            {
                "name": "agents",
                "description": "Create and manage custom agents with per-agent config and prompts",
            },
            {
                "name": "suggestions",
                "description": "Generate follow-up question suggestions for conversations",
            },
            {
                "name": "channels",
                "description": "Manage IM channel integrations (Feishu, Slack, Telegram)",
            },
            {
                "name": "assistants-compat",
                "description": "LangGraph Platform-compatible assistants API (stub)",
            },
            {
                "name": "runs",
                "description": "LangGraph Platform-compatible runs lifecycle (create, stream, cancel)",
            },
            {
                "name": "health",
                "description": "Health check and system status endpoints",
            },
        ],
    )

    # Auth: reject unauthenticated requests to non-public paths (fail-closed safety net)
    # | Auth：拒绝未认证请求访问非公开路径（fail-closed 安全网）
    app.add_middleware(AuthMiddleware)

    # CSRF: Double Submit Cookie pattern for state-changing requests
    # | CSRF：状态变更请求的双重提交 Cookie 模式
    app.add_middleware(CSRFMiddleware)

    # CORS: the unified nginx endpoint is same-origin by default. Split-origin
    # browser clients must opt in with this explicit Gateway allowlist so CORS
    # and CSRF origin checks share the same source of truth.
    # | CORS：统一的 nginx 端点默认是同源的。分离源的
    # 浏览器客户端必须通过此显式 Gateway 允许列表选择加入，
    # 以便 CORS 和 CSRF 源检查共享相同的真实来源。
    cors_origins = sorted(get_configured_cors_origins())
    if cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Include routers
    # | 包含路由器
    # Models API is mounted at /api/models
    # | Models API 挂载在 /api/models
    app.include_router(models.router)

    # MCP API is mounted at /api/mcp
    # | MCP API 挂载在 /api/mcp
    app.include_router(mcp.router)

    # Memory API is mounted at /api/memory
    # | Memory API 挂载在 /api/memory
    app.include_router(memory.router)

    # Skills API is mounted at /api/skills
    # | Skills API 挂载在 /api/skills
    app.include_router(skills.router)

    # Artifacts API is mounted at /api/threads/{thread_id}/artifacts
    # | Artifacts API 挂载在 /api/threads/{thread_id}/artifacts
    app.include_router(artifacts.router)

    # Uploads API is mounted at /api/threads/{thread_id}/uploads
    # | Uploads API 挂载在 /api/threads/{thread_id}/uploads
    app.include_router(uploads.router)

    # Thread cleanup API is mounted at /api/threads/{thread_id}
    # | Thread cleanup API 挂载在 /api/threads/{thread_id}
    app.include_router(threads.router)

    # Agents API is mounted at /api/agents
    # | Agents API 挂载在 /api/agents
    app.include_router(agents.router)

    # Suggestions API is mounted at /api/threads/{thread_id}/suggestions
    # | Suggestions API 挂载在 /api/threads/{thread_id}/suggestions
    app.include_router(suggestions.router)

    # Channels API is mounted at /api/channels
    # | Channels API 挂载在 /api/channels
    app.include_router(channels.router)

    # Assistants compatibility API (LangGraph Platform stub)
    # | Assistants 兼容 API（LangGraph Platform 存根）
    app.include_router(assistants_compat.router)

    # Auth API is mounted at /api/v1/auth
    # | Auth API 挂载在 /api/v1/auth
    app.include_router(auth.router)

    # Feedback API is mounted at /api/threads/{thread_id}/runs/{run_id}/feedback
    # | Feedback API 挂载在 /api/threads/{thread_id}/runs/{run_id}/feedback
    app.include_router(feedback.router)

    # Thread Runs API (LangGraph Platform-compatible runs lifecycle)
    # | Thread Runs API（LangGraph Platform 兼容的运行生命周期）
    app.include_router(thread_runs.router)

    # Stateless Runs API (stream/wait without a pre-existing thread)
    # | Stateless Runs API（无需预先存在线程的 stream/wait）
    app.include_router(runs.router)

    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Health check endpoint.

        Returns:
            Service health status information.

        健康检查端点。

        返回：
            服务健康状态信息。
        """
        return {"status": "healthy", "service": "deer-flow-gateway"}

    return app


# Create app instance for uvicorn
# | 为 uvicorn 创建 app 实例
app = create_app()
