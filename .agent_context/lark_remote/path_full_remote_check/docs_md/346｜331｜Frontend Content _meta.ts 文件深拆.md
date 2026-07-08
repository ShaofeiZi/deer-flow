{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>331｜Frontend Content _meta.ts 文件深拆</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 remaining route/content/docker/script 内部模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| \\_meta.ts root | 语言根目录元数据。 |\n| application/\\_meta.ts | 应用文档目录。 |\n| harness/\\_meta.ts | harness 文档目录。 |\n| reference/\\_meta.ts | 参考文档目录。 |\n| tutorials/\\_meta.ts | 教程目录。 |\n| posts/\\_meta.ts | 博客元数据。 |\n\n```mermaid\nflowchart TD\n  ContentDirs --> RootMeta\n  RootMeta --> PageMap\n  ApplicationMeta --> PageMap\n  HarnessMeta --> PageMap\n  ReferenceMeta --> PageMap\n  TutorialsMeta --> PageMap\n  PostsMeta --> BlogIndex\n  PageMap --> NextraSidebar\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |\n| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |\n| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |\n| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Cu39dcmSloriSxxDBtDmNAO8yYd",
      "revision_id": 16
    }
  }
}
