<title>40｜Memory Queue、Updater、Storage 单文件详解</title>

<callout emoji="✅">
**本章目标：**讲清 memory 从对话过滤、入队 debounce、LLM 更新、文件存储的完整链路。
</callout>

## 本轮源码校准补充：Memory 注入与更新

| 阶段 | 说明 |
|-|-|
| 注入 | memory 不是简单拼进静态 prompt；通常通过 DynamicContextMiddleware 以 hidden/system-reminder 形式注入当前 turn。 |
| 更新 | MemoryMiddleware / MemoryUpdateQueue 异步队列化对话摘要、事实抽取和持久化。 |
| scope | memory 与 user、agent、配置有关，调试时要先确认 effective user。 |
| 存储 | FileMemoryStorage/配置化 storage 负责持久化和 reload。 |

| 文件 | 职责 |
|-|-|
| `message_processing.py` | 抽取文本、过滤消息、检测纠正/强化。 |
| `queue.py` | ConversationContext、debounce、后台更新队列。 |
| `updater.py` | 构造更新 prompt、解析 JSON、归一化、应用更新。 |
| `storage.py` | FileMemoryStorage 读写 memory.json。 |
| `prompt.py` | format_memory_for_injection 和 conversation update prompt。 |

```mermaid
sequenceDiagram
  participant MW as MemoryMiddleware
  participant MP as message_processing
  participant Q as MemoryUpdateQueue
  participant U as MemoryUpdater
  participant LLM as LLM
  participant S as FileMemoryStorage
  MW->>MP: filter_messages_for_memory
  MP-->>MW: user and final assistant messages
  MW->>Q: add ConversationContext
  Q-->>Q: debounce and merge
  Q->>U: update_memory
  U->>S: load current memory
  U->>LLM: memory update prompt
  LLM-->>U: JSON update
  U->>U: normalize and strip upload mentions
  U->>S: save memory.json
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这些模块负责扩展 agent 能力：skill 提供方法论，MCP 提供外部工具，memory 提供长期上下文。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是能力可扩展、可配置、可跨会话复用。 |
| 代价 | 代价是 prompt、工具、记忆三者都会影响模型行为，问题定位需要分层排查。 |
| 重点代码 | 重点代码在 `backend/packages/harness/deerflow/skills`、`mcp`、`agents/memory`。 |
| 阅读路径 | 阅读路径：把 skill 当说明书，MCP 当工具注册表，memory 当上下文注入源。 |

```mermaid
flowchart TD
  A[设计目的] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```