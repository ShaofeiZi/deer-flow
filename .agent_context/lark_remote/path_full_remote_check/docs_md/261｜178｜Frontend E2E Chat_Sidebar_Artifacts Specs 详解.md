{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>178｜Frontend E2E Chat/Sidebar/Artifacts Specs 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 CI、脚本、E2E 具体模块，说明触发、执行与产出。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| chat.spec.ts | 基础聊天 UI。 |\n| agent-chat.spec.ts | agent chat 流程。 |\n| sidebar.spec.ts | 侧边栏。 |\n| artifact-preview.spec.ts | artifact 预览。 |\n| chat-thread-init-ordering.spec.ts | 新 thread 初始化顺序。 |\n\n```mermaid\nflowchart TD\n  Playwright --> Chat[chat spec]\n  Playwright --> AgentChat[agent chat]\n  Playwright --> Sidebar[sidebar]\n  Playwright --> Artifact[artifact preview]\n  Playwright --> Init[thread init ordering]\n  MockAPI --> Chat\n  MockAPI --> Sidebar\n  MockAPI --> Artifact\n  Specs --> Assertions[UI assertions]\n  Assertions --> CI\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Z6d4dIlnSoqvWixQ5QNmCXK9y1d",
      "revision_id": 16
    }
  }
}
