{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>72｜Frontend Landing、Docs、Blog 页面详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**补齐官网 landing、Nextra docs、blog/content 模块。\n</callout>\n\n# 1. 模块职责\n\n| 模块 | 说明 |\n|-|-|\n| Landing | `components/landing/*` 和 `app/page.tsx` 组成首页。 |\n| Docs | `app/[lang]/docs` 使用 Nextra importPage 渲染 MDX。 |\n| Blog | `app/blog` 读取 content posts/tags。 |\n| Content | `frontend/src/content/en\\|zh` 存放文档内容。 |\n| I18n | `frontend/src/core/i18n` 提供 locale detection 和 provider。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  Root[app page] --> Landing[Landing sections]\n  Landing --> Hero[Hero]\n  Landing --> Skills[Skills section]\n  Landing --> Sandbox[Sandbox section]\n  DocsRoute[app lang docs] --> Nextra[Nextra Layout]\n  Nextra --> Content[MDX content by locale]\n  BlogRoute[app blog] --> BlogCore[core blog]\n  BlogCore --> Posts[content posts]\n  I18n[detect locale] --> Layout[RootLayout I18nProvider]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是前后端契约清晰，接口可独立演进。 |\n| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |\n| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |\n| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Wc80dFkogouhcuxbpIOmzcBPyIb",
      "revision_id": 18
    }
  }
}
