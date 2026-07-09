<title>181｜Auth / Owner Isolation Tests 详解</title>

<callout emoji="✅">
**本章目标：**继续拆测试/workflow/script 单文件族，说明覆盖目标和运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| test_auth\*.py | 认证配置、错误、middleware、类型系统。 |
| test_owner_isolation.py | owner 隔离。 |
| test_stateless_runs_owner_isolation.py | stateless runs owner 隔离。 |
| \_router_auth_helpers.py | router auth 测试辅助。 |

```mermaid
flowchart TD
  AuthCode --> AuthTests
  OwnerCode --> OwnerTests
  AuthTests --> TestClient
  OwnerTests --> TestClient
  TestClient --> Request[authenticated requests]
  Request --> Assertions[401 403 owner checks]
  Assertions --> CI
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这组测试验证认证身份如何进入 Gateway 请求，并在 threads/runs/uploads/artifacts/memory/feedback 等资源访问时保持 owner isolation。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 401/403/404、CSRF、admin 初始化、无 auth 兼容和跨用户隔离都有明确回归点。 |
| 代价 | 一次鉴权问题可能跨 middleware、permission decorator、repository owner filter、ContextVar 和测试 helper。 |
| 重点代码 | `backend/app/gateway/auth_middleware.py`、`backend/app/gateway/authz.py`、`backend/app/gateway/auth/`、`backend/tests/_router_auth_helpers.py`、`backend/tests/test_owner_isolation.py`、`backend/tests/test_stateless_runs_owner_isolation.py`。 |
| 阅读路径 | 先看请求如何得到 current user，再看 owner_check 如何查资源归属，最后用测试确认未授权、跨用户和 auth-disabled 分支。 |

```mermaid
sequenceDiagram
    participant Client as TestClient
    participant MW as AuthMiddleware
    participant Deps as deps get_current_user
    participant Route as require_permission decorator
    participant TS as thread_store check_access
    participant Svc as services.start_run
    participant Repo as Repository owner filter
    autonumber
    Client->>MW: request to non-public path
    alt public path
        MW-->>Client: pass-through 200
    else no cookie or invalid JWT
        MW-->>Client: 401 NOT_AUTHENTICATED or TOKEN_INVALID
    else valid cookie
        MW->>Deps: resolve JWT to User
        Deps-->>MW: User
        MW->>MW: stamp request.state.user and AuthContext
        MW->>MW: set_current_user contextvar token
    end
    alt path-param route threads
        Client->>Route: GET/PATCH/DELETE thread_id
        Route->>TS: check_access thread_id user_id
        alt different owner
            TS-->>Route: False
            Route-->>Client: 404 Thread not found
        else owner or shared or missing row
            TS-->>Route: True
            Route->>Repo: handler runs with contextvar
            Repo-->>Client: 200 own rows only
        end
    else stateless runs body thread_id
        Client->>Svc: POST runs/stream or runs/wait
        Svc->>TS: check_access thread_id user_id
        alt foreign owner
            TS-->>Svc: False
            Svc-->>Client: 404 Thread not found
        else owner or untracked or internal role
            TS-->>Svc: True
            Svc->>Svc: run_manager create_or_reject
            Svc-->>Client: 409 sentinel
        end
    end
    Note over MW: finally reset_current_user token
```