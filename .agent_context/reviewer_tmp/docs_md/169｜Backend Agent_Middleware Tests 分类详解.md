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
**设计目的：**该文档说明一个 public skill 或 skill 分类的目标、触发条件、执行链路和维护边界，方便新同学理解 DeerFlow 的可扩展能力。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | skill 能力被文档化后，使用者能快速判断何时触发、读哪些文件、如何验证输出。 |
| 代价 | skill 文档容易和实际 `SKILL.md` 漂移，需要定期回到源码和示例验证。 |
| 重点代码 | 对应 `skills/public/.../SKILL.md`、相关 `references/`、`templates/`、`scripts/`。 |
| 阅读路径 | 先读 skill frontmatter 和触发场景，再读正文 workflow，最后检查 references/templates/scripts 是否支撑描述。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```