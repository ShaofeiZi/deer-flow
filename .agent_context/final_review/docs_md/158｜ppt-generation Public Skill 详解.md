<title>158｜ppt-generation Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**PPT 生成流程。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `ppt-generation` |
| 路径 | `skills/public/ppt-generation/SKILL.md` |
| 类型 | presentation generation |
| 触发方式 | 任务匹配或显式 `/ppt-generation` |

```mermaid
flowchart TD
  User[User task] --> Match[match ppt-generation]
  Match --> Read[read skills public ppt-generation SKILL md]
  Read --> Workflow[presentation generation workflow]
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
  A["SKILL.md frontmatter match"] --> B["plan JSON write"]
  B --> C["slide-01 prompt JSON"]
  C --> D["image-generation generate.py"]
  D --> E["_resolve_provider picks gemini or minimax"]
  E --> F["slide-01.jpg"]
  F --> G["slide-02 prompt references slide-01"]
  G --> D
  F --> H["slide-02.jpg"]
  H --> I["repeat per slide sequential"]
  I --> J["ppt-generation generate.py generate_ppt"]
  J --> K["python-pptx Presentation blank layout"]
  K --> L["add_picture fit aspect ratio"]
  L --> M["notes_slide add title and key_points"]
  M --> N["save presentation.pptx"]
```