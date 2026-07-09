<title>142｜Analysis/Consulting Public Skills 详解</title>

<callout emoji="✅">
**本章目标：**把 public skills 按能力组拆开，说明触发场景、工作流和运行逻辑。
</callout>

| Skill | 职责 |
|-|-|
| `data-analysis` | 数据分析。 |
| `consulting-analysis` | 咨询分析。 |
| `chart-visualization` | 图表可视化。 |
| `surprise-me` | 探索式 surprise 任务。 |

```mermaid
flowchart TD
  User[User task] --> Match[Skill relevance or slash command]
  Match --> Load[read SKILL md]
  Load --> Plan[analysis workflow]
  Plan --> Tools[use allowed tools or scripts]
  Tools --> Output[deliver artifact or answer]
  Output --> Agent[agent continues conversation]
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
flowchart LR
  SM["surprise-me SKILL.md"] -->|"discover skills"| CA1["consulting-analysis Phase 1"]
  CA1 -->|"data requirements"| DA["analyze.py"]
  DA --> INS["action inspect"]
  DA --> QRY["action query"]
  DA --> SUM["action summary"]
  DA -.->|"SHA256 cache"| DDB["DuckDB cache"]
  INS --> DS["Data Summary"]
  QRY --> DS
  SUM --> DS
  CA1 -->|"viz plan"| CV["generate.js"]
  CV --> REF["references specs"]
  CV -->|"HTTP POST"| GV["gpt-vis"]
  GV --> URL["chart image URL"]
  DS --> PKG["Data Package"]
  URL --> PKG
  PKG --> CA2["consulting-analysis Phase 2"]
  CA2 --> RPT["final report MD"]
```