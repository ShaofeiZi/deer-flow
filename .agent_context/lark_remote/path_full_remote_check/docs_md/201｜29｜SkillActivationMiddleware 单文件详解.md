{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>29｜SkillActivationMiddleware 单文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲清 /skill-name 显式激活如何解析、定位、读取并注入完整 SKILL.md。\n</callout>\n\n## 本轮源码校准补充：SkillActivationMiddleware\n\n| 行为 | 说明 |\n|-|-|\n| 激活方式 | 严格匹配 `/skill-name task` 形式的最新真实用户消息。 |\n| 内容来源 | 从可信 skill storage 读取 `SKILL.md`，作为 hidden/current-turn model context 注入。 |\n| 工具限制 | 如果被激活 skill 声明 `allowed-tools`，会参与工具过滤策略。 |\n| 审计 | 记录 skill name、category、path、content hash 等 audit 信息。 |\n\n| 步骤 | 说明 |\n|-|-|\n| 解析 | 识别最后一条用户消息开头的 slash skill。 |\n| 解析路径 | 根据 available_skills 和 skill storage 定位 SKILL.md。 |\n| 读取 | 读取完整技能说明和必要元数据。 |\n| 注入 | 添加隐藏 reminder，让模型本轮遵循该 skill。 |\n\n```mermaid\nflowchart TD\n  User[HumanMessage starts with slash] --> Parse[parse_slash_skill_reference]\n  Parse --> Allowed{skill in available set?}\n  Allowed -->|no| Skip[no activation]\n  Allowed -->|yes| Resolve[resolve skill path]\n  Resolve --> Read[read SKILL.md]\n  Read --> Reminder[build slash skill activation reminder]\n  Reminder --> Messages[inject hidden context]\n  Messages --> Model[model follows skill workflow]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块采用 middleware 形态，是为了把横切能力从主 agent 逻辑里剥离出来，并按 LangChain/LangGraph 生命周期挂载。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是可插拔、可独立测试、能按 before/after/wrap 阶段控制行为。 |\n| 代价 | 代价是执行顺序不直观，多个 middleware 同时改 messages/state 时调试成本较高。 |\n| 重点代码 | 重点代码通常在 `backend/packages/harness/deerflow/agents/middlewares/`，先看 class 的 hook 方法。 |\n| 阅读路径 | 阅读路径：先判断它在哪个 hook 生效，再看它读写 ThreadState 的哪些字段。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Wqntdu46NobRZ6xXj1Jm07u2y3c",
      "revision_id": 17
    }
  }
}
