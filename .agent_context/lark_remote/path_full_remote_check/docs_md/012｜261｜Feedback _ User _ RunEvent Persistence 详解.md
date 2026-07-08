{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>261｜Feedback / User / RunEvent Persistence 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 persistence/runtime 单文件，说明模型、仓储、provider 的调用关系。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| feedback/model.py | FeedbackRow。 |\n| feedback/sql.py | FeedbackRepository。 |\n| user/model.py | UserRow。 |\n| models/run_event.py | RunEventRow。 |\n| events store | RunJournal 写入 RunEventStore；只有 `run_events.backend=db` 时才落 `RunEventRow`。 |\n\n```mermaid\nflowchart TD\n  FeedbackRouter --> FeedbackRepository\n  FeedbackRepository --> FeedbackRow\n  AuthProvider --> UserRow\n  RunJournal --> RunEventStore\n  RunEventStore --> MemoryOrJsonl[memory or jsonl backend]\n  RunEventStore --> DbBackend[db backend]\n  DbBackend --> RunEventRow\n  RunsAPI --> RunEventStore\n  FeedbackStats --> FeedbackRepository\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明工程脚本、测试、部署或运行时辅助模块的职责、调用入口和验证方式，避免把流程知识只留在脚本里。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 新同学能按脚本/测试入口复现工程流程，并知道失败时应检查哪个阶段。 |\n| 代价 | 脚本和 CI 逻辑容易随依赖或平台变化漂移，需要用命令和源码双重验证。 |\n| 重点代码 | 文档标题对应的 `scripts/`、`docker/`、`backend/tests/`、`frontend/tests/` 或 `docs/` 文件。 |\n| 阅读路径 | 先看入口命令，再看脚本调用链，最后看测试或日志如何证明行为。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "PX2xdEvvjogMKFxoLFfm5iM3yHc",
      "revision_id": 20
    }
  }
}
