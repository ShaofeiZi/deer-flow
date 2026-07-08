{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>45｜Models Provider Patch 文件详解</title>\n\n<callout emoji=\"✅\">\n**本章目标：**把 models 包下 provider patch 文件逐一说明，帮助定位模型兼容问题。\n</callout>\n\n| 文件 | 职责 |\n|-|-|\n| `factory.py` | 统一 create_chat_model，解析 ModelConfig 和 class path。 |\n| `credential_loader.py` | 解析 API key、credential、环境变量引用。 |\n| `patched_openai.py` | OpenAI 兼容 provider patch。 |\n| `patched_deepseek.py` | DeepSeek provider 兼容处理。 |\n| `patched_minimax.py` | MiniMax reasoning/think block 适配。 |\n| `claude_provider.py` | Claude provider 封装。 |\n| `openai_codex_provider.py` | Codex/OpenAI 特定 provider。 |\n\n```mermaid\nflowchart TD\n  Request[model_name from context] --> Resolve[AppConfig get_model_config]\n  Resolve --> Factory[create_chat_model]\n  Factory --> Credential[credential_loader]\n  Factory --> Reflection[resolve class from use]\n  Reflection --> Provider[provider class]\n  Provider --> Patch[patched provider behavior]\n  Patch --> LangChain[BaseChatModel]\n  LangChain --> Agent[lead_agent]\n```\n\n---\n\n# 补充：设计取舍、重点代码与阅读路径\n\n<callout emoji=\"💡\">\n**设计目的：**这个模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统里抽出来。\n</callout>\n\n| 维度 | 说明 |\n|-|-|\n| 收益 | 收益是查找和学习更快，职责更聚焦。 |\n| 代价 | 代价是章节数量增加，需要依赖目录和索引维护。 |\n| 重点代码 | 重点代码见本章表格列出的源码路径。 |\n| 阅读路径 | 阅读路径：先确认它在系统链路中的上游和下游，再看关键函数。 |\n\n```mermaid\nflowchart TD\n  A[设计目的] --> B[模块职责]\n  B --> C[收益]\n  B --> D[代价]\n  C --> E[重点代码]\n  D --> E\n  E --> F[阅读路径]\n```",
      "document_id": "Px9jdtsoToG0dGxxvrqmwjAayYd",
      "revision_id": 15
    }
  }
}
