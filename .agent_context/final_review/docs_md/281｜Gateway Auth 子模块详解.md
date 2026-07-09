<title>281｜Gateway Auth 子模块详解</title>

<callout emoji="✅">
**本章目标：**继续拆 channels/auth/frontend core 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| auth/config.py | auth 配置。 |
| auth/models.py | UserResponse 等模型。 |
| auth/jwt.py | JWT/session token。 |
| auth/password.py | 密码 hash。 |
| auth/errors.py | 错误码。 |
| auth/providers.py | OAuth provider 抽象。 |

```mermaid
flowchart TD
  AuthRouter --> AuthConfig
  AuthRouter --> UserModels
  AuthRouter --> JWT
  AuthRouter --> Password
  AuthRouter --> Errors
  OAuth --> Providers
  Password --> LocalProvider
  JWT --> Cookie
  Errors --> APIResponse
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
    participant Client
    participant Router as "routers/auth.py"
    participant Provider as "LocalAuthProvider"
    participant Repo as "UserRepository"
    participant PW as "password.py"
    participant JWT as "jwt.py"
    participant MW as "AuthMiddleware"
    Participant Deps as "get_current_user"

    Client->>Router: POST login/local
    Router->>Router: check_rate_limit client_ip
    Router->>Provider: authenticate email password
    Provider->>Repo: get_user_by_email
    Repo-->>Provider: User or None
    Provider->>PW: verify_password_async
    PW-->>Provider: ok or fail
    alt valid credentials
      Provider->>PW: needs_rehash upgrade
      Provider-->>Router: User
      Router->>JWT: create_access_token user_id token_version
      JWT-->>Router: signed HS256 token
      Router-->>Client: HttpOnly cookie LoginResponse
    else invalid
      Router->>Router: record_login_failure ip
      Router-->>Client: 401 invalid_credentials
    end

    Note over Client,MW: later protected request
    Client->>MW: GET /api/threads with cookie
    MW->>Deps: get_current_user_from_request
    Deps->>JWT: decode_token
    JWT-->>Deps: TokenPayload or TokenError
    alt TokenError
      Deps-->>MW: 401 token_expired or token_invalid
    else valid payload
      Deps->>Provider: get_user payload.sub
      Provider->>Repo: get_user_by_id
      Repo-->>Provider: User
      Provider-->>Deps: User
      Deps->>Deps: check token_version match
      alt version mismatch
        Deps-->>MW: 401 token_invalid revoked
      else match
        Deps-->>MW: User
        MW->>MW: stamp request.state.user contextvar
        MW-->>Client: route response
      end
    end
```