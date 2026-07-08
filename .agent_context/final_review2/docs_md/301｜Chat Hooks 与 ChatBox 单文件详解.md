<title>301｜Chat Hooks 与 ChatBox 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续拆 frontend workspace/chat/artifacts/messages 单文件模块。
</callout>

| 模块点 | 说明 |
|-|-|
| use-thread-chat.ts | /new 临时 thread id 和状态。 |
| use-chat-mode.ts | URL mode 处理。 |
| chat-box.tsx | 聊天/Artifacts resizable panel。 |
| index.ts | chat 模块导出。 |

```mermaid
flowchart TD
  URL --> UseThreadChat
  UseThreadChat --> ThreadId
  SearchParams --> UseChatMode
  ChatPage --> ChatBox
  ChatBox --> ResizablePanels
  ThreadValues[artifacts] --> ChatBox
  ChatBox --> ArtifactPanel
  Index --> Exports
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**Chat hooks 与 ChatBox 把路由 thread 状态、stream 提交、历史消息、artifact 面板和左右布局组合起来，是聊天主链路的前端运行时装配层。
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

## 运行时状态机补充

`useThreadChat` 只负责从路由得到当前展示 thread id：`/new` 会先生成临时 uuid。真正提交时，`ChatPage` 的 `isNewThread` 仍保持为 true，避免 SDK 过早请求尚不存在的后端 history；`isWelcomeMode` 则会在 `onSend` 立即变为 false，用于先切换视觉布局。后端创建 thread 后，`onStart` 使用 `history.replaceState` 原地替换 URL，再写入真实 thread id 并关闭 new-thread 状态。

```mermaid
stateDiagram-v2
  [*] --> NewRoute: /workspace/chats/new
  NewRoute --> TempThreadId: useThreadChat creates uuid
  TempThreadId --> WelcomeMode: isNewThread true / isWelcomeMode true
  WelcomeMode --> SubmittedVisual: onSend sets isWelcomeMode false
  SubmittedVisual --> Uploading: files exist
  Uploading --> SubmittedToStream: uploadFiles success
  SubmittedVisual --> SubmittedToStream: no files
  SubmittedToStream --> BackendCreated: useStream onCreated/onStart
  BackendCreated --> StableThread: history.replaceState + setThreadId + setIsNewThread false
  StableThread --> Streaming: thread.submit
  Streaming --> Finished: onFinish invalidates caches
  Streaming --> Error: onError clears optimistic/live state
```
