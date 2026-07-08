"""MessageBus — async pub/sub hub that decouples channels from the agent dispatcher.

MessageBus — 异步发布/订阅中心，解耦 channels 和 agent 调度器。
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

PENDING_CLARIFICATION_METADATA_KEY = "pending_clarification"
RESOLVED_FROM_PENDING_CLARIFICATION_METADATA_KEY = "resolved_from_pending_clarification"


# ---------------------------------------------------------------------------
# Message types
# | 消息类型
# ---------------------------------------------------------------------------


class InboundMessageType(StrEnum):
    """Types of messages arriving from IM channels.

    从 IM channels 到达的消息类型。
    """

    CHAT = "chat"
    COMMAND = "command"


@dataclass
class InboundMessage:
    """A message arriving from an IM channel toward the agent dispatcher.

    Attributes:
        channel_name: Name of the source channel (e.g. "feishu", "slack").
        chat_id: Platform-specific chat/conversation identifier.
        user_id: Platform-specific user identifier.
        text: The message text.
        msg_type: Whether this is a regular chat message or a command.
        thread_ts: Optional platform thread identifier (for threaded replies).
        topic_id: Conversation topic identifier used to map to a DeerFlow thread.
            Messages sharing the same ``topic_id`` within a ``chat_id`` will
            reuse the same DeerFlow thread.  When ``None``, each message
            creates a new thread (one-shot Q&A).
        files: Optional list of file attachments (platform-specific dicts).
        metadata: Arbitrary extra data from the channel.
        created_at: Unix timestamp when the message was created.

    从 IM channel 到达 agent 调度器的消息。

    属性:
        channel_name: 源 channel 名称（例如 "feishu"、"slack"）。
        chat_id: 平台特定的聊天/对话标识符。
        user_id: 平台特定的用户标识符。
        text: 消息文本。
        msg_type: 是常规聊天消息还是命令。
        thread_ts: 可选的平台线程标识符（用于线程回复）。
        topic_id: 用于映射到 DeerFlow 线程的对话主题标识符。
            在同一个 ``chat_id`` 内共享相同 ``topic_id`` 的消息将
            重用同一个 DeerFlow 线程。当为 ``None`` 时，每条消息
            创建新线程（一次性问答）。
        files: 可选的文件附件列表（平台特定的 dict）。
        metadata: 来自 channel 的任意额外数据。
        created_at: 消息创建时的 Unix 时间戳。
    """

    channel_name: str
    chat_id: str
    user_id: str
    text: str
    msg_type: InboundMessageType = InboundMessageType.CHAT
    thread_ts: str | None = None
    topic_id: str | None = None
    files: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


@dataclass
class ResolvedAttachment:
    """A file attachment resolved to a host filesystem path, ready for upload.

    Attributes:
        virtual_path: Original virtual path (e.g. /mnt/user-data/outputs/report.pdf).
        actual_path: Resolved host filesystem path.
        filename: Basename of the file.
        mime_type: MIME type (e.g. "application/pdf").
        size: File size in bytes.
        is_image: True for image/* MIME types (platforms may handle images differently).

    已解析到主机文件系统路径的文件附件，准备上传。

    属性:
        virtual_path: 原始虚拟路径（例如 /mnt/user-data/outputs/report.pdf）。
        actual_path: 解析后的主机文件系统路径。
        filename: 文件的基本名称。
        mime_type: MIME 类型（例如 "application/pdf"）。
        size: 文件大小（字节）。
        is_image: 对于 image/* MIME 类型为 True（平台可能以不同方式处理图像）。
    """

    virtual_path: str
    actual_path: Path
    filename: str
    mime_type: str
    size: int
    is_image: bool


@dataclass
class OutboundMessage:
    """A message from the agent dispatcher back to a channel.

    Attributes:
        channel_name: Target channel name (used for routing).
        chat_id: Target chat/conversation identifier.
        thread_id: DeerFlow thread ID that produced this response.
        text: The response text.
        artifacts: List of artifact paths produced by the agent.
        is_final: Whether this is the final message in the response stream.
        thread_ts: Optional platform thread identifier for threaded replies.
        metadata: Arbitrary extra data.
        created_at: Unix timestamp.

    从 agent 调度器返回到 channel 的消息。

    属性:
        channel_name: 目标 channel 名称（用于路由）。
        chat_id: 目标聊天/对话标识符。
        thread_id: 产生此响应的 DeerFlow 线程 ID。
        text: 响应文本。
        artifacts: agent 产生的 artifact 路径列表。
        is_final: 这是否是响应流中的最后一条消息。
        thread_ts: 可选的平台线程标识符（用于线程回复）。
        metadata: 任意额外数据。
        created_at: Unix 时间戳。
    """

    channel_name: str
    chat_id: str
    thread_id: str
    text: str
    artifacts: list[str] = field(default_factory=list)
    attachments: list[ResolvedAttachment] = field(default_factory=list)
    is_final: bool = True
    thread_ts: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


# ---------------------------------------------------------------------------
# MessageBus
# | MessageBus
# ---------------------------------------------------------------------------

OutboundCallback = Callable[[OutboundMessage], Coroutine[Any, Any, None]]


class MessageBus:
    """Async pub/sub hub connecting channels and the agent dispatcher.

    Channels publish inbound messages; the dispatcher consumes them.
    The dispatcher publishes outbound messages; channels receive them
    via registered callbacks.

    异步发布/订阅中心，连接 channels 和 agent 调度器。
    Channels 发布入站消息；调度器消费它们。
    调度器发布出站消息；channels 通过注册的回调接收它们。
    """

    def __init__(self) -> None:
        self._inbound_queue: asyncio.Queue[InboundMessage] = asyncio.Queue()
        self._outbound_listeners: list[OutboundCallback] = []

    # -- inbound -----------------------------------------------------------
    # | 入站

    async def publish_inbound(self, msg: InboundMessage) -> None:
        """Enqueue an inbound message from a channel.

        将来自 channel 的入站消息入队。
        """
        await self._inbound_queue.put(msg)
        logger.info(
            "[Bus] inbound enqueued: channel=%s, chat_id=%s, type=%s, queue_size=%d",
            msg.channel_name,
            msg.chat_id,
            msg.msg_type.value,
            self._inbound_queue.qsize(),
        )

    async def get_inbound(self) -> InboundMessage:
        """Block until the next inbound message is available.

        阻塞直到下一条入站消息可用。
        """
        return await self._inbound_queue.get()

    @property
    def inbound_queue(self) -> asyncio.Queue[InboundMessage]:
        return self._inbound_queue

    # -- outbound ----------------------------------------------------------

    def subscribe_outbound(self, callback: OutboundCallback) -> None:
        """Register an async callback for outbound messages."""
        self._outbound_listeners.append(callback)

    def unsubscribe_outbound(self, callback: OutboundCallback) -> None:
        """Remove a previously registered outbound callback."""
        self._outbound_listeners = [cb for cb in self._outbound_listeners if cb is not callback]

    async def publish_outbound(self, msg: OutboundMessage) -> None:
        """Dispatch an outbound message to all registered listeners."""
        logger.info(
            "[Bus] outbound dispatching: channel=%s, chat_id=%s, listeners=%d, text_len=%d",
            msg.channel_name,
            msg.chat_id,
            len(self._outbound_listeners),
            len(msg.text),
        )
        for callback in self._outbound_listeners:
            try:
                await callback(msg)
            except Exception:
                logger.exception("Error in outbound callback for channel=%s", msg.channel_name)
