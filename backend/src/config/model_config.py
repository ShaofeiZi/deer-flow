from pydantic import BaseModel, ConfigDict, Field


class ModelConfig(BaseModel):
    """模型的配置。

    该类用于配置 AI 模型的各项参数，包括名称、显示名称、描述、
    提供者类路径、模型名称、思考模式支持等。

    Attributes:
        name: 模型的唯一名称。
        display_name: 模型的显示名称。
        description: 模型的描述。
        use: 模型提供者的类路径（例如 langchain_openai.ChatOpenAI）。
        model: 模型名称。
        supports_thinking: 模型是否支持思考模式。
        when_thinking_enabled: 启用思考模式时传递给模型的额外设置。
        supports_vision: 模型是否支持视觉/图像输入。
    """

    name: str = Field(..., description="模型的唯一名称")
    display_name: str | None = Field(..., default_factory=lambda: None, description="模型的显示名称")
    description: str | None = Field(..., default_factory=lambda: None, description="模型的描述")
    use: str = Field(
        ...,
        description="模型提供者的类路径（例如 langchain_openai.ChatOpenAI）",
    )
    model: str = Field(..., description="模型名称")
    model_config = ConfigDict(extra="allow")
    supports_thinking: bool = Field(default_factory=lambda: False, description="模型是否支持思考模式")
    when_thinking_enabled: dict | None = Field(
        default_factory=lambda: None,
        description="启用思考模式时传递给模型的额外设置",
    )
    supports_vision: bool = Field(default_factory=lambda: False, description="模型是否支持视觉/图像输入")
