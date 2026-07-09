<title>191｜Client E2E / Live Tests 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 Docker、Provisioner、脚本和测试细模块。
</callout>

| 模块点 | 说明 |
|-|-|
| test_client.py | DeerFlow client 基础行为。 |
| test_client_e2e.py | client 端到端。 |
| test_client_live.py | live 环境 client。 |
| test_client_message_serialization.py | 消息序列化。 |
| test_client_langfuse_metadata.py | client tracing metadata。 |

```mermaid
flowchart TD
  ClientCode --> ClientTests
  ClientTests --> Serialization[message serialization]
  ClientTests --> E2E[client e2e]
  ClientTests --> Live[live tests]
  E2E --> Gateway[Test Gateway]
  Live --> External[real config if enabled]
  Serialization --> Assertions
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
  Stream["DeerFlowClient.stream"] --> AutoID["thread_id or uuid4"]
  AutoID --> GetCfg["_get_runnable_config"]
  GetCfg --> Trace["tracing callbacks plus langfuse metadata"]
  Trace --> Ensure["_ensure_agent"]
  Ensure -->|config key changed| Build["build_middlewares and create_agent"]
  Build --> Agent["self._agent.stream"]
  Ensure -->|same config key| Agent
  Agent -->|stream_mode list| Fan["values messages custom"]
  Fan -->|custom| EvCustom["StreamEvent custom"]
  Fan -->|messages AI| EvAI["_ai_text_event and _ai_tool_calls_event"]
  Fan -->|messages tool| EvTool["_tool_message_event"]
  Fan -->|values| Dedup["streamed_ids and seen_ids dedup"]
  Dedup --> EvValues["StreamEvent values via _serialize_message"]
  EvCustom --> End["StreamEvent end cumulative usage"]
  EvAI --> End
  EvTool --> End
  EvValues --> End
```