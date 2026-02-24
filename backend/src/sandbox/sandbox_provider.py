from abc import ABC, abstractmethod

from typing import cast, Type, Any

from src.config import get_app_config
from src.reflection import resolve_class
from src.sandbox.sandbox import Sandbox


class SandboxProvider(ABC):
    """SandboxProvider 的抽象基类。"""

    @abstractmethod
    def acquire(self, thread_id: str | None = None) -> str:
        """获取一个 sandbox 环境并返回其 ID。

        参数:
            thread_id: 线程标识符，用于分配线程相关的 sandbox（如果需要）。

        返回:
            获取到的 sandbox 环境的 ID。
        """
        pass

    @abstractmethod
    def get(self, sandbox_id: str) -> Sandbox | None:
        """按 ID 获取 sandbox 环境。

        参数:
            sandbox_id: 要检索的 sandbox 环境的 ID。
        """
        pass

    @abstractmethod
    def release(self, sandbox_id: str) -> None:
        """释放 sandbox 环境。

        参数:
            sandbox_id: 要销毁的 sandbox 环境的 ID。
        """
        pass


_default_sandbox_provider: SandboxProvider | None = None


def get_sandbox_provider(**kwargs) -> SandboxProvider:
    """获取 sandbox provider 的单例实例。

    返回缓存的单例实例。若要清空缓存，请使用 `reset_sandbox_provider()`，若要正确关闭并清理，请使用 `shutdown_sandbox_provider()`。

    返回:
        一个 sandbox provider 实例。
    """
    global _default_sandbox_provider
    if _default_sandbox_provider is None:
        config = get_app_config()
        # Type: ignore abstract issue in static analyzers by casting to the concrete type
        cls = cast(Type[SandboxProvider], resolve_class(config.sandbox.use, SandboxProvider))
        _default_sandbox_provider = cls(**kwargs)  # type: ignore[abstract-class-instantiation, call-arg]
    return _default_sandbox_provider


def reset_sandbox_provider() -> None:
    """重置 sandbox provider 的单例。

    该操作会清空缓存的实例，但不会调用 shutdown。下一次调用 `get_sandbox_provider()` 时将创建一个新实例。
    这在测试或切换配置时非常有用。

    注意：如果提供者仍有活动的 sandbox，它们可能会成为孤儿对象，需要通过 `shutdown_sandbox_provider()` 进行清理。
    """
    global _default_sandbox_provider
    _default_sandbox_provider = None


def shutdown_sandbox_provider() -> None:
    """关闭并重置 sandbox provider。

    在清除单例此前，正确关闭提供者（释放所有 sandbox）。在应用程序退出时或需要完全重置 sandbox 系统时调用。
    """
    global _default_sandbox_provider
    if _default_sandbox_provider is not None:
        provider_any: Any = _default_sandbox_provider  # type: ignore[assignment]
        shutdown_func = getattr(provider_any, "shutdown", None)
        if callable(shutdown_func):
            shutdown_func()
        _default_sandbox_provider = None


def set_sandbox_provider(provider: SandboxProvider) -> None:
    """设置自定义 sandbox provider 实例。

    这允许在测试中注入自定义或模拟的 provider。

    参数:
        provider: 要使用的 SandboxProvider 实例。
    """
    global _default_sandbox_provider
    _default_sandbox_provider = provider
