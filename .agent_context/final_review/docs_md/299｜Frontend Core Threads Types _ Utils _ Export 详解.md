<title>299｜Frontend Core Threads Types / Utils / Export 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 frontend core 数据层单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| threads/types.ts | AgentThreadState/Run/TokenUsage 类型。 |
| threads/utils.ts | thread title/path/text 辅助。 |
| threads/export.ts | 会话导出。 |
| threads/token-usage.ts | 后端 token usage 到 UI token usage 转换。 |
| threads/api.ts | thread token usage REST API。 |

```mermaid
flowchart TD
  BackendState --> ThreadTypes
  ThreadTypes --> UI
  Thread --> ThreadUtils
  ThreadUtils --> SidebarPathTitle
  ThreadMessages --> ExportThread
  TokenUsageAPI --> TokenUsageTransform
  TokenUsageTransform --> TokenUsageIndicator
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
flowchart LR
  subgraph exportTs["threads/export.ts"]
    MD["exportThreadAsMarkdown"]
    JSON["exportThreadAsJSON"]
    VIS["visibleMessages"]
    FMC["formatMessageContent"]
    SIM["stripInternalMarkers"]
    DL["downloadAsFile"]
  end
  subgraph utilsTs["threads/utils.ts"]
    TITLE["titleOfThread"]
    SAN["sanitizeFilename"]
  end
  subgraph msgUtils["messages/utils.ts"]
    HIDE["isHiddenFromUIMessage"]
  end
  MD --> VIS
  JSON --> VIS
  VIS --> HIDE
  VIS --> FMC
  FMC --> SIM
  MD --> TITLE
  TITLE --> SAN
  SAN --> DL
  FMC --> DL
  DL --> OUT["Blob + anchor download"]
```