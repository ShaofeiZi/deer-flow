{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>342｜Landing Header / Footer / Section 组件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续细化前端 UI/Landing/I18n 模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| header.tsx | 首页顶部导航。 |\n| footer.tsx | 页脚。 |\n| section.tsx | 通用 section 布局。 |\n| post-list.tsx | 文章列表组件。 |\n\n```mermaid\nflowchart TD\n  LandingPage --> Header\n  LandingPage --> Sections\n  Sections --> SectionWrapper\n  LandingPage --> Footer\n  BlogPage --> PostList\n  Header --> Navigation\n  Footer --> Links\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "VrzHdwzdRoi76PxCPb2mWMD9yrg",
      "revision_id": 16
    }
  }
}
