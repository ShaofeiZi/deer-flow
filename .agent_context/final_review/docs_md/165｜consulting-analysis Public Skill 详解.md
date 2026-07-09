<title>165｜consulting-analysis Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**咨询分析和结构化洞察。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `consulting-analysis` |
| 路径 | `skills/public/consulting-analysis/SKILL.md` |
| 类型 | consulting analysis |
| 触发方式 | 任务匹配或显式 `/consulting-analysis` |

```mermaid
flowchart TD
  User[User task] --> Match[match consulting-analysis]
  Match --> Read[read skills public consulting-analysis SKILL md]
  Read --> Workflow[consulting analysis workflow]
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
  Sub["research subject"] --> P1["Phase 1 SKILL.md"]
  P1 --> Skel["chapter skeleton + frameworks"]
  Skel --> DR["data requirements P0 P1 P2"]
  DR --> VP["visualization plan"]
  VP --> AF["Analysis Framework"]
  AF --> Coll["deep-research data-analysis web search"]
  Coll --> DP["Data Package"]
  DP --> P2["Phase 2 SKILL.md"]
  AF --> P2
  P2 --> Chart["Step 2.3 chart generation"]
  Chart --> Write["Step 2.4 write narrative"]
  Write --> Report["final consulting report"]
  Report --> Ref["GB/T 7714 references"]
```