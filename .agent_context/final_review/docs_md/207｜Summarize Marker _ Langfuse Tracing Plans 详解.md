<title>207｜Summarize Marker / Langfuse Tracing Plans 详解</title>

<callout emoji="✅">
**本章目标：**继续拆单测试族、单规格文档和根文档模块。
</callout>

| 模块点 | 说明 |
|-|-|
| 2026-04-11-summarize-marker-design.md | 摘要 marker 设计。 |
| 2026-04-01-langfuse-tracing.md | Langfuse tracing plan。 |
| 目标 | 提升长上下文摘要和 trace 可观测性。 |
| 关联 | SummarizationMiddleware、tracing/factory、metadata。 |

```mermaid
flowchart TD
  LongContext --> SummarizeMarker[summary marker design]
  SummarizeMarker --> SummaryMW[SummarizationMiddleware]
  RunTrace --> LangfusePlan[Langfuse tracing plan]
  LangfusePlan --> TracingFactory
  TracingFactory --> Metadata[trace metadata]
  Metadata --> Observability
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
sequenceDiagram
  participant Worker as RunWorker
  participant Meta as tracing.metadata
  participant TFactory as tracing.factory
  participant Agent as lead_agent
  participant SMW as SummarizationMiddleware
  participant Hook as memory_flush_hook
  participant SModel as summary_model
  participant LF as LangfuseHandler

  Worker->>Meta: inject_langfuse_metadata
  Note over Meta: sets session_id user_id trace_name tags
  Worker->>Agent: build and stream config
  Agent->>TFactory: build_tracing_callbacks
  TFactory-->>Agent: langfuse handler
  Agent->>SMW: abefore_model state runtime
  SMW->>SMW: should_summarize token trigger
  alt threshold met
    SMW->>SMW: partition_with_skill_rescue
    SMW->>Hook: before_summarization event
    Hook->>Hook: MemoryQueue add_nowait
    SMW->>SModel: ainvoke nostream prompt
    SModel->>LF: on_chain_start root trace
    SMW-->>Agent: RemoveMessage plus summary plus preserved
  else not met
    SMW-->>Agent: None
  end
```