"""使用 langchain-mcp-adapters 的 MCP 客户端。"""

import logging
from typing import Any

from src.config.extensions_config import ExtensionsConfig, McpServerConfig

logger = logging.getLogger(__name__)


def build_server_params(server_name: str, config: McpServerConfig) -> dict[str, Any]:
    """为 MultiServerMCPClient 构建服务器参数。

    Args:
        server_name: MCP 服务器名称。
        config: MCP 服务器的配置。

    Returns:
        用于 langchain-mcp-adapters 的服务器参数字典。
    """
    transport_type = config.type or "stdio"
    params: dict[str, Any] = {"transport": transport_type}

    if transport_type == "stdio":
        if not config.command:
            raise ValueError(f"使用 stdio 传输的 MCP 服务器 '{server_name}' 需要 'command' 字段")
        params["command"] = config.command
        params["args"] = config.args
        # 如果存在环境变量则添加
        if config.env:
            params["env"] = config.env
    elif transport_type in ("sse", "http"):
        if not config.url:
            raise ValueError(f"使用 {transport_type} 传输的 MCP 服务器 '{server_name}' 需要 'url' 字段")
        params["url"] = config.url
        # 如果存在请求头则添加
        if config.headers:
            params["headers"] = config.headers
    else:
        raise ValueError(f"MCP 服务器 '{server_name}' 使用了不支持的传输类型：{transport_type}")

    return params


def build_servers_config(extensions_config: ExtensionsConfig) -> dict[str, dict[str, Any]]:
    """为 MultiServerMCPClient 构建服务器配置。

    Args:
        extensions_config: 包含所有 MCP 服务器的扩展配置。

    Returns:
        服务器名称到参数的映射字典。
    """
    enabled_servers = extensions_config.get_enabled_mcp_servers()

    if not enabled_servers:
        logger.info("未找到已启用的 MCP 服务器")
        return {}

    servers_config = {}
    for server_name, server_config in enabled_servers.items():
        try:
            servers_config[server_name] = build_server_params(server_name, server_config)
            logger.info(f"已配置 MCP 服务器：{server_name}")
        except Exception as e:
            logger.error(f"配置 MCP 服务器 '{server_name}' 失败：{e}")

    return servers_config
