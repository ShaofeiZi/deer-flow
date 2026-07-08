"""Abstract base class for IM channels.

IM channels 的抽象基类。
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

from app.channels.message_bus import InboundMessage, InboundMessageType, MessageBus, OutboundMessage, ResolvedAttachment

logger = logging.getLogger(__name__)


class Channel(ABC):
    """Base class for all IM channel implementations.

    Each channel connects to an external messaging platform and:
    1. Receives messages, wraps them as InboundMessage, publishes to the bus.
    2. Subscribes to outbound messages and sends replies back to the platform.

    Subclasses must implement ``start``, ``stop``, and ``send``.

    所有 IM channel 实现的基类。
    每个 channel 连接到外部消息平台并：
    1. 接收消息，包装为 InboundMessage，发布到 bus。
    2. 订阅出站消息并将回复发送回平台。

    子类必须实现 ``start``、``stop`` 和 ``send``。
    """

    def __init__(self, name: str, bus: MessageBus, config: dict[str, Any]) -> None:
        self.name = name
        self.bus = bus
        self.config = config
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def supports_streaming(self) -> bool:
        return False

    # -- lifecycle ---------------------------------------------------------
    # | 生命周期

    @abstractmethod
    async def start(self) -> None:
        """Start listening for messages from the external platform.

        开始监听来自外部平台的消息。
        """

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully stop the channel.

        优雅地停止 channel。
        """

    # -- outbound ----------------------------------------------------------
    # | 出站

    @abstractmethod
    async def send(self, msg: OutboundMessage) -> None:
        """Send a message back to the external platform.

        The implementation should use ``msg.chat_id`` and ``msg.thread_ts``
        to route the reply to the correct conversation/thread.

        将消息发送回外部平台。
        实现应使用 ``msg.chat_id`` 和 ``msg.thread_ts``
        将回复路由到正确的对话/线程。
        """

    async def send_file(self, msg: OutboundMessage, attachment: ResolvedAttachment) -> bool:
        """Upload a single file attachment to the platform.

        Returns True if the upload succeeded, False otherwise.
        Default implementation returns False (no file upload support).

        将单个文件附件上传到平台。
        上传成功返回 True，否则返回 False。
        默认实现返回 False（不支持文件上传）。
        """
        return False

    # -- helpers -----------------------------------------------------------
    # | 辅助方法

    def _make_inbound(
        self,
        chat_id: str,
        user_id: str,
        text: str,
        *,
        msg_type: InboundMessageType = InboundMessageType.CHAT,
        thread_ts: str | None = None,
        files: list[dict[str, Any]] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> InboundMessage:
        """Convenience factory for creating InboundMessage instances.

        创建 InboundMessage 实例的便捷工厂方法。
        """
        return InboundMessage(
            channel_name=self.name,
            chat_id=chat_id,
            user_id=user_id,
            text=text,
            msg_type=msg_type,
            thread_ts=thread_ts,
            files=files or [],
            metadata=metadata or {},
        )

    async def _on_outbound(self, msg: OutboundMessage) -> None:
        """Outbound callback registered with the bus.

        Only forwards messages targeted at this channel.
        Sends the text message first, then uploads any file attachments.
        File uploads are skipped entirely when the text send fails to avoid
        partial deliveries (files without accompanying text).

        在 bus 上注册的出站回调。
        仅转发针对此 channel 的消息。
        先发送文本消息，然后上传任何文件附件。
        当文本发送失败时，完全跳过文件上传，以避免部分交付（没有附带文本的文件）。
        """
        if msg.channel_name == self.name:
            try:
                await self.send(msg)
            except Exception:
                logger.exception("Failed to send outbound message on channel %s", self.name)
                return  # Do not attempt file uploads when the text message failed
                # | 文本消息失败时不要尝试文件上传

            for attachment in msg.attachments:
                try:
                    success = await self.send_file(msg, attachment)
                    if not success:
                        logger.warning("[%s] file upload skipped for %s", self.name, attachment.filename)
                except Exception:
                    logger.exception("[%s] failed to upload file %s", self.name, attachment.filename)

    async def receive_file(self, msg: InboundMessage, thread_id: str) -> InboundMessage:
        """
        Optionally process and materialize inbound file attachments for this channel.

        By default, this method does nothing and simply returns the original message.
        Subclasses (e.g. FeishuChannel) may override this to download files (images, documents, etc)
        referenced in msg.files, save them to the sandbox, and update msg.text to include
        the sandbox file paths for downstream model consumption.

        Args:
            msg: The inbound message, possibly containing file metadata in msg.files.
            thread_id: The resolved DeerFlow thread ID for sandbox path context.

        Returns:
            The (possibly modified) InboundMessage, with text and/or files updated as needed.
        """
        return msg
