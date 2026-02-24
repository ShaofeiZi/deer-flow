from typing import Annotated

from langchain.tools import InjectedToolCallId, ToolRuntime, tool
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from langgraph.typing import ContextT

from src.agents.thread_state import ThreadState


@tool("present_files", parse_docstring=True)
def present_file_tool(
    runtime: ToolRuntime[ContextT, ThreadState],
    filepaths: list[str],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """使文件对用户可见，以便在客户端界面中查看和渲染。

    何时使用 present_files 工具：

    - 使任何文件可供用户查看、下载或交互
    - 一次呈现多个相关文件
    - 创建应呈现给用户的文件后

    何时不使用 present_files 工具：

    - 当你只需要读取文件内容供自己处理时
    - 对于不打算让用户查看的临时或中间文件

    注意：
    - 创建文件并将其移动到 `/mnt/user-data/outputs` 目录后，应调用此工具。
    - 此工具可以安全地与其他工具并行调用。状态更新由归并器处理以防止冲突。

    Args:
        filepaths: 要呈现给用户的绝对文件路径列表。**只有** `/mnt/user-data/outputs` 中的文件可以被呈现。
    """
    # merge_artifacts 归并器将处理合并和去重
    return Command(
        update={"artifacts": filepaths, "messages": [ToolMessage("成功呈现文件", tool_call_id=tool_call_id)]},
    )
