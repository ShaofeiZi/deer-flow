"""Global authentication middleware — fail-closed safety net.

Rejects unauthenticated requests to non-public paths with 401. When a
request passes the cookie check, resolves the JWT payload to a real
``User`` object and stamps it into both ``request.state.user`` and the
``deerflow.runtime.user_context`` contextvar so that repository-layer
owner filtering works automatically via the sentinel pattern.

Fine-grained permission checks remain in authz.py decorators.
| 全局认证中间件 — 故障关闭安全网。

对非公开路径的未认证请求返回 401。当请求通过 cookie 检查时，
将 JWT 负载解析为真实的 ``User`` 对象，并将其标记到 ``request.state.user``
和 ``deerflow.runtime.user_context`` contextvar 中，
使仓库层的所有者过滤通过哨兵模式自动工作。

细粒度权限检查保留在 authz.py 装饰器中。
"""

from collections.abc import Callable

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.gateway.auth.errors import AuthErrorCode, AuthErrorResponse
from app.gateway.auth_disabled import (
    AUTH_SOURCE_AUTH_DISABLED,
    AUTH_SOURCE_INTERNAL,
    AUTH_SOURCE_SESSION,
    get_auth_disabled_user,
    is_auth_disabled,
)
from app.gateway.authz import _ALL_PERMISSIONS, AuthContext
from app.gateway.internal_auth import INTERNAL_AUTH_HEADER_NAME, get_internal_user, is_valid_internal_auth_token
from deerflow.runtime.user_context import reset_current_user, set_current_user

# Paths that never require authentication.
# | 永远不需要认证的路径。
_PUBLIC_PATH_PREFIXES: tuple[str, ...] = (
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
)

# Exact auth paths that are public (login/register/status check).
# /api/v1/auth/me, /api/v1/auth/change-password etc. are NOT public.
# | 公开的精确认证路径（登录/注册/状态检查）。
# /api/v1/auth/me、/api/v1/auth/change-password 等不是公开的。
_PUBLIC_EXACT_PATHS: frozenset[str] = frozenset(
    {
        "/api/v1/auth/login/local",
        "/api/v1/auth/register",
        "/api/v1/auth/logout",
        "/api/v1/auth/setup-status",
        "/api/v1/auth/initialize",
    }
)


def _is_public(path: str) -> bool:
    stripped = path.rstrip("/")
    if stripped in _PUBLIC_EXACT_PATHS:
        return True
    return any(path.startswith(prefix) for prefix in _PUBLIC_PATH_PREFIXES)


class AuthMiddleware(BaseHTTPMiddleware):
    """Strict auth gate: reject requests without a valid session.

    Two-stage check for non-public paths:

    1. Cookie presence — return 401 NOT_AUTHENTICATED if missing
    2. JWT validation via ``get_optional_user_from_request`` — return 401
       TOKEN_INVALID if the token is absent, malformed, expired, or the
       signed user does not exist / is stale

    On success, stamps ``request.state.user`` and the
    ``deerflow.runtime.user_context`` contextvar so that repository-layer
    owner filters work downstream without every route needing a
    ``@require_auth`` decorator. Routes that need per-resource
    authorization (e.g. "user A cannot read user B's thread by guessing
    the URL") should additionally use ``@require_permission(...,
    owner_check=True)`` for explicit enforcement — but authentication
    itself is fully handled here.
    | 严格认证网关：拒绝没有有效会话的请求。

    对非公开路径的两阶段检查：

    1. Cookie 存在性 — 如果缺失则返回 401 NOT_AUTHENTICATED
    2. 通过 ``get_optional_user_from_request`` 进行 JWT 验证 — 如果令牌
       缺失、格式错误、过期或签名的用户不存在/已过期，则返回 401 TOKEN_INVALID

    成功时，标记 ``request.state.user`` 和 ``deerflow.runtime.user_context``
    contextvar，使仓库层的所有者过滤器在下游工作，无需每个路由都需要
    ``@require_auth`` 装饰器。需要按资源授权（例如"用户 A 不能通过猜测 URL
    读取用户 B 的线程"）的路由应额外使用 ``@require_permission(...,
    owner_check=True)`` 进行显式强制执行 — 但认证本身在此完全处理。
    """

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if _is_public(request.url.path):
            return await call_next(request)

        internal_user = None
        if is_valid_internal_auth_token(request.headers.get(INTERNAL_AUTH_HEADER_NAME)):
            internal_user = get_internal_user()

        auth_source = AUTH_SOURCE_SESSION
        access_token = request.cookies.get("access_token")

        # Non-public path: require session cookie
        # | 非公开路径：需要会话 cookie
        if internal_user is not None:
            user = internal_user
            auth_source = AUTH_SOURCE_INTERNAL
        elif access_token:
            # Strict JWT validation: reject junk/expired tokens with 401
            # right here instead of silently passing through. This closes
            # the "junk cookie bypass" gap (AUTH_TEST_PLAN test 7.5.8):
            # without this, non-isolation routes like /api/models would
            # accept any cookie-shaped string as authentication.
            #
            # We call the *strict* resolver so that fine-grained error
            # codes (token_expired, token_invalid, user_not_found, …)
            # propagate from AuthErrorCode, not get flattened into one
            # generic code. BaseHTTPMiddleware doesn't let HTTPException
            # bubble up, so we catch and render it as JSONResponse here.
            # | 严格 JWT 验证：在此处拒绝垃圾/过期令牌并返回 401，
            # 而不是静默通过。这关闭了"垃圾 cookie 绕过"漏洞（AUTH_TEST_PLAN 测试 7.5.8）：
            # 没有此检查，非隔离路由（如 /api/models）会将任何 cookie 形状的字符串视为认证。
            #
            # 我们调用 *严格* 解析器，使细粒度错误代码
            # （token_expired、token_invalid、user_not_found 等）
            # 从 AuthErrorCode 传播，而不是被扁平化为一个通用代码。
            # BaseHTTPMiddleware 不允许 HTTPException 冒泡，因此我们在此捕获并将其渲染为 JSONResponse。
            from app.gateway.deps import get_current_user_from_request

            try:
                user = await get_current_user_from_request(request)
            except HTTPException as exc:
                if not is_auth_disabled():
                    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
                user = get_auth_disabled_user()
                auth_source = AUTH_SOURCE_AUTH_DISABLED
        elif is_auth_disabled():
            user = get_auth_disabled_user()
            auth_source = AUTH_SOURCE_AUTH_DISABLED
        else:
            return JSONResponse(
                status_code=401,
                content={
                    "detail": AuthErrorResponse(
                        code=AuthErrorCode.NOT_AUTHENTICATED,
                        message="Authentication required",
                    ).model_dump()
                },
            )

        # Stamp both request.state.user (for the contextvar pattern)
        # and request.state.auth (so @require_permission's "auth is
        # None" branch short-circuits instead of running the entire
        # JWT-decode + DB-lookup pipeline a second time per request).
        # | 标记 request.state.user（用于 contextvar 模式）
        # 和 request.state.auth（使 @require_permission 的 "auth is None"
        # 分支短路，而不是每个请求运行整个 JWT 解码 + 数据库查找管道第二次）。
        request.state.user = user
        request.state.auth_source = auth_source
        request.state.auth = AuthContext(user=user, permissions=_ALL_PERMISSIONS)
        token = set_current_user(user)
        try:
            return await call_next(request)
        finally:
            reset_current_user(token)
