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
| 收益 | 好处是前后端契约清晰，接口可独立演进。 |
| 代价 | 坏处是一次功能可能跨 router、service、repository 和前端 hook。 |
| 重点代码 | 重点代码在 `backend/app/gateway/routers/`、`backend/app/gateway/auth/*` 或对应前端 `frontend/src/core/*/api.ts`。 |
| 阅读路径 | 阅读路径：从 URL/API 入口往内追 service，再看数据落到哪里。 |

```mermaid
flowchart TD
  A[为什么这么设计] --> B[解决的问题]
  B --> C[好处]
  B --> D[坏处]
  C --> E[重点代码]
  D --> E
  E --> F[怎么理解]
```