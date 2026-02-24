"""内存机制的配置。"""

from pydantic import BaseModel, Field


class MemoryConfig(BaseModel):
    """全局内存机制的配置。

    该类用于配置对话记忆系统的各项参数，包括启用状态、存储路径、
    防抖时间、事实存储限制、置信度阈值和注入设置等。

    Attributes:
        enabled: 是否启用内存机制。
        storage_path: 存储内存数据的路径（相对于 backend 目录）。
        debounce_seconds: 在处理排队更新前等待的秒数（去抖动）。
        model_name: 用于内存更新的模型名称（None 表示使用默认模型）。
        max_facts: 要存储的事实的最大数量。
        fact_confidence_threshold: 存储事实的最小置信度阈值。
        injection_enabled: 是否将内存注入系统提示中。
        max_injection_tokens: 用于内存注入的最大标记数。
    """

    enabled: bool = Field(
        default=True,
        description="是否启用内存机制",
    )
    storage_path: str = Field(
        default=".deer-flow/memory.json",
        description="存储内存数据的路径（相对于 backend 目录）",
    )
    debounce_seconds: int = Field(
        default=30,
        ge=1,
        le=300,
        description="在处理排队更新前等待的秒数（去抖动）",
    )
    model_name: str | None = Field(
        default=None,
        description="用于内存更新的模型名称（None 表示使用默认模型）",
    )
    max_facts: int = Field(
        default=100,
        ge=10,
        le=500,
        description="要存储的事实的最大数量",
    )
    fact_confidence_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="存储事实的最小置信度阈值",
    )
    injection_enabled: bool = Field(
        default=True,
        description="是否将内存注入系统提示中",
    )
    max_injection_tokens: int = Field(
        default=2000,
        ge=100,
        le=8000,
        description="用于内存注入的最大标记数",
    )


_memory_config: MemoryConfig = MemoryConfig()


def get_memory_config() -> MemoryConfig:
    """获取当前内存配置。

    Returns:
        当前的 MemoryConfig 实例。
    """
    return _memory_config


def set_memory_config(config: MemoryConfig) -> None:
    """设置内存配置。

    Args:
        config: 要设置的 MemoryConfig 实例。
    """
    global _memory_config
    _memory_config = config


def load_memory_config_from_dict(config_dict: dict) -> None:
    """从字典加载内存配置。

    Args:
        config_dict: 包含配置参数的字典。
    """
    global _memory_config
    _memory_config = MemoryConfig(**config_dict)
