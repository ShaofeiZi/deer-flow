"""子代理执行引擎。"""

import logging
import threading
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from langchain.agents import create_agent
from langchain.tools import BaseTool
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from src.agents.thread_state import SandboxState, ThreadDataState, ThreadState
from src.models import create_chat_model
from src.subagents.config import SubagentConfig

logger = logging.getLogger(__name__)


class SubagentStatus(Enum):
    """子代理执行状态。"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


@dataclass
class SubagentResult:
    """子代理执行结果。

    Attributes:
        task_id: 此执行的唯一标识符。
        trace_id: 分布式追踪的追踪 ID（关联父代理和子代理日志）。
        status: 执行的当前状态。
        result: 最终结果消息（如果已完成）。
        error: 错误消息（如果失败）。
        started_at: 执行开始时间。
        completed_at: 执行完成时间。
        ai_messages: 执行期间生成的完整 AI 消息列表（字典格式）。
    """

    task_id: str
    trace_id: str
    status: SubagentStatus
    result: str | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    ai_messages: list[dict[str, Any]] | None = None

    def __post_init__(self):
        """初始化可变默认值。"""
        if self.ai_messages is None:
            self.ai_messages = []


# 后台任务结果的全局存储
_background_tasks: dict[str, SubagentResult] = {}
_background_tasks_lock = threading.Lock()

# 用于后台任务调度和编排的线程池
_scheduler_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="subagent-scheduler-")

# 用于实际子代理执行的线程池（支持超时）
# 较大的池以避免调度器提交执行任务时阻塞
_execution_pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="subagent-exec-")


def _filter_tools(
    all_tools: list[BaseTool],
    allowed: list[str] | None,
    disallowed: list[str] | None,
) -> list[BaseTool]:
    """根据子代理配置过滤工具。

    Args:
        all_tools: 所有可用工具列表。
        allowed: 工具名称的白名单。如果提供，只包含这些工具。
        disallowed: 工具名称的黑名单。这些工具始终被排除。

    Returns:
        过滤后的工具列表。
    """
    filtered = all_tools

    # 如果指定了白名单则应用
    if allowed is not None:
        allowed_set = set(allowed)
        filtered = [t for t in filtered if t.name in allowed_set]

    # 应用黑名单
    if disallowed is not None:
        disallowed_set = set(disallowed)
        filtered = [t for t in filtered if t.name not in disallowed_set]

    return filtered


def _get_model_name(config: SubagentConfig, parent_model: str | None) -> str | None:
    """解析子代理的模型名称。

    Args:
        config: 子代理配置。
        parent_model: 父代理的模型名称。

    Returns:
        要使用的模型名称，或 None 以使用默认值。
    """
    if config.model == "inherit":
        return parent_model
    return config.model


class SubagentExecutor:
    """子代理执行器。"""

    def __init__(
        self,
        config: SubagentConfig,
        tools: list[BaseTool],
        parent_model: str | None = None,
        sandbox_state: SandboxState | None = None,
        thread_data: ThreadDataState | None = None,
        thread_id: str | None = None,
        trace_id: str | None = None,
    ):
        """初始化执行器。

        Args:
            config: 子代理配置。
            tools: 所有可用工具列表（将被过滤）。
            parent_model: 父代理的模型名称，用于继承。
            sandbox_state: 父代理的沙箱状态。
            thread_data: 父代理的线程数据。
            thread_id: 用于沙箱操作的线程 ID。
            trace_id: 父代理的追踪 ID，用于分布式追踪。
        """
        self.config = config
        self.parent_model = parent_model
        self.sandbox_state = sandbox_state
        self.thread_data = thread_data
        self.thread_id = thread_id
        # 如果未提供则生成 trace_id（用于顶层调用）
        self.trace_id = trace_id or str(uuid.uuid4())[:8]

        # 根据配置过滤工具
        self.tools = _filter_tools(
            tools,
            config.tools,
            config.disallowed_tools,
        )

        logger.info(f"[trace={self.trace_id}] SubagentExecutor 已初始化：{config.name}，共 {len(self.tools)} 个工具")

    def _create_agent(self):
        """创建代理实例。"""
        model_name = _get_model_name(self.config, self.parent_model)
        model = create_chat_model(name=model_name, thinking_enabled=False)

        # 子代理需要最少的中间件以确保工具可以访问沙箱和 thread_data
        # 这些中间件将重用父代理的沙箱/thread_data
        from src.agents.middlewares.thread_data_middleware import ThreadDataMiddleware
        from src.sandbox.middleware import SandboxMiddleware

        middlewares = [
            ThreadDataMiddleware(lazy_init=True),  # 计算线程路径
            SandboxMiddleware(lazy_init=True),  # 重用父代理的沙箱（不重新获取）
        ]

        return create_agent(
            model=model,
            tools=self.tools,
            middleware=middlewares,
            system_prompt=self.config.system_prompt,
            state_schema=ThreadState,
        )

    def _build_initial_state(self, task: str) -> dict[str, Any]:
        """构建代理执行的初始状态。

        Args:
            task: 任务描述。

        Returns:
            初始状态字典。
        """
        state: dict[str, Any] = {
            "messages": [HumanMessage(content=task)],
        }

        # 从父代理传递沙箱和线程数据
        if self.sandbox_state is not None:
            state["sandbox"] = self.sandbox_state
        if self.thread_data is not None:
            state["thread_data"] = self.thread_data

        return state

    def execute(self, task: str, result_holder: SubagentResult | None = None) -> SubagentResult:
        """同步执行任务。

        Args:
            task: 子代理的任务描述。
            result_holder: 可选的预创建结果对象，在执行期间更新。

        Returns:
            包含执行结果的 SubagentResult。
        """
        if result_holder is not None:
            # 使用提供的结果持有者（用于异步执行和实时更新）
            result = result_holder
        else:
            # 为同步执行创建新结果
            task_id = str(uuid.uuid4())[:8]
            result = SubagentResult(
                task_id=task_id,
                trace_id=self.trace_id,
                status=SubagentStatus.RUNNING,
                started_at=datetime.now(),
            )

        try:
            agent = self._create_agent()
            state = self._build_initial_state(task)

            # 构建配置，包含 thread_id 用于沙箱访问和递归限制
            run_config: RunnableConfig = {
                "recursion_limit": self.config.max_turns,
            }
            context = {}
            if self.thread_id:
                run_config["configurable"] = {"thread_id": self.thread_id}
                context["thread_id"] = self.thread_id

            logger.info(f"[trace={self.trace_id}] 子代理 {self.config.name} 开始执行，max_turns={self.config.max_turns}")

            # 使用 stream 而不是 invoke 以获取实时更新
            # 这允许我们在生成 AI 消息时收集它们
            final_state = None
            for chunk in agent.stream(state, config=run_config, context=context, stream_mode="values"):  # type: ignore[arg-type]
                final_state = chunk

                # 从当前状态提取 AI 消息
                messages = chunk.get("messages", [])
                if messages:
                    last_message = messages[-1]
                    # 检查是否为新的 AI 消息
                    if isinstance(last_message, AIMessage):
                        # 将消息转换为字典以便序列化
                        message_dict = last_message.model_dump()
                        # 仅当不在列表中时才添加（避免重复）
                        # 如果可用则通过比较消息 ID，否则比较完整字典
                        message_id = message_dict.get("id")
                        is_duplicate = False
                        if message_id:
                            is_duplicate = any(msg.get("id") == message_id for msg in result.ai_messages)
                        else:
                            is_duplicate = message_dict in result.ai_messages

                        if not is_duplicate:
                            result.ai_messages.append(message_dict)
                            logger.info(f"[trace={self.trace_id}] 子代理 {self.config.name} 捕获到第 {len(result.ai_messages)} 条 AI 消息")

            logger.info(f"[trace={self.trace_id}] 子代理 {self.config.name} 执行完成")

            if final_state is None:
                logger.warning(f"[trace={self.trace_id}] 子代理 {self.config.name} 没有最终状态")
                result.result = "未生成响应"
            else:
                # 提取最终消息 - 查找最后一条 AIMessage
                messages = final_state.get("messages", [])
                logger.info(f"[trace={self.trace_id}] 子代理 {self.config.name} 最终消息数量：{len(messages)}")

                # 在对话中查找最后一条 AIMessage
                last_ai_message = None
                for msg in reversed(messages):
                    if isinstance(msg, AIMessage):
                        last_ai_message = msg
                        break

                if last_ai_message is not None:
                    content = last_ai_message.content
                    # 处理字符串和列表类型的内容作为最终结果
                    if isinstance(content, str):
                        result.result = content
                    elif isinstance(content, list):
                        # 仅从内容块列表中提取文本作为最终结果
                        text_parts = []
                        for block in content:
                            if isinstance(block, str):
                                text_parts.append(block)
                            elif isinstance(block, dict) and "text" in block:
                                text_parts.append(block["text"])
                        result.result = "\n".join(text_parts) if text_parts else "响应中没有文本内容"
                    else:
                        result.result = str(content)
                elif messages:
                    # 回退：如果未找到 AIMessage 则使用最后一条消息
                    last_message = messages[-1]
                    logger.warning(f"[trace={self.trace_id}] 子代理 {self.config.name} 未找到 AIMessage，使用最后一条消息：{type(last_message)}")
                    result.result = str(last_message.content) if hasattr(last_message, "content") else str(last_message)
                else:
                    logger.warning(f"[trace={self.trace_id}] 子代理 {self.config.name} 最终状态中没有消息")
                    result.result = "未生成响应"

            result.status = SubagentStatus.COMPLETED
            result.completed_at = datetime.now()

        except Exception as e:
            logger.exception(f"[trace={self.trace_id}] 子代理 {self.config.name} 执行失败")
            result.status = SubagentStatus.FAILED
            result.error = str(e)
            result.completed_at = datetime.now()

        return result

    def execute_async(self, task: str, task_id: str | None = None) -> str:
        """在后台启动任务执行。

        Args:
            task: 子代理的任务描述。
            task_id: 可选的任务 ID。如果未提供，将生成随机 UUID。

        Returns:
            可用于稍后检查状态的任务 ID。
        """
        # 使用提供的 task_id 或生成新的
        if task_id is None:
            task_id = str(uuid.uuid4())[:8]

        # 创建初始待处理结果
        result = SubagentResult(
            task_id=task_id,
            trace_id=self.trace_id,
            status=SubagentStatus.PENDING,
        )

        logger.info(f"[trace={self.trace_id}] 子代理 {self.config.name} 开始异步执行，task_id={task_id}")

        with _background_tasks_lock:
            _background_tasks[task_id] = result

        # 提交到调度器池
        def run_task():
            """在后台运行任务。"""
            with _background_tasks_lock:
                _background_tasks[task_id].status = SubagentStatus.RUNNING
                _background_tasks[task_id].started_at = datetime.now()
                result_holder = _background_tasks[task_id]

            try:
                # 提交执行到执行池并设置超时
                # 传递 result_holder 以便 execute() 可以实时更新它
                execution_future: Future = _execution_pool.submit(self.execute, task, result_holder)
                try:
                    # 等待执行完成（带超时）
                    exec_result = execution_future.result(timeout=self.config.timeout_seconds)
                    with _background_tasks_lock:
                        _background_tasks[task_id].status = exec_result.status
                        _background_tasks[task_id].result = exec_result.result
                        _background_tasks[task_id].error = exec_result.error
                        _background_tasks[task_id].completed_at = datetime.now()
                        _background_tasks[task_id].ai_messages = exec_result.ai_messages
                except FuturesTimeoutError:
                    logger.error(f"[trace={self.trace_id}] 子代理 {self.config.name} 执行在 {self.config.timeout_seconds} 秒后超时")
                    with _background_tasks_lock:
                        _background_tasks[task_id].status = SubagentStatus.TIMED_OUT
                        _background_tasks[task_id].error = f"执行在 {self.config.timeout_seconds} 秒后超时"
                        _background_tasks[task_id].completed_at = datetime.now()
                    # 取消 future（尽力而为 - 可能无法停止实际执行）
                    execution_future.cancel()
            except Exception as e:
                logger.exception(f"[trace={self.trace_id}] 子代理 {self.config.name} 异步执行失败")
                with _background_tasks_lock:
                    _background_tasks[task_id].status = SubagentStatus.FAILED
                    _background_tasks[task_id].error = str(e)
                    _background_tasks[task_id].completed_at = datetime.now()

        _scheduler_pool.submit(run_task)
        return task_id


MAX_CONCURRENT_SUBAGENTS = 3


def get_background_task_result(task_id: str) -> SubagentResult | None:
    """获取后台任务的结果。

    Args:
        task_id: execute_async 返回的任务 ID。

    Returns:
        如果找到则返回 SubagentResult，否则返回 None。
    """
    with _background_tasks_lock:
        return _background_tasks.get(task_id)


def list_background_tasks() -> list[SubagentResult]:
    """列出所有后台任务。

    Returns:
        所有 SubagentResult 实例的列表。
    """
    with _background_tasks_lock:
        return list(_background_tasks.values())
