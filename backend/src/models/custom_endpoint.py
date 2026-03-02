"""自定义端点的 ChatOpenAI 包装器。

此模块提供 ChatOpenAI 的自定义版本，支持将请求转发到非标准 API 端点。
主要用于支持需要特殊请求格式的 API（如字节跳动内部 API）。
"""

import json
import logging
from typing import Any

import httpx
from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


class CustomEndpointChatOpenAI(ChatOpenAI):
    """支持自定义端点的 ChatOpenAI。

    此类继承自 ChatOpenAI，重写了请求逻辑以支持自定义 API 端点。
    当配置了 custom_endpoint 时，请求将被转发到该端点而不是标准的 OpenAI API。

    Attributes:
        custom_endpoint: 自定义 API 端点的完整 URL。
    """

    custom_endpoint: str | None = None

    def _build_custom_request_body(
        self,
        messages: list[dict],
        **kwargs: Any,
    ) -> dict:
        """构建自定义端点的请求体。

        将标准 OpenAI 格式的消息转换为自定义端点所需的格式。

        Args:
            messages: OpenAI 格式的消息列表。
            **kwargs: 额外的请求参数。

        Returns:
            自定义端点所需的请求体字典。
        """
        body = {
            "stream": False,
            "messages": messages,
            "temperature": self.temperature if self.temperature is not None else 1.0,
            "model": self.model_name,
            "max_tokens": self.max_tokens if self.max_tokens else 1000,
        }

        if kwargs.get("stop"):
            body["stop"] = kwargs["stop"]

        return body

    def _parse_custom_response(self, response_data: dict) -> dict:
        """解析自定义端点的响应。

        将自定义端点的响应转换为 OpenAI 格式。

        Args:
            response_data: 自定义端点返回的响应数据。

        Returns:
            OpenAI 格式的响应字典。
        """
        if "choices" in response_data:
            return response_data

        if "message" in response_data:
            return {
                "id": "custom-response",
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "message": response_data["message"],
                        "finish_reason": "stop",
                    }
                ],
                "usage": response_data.get("usage", {}),
            }

        if "content" in response_data:
            return {
                "id": "custom-response",
                "object": "chat.completion",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": response_data["content"],
                        },
                        "finish_reason": "stop",
                    }
                ],
                "usage": response_data.get("usage", {}),
            }

        return {
            "id": "custom-response",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": json.dumps(response_data, ensure_ascii=False),
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {},
        }

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> Any:
        """重写生成方法以支持自定义端点。

        当配置了 custom_endpoint 时，使用自定义端点发送请求；
        否则使用父类的默认行为。

        Args:
            messages: 消息列表。
            stop: 停止词列表。
            run_manager: 运行管理器。
            **kwargs: 额外参数。

        Returns:
            LLM 结果。
        """
        if not self.custom_endpoint:
            return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)

        message_dicts = [self._convert_message_to_dict(m) for m in messages]
        request_body = self._build_custom_request_body(message_dicts, stop=stop, **kwargs)

        logger.debug(f"Sending request to custom endpoint: {self.custom_endpoint}")
        logger.debug(f"Request body: {json.dumps(request_body, ensure_ascii=False)[:500]}")

        with httpx.Client(timeout=self.request_timeout or 120.0) as client:
            response = client.post(
                self.custom_endpoint,
                headers={"Content-Type": "application/json"},
                json=request_body,
            )
            response.raise_for_status()
            response_data = response.json()

        logger.debug(f"Response: {json.dumps(response_data, ensure_ascii=False)[:500]}")

        parsed_response = self._parse_custom_response(response_data)

        return self._create_chat_result(parsed_response)

    async def _agenerate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> Any:
        """重写异步生成方法以支持自定义端点。

        当配置了 custom_endpoint 时，使用自定义端点发送请求；
        否则使用父类的默认行为。

        Args:
            messages: 消息列表。
            stop: 停止词列表。
            run_manager: 运行管理器。
            **kwargs: 额外参数。

        Returns:
            LLM 结果。
        """
        if not self.custom_endpoint:
            return await super()._agenerate(messages, stop=stop, run_manager=run_manager, **kwargs)

        message_dicts = [self._convert_message_to_dict(m) for m in messages]
        request_body = self._build_custom_request_body(message_dicts, stop=stop, **kwargs)

        logger.debug(f"Sending async request to custom endpoint: {self.custom_endpoint}")

        async with httpx.AsyncClient(timeout=self.request_timeout or 120.0) as client:
            response = await client.post(
                self.custom_endpoint,
                headers={"Content-Type": "application/json"},
                json=request_body,
            )
            response.raise_for_status()
            response_data = response.json()

        parsed_response = self._parse_custom_response(response_data)

        return self._create_chat_result(parsed_response)

    def _convert_message_to_dict(self, message: BaseMessage) -> dict:
        """将 BaseMessage 转换为字典格式。

        Args:
            message: LangChain 消息对象。

        Returns:
            消息字典。
        """
        if hasattr(message, "content"):
            content = message.content
            if isinstance(content, str):
                return {"role": message.type, "content": content}
            elif isinstance(content, list):
                return {"role": message.type, "content": content}

        return {"role": getattr(message, "type", "user"), "content": str(message)}
