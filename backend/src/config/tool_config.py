from pydantic import BaseModel, ConfigDict, Field


class ToolGroupConfig(BaseModel):
    """工具组配置。

    该类用于配置工具组的名称。

    Attributes:
        name: 工具组的唯一名称。
    """

    name: str = Field(..., description="工具组的唯一名称")
    model_config = ConfigDict(extra="allow")


class ToolConfig(BaseModel):
    """工具配置。

    该类用于配置工具的名称、所属组和提供者。

    Attributes:
        name: 工具的唯一名称。
        group: 工具所属的组名。
        use: 工具提供者的变量名（例如 src.sandbox.tools:bash_tool）。
    """

    name: str = Field(..., description="工具的唯一名称")
    group: str = Field(..., description="工具所属的组名")
    use: str = Field(
        ...,
        description="工具提供者的变量名（例如 src.sandbox.tools:bash_tool）",
    )
    model_config = ConfigDict(extra="allow")
