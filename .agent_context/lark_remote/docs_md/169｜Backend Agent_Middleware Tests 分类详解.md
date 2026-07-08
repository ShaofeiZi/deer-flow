<title>169｜Backend Agent/Middleware Tests 分类详解</title>

<callout emoji="✅">
**本章目标：**继续拆测试/CI/脚本模块，说明覆盖范围、运行入口和逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| lead_agent tests | 模型解析、prompt、skills。 |
| middleware tests | clarification、loop、summary、todo、token usage 等。 |
| task/subagent tests | task tool、executor、status contract。 |
| tool tests | present_file、view_image、tool errors、output budget。 |

```mermaid
flowchart TD
  AgentCode --> LeadTests[lead agent tests]
  MiddlewareCode --> MWTests[middleware tests]
  SubagentCode --> SubTests[subagent tests]
  ToolsCode --> ToolTests[tool tests]
  LeadTests --> Assertions
  MWTests --> Assertions
  SubTests --> Assertions
  ToolTests --> Assertions
  Assertions --> CI
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块承担 agent 扩展能力，是为了把工具、知识、长期上下文或执行环境做成可组合部件。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是可扩展、可配置、可替换。 |
| 代价 | 代价是配置、prompt、工具 schema、外部服务任一环节出错都会影响结果。 |
| 重点代码 | 重点代码在 `backend/packages/harness/deerflow` 下对应 skills/mcp/memory/sandbox/tools/models 模块。 |
| 阅读路径 | 阅读路径：明确它给 agent 增加了什么能力，以及该能力在哪里被注入。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```