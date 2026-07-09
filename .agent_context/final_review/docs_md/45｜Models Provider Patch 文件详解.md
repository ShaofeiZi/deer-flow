<title>45｜Models Provider Patch 文件详解</title>

<callout emoji="✅">
**本章目标：**把 models 包下 provider patch 文件逐一说明，帮助定位模型兼容问题。
</callout>

| 文件 | 职责 |
|-|-|
| `factory.py` | 统一 create_chat_model，解析 ModelConfig 和 class path。 |
| `credential_loader.py` | 解析 API key、credential、环境变量引用。 |
| `patched_openai.py` | OpenAI 兼容 provider patch。 |
| `patched_deepseek.py` | DeepSeek provider 兼容处理。 |
| `patched_minimax.py` | MiniMax reasoning/think block 适配。 |
| `claude_provider.py` | Claude provider 封装。 |
| `openai_codex_provider.py` | Codex/OpenAI 特定 provider。 |

```mermaid
flowchart TD
  Request[model_name from context] --> Resolve[AppConfig get_model_config]
  Resolve --> Factory[create_chat_model]
  Factory --> Credential[credential_loader]
  Factory --> Reflection[resolve class from use]
  Reflection --> Provider[provider class]
  Provider --> Patch[patched provider behavior]
  Patch --> LangChain[BaseChatModel]
  LangChain --> Agent[lead_agent]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块单独成章，是为了把职责边界、运行逻辑和维护入口从大系统里抽出来。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是查找和学习更快，职责更聚焦。 |
| 代价 | 代价是章节数量增加，需要依赖目录和索引维护。 |
| 重点代码 | 重点代码见本章表格列出的源码路径。 |
| 阅读路径 | 阅读路径：先确认它在系统链路中的上游和下游，再看关键函数。 |

```mermaid
sequenceDiagram
    participant Agent as leadAgent
    participant Factory as create_chat_model
    participant Patch as patched provider
    participant Base as BaseChatModel
    participant API as provider gateway

    Agent->>Factory: name and thinking_enabled
    Factory->>Patch: model_class with merged settings
    Agent->>Patch: invoke multi-turn messages
    Patch->>Base: call base _get_request_payload
    Base-->>Patch: payload drops thought_signature and reasoning_content
    Patch->>Patch: restore_assistant_payloads or reasoning_split or OAuth billing
    Patch->>API: POST repaired payload
    API-->>Patch: response with reasoning_details and signatures
    Patch-->>Agent: AIMessage additional_kwargs preserved
    Note over Agent,API: next turn reuses preserved fields
```
