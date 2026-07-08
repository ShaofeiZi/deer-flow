{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>123｜WorkspaceContainer、Header、Overscroll 组件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续按 workspace 业务组件讲解职责、输入输出和运行逻辑。\n</callout>\n\n| 组件/文件 | 说明 |\n|-|-|\n| workspace-container.tsx | 页面主容器，并导出内容区 `WorkspaceHeader`（面包屑 + GitHub 链接）和 `WorkspaceBody`。 |\n| workspace-header.tsx | 侧边栏头部：DeerFlow/DF 标识、SidebarTrigger、新建聊天入口。 |\n| overscroll.tsx | 滚动边界体验。 |\n| tooltip.tsx | workspace 局部 tooltip 封装。 |\n\n```mermaid\nflowchart TD\n  ChatPage --> MainWorkspaceHeader[workspace-container WorkspaceHeader]\n  ChatPage --> WorkspaceContainer\n  WorkspaceContainer --> WorkspaceBody\n  WorkspaceSidebar --> SidebarWorkspaceHeader[workspace-header WorkspaceHeader]\n  SidebarWorkspaceHeader --> SidebarTrigger\n  SidebarWorkspaceHeader --> NewChatLink\n  WorkspaceBody --> Content\n  Content --> Overscroll\n  UIHints --> WorkspaceTooltip\n  Header --> Actions\n  Body --> ChatOrSettings\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```\n\n<callout emoji=\"💡\">\n注意两个文件都导出名为 `WorkspaceHeader` 的组件；阅读时必须按 import 来源区分主内容 header 与 sidebar header。\n</callout>",
      "document_id": "JEBDdvjamoEHsLxNe5kmgPxIyDf",
      "revision_id": 18
    }
  }
}
