{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>306｜CommandPalette、GithubIcon、Tooltip 组件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 frontend workspace/chat/artifacts/messages 单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| command-palette.tsx | 全局命令面板。 |\n| github-icon.tsx | GitHub 图标。 |\n| tooltip.tsx | workspace tooltip 封装。 |\n| copy-button.tsx | 复制按钮也复用 workspace 交互。 |\n\n```mermaid\nflowchart TD\n  KeyboardShortcut --> CommandPalette\n  CommandPalette --> CommandItems\n  CommandItems --> Navigation\n  UI --> Tooltip\n  GitHubLink --> GithubIcon\n  CopyAction --> CopyButton\n  CopyButton --> Clipboard\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "T8D7dkDjEoe8fexsuKOmSzhqy7d",
      "revision_id": 16
    }
  }
}
