<title>152｜chart-visualization Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**图表可视化生成与解释。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `chart-visualization` |
| 路径 | `skills/public/chart-visualization/SKILL.md` |
| 类型 | chart visualization |
| 触发方式 | 任务匹配或显式 `/chart-visualization` |

```mermaid
flowchart TD
  User[User task] --> Match[match chart-visualization]
  Match --> Read[read skills public chart-visualization SKILL md]
  Read --> Workflow[chart visualization workflow]
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
  A["SKILL.md workflow"] --> B["Step1 chart selection"]
  B --> C{"data feature"}
  C -->|"time series"| D1["generate_line_chart"]
  C -->|"comparison"| D2["generate_bar_chart"]
  C -->|"map"| D3["generate_district_map"]
  C -->|"other 23 tools"| D4["generate_*_chart"]
  D1 --> E["Step2 read references/tool.md"]
  D2 --> E
  D3 --> E
  D4 --> E
  E --> F["build args payload"]
  F --> G["node scripts/generate.js"]
  G --> H["main parse spec"]
  H --> I["CHART_TYPE_MAP tool lookup"]
  I --> J{"isMapChartTool"}
  J -->|"no"| K["generateChartUrl"]
  J -->|"yes"| L["generateMap + SERVICE_ID"]
  K --> M["httpPost gpt-vis"]
  L --> M
  M --> N["data.resultObj"]
  N --> O["return image URL and args"]
```