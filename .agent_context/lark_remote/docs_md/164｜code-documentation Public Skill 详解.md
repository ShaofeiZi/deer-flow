<title>164｜code-documentation Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**代码文档化和讲解。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `code-documentation` |
| 路径 | `skills/public/code-documentation/SKILL.md` |
| 类型 | code documentation |
| 触发方式 | 任务匹配或显式 `/code-documentation` |

```mermaid
flowchart TD
  User[User task] --> Match[match code-documentation]
  Match --> Read[read skills public code-documentation SKILL md]
  Read --> Workflow[code documentation workflow]
  Workflow --> Scripts[use bundled scripts if present]
  Scripts --> Output[deliver artifact or answer]
  Output --> Agent[agent continues]
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