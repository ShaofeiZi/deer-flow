<title>157｜podcast-generation Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**播客生成流程。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `podcast-generation` |
| 路径 | `skills/public/podcast-generation/SKILL.md` |
| 类型 | podcast generation |
| 触发方式 | 任务匹配或显式 `/podcast-generation` |

```mermaid
flowchart TD
  User[User task] --> Match[match podcast-generation]
  Match --> Read[read skills public podcast-generation SKILL md]
  Read --> Workflow[podcast generation workflow]
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
  CLI["generate.py CLI"]
  GP["generate_podcast"]
  LOAD["Script.from_dict"]
  MD["generate_markdown"]
  TN["tts_node"]
  PROV["_resolve_tts_provider"]
  WORK["_default_max_workers"]
  POOL["ThreadPoolExecutor _process_line"]
  VOLC["text_to_speech_volcengine"]
  MM["text_to_speech_minimax"]
  RTY["_backoff_sleep retry"]
  MIX["mix_audio"]
  OUT["output MP3 and transcript"]

  CLI --> GP
  GP --> LOAD
  LOAD --> MD
  LOAD --> TN
  TN --> PROV
  PROV --> WORK
  WORK --> POOL
  POOL --> VOLC
  POOL --> MM
  VOLC -.transient error.-> RTY
  MM -.transient error.-> RTY
  RTY -.backoff retry.-> VOLC
  RTY -.backoff retry.-> MM
  VOLC --> MIX
  MM --> MIX
  MIX --> OUT
  MD --> OUT
```