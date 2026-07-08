{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>323｜Frontend Root/Auth/Workspace Page Layout 深拆</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 backend tests、frontend pages、docker/provisioner、wizard step 模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| app/layout.tsx | Root layout、ThemeProvider、I18nProvider。 |\n| app/page.tsx | Landing page。 |\n| app/(auth)/layout.tsx | Auth layout。 |\n| app/(auth)/login/page.tsx | 登录页。 |\n| app/(auth)/setup/page.tsx | 初始化/改密码页。 |\n| app/workspace/layout.tsx | workspace 鉴权布局。 |\n\n```mermaid\nflowchart TD\n  RootLayout --> ThemeProvider\n  RootLayout --> I18nProvider\n  LandingRoute --> LandingPage\n  AuthLayout --> LoginPage\n  AuthLayout --> SetupPage\n  WorkspaceLayout --> ServerSideUser\n  ServerSideUser --> WorkspaceContent\n  ServerSideUser --> Redirects\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "ZiDYd8Blkoe9RQxGATcmi0hYy8c",
      "revision_id": 16
    }
  }
}
