<title>203｜Run API / Runs Endpoint 测试详解</title>

<callout emoji="✅">
**本章目标：**继续拆单测试族、单规格文档和根文档模块。
</callout>

| 模块点 | 说明 |
|-|-|
| test_runs_api_endpoints.py | run API endpoints。 |
| test_cancel_run_idempotent.py | cancel 幂等。 |
| test_gateway_services.py | services.start_run。 |
| test_thread_run_messages_pagination.py | run messages 分页。 |
| test_run_worker_rollback.py | rollback。 |

```mermaid
flowchart TD
  RunAPI --> EndpointTests
  Cancel --> CancelTests
  Services --> ServiceTests
  Messages --> PaginationTests
  Worker --> RollbackTests
  EndpointTests --> RunManager
  ServiceTests --> RunManager
  RollbackTests --> Checkpointer
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
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```