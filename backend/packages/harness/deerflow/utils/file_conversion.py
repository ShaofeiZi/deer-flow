"""File conversion utilities.
文件转换工具。

Converts document files (PDF, PPT, Excel, Word) to Markdown.
将文档文件（PDF、PPT、Excel、Word）转换为 Markdown。

PDF conversion strategy (auto mode):
  1. Try pymupdf4llm if installed — better heading detection, faster on most files.
  2. If output is suspiciously short (< _MIN_CHARS_PER_PAGE chars/page, or < 200 chars
     total when page count is unavailable), treat as image-based and fall back to MarkItDown.
  3. If pymupdf4llm is not installed, use MarkItDown directly (existing behaviour).
PDF 转换策略（auto 模式）：
  1. 如果已安装 pymupdf4llm，则优先使用——标题检测更好，大多数文件上更快。
  2. 如果输出可疑地短（< _MIN_CHARS_PER_PAGE 字符/页，或当页数不可用时 < 200 字符），
     视为基于图像的 PDF 并回退到 MarkItDown。
  3. 如果未安装 pymupdf4llm，则直接使用 MarkItDown（现有行为）。

Large files (> ASYNC_THRESHOLD_BYTES) are converted in a thread pool via
asyncio.to_thread() to avoid blocking the event loop (fixes #1569).
大文件（> ASYNC_THRESHOLD_BYTES）通过 asyncio.to_thread() 在线程池中转换，
以避免阻塞事件循环（修复 #1569）。

No FastAPI or HTTP dependencies — pure utility functions.
无 FastAPI 或 HTTP 依赖——纯工具函数。
"""

import asyncio
import logging
import re
from pathlib import Path

from deerflow.config.app_config import get_app_config

logger = logging.getLogger(__name__)

# File extensions that should be converted to markdown
# 应转换为 markdown 的文件扩展名
CONVERTIBLE_EXTENSIONS = {
    ".pdf",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".doc",
    ".docx",
}

# Files larger than this threshold are converted in a background thread.
# Small files complete in < 1s synchronously; spawning a thread adds unnecessary
# scheduling overhead for them.
# 大于此阈值的文件在后台线程中转换。
# 小文件在 < 1 秒内同步完成；为它们创建线程会增加不必要的调度开销。
_ASYNC_THRESHOLD_BYTES = 1 * 1024 * 1024  # 1 MB

# If pymupdf4llm produces fewer characters *per page* than this threshold,
# the PDF is likely image-based or encrypted — fall back to MarkItDown.
# Rationale: normal text PDFs yield 200-2000 chars/page; image-based PDFs
# yield close to 0. 50 chars/page gives a wide safety margin.
# Falls back to absolute 200-char check when page count is unavailable.
# 如果 pymupdf4llm 每页产生的字符数少于此阈值，PDF 可能是基于图像的或加密的——回退到 MarkItDown。
# 理由：正常文本 PDF 每页产生 200-2000 字符；基于图像的 PDF 接近 0。
# 50 字符/页提供了足够的安全余量。
# 当页数不可用时，回退到绝对 200 字符检查。
_MIN_CHARS_PER_PAGE = 50


def _pymupdf_output_too_sparse(text: str, file_path: Path) -> bool:
    """Return True if pymupdf4llm output is suspiciously short (image-based PDF).
    如果 pymupdf4llm 输出可疑地短（基于图像的 PDF），则返回 True。

    Uses chars-per-page rather than an absolute threshold so that both short
    documents (few pages, few chars) and long documents (many pages, many chars)
    are handled correctly.
    使用每页字符数而非绝对阈值，以便正确处理短文档（少页数、少字符）和
    长文档（多页数、多字符）。
    """
    chars = len(text.strip())
    doc = None
    pages: int | None = None
    try:
        import pymupdf

        doc = pymupdf.open(str(file_path))
        pages = len(doc)
    except Exception:
        pass
    finally:
        if doc is not None:
            try:
                doc.close()
            except Exception:
                pass
    if pages is not None and pages > 0:
        return (chars / pages) < _MIN_CHARS_PER_PAGE
    # Fallback: absolute threshold when page count is unavailable
    # 回退：当页数不可用时使用绝对阈值
    return chars < 200


def _convert_pdf_with_pymupdf4llm(file_path: Path) -> str | None:
    """Attempt PDF conversion with pymupdf4llm.
    尝试使用 pymupdf4llm 进行 PDF 转换。

    Returns the markdown text, or None if pymupdf4llm is not installed or
    if conversion fails (e.g. encrypted/corrupt PDF).
    返回 markdown 文本，如果 pymupdf4llm 未安装或转换失败（例如加密/损坏的 PDF），则返回 None。
    """
    try:
        import pymupdf4llm
    except ImportError:
        return None

    try:
        return pymupdf4llm.to_markdown(str(file_path))
    except Exception:
        logger.exception("pymupdf4llm failed to convert %s; falling back to MarkItDown", file_path.name)
        return None


