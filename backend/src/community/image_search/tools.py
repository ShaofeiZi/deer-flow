"""图片搜索（Image Search）工具。

基于 DuckDuckGo/`ddgs` 搜索图片，用于在 image generation 前获取参考图。
"""

# pyright: reportMissingImports=false, reportMissingTypeArgument=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownParameterType=false, reportUnknownArgumentType=false, reportOptionalMemberAccess=false, reportOperatorIssue=false

import importlib
from collections.abc import Callable, Iterable
from typing import cast

import json
import logging

from langchain.tools import tool

from src.config import get_app_config

logger = logging.getLogger(__name__)


def _search_images(
    query: str,
    max_results: int = 5,
    region: str = "wt-wt",
    safesearch: str = "moderate",
    size: str | None = None,
    color: str | None = None,
    type_image: str | None = None,
    layout: str | None = None,
    license_image: str | None = None,
) -> list[dict[str, object]]:
    """
    Execute image search using DuckDuckGo.

    Args:
        query: Search keywords
        max_results: Maximum number of results
        region: Search region
        safesearch: Safe search level
        size: Image size (Small/Medium/Large/Wallpaper)
        color: Color filter
        type_image: Image type (photo/clipart/gif/transparent/line)
        layout: Layout (Square/Tall/Wide)
        license_image: License filter

    Returns:
        List of search results
    """
    try:
        ddgs_mod = importlib.import_module("ddgs")
        ddgs_cls = cast(object, getattr(ddgs_mod, "DDGS"))
    except Exception:
        logger.error("ddgs library not installed. Run: pip install ddgs")
        return []

    ddgs_ctor = cast(Callable[..., object], ddgs_cls)
    ddgs = ddgs_ctor(timeout=30)

    try:
        kwargs: dict[str, object] = {
            "region": region,
            "safesearch": safesearch,
            "max_results": max_results,
        }

        if size:
            kwargs["size"] = size
        if color:
            kwargs["color"] = color
        if type_image:
            kwargs["type_image"] = type_image
        if layout:
            kwargs["layout"] = layout
        if license_image:
            kwargs["license_image"] = license_image

        images_fn = cast(Callable[..., object], getattr(ddgs, "images"))
        results_obj = images_fn(query, **kwargs)
        if results_obj is None:
            return []
        if isinstance(results_obj, list):
            return cast(list[dict[str, object]], results_obj)
        if isinstance(results_obj, Iterable):
            return cast(list[dict[str, object]], list(results_obj))
        return []

    except Exception as e:
        logger.error(f"Failed to search images: {e}")
        return []


@tool("image_search", parse_docstring=True)
def image_search_tool(
    query: str,
    max_results: int = 5,
    size: str | None = None,
    type_image: str | None = None,
    layout: str | None = None,
) -> str:
    """Search for images online. Use this tool BEFORE image generation to find reference images for characters, portraits, objects, scenes, or any content requiring visual accuracy.

    **When to use:**
    - Before generating character/portrait images: search for similar poses, expressions, styles
    - Before generating specific objects/products: search for accurate visual references
    - Before generating scenes/locations: search for architectural or environmental references
    - Before generating fashion/clothing: search for style and detail references

    The returned image URLs can be used as reference images in image generation to significantly improve quality.

    Args:
        query: Search keywords describing the images you want to find. Be specific for better results (e.g., "Japanese woman street photography 1990s" instead of just "woman").
        max_results: Maximum number of images to return. Default is 5.
        size: Image size filter. Options: "Small", "Medium", "Large", "Wallpaper". Use "Large" for reference images.
        type_image: Image type filter. Options: "photo", "clipart", "gif", "transparent", "line". Use "photo" for realistic references.
        layout: Layout filter. Options: "Square", "Tall", "Wide". Choose based on your generation needs.
    """
    config = get_app_config().get_tool_config("image_search")

    extra = cast(dict[str, object], config.model_extra or {}) if config is not None else {}
    raw_max_results = extra.get("max_results")
    if isinstance(raw_max_results, int):
        max_results = raw_max_results
    elif isinstance(raw_max_results, str) and raw_max_results.isdigit():
        max_results = int(raw_max_results)

    results = _search_images(
        query=query,
        max_results=max_results,
        size=size,
        type_image=type_image,
        layout=layout,
    )

    if not results:
        return json.dumps({"error": "No images found", "query": query}, ensure_ascii=False)

    normalized_results = [
        {
            "title": str(r.get("title", "")),
            "image_url": str(r.get("thumbnail", "")),
            "thumbnail_url": str(r.get("thumbnail", "")),
        }
        for r in results
    ]

    output = {
        "query": query,
        "total_results": len(normalized_results),
        "results": normalized_results,
        "usage_hint": "Use the 'image_url' values as reference images in image generation. Download them first if needed.",
    }

    return json.dumps(output, indent=2, ensure_ascii=False)
