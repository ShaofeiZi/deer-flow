<title>205｜MiniMax Generation Providers Specs/Plans 详解</title>

<callout emoji="✅">
**本章目标：**继续拆单测试族、单规格文档和根文档模块。
</callout>

| 模块点 | 说明 |
|-|-|
| 2026-06-08-minimax-generation-providers-design.md | MiniMax 生成 provider 设计。 |
| 2026-06-08-minimax-generation-providers.md | 实施计划。 |
| 目标 | 补充 image/music/video/podcast generation provider。 |
| 验证 | skills generation tests 与 provider tests。 |

```mermaid
flowchart TD
  Requirement[MiniMax generation providers] --> Spec[design spec]
  Spec --> Plan[implementation plan]
  Plan --> Providers[provider implementation]
  Providers --> Skills[media generation skills]
  Skills --> Tests[generation skill tests]
  Tests --> Release
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
flowchart LR
  ENV["env: SKILL_PROVIDER / creds"] --> RES["_resolve_provider"]
  RES -->|override or existing creds| GEN["existing provider path"]
  RES -->|MINIMAX_API_KEY fallback| MM["MiniMax branch"]

  GEN --> IMG["generate_image to gemini"]
  GEN --> VID["generate_video to veo"]
  GEN --> POD["tts_node to volcengine"]

  MM --> IMGMM["_generate_image_minimax"]
  MM --> VIDMM["_generate_video_minimax"]
  MM --> PODMM["text_to_speech_minimax"]
  MM --> MUS["generate_music"]

  IMGMM -->|"POST /v1/image_generation"| BASE["base_resp check + base64 write"]
  VIDMM --> POLL["_poll_video_task to /v1/query/video_generation"]
  POLL --> RETR["_retrieve_file_url to /v1/files/retrieve"]
  RETR --> DL["_download mp4"]
  PODMM -->|"POST /v1/t2a_v2"| HEX["bytes.fromhex to mp3"]
  MUS -->|"POST /v1/music_generation"| HEX

  BASE --> OUT["output_file"]
  DL --> OUT
  HEX --> OUT
```