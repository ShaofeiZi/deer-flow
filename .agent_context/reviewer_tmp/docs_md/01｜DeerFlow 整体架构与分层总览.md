<title>01｜DeerFlow 整体架构与分层总览</title>

<callout emoji="✅">
**核心结论：** DeerFlow 2.0 的默认运行形态是“Frontend + Gateway 内嵌 LangGraph Runtime + lead_agent”。不要把它理解成单独的 LangGraph Server。
</callout>

# 1. 分层职责

| 分层 | 职责 | 关键路径 |
|-|-|-|
| Browser / Frontend | Next.js App Router、workspace chat、settings、artifacts 面板 | `frontend/src/app、frontend/src/components/workspace、frontend/src/core` |
| Nginx | 统一入口和 /api/langgraph rewrite | `docker/nginx/nginx.local.conf、docker/nginx/nginx.conf` |
| Gateway API | REST + LangGraph-compatible API；初始化运行时单例 | `backend/app/gateway/app.py、deps.py、routers/*` |
| Run Runtime | RunManager、StreamBridge、checkpointer、store、journal | `backend/packages/harness/deerflow/runtime/*` |
| Lead Agent | 模型、工具、skills、middleware、prompt 组装 | `backend/packages/harness/deerflow/agents/lead_agent/*` |
| Execution Extensions | sandbox、MCP、skills、memory、uploads/artifacts | `sandbox/*、mcp/*、skills/*、agents/memory/*、uploads/*` |

# 2. 请求入口与服务拓扑

```mermaid
flowchart TD
  Browser[Browser] --> Nginx[nginx localhost:2026]
  Nginx -->|/| Frontend[Next.js Frontend localhost:3000]
  Nginx -->|/api/*| Gateway[FastAPI Gateway localhost:8001]
  Nginx -->|/api/langgraph/* rewrite| Gateway
  Gateway --> Routers[Gateway Routers]
  Gateway --> Runtime[LangGraph Runtime Singletons]
  Runtime --> Runs[RunManager + RunStore]
  Runtime --> Bridge[StreamBridge SSE]
  Runtime --> Checkpointer[Checkpointer]
  Runtime --> Store[LangGraph Store]
  Runtime --> Agent[lead_agent graph]
```

# 3. 一次用户消息的跨层流转

```mermaid
sequenceDiagram
  participant U as User
  participant FE as Frontend ChatPage
  participant SDK as LangGraph SDK
  participant GW as Gateway
  participant RT as Runtime Worker
  participant AG as lead_agent
  participant SB as StreamBridge
  U->>FE: 输入消息并提交
  FE->>SDK: thread.submit(messages, context)
  SDK->>GW: POST /api/langgraph/threads/{id}/runs/stream
  GW->>RT: create RunRecord and run_agent task
  RT->>AG: make_lead_agent + agent.astream
  AG-->>RT: message/tool/state chunks
  RT->>SB: publish SSE events
  SB-->>FE: values/messages/custom events
  FE-->>U: MessageList / Todo / Artifacts 更新
```

# 4. 新同学阅读检查点

- [ ] 能解释 nginx 将 `/api/langgraph/*` rewrite 到 Gateway 的原因。

- [ ] 能说清 Gateway lifespan 初始化了哪些 runtime singleton。

- [ ] 能把 Frontend、Gateway、Runtime、lead_agent、Tools 的关系画出来。

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**分层架构把 Browser、Nginx、Gateway、Runtime、Agent、Tools 拆开，是为了让运行边界清晰。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是定位问题时能按层排查；代价是跨层链路长，新人容易只看局部。 |
| 代价 | 见收益说明中的代价部分；此章节采用收益与代价合并描述。 |
| 重点代码 | 重点代码：`docker/nginx/nginx.local.conf`、`backend/app/gateway/app.py`、`backend/packages/harness/deerflow/agents/lead_agent/agent.py`。 |
| 阅读路径 | 阅读路径：把它看成一条请求流水线，而不是一组目录。 |

```mermaid
flowchart TD
  A[设计目的] --> B[模块职责]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```