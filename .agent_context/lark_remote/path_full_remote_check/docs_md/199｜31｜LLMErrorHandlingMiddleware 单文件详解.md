{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>31｜LLMErrorHandlingMiddleware 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清模型调用异常如何分类、重试、熔断，并转换为用户可理解的 fallback message。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| Hook | `wrap_model_call/awrap_model_call` 包裹模型请求。 |\n| 分类 | quota/auth/transient/busy/generic。 |\n| 重试 | 按异常类型和 retry-after 计算退避。 |\n| 熔断 | 连续失败时 circuit breaker 保护 provider。 |\n| UI 反馈 | 通过 custom event 发出 llm_retry toast。 |\n\n```mermaid\nflowchart TD\n  A[model request] --> B{circuit open?}\n  B -->|yes| C[return circuit breaker AIMessage]\n  B -->|no| D[call model]\n  D -->|success| E[record success and return response]\n  D -->|error| F[classify error]\n  F --> G{retryable and attempts left?}\n  G -->|yes| H[emit retry event and sleep]\n  H --> D\n  G -->|no| I[record failure]\n  I --> J[build user fallback AIMessage]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块采用 middleware 形态，是为了把横切能力从主 agent 逻辑里剥离出来，并按 LangChain/LangGraph 生命周期挂载。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是可插拔、可独立测试、能按 before/after/wrap 阶段控制行为。 |\n| 代价 | 代价是执行顺序不直观，多个 middleware 同时改 messages/state 时调试成本较高。 |\n| 重点代码 | 重点代码通常在 `backend/packages/harness/deerflow/agents/middlewares/`，先看 class 的 hook 方法。 |\n| 阅读路径 | 阅读路径：先判断它在哪个 hook 生效，再看它读写 ThreadState 的哪些字段。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "YFlDdZ5uLoCidrxeQJ6mzqhfyUc",
      "revision_id": 15
    }
  }
}
