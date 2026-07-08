{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>284｜Frontend Core Uploads / Agents / Notification 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 channels/auth/frontend core 单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| core/uploads | upload/list/delete files、file validation。 |\n| core/agents | agents API/hooks/types。 |\n| core/notification | 浏览器通知 hook。 |\n| prompt-input-files | PromptInput file 转 File。 |\n\n```mermaid\nflowchart TD\n  InputBox --> PromptInputFiles\n  PromptInputFiles --> UploadsAPI\n  UploadsAPI --> GatewayUploads\n  AgentsPage --> AgentsHooks\n  AgentsHooks --> AgentsAPI\n  RunFinish --> NotificationHook\n  NotificationHook --> BrowserNotification\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "ROhedWkLuo9JQ4xnm25mXjRQyOg",
      "revision_id": 16
    }
  }
}
