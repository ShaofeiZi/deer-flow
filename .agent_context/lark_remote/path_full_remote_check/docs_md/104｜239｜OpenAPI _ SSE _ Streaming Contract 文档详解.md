{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>239｜OpenAPI / SSE / Streaming Contract 文档详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续细化 content/docs/evidence 模块并给出维护逻辑图。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| API.md | 接口契约。 |\n| STREAMING.md | SSE 流式契约。 |\n| test_sse_format.py | SSE 格式测试。 |\n| api-client.ts | 前端 SDK 封装。 |\n\n```mermaid\nflowchart TD\n  APIDoc --> OpenAPIContract\n  StreamingDoc --> SSEContract\n  SSEContract --> BackendSSE[sse_consumer]\n  BackendSSE --> FrontendSDK[LangGraph client]\n  FrontendSDK --> UI[useThreadStream]\n  Tests --> SSEContract\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该模块固定 Gateway OpenAPI、SSE frame 格式、stream mode 兼容性和前端 SDK 消费契约。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 后端改 router、stream event 或 schema 时，前端和测试能更早发现协议漂移。 |\n| 代价 | SSE 既有 event/data/id/heartbeat/end 细节，又有 LangGraph SDK 兼容命名，文档必须和代码/测试同步。 |\n| 重点代码 | `backend/docs/API.md`、`backend/docs/STREAMING.md`、`backend/app/gateway/services.py`、`backend/tests/test_sse_format.py`、`frontend/src/core/api/api-client.ts`。 |\n| 阅读路径 | 先看 API.md 的公开路径和 stream_mode，再看 services.py 的 SSE 输出，最后看前端 SDK/hook 如何解析。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```\n\n```mermaid\nflowchart TD\n  OpenAPIDoc[API.md openapi contract] --> Router[Gateway routers]\n  StreamDoc[STREAMING.md] --> SSEConsumer[sse_consumer]\n  SSEConsumer --> Frames[event data id heartbeat end]\n  Frames --> ApiClient[frontend api-client]\n  ApiClient --> Hooks[thread stream hooks]\n  Tests[test_sse_format and openapi tests] --> Frames\n```",
      "document_id": "EM3rd6XoSo7lS7xL1gLm2F0Ayaf",
      "revision_id": 18
    }
  }
}
