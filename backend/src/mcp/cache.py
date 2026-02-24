"""MCP 工具缓存，避免重复加载。"""

import asyncio
import logging
import os

from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

_mcp_tools_cache: list[BaseTool] | None = None
_cache_initialized = False
_initialization_lock = asyncio.Lock()
_config_mtime: float | None = None  # 跟踪配置文件修改时间


def _get_config_mtime() -> float | None:
    """获取扩展配置文件的修改时间。

    Returns:
        修改时间（浮点数），如果文件不存在则返回 None。
    """
    from src.config.extensions_config import ExtensionsConfig

    config_path = ExtensionsConfig.resolve_config_path()
    if config_path and config_path.exists():
        return os.path.getmtime(config_path)
    return None


def _is_cache_stale() -> bool:
    """检查缓存是否因配置文件更改而过期。

    Returns:
        如果缓存应该失效则返回 True，否则返回 False。
    """
    global _config_mtime

    if not _cache_initialized:
        return False  # 尚未初始化，未过期

    current_mtime = _get_config_mtime()

    # 如果之前或现在无法获取 mtime，假设未过期
    if _config_mtime is None or current_mtime is None:
        return False

    # 如果配置文件在缓存后被修改，则已过期
    if current_mtime > _config_mtime:
        logger.info(f"MCP 配置文件已被修改（mtime: {_config_mtime} -> {current_mtime}），缓存已过期")
        return True

    return False


async def initialize_mcp_tools() -> list[BaseTool]:
    """初始化并缓存 MCP 工具。

    应在应用启动时调用一次。

    Returns:
        来自所有已启用 MCP 服务器的 LangChain 工具列表。
    """
    global _mcp_tools_cache, _cache_initialized, _config_mtime

    async with _initialization_lock:
        if _cache_initialized:
            logger.info("MCP 工具已初始化")
            return _mcp_tools_cache or []

        from src.mcp.tools import get_mcp_tools

        logger.info("正在初始化 MCP 工具...")
        _mcp_tools_cache = await get_mcp_tools()
        _cache_initialized = True
        _config_mtime = _get_config_mtime()  # 记录配置文件 mtime
        logger.info(f"MCP 工具已初始化：已加载 {len(_mcp_tools_cache)} 个工具（配置 mtime: {_config_mtime}）")

        return _mcp_tools_cache


def get_cached_mcp_tools() -> list[BaseTool]:
    """获取缓存的 MCP 工具，支持延迟初始化。

    如果工具未初始化，将自动初始化。
    这确保 MCP 工具在 FastAPI 和 LangGraph Studio 上下文中都能正常工作。

    同时检查配置文件自上次初始化以来是否被修改，
    如有需要则重新初始化。这确保通过 Gateway API（在独立进程中运行）
    所做的更改能够反映到 LangGraph Server 中。

    Returns:
        缓存的 MCP 工具列表。
    """
    global _cache_initialized

    # 检查缓存是否因配置文件更改而过期
    if _is_cache_stale():
        logger.info("MCP 缓存已过期，正在重置以重新初始化...")
        reset_mcp_tools_cache()

    if not _cache_initialized:
        logger.info("MCP 工具未初始化，正在执行延迟初始化...")
        try:
            # 尝试在当前事件循环中初始化
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 如果循环已在运行（例如在 LangGraph Studio 中），
                # 我们需要在线程中创建新循环
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, initialize_mcp_tools())
                    future.result()
            else:
                # 如果没有循环在运行，可以使用当前循环
                loop.run_until_complete(initialize_mcp_tools())
        except RuntimeError:
            # 不存在事件循环，创建一个
            asyncio.run(initialize_mcp_tools())
        except Exception as e:
            logger.error(f"延迟初始化 MCP 工具失败：{e}")
            return []

    return _mcp_tools_cache or []


def reset_mcp_tools_cache() -> None:
    """重置 MCP 工具缓存。

    适用于测试或需要重新加载 MCP 工具时。
    """
    global _mcp_tools_cache, _cache_initialized, _config_mtime
    _mcp_tools_cache = None
    _cache_initialized = False
    _config_mtime = None
    logger.info("MCP 工具缓存已重置")