def _convert_with_markitdown(file_path: Path) -> str:
    """Convert any supported file to markdown text using MarkItDown.
    使用 MarkItDown 将任何支持的文件转换为 markdown 文本。"""
    from markitdown import MarkItDown

    md = MarkItDown()
    return md.convert(str(file_path)).text_content


def _do_convert(file_path: Path, pdf_converter: str) -> str:
    """Synchronous conversion — called directly or via asyncio.to_thread.
    同步转换——直接调用或通过 asyncio.to_thread 调用。

    Args:
        file_path: Path to the file.
        pdf_converter: "auto" | "pymupdf4llm" | "markitdown"
    """
    is_pdf = file_path.suffix.lower() == ".pdf"

    if is_pdf and pdf_converter != "markitdown":
        # Try pymupdf4llm first (auto or explicit)
        # 首先尝试 pymupdf4llm（auto 或显式指定）
        pymupdf_text = _convert_pdf_with_pymupdf4llm(file_path)

        if pymupdf_text is not None:
            # pymupdf4llm is installed
            # pymupdf4llm 已安装
            if pdf_converter == "pymupdf4llm":
                # Explicit — use as-is regardless of output length
                # 显式指定——无论输出长度如何，直接使用
                return pymupdf_text
            # auto mode: fall back if output looks like a failed parse.
            # Use chars-per-page to distinguish image-based PDFs (near 0) from
            # legitimately short documents.
            # auto 模式：如果输出看起来像解析失败，则回退。
            # 使用每页字符数来区分基于图像的 PDF（接近 0）和合法的短文档。
            if not _pymupdf_output_too_sparse(pymupdf_text, file_path):
                return pymupdf_text
            logger.warning(
                "pymupdf4llm produced only %d chars for %s (likely image-based PDF); falling back to MarkItDown",
                len(pymupdf_text.strip()),
                file_path.name,
            )
        # pymupdf4llm not installed or fallback triggered → use MarkItDown
        # pymupdf4llm 未安装或触发了回退 → 使用 MarkItDown

    return _convert_with_markitdown(file_path)


async def convert_file_to_markdown(file_path: Path) -> Path | None:
    """Convert a supported document file to Markdown.
    将支持的文档文件转换为 Markdown。

    PDF files are handled with a two-converter strategy (see module docstring).
    Large files (> 1 MB) are offloaded to a thread pool to avoid blocking the
    event loop.
    PDF 文件使用双转换器策略处理（参见模块文档字符串）。
    大文件（> 1 MB）被卸载到线程池以避免阻塞事件循环。

    Args:
        file_path: Path to the file to convert.

    Returns:
        Path to the generated .md file, or None if conversion failed.
    """
    try:
        pdf_converter = _get_pdf_converter()
        file_size = file_path.stat().st_size

        if file_size > _ASYNC_THRESHOLD_BYTES:
            text = await asyncio.to_thread(_do_convert, file_path, pdf_converter)
        else:
            text = _do_convert(file_path, pdf_converter)

        md_path = file_path.with_suffix(".md")
        md_path.write_text(text, encoding="utf-8")

        logger.info("Converted %s to markdown: %s (%d chars)", file_path.name, md_path.name, len(text))
        return md_path
    except Exception as e:
        logger.error("Failed to convert %s to markdown: %s", file_path.name, e)
        return None


# Regex for bold-only lines that look like section headings.
# Targets SEC filing structural headings that pymupdf4llm renders as **bold**
# rather than # Markdown headings (because they use same font size as body text,
# distinguished only by bold+caps formatting).
# 用于匹配看起来像章节标题的纯粗体行的正则表达式。
# 针对 SEC 文件中 pymupdf4llm 渲染为 **粗体** 而非 # Markdown 标题的结构性标题
# （因为它们使用与正文相同的字体大小，仅通过粗体+大写格式区分）。
#
# Pattern requires ALL of:
#   1. Entire line is a single **...** block (no surrounding prose)
#   2. Starts with a recognised structural keyword:
#      - ITEM / PART / SECTION (with optional number/letter after)
#      - SCHEDULE, EXHIBIT, APPENDIX, ANNEX, CHAPTER
#      All-caps addresses, boilerplate ("CURRENT REPORT", "SIGNATURES",
#      "WASHINGTON, DC 20549") do NOT start with these keywords and are excluded.
# 模式要求全部满足：
#   1. 整行是单个 **...** 块（无周围文本）
#   2. 以可识别的结构性关键词开头：
#      - ITEM / PART / SECTION（后可跟可选数字/字母）
#      - SCHEDULE、EXHIBIT、APPENDIX、ANNEX、CHAPTER
#      全大写地址、模板文本（"CURRENT REPORT"、"SIGNATURES"、
#      "WASHINGTON, DC 20549"）不以这些关键词开头，因此被排除。
#
# Chinese headings (第三节...) are already captured as standard # headings
# by pymupdf4llm, so they don't need this pattern.
# 中文标题（第三节...）已被 pymupdf4llm 捕获为标准 # 标题，因此不需要此模式。
_BOLD_HEADING_RE = re.compile(r"^\*\*((ITEM|PART|SECTION|SCHEDULE|EXHIBIT|APPENDIX|ANNEX|CHAPTER)\b[A-Z0-9 .,\-]*)\*\*\s*$")

