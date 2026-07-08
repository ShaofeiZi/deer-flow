{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>35｜SafetyFinishReasonMiddleware 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 provider 安全终止时，如何抑制半截 tool_calls，避免执行不完整或风险工具。\n</callout>\n\n| 点 | 说明 |\n|-|-|\n| Hook | after_model，处理正常返回但带 safety finish reason 的 AIMessage。 |\n| detectors | OpenAI/Anthropic/Gemini 等 detector。 |\n| 动作 | 清空 tool_calls，追加用户可读说明，记录 audit event。 |\n| 目的 | 防止 provider 中途安全截断后仍执行半成型工具调用。 |\n\n```mermaid\nflowchart TD\n  A[AIMessage after model] --> B[detect safety termination]\n  B --> C{hit?}\n  C -->|no| D[return none]\n  C -->|yes| E[record audit event]\n  E --> F[clear tool_calls]\n  F --> G[append safety explanation]\n  G --> H[return patched message]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块采用 middleware 形态，是为了把横切能力从主 agent 逻辑里剥离出来，并按 LangChain/LangGraph 生命周期挂载。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是可插拔、可独立测试、能按 before/after/wrap 阶段控制行为。 |\n| 代价 | 代价是执行顺序不直观，多个 middleware 同时改 messages/state 时调试成本较高。 |\n| 重点代码 | 重点代码通常在 `backend/packages/harness/deerflow/agents/middlewares/`，先看 class 的 hook 方法。 |\n| 阅读路径 | 阅读路径：先判断它在哪个 hook 生效，再看它读写 ThreadState 的哪些字段。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "AqFBdegF4osKOsx759OmqUGfyGd",
      "revision_id": 15
    }
  }
}
