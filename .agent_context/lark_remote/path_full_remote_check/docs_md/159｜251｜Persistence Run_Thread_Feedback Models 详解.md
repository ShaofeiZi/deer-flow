{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 251｜Persistence Run/Thread/Feedback Models 详解\n\n<callout emoji=\"✅\">\n**本章目标：**补齐 persistence/runtime/frontend 基础设施模块。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| run/model.py | RunRow 表。 |\n| thread_meta/model.py | ThreadMetaRow 表。 |\n| feedback/model.py | FeedbackRow 表。 |\n| models/run_event.py | RunEventRow 表。 |\n| user/model.py | UserRow 表。 |\n\n```mermaid\nflowchart TD\n  SQLAlchemyBase --> RunRow\n  SQLAlchemyBase --> ThreadMetaRow\n  SQLAlchemyBase --> FeedbackRow\n  SQLAlchemyBase --> RunEventRow\n  SQLAlchemyBase --> UserRow\n  RunRepository --> RunRow\n  ThreadRepo --> ThreadMetaRow\n  FeedbackRepo --> FeedbackRow\n  EventStore --> RunEventRow\n```",
      "document_id": "Ec12dK8I5oOYEUxY2mDmuuiuyZf",
      "revision_id": 18
    }
  }
}
