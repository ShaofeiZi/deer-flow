<title>233｜MiniMax Provider Spec/Plan 单文件详解</title>

<callout emoji="✅">
**本章目标：**继续细化 content/spec/docs 单模块，补充运行/维护逻辑图。
</callout>

| 模块点 | 说明 |
|-|-|
| spec | 2026-06-08-minimax-generation-providers-design.md。 |
| plan | 2026-06-08-minimax-generation-providers.md。 |
| 目标 | 接入 MiniMax generation providers。 |
| 关联 | media generation skills。 |

```mermaid
flowchart TD
  MiniMaxNeed --> Spec
  Spec --> ProviderDesign
  ProviderDesign --> Plan
  Plan --> ImplementProviders
  ImplementProviders --> MediaSkills
  MediaSkills --> GenerationTests
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块用于固化工程流程、质量门禁或设计背景，是为了让行为可复现、可审计。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是降低回归风险，帮助新人理解历史决策。 |
| 代价 | 代价是容易与代码实现漂移，需要持续维护。 |
| 重点代码 | 重点代码/资料是对应 tests、scripts、workflow、docs 文件及其调用的源码入口。 |
| 阅读路径 | 阅读路径：按输入、执行步骤、输出证据三段看。 |

```mermaid
flowchart TD
  Entry["generate_image / generate_video / generate_podcast"]
  Entry --> Resolve["_resolve_provider"]
  Resolve -->|"SKILL_PROVIDER set"| Force["override wins"]
  Resolve -->|"existing creds present"| Legacy["gemini or volcengine"]
  Resolve -->|"only MINIMAX_API_KEY"| MM["minimax"]
  Resolve -->|"no creds"| Err["ValueError"]
  MM --> Img["POST /v1/image_generation"]
  MM --> Vid["POST /v1/video_generation"]
  MM --> Pod["POST /v1/t2a_v2"]
  MusEntry["generate_music minimax only"] --> Mus["POST /v1/music_generation"]
  Img --> ImgDec["base64 decode image_base64"]
  Pod --> HexDec["hex decode data.audio"]
  Mus --> HexDec
  Vid --> Poll["_poll_video_task /v1/query then /v1/files/retrieve"]
  Poll --> DL["download mp4"]
  ImgDec --> Write["write output file"]
  HexDec --> Write
  DL --> Write
```