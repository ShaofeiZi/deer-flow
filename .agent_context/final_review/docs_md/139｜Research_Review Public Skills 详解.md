<title>139｜Research/Review Public Skills 详解</title>

<callout emoji="✅">
**本章目标：**把 public skills 按能力组拆开，说明触发场景、工作流和运行逻辑。
</callout>

| Skill | 职责 |
|-|-|
| `deep-research` | 通用深度研究工作流。 |
| `github-deep-research` | GitHub 仓库/议题深度研究。 |
| `academic-paper-review` | 学术论文审阅。 |
| `systematic-literature-review` | 系统文献综述。 |

```mermaid
flowchart TD
  User[User task] --> Match[Skill relevance or slash command]
  Match --> Load[read SKILL md]
  Load --> Plan[research and review workflow]
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
flowchart TD
    U["User task"] --> R{"Intent routing"}
    R -->|"web research"| DR["deep-research SKILL.md"]
    R -->|"GitHub repo URL"| GH["github-deep-research SKILL.md"]
    R -->|"single paper review"| AP["academic-paper-review SKILL.md"]
    R -->|"multi-paper SLR"| SL["systematic-literature-review SKILL.md"]

    DR --> WS["web_search + web_fetch"]
    DR --> SYN1["4-phase synthesis"]

    GH --> GA["scripts/github_api.py"]
    GA --> GHAPI["GitHubAPI class"]
    GHAPI --> RT["assets/report_template.md"]
    GH --> WF1["web_search + web_fetch"]

    AP --> PDF["PDF / arXiv URL parse"]
    PDF --> MA["methodology + contribution assessment"]
    MA --> LIT["literature context search"]
    AP --> PF1["present_files"]

    SL --> ARX["scripts/arxiv_search.py"]
    ARX --> ATOM["Atom XML parse + id normalise"]
    ATOM --> TASK["task tool subagents max 3"]
    TASK --> BATCH["batch of 5 papers"]
    BATCH --> TPL["templates apa ieee bibtex"]
    TPL --> PF2["present_files slr file"]

    SYN1 --> OUT["Markdown artifact"]
    RT --> OUT
    LIT --> OUT
    PF2 --> OUT
```