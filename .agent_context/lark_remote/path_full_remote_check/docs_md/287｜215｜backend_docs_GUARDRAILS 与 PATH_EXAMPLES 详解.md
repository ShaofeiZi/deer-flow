{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>215｜backend/docs/GUARDRAILS 与 PATH_EXAMPLES 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续把 backend/docs 中重要说明拆成独立讲解文档。\n</callout>\n\n| 文档点 | 说明 |\n|-|-|\n| GUARDRAILS.md | 工具调用安全策略。 |\n| PATH_EXAMPLES.md | 虚拟路径和物理路径示例。 |\n| BLOCKING_IO_DETECTION.md | 阻塞 IO 检测。 |\n| SANDBOX_MEMORY_PROFILING.md | sandbox 内存画像。 |\n\n```mermaid\nflowchart TD\n  SafetyDocs --> Guardrails\n  SafetyDocs --> PathExamples\n  SafetyDocs --> BlockingIO\n  SafetyDocs --> SandboxMemory\n  Guardrails --> GuardrailMiddleware\n  PathExamples --> SandboxTools\n  BlockingIO --> BlockingTests\n  SandboxMemory --> ProfileScript\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |\n| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |\n| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |\n| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Gm17danMcod7CvxlF88mhxGmyhg",
      "revision_id": 16
    }
  }
}
