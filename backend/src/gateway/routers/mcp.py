import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.config.extensions_config import ExtensionsConfig, get_extensions_config, reload_extensions_config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["mcp"])


class McpServerConfigResponse(BaseModel):
    """MCP 服务器配置的响应模型。

    该模型用于表示单个 MCP 服务器的配置信息，包括传输类型、启动命令、
    环境变量、URL 地址等配置项。

    Attributes:
        enabled: 是否启用该 MCP 服务器。
        type: 传输类型，支持 'stdio'、'sse' 或 'http'。
        command: 启动 MCP 服务器的命令（适用于 stdio 类型）。
        args: 传递给命令的参数列表（适用于 stdio 类型）。
        env: MCP 服务器的环境变量配置。
        url: MCP 服务器的 URL 地址（适用于 sse 或 http 类型）。
        headers: 发送的 HTTP 请求头（适用于 sse 或 http 类型）。
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


class McpConfigResponse(BaseModel):
    """MCP 配置的响应模型。

    该模型用于表示完整的 MCP 配置，包含所有已配置的 MCP 服务器。

    Attributes:
        mcp_servers: MCP 服务器名称到配置的映射字典。
    """

    mcp_servers: dict[str, McpServerConfigResponse] = Field(
        default_factory=dict,
        description="MCP 服务器名称到配置的映射",
    )


class McpConfigUpdateRequest(BaseModel):
    """用于更新 MCP 配置的请求模型。

    该模型用于接收客户端提交的 MCP 配置更新请求。

    Attributes:
        mcp_servers: MCP 服务器名称到配置的映射字典。
    """

    mcp_servers: dict[str, McpServerConfigResponse] = Field(
        ...,
        description="MCP 服务器名称到配置的映射",
    )


@router.get(
    "/mcp/config",
    response_model=McpConfigResponse,
    summary="获取 MCP 配置",
    description="检索当前 Model Context Protocol (MCP) 服务器的配置。",
)
async def get_mcp_configuration() -> McpConfigResponse:
    """获取当前的 MCP 配置。

    从配置缓存中读取当前的 MCP 服务器配置，并返回包含所有服务器配置的响应对象。

    Returns:
        McpConfigResponse: 包含所有 MCP 服务器配置的响应对象。
    """
    config = get_extensions_config()

    return McpConfigResponse(mcp_servers={name: McpServerConfigResponse(**server.model_dump()) for name, server in config.mcp_servers.items()})


@router.put(
    "/mcp/config",
    response_model=McpConfigResponse,
    summary="更新 MCP 配置",
    description="更新 Model Context Protocol (MCP) 服务器的配置并保存到配置文件。",
)
async def update_mcp_configuration(request: McpConfigUpdateRequest) -> McpConfigResponse:
    """更新 MCP 配置。

    将新配置保存到配置文件、重新加载缓存，并重置 MCP 工具缓存以触发重新初始化。

    Args:
        request: 要保存的新 MCP 配置请求对象。

    Returns:
        McpConfigResponse: 更新后的 MCP 配置响应对象。

    Raises:
        HTTPException: 当写入配置文件失败时抛出 500 错误。
    """
    try:
        config_path = ExtensionsConfig.resolve_config_path()

        if config_path is None:
            config_path = Path.cwd().parent / "extensions_config.json"
            logger.info(f"未找到现有的扩展配置文件。将在以下位置创建新配置：{config_path}")

        current_config = get_extensions_config()

        config_data = {
            "mcpServers": {name: server.model_dump() for name, server in request.mcp_servers.items()},
            "skills": {name: {"enabled": skill.enabled} for name, skill in current_config.skills.items()},
        }

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        logger.info(f"MCP 配置已更新并保存至：{config_path}")

        reloaded_config = reload_extensions_config()
        return McpConfigResponse(mcp_servers={name: McpServerConfigResponse(**server.model_dump()) for name, server in reloaded_config.mcp_servers.items()})

    except Exception as e:
        logger.error(f"更新 MCP 配置失败：{e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新 MCP 配置失败：{str(e)}")
