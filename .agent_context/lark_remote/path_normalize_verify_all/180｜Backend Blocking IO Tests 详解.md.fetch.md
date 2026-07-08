{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>180｜Backend Blocking IO Tests 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 CI、脚本、E2E 具体模块，说明触发、执行与产出。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| blocking_io/conftest.py | 启用 Blockbuster gate。 |\n| test_sqlite_lifespan | SQLite lifespan 异步边界。 |\n| test_uploads_middleware | 上传中间件阻塞检查。 |\n| test_dynamic_context_middleware | 动态上下文阻塞检查。 |\n| test_agents_router | agents router 阻塞检查。 |\n\n```mermaid\nflowchart TD\n  Pytest --> Blockbuster[blocking io conftest]\n  Blockbuster --> TestSQLite\n  Blockbuster --> TestUploads\n  Blockbuster --> TestDynamicContext\n  Blockbuster --> TestAgentsRouter\n  Tests --> Detect[detect sync IO in async path]\n  Detect --> Fail[fail if blocking]\n  Detect --> Pass[pass gate]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是前后端契约清晰，接口可独立演进。 |\n| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |\n| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |\n| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Flz4daeKQoknccxEUlvmG9Rzy3b",
      "revision_id": 18
    }
  }
}
