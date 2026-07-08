{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>62｜agents.py Router 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**讲清 custom agents API、agent config/SOUL 读写和用户 profile。\n</callout>\n\n# 1. 模块职责\n\n| 对象 | 说明 |\n|-|-|\n| `list_agents` | 列出自定义 agent。 |\n| `check_agent_name` | 校验名称合法性和冲突。 |\n| `create_agent_endpoint` | 创建 agent config 和 SOUL。 |\n| `update_agent/delete_agent` | 更新/删除自定义 agent。 |\n| `user_profile` | 读取和更新用户 profile。 |\n\n# 2. 运行逻辑图\n\n```mermaid\nflowchart TD\n  UI[Agent Gallery] --> API[agents.py]\n  API --> Enabled{agents api enabled?}\n  Enabled --> Name[validate and normalize name]\n  Name --> Dir[resolve agent dir per user]\n  Dir --> Config[AGENT config]\n  Dir --> Soul[SOUL md]\n  Config --> Response[AgentResponse]\n  Soul --> Response\n  Update[update/delete] --> Dir\n```\n\n# 3. 排障与修改建议\n\n- 先确认调用方和数据源，再改 schema。\n- 涉及用户数据必须确认鉴权和 owner check。\n- 涉及缓存需要同步 invalidate 或 reset。\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档用于把模块职责、运行逻辑、关键代码和阅读路径固定下来，帮助读者从源码验证行为。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 读者可以按文档快速定位模块入口和上下游关系。 |\n| 代价 | 文档需要随源码变更持续校准，避免模板化描述掩盖真实行为。 |\n| 重点代码 | 标题对应的源码、测试或文档入口。 |\n| 阅读路径 | 先看上游输入，再看核心函数，最后看下游输出和测试验证。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "FgmQddXpfogJd2xoPJUmcxubytf",
      "revision_id": 17
    }
  }
}