# Regex for split-bold headings produced by pymupdf4llm when a heading spans
# multiple text spans in the PDF (e.g. section number and title are separate spans).
# Matches lines like:  **1** **Introduction**  or  **3.2** **Multi-Head Attention**
# 用于 pymupdf4llm 产生的分割粗体标题的正则表达式，当标题跨越 PDF 中的多个文本跨度时
# （例如章节号和标题是分开的跨度）。匹配类似 **1** **Introduction** 或 **3.2** **Multi-Head Attention** 的行。
#
# Requirements:
#   1. Entire line consists only of **...** blocks separated by whitespace (no prose)
#   2. First block is a section number (digits and dots, e.g. "1", "3.2", "A.1")
#   3. Second block must not be purely numeric/punctuation — excludes financial table
#      headers like **2023** **2022** **2021** while allowing non-ASCII titles such as
#      **1** **概述** or accented words (negative lookahead instead of [A-Za-z])
#   4. At most two additional blocks (four total) with [^*]+ (no * inside) to keep
#      the regex linear and avoid ReDoS on attacker-controlled content
# 要求：
#   1. 整行仅由空格分隔的 **...** 块组成（无正文文本）
#   2. 第一个块是章节号（数字和点，例如 "1"、"3.2"、"A.1"）
#   3. 第二个块不能是纯数字/标点——排除财务表头如 **2023** **2022** **2021**，
#      同时允许非 ASCII 标题如 **1** **概述** 或带重音的单词（使用否定前瞻而非 [A-Za-z]）
#   4. 最多两个额外块（总共四个），使用 [^*]+（内部无 *）以保持正则线性并避免
#      攻击者控制内容上的 ReDoS
_SPLIT_BOLD_HEADING_RE = re.compile(r"^\*\*[\dA-Z][\d\.]*\*\*\s+\*\*(?!\d[\d\s.,\-–—/:()%]*\*\*)[^*]+\*\*(?:\s+\*\*[^*]+\*\*){0,2}\s*$")

# Maximum number of outline entries injected into the agent context.
# Keeps prompt size bounded even for very long documents.
# 注入代理上下文的大纲条目最大数量。
# 即使对于非常长的文档，也能保持提示大小有界。
MAX_OUTLINE_ENTRIES = 50

_ALLOWED_PDF_CONVERTERS = {"auto", "pymupdf4llm", "markitdown"}


def _clean_bold_title(raw: str) -> str:
    """Normalise a title string that may contain pymupdf4llm bold artefacts.
    规范化可能包含 pymupdf4llm 粗体伪影的标题字符串。

    pymupdf4llm sometimes emits adjacent bold spans as ``**A** **B**`` instead
    of a single ``**A B**`` block.  This helper merges those fragments and then
    strips the outermost ``**...**`` wrapper so the caller gets plain text.
    pymupdf4llm 有时会将相邻的粗体跨度输出为 ``**A** **B**`` 而非单个 ``**A B**`` 块。
    此辅助函数合并这些片段，然后剥离最外层的 ``**...**`` 包装，使调用者获得纯文本。

    Examples::

        "**Overview**"                       → "Overview"
        "**UNITED STATES** **SECURITIES**"   → "UNITED STATES SECURITIES"
        "plain text"                         → "plain text"  (unchanged)
    """
    # Merge adjacent bold spans: "** **" → " "
    # 合并相邻的粗体跨度："** **" → " "
    merged = re.sub(r"\*\*\s*\*\*", " ", raw).strip()
    # Strip outermost **...** if the whole string is wrapped
    # 如果整个字符串被包装，则剥离最外层的 **...**
    if m := re.fullmatch(r"\*\*(.+?)\*\*", merged, re.DOTALL):
        return m.group(1).strip()
    return merged


