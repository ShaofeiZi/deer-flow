<title>282｜Gateway LocalAuthProvider / SQLiteUserRepository 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 channels/auth/frontend core 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| local_provider.py | 本地认证 provider。 |
| repositories/sqlite.py | SQLite user repo。 |
| repositories/base.py | repo 抽象。 |
| credential_file.py | 凭证文件。 |
| reset_admin.py | 重置 admin。 |

```mermaid
flowchart TD
  AuthRouter --> LocalProvider
  LocalProvider --> UserRepository
  UserRepository --> SQLiteRepo
  SQLiteRepo --> UserRow
  CredentialFile --> LocalProvider
  ResetAdmin --> UserRepository
  UserRepository --> AuthResult
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
    participant Router as login_local
    participant Deps as get_local_provider
    participant Provider as LocalAuthProvider
    participant Repo as SQLiteUserRepository
    participant DB as UserRow users table
    participant Pw as password module

    Client->>Router: POST /login/local
    Router->>Deps: get_local_provider
    Deps-->>Router: cached LocalAuthProvider
    Router->>Provider: authenticate email password
    Provider->>Repo: get_user_by_email
    Repo->>DB: SELECT by email
    DB-->>Repo: UserRow
    Repo-->>Provider: User or None
    alt no user or OAuth only
        Provider-->>Router: None
        Router-->>Client: 401 invalid credentials
    else password matches
        Provider->>Pw: verify_password_async
        Pw-->>Provider: verified
        opt needs_rehash v1 hash
            Provider->>Pw: hash_password_async
            Provider->>Repo: update_user rehash
            Repo->>DB: UPDATE password_hash
        end
        Provider-->>Router: User
        Router->>Router: create_access_token token_version
        Router->>Router: set access_token cookie
        Router-->>Client: LoginResponse needs_setup
    end
```