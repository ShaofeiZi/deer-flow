<title>138｜Public Skills 分类与运行逻辑详解</title>

<callout emoji="✅">
**本章目标：**补齐测试、脚本、Docker、Skills 分类，解释运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| Research | deep-research、github-deep-research、academic-paper-review、systematic-literature-review。 |
| Generation | image/music/video/podcast/ppt/newsletter。 |
| Development | frontend-design、code-documentation、vercel-deploy、claude-to-deerflow。 |
| Analysis | data-analysis、consulting-analysis、chart-visualization。 |
| Meta | skill-creator、find-skills、bootstrap、surprise-me。 |

## 补充：Public Skills 分类简化运行图

```mermaid
flowchart TD
  A[skills public] --> B[Skill parser]
  B --> C[Research skills]
  B --> D[Generation skills]
  B --> E[Development skills]
  B --> F[Analysis skills]
  B --> G[Meta skills]
  H[enabled state] --> I[Prompt metadata]
  J[user slash skill] --> K[SkillActivationMiddleware]
  K --> L[Read full SKILL md]
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
sequenceDiagram
    participant User
    participant SAMW as SkillActivationMiddleware
    participant Slash as slash.py
    participant Store as SkillStorage
    participant Parser as parser.py
    participant Ext as ExtensionsConfig
    participant File as SKILL.md
    User->>SAMW: turn starts with /skill-name task
    SAMW->>Slash: parse_slash_skill_reference text
    Slash-->>SAMW: SlashSkillReference name plus remaining text
    SAMW->>Store: load_skills enabled_only false
    Store->>Parser: parse_skill_file md_path
    Parser->>Parser: read YAML frontmatter
    Parser-->>Store: Skill name description allowed-tools
    Store->>Ext: is_skill_enabled name category
    Ext-->>Store: enabled bool
    Store-->>SAMW: skills list with enabled state
    alt skill disabled or not available
        SAMW-->>User: AIMessage failure_message
    else enabled and whitelisted
        SAMW->>Store: resolve_slash_skill text skills
        SAMW->>File: _read_skill_content validated path
        File-->>SAMW: skill content sha256 hash
        SAMW->>SAMW: _build_activation_reminder XML
        SAMW->>User: insert hidden HumanMessage at target
        SAMW->>SAMW: request.override messages
    end
    SAMW->>SAMW: handler prepared request
```