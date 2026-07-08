{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 108｜Claude、vLLM、MindIE、OpenAI Codex Provider 详解\n\n<callout emoji=\"✅\">\n**本章目标：**单独讲解该模块职责、输入输出和运行逻辑。\n</callout>\n\n| 模块点 | 说明 |\n|-|-|\n| claude_provider.py | Claude provider 封装。 |\n| vllm_provider.py | vLLM OpenAI-compatible 或本地推理适配。 |\n| mindie_provider.py | MindIE provider 适配。 |\n| openai_codex_provider.py | Codex/OpenAI 特定 provider。 |\n| factory.py | 按 use 字段解析这些 provider。 |\n\n```mermaid\nflowchart TD\n  ModelConfig --> Factory\n  Factory --> Claude[ClaudeProvider]\n  Factory --> VLLM[vLLMProvider]\n  Factory --> MindIE[MindIEProvider]\n  Factory --> Codex[OpenAICodexProvider]\n  Claude --> ChatModel\n  VLLM --> ChatModel\n  MindIE --> ChatModel\n  Codex --> ChatModel\n  ChatModel --> LeadAgent\n```",
      "document_id": "PWcGdJg5MoC7OHxYUFqmq6zryxc",
      "revision_id": 18
    }
  }
}
