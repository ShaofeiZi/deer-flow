{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>237｜Frontend Reference Model Providers 文档详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续细化 content/docs/evidence 模块并给出维护逻辑图。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| reference/model-providers | 模型 provider 参考文档目录。 |\n| ark.mdx | 火山方舟 provider 说明。 |\n| index.mdx | provider 总览。 |\n| \\_meta.ts | 目录顺序和侧边栏。 |\n\n```mermaid\nflowchart TD\n  ProviderDocs --> Meta[_meta]\n  ProviderDocs --> Index[index mdx]\n  ProviderDocs --> Ark[ark mdx]\n  Meta --> PageMap\n  Index --> Nextra\n  Ark --> Nextra\n  Nextra --> DocsSite\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "UCzhdTVw0oJ6h1xoQTDmFVVtyMe",
      "revision_id": 16
    }
  }
}
