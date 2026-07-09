<title>150｜web-design-guidelines Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**网页设计规范和审美指导。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `web-design-guidelines` |
| 路径 | `skills/public/web-design-guidelines/SKILL.md` |
| 类型 | design guideline |
| 触发方式 | 任务匹配或显式 `/web-design-guidelines` |

```mermaid
flowchart TD
  User[User task] --> Match[match web-design-guidelines]
  Match --> Read[read skills public web-design-guidelines SKILL md]
  Read --> Workflow[design guideline workflow]
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
sequenceDiagram
    participant U as User
    participant M as SkillActivationMiddleware
    participant P as slash.py
    participant S as SkillStorage
    participant A as Agent

    U->>M: HumanMessage slash web-design-guidelines app.tsx
    M->>M: _find_activation_target scans messages
    M->>P: parse_slash_skill_reference text
    P-->>M: SlashSkillReference name and remaining_text
    M->>S: load_skills enabled_only false
    S->>S: _iter_skill_files parse_skill_file SKILL.md
    S-->>M: Skill list with enabled state
    M->>P: resolve_slash_skill name skills
    P-->>M: ResolvedSlashSkill container_file_path
    M->>M: _read_skill_content sha256 hash
    M->>M: _build_activation_reminder XML skill_content
    M->>M: insert hidden HumanMessage before target
    M->>A: override messages then handler
    A-->>U: terse file-line findings
```