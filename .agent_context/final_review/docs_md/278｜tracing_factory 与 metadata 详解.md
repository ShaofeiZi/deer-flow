<title>278｜tracing/factory 与 metadata 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 tools/reflection/utils 等基础模块。
</callout>

| 模块点 | 说明 |
|-|-|
| factory.py | build_tracing_callbacks。 |
| metadata.py | trace metadata 构造。 |
| Langfuse/LangSmith | 按配置启用 callbacks。 |
| run_agent | 把 callbacks 挂到 graph root。 |

```mermaid
flowchart TD
  TracingConfig --> Factory[build tracing callbacks]
  RuntimeConfig --> Metadata[trace metadata]
  Factory --> Callbacks
  Metadata --> RunnableConfig
  RunnableConfig --> GraphRoot
  GraphRoot --> LLMSpans
  GraphRoot --> ToolSpans
  Spans --> Observability
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**前端按 route、core 数据层、业务组件、UI primitive 分层，是为了降低组件耦合。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是展示层和数据请求分离，组件更容易复用。 |
| 代价 | 代价是一次用户交互常跨页面、hook、缓存、上下文和组件。 |
| 重点代码 | 重点代码在 `frontend/src/app`、`frontend/src/core`、`frontend/src/components` 对应模块。 |
| 阅读路径 | 阅读路径：先找 route，再找 hook 数据源，最后看组件消费。 |

```mermaid
sequenceDiagram
    participant GW as RunsWorker
    participant CL as DeerFlowClient stream
    participant CFG as tracing_config
    participant FAC as factory build_tracing_callbacks
    participant MD as metadata inject_langfuse_metadata
    participant RC as RunnableConfig
    participant GR as lead_agent astream
    participant LF as Langfuse CallbackHandler

    GW->>CFG: get_enabled_tracing_providers
    CL->>CFG: get_enabled_tracing_providers
    CFG-->>FAC: langsmith or langfuse
    FAC->>FAC: LangChainTracer or Langfuse CallbackHandler
    GW->>MD: thread_id user_id assistant_id model_name
    CL->>MD: thread_id user_id assistant_id model_name
    MD->>RC: setdefault langfuse_session_id user_id tags
    GW->>RC: append config callbacks
    CL->>RC: append config callbacks
    GW->>GR: agent.astream runnableConfig
    CL->>GR: agent.astream config
    GR->>LF: on_chain_start parent_run_id None
    LF->>LF: propagate session_id user_id to root trace
    GR-->>LF: nested LLM spans and tool spans
```