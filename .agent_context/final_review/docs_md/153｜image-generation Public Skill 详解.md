<title>153｜image-generation Public Skill 详解</title>

<callout emoji="✅">
**Skill 目标：**图片生成与模板化 prompt。
</callout>

| 字段 | 说明 |
|-|-|
| Skill 名称 | `image-generation` |
| 路径 | `skills/public/image-generation/SKILL.md` |
| 类型 | image generation |
| 触发方式 | 任务匹配或显式 `/image-generation` |

```mermaid
flowchart TD
  User[User task] --> Match[match image-generation]
  Match --> Read[read skills public image-generation SKILL md]
  Read --> Workflow[image generation workflow]
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
flowchart TD
  Read["read prompt_file"] --> Resolve["_resolve_provider"]
  Resolve --> Decide{"provider selected"}
  Decide -- "gemini" --> Gemini["_generate_image_gemini"]
  Decide -- "minimax" --> MiniMax["_generate_image_minimax"]
  Decide -- "unknown" --> Err["raise ValueError"]
  Gemini --> GVal["validate_image per ref"]
  GVal --> GApi["POST gemini generateContent"]
  GApi --> GDecode["decode inlineData"]
  MiniMax --> MCheck["prompt under 1500 chars"]
  MCheck --> MApi["POST v1 image_generation"]
  MApi --> MDecode["decode image_base64"]
  GDecode --> OutDir["_ensure_output_dir"]
  MDecode --> OutDir
  OutDir --> Write["write output_file"]
  Write --> Done["return success"]
```