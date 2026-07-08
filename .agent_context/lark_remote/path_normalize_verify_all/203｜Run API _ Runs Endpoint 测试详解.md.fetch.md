{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>203｜Run API / Runs Endpoint 测试详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆单测试族、单规格文档和根文档模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| test_runs_api_endpoints.py | run API endpoints。 |\n| test_cancel_run_idempotent.py | cancel 幂等。 |\n| test_gateway_services.py | services.start_run。 |\n| test_thread_run_messages_pagination.py | run messages 分页。 |\n| test_run_worker_rollback.py | rollback。 |\n\n```mermaid\nflowchart TD\n  RunAPI --> EndpointTests\n  Cancel --> CancelTests\n  Services --> ServiceTests\n  Messages --> PaginationTests\n  Worker --> RollbackTests\n  EndpointTests --> RunManager\n  ServiceTests --> RunManager\n  RollbackTests --> Checkpointer\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是前后端契约清晰，接口可独立演进。 |\n| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |\n| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |\n| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "KAD8dRD4aoKkUix8wNVmF4K9yoe",
      "revision_id": 18
    }
  }
}
