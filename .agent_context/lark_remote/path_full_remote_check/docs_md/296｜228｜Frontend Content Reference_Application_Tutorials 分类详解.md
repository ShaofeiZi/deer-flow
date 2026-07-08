{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>228｜Frontend Content Reference/Application/Tutorials 分类详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆剩余文档/content 模块，说明用途和关联运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| reference | 模型 providers/API 参考。 |\n| application | 应用场景文档。 |\n| tutorials | 教程。 |\n| posts | 博客文章。 |\n| meta files | \\_meta.ts 控制目录。 |\n\n```mermaid\nflowchart TD\n  Content --> Reference\n  Content --> Application\n  Content --> Tutorials\n  Content --> Posts\n  Meta[_meta ts] --> NextraPageMap\n  Reference --> DocsSite\n  Application --> DocsSite\n  Tutorials --> DocsSite\n  Posts --> Blog\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "KdEbdHreKob17ixvQMrmrhExyWk",
      "revision_id": 16
    }
  }
}
