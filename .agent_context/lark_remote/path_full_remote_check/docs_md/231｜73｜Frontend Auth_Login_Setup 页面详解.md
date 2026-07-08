{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>73｜Frontend Auth/Login/Setup 页面详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清前端登录、初始化 admin、修改密码和 Gateway unavailable fallback。\n</callout>\n\n# 1. 模块职责\n\n| 模块 | 说明 |\n|-|-|\n| `app/(auth)/layout.tsx` | 根据 getServerSideUser 判断跳转或渲染。 |\n| `login/page.tsx` | 登录/注册表单，调用 auth API。 |\n| `setup/page.tsx` | 首次初始化 admin 或强制改密码。 |\n| `frontend/src/core/auth/*` | AuthProvider、server user、proxy policy、types。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  AuthLayout --> ServerUser[getServerSideUser]\n  ServerUser --> Decision{status}\n  Decision -->|authenticated| Workspace[redirect workspace]\n  Decision -->|needs setup| Setup[setup page]\n  Decision -->|unauthenticated| Login[login page]\n  Login --> AuthAPI[api v1 auth login/register]\n  Setup --> Init[api v1 auth initialize/change password]\n  AuthAPI --> Cookie[HttpOnly session]\n  Cookie --> AuthProvider[client AuthProvider]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "P0ybdryeloBAZsxsrWWm1iOQyjF",
      "revision_id": 18
    }
  }
}
