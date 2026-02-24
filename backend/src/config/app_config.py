import os
from pathlib import Path
from typing import Any, Self

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

from src.config.extensions_config import ExtensionsConfig
from src.config.memory_config import load_memory_config_from_dict
from src.config.model_config import ModelConfig
from src.config.sandbox_config import SandboxConfig
from src.config.skills_config import SkillsConfig
from src.config.summarization_config import load_summarization_config_from_dict
from src.config.title_config import load_title_config_from_dict
from src.config.tool_config import ToolConfig, ToolGroupConfig

load_dotenv()


class AppConfig(BaseModel):
    """DeerFlow 应用的配置。

    该类是应用的主配置模型，包含模型、沙箱、工具、技能和扩展等配置项。

    Attributes:
        models: 可用模型列表。
        sandbox: 沙箱配置。
        tools: 可用工具列表。
        tool_groups: 可用工具组列表。
        skills: 技能配置。
        extensions: 扩展配置（MCP 服务器和技能状态）。
    """

    models: list[ModelConfig] = Field(default_factory=list, description="可用模型列表")
    sandbox: SandboxConfig = Field(description="沙箱配置")
    tools: list[ToolConfig] = Field(default_factory=list, description="可用工具列表")
    tool_groups: list[ToolGroupConfig] = Field(default_factory=list, description="可用工具组列表")
    skills: SkillsConfig = Field(default_factory=SkillsConfig, description="技能配置")
    extensions: ExtensionsConfig = Field(default_factory=ExtensionsConfig, description="扩展配置（MCP 服务器和技能状态）")
    model_config = ConfigDict(extra="allow", frozen=False)

    @classmethod
    def resolve_config_path(cls, config_path: str | None = None) -> Path:
        """解析配置文件路径。

        按以下优先级查找配置文件：
        1. 如果提供了 `config_path` 参数，则使用它。
        2. 如果提供了 `DEER_FLOW_CONFIG_PATH` 环境变量，则使用它。
        3. 否则，先检查当前目录中的 `config.yaml`，然后回退到父目录中的 `config.yaml`。

        Args:
            config_path: 可选的配置文件路径。

        Returns:
            解析后的配置文件路径。

        Raises:
            FileNotFoundError: 配置文件不存在时抛出。
        """
        if config_path:
            path = Path(config_path)
            if not Path.exists(path):
                raise FileNotFoundError(f"参数 `config_path` 指定的配置文件在 {path} 未找到")
            return path
        elif os.getenv("DEER_FLOW_CONFIG_PATH"):
            path = Path(os.getenv("DEER_FLOW_CONFIG_PATH"))
            if not Path.exists(path):
                raise FileNotFoundError(f"环境变量 `DEER_FLOW_CONFIG_PATH` 指定的配置文件在 {path} 未找到")
            return path
        else:
            path = Path(os.getcwd()) / "config.yaml"
            if not path.exists():
                path = Path(os.getcwd()).parent / "config.yaml"
                if not path.exists():
                    raise FileNotFoundError("`config.yaml` 文件在当前目录及其父目录中均未找到")
            return path

    @classmethod
    def from_file(cls, config_path: str | None = None) -> Self:
        """从 YAML 文件加载配置。

        参考 `resolve_config_path` 了解更多细节。

        Args:
            config_path: 配置文件的路径。

        Returns:
            AppConfig: 加载的配置实例。
        """
        resolved_path = cls.resolve_config_path(config_path)
        with open(resolved_path) as f:
            config_data = yaml.safe_load(f)
        config_data = cls.resolve_env_variables(config_data)

        if "title" in config_data:
            load_title_config_from_dict(config_data["title"])

        if "summarization" in config_data:
            load_summarization_config_from_dict(config_data["summarization"])

        if "memory" in config_data:
            load_memory_config_from_dict(config_data["memory"])

        extensions_config = ExtensionsConfig.from_file()
        config_data["extensions"] = extensions_config.model_dump()

        result = cls.model_validate(config_data)
        return result

    @classmethod
    def resolve_env_variables(cls, config: Any) -> Any:
        """递归解析配置中的环境变量。

        环境变量通过 `os.getenv` 函数解析。示例: $OPENAI_API_KEY

        Args:
            config: 需要解析环境变量的配置。

        Returns:
            已解析环境变量的配置。
        """
        if isinstance(config, str):
            if config.startswith("$"):
                return os.getenv(config[1:], config)
            return config
        elif isinstance(config, dict):
            return {k: cls.resolve_env_variables(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [cls.resolve_env_variables(item) for item in config]
        return config

    def get_model_config(self, name: str) -> ModelConfig | None:
        """按名称获取模型配置。

        Args:
            name: 要获取配置的模型名称。

        Returns:
            若找到则返回模型配置，否则返回 None。
        """
        return next((model for model in self.models if model.name == name), None)

    def get_tool_config(self, name: str) -> ToolConfig | None:
        """按名称获取工具配置。

        Args:
            name: 要获取配置的工具名称。

        Returns:
            若找到则返回工具配置，否则返回 None。
        """
        return next((tool for tool in self.tools if tool.name == name), None)

    def get_tool_group_config(self, name: str) -> ToolGroupConfig | None:
        """按名称获取工具组配置。

        Args:
            name: 要获取配置的工具组名称。

        Returns:
            若找到则返回工具组配置，否则返回 None。
        """
        return next((group for group in self.tool_groups if group.name == name), None)


_app_config: AppConfig | None = None


def get_app_config() -> AppConfig:
    """获取 DeerFlow 配置实例。

    返回一个缓存的单例实例。需要重新从文件加载时，请使用 `reload_app_config()`；
    若要清除缓存，请使用 `reset_app_config()`。

    Returns:
        缓存的 AppConfig 实例。
    """
    global _app_config
    if _app_config is None:
        _app_config = AppConfig.from_file()
    return _app_config


def reload_app_config(config_path: str | None = None) -> AppConfig:
    """从文件重新加载配置并更新缓存的实例。

    当配置文件修改后，此操作有助于在不重启应用的情况下获取变更。

    Args:
        config_path: 配置文件的可选路径。如果未提供，将使用默认解析策略。

    Returns:
        新加载的 AppConfig 实例。
    """
    global _app_config
    _app_config = AppConfig.from_file(config_path)
    return _app_config


def reset_app_config() -> None:
    """重置缓存的配置实例。

    这将清空单例缓存，使下一次调用 `get_app_config()` 时从文件重新加载。
    适用于测试或在不同配置之间切换的时候。
    """
    global _app_config
    _app_config = None


def set_app_config(config: AppConfig) -> None:
    """设置自定义配置实例。

    这允许在测试中注入自定义或模拟的配置。

    Args:
        config: 要使用的 AppConfig 实例。
    """
    global _app_config
    _app_config = config
