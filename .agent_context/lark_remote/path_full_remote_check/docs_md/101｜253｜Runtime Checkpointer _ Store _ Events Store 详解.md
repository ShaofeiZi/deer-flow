{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 253｜Runtime Checkpointer / Store / Events Store 详解\n\n<callout emoji=\"✅\">\n**本章目标：**补齐 persistence/runtime/frontend 基础设施模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| runtime/checkpointer/\\* | make_checkpointer provider。 |\n| runtime/store/\\* | make_store provider。 |\n| runtime/events/store | run event store。 |\n| runtime/store/\\_sqlite_utils.py | SQLite 工具。 |\n| async_provider.py | 异步上下文 provider。 |\n\n```mermaid\nflowchart TD\n  GatewayLifespan --> MakeCheckpointer\n  GatewayLifespan --> MakeStore\n  GatewayLifespan --> MakeEventStore\n  MakeCheckpointer --> Checkpointer\n  MakeStore --> LangGraphStore\n  MakeEventStore --> RunEventStore\n  RunAgent --> Checkpointer\n  RunJournal --> RunEventStore\n  ThreadsRouter --> LangGraphStore\n```\n\n<callout emoji=\"💡\">\n**运行时持久化边界：**checkpointer、LangGraph store、RunStore/ThreadMeta/Feedback repositories、RunEventStore 是四条相关但不完全相同的持久化链路。\n</callout>\n\n| 链路 | 当前来源 |\n|-|-|\n| Checkpointer | `make_checkpointer()` 优先 legacy `checkpointer:`，其次 unified `database:` 非 memory，最后 `InMemorySaver`。 |\n| LangGraph Store | `make_store()` 当前只跟 legacy `checkpointer:`；没有该段时回退 `InMemoryStore`。 |\n| Run/Thread/Feedback repositories | Gateway lifespan 先 `init_engine_from_config(config.database)`，有 session factory 时使用 SQL repositories，否则 memory store/空 feedback。 |\n| RunEventStore | `make_run_event_store(config.run_events)` 单独选择 `memory`、`db` 或 `jsonl`；`db` 复用 SQLAlchemy session factory，失败时回退 memory。 |\n\n```mermaid\nflowchart TD\n  Lifespan[Gateway lifespan] --> InitDB[init_engine_from_config]\n  Lifespan --> Checkpointer[make_checkpointer]\n  Lifespan --> LGStore[make_store]\n  Lifespan --> EventFactory[make_run_event_store]\n  InitDB --> SQLRepos[Run ThreadMeta Feedback repositories]\n  EventFactory --> EventStore[RunEventStore memory db jsonl]\n  Worker[run_agent worker] --> Checkpointer\n  Worker --> Journal[RunJournal]\n  Journal --> EventStore\n  ThreadsRouter[threads messages APIs] --> SQLRepos\n  ThreadsRouter --> EventStore\n```",
      "document_id": "D6yodUpI9oCjvZx5ad1mKCAay0e",
      "revision_id": 20
    }
  }
}
