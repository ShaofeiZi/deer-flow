{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>17｜Model Provider Factory 与模型适配详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**把模型配置如何解析为 LangChain ChatModel，以及各 provider patch 的职责讲清楚。\n</callout>\n\n# 1. 模型配置到实例\n\n```mermaid\nflowchart TD\n  YAML[config.yaml models] --> ModelConfig[ModelConfig]\n  Request[run context model_name] --> Resolve[resolve requested or default model]\n  ModelConfig --> Factory[create_chat_model]\n  Factory --> Reflection[resolve_class use field]\n  Reflection --> Provider[LangChain provider class]\n  Provider --> Params[api_key base_url model max_tokens temperature]\n  Params --> Patch[provider-specific patch]\n  Patch --> ChatModel[BaseChatModel]\n  ChatModel --> Agent[lead_agent create_agent]\n```\n\n# 2. provider 类型\n\n| 文件 | 用途 |\n|-|-|\n| `models/factory.py` | 统一 create_chat_model 入口。 |\n| `models/credential_loader.py` | API key / credential 解析。 |\n| `models/patched_openai.py` | OpenAI 兼容行为 patch。 |\n| `models/patched_deepseek.py` | DeepSeek 特定适配。 |\n| `models/patched_minimax.py` | MiniMax 特定适配。 |\n| `models/claude_provider.py` | Claude provider 封装。 |\n| `models/vllm_provider.py` | vLLM provider。 |\n\n# 3. thinking / reasoning effort / vision\n\n`ModelConfig` 中的 `supports_thinking`、`supports_reasoning_effort`、`supports_vision` 会影响前端选择能力和后端 middleware，例如 vision 模型才会启用 ViewImageMiddleware。\n\n# 4. 常见问题\n\n- 模型下拉没有显示：检查 `GET /api/models` 是否返回。\n- thinking 开了但无效：检查模型配置 `supports_thinking`。\n- provider 参数不生效：检查 `use` 类路径和 reflection resolver。\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**模型工厂用 class path 动态创建 provider，是为了支持多模型生态。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是 provider 可扩展；代价是配置错误会在运行时暴露。 |\n| 代价 | 见收益说明中的代价部分；此章节采用收益与代价合并描述。 |\n| 重点代码 | 重点代码：`backend/packages/harness/deerflow/models/factory.py`、`backend/packages/harness/deerflow/reflection/resolvers.py`。 |\n| 阅读路径 | 阅读路径：ModelConfig.use 是字符串，resolver 把它变成类。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "GHiydyXRiof4QWxhlrcm8Y8MyAe",
      "revision_id": 14
    }
  }
}
