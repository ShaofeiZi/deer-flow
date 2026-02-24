from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, TodoListMiddleware
from langchain_core.runnables import RunnableConfig

from src.agents.lead_agent.prompt import apply_prompt_template
from src.agents.middlewares.clarification_middleware import ClarificationMiddleware
from src.agents.middlewares.dangling_tool_call_middleware import DanglingToolCallMiddleware
from src.agents.middlewares.memory_middleware import MemoryMiddleware
from src.agents.middlewares.subagent_limit_middleware import SubagentLimitMiddleware
from src.agents.middlewares.thread_data_middleware import ThreadDataMiddleware
from src.agents.middlewares.title_middleware import TitleMiddleware
from src.agents.middlewares.uploads_middleware import UploadsMiddleware
from src.agents.middlewares.view_image_middleware import ViewImageMiddleware
from src.agents.thread_state import ThreadState
from src.config.summarization_config import get_summarization_config
from src.models import create_chat_model
from src.sandbox.middleware import SandboxMiddleware


def _create_summarization_middleware() -> SummarizationMiddleware | None:
    """从配置创建并配置 SummarizationMiddleware。

    根据摘要配置创建中间件实例。如果摘要功能未启用，则返回 None。

    Returns:
        配置好的 SummarizationMiddleware 实例，或 None（如果未启用）。
    """
    config = get_summarization_config()

    if not config.enabled:
        return None

    trigger = None
    if config.trigger is not None:
        if isinstance(config.trigger, list):
            trigger = [t.to_tuple() for t in config.trigger]
        else:
            trigger = config.trigger.to_tuple()

    keep = config.keep.to_tuple()

    if config.model_name:
        model = config.model_name
    else:
        model = create_chat_model(thinking_enabled=False)

    kwargs = {
        "model": model,
        "trigger": trigger,
        "keep": keep,
    }

    if config.trim_tokens_to_summarize is not None:
        kwargs["trim_tokens_to_summarize"] = config.trim_tokens_to_summarize

    if config.summary_prompt is not None:
        kwargs["summary_prompt"] = config.summary_prompt

    return SummarizationMiddleware(**kwargs)


def _create_todo_list_middleware(is_plan_mode: bool) -> TodoListMiddleware | None:
    """创建并配置 TodoList 中间件。

    Args:
        is_plan_mode: 是否启用计划模式（带 TodoList 中间件）。

    Returns:
        如果计划模式启用，返回 TodoListMiddleware 实例，否则返回 None。
    """
    if not is_plan_mode:
        return None

    system_prompt = """
<todo_list_system>
你可以使用 `write_todos` 工具来帮助管理和跟踪复杂的多步骤目标。

**关键规则：**
- 完成每个步骤后立即将待办事项标记为已完成 - 不要批量完成
- 任何时候只保持一个任务为 `in_progress`（除非任务可以并行运行）
- 在工作时实时更新待办列表 - 这让用户可以了解你的进度
- 不要将此工具用于简单任务（< 3 步）- 直接完成即可

**何时使用：**
此工具专为需要系统跟踪的复杂目标设计：
- 需要 3 个以上不同步骤的复杂多步骤任务
- 需要仔细规划和执行的非平凡任务
- 用户明确要求待办列表
- 用户提供多个任务（编号或逗号分隔的列表）
- 计划可能需要根据中间结果进行修订

**何时不使用：**
- 单一、直接的任务
- 琐碎任务（< 3 步）
- 纯对话或信息请求
- 方法显而易见的简单工具调用

**最佳实践：**
- 将复杂任务分解为更小的、可操作的步骤
- 使用清晰、描述性的任务名称
- 删除不再相关的任务
- 添加在实现过程中发现的新任务
- 不要害怕随着了解更多而修改待办列表

**任务管理：**
编写待办事项需要时间和令牌 - 在有助于管理复杂问题时使用，而不是用于简单请求。
</todo_list_system>
"""

    tool_description = """使用此工具为复杂工作会话创建和管理结构化任务列表。

**重要：仅将此工具用于复杂任务（3 步以上）。对于简单请求，直接执行工作即可。**

## 何时使用

在以下场景使用此工具：
1. **复杂多步骤任务**：当任务需要 3 个或更多不同步骤或操作时
2. **非平凡任务**：需要仔细规划或多个操作的任务
3. **用户明确要求待办列表**：当用户直接要求你跟踪任务时
4. **多个任务**：当用户提供要完成的事项列表时
5. **动态规划**：当计划可能需要根据中间结果更新时

## 何时不使用

在以下情况跳过此工具：
1. 任务简单直接，少于 3 步
2. 任务琐碎，跟踪没有好处
3. 任务纯对话或信息性质
4. 很清楚需要做什么，可以直接执行

## 如何使用

1. **开始任务**：在开始工作前将其标记为 `in_progress`
2. **完成任务**：完成后立即将其标记为 `completed`
3. **更新列表**：根据需要添加新任务、删除不相关的任务或更新描述
4. **多次更新**：可以一次进行多次更新（例如，完成一个任务并开始下一个）

## 任务状态

- `pending`：任务尚未开始
- `in_progress`：当前正在处理（如果任务可以并行运行，可以有多个）
- `completed`：任务已成功完成

## 任务完成要求

**关键：只有在完全完成任务后才将任务标记为已完成。**

如果有以下情况，永远不要将任务标记为已完成：
- 存在未解决的问题或错误
- 工作部分或不完整
- 遇到阻止完成的障碍
- 无法找到必要的资源或依赖
- 质量标准未达到

如果被阻止，保持任务为 `in_progress` 并创建一个新任务描述需要解决的问题。

## 最佳实践

- 创建具体、可操作的项目
- 将复杂任务分解为更小的、可管理的步骤
- 使用清晰、描述性的任务名称
- 在工作时实时更新任务状态
- 完成后立即标记任务完成（不要批量完成）
- 删除不再相关的任务
- **重要**：编写待办列表时，立即将第一个任务标记为 `in_progress`
- **重要**：除非所有任务都已完成，否则始终至少有一个任务为 `in_progress` 以显示进度

主动进行任务管理体现了全面性，并确保所有要求都能成功完成。

**记住**：如果只需要几次工具调用就能完成任务，而且很清楚该做什么，最好直接执行任务，根本不使用此工具。
"""

    return TodoListMiddleware(system_prompt=system_prompt, tool_description=tool_description)


