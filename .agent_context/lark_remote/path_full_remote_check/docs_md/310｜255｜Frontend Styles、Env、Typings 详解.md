{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>255｜Frontend Styles、Env、Typings 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐 persistence/runtime/frontend 基础设施模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| styles/globals.css | 全局样式。 |\n| env | Next.js env validation。 |\n| typings/md.d.ts | Markdown 类型声明。 |\n| tailwind/postcss config | 样式构建。 |\n| components.json | shadcn 组件配置。 |\n\n```mermaid\nflowchart TD\n  CSS[globals css] --> AppLayout\n  Env[env validation] --> RuntimeConfig\n  Typings[md d ts] --> TSCompiler\n  Tailwind[tailwind postcss] --> Build\n  ComponentsJson --> UIPrimitives\n  Build --> FrontendApp\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "JyumdDj7ioEyWWxAcfImBGpfyAd",
      "revision_id": 16
    }
  }
}
