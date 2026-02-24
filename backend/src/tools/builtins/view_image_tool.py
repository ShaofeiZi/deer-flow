import base64
import mimetypes
from pathlib import Path
from typing import Annotated

from langchain.tools import InjectedToolCallId, ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph.typing import ContextT

from src.agents.thread_state import ThreadState
from src.sandbox.tools import get_thread_data, replace_virtual_path


@tool("view_image", parse_docstring=True)
def view_image_tool(
    runtime: ToolRuntime[ContextT, ThreadState],
    image_path: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """读取图像文件。

    使用此工具读取图像文件并使其可供显示。

    何时使用 view_image 工具：
    - 当需要查看图像文件时。

    何时不使用 view_image 工具：
    - 对于非图像文件（改用 present_files）
    - 对于多个文件（改用 present_files）

    Args:
        image_path: 图像文件的绝对路径。支持常见格式：jpg、jpeg、png、webp。
    """
    # 将虚拟路径替换为实际路径
    # /mnt/user-data/* 路径映射到线程特定目录
    thread_data = get_thread_data(runtime)
    actual_path = replace_virtual_path(image_path, thread_data)

    # 验证路径是绝对路径
    path = Path(actual_path)
    if not path.is_absolute():
        return Command(
            update={"messages": [ToolMessage(f"错误：路径必须是绝对路径，实际为：{image_path}", tool_call_id=tool_call_id)]},
        )

    # 验证文件存在
    if not path.exists():
        return Command(
            update={"messages": [ToolMessage(f"错误：未找到图像文件：{image_path}", tool_call_id=tool_call_id)]},
        )

    # 验证是文件（不是目录）
    if not path.is_file():
        return Command(
            update={"messages": [ToolMessage(f"错误：路径不是文件：{image_path}", tool_call_id=tool_call_id)]},
        )

    # 验证图像扩展名
    valid_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    if path.suffix.lower() not in valid_extensions:
        return Command(
            update={"messages": [ToolMessage(f"错误：不支持的图像格式：{path.suffix}。支持的格式：{', '.join(valid_extensions)}", tool_call_id=tool_call_id)]},
        )

    # 从文件扩展名检测 MIME 类型
    mime_type, _ = mimetypes.guess_type(actual_path)
    if mime_type is None:
        # 回退到常见图像格式的默认 MIME 类型
        extension_to_mime = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }
        mime_type = extension_to_mime.get(path.suffix.lower(), "application/octet-stream")

    # 读取图像文件并转换为 base64
    try:
        with open(actual_path, "rb") as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode("utf-8")
    except Exception as e:
        return Command(
            update={"messages": [ToolMessage(f"读取图像文件失败：{str(e)}", tool_call_id=tool_call_id)]},
        )

    # 更新状态中的 viewed_images
    # merge_viewed_images 归并器将处理与现有图像的合并
    new_viewed_images = {image_path: {"base64": image_base64, "mime_type": mime_type}}

    return Command(
        update={"viewed_images": new_viewed_images, "messages": [ToolMessage("成功读取图像", tool_call_id=tool_call_id)]},
    )
