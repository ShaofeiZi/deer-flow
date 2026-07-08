{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>40｜Memory Queue、Updater、Storage 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 memory 从对话过滤、入队 debounce、LLM 更新、文件存储的完整链路。\n</callout>\n\n## 本轮源码校准补充：Memory 注入与更新\n\n| 阶段 | 说明 |\n|-|-|\n| 注入 | memory 不是简单拼进静态 prompt；通常通过 DynamicContextMiddleware 以 hidden/system-reminder 形式注入当前 turn。 |\n| 更新 | MemoryMiddleware / MemoryUpdateQueue 异步队列化对话摘要、事实抽取和持久化。 |\n| scope | memory 与 user、agent、配置有关，调试时要先确认 effective user。 |\n| 存储 | FileMemoryStorage/配置化 storage 负责持久化和 reload。 |\n\n| 文件 | 职责 |\n|-|-|\n| `message_processing.py` | 抽取文本、过滤消息、检测纠正/强化。 |\n| `queue.py` | ConversationContext、debounce、后台更新队列。 |\n| `updater.py` | 构造更新 prompt、解析 JSON、归一化、应用更新。 |\n| `storage.py` | FileMemoryStorage 读写 memory.json。 |\n| `prompt.py` | format_memory_for_injection 和 conversation update prompt。 |\n\n```mermaid\nsequenceDiagram\n  participant MW as MemoryMiddleware\n  participant MP as message_processing\n  participant Q as MemoryUpdateQueue\n  participant U as MemoryUpdater\n  participant LLM as LLM\n  participant S as FileMemoryStorage\n  MW->>MP: filter_messages_for_memory\n  MP-->>MW: user and final assistant messages\n  MW->>Q: add ConversationContext\n  Q-->>Q: debounce and merge\n  Q->>U: update_memory\n  U->>S: load current memory\n  U->>LLM: memory update prompt\n  LLM-->>U: JSON update\n  U->>U: normalize and strip upload mentions\n  U->>S: save memory.json\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这些模块负责扩展 agent 能力：skill 提供方法论，MCP 提供外部工具，memory 提供长期上下文。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是能力可扩展、可配置、可跨会话复用。 |\n| 代价 | 代价是 prompt、工具、记忆三者都会影响模型行为，问题定位需要分层排查。 |\n| 重点代码 | 重点代码在 `backend/packages/harness/deerflow/skills`、`mcp`、`agents/memory`。 |\n| 阅读路径 | 阅读路径：把 skill 当说明书，MCP 当工具注册表，memory 当上下文注入源。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "LEsJdNSIWoaRpUxxcxCms3S9ykd",
      "revision_id": 17
    }
  }
}
