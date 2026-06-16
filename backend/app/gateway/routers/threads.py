"""Thread CRUD, state, and history endpoints. | 线程 CRUD、状态和历史端点。

Combines the existing thread-local filesystem cleanup with LangGraph
Platform-compatible thread management backed by the checkpointer.
| 将现有的线程本地文件系统清理与基于 checkpointer 的 LangGraph 平台兼容线程管理相结合。

Channel values returned in state responses are serialized through
:func:`deerflow.runtime.serialization.serialize_channel_values` to
ensure LangChain message objects are converted to JSON-safe dicts
matching the LangGraph Platform wire format expected by the
``useStream`` React hook.
| 状态响应中返回的通道值通过 :func:`deerflow.runtime.serialization.serialize_channel_values` 序列化，
以确保 LangChain 消息对象被转换为 JSON 安全的字典，匹配 ``useStream`` React hook 期望的 LangGraph Platform 传输格式。
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from langgraph.checkpoint.base import empty_checkpoint, uuid6
from pydantic import BaseModel, Field, field_validator

from app.gateway.authz import require_permission
from app.gateway.deps import get_checkpointer
from app.gateway.utils import sanitize_log_param
from deerflow.config.paths import Paths, get_paths
from deerflow.runtime import serialize_channel_values
from deerflow.runtime.user_context import get_effective_user_id
from deerflow.utils.time import coerce_iso, now_iso

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/threads", tags=["threads"])


# Metadata keys that the server controls; clients are not allowed to set
# them. Pydantic ``@field_validator("metadata")`` strips them on every
# inbound model below so a malicious client cannot reflect a forged
# owner identity through the API surface. Defense-in-depth — the
# row-level invariant is still ``threads_meta.user_id`` populated from
# the auth contextvar; this list closes the metadata-blob echo gap.
# | 服务器控制的元数据键；客户端不允许设置它们。Pydantic ``@field_validator("metadata")``
# 会在每个入站模型上剥离它们，因此恶意客户端无法通过 API 表面反射伪造的所有者身份。
# 纵深防御 — 行级不变量仍然是 ``threads_meta.user_id`` 从 auth contextvar 填充；
# 此列表关闭了元数据 blob 回显漏洞。
_SERVER_RESERVED_METADATA_KEYS: frozenset[str] = frozenset({"owner_id", "user_id"})


def _strip_reserved_metadata(metadata: dict[str, Any] | None) -> dict[str, Any]:
    """Return ``metadata`` with server-controlled keys removed. | 返回移除了服务器控制键的 ``metadata``。"""
    if not metadata:
        return metadata or {}
    return {k: v for k, v in metadata.items() if k not in _SERVER_RESERVED_METADATA_KEYS}


# ---------------------------------------------------------------------------
# Response / request models | 响应 / 请求模型
# ---------------------------------------------------------------------------


class ThreadDeleteResponse(BaseModel):
    """Response model for thread cleanup. | 线程清理的响应模型。"""

    success: bool
    message: str


class ThreadResponse(BaseModel):
    """Response model for a single thread. | 单个线程的响应模型。"""

    thread_id: str = Field(description="Unique thread identifier")
    status: str = Field(default="idle", description="Thread status: idle, busy, interrupted, error")
    created_at: str = Field(default="", description="ISO timestamp")
    updated_at: str = Field(default="", description="ISO timestamp")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Thread metadata")
    values: dict[str, Any] = Field(default_factory=dict, description="Current state channel values")
    interrupts: dict[str, Any] = Field(default_factory=dict, description="Pending interrupts")


class ThreadCreateRequest(BaseModel):
    """Request body for creating a thread. | 创建线程的请求体。"""

    thread_id: str | None = Field(default=None, description="Optional thread ID (auto-generated if omitted)")
    assistant_id: str | None = Field(default=None, description="Associate thread with an assistant")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Initial metadata")

    _strip_reserved = field_validator("metadata")(classmethod(lambda cls, v: _strip_reserved_metadata(v)))


class ThreadSearchRequest(BaseModel):
    """Request body for searching threads. | 搜索线程的请求体。"""

    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata filter (exact match)")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum results")
    offset: int = Field(default=0, ge=0, description="Pagination offset")
    status: str | None = Field(default=None, description="Filter by thread status")

    @field_validator("metadata")
    @classmethod
    def _validate_metadata_filters(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Reject filter entries the SQL backend cannot compile.

        Enforces consistent behaviour across SQL and memory backends.
        See ``deerflow.persistence.json_compat`` for the shared validators.
        | 拒绝 SQL 后端无法编译的过滤条目。

        在 SQL 和内存后端之间强制执行一致的行为。
        参见 ``deerflow.persistence.json_compat`` 中的共享验证器。
        """
        if not v:
            return v
        from deerflow.persistence.json_compat import validate_metadata_filter_key, validate_metadata_filter_value

        bad_entries: list[str] = []
        for key, value in v.items():
            if not validate_metadata_filter_key(key):
                bad_entries.append(f"{key!r} (unsafe key)")
            elif not validate_metadata_filter_value(value):
                bad_entries.append(f"{key!r} (unsupported value type {type(value).__name__})")
        if bad_entries:
            raise ValueError(f"Invalid metadata filter entries: {', '.join(bad_entries)}")
        return v


