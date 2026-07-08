<title>287｜auth/config、models、providers 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 auth/channel/frontend core 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| config.py | AuthConfig 和开关。 |
| models.py | UserResponse 等 API 模型。 |
| providers.py | OAuth provider 抽象。 |
| auth_disabled.py | 禁用认证模式。 |
| langgraph_auth.py | LangGraph auth 集成。 |

```mermaid
flowchart TD
  Config --> AuthConfig
  AuthConfig --> AuthRouter
  Models --> APIResponse
  OAuth --> Providers
  Providers --> Callback
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
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth*` 或对应前端 `core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```