"""Run lifecycle service layer.

Centralizes the business logic for creating runs, formatting SSE
frames, and consuming stream bridge events.  Router modules
(``thread_runs``, ``runs``) are thin HTTP handlers that delegate here.

运行生命周期服务层。
集中管理创建运行、格式化 SSE 帧和消费 stream bridge 事件的业务逻辑。
路由器模块（``thread_runs``、``runs``）是薄 HTTP 处理器，委托到这里。
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from collections.abc import Mapping
from typing import Any

from fastapi import HTTPException, Request
from langchain_core.messages import BaseMessage
from langchain_core.messages.utils import convert_to_messages

from app.gateway.deps import get_run_context, get_run_manager, get_stream_bridge
from app.gateway.internal_auth import INTERNAL_SYSTEM_ROLE
from app.gateway.utils import sanitize_log_param
from deerflow.config.app_config import get_app_config
from deerflow.runtime import (
    END_SENTINEL,
    HEARTBEAT_SENTINEL,
    ConflictError,
    DisconnectMode,
    RunManager,
    RunRecord,
    RunStatus,
    StreamBridge,
    UnsupportedStrategyError,
    run_agent,
)
from deerflow.runtime.runs.naming import resolve_root_run_name

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# SSE formatting
# | SSE 格式化
# ---------------------------------------------------------------------------


def format_sse(event: str, data: Any, *, event_id: str | None = None) -> str:
    """Format a single SSE frame.

    Field order: ``event:`` -> ``data:`` -> ``id:`` (optional) -> blank line.
    This matches the LangGraph Platform wire format consumed by the
    ``useStream`` React hook and the Python ``langgraph-sdk`` SSE decoder.

    格式化单个 SSE 帧。
    字段顺序：``event:`` -> ``data:`` -> ``id:``（可选）-> 空行。
    这与 ``useStream`` React hook 和 Python ``langgraph-sdk`` SSE 解码器
    消费的 LangGraph Platform 线格式匹配。
    """
    payload = json.dumps(data, default=str, ensure_ascii=False)
    parts = [f"event: {event}", f"data: {payload}"]
    if event_id:
        parts.append(f"id: {event_id}")
    parts.append("")
    parts.append("")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Input / config helpers
# | 输入 / 配置辅助函数
# ---------------------------------------------------------------------------


def normalize_stream_modes(raw: list[str] | str | None) -> list[str]:
    """Normalize the stream_mode parameter to a list.

    Default matches what ``useStream`` expects: values + messages-tuple.

    将 stream_mode 参数规范化为列表。
    默认值与 ``useStream`` 期望的一致：values + messages-tuple。
    """
    if raw is None:
        return ["values"]
    if isinstance(raw, str):
        return [raw]
    return raw if raw else ["values"]


def normalize_input(raw_input: dict[str, Any] | None) -> dict[str, Any]:
    """Convert LangGraph Platform input format to LangChain state dict.

    Delegates dict→message coercion to ``langchain_core.messages.utils.convert_to_messages``
    so that ``additional_kwargs`` (e.g. uploaded-file metadata — gh #3132), ``id``,
    ``name``, and non-human roles (ai/system/tool) survive unchanged.  An earlier
    hand-rolled version only forwarded ``content`` and collapsed every role to
    ``HumanMessage``, which silently stripped frontend-supplied attachments.

    Malformed message dicts (missing ``role``/``type``/``content``, unsupported
    role, etc.) raise ``HTTPException(400)`` with the offending index, instead
    of bubbling up as a 500.  The gateway is a system boundary, so per-entry
    validation errors are the right shape for clients to retry against.

    将 LangGraph Platform 输入格式转换为 LangChain state dict。
    将 dict→message 转换委托给 ``langchain_core.messages.utils.convert_to_messages``，
    以便 ``additional_kwargs``（例如上传文件元数据 — gh #3132）、``id``、
    ``name`` 和非人类角色（ai/system/tool）保持不变。早期的手写版本
    只转发 ``content`` 并将每个角色折叠为 ``HumanMessage``，
    这悄无声息地剥离了前端提供的附件。

    格式错误的消息 dict（缺少 ``role``/``type``/``content``、不支持的角色等）
    抛出 ``HTTPException(400)`` 并附带出错的索引，而不是冒泡为 500。
    网关是系统边界，因此逐条验证错误是客户端可以重试的正确形式。
    """
    if raw_input is None:
        return {}
    messages = raw_input.get("messages")
    if messages and isinstance(messages, list):
        converted: list[Any] = []
        for index, msg in enumerate(messages):
            if isinstance(msg, BaseMessage):
                converted.append(msg)
            elif isinstance(msg, dict):
                try:
                    converted.extend(convert_to_messages([msg]))
                except (ValueError, TypeError, NotImplementedError) as exc:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid message at input.messages[{index}]: {exc}",
                    ) from exc
            else:
                converted.append(msg)
        return {**raw_input, "messages": converted}
    return raw_input


_DEFAULT_ASSISTANT_ID = "lead_agent"


# Whitelist of run-context keys that the langgraph-compat layer forwards from
# ``body.context`` into the run config. ``config["context"]`` exists in
# LangGraph >=0.6, but these values must be written to both ``configurable``
# (for legacy ``_get_runtime_config`` consumers) and ``context`` because
# LangGraph >=1.1.9 no longer makes ``ToolRuntime.context`` fall back to
# ``configurable`` for consumers like ``setup_agent``.
# | langgraph-compat 层从 ``body.context`` 转发到运行配置中的运行上下文键白名单。
# ``config["context"]`` 在 LangGraph >=0.6 中存在，但这些值必须同时写入 ``configurable``
#（供旧版 ``_get_runtime_config`` 消费者使用）和 ``context``，
# 因为 LangGraph >=1.1.9 不再让 ``ToolRuntime.context`` 回退到
# ``configurable`` 供 ``setup_agent`` 等消费者使用。
_CONTEXT_CONFIGURABLE_KEYS: frozenset[str] = frozenset(
    {
        "model_name",
        "mode",
        "thinking_enabled",
        "reasoning_effort",
        "is_plan_mode",
        "subagent_enabled",
        "max_concurrent_subagents",
        "agent_name",
        "is_bootstrap",
    }
)


def merge_run_context_overrides(config: dict[str, Any], context: Mapping[str, Any] | None) -> None:
    """Merge whitelisted keys from ``body.context`` into both ``config['configurable']``
    and ``config['context']`` so they are visible to legacy configurable readers and
    to LangGraph ``ToolRuntime.context`` consumers (e.g. the ``setup_agent`` tool —
    see issue #2677).

    ``user_id`` is intentionally propagated into ``config['context']`` in addition to
    the whitelisted keys, so non-web callers (e.g. IM channels) that supply identity in
    ``body.context`` keep it on ``ToolRuntime.context``. It is merged with
    ``setdefault`` so a server-authenticated id stamped by
    :func:`inject_authenticated_user_context` always wins over the client-supplied one.

    将 ``body.context`` 中的白名单键合并到 ``config['configurable']`` 和 ``config['context']`` 中，
    使它们对旧版 configurable 读取器和 LangGraph ``ToolRuntime.context`` 消费者
    （例如 ``setup_agent`` 工具 — 参见 issue #2677）可见。

    ``user_id`` 有意在除了白名单键之外还传播到 ``config['context']`` 中，
    以便在 ``body.context`` 中提供身份的非 Web 调用者（例如 IM channels）
    将其保留在 ``ToolRuntime.context`` 上。它使用 ``setdefault`` 合并，
    因此由 :func:`inject_authenticated_user_context` 标记的服务器认证 id
    始终优先于客户端提供的 id。
    """
    if not context:
        return
    configurable = config.setdefault("configurable", {})
    runtime_context = config.setdefault("context", {})
    for key in _CONTEXT_CONFIGURABLE_KEYS:
        if key in context:
            if isinstance(configurable, dict):
                configurable.setdefault(key, context[key])
            if isinstance(runtime_context, dict):
                runtime_context.setdefault(key, context[key])
    if "user_id" in context and isinstance(runtime_context, dict):
        runtime_context.setdefault("user_id", context["user_id"])


def inject_authenticated_user_context(config: dict[str, Any], request: Request) -> None:
    """Stamp the authenticated user into the run context for background tools.

    Tool execution may happen after the request handler has returned, so tools
    that persist user-scoped files should not rely only on ambient ContextVars.
    The value comes from server-side auth state, never from client context.

    将已认证用户标记到运行上下文中，供后台工具使用。
    工具执行可能在请求处理器返回之后发生，因此持久化用户范围文件的工具
    不应仅依赖环境 ContextVars。该值来自服务器端认证状态，从不来自客户端上下文。
    """

    user = getattr(request.state, "user", None)
    user_id = getattr(user, "id", None)
    if user_id is None:
        return

    if getattr(user, "system_role", None) == INTERNAL_SYSTEM_ROLE:
        return

    runtime_context = config.setdefault("context", {})
    if isinstance(runtime_context, dict):
        runtime_context["user_id"] = str(user_id)


def resolve_agent_factory(assistant_id: str | None):
    """Resolve the agent factory callable from config.

    Custom agents are implemented as ``lead_agent`` + an ``agent_name``
    injected into ``configurable`` or ``context`` — see
    :func:`build_run_config`.  All ``assistant_id`` values therefore map to the
    same factory; the routing happens inside ``make_lead_agent`` when it reads
    ``cfg["agent_name"]``.

    从配置中解析 agent factory 可调用对象。
    自定义 agent 实现为 ``lead_agent`` + 注入到 ``configurable`` 或 ``context`` 中的 ``agent_name`` —
    参见 :func:`build_run_config`。因此所有 ``assistant_id`` 值都映射到同一个 factory；
    路由在 ``make_lead_agent`` 读取 ``cfg["agent_name"]`` 时发生。
    """
    from deerflow.agents.lead_agent.agent import make_lead_agent

    return make_lead_agent


def build_run_config(
    thread_id: str,
    request_config: dict[str, Any] | None,
    metadata: dict[str, Any] | None,
    *,
    assistant_id: str | None = None,
) -> dict[str, Any]:
    """Build a RunnableConfig dict for the agent.

    When *assistant_id* refers to a custom agent (anything other than
    ``"lead_agent"`` / ``None``), the name is forwarded as ``agent_name`` in
    whichever runtime options container is active: ``context`` for
    LangGraph >= 0.6.0 requests, otherwise ``configurable``.
    ``make_lead_agent`` reads this key to load the matching
    ``agents/<name>/SOUL.md`` and per-agent config — without it the agent
    silently runs as the default lead agent.

    This mirrors the channel manager's ``_resolve_run_params`` logic so that
    the LangGraph Platform-compatible HTTP API and the IM channel path behave
    identically.

    为 agent 构建 RunnableConfig dict。
    当 *assistant_id* 指向自定义 agent（除 ``"lead_agent"`` / ``None`` 之外的任何值）时，
    名称作为 ``agent_name`` 转发到当前活跃的运行时选项容器中：
    LangGraph >= 0.6.0 请求使用 ``context``，否则使用 ``configurable``。
    ``make_lead_agent`` 读取此键以加载匹配的 ``agents/<name>/SOUL.md``
    和每个 agent 的配置 — 没有它，agent 会静默地作为默认 lead agent 运行。

    这镜像了 channel manager 的 ``_resolve_run_params`` 逻辑，
    以便 LangGraph Platform 兼容的 HTTP API 和 IM channel 路径行为一致。
    """
    config: dict[str, Any] = {"recursion_limit": 100}
    if request_config:
        # LangGraph >= 0.6.0 introduced ``context`` as the preferred way to
        # pass thread-level data and rejects requests that include both
        # ``configurable`` and ``context``.  If the caller already sends
        # ``context``, honour it and skip our own ``configurable`` dict.
        # | LangGraph >= 0.6.0 引入了 ``context`` 作为传递线程级数据的首选方式，
        # 并拒绝同时包含 ``configurable`` 和 ``context`` 的请求。
        # 如果调用者已经发送了 ``context``，则遵循它并跳过我们自己的 ``configurable`` dict。
        if "context" in request_config:
            if "configurable" in request_config:
                logger.warning(
                    "build_run_config: client sent both 'context' and 'configurable'; preferring 'context' (LangGraph >= 0.6.0). thread_id=%s, caller_configurable keys=%s",
                    thread_id,
                    list(request_config.get("configurable", {}).keys()),
                )
            context_value = request_config["context"]
            if context_value is None:
                context = {}
            elif isinstance(context_value, Mapping):
                context = dict(context_value)
            else:
                raise ValueError("request config 'context' must be a mapping or null.")
            config["context"] = context
        else:
            configurable = {"thread_id": thread_id}
            configurable.update(request_config.get("configurable", {}))
            config["configurable"] = configurable
        for k, v in request_config.items():
            if k not in ("configurable", "context"):
                config[k] = v
    else:
        config["configurable"] = {"thread_id": thread_id}

    # Inject custom agent name when the caller specified a non-default assistant.
    # Honour an explicit agent_name in the active runtime options container.
    # | 当调用者指定了非默认 assistant 时，注入自定义 agent 名称。
    # 遵循活跃运行时选项容器中的显式 agent_name。
    if assistant_id and assistant_id != _DEFAULT_ASSISTANT_ID:
        normalized = assistant_id.strip().lower().replace("_", "-")
        if not normalized or not re.fullmatch(r"[a-z0-9-]+", normalized):
            raise ValueError(f"Invalid assistant_id {assistant_id!r}: must contain only letters, digits, and hyphens after normalization.")
        if "configurable" in config:
            target = config["configurable"]
        elif "context" in config:
            target = config["context"]
        else:
            target = config.setdefault("configurable", {})
        if target is not None and "agent_name" not in target:
            target["agent_name"] = normalized
        config.setdefault("run_name", resolve_root_run_name(config, normalized))
    if metadata:
        config.setdefault("metadata", {}).update(metadata)
    return config


# ---------------------------------------------------------------------------
# Run lifecycle
# | 运行生命周期
# ---------------------------------------------------------------------------


async def start_run(
    body: Any,
    thread_id: str,
    request: Request,
) -> RunRecord:
    """Create a RunRecord and launch the background agent task.

    Parameters
    ----------
    body : RunCreateRequest
        The validated request body (typed as Any to avoid circular import
        with the router module that defines the Pydantic model).
    thread_id : str
        Target thread.
    request : Request
        FastAPI request — used to retrieve singletons from ``app.state``.

    创建 RunRecord 并启动后台 agent 任务。

    参数
    ----------
    body : RunCreateRequest
        已验证的请求体（类型为 Any 以避免与定义 Pydantic 模型的路由器模块循环导入）。
    thread_id : str
        目标线程。
    request : Request
        FastAPI 请求 — 用于从 ``app.state`` 检索单例。
    """
    bridge = get_stream_bridge(request)
    run_mgr = get_run_manager(request)
    run_ctx = get_run_context(request)

    disconnect = DisconnectMode.cancel if body.on_disconnect == "cancel" else DisconnectMode.continue_

    body_context = getattr(body, "context", None) or {}
    model_name = body_context.get("model_name")

    # Coerce non-string model_name values to str before truncation.
    # | 在截断前将非字符串 model_name 值强制转换为 str。
    if model_name is not None and not isinstance(model_name, str):
        model_name = str(model_name)

    # Validate model against the allowlist when a model_name is provided.
    # | 当提供了 model_name 时，根据允许列表验证模型。
    if model_name:
        app_config = get_app_config()
        resolved = app_config.get_model_config(model_name)
        if resolved is None:
            raise HTTPException(
                status_code=400,
                detail=f"Model {model_name!r} is not in the configured model allowlist",
            )

    # Stateless run endpoints carry thread_id in the request *body*, so the
    # @require_permission(owner_check=True) decorator -- which resolves ownership
    # from the path param -- cannot protect them. Enforce thread ownership here,
    # before any run is created, so one user cannot start runs on (or read /wait
    # checkpoint state from) another user's thread. Missing rows (auto-created
    # temp threads) and NULL-owner rows (shared / pre-auth data) stay accessible
    # via check_access; only a thread already owned by another user is rejected
    # with 404, matching thread_runs.py's anti-enumeration behaviour. Internal
    # channel runs act on behalf of IM users they do not own (see
    # inject_authenticated_user_context), so the internal system role is exempt.
    # | 无状态运行端点在请求 *body* 中携带 thread_id，因此
    # @require_permission(owner_check=True) 装饰器 — 它从路径参数解析所有权 —
    # 无法保护它们。在此处强制线程所有权，在任何运行创建之前，
    # 这样一个用户无法在另一个用户的线程上启动运行（或读取 /wait 检查点状态）。
    # 缺失行（自动创建的临时线程）和 NULL-owner 行（共享/预认证数据）
    # 通过 check_access 保持可访问；只有已被另一个用户拥有的线程
    # 才会被 404 拒绝，匹配 thread_runs.py 的反枚举行为。
    # 内部 channel 运行代表它们不拥有的 IM 用户行事（参见
    # inject_authenticated_user_context），因此内部系统角色被豁免。
    user = getattr(request.state, "user", None)
    if user is not None and getattr(user, "system_role", None) != INTERNAL_SYSTEM_ROLE:
        if not await run_ctx.thread_store.check_access(thread_id, str(user.id)):
            raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    try:
        record = await run_mgr.create_or_reject(
            thread_id,
            body.assistant_id,
            on_disconnect=disconnect,
            metadata=body.metadata or {},
            kwargs={"input": body.input, "config": body.config},
            multitask_strategy=body.multitask_strategy,
            model_name=model_name,
        )
    except ConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except UnsupportedStrategyError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc

    # Upsert thread metadata so the thread appears in /threads/search,
    # even for threads that were never explicitly created via POST /threads
    # (e.g. stateless runs).
    # | 更新插入线程元数据，使线程出现在 /threads/search 中，
    # 即使对于从未通过 POST /threads 显式创建的线程（例如无状态运行）。
    try:
        existing = await run_ctx.thread_store.get(thread_id)
        if existing is None:
            await run_ctx.thread_store.create(
                thread_id,
                assistant_id=body.assistant_id,
                metadata=body.metadata,
            )
        else:
            await run_ctx.thread_store.update_status(thread_id, "running")
    except Exception:
        logger.warning("Failed to upsert thread_meta for %s (non-fatal)", sanitize_log_param(thread_id))

    agent_factory = resolve_agent_factory(body.assistant_id)
    graph_input = normalize_input(body.input)
    config = build_run_config(thread_id, body.config, body.metadata, assistant_id=body.assistant_id)

    # Merge DeerFlow-specific context overrides into both ``configurable`` and ``context``.
    # The ``context`` field is a custom extension for the langgraph-compat layer
    # that carries agent configuration (model_name, thinking_enabled, etc.).
    # Only agent-relevant keys are forwarded; unknown keys (e.g. thread_id) are ignored.
    # | 将 DeerFlow 特定的上下文覆盖合并到 ``configurable`` 和 ``context`` 中。
    # ``context`` 字段是 langgraph-compat 层的自定义扩展，
    # 携带 agent 配置（model_name、thinking_enabled 等）。
    # 仅转发与 agent 相关的键；未知键（例如 thread_id）被忽略。
    merge_run_context_overrides(config, getattr(body, "context", None))
    inject_authenticated_user_context(config, request)

    stream_modes = normalize_stream_modes(body.stream_mode)

    task = asyncio.create_task(
        run_agent(
            bridge,
            run_mgr,
            record,
            ctx=run_ctx,
            agent_factory=agent_factory,
            graph_input=graph_input,
            config=config,
            stream_modes=stream_modes,
            stream_subgraphs=body.stream_subgraphs,
            interrupt_before=body.interrupt_before,
            interrupt_after=body.interrupt_after,
        )
    )
    record.task = task

    # Title sync is handled by worker.py's finally block which reads the
    # title from the checkpoint and calls thread_store.update_display_name
    # after the run completes.
    # | 标题同步由 worker.py 的 finally 块处理，它在运行完成后
    # 从检查点读取标题并调用 thread_store.update_display_name。

    return record


async def sse_consumer(
    bridge: StreamBridge,
    record: RunRecord,
    request: Request,
    run_mgr: RunManager,
):
    """Async generator that yields SSE frames from the bridge.

    The ``finally`` block implements ``on_disconnect`` semantics:
    - ``cancel``: abort the background task on client disconnect.
    - ``continue``: let the task run; events are discarded.

    异步生成器，从 bridge 产出 SSE 帧。
    ``finally`` 块实现 ``on_disconnect`` 语义：
    - ``cancel``：客户端断开时中止后台任务。
    - ``continue``：让任务继续运行；事件被丢弃。
    """
    last_event_id = request.headers.get("Last-Event-ID")
    try:
        async for entry in bridge.subscribe(record.run_id, last_event_id=last_event_id):
            if await request.is_disconnected():
                break

            if entry is HEARTBEAT_SENTINEL:
                yield ": heartbeat\n\n"
                continue

            if entry is END_SENTINEL:
                yield format_sse("end", None, event_id=entry.id or None)
                return

            yield format_sse(entry.event, entry.data, event_id=entry.id or None)

    finally:
        if record.status in (RunStatus.pending, RunStatus.running):
            if record.on_disconnect == DisconnectMode.cancel:
                await run_mgr.cancel(record.run_id)


async def wait_for_run_completion(
    bridge: StreamBridge,
    record: RunRecord,
    request: Request,
    run_mgr: RunManager,
) -> bool:
    """Block until the run publishes ``END_SENTINEL``, honouring on_disconnect.

    The non-streaming ``/wait`` endpoints used to ``await record.task``
    directly with no disconnect handling.  When the client (or an
    intermediate HTTP proxy) timed out during a long tool call such as
    ``pip install``, the handler would swallow ``CancelledError`` and
    serialize whatever checkpoint happened to exist — masking a half-finished
    run as a normal completion (issue #3265).

    This helper consumes the same bridge that ``sse_consumer`` does so the
    wait path shares its disconnect semantics: each wake-up polls
    ``request.is_disconnected()``; on a real disconnect it cancels the
    background run when ``record.on_disconnect`` is ``cancel``.  The bridge's
    heartbeat sentinels guarantee at least one wake-up per
    ``heartbeat_interval`` even when the agent emits no events for a while.

    Returns:
        ``True`` when ``END_SENTINEL`` was observed (run reached a terminal
        state), ``False`` when the loop exited because the client
        disconnected.  Callers must skip checkpoint serialization on
        ``False`` so a partial checkpoint is not returned as a normal
        response.

    阻塞直到运行发布 ``END_SENTINEL``，遵循 on_disconnect 语义。
    非流式 ``/wait`` 端点曾经直接 ``await record.task`` 而没有断开处理。
    当客户端（或中间 HTTP 代理）在长时间工具调用（如 ``pip install``）期间超时时，
    处理器会吞掉 ``CancelledError`` 并序列化碰巧存在的任何检查点 —
    将半完成的运行伪装成正常完成（issue #3265）。

    此辅助函数消费与 ``sse_consumer`` 相同的 bridge，因此等待路径共享其断开语义：
    每次唤醒轮询 ``request.is_disconnected()``；在真正断开时，
    当 ``record.on_disconnect`` 为 ``cancel`` 时取消后台运行。
    bridge 的心跳哨兵保证每个 ``heartbeat_interval`` 至少唤醒一次，
    即使 agent 一段时间内没有发出事件。

    返回：
        当观察到 ``END_SENTINEL`` 时返回 ``True``（运行达到终止状态），
        当循环因客户端断开而退出时返回 ``False``。
        调用者在 ``False`` 时必须跳过检查点序列化，
        以免将部分检查点作为正常响应返回。
    """
    completed = False
    try:
        async for entry in bridge.subscribe(record.run_id):
            # END_SENTINEL means the run reached a terminal state; honour it
            # even if the client just disconnected so the caller still serializes
            # the real final checkpoint.
            # | END_SENTINEL 表示运行已达到终止状态；即使客户端刚刚断开也遵循它，
            # 以便调用者仍然序列化真正的最终检查点。
            if entry is END_SENTINEL:
                completed = True
                return True
            if await request.is_disconnected():
                break
            # Heartbeats and regular events: keep waiting for END_SENTINEL.
            # | 心跳和常规事件：继续等待 END_SENTINEL。
        return completed
    finally:
        if not completed and record.status in (RunStatus.pending, RunStatus.running):
            if record.on_disconnect == DisconnectMode.cancel:
                await run_mgr.cancel(record.run_id)
