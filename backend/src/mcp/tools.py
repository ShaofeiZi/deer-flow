"""使用 langchain-mcp-adapters 加载 MCP 工具。"""

import logging

from langchain_core.tools import BaseTool

from src.config.extensions_config import ExtensionsConfig
from src.mcp.client import build_servers_config

logger = logging.getLogger(__name__)


async def get_mcp_tools() -> list[BaseTool]:
    """从已启用的 MCP 服务器获取所有工具。

    Returns:
        来自所有已启用 MCP 服务器的 LangChain 工具列表。
    """
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError:
        logger.warning("未安装 langchain-mcp-adapters。请安装以启用 MCP 工具：pip install langchain-mcp-adapters")
        return []

    # 注意：我们使用 ExtensionsConfig.from_file() 而不是 get_extensions_config()
    # 以始终从磁盘读取最新配置。这确保通过 Gateway API（在独立进程中运行）
    # 所做的更改在初始化 MCP 工具时立即生效。
    extensions_config = ExtensionsConfig.from_file()
    servers_config = build_servers_config(extensions_config)

    if not servers_config:
        logger.info("未配置已启用的 MCP 服务器")
        return []

    try:
        # 创建多服务器 MCP 客户端
        logger.info(f"正在初始化 MCP 客户端，共 {len(servers_config)} 个服务器")
        client = MultiServerMCPClient(servers_config)

        # 从所有服务器获取所有工具
        tools = await client.get_tools()
        logger.info(f"成功从 MCP 服务器加载 {len(tools)} 个工具")

        return tools

    except Exception as e:
        logger.error(f"加载 MCP 工具失败：{e}", exc_info=True)
        return []