def extract_outline(md_path: Path) -> list[dict]:
    """Extract document outline (headings) from a Markdown file.
    从 Markdown 文件中提取文档大纲（标题）。

    Recognises three heading styles produced by pymupdf4llm:
    识别 pymupdf4llm 产生的三种标题样式：

    1. Standard Markdown headings: lines starting with one or more '#'.
       Inline ``**...**`` wrappers and adjacent bold spans (``** **``) are
       cleaned so the title is plain text.
       标准 Markdown 标题：以一个或多个 '#' 开头的行。
       内联 ``**...**`` 包装和相邻粗体跨度（``** **``）被清理，使标题为纯文本。

    2. Bold-only structural headings: ``**ITEM 1. BUSINESS**``, ``**PART II**``,
       etc.  SEC filings use bold+caps for section headings with the same font
       size as body text, so pymupdf4llm cannot promote them to # headings.
       纯粗体结构性标题：``**ITEM 1. BUSINESS**``、``**PART II**`` 等。
       SEC 文件使用粗体+大写作为章节标题，字体大小与正文相同，因此 pymupdf4llm 无法将其提升为 # 标题。

    3. Split-bold headings: ``**1** **Introduction**``, ``**3.2** **Attention**``.
       pymupdf4llm emits these when the section number and title text are
       separate spans in the underlying PDF (common in academic papers).
       分割粗体标题：``**1** **Introduction**``、``**3.2** **Attention**``。
       当底层 PDF 中章节号和标题文本是分开的跨度时（常见于学术论文），pymupdf4llm 会输出这些。

    Args:
        md_path: Path to the .md file.

    Returns:
        List of dicts with keys: title (str), line (int, 1-based).
        When the outline is truncated at MAX_OUTLINE_ENTRIES, a sentinel entry
        ``{"truncated": True}`` is appended as the last element so callers can
        render a "showing first N headings" hint without re-scanning the file.
        Returns an empty list if the file cannot be read or has no headings.
    """
    outline: list[dict] = []
    try:
        with md_path.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                stripped = line.strip()
                if not stripped:
                    continue

                # Style 1: standard Markdown heading
                # 样式 1：标准 Markdown 标题
                if stripped.startswith("#"):
                    title = _clean_bold_title(stripped.lstrip("#").strip())
                    if title:
                        outline.append({"title": title, "line": lineno})

                # Style 2: single bold block with SEC structural keyword
                # 样式 2：带有 SEC 结构性关键词的单个粗体块
                elif m := _BOLD_HEADING_RE.match(stripped):
                    title = m.group(1).strip()
                    if title:
                        outline.append({"title": title, "line": lineno})

                # Style 3: split-bold heading — **<num>** **<title>**
                # Regex already enforces max 4 blocks and non-numeric second block.
                # 样式 3：分割粗体标题 — **<num>** **<title>**
                # 正则已强制最多 4 个块且第二个块非数字。
                elif _SPLIT_BOLD_HEADING_RE.match(stripped):
                    title = " ".join(re.findall(r"\*\*([^*]+)\*\*", stripped))
                    if title:
                        outline.append({"title": title, "line": lineno})

                if len(outline) >= MAX_OUTLINE_ENTRIES:
                    outline.append({"truncated": True})
                    break
    except Exception:
        return []

    return outline


def _get_uploads_config_value(key: str, default: object) -> object:
    """Read a value from the uploads config, supporting dict and attribute access.
    从 uploads 配置中读取值，支持字典和属性访问。"""
    cfg = get_app_config()
    uploads_cfg = getattr(cfg, "uploads", None)
    if isinstance(uploads_cfg, dict):
        return uploads_cfg.get(key, default)
    return getattr(uploads_cfg, key, default)


def _get_pdf_converter() -> str:
    """Read pdf_converter setting from app config, defaulting to 'auto'.
    从应用配置中读取 pdf_converter 设置，默认为 'auto'。

    Normalizes the value to lowercase and validates it against the allowed set
    so that values like 'AUTO' or 'MarkItDown' from config.yaml don't silently
    fall through to unexpected behaviour.
    将值规范化为小写并根据允许的集合进行验证，这样 config.yaml 中的 'AUTO' 或 'MarkItDown'
    等值不会静默地导致意外行为。
    """
    try:
        raw = str(_get_uploads_config_value("pdf_converter", "auto")).strip().lower()
        if raw not in _ALLOWED_PDF_CONVERTERS:
            logger.warning("Invalid pdf_converter value %r; falling back to 'auto'", raw)
            return "auto"
        return raw
    except Exception:
        pass
    return "auto"
