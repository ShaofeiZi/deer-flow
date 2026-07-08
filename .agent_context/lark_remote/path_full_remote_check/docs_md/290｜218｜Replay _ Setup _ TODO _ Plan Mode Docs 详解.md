{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>218｜Replay / Setup / TODO / Plan Mode Docs 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 backend/docs 与项目文档模块，说明用途和关联代码。\n</callout>\n\n| 文档点 | 说明 |\n|-|-|\n| REPLAY_E2E.md | Replay E2E 使用说明。 |\n| SETUP.md | 后端 setup 说明。 |\n| TODO.md | 待办列表。 |\n| plan_mode_usage.md | plan mode 用法。 |\n| task_tool_improvements.md | task tool 改进记录。 |\n\n```mermaid\nflowchart TD\n  ReplayDoc --> ReplayFixtures[record and replay fixtures]\n  SetupDoc --> DevSetup[backend setup]\n  PlanModeDoc --> TodoMiddleware[TodoMiddleware]\n  TaskDoc --> TaskTool[task tool]\n  TodoDoc --> Backlog[future improvements]\n  ReplayFixtures --> Tests[replay e2e tests]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "ZfmqdK80tomX36xDlermqzhNyYb",
      "revision_id": 16
    }
  }
}
