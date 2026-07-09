<title>178｜Frontend E2E Chat/Sidebar/Artifacts Specs 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 CI、脚本、E2E 具体模块，说明触发、执行与产出。
</callout>

| 模块点 | 说明 |
|-|-|
| chat.spec.ts | 基础聊天 UI。 |
| agent-chat.spec.ts | agent chat 流程。 |
| sidebar.spec.ts | 侧边栏。 |
| artifact-preview.spec.ts | artifact 预览。 |
| chat-thread-init-ordering.spec.ts | 新 thread 初始化顺序。 |

```mermaid
flowchart TD
  Playwright --> Chat[chat spec]
  Playwright --> AgentChat[agent chat]
  Playwright --> Sidebar[sidebar]
  Playwright --> Artifact[artifact preview]
  Playwright --> Init[thread init ordering]
  MockAPI --> Chat
  MockAPI --> Sidebar
  MockAPI --> Artifact
  Specs --> Assertions[UI assertions]
  Assertions --> CI
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
  ChatSpec["chat.spec.ts"]
  AgentSpec["agent-chat.spec.ts"]
  SideSpec["sidebar.spec.ts"]
  ArtSpec["artifact-preview.spec.ts"]
  InitSpec["chat-thread-init-ordering.spec.ts"]
  ChatRoute["/workspace/chats/new"]
  AgentRoute["/workspace/agents"]
  AgentChatRoute["/workspace/agents/test-agent/chats/new"]
  ThreadRoute["/workspace/chats/threadId"]
  MockAPI["mockLangGraphAPI in utils/mock-api.ts"]
  EP1["/api/langgraph/threads"]
  EP2["/api/langgraph/threads/*/runs/stream"]
  Assert["Playwright expect toHaveURL and toBeVisible"]
  CI["CI e2e job"]

  ChatSpec --> ChatRoute
  AgentSpec --> AgentRoute
  AgentSpec --> AgentChatRoute
  SideSpec --> ChatRoute
  ArtSpec --> ThreadRoute
  InitSpec --> ChatRoute
  ChatRoute --> MockAPI
  AgentRoute --> MockAPI
  AgentChatRoute --> MockAPI
  ThreadRoute --> MockAPI
  MockAPI --> EP1
  MockAPI --> EP2
  ChatRoute --> Assert
  ThreadRoute --> Assert
  AgentRoute --> Assert
  Assert --> CI
```