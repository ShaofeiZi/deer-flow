"""用于将工作委托给子代理的任务工具。"""

import logging
import time
import uuid
from dataclasses import replace
from typing import Annotated, Literal

from langchain.tools import InjectedToolCallId, ToolRuntime, tool
from langgraph.config import get_stream_writer
from langgraph.typing import ContextT

from src.agents.lead_agent.prompt import get_skills_prompt_section
from src.agents.thread_state import ThreadState
from src.subagents import SubagentExecutor, get_subagent_config
from src.subagents.executor import SubagentStatus, get_background_task_result

logger = logging.getLogger(__name__)


@tool("task", parse_docstring=True)
def task_tool(
    runtime: ToolRuntime[ContextT, ThreadState],
    description: str,
    prompt: str,
    subagent_type: Literal["general-purpose", "bash"],
    tool_call_id: Annotated[str, InjectedToolCallId],
    max_turns: int | None = None,
) -> str:
    """将任务委托给在自己的上下文中运行的专用子代理。

    子代理帮助你：
    - 通过将探索和实现分开来保持上下文
    - 自主处理复杂的多步骤任务
    - 在隔离的上下文中执行命令或操作

    可用的子代理类型：
    - **general-purpose**：用于需要探索和行动的复杂多步骤任务的能力强大的代理。
      当任务需要复杂推理、多个依赖步骤或能从隔离上下文中受益时使用。
    - **bash**：用于运行 bash 命令的命令执行专家。用于 git 操作、
      构建过程或命令输出冗长的情况。

    何时使用此工具：
    - 需要多个步骤或工具的复杂任务
    - 产生冗长输出的任务
    - 当你想将上下文与主对话隔离时
    - 并行研究或探索任务

    何时不使用此工具：
    - 简单的单步操作（直接使用工具）
    - 需要用户交互或澄清的任务

    Args:
        description: 任务的简短（3-5 个词）描述，用于日志/显示。始终将此参数放在第一位。
        prompt: 子代理的任务描述。要具体明确需要做什么。始终将此参数放在第二位。
        subagent_type: 要使用的子代理类型。始终将此参数放在第三位。
        max_turns: 可选的代理最大轮次。默认为子代理配置的最大值。
    """
    # 获取子代理配置
    config = get_subagent_config(subagent_type)
    if config is None:
        return f"错误：未知的子代理类型 '{subagent_type}'。可用类型：general-purpose、bash"

    # 构建配置覆盖
    overrides: dict = {}

    skills_section = get_skills_prompt_section()
    if skills_section:
        overrides["system_prompt"] = config.system_prompt + "\n\n" + skills_section

    if max_turns is not None:
        overrides["max_turns"] = max_turns

    if overrides:
        config = replace(config, **overrides)

    # 从运行时提取父代理上下文
    sandbox_state = None
    thread_data = None
    thread_id = None
    parent_model = None
    trace_id = None

    if runtime is not None:
        sandbox_state = runtime.state.get("sandbox")
        thread_data = runtime.state.get("thread_data")
        thread_id = runtime.context.get("thread_id")

        # 尝试从 configurable 获取父代理模型
        metadata = runtime.config.get("metadata", {})
        parent_model = metadata.get("model_name")

        # 获取或生成 trace_id 用于分布式追踪
        trace_id = metadata.get("trace_id") or str(uuid.uuid4())[:8]

    # 获取可用工具（排除 task 工具以防止嵌套）
    # 延迟导入以避免循环依赖
    from src.tools import get_available_tools

    # 子代理不应启用子代理工具（防止递归嵌套）
    tools = get_available_tools(model_name=parent_model, subagent_enabled=False)

    # 创建执行器
    executor = SubagentExecutor(
        config=config,
        tools=tools,
        parent_model=parent_model,
        sandbox_state=sandbox_state,
        thread_data=thread_data,
        thread_id=thread_id,
        trace_id=trace_id,
    )

    # 启动后台执行（始终异步以防止阻塞）
    # 使用 tool_call_id 作为 task_id 以便更好地追踪
    task_id = executor.execute_async(prompt, task_id=tool_call_id)
    logger.info(f"[trace={trace_id}] 已启动后台任务 {task_id}，正在轮询完成状态...")

    # 在后端轮询任务完成（无需 LLM 轮询）
    poll_count = 0
    last_status = None
    last_message_count = 0  # 跟踪已发送的 AI 消息数量

    writer = get_stream_writer()
    # 发送任务开始消息
    writer({"type": "task_started", "task_id": task_id, "description": description})

    while True:
        result = get_background_task_result(task_id)

        if result is None:
            logger.error(f"[trace={trace_id}] 任务 {task_id} 在后台任务中未找到")
            writer({"type": "task_failed", "task_id": task_id, "error": "任务在后台任务中消失"})
            return f"错误：任务 {task_id} 在后台任务中消失"

        # 记录状态变化以便调试
        if result.status != last_status:
            logger.info(f"[trace={trace_id}] 任务 {task_id} 状态：{result.status.value}")
            last_status = result.status

        # 检查新的 AI 消息并发送 task_running 事件
        current_message_count = len(result.ai_messages)
        if current_message_count > last_message_count:
            # 为每条新消息发送 task_running 事件
            for i in range(last_message_count, current_message_count):
                message = result.ai_messages[i]
                writer(
                    {
                        "type": "task_running",
                        "task_id": task_id,
                        "message": message,
                        "message_index": i + 1,  # 基于 1 的索引用于显示
                        "total_messages": current_message_count,
                    }
                )
                logger.info(f"[trace={trace_id}] 任务 {task_id} 发送消息 #{i + 1}/{current_message_count}")
            last_message_count = current_message_count

        # 检查任务是否完成、失败或超时
        if result.status == SubagentStatus.COMPLETED:
            writer({"type": "task_completed", "task_id": task_id, "result": result.result})
            logger.info(f"[trace={trace_id}] 任务 {task_id} 在 {poll_count} 次轮询后完成")
            return f"任务成功。结果：{result.result}"
        elif result.status == SubagentStatus.FAILED:
            writer({"type": "task_failed", "task_id": task_id, "error": result.error})
            logger.error(f"[trace={trace_id}] 任务 {task_id} 失败：{result.error}")
            return f"任务失败。错误：{result.error}"
        elif result.status == SubagentStatus.TIMED_OUT:
            writer({"type": "task_timed_out", "task_id": task_id, "error": result.error})
            logger.warning(f"[trace={trace_id}] 任务 {task_id} 超时：{result.error}")
            return f"任务超时。错误：{result.error}"

        # 仍在运行，等待下一次轮询
        time.sleep(5)  # 每 5 秒轮询一次
        poll_count += 1

        # 轮询超时作为安全网（以防线程池超时不起作用）
        # 设置为 16 分钟（长于默认的 15 分钟线程池超时）
        # 这捕获后台任务卡住的边缘情况
        if poll_count > 192:  # 192 * 5s = 16 分钟
            logger.error(f"[trace={trace_id}] 任务 {task_id} 轮询在 {poll_count} 次后超时（应该被线程池超时捕获）")
            writer({"type": "task_timed_out", "task_id": task_id})
            return f"任务轮询在 16 分钟后超时。这可能表示后台任务卡住。状态：{result.status.value}"
