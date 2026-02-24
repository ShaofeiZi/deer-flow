"""统一的 MCP 服务器与技能扩展配置。"""

import json
import os
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class McpServerConfig(BaseModel):
    """单个 MCP 服务器的配置。

    该类用于配置单个 MCP 服务器的连接信息，包括传输类型、启动命令、
    环境变量、URL 地址等配置项。

    Attributes:
        enabled: 是否启用该 MCP 服务器。
        type: 传输类型，支持 'stdio'、'sse' 或 'http'。
        command: 启动 MCP 服务器的命令（适用于 stdio 类型）。
        args: 传递给命令的参数列表（适用于 stdio 类型）。
        env: MCP 服务器的环境变量。
        url: MCP 服务器的 URL 地址（适用于 sse 或 http 类型）。
        headers: HTTP 请求头（适用于 sse 或 http 类型）。
        description: MCP 服务器功能的可读描述。
    """

    enabled: bool = Field(default=True, description="是否启用该 MCP 服务器")
    type: str = Field(default="stdio", description="传输类型：'stdio'、'sse' 或 'http'")
    command: str | None = Field(default=None, description="启动 MCP 服务器的命令（适用于 stdio 类型）")
    args: list[str] = Field(default_factory=list, description="传递给命令的参数列表（适用于 stdio 类型）")
    env: dict[str, str] = Field(default_factory=dict, description="MCP 服务器的环境变量")
    url: str | None = Field(default=None, description="MCP 服务器的 URL 地址（适用于 sse 或 http 类型）")
    headers: dict[str, str] = Field(default_factory=dict, description="HTTP 请求头（适用于 sse 或 http 类型）")
    description: str = Field(default="", description="MCP 服务器功能的可读描述")
    model_config = ConfigDict(extra="allow")


class SkillStateConfig(BaseModel):
    """单个技能状态的配置。

    该类用于配置单个技能的启用状态。

    Attributes:
        enabled: 是否启用该技能。
    """

    enabled: bool = Field(default=True, description="是否启用该技能")


