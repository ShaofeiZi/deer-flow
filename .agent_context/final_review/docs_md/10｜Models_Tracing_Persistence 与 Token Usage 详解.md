<title>10｜Models、Tracing、Persistence 与 Token Usage 详解</title>

<callout emoji="✅">
**本章目标：** 讲清模型如何从 config.yaml 变成 LangChain model，trace/token/persistence 如何贯穿一次 run。
</callout>

# 1. Model Factory

```mermaid
flowchart TD
  Config[config.yaml models] --> AppConfig[AppConfig]
  AppConfig --> Resolve[resolve model by name]
  Resolve --> Class[reflection resolve_class]
  Class --> Provider[LangChain ChatModel provider]
  Provider --> Patch[provider patches if needed]
  Patch --> Model[BaseChatModel]
  Model --> Agent[create_agent model binding]
```

# 2. Tracing 与 Token Usage

```mermaid
flowchart TD
  Run[run_agent] --> Metadata[trace metadata]
  Metadata --> Callbacks[build_tracing_callbacks]
  Callbacks --> GraphRoot[attach at graph invocation root]
  GraphRoot --> LLM[model/tool spans]
  LLM --> TokenMW[TokenUsageMiddleware]
  TokenMW --> Journal[RunJournal]
  Journal --> Store[run events / token usage]
  Store --> Frontend[TokenUsageIndicator]
```

# 3. Persistence 运行逻辑

```mermaid
flowchart TD
  Startup[langgraph_runtime startup] --> Engine[init persistence engine]
  Engine --> Checkpointer[make_checkpointer]
  Engine --> Store[make_store]
  Engine --> RunStore[RunRepository]
  Engine --> ThreadStore[make_thread_store]
  Engine --> Feedback[FeedbackRepository]
  Run[run_agent] --> CheckpointPut[checkpoint writes]
  Run --> EventWrite[run event writes]
  Run --> ThreadMeta[thread title/status update]
```

# 4. 关键文件

| 模块 | 关键文件 |
|-|-|
| Model factory | `backend/packages/harness/deerflow/models/factory.py` |
| Provider patches | `backend/packages/harness/deerflow/models/patched_*.py` |
| Tracing | `backend/packages/harness/deerflow/tracing/factory.py` |
| Persistence engine | `backend/packages/harness/deerflow/persistence/engine.py` |
| Run journal | `backend/packages/harness/deerflow/runtime/journal.py` |
| Token UI | `frontend/src/components/workspace/token-usage-indicator.tsx` |

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**模型、追踪、持久化是 run 可观测与可恢复的基础。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是可切模型、可追 trace、可恢复状态；代价是配置和启动期资源复杂。 |
| 代价 | 见收益说明中的代价部分；此章节采用收益与代价合并描述。 |
| 重点代码 | 重点代码：`backend/packages/harness/deerflow/models/factory.py`、`backend/packages/harness/deerflow/tracing/factory.py`、`backend/packages/harness/deerflow/persistence/engine.py`。 |
| 阅读路径 | 阅读路径：模型负责推理，trace 记录过程，persistence 记录状态。 |

```mermaid
flowchart TD
  Start[init_engine_from_config] --> Branch{backend}
  Branch -->|memory| NoOp[no-op return]
  Branch -->|sqlite| SQLite[create_async_engine]
  Branch -->|postgres| PgCheck[verify asyncpg import]
  SQLite --> WAL[PRAGMA WAL and synchronous NORMAL]
  PgCheck --> PgEngine[create_async_engine pool_pre_ping]
  WAL --> Session[async_sessionmaker]
  PgEngine --> Session
  Session --> ImportModels[import persistence.models]
  ImportModels --> CreateAll[Base.metadata.create_all]
  CreateAll --> Err{create fails}
  Err -->|postgres missing db| Auto[_auto_create_postgres_db]
  Auto --> Retry[rebuild engine retry create_all]
  Err -->|ok| Ready[engine ready]
  Retry --> Ready
  Err -->|other error| Raise[re-raise]
```