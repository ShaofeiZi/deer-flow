"""Auth provider abstraction. | 认证提供者抽象。"""

from abc import ABC, abstractmethod


class AuthProvider(ABC):
    """Abstract base class for authentication providers. | 认证提供者的抽象基类。"""

    @abstractmethod
    async def authenticate(self, credentials: dict) -> "User | None":
        """Authenticate user with given credentials.

        Returns User if authentication succeeds, None otherwise.
        | 使用给定的凭据认证用户。

        如果认证成功则返回 User，否则返回 None。
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, user_id: str) -> "User | None":
        """Retrieve user by ID. | 通过 ID 检索用户。"""
        raise NotImplementedError


# Import User at runtime to avoid circular imports
# | 在运行时导入 User 以避免循环导入
from app.gateway.auth.models import User  # noqa: E402
