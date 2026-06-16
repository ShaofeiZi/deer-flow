"""Shared command definitions used by all channel implementations.

Keeping the authoritative command set in one place ensures that channel
parsers (e.g. Feishu) and the ChannelManager dispatcher stay in sync
automatically — adding or removing a command here is the single edit
required.

所有 channel 实现共享的命令定义。
将权威命令集集中在一个地方，确保 channel 解析器（例如 Feishu）
和 ChannelManager 调度器自动保持同步 — 在此处添加或删除命令是唯一需要的编辑。
"""

from __future__ import annotations

KNOWN_CHANNEL_COMMANDS: frozenset[str] = frozenset(
    {
        "/bootstrap",
        "/new",
        "/status",
        "/models",
        "/memory",
        "/help",
    }
)


def is_known_channel_command(text: str) -> bool:
    """Return whether text starts with a registered channel control command.

    返回文本是否以已注册的 channel 控制命令开头。
    """
    if not text.startswith("/"):
        return False
    return text.split(maxsplit=1)[0].lower() in KNOWN_CHANNEL_COMMANDS
