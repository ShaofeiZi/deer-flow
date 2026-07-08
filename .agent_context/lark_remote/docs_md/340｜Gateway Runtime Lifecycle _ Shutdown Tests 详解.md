<title>340｜Gateway Runtime Lifecycle / Shutdown Tests 详解</title>

<callout emoji="✅">
**本章目标：**补齐 remaining scripts/tests/routes/package docs 模块。
</callout>

| 模块点 | 说明 |
|-|-|
| test_gateway_lifespan_shutdown.py | lifespan shutdown。 |
| test_gateway_run_drain_shutdown.py | run drain。 |
| test_gateway_run_recovery.py | run recovery。 |
| test_gateway_runtime_cleanup.py | runtime cleanup。 |
| test_runtime_lifecycle_e2e.py | runtime E2E 生命周期。 |

```mermaid
flowchart TD
  GatewayStartup --> RuntimeInit
  RuntimeInit --> Tests
  Shutdown --> DrainRuns
  DrainRuns --> CheckpointerClose
  Restart --> Recovery
  Cleanup --> CleanupTests
  Tests --> CI
```

---

# 补充：设计取舍、重点代码与阅读路径

<callout emoji="💡">
**设计目的：**该模块承担 agent 扩展能力，是为了把工具、知识、长期上下文或执行环境做成可组合部件。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 收益是可扩展、可配置、可替换。 |
| 代价 | 代价是配置、prompt、工具 schema、外部服务任一环节出错都会影响结果。 |
| 重点代码 | 重点代码在 `backend/packages/harness/deerflow` 下对应 skills/mcp/memory/sandbox/tools/models 模块。 |
| 阅读路径 | 阅读路径：明确它给 agent 增加了什么能力，以及该能力在哪里被注入。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```