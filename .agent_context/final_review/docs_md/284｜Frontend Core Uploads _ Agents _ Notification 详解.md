<title>284｜Frontend Core Uploads / Agents / Notification 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 channels/auth/frontend core 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| core/uploads | upload/list/delete files、file validation。 |
| core/agents | agents API/hooks/types。 |
| core/notification | 浏览器通知 hook。 |
| prompt-input-files | PromptInput file 转 File。 |

```mermaid
flowchart TD
  InputBox --> PromptInputFiles
  PromptInputFiles --> UploadsAPI
  UploadsAPI --> GatewayUploads
  AgentsPage --> AgentsHooks
  AgentsHooks --> AgentsAPI
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
  A["prompt-input.tsx"] --> B["splitUnsupportedUploadFiles"]
  B --> C["accepted File list"]
  C --> D["threads/hooks submit"]
  D --> E["promptInputFilePartToFile"]
  E --> F["wrap browser File"]
  E --> G["fetch url to blob"]
  G --> H["new File from blob"]
  F --> I["uploadFiles"]
  H --> I
  I --> J["api/fetcher POST CSRF"]
  J --> K["/api/threads/id/uploads"]
  K --> L["UploadResponse files"]
  L --> M["virtual_path to optimistic msg"]
```