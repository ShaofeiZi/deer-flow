"""文件上传路由，用于处理文件上传请求。"""

import logging
import os
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from src.agents.middlewares.thread_data_middleware import THREAD_DATA_BASE_DIR
from src.sandbox.sandbox_provider import get_sandbox_provider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/threads/{thread_id}/uploads", tags=["uploads"])

CONVERTIBLE_EXTENSIONS = {
    ".pdf",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".doc",
    ".docx",
}


class UploadResponse(BaseModel):
    """文件上传的响应模型。

    该模型用于表示文件上传操作的结果。

    Attributes:
        success: 上传是否成功。
        files: 已上传文件的信息列表。
        message: 上传结果消息。
    """

    success: bool
    files: list[dict[str, str]]
    message: str


def get_uploads_dir(thread_id: str) -> Path:
    """获取线程的上传目录路径。

    如果目录不存在，将自动创建。

    Args:
        thread_id: 线程 ID。

    Returns:
        上传目录的路径。
    """
    base_dir = Path(os.getcwd()) / THREAD_DATA_BASE_DIR / thread_id / "user-data" / "uploads"
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


async def convert_file_to_markdown(file_path: Path) -> Path | None:
    """使用 markitdown 将文件转换为 Markdown 格式。

    支持转换 PDF、PPT、Excel 和 Word 文档为 Markdown 格式。

    Args:
        file_path: 要转换的文件路径。

    Returns:
        转换成功时返回 Markdown 文件路径，失败时返回 None。
    """
    try:
        from markitdown import MarkItDown

        md = MarkItDown()
        result = md.convert(str(file_path))

        md_path = file_path.with_suffix(".md")
        md_path.write_text(result.text_content, encoding="utf-8")

        logger.info(f"已将 {file_path.name} 转换为 Markdown：{md_path.name}")
        return md_path
    except Exception as e:
        logger.error(f"将 {file_path.name} 转换为 Markdown 失败：{e}")
        return None


@router.post("", response_model=UploadResponse)
async def upload_files(
    thread_id: str,
    files: list[UploadFile] = File(...),
) -> UploadResponse:
    """上传多个文件到线程的上传目录。

    对于 PDF、PPT、Excel 和 Word 文件，将使用 markitdown 转换为 Markdown 格式。
    所有文件（原始文件和转换后的文件）都保存到 /mnt/user-data/uploads。

    Args:
        thread_id: 要上传文件的线程 ID。
        files: 要上传的文件列表。

    Returns:
        UploadResponse: 包含成功状态和文件信息的上传响应。

    Raises:
        HTTPException: 未提供文件时抛出 400 错误，上传失败时抛出 500 错误。
    """
    if not files:
        raise HTTPException(status_code=400, detail="未提供文件")

    uploads_dir = get_uploads_dir(thread_id)
    uploaded_files = []

    sandbox_provider = get_sandbox_provider()
    sandbox_id = sandbox_provider.acquire(thread_id)
    sandbox = sandbox_provider.get(sandbox_id)

    for file in files:
        if not file.filename:
            continue

        try:
            file_path = uploads_dir / file.filename
            content = await file.read()

            relative_path = f".deer-flow/threads/{thread_id}/user-data/uploads/{file.filename}"
            virtual_path = f"/mnt/user-data/uploads/{file.filename}"
            sandbox.update_file(virtual_path, content)

            file_info = {
                "filename": file.filename,
                "size": str(len(content)),
                "path": relative_path,
                "virtual_path": virtual_path,
                "artifact_url": f"/api/threads/{thread_id}/artifacts/mnt/user-data/uploads/{file.filename}",
            }

            logger.info(f"已保存文件：{file.filename}（{len(content)} 字节）至 {relative_path}")

            file_ext = file_path.suffix.lower()
            if file_ext in CONVERTIBLE_EXTENSIONS:
                md_path = await convert_file_to_markdown(file_path)
                if md_path:
                    md_relative_path = f".deer-flow/threads/{thread_id}/user-data/uploads/{md_path.name}"
                    file_info["markdown_file"] = md_path.name
                    file_info["markdown_path"] = md_relative_path
                    file_info["markdown_virtual_path"] = f"/mnt/user-data/uploads/{md_path.name}"
                    file_info["markdown_artifact_url"] = f"/api/threads/{thread_id}/artifacts/mnt/user-data/uploads/{md_path.name}"

            uploaded_files.append(file_info)

        except Exception as e:
            logger.error(f"上传 {file.filename} 失败：{e}")
            raise HTTPException(status_code=500, detail=f"上传 {file.filename} 失败：{str(e)}")

    return UploadResponse(
        success=True,
        files=uploaded_files,
        message=f"成功上传 {len(uploaded_files)} 个文件",
    )


@router.get("/list", response_model=dict)
async def list_uploaded_files(thread_id: str) -> dict:
    """列出线程上传目录中的所有文件。

    Args:
        thread_id: 要列出文件的线程 ID。

    Returns:
        包含文件列表及其元数据的字典。
    """
    uploads_dir = get_uploads_dir(thread_id)

    if not uploads_dir.exists():
        return {"files": [], "count": 0}

    files = []
    for file_path in sorted(uploads_dir.iterdir()):
        if file_path.is_file():
            stat = file_path.stat()
            relative_path = f".deer-flow/threads/{thread_id}/user-data/uploads/{file_path.name}"
            files.append(
                {
                    "filename": file_path.name,
                    "size": stat.st_size,
                    "path": relative_path,
                    "virtual_path": f"/mnt/user-data/uploads/{file_path.name}",
                    "artifact_url": f"/api/threads/{thread_id}/artifacts/mnt/user-data/uploads/{file_path.name}",
                    "extension": file_path.suffix,
                    "modified": stat.st_mtime,
                }
            )

    return {"files": files, "count": len(files)}


@router.delete("/{filename}")
async def delete_uploaded_file(thread_id: str, filename: str) -> dict:
    """删除线程上传目录中的文件。

    Args:
        thread_id: 线程 ID。
        filename: 要删除的文件名。

    Returns:
        成功消息。

    Raises:
        HTTPException: 文件不存在时抛出 404 错误，访问被拒绝时抛出 403 错误。
    """
    uploads_dir = get_uploads_dir(thread_id)
    file_path = uploads_dir / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"未找到文件：{filename}")

    try:
        file_path.resolve().relative_to(uploads_dir.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="访问被拒绝")

    try:
        file_path.unlink()
        logger.info(f"已删除文件：{filename}")
        return {"success": True, "message": f"已删除 {filename}"}
    except Exception as e:
        logger.error(f"删除 {filename} 失败：{e}")
        raise HTTPException(status_code=500, detail=f"删除 {filename} 失败：{str(e)}")
