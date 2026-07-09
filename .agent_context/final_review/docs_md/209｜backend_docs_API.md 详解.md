<title>209｜backend/docs/API.md 详解</title>

<callout emoji="✅">
**本章目标：**继续把 backend/docs 中重要说明拆成独立讲解文档。
</callout>

| 文档点 | 说明 |
|-|-|
| LangGraph-compatible API | threads、runs、state、history、stream。 |
| Gateway API | models、mcp、skills、uploads、artifacts、memory。 |
| stream modes | values/messages/custom/events 等。 |
| 前端关系 | LangGraph SDK 和 REST fetcher 调用。 |

```mermaid
flowchart TD
  Client --> LangGraphAPI[api langgraph]
  Client --> GatewayAPI[api]
  LangGraphAPI --> Threads[threads]
  LangGraphAPI --> Runs[runs stream wait]
  GatewayAPI --> Models
  GatewayAPI --> MCP
  GatewayAPI --> Skills
  GatewayAPI --> Uploads
  GatewayAPI --> Artifacts
  GatewayAPI --> Memory
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
  participant Client
  participant Auth as AuthMiddleware
  participant CSRF as CSRFMiddleware
  participant Handler as stream_run
  participant StartRun as start_run
  participant RunMgr as RunManager
  participant Task as run_agent task
  participant Bridge as StreamBridge
  participant Consumer as sse_consumer

  Client->>Auth: POST runs/stream
  Auth->>CSRF: user context
  CSRF->>Handler: csrf ok
  Handler->>StartRun: body thread_id
  StartRun->>StartRun: check_access ownership
  StartRun->>RunMgr: create_or_reject
  RunMgr-->>StartRun: RunRecord
  StartRun->>StartRun: build_run_config
  StartRun->>Task: create_task run_agent
  Handler->>Consumer: StreamingResponse
  Task->>Bridge: publish events
  Bridge->>Consumer: values messages end
  Consumer->>Client: SSE frames
  Consumer->>RunMgr: cancel on disconnect
```