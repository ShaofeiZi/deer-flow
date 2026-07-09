<title>212｜backend/docs/STREAMING.md 详解</title>

<callout emoji="✅">
**本章目标：**继续把 backend/docs 中重要说明拆成独立讲解文档。
</callout>

| 文档点 | 说明 |
|-|-|
| SSE | 服务端事件流。 |
| StreamBridge | 后台 run 到 HTTP response 的桥。 |
| LangGraph modes | values/messages/custom。 |
| frontend | useStream callbacks。 |

```mermaid
sequenceDiagram
  participant Worker as run_agent
  participant Bridge as StreamBridge
  participant SSE as sse_consumer
  participant UI as Frontend
  Worker->>Bridge: publish event
  SSE->>Bridge: subscribe
  Bridge-->>SSE: event
  SSE-->>UI: SSE frame
  Worker->>Bridge: end
  Bridge-->>UI: done
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