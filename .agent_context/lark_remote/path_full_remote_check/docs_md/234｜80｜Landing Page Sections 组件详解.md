{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>80｜Landing Page Sections 组件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲清首页各 section 的组合和内容层级。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| Hero | 首页主视觉和 CTA。 |\n| CaseStudySection | 案例展示。 |\n| SkillsSection | skills 能力展示。 |\n| SandboxSection | sandbox 能力展示。 |\n| WhatsNewSection | 版本亮点。 |\n| CommunitySection | 社区引导。 |\n\n```mermaid\nflowchart TD\n  Page[app page] --> Header\n  Page --> Hero\n  Page --> CaseStudy\n  Page --> Skills\n  Page --> Sandbox\n  Page --> WhatsNew\n  Page --> Community\n  Page --> Footer\n  Skills --> Animation[progressive skills animation]\n  Sections --> UI[shared Section layout]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Odo6dODyOooQqSxIkFGm4V5EyHt",
      "revision_id": 16
    }
  }
}
