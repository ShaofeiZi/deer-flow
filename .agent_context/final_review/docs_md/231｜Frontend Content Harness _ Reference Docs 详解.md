<title>231｜Frontend Content Harness / Reference Docs 详解</title>

<callout emoji="✅">
**本章目标：**继续细化 content/spec/docs 单模块，补充运行/维护逻辑图。
</callout>

| 模块点 | 说明 |
|-|-|
| content/\*/harness | harness 能力说明。 |
| content/\*/reference | API/model providers 参考。 |
| model-providers | provider 文档。 |
| docsRepositoryBase | 指向 GitHub 源码。 |

```mermaid
flowchart TD
  HarnessDocs --> Nextra
  ReferenceDocs --> Nextra
  ModelProviderDocs --> ReferenceDocs
  Nextra --> Sidebar[docs sidebar]
  Sidebar --> Page[rendered docs]
  Page --> SourceLink[GitHub source link]
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
  Route["app/workspace/chats/[thread_id]/page.tsx"] --> ChatHook["useThreadChat/useThreadStream"]
  ChatHook --> SDK["core/api/api-client.ts getAPIClient"]
  SDK --> Fetcher["core/api/fetcher.ts fetchWithAuth"]
  Fetcher -->|"X-CSRF-Token + credentials"| Gateway["gateway /api/langgraph + /api/threads"]
  ChatHook -->|"threads.search"| ThreadList["useInfiniteThreads"]
  ChatHook -->|"runs.stream"| Thread["AgentThreadState stream"]
  Route --> Providers["ChatProviders SubtasksProvider/ArtifactsProvider/PromptInputProvider"]
  Route --> Comp["components/workspace MessageList/InputBox/ThreadTitle"]
  Comp --> ThreadCtx["ThreadContext thread/isMock"]
  Thread -->|"onUpdateEvent"| Comp
  ThreadList --> Sidebar["workspace-sidebar recent-chat-list"]
```