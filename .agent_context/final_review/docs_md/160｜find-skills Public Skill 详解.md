<title>160｜find-skills Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**发现和安装适合任务的 skills。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `find-skills` |
| 路径 | `skills/public/find-skills/SKILL.md` |
| 类型 | skill discovery |
| 触发方式 | 任务匹配或显式 `/find-skills` |

```mermaid
flowchart TD
  User[User task] --> Match[match find-skills]
  Match --> Read[read skills public find-skills SKILL md]
  Read --> Workflow[skill discovery workflow]
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
  U["User asks find a skill for X"] --> A["Agent matches find-skills"]
  A --> R["Read SKILL.md frontmatter"]
  R --> Q["npx skills find query"]
  Q --> S["skills.sh registry results"]
  S --> P["Present options and install cmd"]
  P --> C{"User confirms?"}
  C -->|yes| I["install-skill.sh owner/repo@name"]
  I --> F["find_project_root deer-flow.code-workspace"]
  F --> N["npx skills add -g"]
  N --> H["~/.agents/skills/name"]
  H --> V{"dir exists?"}
  V -->|yes| L["ln -sf into skills/custom"]
  L --> D["Skill linked in project"]
  C -->|no| G["Help directly or npx skills init"]
```