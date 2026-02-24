import logging
import mimetypes
import zipfile
from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, Response

from src.gateway.path_utils import resolve_thread_virtual_path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["artifacts"])


def is_text_file_by_content(path: Path, sample_size: int = 8192) -> bool:
    """通过检查内容中的空字节来判断文件是否为文本文件。

    读取文件的前 N 个字节，检查是否包含空字节来判断文件类型。
    文本文件通常不包含空字节。

    Args:
        path: 要检查的文件路径。
        sample_size: 要读取的样本字节数，默认为 8192。

    Returns:
        如果是文本文件返回 True，否则返回 False。
    """
    try:
        with open(path, "rb") as f:
            chunk = f.read(sample_size)
            return b"\x00" not in chunk
    except Exception:
        return False


def _extract_file_from_skill_archive(zip_path: Path, internal_path: str) -> bytes | None:
    """从 .skill ZIP 归档中提取一个文件。

    尝试从 .skill 文件（ZIP 格式）中提取指定路径的文件内容。
    支持直接路径匹配和带顶级目录前缀的路径匹配。

    Args:
        zip_path: .skill 文件路径（ZIP 存档）。
        internal_path: 归档内部的文件路径（例如 "SKILL.md"）。

    Returns:
        文件内容的字节序列；未找到时返回 None。
    """
    if not zipfile.is_zipfile(zip_path):
        return None

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            namelist = zip_ref.namelist()

            if internal_path in namelist:
                return zip_ref.read(internal_path)

            for name in namelist:
                if name.endswith("/" + internal_path) or name == internal_path:
                    return zip_ref.read(name)

            return None
    except (zipfile.BadZipFile, KeyError):
        return None


@router.get(
    "/threads/{thread_id}/artifacts/{path:path}",
    summary="获取工件文件",
    description="检索由 AI 代理生成的工件文件。支持文本、HTML 和二进制文件。",
)
async def get_artifact(thread_id: str, path: str, request) -> FileResponse:
    """按路径获取工件文件。

    支持获取普通文件和 .skill 归档内的文件。根据文件类型返回适当的响应格式。

    Args:
        thread_id (str): 线程 ID。
        path (str): 带虚拟前缀的工件路径（如 mnt/user-data/outputs/file.txt）。前导斜杠将被忽略。
        request: FastAPI 请求对象（框架自动注入）。

    Returns:
        FileResponse：具备正确 Content-Type 的响应，支持以下情况：
        - text/html：HTML 内容将渲染为页面
        - text/*：文本内容以文本形式返回并设置正确的 MIME type
        - 其他：二进制数据以 inline 方式返回，必要时提供下载选项

    Raises:
        HTTPException:
            - 400: 路径无效或不是文件
            - 403: 访问被拒绝
            - 404: 文件未找到

    Notes:
        如果请求包含 download=true，则会将内容作为附件下载。
    """
    if ".skill/" in path:
        skill_marker = ".skill/"
        marker_pos = path.find(skill_marker)
        skill_file_path = path[: marker_pos + len(".skill")]
        internal_path = path[marker_pos + len(skill_marker) :]

        actual_skill_path = resolve_thread_virtual_path(thread_id, skill_file_path)

        if not actual_skill_path.exists():
            raise HTTPException(status_code=404, detail=f"未找到技能文件：{skill_file_path}")

        if not actual_skill_path.is_file():
            raise HTTPException(status_code=400, detail=f"路径不是文件：{skill_file_path}")

        content = _extract_file_from_skill_archive(actual_skill_path, internal_path)
        if content is None:
            raise HTTPException(status_code=404, detail=f"技能归档中未找到文件 '{internal_path}'")

        mime_type, _ = mimetypes.guess_type(internal_path)
        cache_headers = {"Cache-Control": "private, max-age=300"}
        if mime_type and mime_type.startswith("text/"):
            return PlainTextResponse(content=content.decode("utf-8"), media_type=mime_type, headers=cache_headers)

        try:
            return PlainTextResponse(content=content.decode("utf-8"), media_type="text/plain", headers=cache_headers)
        except UnicodeDecodeError:
            return Response(content=content, media_type=mime_type or "application/octet-stream", headers=cache_headers)

    actual_path = resolve_thread_virtual_path(thread_id, path)

    logger.info(f"解析工件路径：thread_id={thread_id}, 请求路径={path}, 实际路径={actual_path}")

    if not actual_path.exists():
        raise HTTPException(status_code=404, detail=f"未找到工件：{path}")

    if not actual_path.is_file():
        raise HTTPException(status_code=400, detail=f"路径不是文件：{path}")

    mime_type, _ = mimetypes.guess_type(actual_path)

    encoded_filename = quote(actual_path.name)

    if request.query_params.get("download"):
        return FileResponse(path=actual_path, filename=actual_path.name, media_type=mime_type, headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"})

    if mime_type and mime_type == "text/html":
        return HTMLResponse(content=actual_path.read_text())

    if mime_type and mime_type.startswith("text/"):
        return PlainTextResponse(content=actual_path.read_text(), media_type=mime_type)

    if is_text_file_by_content(actual_path):
        return PlainTextResponse(content=actual_path.read_text(), media_type=mime_type)

    return Response(content=actual_path.read_bytes(), media_type=mime_type, headers={"Content-Disposition": f"inline; filename*=UTF-8''{encoded_filename}"})
