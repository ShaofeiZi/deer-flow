"""模型模块导出。"""

from .factory import create_chat_model

try:
    from .custom_endpoint import CustomEndpointChatOpenAI
    from .patched_deepseek import PatchedChatDeepSeek

    __all__ = ["create_chat_model", "PatchedChatDeepSeek", "CustomEndpointChatOpenAI"]
except ImportError:
    __all__ = ["create_chat_model"]
