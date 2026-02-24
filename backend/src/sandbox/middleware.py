from typing import NotRequired, override

from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware
from langgraph.runtime import Runtime

from src.agents.thread_state import SandboxState, ThreadDataState
from src.sandbox import get_sandbox_provider


class SandboxMiddlewareState(AgentState):
    """与 `ThreadState` 架构兼容。"""

    sandbox: NotRequired[SandboxState | None]
    thread_data: NotRequired[ThreadDataState | None]


class SandboxMiddleware(AgentMiddleware[SandboxMiddlewareState]):
    """创建 sandbox 环境并将其分配给 agent。

    Lifecycle Management:
    - 使用 lazy_init=True（默认值）：在第一次调用 tool 时获取 sandbox。
    - 使用 lazy_init=False：在 before_agent() 中首次调用时就获取 sandbox。
    - sandbox 将在同一 thread 的多轮对话中重复使用。
    - 为避免重复创建，不会在每次 agent 调用后释放 sandbox。
    - 通过 SandboxProvider.shutdown() 在应用程序退出时进行清理。
    """

    state_schema = SandboxMiddlewareState

    def __init__(self, lazy_init: bool = True):
        """初始化 sandbox 中间件。"""

        # 参数：
        #     lazy_init: 如果为 True，则将 sandbox 的获取延迟到第一次工具调用时。
        #                如果为 False，则在 before_agent() 中提前获取 sandbox。
        #                默认值为 True，以实现最佳性能。
        super().__init__()
        self._lazy_init = lazy_init

    def _acquire_sandbox(self, thread_id: str) -> str:
        """
        【函数功能描述】
        
        参数:
            【参数名】: 【参数描述】
        
        返回:
            【返回值描述】
        """

        provider = get_sandbox_provider()
        sandbox_id = provider.acquire(thread_id)
        print(f"Acquiring sandbox {sandbox_id}")
        return sandbox_id

    @override
    def before_agent(self, state: SandboxMiddlewareState, runtime: Runtime) -> dict | None:
        """
        【函数功能描述】
        
        参数:
            【参数名】: 【参数描述】
        
        返回:
            【返回值描述】
        """

        # Skip acquisition if lazy_init is enabled
        if self._lazy_init:
            return super().before_agent(state, runtime)

        # Eager initialization (original behavior)
        sandbox_state = getattr(state, "sandbox", None)
        if sandbox_state is None:
            thread_ctx = runtime.context if isinstance(runtime.context, dict) else {}
            thread_id = thread_ctx.get("thread_id") or ""
            print(f"Thread ID: {thread_id}")
            sandbox_id = self._acquire_sandbox(thread_id)
            return {"sandbox": {"sandbox_id": sandbox_id}}
        return super().before_agent(state, runtime)
