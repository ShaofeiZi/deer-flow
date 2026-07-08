{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>32｜LoopDetectionMiddleware 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清重复工具调用如何被检测、预警和硬停止，避免 agent 陷入循环。\n</callout>\n\n| 机制 | 说明 |\n|-|-|\n| after_model | 观察最新 AIMessage 的 tool_calls，计算稳定 hash 和工具频率。 |\n| pending warning | warning 不在 after_model 直接插，而是在下一次 wrap_model_call 注入。 |\n| hard stop | 达到硬阈值时清空 tool_calls 并追加说明。 |\n| reset | 按 thread/run 维护状态并清理旧 key。 |\n\n```mermaid\nflowchart TD\n  A[after_model receives AIMessage] --> B{has tool calls?}\n  B -->|no| C[clear run warnings]\n  B -->|yes| D[normalize tool calls]\n  D --> E[hash sequence and count frequency]\n  E --> F{hard threshold?}\n  F -->|yes| G[strip tool_calls and append hard stop]\n  F -->|no| H{warning threshold?}\n  H -->|yes| I[queue pending warning]\n  H -->|no| J[allow]\n  I --> K[next wrap_model_call inject warning]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块采用 middleware 形态，是为了把横切能力从主 agent 逻辑里剥离出来，并按 LangChain/LangGraph 生命周期挂载。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是可插拔、可独立测试、能按 before/after/wrap 阶段控制行为。 |\n| 代价 | 代价是执行顺序不直观，多个 middleware 同时改 messages/state 时调试成本较高。 |\n| 重点代码 | 重点代码通常在 `backend/packages/harness/deerflow/agents/middlewares/`，先看 class 的 hook 方法。 |\n| 阅读路径 | 阅读路径：先判断它在哪个 hook 生效，再看它读写 ThreadState 的哪些字段。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "B0EAdEvMoo9NCDxwUHLm5GMqyUf",
      "revision_id": 15
    }
  }
}
