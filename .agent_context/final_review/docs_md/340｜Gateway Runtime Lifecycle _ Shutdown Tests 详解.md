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
**设计目的：**该文档说明前端 UI primitive、workspace 组件或页面模块的职责、状态来源和渲染分支。
</callout>

| 维度 | 说明 |
|-|-|
| 收益 | 组件边界清晰后，UI 问题可按 props/state/hook/route 快速定位。 |
| 代价 | 一次交互常跨页面、hook、context 和展示组件，需要按数据流追踪。 |
| 重点代码 | 标题对应的 `frontend/src/app/`、`frontend/src/components/` 或 `frontend/src/core/` 文件。 |
| 阅读路径 | 先看组件输入输出，再看状态来源，最后看事件回调如何改变 UI。 |

```mermaid
flowchart TD
  A[设计目的] --> B[解决的问题]
  B --> C[收益]
  B --> D[代价]
  C --> E[重点代码]
  D --> E
  E --> F[阅读路径]
```