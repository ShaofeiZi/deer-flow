{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>169｜Backend Agent/Middleware Tests 分类详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆测试/CI/脚本模块，说明覆盖范围、运行入口和逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| lead_agent tests | 模型解析、prompt、skills。 |\n| middleware tests | clarification、loop、summary、todo、token usage 等。 |\n| task/subagent tests | task tool、executor、status contract。 |\n| tool tests | present_file、view_image、tool errors、output budget。 |\n\n```mermaid\nflowchart TD\n  AgentCode --> LeadTests[lead agent tests]\n  MiddlewareCode --> MWTests[middleware tests]\n  SubagentCode --> SubTests[subagent tests]\n  ToolsCode --> ToolTests[tool tests]\n  LeadTests --> Assertions\n  MWTests --> Assertions\n  SubTests --> Assertions\n  ToolTests --> Assertions\n  Assertions --> CI\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**该文档说明一个 public skill 或 skill 分类的目标、触发条件、执行链路和维护边界，方便新同学理解 DeerFlow 的可扩展能力。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | skill 能力被文档化后，使用者能快速判断何时触发、读哪些文件、如何验证输出。 |\n| 代价 | skill 文档容易和实际 `SKILL.md` 漂移，需要定期回到源码和示例验证。 |\n| 重点代码 | 对应 `skills/public/.../SKILL.md`、相关 `references/`、`templates/`、`scripts/`。 |\n| 阅读路径 | 先读 skill frontmatter 和触发场景，再读正文 workflow，最后检查 references/templates/scripts 是否支撑描述。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[解决的问题]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "FfXYdW7tYoKZFwxLhq5m6v5Oy9c",
      "revision_id": 18
    }
  }
}
