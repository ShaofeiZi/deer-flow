<title>214｜backend/docs/AUTH_DESIGN / AUTH_UPGRADE 详解</title>

<callout emoji="✅">
**本章目标：**继续把 backend/docs 中重要说明拆成独立讲解文档。
</callout>

| 文档点 | 说明 |
|-|-|
| AUTH_DESIGN | 认证模型和用户体系。 |
| AUTH_UPGRADE | 从无 auth 到有 auth 的升级路径。 |
| AUTH_TEST_PLAN | 测试计划。 |
| AUTH_TEST_DOCKER_GAP | Docker 测试差距。 |

```mermaid
flowchart TD
  AuthDocs --> Design[AUTH DESIGN]
  AuthDocs --> Upgrade[AUTH UPGRADE]
  AuthDocs --> Tests[AUTH TEST PLAN]
  Design --> AuthMiddleware
  Design --> UserModel
  Upgrade --> OrphanMigration[orphan threads migration]
  Tests --> AuthTests
  DockerGap --> FutureWork
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
sequenceDiagram
    participant C as Client
    participant R as routers/auth.py
    participant JWT as auth/jwt.py
    participant MW as auth_middleware.py
    participant D as deps.get_current_user_from_request
    participant P as LocalAuthProvider
    participant Repo as SQLiteUserRepository
    participant UC as user_context ContextVar

    C->>R: POST /api/v1/auth/login/local
    R->>P: authenticate email/password
    P->>Repo: get_user_by_email
    Repo-->>P: User record
    P->>P: verify_password_async
    P-->>R: User
    R->>JWT: create_access_token user_id token_version
    JWT-->>R: JWT string
    R-->>C: 200 + access_token HttpOnly cookie

    C->>MW: GET /api/v1/threads (cookie)
    MW->>MW: _is_public path? no
    MW->>D: resolve access_token cookie
    D->>JWT: decode_token
    JWT-->>D: TokenPayload or TokenError
    D->>P: get_user payload.sub
    P->>Repo: get_user_by_id
    Repo-->>P: User
    P-->>D: User
    D->>D: check token_version == User.token_version
    D-->>MW: User
    MW->>UC: set_current_user User
    MW->>MW: request.state.user = User
    MW-->>C: route response
```