"""子代理注册表，用于管理可用的子代理。"""

from src.subagents.builtins import BUILTIN_SUBAGENTS
from src.subagents.config import SubagentConfig


def get_subagent_config(name: str) -> SubagentConfig | None:
    """按名称获取子代理配置。

    Args:
        name: 子代理名称。

    Returns:
        如果找到则返回 SubagentConfig，否则返回 None。
    """
    return BUILTIN_SUBAGENTS.get(name)


def list_subagents() -> list[SubagentConfig]:
    """列出所有可用的子代理配置。

    Returns:
        所有已注册的 SubagentConfig 实例列表。
    """
    return list(BUILTIN_SUBAGENTS.values())


def get_subagent_names() -> list[str]:
    """获取所有可用的子代理名称。

    Returns:
        子代理名称列表。
    """
    return list(BUILTIN_SUBAGENTS.keys())
