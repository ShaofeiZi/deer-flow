import logging

from langchain.tools import BaseTool

from src.config import get_app_config
from src.reflection import resolve_variable
from src.tools.builtins import ask_clarification_tool, present_file_tool, task_tool, view_image_tool

logger = logging.getLogger(__name__)

BUILTIN_TOOLS = [
    present_file_tool,
    ask_clarification_tool,
]

SUBAGENT_TOOLS = [
    task_tool,
    # task_status_tool 不再暴露给 LLM（后端在内部处理轮询）
]


def get_available_tools(
    groups: list[str] | None = None,
    include_mcp: bool = True,
    model_name: str | None = None,
    subagent_enabled: bool = False,
) -> list[BaseTool]:
    """从配置获取所有可用工具。

    注意：MCP 工具应在应用启动时使用 src.mcp 模块的
    `initialize_mcp_tools()` 进行初始化。

    Args:
        groups: 可选的工具组列表，用于按组过滤。
        include_mcp: 是否包含来自 MCP 服务器的工具（默认：True）。
        model_name: 可选的模型名称，用于确定是否应包含视觉工具。
        subagent_enabled: 是否包含子代理工具（task、task_status）。

    Returns:
        可用工具列表。
    """
    config = get_app_config()
    loaded_tools = [resolve_variable(tool.use, BaseTool) for tool in config.tools if groups is None or tool.group in groups]

    # 如果启用则获取缓存的 MCP 工具
    # 注意：我们使用 ExtensionsConfig.from_file() 而不是 config.extensions
    # 以始终从磁盘读取最新配置。这确保通过 Gateway API（在独立进程中运行）
    # 所做的更改在加载 MCP 工具时立即生效。
    mcp_tools = []
    if include_mcp:
        try:
            from src.config.extensions_config import ExtensionsConfig
            from src.mcp.cache import get_cached_mcp_tools

            extensions_config = ExtensionsConfig.from_file()
            if extensions_config.get_enabled_mcp_servers():
                mcp_tools = get_cached_mcp_tools()
                if mcp_tools:
                    logger.info(f"正在使用 {len(mcp_tools)} 个缓存的 MCP 工具")
        except ImportError:
            logger.warning("MCP 模块不可用。请安装 'langchain-mcp-adapters' 包以启用 MCP 工具。")
        except Exception as e:
            logger.error(f"获取缓存的 MCP 工具失败：{e}")

    # 根据配置有条件地添加工具
    builtin_tools = BUILTIN_TOOLS.copy()

    # 仅在通过运行时参数启用时才添加子代理工具
    if subagent_enabled:
        builtin_tools.extend(SUBAGENT_TOOLS)
        logger.info("正在包含子代理工具（task）")

    # 如果未指定 model_name，使用第一个模型（默认）
    if model_name is None and config.models:
        model_name = config.models[0].name

    # 仅当模型支持视觉时才添加 view_image_tool
    model_config = config.get_model_config(model_name) if model_name else None
    if model_config is not None and model_config.supports_vision:
        builtin_tools.append(view_image_tool)
        logger.info(f"正在为模型 '{model_name}' 包含 view_image_tool（supports_vision=True）")

    return loaded_tools + builtin_tools + mcp_tools
