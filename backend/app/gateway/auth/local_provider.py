"""Local email/password authentication provider. | 本地邮箱/密码认证提供者。"""

import logging

from app.gateway.auth.models import User
from app.gateway.auth.password import hash_password_async, needs_rehash, verify_password_async
from app.gateway.auth.providers import AuthProvider
from app.gateway.auth.repositories.base import UserRepository

logger = logging.getLogger(__name__)


class LocalAuthProvider(AuthProvider):
    """Email/password authentication provider using local database. | 使用本地数据库的邮箱/密码认证提供者。"""

    def __init__(self, repository: UserRepository):
        """Initialize with a UserRepository.

        Args:
            repository: UserRepository implementation (SQLite)
        | 使用 UserRepository 初始化。

        Args:
            repository: UserRepository 实现（SQLite）
        """
        self._repo = repository

    async def authenticate(self, credentials: dict) -> User | None:
        """Authenticate with email and password.

        Args:
            credentials: dict with 'email' and 'password' keys

        Returns:
            User if authentication succeeds, None otherwise
        | 使用邮箱和密码进行认证。

        Args:
            credentials: 包含 'email' 和 'password' 键的字典

        Returns:
            如果认证成功则返回 User，否则返回 None
        """
        email = credentials.get("email")
        password = credentials.get("password")

        if not email or not password:
            return None

        user = await self._repo.get_user_by_email(email)
        if user is None:
            return None

        if user.password_hash is None:
            # OAuth user without local password | 没有本地密码的 OAuth 用户
            return None

        if not await verify_password_async(password, user.password_hash):
            return None

        if needs_rehash(user.password_hash):
            try:
                user.password_hash = await hash_password_async(password)
                await self._repo.update_user(user)
            except Exception:
                # Rehash is an opportunistic upgrade; a transient DB error must not
                # prevent an otherwise-valid login from succeeding.
                # | Rehash 是机会性升级；临时数据库错误不应阻止原本有效的登录成功。
                logger.warning("Failed to rehash password for user %s; login will still succeed", user.email, exc_info=True)

        return user

    async def get_user(self, user_id: str) -> User | None:
        """Get user by ID. | 通过 ID 获取用户。"""
        return await self._repo.get_user_by_id(user_id)

    async def create_user(self, email: str, password: str | None = None, system_role: str = "user", needs_setup: bool = False) -> User:
        """Create a new local user.

        Args:
            email: User email address
            password: Plain text password (will be hashed)
            system_role: Role to assign ("admin" or "user")
            needs_setup: If True, user must complete setup on first login

        Returns:
            Created User instance
        | 创建新的本地用户。

        Args:
            email: 用户邮箱地址
            password: 明文密码（将被哈希）
            system_role: 要分配的角色（"admin" 或 "user"）
            needs_setup: 如果为 True，用户必须在首次登录时完成设置

        Returns:
            创建的 User 实例
        """
        password_hash = await hash_password_async(password) if password else None
        user = User(
            email=email,
            password_hash=password_hash,
            system_role=system_role,
            needs_setup=needs_setup,
        )
        return await self._repo.create_user(user)

    async def get_user_by_oauth(self, provider: str, oauth_id: str) -> User | None:
        """Get user by OAuth provider and ID. | 通过 OAuth 提供者和 ID 获取用户。"""
        return await self._repo.get_user_by_oauth(provider, oauth_id)

    async def count_users(self) -> int:
        """Return total number of registered users. | 返回已注册用户的总数。"""
        return await self._repo.count_users()

    async def count_admin_users(self) -> int:
        """Return number of admin users. | 返回管理员用户的数量。"""
        return await self._repo.count_admin_users()

    async def update_user(self, user: User) -> User:
        """Update an existing user. | 更新现有用户。"""
        return await self._repo.update_user(user)

    async def get_user_by_email(self, email: str) -> User | None:
        """Get user by email. | 通过邮箱获取用户。"""
        return await self._repo.get_user_by_email(email)
