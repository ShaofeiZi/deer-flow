"""对话摘要的配置。"""

from typing import Literal

from pydantic import BaseModel, Field

ContextSizeType = Literal["fraction", "tokens", "messages"]


class ContextSize(BaseModel):
    """上下文大小规格，用于触发或保留参数。

    该类用于指定上下文大小的类型和值。

    Attributes:
        type: 上下文大小规格的类型。
        value: 上下文大小规格的值。
    """

    type: ContextSizeType = Field(description="上下文大小规格的类型")
    value: int | float = Field(description="上下文大小规格的值")

    def to_tuple(self) -> tuple[ContextSizeType, int | float]:
        """转换为 SummarizationMiddleware 期望的元组格式。

        Returns:
            包含类型和值的元组。
        """
        return (self.type, self.value)


class SummarizationConfig(BaseModel):
    """自动对话摘要的配置。

    该类用于配置自动对话摘要的各项参数，包括启用状态、
    模型名称、触发条件、保留策略、令牌限制和自定义提示等。

    Attributes:
        enabled: 是否启用自动对话摘要。
        model_name: 用于摘要的模型名称（None 表示使用轻量级模型）。
        trigger: 触发摘要的一个或多个阈值。当任一阈值满足时，执行摘要。
        keep: 摘要后的上下文保留策略。指定保留多少历史记录。
        trim_tokens_to_summarize: 准备摘要消息时保留的最大令牌数。传入 null 以跳过裁剪。
        summary_prompt: 生成摘要的自定义提示模板。如果未提供，使用默认的 LangChain 提示。
    """

    enabled: bool = Field(
        default=False,
        description="是否启用自动对话摘要",
    )
    model_name: str | None = Field(
        default=None,
        description="用于摘要的模型名称（None 表示使用轻量级模型）",
    )
    trigger: ContextSize | list[ContextSize] | None = Field(
        default=None,
        description="触发摘要的一个或多个阈值。当任一阈值满足时，执行摘要。"
        "示例：{'type': 'messages', 'value': 50} 在 50 条消息时触发，"
        "{'type': 'tokens', 'value': 4000} 在 4000 个令牌时触发，"
        "{'type': 'fraction', 'value': 0.8} 在模型最大输入令牌的 80% 时触发",
    )
    keep: ContextSize = Field(
        default_factory=lambda: ContextSize(type="messages", value=20),
        description="摘要后的上下文保留策略。指定保留多少历史记录。"
        "示例：{'type': 'messages', 'value': 20} 保留 20 条消息，"
        "{'type': 'tokens', 'value': 3000} 保留 3000 个令牌，"
        "{'type': 'fraction', 'value': 0.3} 保留模型最大输入令牌的 30%",
    )
    trim_tokens_to_summarize: int | None = Field(
        default=4000,
        description="准备摘要消息时保留的最大令牌数。传入 null 以跳过裁剪。",
    )
    summary_prompt: str | None = Field(
        default=None,
        description="生成摘要的自定义提示模板。如果未提供，使用默认的 LangChain 提示。",
    )


_summarization_config: SummarizationConfig = SummarizationConfig()


def get_summarization_config() -> SummarizationConfig:
    """获取当前摘要配置。

    Returns:
        当前的 SummarizationConfig 实例。
    """
    return _summarization_config


def set_summarization_config(config: SummarizationConfig) -> None:
    """设置摘要配置。

    Args:
        config: 要设置的 SummarizationConfig 实例。
    """
    global _summarization_config
    _summarization_config = config


def load_summarization_config_from_dict(config_dict: dict) -> None:
    """从字典加载摘要配置。

    Args:
        config_dict: 包含配置参数的字典。
    """
    global _summarization_config
    _summarization_config = SummarizationConfig(**config_dict)
