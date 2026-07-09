<title>143｜Meta/Bootstrap Public Skills 详解</title>

<callout emoji="✅">
**本章目标：**把 public skills 按能力组拆开，说明触发场景、工作流和运行逻辑。
</callout>

| Skill | 职责 |
|-|-|
| `bootstrap` | 引导初始化。 |
| `skill-creator` | 创建 skill。 |
| `find-skills` | 发现/安装 skills。 |

```mermaid
flowchart TD
  User[User task] --> Match[Skill relevance or slash command]
  Match --> Load[read SKILL md]
  Load --> Plan[meta skill management workflow]
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
    Req["user request"]
    Req --> Bootstrap["bootstrap SKILL.md"]
    Req --> Find["find-skills SKILL.md"]
    Req --> Creator["skill-creator SKILL.md"]

    Bootstrap --> ReadGuide["references/conversation-guide.md"]
    Bootstrap --> ReadTpl["templates/SOUL.template.md"]
    ReadGuide --> Phases["Hello You Personality Depth phases"]
    Phases --> Gen["generate SOUL.md"]
    Gen --> SetupAgent["setup_agent tool persists SOUL.md"]

    Find --> NpxFind["npx skills find query"]
    NpxFind --> InstallSh["scripts/install-skill.sh"]
    InstallSh --> NpxAdd["npx skills add owner/repo@skill"]
    NpxAdd --> CustomDir["skills/custom symlink"]

    Creator --> Draft["write SKILL.md draft"]
    Draft --> Runs["spawn with-skill and baseline runs"]
    Runs --> Grader["agents/grader.md"]
    Grader --> Agg["scripts/aggregate_benchmark.py"]
    Agg --> Viewer["eval-viewer/generate_review.py"]
    Viewer --> Loop["scripts/run_loop.py optimize description"]
    Loop --> Package["scripts/package_skill.py"]
```