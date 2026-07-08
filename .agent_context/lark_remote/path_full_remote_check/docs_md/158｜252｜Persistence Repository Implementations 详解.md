{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 252｜Persistence Repository Implementations 详解\n\n<callout emoji=\"✅\">\n**本章目标：**补齐 persistence/runtime/frontend 基础设施模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| run/sql.py | RunRepository。 |\n| thread_meta/sql.py | ThreadMetaRepository。 |\n| thread_meta/memory.py | MemoryThreadMetaStore。 |\n| feedback/sql.py | FeedbackRepository。 |\n| json_compat.py | 跨数据库 JSON 查询。 |\n\n```mermaid\nflowchart TD\n  Router --> Repository\n  Repository --> RunRepository\n  Repository --> ThreadMetaRepository\n  Repository --> FeedbackRepository\n  ThreadMetaRepository --> SQLStore\n  ThreadMetaRepository --> MemoryStore\n  RunRepository --> RunTable\n  FeedbackRepository --> FeedbackTable\n  Filters --> JsonCompat\n```",
      "document_id": "YPaEdeb9AoNpwBxqCFcmZTGxyid",
      "revision_id": 18
    }
  }
}
