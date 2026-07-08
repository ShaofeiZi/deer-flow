{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>81｜Nextra Docs、Content 与 Blog 渲染详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清文档站、博客、content 多语言内容如何被路由加载。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| Docs route | `app/[lang]/docs/[[...mdxPath]]` 调 importPage。 |\n| Docs layout | Nextra Layout + pageMap + i18n。 |\n| Blog route | `app/blog` 读取 posts/tags。 |\n| Content | `src/content/en\\|zh` 存放 MDX。 |\n| MDX components | 统一 wrapper 和组件。 |\n\n```mermaid\nflowchart TD\n  URL[docs or blog URL] --> Route[Next app route]\n  Route --> Locale[detect preferred lang]\n  Locale --> Import[importPage or getAllPosts]\n  Import --> Content[MDX content]\n  Content --> Wrapper[MDX components wrapper]\n  Wrapper --> Nextra[Nextra Layout]\n  Nextra --> Browser[rendered page]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "AQyEdfAQtoEFjSx9QGkmHu9NyYe",
      "revision_id": 18
    }
  }
}
