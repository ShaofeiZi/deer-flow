<title>159｜newsletter-generation Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**Newsletter 生成流程。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `newsletter-generation` |
| 路径 | `skills/public/newsletter-generation/SKILL.md` |
| 类型 | newsletter generation |
| 触发方式 | 任务匹配或显式 `/newsletter-generation` |

```mermaid
flowchart TD
  User[User task] --> Match[match newsletter-generation]
  Match --> Read[read skills public newsletter-generation SKILL md]
  Read --> Workflow[newsletter generation workflow]
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
  Plan["Phase 1 Planning - requirements and structure"]
  Plan --> Research["Step 2.1 Multi-Source Web Search"]
  Research --> Evaluate["Step 2.2 Source Evaluation"]
  Evaluate --> Extract["Step 2.3 Deep Extraction via web_fetch"]
  Extract --> Write["Phase 3 Writing - header sections standards"]
  Write --> Assemble["Step 4.1 Assemble Newsletter"]
  Assemble --> Footer["Step 4.2 Add Footer"]
  Footer --> Checklist["Step 4.3 Quality Checklist"]
  Checklist --> Save["Save newsletter-topic-date.md"]
  Save --> Present["present_files tool"]
  Present --> Refine["Offer tone or length adjustments"]
```