class ExtensionsConfig(BaseModel):
    """统一的 MCP 服务器和技能配置。

    该类是扩展配置的主模型，包含 MCP 服务器和技能的状态配置。

    Attributes:
        mcp_servers: MCP 服务器名称到配置的映射。
        skills: 技能名称到状态配置的映射。
    """

    mcp_servers: dict[str, McpServerConfig] = Field(
        default_factory=dict,
        description="MCP 服务器名称到配置的映射",
        alias="mcpServers",
    )
    skills: dict[str, SkillStateConfig] = Field(
        default_factory=dict,
        description="技能名称到状态配置的映射",
    )
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @classmethod
    def resolve_config_path(cls, config_path: str | None = None) -> Path | None:
        """解析扩展配置文件路径。

        按以下优先级查找配置文件：
        1. 如果提供了 `config_path` 参数，则使用它。
        2. 如果提供了环境变量 `DEER_FLOW_EXTENSIONS_CONFIG_PATH`，则使用它。
        3. 否则，在当前目录查找 `extensions_config.json`，再在父目录中查找。
        4. 为向后兼容，如果未找到 `extensions_config.json`，也检查 `mcp_config.json`。
        5. 未找到时返回 None（扩展配置为可选）。

        Args:
            config_path: 可选的扩展配置文件路径。

        Returns:
            找到时返回扩展配置文件的路径，否则返回 None。

        Raises:
            FileNotFoundError: 指定的配置文件不存在时抛出。
        """
        if config_path:
            path = Path(config_path)
            if not path.exists():
                raise FileNotFoundError(f"参数 `config_path` 指定的扩展配置文件在 {path} 未找到")
            return path
        elif os.getenv("DEER_FLOW_EXTENSIONS_CONFIG_PATH"):
            path = Path(os.getenv("DEER_FLOW_EXTENSIONS_CONFIG_PATH"))
            if not path.exists():
                raise FileNotFoundError(f"环境变量 `DEER_FLOW_EXTENSIONS_CONFIG_PATH` 指定的扩展配置文件在 {path} 未找到")
            return path
        else:
            path = Path(os.getcwd()) / "extensions_config.json"
            if path.exists():
                return path

            path = Path(os.getcwd()).parent / "extensions_config.json"
            if path.exists():
                return path

            path = Path(os.getcwd()) / "mcp_config.json"
            if path.exists():
                return path

            path = Path(os.getcwd()).parent / "mcp_config.json"
            if path.exists():
                return path

            return None

    @classmethod
    def from_file(cls, config_path: str | None = None) -> "ExtensionsConfig":
        """从 JSON 文件加载扩展配置。

        详见 `resolve_config_path` 了解更多细节。

        Args:
            config_path: 扩展配置文件的路径。

        Returns:
            ExtensionsConfig: 加载的配置；如果未找到文件则返回空配置。
        """
        resolved_path = cls.resolve_config_path(config_path)
        if resolved_path is None:
            return cls(mcp_servers={}, skills={})

        with open(resolved_path) as f:
            config_data = json.load(f)

        cls.resolve_env_variables(config_data)
        return cls.model_validate(config_data)

    @classmethod
    def resolve_env_variables(cls, config: dict[str, Any]) -> dict[str, Any]:
        """递归解析扩展配置中的环境变量。

        环境变量通过 `os.getenv` 函数解析。示例: $OPENAI_API_KEY

        Args:
            config: 需要解析环境变量的配置。

        Returns:
            解析后的配置。
        """
        for key, value in config.items():
            if isinstance(value, str):
                if value.startswith("$"):
                    env_value = os.getenv(value[1:], None)
                    if env_value is not None:
                        config[key] = env_value
                else:
                    config[key] = value
            elif isinstance(value, dict):
                config[key] = cls.resolve_env_variables(value)
            elif isinstance(value, list):
                config[key] = [cls.resolve_env_variables(item) if isinstance(item, dict) else item for item in value]
        return config

    def get_enabled_mcp_servers(self) -> dict[str, McpServerConfig]:
        """仅获取已启用的 MCP 服务器。

        Returns:
            已启用 MCP 服务器的字典。
        """
        return {name: config for name, config in self.mcp_servers.items() if config.enabled}

    def is_skill_enabled(self, skill_name: str, skill_category: str) -> bool:
        """检查技能是否启用。

        Args:
            skill_name: 技能名称。
            skill_category: 技能类别。

        Returns:
            启用时返回 True，否则返回 False。
        """
        skill_config = self.skills.get(skill_name)
        if skill_config is None:
            return skill_category in ("public", "custom")
        return skill_config.enabled


_extensions_config: ExtensionsConfig | None = None


def get_extensions_config() -> ExtensionsConfig:
    """获取扩展配置实例。

    返回一个缓存的单例实例。需要重新从文件加载时，请使用 `reload_extensions_config()`；
    若要清除缓存，请使用 `reset_extensions_config()`。

    Returns:
        缓存的 ExtensionsConfig 实例。
    """
    global _extensions_config
    if _extensions_config is None:
        _extensions_config = ExtensionsConfig.from_file()
    return _extensions_config


def reload_extensions_config(config_path: str | None = None) -> ExtensionsConfig:
    """从文件重新加载扩展配置并更新缓存的实例。

    当配置文件修改后，此操作有助于在不重启应用的情况下获取变更。

    Args:
        config_path: 可选的扩展配置文件路径。若未提供，将使用默认解析策略。

    Returns:
        新加载的 ExtensionsConfig 实例。
    """
    global _extensions_config
    _extensions_config = ExtensionsConfig.from_file(config_path)
    return _extensions_config


def reset_extensions_config() -> None:
    """重置缓存的扩展配置实例。

    这将清空单例缓存，使下一次调用 `get_extensions_config()` 时从文件重新加载。
    对测试或在不同配置之间切换时很有用。
    """
    global _extensions_config
    _extensions_config = None


def set_extensions_config(config: ExtensionsConfig) -> None:
    """设置自定义扩展配置实例。

    这允许在测试中注入自定义或模拟的配置。

    Args:
        config: 要使用的 ExtensionsConfig 实例。
    """
    global _extensions_config
    _extensions_config = config
