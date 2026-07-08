"""Password hashing utilities with versioned hash format.

Hash format: ``$dfv<N>$<bcrypt_hash>`` where ``<N>`` is the version.

- **v1** (legacy): ``bcrypt(password)`` — plain bcrypt, susceptible to
  72-byte silent truncation.
- **v2** (current): ``bcrypt(b64(sha256(password)))`` — SHA-256 pre-hash
  avoids the 72-byte truncation limit so the full password contributes
  to the hash.

Verification auto-detects the version and falls back to v1 for hashes
without a prefix, so existing deployments upgrade transparently on next
login.
| 带版本化哈希格式的密码哈希工具。

哈希格式：``$dfv<N>$<bcrypt_hash>``，其中 ``<N>`` 是版本号。

- **v1**（遗留）：``bcrypt(password)`` — 纯 bcrypt，容易受到 72 字节静默截断的影响。
- **v2**（当前）：``bcrypt(b64(sha256(password)))`` — SHA-256 预哈希避免了 72 字节截断限制，
  使完整密码参与哈希计算。

验证自动检测版本，对于没有前缀的哈希回退到 v1，因此现有部署在下一次登录时透明升级。
"""

import asyncio
import base64
import hashlib

import bcrypt

_CURRENT_VERSION = 2
_PREFIX_V2 = "$dfv2$"
_PREFIX_V1 = "$dfv1$"


def _pre_hash_v2(password: str) -> bytes:
    """SHA-256 pre-hash to bypass bcrypt's 72-byte limit. | SHA-256 预哈希以绕过 bcrypt 的 72 字节限制。"""
    return base64.b64encode(hashlib.sha256(password.encode("utf-8")).digest())


def hash_password(password: str) -> str:
    """Hash a password (current version: v2 — SHA-256 + bcrypt). | 哈希密码（当前版本：v2 — SHA-256 + bcrypt）。"""
    raw = bcrypt.hashpw(_pre_hash_v2(password), bcrypt.gensalt()).decode("utf-8")
    return f"{_PREFIX_V2}{raw}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password, auto-detecting the hash version.

    Accepts v2 (``$dfv2$…``), v1 (``$dfv1$…``), and bare bcrypt hashes
    (treated as v1 for backward compatibility with pre-versioning data).
    | 验证密码，自动检测哈希版本。

    接受 v2（``$dfv2$…``）、v1（``$dfv1$…``）和裸 bcrypt 哈希
    （为与版本化之前的数据向后兼容，视为 v1）。
    """
    try:
        if hashed_password.startswith(_PREFIX_V2):
            bcrypt_hash = hashed_password[len(_PREFIX_V2) :]
            return bcrypt.checkpw(_pre_hash_v2(plain_password), bcrypt_hash.encode("utf-8"))

        if hashed_password.startswith(_PREFIX_V1):
            bcrypt_hash = hashed_password[len(_PREFIX_V1) :]
        else:
            bcrypt_hash = hashed_password

        return bcrypt.checkpw(plain_password.encode("utf-8"), bcrypt_hash.encode("utf-8"))
    except ValueError:
        # bcrypt raises ValueError for malformed or corrupt hashes (e.g., invalid salt).
        # Fail closed rather than crashing the request.
        # | bcrypt 对格式错误或损坏的哈希（例如无效的 salt）抛出 ValueError。
        # 安全失败而不是使请求崩溃。
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Return True if the hash uses an older version and should be rehashed. | 如果哈希使用旧版本且应重新哈希，则返回 True。"""
    return not hashed_password.startswith(_PREFIX_V2)


async def hash_password_async(password: str) -> str:
    """Hash a password using bcrypt (non-blocking).

    Wraps the blocking bcrypt operation in a thread pool to avoid
    blocking the event loop during password hashing.
    | 使用 bcrypt 哈希密码（非阻塞）。

    将阻塞的 bcrypt 操作包装在线程池中，以避免在密码哈希期间阻塞事件循环。
    """
    return await asyncio.to_thread(hash_password, password)


async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash (non-blocking).

    Wraps the blocking bcrypt operation in a thread pool to avoid
    blocking the event loop during password verification.
    | 根据哈希验证密码（非阻塞）。

    将阻塞的 bcrypt 操作包装在线程池中，以避免在密码验证期间阻塞事件循环。
    """
    return await asyncio.to_thread(verify_password, plain_password, hashed_password)
