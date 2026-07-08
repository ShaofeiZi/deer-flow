{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 264｜Runtime Events Store Provider 详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 persistence/runtime 单文件，说明模型、仓储、provider 的调用关系。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| runtime/events/store/**init**.py | `make_run_event_store(config)` 是事件存储工厂。 |\n| RunEventsConfig | 通过 `run_events.backend` 选择 `memory`、`db` 或 `jsonl`。 |\n| memory backend | `MemoryRunEventStore` 用于开发/测试，不落 `run_events` 表。 |\n| db backend | `DbRunEventStore` 复用 SQLAlchemy session factory，写入 `RunEventRow`，并按 `max_trace_content` 截断 trace。 |\n| jsonl backend | `JsonlRunEventStore` 写 JSONL 文件，适合轻量单机持久化。 |\n| fallback | `run_events.backend=db` 但 session factory 不存在时，会回退到 `MemoryRunEventStore`。 |\n| RunJournal | 写入 human/message/trace/token 等事件，再由 store 分配 thread 内递增 seq。 |\n| thread_runs events API | 通过 RunEventStore 读取 messages/events。 |\n\n```mermaid\nflowchart TD\n  RunEventsConfig --> MakeEventStore[make_run_event_store]\n  MakeEventStore --> Memory[MemoryRunEventStore]\n  MakeEventStore --> Db[DbRunEventStore]\n  MakeEventStore --> Jsonl[JsonlRunEventStore]\n  Db --> RunEventRow[run_events table]\n  Db --> Fallback[no session factory -> memory]\n  RunAgent --> RunJournal\n  RunJournal --> Store[chosen RunEventStore]\n  ThreadRunsRouter --> Store\n  Store --> EventsResponse\n```",
      "document_id": "BbSodvM4koWnRkxm7bnmqw7vy5b",
      "revision_id": 20
    }
  }
}
