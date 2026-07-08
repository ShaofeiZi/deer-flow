{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>93｜Frontend UI Primitives 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 components/ui 中基础组件如何支撑 workspace 和 landing。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| Button/Input/Dialog | 基础交互组件。 |\n| Sidebar/ScrollArea/Resizable | workspace 布局和滚动/分栏。 |\n| Select/Dropdown/Command | 模型选择、菜单、命令面板。 |\n| Tooltip/Badge/Alert/Skeleton | 提示、状态和加载态。 |\n| ThemeProvider | 主题切换和系统主题。 |\n\n```mermaid\nflowchart TD\n  UI[components ui primitives] --> Workspace[workspace components]\n  UI --> Landing[landing components]\n  Button --> InputBox\n  Dialog --> SettingsDialog\n  Sidebar --> WorkspaceSidebar\n  ScrollArea --> MessageList\n  Resizable --> ChatBox\n  Select --> ModelSelector\n  Command --> CommandPalette\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "T2S7diLrro8qWjxgBkDmAiW9yih",
      "revision_id": 16
    }
  }
}
