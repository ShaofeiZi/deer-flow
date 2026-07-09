<title>287｜auth/config、models、providers 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 auth/channel/frontend core 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| config.py | AuthConfig 和开关。 |
| models.py | UserResponse 等 API 模型。 |
| providers.py | 通用 AuthProvider 抽象，定义 authenticate/get_user。 |
| ../auth_disabled.py | Gateway 级禁用认证模式；文件在 `backend/app/gateway/`，不在 `auth/` 子包内。 |
| ../langgraph_auth.py | LangGraph compatibility auth handler；复用 Gateway JWT/CSRF 规则。 |

```mermaid
flowchart TD
  Config --> AuthConfig
  AuthConfig --> AuthRouter
  Models --> APIResponse
  Providers --> LocalProvider
  AuthDisabled --> Middleware
  LangGraphAuth --> LangGraphRoutes
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
flowchart TD
  Req["auth request"]
  Req --> AD{"is_auth_disabled"}
  AD -- yes --> AU["AUTH_DISABLED_USER_ID admin"]
  AD -- no --> CK{"access_token cookie"}
  CK -- absent --> E1["401 not_authenticated"]
  CK -- present --> DT["jwt.decode_token"]
  DT -- TokenError --> E2["401 token_expired or token_invalid"]
  DT -- TokenPayload --> GU["LocalAuthProvider.get_user"]
  GU -- None --> E3["401 user_not_found"]
  GU -- User --> TV{"token_version match"}
  TV -- no --> E4["401 token_invalid revoked"]
  TV -- yes --> OK["return User"]
  LG["langgraph_auth.authenticate"] -.reuses.-> DT
  LG -.reuses.-> GU
```