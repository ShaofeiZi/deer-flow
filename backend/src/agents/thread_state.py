from typing import Annotated, NotRequired, TypedDict

from langchain.agents import AgentState


class SandboxState(TypedDict):
    """沙箱状态类型定义。

    用于存储沙箱相关的状态信息。

    Attributes:
        sandbox_id: 沙箱实例的唯一标识符。
    """

    sandbox_id: NotRequired[str | None]


class ThreadDataState(TypedDict):
    """线程数据状态类型定义。

    用于存储线程相关的路径信息。

    Attributes:
        workspace_path: 工作区路径。
        uploads_path: 上传文件路径。
        outputs_path: 输出文件路径。
    """

    workspace_path: NotRequired[str | None]
    uploads_path: NotRequired[str | None]
    outputs_path: NotRequired[str | None]


class ViewedImageData(TypedDict):
    """已查看图像数据类型定义。

    用于存储图像的 Base64 编码和 MIME 类型。

    Attributes:
        base64: 图像的 Base64 编码字符串。
        mime_type: 图像的 MIME 类型。
    """

    base64: str
    mime_type: str


def merge_artifacts(existing: list[str] | None, new: list[str] | None) -> list[str]:
    """用于 artifacts 列表的归并器 - 将 artifact 合并并去重。

    Args:
        existing: 现有的 artifacts 列表。
        new: 新增的 artifacts 列表。

    Returns:
        合并并去重后的 artifacts 列表。
    """
    if existing is None:
        return new or []
    if new is None:
        return existing
    return list(dict.fromkeys(existing + new))


def merge_viewed_images(existing: dict[str, ViewedImageData] | None, new: dict[str, ViewedImageData] | None) -> dict[str, ViewedImageData]:
    """用于 viewed_images 字典的归并器 - 将图像字典合并。

    特例：若 new 是空字典 {}，则清空现有图像。
    这允许中间件在处理后清理 viewed_images 状态。

    Args:
        existing: 现有的已查看图像字典。
        new: 新增的已查看图像字典。

    Returns:
        合并后的图像字典。
    """
    if existing is None:
        return new or {}
    if new is None:
        return existing
    if len(new) == 0:
        return {}
    return {**existing, **new}


class ThreadState(AgentState):
    """线程状态类型定义。

    扩展 AgentState，添加沙箱、线程数据、标题、工件、待办事项、
    上传文件和已查看图像等状态字段。

    Attributes:
        sandbox: 沙箱状态。
        thread_data: 线程数据状态。
        title: 线程标题。
        artifacts: 工件路径列表（自动合并去重）。
        todos: 待办事项列表。
        uploaded_files: 上传文件信息列表。
        viewed_images: 已查看图像字典（图像路径 -> {base64, mime_type}）。
    """

    sandbox: NotRequired[SandboxState | None]
    thread_data: NotRequired[ThreadDataState | None]
    title: NotRequired[str | None]
    artifacts: Annotated[list[str], merge_artifacts]
    todos: NotRequired[list | None]
    uploaded_files: NotRequired[list[dict] | None]
    viewed_images: Annotated[dict[str, ViewedImageData], merge_viewed_images]
