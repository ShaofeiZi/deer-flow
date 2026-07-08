{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>63｜feedback、suggestions、channels Router 详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清反馈、跟进建议和 IM channel 管理这些辅助 router。\n</callout>\n\n# 1. 模块职责\n\n| 对象 | 说明 |\n|-|-|\n| `backend/app/gateway/routers/feedback.py` | run feedback CRUD、upsert、stats。 |\n| `backend/app/gateway/routers/suggestions.py` | 根据最近对话生成 follow-up suggestions。 |\n| `backend/app/gateway/routers/channels.py` | 查询/重启 IM channel service。 |\n| `feedback stats` | 按 run 汇总反馈。 |\n| `think block strip` | suggestions 解析前剥离 reasoning <think>。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  FeedbackUI[Feedback UI] --> FeedbackRouter[backend/app/gateway/routers/feedback.py]\n  FeedbackRouter --> Repo[FeedbackRepository]\n  ChatUI[Chat UI] --> Suggest[backend/app/gateway/routers/suggestions.py]\n  Suggest --> Strip[strip think blocks]\n  Strip --> Model[LLM generate JSON list]\n  Model --> Parse[parse suggestions]\n  Admin[Admin UI] --> Channels[backend/app/gateway/routers/channels.py]\n  Channels --> Service[channel service status restart]\n```\n\n# 3. 排障与修改建议\n\n- 先确认调用方和数据源，再改 schema。\n- 涉及用户数据必须确认鉴权和 owner check。\n- 涉及缓存需要同步 invalidate 或 reset。\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "EemWdDNmiovWWlxz6Y3mqSt7y6e",
      "revision_id": 19
    }
  }
}
