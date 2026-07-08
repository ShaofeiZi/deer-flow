{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 95｜Patched Model Providers 深入详解\n\n<callout emoji=\"✅\">\n**本章目标：**继续拆 patched providers，说明不同模型兼容处理的必要性。\n</callout>\n\n## 本轮源码校准补充：Patched Model Providers\n\n| Provider 类型 | 关注点 |\n|-|-|\n| OpenAI-compatible / Responses | base_url、api_key、output_version、tool calling、vision/reasoning 支持。 |\n| Codex / Claude CLI-backed | 依赖本机 CLI auth/config，适合本地开发或受控环境。 |\n| vLLM / MindIE / DeepSeek / MiniMax 等 patched provider | 重点关注非标准 thinking/reasoning 字段、tool-call 兼容和 streaming 差异。 |\n| Replay / seed provider | 用于测试和回放，不应误认为真实线上模型能力。 |\n\n<callout emoji=\"💡\">\n模型配置调试时不要只看前端下拉框；要同时检查 `config.yaml`、provider factory、模型能力标记、后端错误处理 middleware 和前端提交 context。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| patched_openai | OpenAI 兼容 API 参数、responses API 等适配。 |\n| patched_deepseek | DeepSeek 特殊输出或参数兼容。 |\n| patched_minimax | MiniMax think block/reasoning 兼容。 |\n| patched_mimo/stepfun | 其他 provider 兼容层。 |\n| assistant_payload_replay | 回放模型 payload 用于测试/诊断。 |\n\n```mermaid\nflowchart TD\n  ModelConfig --> Factory[create_chat_model]\n  Factory --> Provider{provider class}\n  Provider --> OpenAI[patched_openai]\n  Provider --> DeepSeek[patched_deepseek]\n  Provider --> MiniMax[patched_minimax]\n  Provider --> Others[patched_mimo stepfun]\n  Provider --> Replay[assistant_payload_replay]\n  OpenAI --> ChatModel\n  DeepSeek --> ChatModel\n  MiniMax --> ChatModel\n  Others --> ChatModel\n  Replay --> Tests[diagnosis tests]\n```",
      "document_id": "WHTodguJQoLMdLxHrN4mQbruy0f",
      "revision_id": 27
    }
  }
}
