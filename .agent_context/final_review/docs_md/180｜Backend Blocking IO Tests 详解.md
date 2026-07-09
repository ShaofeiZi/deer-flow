<title>180｜Backend Blocking IO Tests 详解</title>

<callout emoji="✅">
**本章目标：**继续拆 CI、脚本、E2E 具体模块，说明触发、执行与产出。
</callout>

| 模块点 | 说明 |
|-|-|
| blocking_io/conftest.py | 启用 Blockbuster gate。 |
| test_sqlite_lifespan | SQLite lifespan 异步边界。 |
| test_uploads_middleware | 上传中间件阻塞检查。 |
| test_dynamic_context_middleware | 动态上下文阻塞检查。 |
| test_agents_router | agents router 阻塞检查。 |

```mermaid
flowchart TD
  Pytest --> Blockbuster[blocking io conftest]
  Blockbuster --> TestSQLite
  Blockbuster --> TestUploads
  Blockbuster --> TestDynamicContext
  Blockbuster --> TestAgentsRouter
  Tests --> Detect[detect sync IO in async path]
  Detect --> Fail[fail if blocking]
  Detect --> Pass[pass gate]
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**这个模块以 API/边界层拆分，是为了隔离 HTTP 协议、认证鉴权、请求模型和内部业务。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是前后端契约清晰，接口可独立演进。 |
| 代价 | 代价是一次功能可能跨 router、service、repository 和前端 hook。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
flowchart TD
    Item["pytest test item"] --> Gate{"is_blocking_io_item"}
    Gate -- "no" --> Skip["yield ungated"]
    Gate -- "yes" --> Mark{"allow_blocking_io marker"}
    Mark -- "set" --> Skip
    Mark -- "unset" --> Strict["detect_blocking_io_strict"]
    Strict --> BB["BlockBuster scanned_modules app deerflow"]
    BB --> Anchor["each anchor runs ainvoke / handler"]
    Anchor --> Off["asyncio.to_thread offload"]
    Off --> Loop["event loop stays free"]
    Loop --> Detect{"sync IO in app/deerflow on loop"}
    Detect -- "yes" --> Fail["BlockingError test fails"]
    Detect -- "no" --> Pass["gate passes"]
    Anchor -. "sqlite path" .-> CP["_async_checkpointer ensure_sqlite_parent_dir"]
    Anchor -. "uploads scan" .-> UM["UploadsMiddleware abefore_agent run_in_executor"]
    Anchor -. "ctx inject" .-> DM["DynamicContextMiddleware abefore_agent to_thread"]
    Anchor -. "agent dir" .→ AG["create_agent_endpoint delete_agent to_thread"]
```