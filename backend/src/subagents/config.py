"""子代理配置定义。"""

from dataclasses import dataclass, field


@dataclass
class SubagentConfig:
    """子代理的配置。

    Attributes:
        name: 子代理的唯一标识符。
        description: 描述何时应将任务委托给此子代理。
        system_prompt: 指导子代理行为的系统提示。
        tools: 允许使用的工具名称列表。如果为 None，则继承所有工具。
        disallowed_tools: 禁止使用的工具名称列表。
        model: 使用的模型 - 'inherit' 使用父代理的模型。
        max_turns: 停止前代理的最大轮次。
        timeout_seconds: 最大执行时间（秒）（默认：900 = 15 分钟）。
    """

    name: str
    description: str
    system_prompt: str
    tools: list[str] | None = None
    disallowed_tools: list[str] | None = field(default_factory=lambda: ["task"])
    model: str = "inherit"
    max_turns: int = 50
    timeout_seconds: int = 900
