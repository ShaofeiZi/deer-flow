{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>46｜Persistence Repository 文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**把 run/thread_meta/feedback/user/run_event 持久化表与 repository 职责讲清。\n</callout>\n\n| 模块 | 文件 | 职责 |\n|-|-|-|\n| Run | `persistence/run/model.py`、`sql.py` | RunRow 和 RunRepository。 |\n| ThreadMeta | `persistence/thread_meta/model.py`、`sql.py` | 线程标题、状态、metadata、搜索。 |\n| Feedback | `persistence/feedback/model.py`、`sql.py` | run feedback CRUD 和统计。 |\n| User | `persistence/user/model.py` | 本地用户表。 |\n| RunEvent | `persistence/models/run_event.py` | run event / message event 持久化。 |\n\n```mermaid\nflowchart TD\n  Engine[SQLAlchemy AsyncEngine] --> Session[async_sessionmaker]\n  Session --> RunRepo[RunRepository]\n  Session --> ThreadRepo[ThreadMetaRepository]\n  Session --> FeedbackRepo[FeedbackRepository]\n  Session --> UserRepo[User repository]\n  RunRepo --> RunRow\n  ThreadRepo --> ThreadMetaRow\n  FeedbackRepo --> FeedbackRow\n  EventStore[RunEventStore] --> RunEventRow\n  Gateway[Gateway routers] --> RunRepo\n  Gateway --> ThreadRepo\n  Gateway --> FeedbackRepo\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "P0iPdScRBooiWtxzMALmUoEGyNd",
      "revision_id": 17
    }
  }
}
