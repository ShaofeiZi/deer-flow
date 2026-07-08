<title>292｜Frontend Agents、Uploads、Notification Core 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 auth/channel/frontend core 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| core/agents/api.ts | agents REST API。 |
| core/agents/hooks.ts | React Query hooks。 |
| core/uploads/api.ts | upload/list/delete files。 |
| core/uploads/file-validation.ts | 文件校验。 |
| core/notification/hooks.ts | 浏览器通知。 |

```mermaid
flowchart TD
  AgentUI --> AgentsHooks
  AgentsHooks --> AgentsAPI
  FileInput --> FileValidation
  FileValidation --> UploadsAPI
  UploadsAPI --> GatewayUploads
  RunFinish --> NotificationHook
  NotificationHook --> BrowserNotification
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
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```