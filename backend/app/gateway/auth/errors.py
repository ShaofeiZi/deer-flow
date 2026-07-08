"""Typed error definitions for auth module.

AuthErrorCode: exhaustive enum of all auth failure conditions.
TokenError: exhaustive enum of JWT decode failures.
AuthErrorResponse: structured error payload for HTTP responses.
| 认证模块的类型化错误定义。

AuthErrorCode: 所有认证失败条件的穷举枚举。
TokenError: JWT 解码失败的穷举枚举。
AuthErrorResponse: HTTP 响应的结构化错误负载。
"""

from enum import StrEnum

from pydantic import BaseModel


class AuthErrorCode(StrEnum):
    """Exhaustive list of auth error conditions. | 认证错误条件的穷举列表。"""

    INVALID_CREDENTIALS = "invalid_credentials"
    TOKEN_EXPIRED = "token_expired"
    TOKEN_INVALID = "token_invalid"
    USER_NOT_FOUND = "user_not_found"
    EMAIL_ALREADY_EXISTS = "email_already_exists"
    PROVIDER_NOT_FOUND = "provider_not_found"
    NOT_AUTHENTICATED = "not_authenticated"
    SYSTEM_ALREADY_INITIALIZED = "system_already_initialized"


class TokenError(StrEnum):
    """Exhaustive list of JWT decode failure reasons. | JWT 解码失败原因的穷举列表。"""

    EXPIRED = "expired"
    INVALID_SIGNATURE = "invalid_signature"
    MALFORMED = "malformed"


class AuthErrorResponse(BaseModel):
    """Structured error response — replaces bare `detail` strings. | 结构化错误响应 — 替代裸 `detail` 字符串。"""

    code: AuthErrorCode
    message: str


def token_error_to_code(err: TokenError) -> AuthErrorCode:
    """Map TokenError to AuthErrorCode — single source of truth. | 将 TokenError 映射到 AuthErrorCode — 单一真相来源。"""
    if err == TokenError.EXPIRED:
        return AuthErrorCode.TOKEN_EXPIRED
    return AuthErrorCode.TOKEN_INVALID