class ThreadStateResponse(BaseModel):
    """Response model for thread state. | 线程状态的响应模型。"""

    values: dict[str, Any] = Field(default_factory=dict, description="Current channel values")
    next: list[str] = Field(default_factory=list, description="Next tasks to execute")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Checkpoint metadata")
    checkpoint: dict[str, Any] = Field(default_factory=dict, description="Checkpoint info")
    checkpoint_id: str | None = Field(default=None, description="Current checkpoint ID")
    parent_checkpoint_id: str | None = Field(default=None, description="Parent checkpoint ID")
    created_at: str | None = Field(default=None, description="Checkpoint timestamp")
    tasks: list[dict[str, Any]] = Field(default_factory=list, description="Interrupted task details")


class ThreadPatchRequest(BaseModel):
    """Request body for patching thread metadata. | 更新线程元数据的请求体。"""

    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata to merge")


class ThreadStateUpdateRequest(BaseModel):
    """Request body for updating thread state (human-in-the-loop resume). | 更新线程状态的请求体（人在回路中恢复）。"""

    values: dict[str, Any] | None = Field(default=None, description="Channel values to merge")
    checkpoint_id: str | None = Field(default=None, description="Checkpoint to branch from")
    checkpoint: dict[str, Any] | None = Field(default=None, description="Full checkpoint object")
    as_node: str | None = Field(default=None, description="Node identity for the update")


class HistoryEntry(BaseModel):
    """Single checkpoint history entry. | 单个检查点历史条目。"""

    checkpoint_id: str
    parent_checkpoint_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    values: dict[str, Any] = Field(default_factory=dict)
    created_at: str | None = None
    next: list[str] = Field(default_factory=list)


class ThreadHistoryRequest(BaseModel):
    """Request body for checkpoint history. | 检查点历史的请求体。"""

    limit: int = Field(default=10, ge=1, le=100, description="Maximum entries")
    before: str | None = Field(default=None, description="Cursor for pagination")


# ---------------------------------------------------------------------------
# Helpers | 辅助函数
# ---------------------------------------------------------------------------


