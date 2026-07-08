<title>193｜Tracing / Token Usage Tests 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 Docker、Provisioner、脚本和测试细模块。
</callout>

| 模块点 | 说明 |
|-|-|
| test_tracing_config/factory/metadata | tracing 配置、回调、metadata。 |
| test_token_usage.py | token usage 聚合。 |
| test_token_usage_middleware.py | middleware attribution。 |
| test_thread_token_usage.py | thread 级 token usage API。 |
| test_task_tool_usage_recorder.py | task tool 用量记录。 |

```mermaid
flowchart TD
  LLMCall --> TokenUsageMW
  TokenUsageMW --> UsageRecords
  UsageRecords --> TokenTests
  RunConfig --> TracingConfig
  TracingConfig --> TracingFactory
  TracingFactory --> TraceMetadata
  TraceMetadata --> TracingTests
  TokenTests --> CI
  TracingTests --> CI
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
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```