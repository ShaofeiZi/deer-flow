{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 91｜Database、Checkpointer、RunEvents Config 详解\n\n<callout emoji=\"✅\">\n**本章目标：**拆 database/checkpointer/run_events 相关配置。\n</callout>\n\n## 本轮源码校准补充：Database、Checkpointer、RunEvents Config\n\n```mermaid\nflowchart TD\n  Lifespan[Gateway lifespan] --> DB[database engine]\n  Lifespan --> Checkpointer[checkpointer]\n  Lifespan --> Store[LangGraph store]\n  Lifespan --> RunStore[Run store]\n  Lifespan --> EventStore[Run event store]\n  EventStore --> Journal[RunJournal]\n  Checkpointer --> Rollback[rollback/checkpoint history]\n```\n\n| 配置 | 影响 |\n|-|-|\n| database | 持久化 run/thread/feedback/user 等数据的基础连接。 |\n| checkpointer | LangGraph checkpoint、history、rollback 的基础。 |\n| run events | run journal、message history、token/progress 记录。 |\n| startup 边界 | 这些资源多在 lifespan 初始化；修改配置后通常需要重启 Gateway。 |\n\n| 模块点 | 说明 |\n|-|-|\n| DatabaseConfig | 数据库 backend 和连接配置。 |\n| CheckpointerConfig | LangGraph checkpoint backend 选择。 |\n| RunEventsConfig | run events 存储开关和后端。 |\n| StreamBridgeConfig | stream bridge backend。 |\n\n```mermaid\nflowchart TD\n  Config[config yaml] --> DB[DatabaseConfig]\n  Config --> CP[CheckpointerConfig]\n  Config --> Events[RunEventsConfig]\n  Config --> Bridge[StreamBridgeConfig]\n  DB --> Engine[init_engine]\n  CP --> Checkpointer[make_checkpointer]\n  Events --> EventStore[make_run_event_store]\n  Bridge --> StreamBridge[make_stream_bridge]\n  Engine --> Repos[run feedback thread repositories]\n```",
      "document_id": "Qp22dl4NqoC0LfxmskNmfXqcyLb",
      "revision_id": 26
    }
  }
}
