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
  P1["Phase 1 Codebase Analysis"] --> S11["Project Discovery"]
  S11 --> S12["Code Structure Analysis"]
  S12 --> S13["Identify Doc Scope"]
  S13 --> P2["Phase 2 Doc Generation"]
  P2 --> S21["README Generation"]
  P2 --> S22["API Reference Generation"]
  P2 --> S23["Architecture Documentation"]
  P2 --> S24["Inline Code Documentation"]
  S21 --> P3["Phase 3 Quality Assurance"]
  S22 --> P3
  S23 --> P3
  S24 --> P3
  P3 --> Q1["Completeness Check"]
  Q1 --> Q2["Quality Standards"]
  Q2 --> Q3["Cross-reference Validation"]
  Q3 --> Out["Output Handling present_files"]
  Out --> Dir["mnt/user-data/outputs"]
```