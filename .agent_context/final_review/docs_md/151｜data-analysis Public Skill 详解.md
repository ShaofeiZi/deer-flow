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
  Start["analyze.py main"] --> Parse["argparse --files --action"]
  Parse --> Hash["compute_files_hash SHA256"]
  Hash --> Cache{"load_table_map hit"}
  Cache -- "hit" --> RO["duckdb.connect read_only"]
  Cache -- "miss" --> RW["duckdb.connect read_write"]
  RW --> Load["load_files then save_table_map"]
  RO --> Action{"args.action"}
  Load --> Action
  Action -- "inspect" --> Inspect["action_inspect schema sample"]
  Action -- "query" --> Query["action_query"]
  Action -- "summary" --> Summary["action_summary stats"]
  Query --> Out{"--output-file"}
  Out -- "set" --> Exp["_export_results csv json md"]
  Out -- "none" --> Fmt["_format_table"]
  Inspect --> Done["con.close"]
  Summary --> Done
  Exp --> Done
  Fmt --> Done
```