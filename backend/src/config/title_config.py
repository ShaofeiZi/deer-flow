"""自动线程标题生成的配置。"""

from pydantic import BaseModel, Field


class TitleConfig(BaseModel):
    """自动线程标题生成的配置。

    该类用于配置自动生成对话标题的各项参数，包括启用状态、
    字数限制、字符数限制、模型名称和提示模板等。

    Attributes:
        enabled: 是否启用自动标题生成。
        max_words: 生成标题的最大字数。
        max_chars: 生成标题的最大字符数。
        model_name: 用于标题生成的模型名称（None 表示使用默认模型）。
        prompt_template: 标题生成的提示模板。
    """

    enabled: bool = Field(
        default=True,
        description="是否启用自动标题生成",
    )
    max_words: int = Field(
        default=6,
        ge=1,
        le=20,
        description="生成标题的最大字数",
    )
    max_chars: int = Field(
        default=60,
        ge=10,
        le=200,
        description="生成标题的最大字符数",
    )
    model_name: str | None = Field(
        default=None,
        description="用于标题生成的模型名称（None 表示使用默认模型）",
    )
    prompt_template: str = Field(
        default=("为以下对话生成一个简洁的标题（最多 {max_words} 个词）。\n用户：{user_msg}\n助手：{assistant_msg}\n\n仅返回标题，不要引号，不要解释。"),
        description="标题生成的提示模板",
    )


_title_config: TitleConfig = TitleConfig()


def get_title_config() -> TitleConfig:
    """获取当前标题配置。

    Returns:
        当前的 TitleConfig 实例。
    """
    return _title_config


def set_title_config(config: TitleConfig) -> None:
    """设置标题配置。

    Args:
        config: 要设置的 TitleConfig 实例。
    """
    global _title_config
    _title_config = config


def load_title_config_from_dict(config_dict: dict) -> None:
    """从字典加载标题配置。

    Args:
        config_dict: 包含配置参数的字典。
    """
    global _title_config
    _title_config = TitleConfig(**config_dict)
