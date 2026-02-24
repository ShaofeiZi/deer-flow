from typing import Literal

from langchain.tools import tool


@tool("ask_clarification", parse_docstring=True, return_direct=True)
def ask_clarification_tool(
    question: str,
    clarification_type: Literal[
        "missing_info",
        "ambiguous_requirement",
        "approach_choice",
        "risk_confirmation",
        "suggestion",
    ],
    context: str | None = None,
    options: list[str] | None = None,
) -> str:
    """当需要更多信息才能继续时，向用户请求澄清。

    在以下情况下使用此工具：

    - **信息缺失**：未提供所需的详细信息（如文件路径、URL、具体要求）
    - **需求模糊**：存在多种有效解释
    - **方法选择**：存在多种有效方法，需要用户偏好
    - **风险操作**：需要明确确认的破坏性操作（如删除文件、修改生产环境）
    - **建议**：你有建议但希望在继续之前获得用户批准

    执行将被中断，问题将呈现给用户。
    在继续之前等待用户的响应。

    何时使用 ask_clarification：
    - 你需要用户请求中未提供的信息
    - 需求可以有多种解释方式
    - 存在多种有效的实现方法
    - 你即将执行潜在危险的操作
    - 你有建议但需要用户批准

    最佳实践：
    - 一次只问一个澄清问题以确保清晰
    - 问题要具体明确
    - 需要澄清时不要做假设
    - 对于风险操作，始终请求确认
    - 调用此工具后，执行将自动中断

    Args:
        question: 向用户提出的澄清问题。要具体明确。
        clarification_type: 需要的澄清类型（missing_info、ambiguous_requirement、approach_choice、risk_confirmation、suggestion）。
        context: 可选的上下文，解释为什么需要澄清。帮助用户理解情况。
        options: 可选的选项列表（用于 approach_choice 或 suggestion 类型）。为用户呈现清晰的选项供选择。
    """
    # 这是一个占位实现
    # 实际逻辑由 ClarificationMiddleware 处理，它会拦截此工具调用
    # 并中断执行以向用户呈现问题
    return "澄清请求已由中间件处理"