def _build_middlewares(config: RunnableConfig):
    """根据运行时配置构建中间件链。

    中间件顺序说明：
    - ThreadDataMiddleware 必须在 SandboxMiddleware 之前，以确保 thread_id 可用
    - UploadsMiddleware 应在 ThreadDataMiddleware 之后以访问 thread_id
    - DanglingToolCallMiddleware 在模型看到历史记录之前修补缺失的 ToolMessages
    - SummarizationMiddleware 应该早执行，以在其他处理之前减少上下文
    - TodoListMiddleware 应在 ClarificationMiddleware 之前，以允许待办管理
    - TitleMiddleware 在首次交流后生成标题
    - MemoryMiddleware 将对话排队等待内存更新（在 TitleMiddleware 之后）
    - ViewImageMiddleware 应在 ClarificationMiddleware 之前，在 LLM 之前注入图像详情
    - ClarificationMiddleware 应该最后执行，以在模型调用后拦截澄清请求

    Args:
        config: 包含可配置选项（如 is_plan_mode）的运行时配置。

    Returns:
        中间件实例列表。
    """
    middlewares = [ThreadDataMiddleware(), UploadsMiddleware(), SandboxMiddleware(), DanglingToolCallMiddleware()]

    summarization_middleware = _create_summarization_middleware()
    if summarization_middleware is not None:
        middlewares.append(summarization_middleware)

    is_plan_mode = config.get("configurable", {}).get("is_plan_mode", False)
    todo_list_middleware = _create_todo_list_middleware(is_plan_mode)
    if todo_list_middleware is not None:
        middlewares.append(todo_list_middleware)

    middlewares.append(TitleMiddleware())

    middlewares.append(MemoryMiddleware())

    model_name = config.get("configurable", {}).get("model_name") or config.get("configurable", {}).get("model")
    from src.config import get_app_config

    app_config = get_app_config()
    if model_name is None and app_config.models:
        model_name = app_config.models[0].name

    model_config = app_config.get_model_config(model_name) if model_name else None
    if model_config is not None and model_config.supports_vision:
        middlewares.append(ViewImageMiddleware())

    subagent_enabled = config.get("configurable", {}).get("subagent_enabled", False)
    if subagent_enabled:
        max_concurrent_subagents = config.get("configurable", {}).get("max_concurrent_subagents", 3)
        middlewares.append(SubagentLimitMiddleware(max_concurrent=max_concurrent_subagents))

    middlewares.append(ClarificationMiddleware())
    return middlewares


def make_lead_agent(config: RunnableConfig):
    """创建主导代理实例。

    根据配置创建并配置主导代理，包括模型、工具、中间件和系统提示。

    Args:
        config: 运行时配置，包含模型名称、思考模式、计划模式等设置。

    Returns:
        配置好的代理实例。
    """
    from src.tools import get_available_tools

    thinking_enabled = config.get("configurable", {}).get("thinking_enabled", True)
    model_name = config.get("configurable", {}).get("model_name") or config.get("configurable", {}).get("model")
    is_plan_mode = config.get("configurable", {}).get("is_plan_mode", False)
    subagent_enabled = config.get("configurable", {}).get("subagent_enabled", False)
    max_concurrent_subagents = config.get("configurable", {}).get("max_concurrent_subagents", 3)
    print(f"thinking_enabled: {thinking_enabled}, model_name: {model_name}, is_plan_mode: {is_plan_mode}, subagent_enabled: {subagent_enabled}, max_concurrent_subagents: {max_concurrent_subagents}")

    if "metadata" not in config:
        config["metadata"] = {}
    config["metadata"].update(
        {
            "model_name": model_name or "default",
            "thinking_enabled": thinking_enabled,
            "is_plan_mode": is_plan_mode,
            "subagent_enabled": subagent_enabled,
        }
    )

    return create_agent(
        model=create_chat_model(name=model_name, thinking_enabled=thinking_enabled),
        tools=get_available_tools(model_name=model_name, subagent_enabled=subagent_enabled),
        middleware=_build_middlewares(config),
        system_prompt=apply_prompt_template(subagent_enabled=subagent_enabled, max_concurrent_subagents=max_concurrent_subagents),
        state_schema=ThreadState,
    )
