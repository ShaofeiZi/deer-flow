{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>33｜SandboxAuditMiddleware 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 bash 命令在真正执行前如何被审计、阻断或追加警告。\n</callout>\n\n| 阶段 | 说明 |\n|-|-|\n| 输入校验 | 空命令、超长命令、null byte 会被拒绝。 |\n| 命令拆分 | 复合命令按 shell 分隔符拆分，失败时 fail-closed。 |\n| 分类 | pass/warn/block 三档。 |\n| 审计 | 写 audit 日志，block 时返回 ToolMessage。 |\n\n```mermaid\nflowchart TD\n  A[bash tool call] --> B[extract command]\n  B --> C{input valid?}\n  C -->|no| D[block ToolMessage]\n  C -->|yes| E[split compound command]\n  E --> F[classify each command]\n  F --> G{verdict}\n  G -->|block| H[write audit and block]\n  G -->|warn| I[execute then append warning]\n  G -->|pass| J[execute normally]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块采用 middleware 形态，是为了把横切能力从主 agent 逻辑里剥离出来，并按 LangChain/LangGraph 生命周期挂载。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是可插拔、可独立测试、能按 before/after/wrap 阶段控制行为。 |\n| 代价 | 代价是执行顺序不直观，多个 middleware 同时改 messages/state 时调试成本较高。 |\n| 重点代码 | 重点代码通常在 `backend/packages/harness/deerflow/agents/middlewares/`，先看 class 的 hook 方法。 |\n| 阅读路径 | 阅读路径：先判断它在哪个 hook 生效，再看它读写 ThreadState 的哪些字段。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "JH1VdeODuo4gavxMsiCmIJ5cyih",
      "revision_id": 15
    }
  }
}
