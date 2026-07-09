<title>146｜github-deep-research Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**围绕 GitHub repo/issues/PR 做深度研究。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `github-deep-research` |
| 路径 | `skills/public/github-deep-research/SKILL.md` |
| 类型 | github research |
| 触发方式 | 任务匹配或显式 `/github-deep-research` |

```mermaid
flowchart TD
  User[User task] --> Match[match github-deep-research]
  Match --> Read[read skills public github-deep-research SKILL md]
  Read --> Workflow[github research workflow]
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
  Trigger["/github-deep-research"] --> SKILL["SKILL.md frontmatter"]
  SKILL --> R1["Round 1 GitHub API"]
  SKILL --> R2["Rounds 2-4 web search"]
  R1 --> CLI["github_api.py main"]
  CLI --> Dispatch["command arg"]
  Dispatch -->|"summary"| Sum["summarize_repo"]
  Dispatch -->|"readme tree"| RT["get_readme get_tree"]
  Dispatch -->|"issues prs commits"| IPC["get_issues get_pull_requests get_recent_commits"]
  Sum --> Get["_get requests.get"]
  RT --> Get
  IPC --> Get
  Get --> API["api.github.com REST"]
  R2 --> WS["web_search web_fetch"]
  R1 --> Tpl["report_template.md"]
  R2 --> Tpl
  Tpl --> Out["research_topic_YYYYMMDD.md"]
```