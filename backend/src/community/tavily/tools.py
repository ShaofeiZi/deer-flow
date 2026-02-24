"""Tavily 社区 web_search/web_fetch 工具封装。

Tavily 为可选依赖，因此采用运行时动态导入。
"""

# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportOptionalMemberAccess=false, reportOperatorIssue=false

import importlib
import json
from collections.abc import Callable
from typing import cast

from langchain.tools import tool

from src.config import get_app_config


def _get_tavily_client() -> object:
    """
    【函数功能描述】
    
    参数:
        【参数名】: 【参数描述】
    
    返回:
        【返回值描述】
    """

    config = get_app_config().get_tool_config("web_search")
    extra = cast(dict[str, object], config.model_extra or {}) if config is not None else {}
    api_key = extra.get("api_key")

    tavily_mod = importlib.import_module("tavily")
    tavily_client_cls = cast(Callable[..., object], getattr(tavily_mod, "TavilyClient"))
    return tavily_client_cls(api_key=api_key)


@tool("web_search", parse_docstring=True)
def web_search_tool(query: str) -> str:
    """搜索网页。"""

    config = get_app_config().get_tool_config("web_search")
    extra = cast(dict[str, object], config.model_extra or {}) if config is not None else {}
    raw_max_results = extra.get("max_results")
    if isinstance(raw_max_results, int):
        max_results = raw_max_results
    elif isinstance(raw_max_results, str) and raw_max_results.isdigit():
        max_results = int(raw_max_results)
    else:
        max_results = 5

    client = _get_tavily_client()
    search_fn = cast(Callable[..., object], getattr(client, "search"))
    res = cast(dict[str, object], search_fn(query, max_results=max_results))
    results = cast(list[object], res.get("results") or [])

    normalized_results: list[dict[str, str]] = []
    for item in results:
        if isinstance(item, dict):
            normalized_results.append(
                {
                    "title": str(item.get("title", "")),
                    "url": str(item.get("url", "")),
                    "snippet": str(item.get("content", "")),
                }
            )

    return json.dumps(normalized_results, indent=2, ensure_ascii=False)


@tool("web_fetch", parse_docstring=True)
def web_fetch_tool(url: str) -> str:
    """抓取指定 URL 的网页内容。

    仅抓取：用户直接提供的 URL，或 web_search/web_fetch 返回的 URL。
    该工具无法访问需要认证的内容（例如私有 Google Docs 或登录后页面）。
    URL 必须包含 schema：例如 https://example.com。
    """

    client = _get_tavily_client()
    extract_fn = cast(Callable[..., object], getattr(client, "extract"))
    res = cast(dict[str, object], extract_fn([url]))

    failed_results = cast(list[object], res.get("failed_results") or [])
    if failed_results:
        first = failed_results[0]
        if isinstance(first, dict):
            return f"Error: {first.get('error', '')}"
        return "Error: fetch failed"

    results = cast(list[object], res.get("results") or [])
    if results:
        first = results[0]
        if isinstance(first, dict):
            title = str(first.get("title", ""))
            raw_content = str(first.get("raw_content", ""))
            return f"# {title}\n\n{raw_content[:4096]}"
        return "Error: Invalid result format"

    return "Error: No results found"
