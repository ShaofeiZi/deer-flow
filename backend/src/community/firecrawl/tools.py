"""Firecrawl 社区工具封装。

提供 web_search/web_fetch 两个工具。firecrawl 为可选依赖，因此采用运行时动态导入。
"""

# pyright: reportMissingImports=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false

import importlib
import json
from collections.abc import Callable
from typing import cast

from langchain.tools import tool

from src.config import get_app_config


def _get_firecrawl_client() -> object:
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

    firecrawl_mod = importlib.import_module("firecrawl")
    firecrawl_app_cls = cast(Callable[..., object], getattr(firecrawl_mod, "FirecrawlApp"))
    return firecrawl_app_cls(api_key=api_key)


@tool("web_search", parse_docstring=True)
def web_search_tool(query: str) -> str:
    """搜索网页。"""
    try:
        config = get_app_config().get_tool_config("web_search")
        extra = cast(dict[str, object], config.model_extra or {}) if config is not None else {}
        raw_max_results = extra.get("max_results")
        if isinstance(raw_max_results, int):
            max_results = raw_max_results
        elif isinstance(raw_max_results, str) and raw_max_results.isdigit():
            max_results = int(raw_max_results)
        else:
            max_results = 5

        client = _get_firecrawl_client()
        search_fn = cast(Callable[..., object], getattr(client, "search"))
        result = cast(object, search_fn(query, limit=max_results))

        web_results = cast(list[object], getattr(result, "web", None) or [])
        normalized_results = [
            {
                "title": getattr(item, "title", "") or "",
                "url": getattr(item, "url", "") or "",
                "snippet": getattr(item, "description", "") or "",
            }
            for item in web_results
        ]
        return json.dumps(normalized_results, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {str(e)}"


@tool("web_fetch", parse_docstring=True)
def web_fetch_tool(url: str) -> str:
    """抓取指定 URL 的网页内容。"""
    try:
        client = _get_firecrawl_client()
        scrape_fn = cast(Callable[..., object], getattr(client, "scrape"))
        result = cast(object, scrape_fn(url, formats=["markdown"]))

        markdown_content = str(getattr(result, "markdown", None) or "")
        metadata = cast(object, getattr(result, "metadata", None))
        title = getattr(metadata, "title", None) if metadata is not None else None
        title = title or "Untitled"

        if not markdown_content:
            return "Error: No content found"
        return f"# {title}\n\n{markdown_content[:4096]}"
    except Exception as e:
        return f"Error: {str(e)}"
