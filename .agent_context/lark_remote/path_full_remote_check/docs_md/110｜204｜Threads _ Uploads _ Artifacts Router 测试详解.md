{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>204｜Threads / Uploads / Artifacts Router 测试详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆单测试族、单规格文档和根文档模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| test_threads_router.py | thread CRUD/state/history。 |\n| test_uploads_router.py | uploads API。 |\n| test_artifacts_router.py | artifact API。 |\n| test_feedback.py | feedback API。 |\n| test_suggestions_router.py | suggestions API。 |\n\n```mermaid\nflowchart TD\n  ThreadsRouter --> ThreadTests\n  UploadsRouter --> UploadTests\n  ArtifactsRouter --> ArtifactTests\n  FeedbackRouter --> FeedbackTests\n  SuggestionsRouter --> SuggestionTests\n  Tests --> FastAPIClient\n  FastAPIClient --> Assertions\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这组测试保护 Gateway router 的 HTTP 契约：thread CRUD/state/history、uploads 限制与路径安全、artifact 预览/下载、feedback 和 suggestions。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 浏览器/API 客户端依赖的状态码、响应字段、owner check 和路径安全行为可稳定回归。 |\n| 代价 | 一个请求可能同时经过 authz、router、manager/repository、filesystem helper 和 runtime state。 |\n| 重点代码 | `backend/app/gateway/routers/threads.py`、`backend/app/gateway/routers/uploads.py`、`backend/app/gateway/routers/artifacts.py`、`backend/app/gateway/routers/feedback.py`、`backend/app/gateway/routers/suggestions.py`，以及对应 `backend/tests/test_*_router.py`。 |\n| 阅读路径 | 先看 route path 与 response model，再追 manager/repository/filesystem helper，最后核对测试中的 status code、owner isolation 和安全断言。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "D9lxdFWHloLMWlxGT6KmcBbPykd",
      "revision_id": 22
    }
  }
}
