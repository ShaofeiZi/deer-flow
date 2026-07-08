{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>247｜Frontend Core Blog 与 I18n 细节详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆测试 helper、fixtures、frontend content 支持模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| core/blog/index.ts | 读取 posts、tags、preferred language。 |\n| core/i18n/server.ts | 服务端 locale 检测。 |\n| core/i18n/context.tsx | I18nProvider。 |\n| core/i18n/translations.ts | 翻译聚合。 |\n| locales/en-US zh-CN | 语言包。 |\n\n```mermaid\nflowchart TD\n  Request --> DetectLocale\n  DetectLocale --> I18nProvider\n  I18nProvider --> UITranslations\n  BlogRoute --> BlogCore\n  BlogCore --> PreferredLang\n  PreferredLang --> Posts\n  Posts --> PostList\n  Locales --> UITranslations\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "ZQVpdSguvoxtOZxHSTGmluX4yjd",
      "revision_id": 16
    }
  }
}
