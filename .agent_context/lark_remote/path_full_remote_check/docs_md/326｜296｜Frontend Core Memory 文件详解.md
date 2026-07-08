{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>296｜Frontend Core Memory 文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 frontend core 数据层单文件模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| memory/api.ts | load/clear/import/export/facts CRUD。 |\n| memory/hooks.ts | useMemory 和 mutations。 |\n| memory/types.ts | UserMemory/MemoryFact 类型。 |\n| memory/index.ts | 统一导出。 |\n\n```mermaid\nflowchart TD\n  MemorySettings --> UseMemory\n  UseMemory --> LoadMemory[GET api memory]\n  FactCreate --> POSTFact\n  FactPatch --> PATCHFact\n  FactDelete --> DELETEFact\n  Import --> ImportAPI\n  Export --> ExportAPI\n  Mutations --> QueryData[setQueryData memory]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "JN6Ud0UD4oGhQ2xt01BmachEyNf",
      "revision_id": 16
    }
  }
}
