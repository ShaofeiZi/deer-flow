<title>161｜bootstrap Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**项目/agent 引导初始化 skill。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `bootstrap` |
| 路径 | `skills/public/bootstrap/SKILL.md` |
| 类型 | bootstrap |
| 触发方式 | 任务匹配或显式 `/bootstrap` |

```mermaid
flowchart TD
  User[User task] --> Match[match bootstrap]
  Match --> Read[read skills public bootstrap SKILL md]
  Read --> Workflow[bootstrap workflow]
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
    Trigger["trigger /bootstrap or SOUL missing"] --> ReadSkill["read SKILL.md"]
    ReadSkill --> ReadRefs["read references/conversation-guide.md"]
    ReadSkill --> ReadTpl["read templates/SOUL.template.md"]
    ReadRefs --> P1["Phase 1 Hello"]
    ReadTpl --> P1
    P1 --> P2["Phase 2 You"]
    P2 --> P3["Phase 3 Personality"]
    P3 --> P4["Phase 4 Depth"]
    P4 --> Tracker{"extraction tracker complete"}
    Tracker -- missing fields --> P2
    Tracker -- all required --> Gen["generate SOUL.md from template"]
    Gen --> Confirm{"user confirms"}
    Confirm -- iterate --> Gen
    Confirm -- confirmed --> CallTool["call setup_agent tool"]
    CallTool --> Persist["setup_agent writes SOUL.md + config.yaml"]
    Persist --> Done["agent continues as custom agent"]
```