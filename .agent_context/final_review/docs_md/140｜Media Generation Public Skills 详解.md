<title>140｜Media Generation Public Skills 详解</title>

<callout emoji="✅">
**本章目标：**把 public skills 按能力组拆开，说明触发场景、工作流和运行逻辑。
</callout>

| Skill | 职责 |
|-|-|
| `image-generation` | 图片生成。 |
| `music-generation` | 音乐生成。 |
| `video-generation` | 视频生成。 |
| `podcast-generation` | 播客生成。 |
| `ppt-generation` | PPT 生成。 |
| `newsletter-generation` | newsletter 生成。 |

```mermaid
flowchart TD
  User[User task] --> Match[Skill relevance or slash command]
  Match --> Load[read SKILL md]
  Load --> Plan[media generation workflow]
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
  A["generate.py entry"] --> B["read prompt-file JSON"]
  B --> C["_resolve_provider"]
  C --> D{"SKILL_PROVIDER env"}
  D -- yes --> E["forced provider"]
  D -- no --> F{"existing creds"}
  F -- yes --> G["default provider"]
  F -- no --> H{"MINIMAX_API_KEY"}
  H -- yes --> I["minimax fallback"]
  H -- no --> J["raise ValueError"]
  E --> K{"dispatch"}
  G --> K
  I --> K
  K -- gemini --> L["Gemini API"]
  K -- minimax --> M["MiniMax API"]
  K -- volcengine --> N["Volcengine TTS"]
  L --> O["write output-file"]
  M --> O
  N --> O
```