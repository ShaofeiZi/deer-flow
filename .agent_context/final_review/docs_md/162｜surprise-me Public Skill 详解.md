<title>162｜surprise-me Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**探索式 surprise 任务流程。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `surprise-me` |
| 路径 | `skills/public/surprise-me/SKILL.md` |
| 类型 | exploratory |
| 触发方式 | 任务匹配或显式 `/surprise-me` |

```mermaid
flowchart TD
  User[User task] --> Match[match surprise-me]
  Match --> Read[read skills public surprise-me SKILL md]
  Read --> Workflow[exploratory workflow]
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
sequenceDiagram
    participant U as User
    participant M as SkillActivationMiddleware
    participant S as slash.py
    participant ST as SkillStorage
    participant SM as surprise-me SKILL.md
    participant L as LeadAgent model

    U->>M: "/surprise-me" turn text
    M->>S: parse_slash_skill_reference
    S-->>M: name surprise-me
    M->>ST: load_skills enabled_only false
    ST-->>M: matched Skill enabled
    M->>S: resolve_slash_skill
    S-->>M: container path /mnt/skills/public/surprise-me
    M->>SM: _read_skill_content SKILL.md
    SM-->>M: full skill body
    M->>M: build slash_skill_activation reminder
    M->>L: insert activation HumanMessage before turn
    L->>L: Step1 discover available_skills
    L->>L: Step2 plan 1-3 skill mashup
    L->>L: Step3 fallback if no skills
    L->>L: Step4 execute selected skills
    L->>U: Step5 reveal single cohesive artifact
```