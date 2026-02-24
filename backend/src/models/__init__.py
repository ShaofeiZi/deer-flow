"""模型模块导出。"""

from .factory import create_chat_model
from .patched_deepseek import PatchedChatDeepSeek

__all__ = ["create_chat_model", "PatchedChatDeepSeek"]