def _delete_thread_data(thread_id: str, paths: Paths | None = None, *, user_id: str | None = None) -> ThreadDeleteResponse:
    """Delete local persisted filesystem data for a thread. | 删除线程的本地持久化文件系统数据。"""
    path_manager = paths or get_paths()
    try:
        path_manager.delete_thread_dir(thread_id, user_id=user_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except FileNotFoundError:
        # Not critical — thread data may not exist on disk
        # | 非关键 — 线程数据可能不存在于磁盘上
        logger.debug("No local thread data to delete for %s", sanitize_log_param(thread_id))
        return ThreadDeleteResponse(success=True, message=f"No local data for {thread_id}")
    except Exception as exc:
        logger.exception("Failed to delete thread data for %s", sanitize_log_param(thread_id))
        raise HTTPException(status_code=500, detail="Failed to delete local thread data.") from exc

    logger.info("Deleted local thread data for %s", sanitize_log_param(thread_id))
    return ThreadDeleteResponse(success=True, message=f"Deleted local thread data for {thread_id}")


def _derive_thread_status(checkpoint_tuple) -> str:
    """Derive thread status from checkpoint metadata. | 从检查点元数据推导线程状态。"""
    if checkpoint_tuple is None:
        return "idle"
    pending_writes = getattr(checkpoint_tuple, "pending_writes", None) or []

    # Check for error in pending writes
    # | 检查挂起写入中的错误
    for pw in pending_writes:
        if len(pw) >= 2 and pw[1] == "__error__":
            return "error"

    # Check for pending next tasks (indicates interrupt)
    # | 检查挂起的下一个任务（表示中断）
    tasks = getattr(checkpoint_tuple, "tasks", None)
    if tasks:
        return "interrupted"

    return "idle"


# ---------------------------------------------------------------------------
# Endpoints | 端点
# ---------------------------------------------------------------------------


@router.delete("/{thread_id}", response_model=ThreadDeleteResponse)
@require_permission("threads", "delete", owner_check=True, require_existing=True)
async def delete_thread_data(thread_id: str, request: Request) -> ThreadDeleteResponse:
    """Delete local persisted filesystem data for a thread.

    Cleans DeerFlow-managed thread directories, removes checkpoint data,
    and removes the thread_meta row from the configured ThreadMetaStore
    (sqlite or memory).
    | 删除线程的本地持久化文件系统数据。

    清理 DeerFlow 管理的线程目录，移除检查点数据，
    并从配置的 ThreadMetaStore（sqlite 或 memory）中移除 thread_meta 行。
    """
    from app.gateway.deps import get_thread_store

    # Clean local filesystem | 清理本地文件系统
    response = _delete_thread_data(thread_id, user_id=get_effective_user_id())

    # Remove checkpoints (best-effort) | 移除检查点（尽力而为）
    checkpointer = getattr(request.app.state, "checkpointer", None)
    if checkpointer is not None:
        try:
            if hasattr(checkpointer, "adelete_thread"):
                await checkpointer.adelete_thread(thread_id)
        except Exception:
            logger.debug("Could not delete checkpoints for thread %s (not critical)", sanitize_log_param(thread_id))

    # Remove thread_meta row (best-effort) — required for sqlite backend
    # so the deleted thread no longer appears in /threads/search.
    # | 移除 thread_meta 行（尽力而为）— sqlite 后端需要此操作，
    # 以便已删除的线程不再出现在 /threads/search 中。
    try:
        thread_store = get_thread_store(request)
        await thread_store.delete(thread_id)
    except Exception:
        logger.debug("Could not delete thread_meta for %s (not critical)", sanitize_log_param(thread_id))

    return response


@router.post("", response_model=ThreadResponse)
async def create_thread(body: ThreadCreateRequest, request: Request) -> ThreadResponse:
    """Create a new thread.

    Writes a thread_meta record (so the thread appears in /threads/search)
    and an empty checkpoint (so state endpoints work immediately).
    Idempotent: returns the existing record when ``thread_id`` already exists.
    | 创建新线程。

    写入 thread_meta 记录（使线程出现在 /threads/search 中）
    和一个空检查点（使状态端点立即可用）。
    幂等：当 ``thread_id`` 已存在时返回现有记录。
    """
    from app.gateway.deps import get_thread_store

    checkpointer = get_checkpointer(request)
    thread_store = get_thread_store(request)
    thread_id = body.thread_id or str(uuid.uuid4())
    now = now_iso()
    # ``body.metadata`` is already stripped of server-reserved keys by
    # ``ThreadCreateRequest._strip_reserved`` — see the model definition.
    # | ``body.metadata`` 已由 ``ThreadCreateRequest._strip_reserved`` 剥离了服务器保留键 — 参见模型定义。

    # Idempotency: return existing record when already present
    # | 幂等性：当已存在时返回现有记录
    existing_record = await thread_store.get(thread_id)
    if existing_record is not None:
        return ThreadResponse(
            thread_id=thread_id,
            status=existing_record.get("status", "idle"),
            created_at=coerce_iso(existing_record.get("created_at", "")),
            updated_at=coerce_iso(existing_record.get("updated_at", "")),
            metadata=existing_record.get("metadata", {}),
        )

    # Write thread_meta so the thread appears in /threads/search immediately
    # | 写入 thread_meta 使线程立即出现在 /threads/search 中
    try:
        await thread_store.create(
            thread_id,
            assistant_id=getattr(body, "assistant_id", None),
            metadata=body.metadata,
        )
    except Exception:
        logger.exception("Failed to write thread_meta for %s", sanitize_log_param(thread_id))
        raise HTTPException(status_code=500, detail="Failed to create thread")

    # Write an empty checkpoint so state endpoints work immediately
    # | 写入空检查点使状态端点立即可用
    config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": ""}}
    try:
        ckpt_metadata = {
            "step": -1,
            "source": "input",
            "writes": None,
            "parents": {},
            **body.metadata,
            "created_at": now,
        }
        await checkpointer.aput(config, empty_checkpoint(), ckpt_metadata, {})
    except Exception:
        logger.exception("Failed to create checkpoint for thread %s", sanitize_log_param(thread_id))
        raise HTTPException(status_code=500, detail="Failed to create thread")

    logger.info("Thread created: %s", sanitize_log_param(thread_id))
    return ThreadResponse(
        thread_id=thread_id,
        status="idle",
        created_at=now,
        updated_at=now,
        metadata=body.metadata,
    )


@router.post("/search", response_model=list[ThreadResponse])
async def search_threads(body: ThreadSearchRequest, request: Request) -> list[ThreadResponse]:
    """Search and list threads.

    Delegates to the configured ThreadMetaStore implementation
    (SQL-backed for sqlite/postgres, Store-backed for memory mode).
    | 搜索并列出线程。

    委托给配置的 ThreadMetaStore 实现
    （sqlite/postgres 使用 SQL 后端，memory 模式使用 Store 后端）。
    """
    from app.gateway.deps import get_thread_store
    from deerflow.persistence.thread_meta import InvalidMetadataFilterError

    repo = get_thread_store(request)
    try:
        rows = await repo.search(
            metadata=body.metadata or None,
            status=body.status,
            limit=body.limit,
            offset=body.offset,
        )
    except InvalidMetadataFilterError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return [
        ThreadResponse(
            thread_id=r["thread_id"],
            status=r.get("status", "idle"),
            # ``coerce_iso`` heals legacy unix-second values that
            # ``MemoryThreadMetaStore`` historically wrote with ``time.time()``;
            # SQL-backed rows already arrive as ISO strings and pass through.
            # | ``coerce_iso`` 修复了 ``MemoryThreadMetaStore`` 历史上用 ``time.time()`` 写入的
            # 遗留 unix 秒值；SQL 后端的行已经以 ISO 字符串形式到达并直接通过。
            created_at=coerce_iso(r.get("created_at", "")),
            updated_at=coerce_iso(r.get("updated_at", "")),
            metadata=r.get("metadata", {}),
            values={"title": r["display_name"]} if r.get("display_name") else {},
            interrupts={},
        )
        for r in rows
    ]


@router.patch("/{thread_id}", response_model=ThreadResponse)
@require_permission("threads", "write", owner_check=True, require_existing=True)
async def patch_thread(thread_id: str, body: ThreadPatchRequest, request: Request) -> ThreadResponse:
    """Merge metadata into a thread record. | 将元数据合并到线程记录中。"""
    from app.gateway.deps import get_thread_store

    thread_store = get_thread_store(request)
    record = await thread_store.get(thread_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    # ``body.metadata`` already stripped by ``ThreadPatchRequest._strip_reserved``.
    # | ``body.metadata`` 已由 ``ThreadPatchRequest._strip_reserved`` 剥离。
    try:
        await thread_store.update_metadata(thread_id, body.metadata)
    except Exception:
        logger.exception("Failed to patch thread %s", sanitize_log_param(thread_id))
        raise HTTPException(status_code=500, detail="Failed to update thread")

    # Re-read to get the merged metadata + refreshed updated_at
    # | 重新读取以获取合并后的元数据 + 刷新后的 updated_at
    record = await thread_store.get(thread_id) or record
    return ThreadResponse(
        thread_id=thread_id,
        status=record.get("status", "idle"),
        created_at=coerce_iso(record.get("created_at", "")),
        updated_at=coerce_iso(record.get("updated_at", "")),
        metadata=record.get("metadata", {}),
    )


@router.get("/{thread_id}", response_model=ThreadResponse)
@require_permission("threads", "read", owner_check=True)
async def get_thread(thread_id: str, request: Request) -> ThreadResponse:
    """Get thread info.

    Reads metadata from the ThreadMetaStore and derives the accurate
    execution status from the checkpointer.  Falls back to the checkpointer
    alone for threads that pre-date ThreadMetaStore adoption (backward compat).
    | 获取线程信息。

    从 ThreadMetaStore 读取元数据，并从 checkpointer 推导准确的执行状态。
    对于 ThreadMetaStore 采用之前的线程，回退到仅使用 checkpointer（向后兼容）。
    """
    from app.gateway.deps import get_thread_store

    thread_store = get_thread_store(request)
    checkpointer = get_checkpointer(request)

    record: dict | None = await thread_store.get(thread_id)

    # Derive accurate status from the checkpointer
    # | 从 checkpointer 推导准确的状态
    config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": ""}}
    try:
        checkpoint_tuple = await checkpointer.aget_tuple(config)
    except Exception:
        logger.exception("Failed to get checkpoint for thread %s", sanitize_log_param(thread_id))
        raise HTTPException(status_code=500, detail="Failed to get thread")

    if record is None and checkpoint_tuple is None:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    # If the thread exists in the checkpointer but not in thread_meta (e.g.
    # legacy data created before thread_meta adoption), synthesize a minimal
    # record from the checkpoint metadata.
    # | 如果线程存在于 checkpointer 中但不在 thread_meta 中（例如
    # thread_meta 采用之前创建的遗留数据），从检查点元数据合成最小记录。
    if record is None and checkpoint_tuple is not None:
        ckpt_meta = getattr(checkpoint_tuple, "metadata", {}) or {}
        record = {
            "thread_id": thread_id,
            "status": "idle",
            "created_at": coerce_iso(ckpt_meta.get("created_at", "")),
            "updated_at": coerce_iso(ckpt_meta.get("updated_at", ckpt_meta.get("created_at", ""))),
            "metadata": {k: v for k, v in ckpt_meta.items() if k not in ("created_at", "updated_at", "step", "source", "writes", "parents")},
        }

    if record is None:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    status = _derive_thread_status(checkpoint_tuple) if checkpoint_tuple is not None else record.get("status", "idle")
    checkpoint = getattr(checkpoint_tuple, "checkpoint", {}) or {} if checkpoint_tuple is not None else {}
    channel_values = checkpoint.get("channel_values", {})

    return ThreadResponse(
        thread_id=thread_id,
        status=status,
        created_at=coerce_iso(record.get("created_at", "")),
        updated_at=coerce_iso(record.get("updated_at", "")),
        metadata=record.get("metadata", {}),
        values=serialize_channel_values(channel_values),
    )


# ---------------------------------------------------------------------------
@router.get("/{thread_id}/state", response_model=ThreadStateResponse)
@require_permission("threads", "read", owner_check=True)
async def get_thread_state(thread_id: str, request: Request) -> ThreadStateResponse:
    """Get the latest state snapshot for a thread.

    Channel values are serialized to ensure LangChain message objects
    are converted to JSON-safe dicts.
    | 获取线程的最新状态快照。

    通道值被序列化以确保 LangChain 消息对象被转换为 JSON 安全的字典。
    """
    checkpointer = get_checkpointer(request)

    config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": ""}}
    try:
        checkpoint_tuple = await checkpointer.aget_tuple(config)
    except Exception:
        logger.exception("Failed to get state for thread %s", sanitize_log_param(thread_id))
        raise HTTPException(status_code=500, detail="Failed to get thread state")

    if checkpoint_tuple is None:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    checkpoint = getattr(checkpoint_tuple, "checkpoint", {}) or {}
    metadata = getattr(checkpoint_tuple, "metadata", {}) or {}
    checkpoint_id = None
    ckpt_config = getattr(checkpoint_tuple, "config", {})
    if ckpt_config:
        checkpoint_id = ckpt_config.get("configurable", {}).get("checkpoint_id")

    channel_values = checkpoint.get("channel_values", {})

    parent_config = getattr(checkpoint_tuple, "parent_config", None)
    parent_checkpoint_id = None
    if parent_config:
        parent_checkpoint_id = parent_config.get("configurable", {}).get("checkpoint_id")

    tasks_raw = getattr(checkpoint_tuple, "tasks", []) or []
    next_tasks = [t.name for t in tasks_raw if hasattr(t, "name")]
    tasks = [{"id": getattr(t, "id", ""), "name": getattr(t, "name", "")} for t in tasks_raw]

    values = serialize_channel_values(channel_values)

    return ThreadStateResponse(
        values=values,
        next=next_tasks,
        metadata=metadata,
        checkpoint={"id": checkpoint_id, "ts": coerce_iso(metadata.get("created_at", ""))},
        checkpoint_id=checkpoint_id,
        parent_checkpoint_id=parent_checkpoint_id,
        created_at=coerce_iso(metadata.get("created_at", "")),
        tasks=tasks,
    )


@router.post("/{thread_id}/state", response_model=ThreadStateResponse)
@require_permission("threads", "write", owner_check=True, require_existing=True)
async def update_thread_state(thread_id: str, body: ThreadStateUpdateRequest, request: Request) -> ThreadStateResponse:
    """Update thread state (e.g. for human-in-the-loop resume or title rename).

    Writes a new checkpoint that merges *body.values* into the latest
    channel values, then syncs any updated ``title`` field through the
    ThreadMetaStore abstraction so that ``/threads/search`` reflects the
    change immediately in both sqlite and memory backends.
    | 更新线程状态（例如用于人在回路中恢复或标题重命名）。

    写入一个新的检查点，将 *body.values* 合并到最新的通道值中，
    然后通过 ThreadMetaStore 抽象同步任何更新的 ``title`` 字段，
    使 ``/threads/search`` 在 sqlite 和 memory 后端中立即反映更改。
    """
    from app.gateway.deps import get_thread_store

    checkpointer = get_checkpointer(request)
    thread_store = get_thread_store(request)

    # checkpoint_ns must be present in the config for aput — default to ""
    # (the root graph namespace).  checkpoint_id is optional; omitting it
    # fetches the latest checkpoint for the thread.
    # | checkpoint_ns 必须存在于 aput 的配置中 — 默认为 ""（根图命名空间）。
    # checkpoint_id 是可选的；省略它会获取线程的最新检查点。
    read_config: dict[str, Any] = {
        "configurable": {
            "thread_id": thread_id,
            "checkpoint_ns": "",
        }
    }
    if body.checkpoint_id:
        read_config["configurable"]["checkpoint_id"] = body.checkpoint_id

    try:
        checkpoint_tuple = await checkpointer.aget_tuple(read_config)
    except Exception:
        logger.exception("Failed to get state for thread %s", sanitize_log_param(thread_id))
        raise HTTPException(status_code=500, detail="Failed to get thread state")

    if checkpoint_tuple is None:
        raise HTTPException(status_code=404, detail=f"Thread {thread_id} not found")

    # Work on mutable copies so we don't accidentally mutate cached objects.
    # | 使用可变副本以避免意外修改缓存对象。
    checkpoint: dict[str, Any] = dict(getattr(checkpoint_tuple, "checkpoint", {}) or {})
    metadata: dict[str, Any] = dict(getattr(checkpoint_tuple, "metadata", {}) or {})
    channel_values: dict[str, Any] = dict(checkpoint.get("channel_values", {}))

    if body.values:
        channel_values.update(body.values)

    checkpoint["channel_values"] = channel_values
    metadata["updated_at"] = now_iso()

    if body.as_node:
        metadata["source"] = "update"
        metadata["step"] = metadata.get("step", 0) + 1
        metadata["writes"] = {body.as_node: body.values}

    # Assign a new checkpoint ID so aput performs an INSERT rather than an
    # in-place REPLACE of the existing row.  Use uuid6 (time-ordered) rather
    # than uuid4 (random) so the new ID is always lexicographically greater
    # than the previous one — LangGraph's checkpointers determine the "latest"
    # checkpoint by max(checkpoint_ids) string order, matching the uuid6 epoch.
    # | 分配新的检查点 ID，使 aput 执行 INSERT 而不是原地 REPLACE 现有行。
    # 使用 uuid6（时间有序）而不是 uuid4（随机），使新 ID 始终按字典序大于前一个 —
    # LangGraph 的 checkpointers 通过 max(checkpoint_ids) 字符串顺序确定"最新"检查点，与 uuid6 epoch 匹配。
    checkpoint["id"] = str(uuid6())

    # aput requires checkpoint_ns in the config — use the same config used for the
    # read (which always includes checkpoint_ns=""). The fresh checkpoint ID is
    # assigned above via checkpoint["id"]; keep checkpoint_id out of the config so
    # the write is keyed by the new checkpoint payload rather than the prior read.
    # All supported savers (InMemorySaver, AsyncSqliteSaver, AsyncPostgresSaver)
    # persist and echo back checkpoint["id"] verbatim — none mint their own — so
    # the new_config below carries the uuid6 we assigned here. (Regression-locked
    # by test_update_thread_state_inserts_new_checkpoint_each_call.)
    # | aput 要求配置中包含 checkpoint_ns — 使用与读取相同的配置（始终包含 checkpoint_ns=""）。
    # 新的检查点 ID 已通过 checkpoint["id"] 分配；将 checkpoint_id 排除在配置之外，
    # 使写入以新的检查点负载为键，而不是先前的读取。
    # 所有支持的 saver（InMemorySaver、AsyncSqliteSaver、AsyncPostgresSaver）
    # 都会原样持久化并回显 checkpoint["id"] — 不会自行生成 — 因此下面的 new_config 携带我们在此分配的 uuid6。
    # （由 test_update_thread_state_inserts_new_checkpoint_each_call 回归锁定。）
    write_config: dict[str, Any] = {
        "configurable": {
            "thread_id": thread_id,
            "checkpoint_ns": "",
        }
    }
    try:
        new_config = await checkpointer.aput(write_config, checkpoint, metadata, {})
    except Exception:
        logger.exception("Failed to update state for thread %s", sanitize_log_param(thread_id))
        raise HTTPException(status_code=500, detail="Failed to update thread state")

    new_checkpoint_id: str | None = None
    if isinstance(new_config, dict):
        new_checkpoint_id = new_config.get("configurable", {}).get("checkpoint_id")

    # Sync title changes through the ThreadMetaStore abstraction so /threads/search
    # reflects them immediately in both sqlite and memory backends.
    # | 通过 ThreadMetaStore 抽象同步标题更改，使 /threads/search 在 sqlite 和 memory 后端中立即反映它们。
    if thread_store and body.values and "title" in body.values:
        new_title = body.values["title"]
        if new_title:  # Skip empty strings and None | 跳过空字符串和 None
            try:
                await thread_store.update_display_name(thread_id, new_title)
            except Exception:
                logger.debug("Failed to sync title to thread_meta for %s (non-fatal)", sanitize_log_param(thread_id))

    return ThreadStateResponse(
        values=serialize_channel_values(channel_values),
        next=[],
        metadata=metadata,
        checkpoint_id=new_checkpoint_id,
        created_at=coerce_iso(metadata.get("created_at", "")),
    )


@router.post("/{thread_id}/history", response_model=list[HistoryEntry])
@require_permission("threads", "read", owner_check=True)
async def get_thread_history(thread_id: str, body: ThreadHistoryRequest, request: Request) -> list[HistoryEntry]:
    """Get checkpoint history for a thread.

    Messages are read from the checkpointer's channel values (the
    authoritative source) and serialized via
    :func:`~deerflow.runtime.serialization.serialize_channel_values`.
    Only the latest (first) checkpoint carries the ``messages`` key to
    avoid duplicating them across every entry.
    | 获取线程的检查点历史。

    消息从 checkpointer 的通道值（权威来源）中读取，并通过
    :func:`~deerflow.runtime.serialization.serialize_channel_values` 序列化。
    只有最新（第一个）检查点携带 ``messages`` 键，以避免在每个条目中重复它们。
    """
    checkpointer = get_checkpointer(request)

    config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
    if body.before:
        config["configurable"]["checkpoint_id"] = body.before

    entries: list[HistoryEntry] = []
    is_latest_checkpoint = True
    try:
        async for checkpoint_tuple in checkpointer.alist(config, limit=body.limit):
            ckpt_config = getattr(checkpoint_tuple, "config", {})
            parent_config = getattr(checkpoint_tuple, "parent_config", None)
            metadata = getattr(checkpoint_tuple, "metadata", {}) or {}
            checkpoint = getattr(checkpoint_tuple, "checkpoint", {}) or {}

            checkpoint_id = ckpt_config.get("configurable", {}).get("checkpoint_id", "")
            parent_id = None
            if parent_config:
                parent_id = parent_config.get("configurable", {}).get("checkpoint_id")

            channel_values = checkpoint.get("channel_values", {})

            # Build values from checkpoint channel_values
            # | 从检查点 channel_values 构建值
            values: dict[str, Any] = {}
            if title := channel_values.get("title"):
                values["title"] = title
            if thread_data := channel_values.get("thread_data"):
                values["thread_data"] = thread_data

            # Attach messages only to the latest checkpoint entry.
            # | 仅将消息附加到最新的检查点条目。
            if is_latest_checkpoint:
                messages = channel_values.get("messages")
                if messages:
                    values["messages"] = serialize_channel_values({"messages": messages}).get("messages", [])
            is_latest_checkpoint = False

            # Derive next tasks | 推导下一个任务
            tasks_raw = getattr(checkpoint_tuple, "tasks", []) or []
            next_tasks = [t.name for t in tasks_raw if hasattr(t, "name")]

            # Strip LangGraph internal keys from metadata
            # | 从元数据中剥离 LangGraph 内部键
            user_meta = {k: v for k, v in metadata.items() if k not in ("created_at", "updated_at", "step", "source", "writes", "parents")}
            # Keep step for ordering context
            # | 保留 step 用于排序上下文
            if "step" in metadata:
                user_meta["step"] = metadata["step"]

            entries.append(
                HistoryEntry(
                    checkpoint_id=checkpoint_id,
                    parent_checkpoint_id=parent_id,
                    metadata=user_meta,
                    values=values,
                    created_at=coerce_iso(metadata.get("created_at", "")),
                    next=next_tasks,
                )
            )
    except Exception:
        logger.exception("Failed to get history for thread %s", sanitize_log_param(thread_id))
        raise HTTPException(status_code=500, detail="Failed to get thread history")

    return entries
