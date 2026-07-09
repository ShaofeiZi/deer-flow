<title>298｜Frontend Core API Feedback / StreamMode 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 frontend core 数据层单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| api/feedback.ts | run feedback API。 |
| api/stream-mode.ts | stream mode 清洗。 |
| api/index.ts | 统一导出。 |
| api/fetcher.ts | REST fetch 基础。 |

```mermaid
flowchart TD
  FeedbackUI --> FeedbackAPI
  FeedbackAPI --> Fetcher
  StreamOptions --> StreamModeSanitize
  StreamModeSanitize --> LangGraphSDK
  Fetcher --> CSRF
  CSRF --> GatewayAPI
  GatewayAPI --> FeedbackResponse
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |
| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |
| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |

```mermaid
flowchart TD
  SDKPath["api-client getAPIClient"]
  RESTPath["feedback upsertFeedback deleteFeedback"]
  SDKPath --> PatchStream["patch runs.stream"]
  SDKPath --> PatchJoin["patch runs.joinStream"]
  PatchStream --> Sanitize["sanitizeRunStreamOptions"]
  PatchJoin --> Sanitize
  PatchJoin --> Inactive["isInactiveRunStreamError clearReconnectRun"]
  Sanitize --> LangGraph["LangGraphClient originalRunStream"]
  LangGraph --> OnReq["onRequest injectCsrfHeader"]
  RESTPath --> Fetcher["fetcher.fetch credentials include"]
  Fetcher --> Fetch401["401 buildLoginUrl redirect"]
  OnReq --> Shared["isStateChangingMethod readCsrfCookie"]
  Fetcher --> Shared
  Shared --> Header["X-CSRF-Token header"]
  Header --> Gateway["Gateway CSRFMiddleware"]
```