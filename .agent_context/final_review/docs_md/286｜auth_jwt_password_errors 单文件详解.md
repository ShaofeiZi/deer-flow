<title>286｜auth/jwt、password、errors 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 auth/channel/frontend core 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| jwt.py | access/session token 创建和校验。 |
| password.py | 密码 hash/verify。 |
| errors.py | AuthErrorCode 与标准错误响应。 |
| routers/auth.py | Gateway auth router；调用这些模块形成登录/注册/退出/改密等响应。 |

```mermaid
flowchart TD
  AuthRouter[routers/auth.py] --> LoginRequest
  LoginRequest --> PasswordVerify
  PasswordVerify --> JWTCreate
  JWTCreate --> Cookie
  ErrorCase --> AuthErrors
  AuthErrors --> ErrorResponse
  ChangePassword --> PasswordHash
  PasswordHash --> UserRepo
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是前后端契约清晰，接口可独立演进。 |
| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
sequenceDiagram
    participant C as Client
    participant R as routers/auth.py
    participant P as LocalAuthProvider
    participant V as password.verify_password_async
    participant J as jwt.create_access_token
    participant K as _set_session_cookie
    participant E as errors.AuthErrorCode
    C->>R: POST login/local
    R->>R: check_rate_limit client_ip
    R->>P: authenticate email password
    P->>V: plain vs password_hash
    alt verify fails
        P-->>R: None
        R->>E: INVALID_CREDENTIALS
        R-->>C: 401 AuthErrorResponse
    else verify ok
        P-->>R: User
        R->>J: user_id token_version
        J-->>R: JWT string
        R->>K: set HttpOnly access_token
        R-->>C: LoginResponse expires_in needs_setup
    end
```