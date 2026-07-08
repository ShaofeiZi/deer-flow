<title>151｜data-analysis Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**数据读取、分析、可视化和报告。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `data-analysis` |
| 路径 | `skills/public/data-analysis/SKILL.md` |
| 类型 | data analysis |
| 触发方式 | 任务匹配或显式 `/data-analysis` |

```mermaid
flowchart TD
  User[User task] --> Match[match data-analysis]
  Match --> Read[read skills public data-analysis SKILL md]
  Read --> Workflow[data analysis workflow]
  Workflow --> Tools[use scripts/tools if needed]
  Tools --> Output[deliver result]
  Output --> Memory[agent may continue or summarize]
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