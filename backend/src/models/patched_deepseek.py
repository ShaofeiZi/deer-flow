"""修复版的 ChatDeepSeek，在多轮对话中保留 reasoning_content。

此模块提供 ChatDeepSeek 的修复版本，正确处理发送回 API 时的
reasoning_content。原始实现将 reasoning_content 存储在 additional_kwargs 中，
但在进行后续 API 调用时不包含它，这会导致启用思考模式时要求所有助手消息
都包含 reasoning_content 的 API 出现错误。
"""

from typing import Any

from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import AIMessage
from langchain_deepseek import ChatDeepSeek


class PatchedChatDeepSeek(ChatDeepSeek):
    """正确保留 reasoning_content 的 ChatDeepSeek。

    使用思考/推理启用的模型时，API 期望多轮对话中的所有助手消息
    都包含 reasoning_content。此修复版本确保 additional_kwargs 中的
    reasoning_content 被包含在请求负载中。
    """

    def _get_request_payload(
        self,
        input_: LanguageModelInput,
        *,
        stop: list[str] | None = None,
        **kwargs: Any,
    ) -> dict:
        """获取保留 reasoning_content 的请求负载。

        重写父类方法，将 additional_kwargs 中的 reasoning_content
        注入到负载中的助手消息中。
        """
        # 在转换之前获取原始消息
        original_messages = self._convert_input(input_).to_messages()

        # 调用父类获取基础负载
        payload = super()._get_request_payload(input_, stop=stop, **kwargs)

        # 将负载消息与原始消息匹配以恢复 reasoning_content
        payload_messages = payload.get("messages", [])

        # 负载消息和原始消息应该按相同顺序排列
        # 遍历两者并按位置匹配
        if len(payload_messages) == len(original_messages):
            for payload_msg, orig_msg in zip(payload_messages, original_messages):
                if payload_msg.get("role") == "assistant" and isinstance(orig_msg, AIMessage):
                    reasoning_content = orig_msg.additional_kwargs.get("reasoning_content")
                    if reasoning_content is not None:
                        payload_msg["reasoning_content"] = reasoning_content
        else:
            # 回退：通过计数助手消息来匹配
            ai_messages = [m for m in original_messages if isinstance(m, AIMessage)]
            assistant_payloads = [(i, m) for i, m in enumerate(payload_messages) if m.get("role") == "assistant"]

            for (idx, payload_msg), ai_msg in zip(assistant_payloads, ai_messages):
                reasoning_content = ai_msg.additional_kwargs.get("reasoning_content")
                if reasoning_content is not None:
                    payload_messages[idx]["reasoning_content"] = reasoning_content

        return payload
