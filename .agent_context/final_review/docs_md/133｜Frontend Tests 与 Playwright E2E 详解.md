<title>133｜Frontend Tests 与 Playwright E2E 详解</title>

<callout emoji="✅">
**本章目标：**补齐测试、脚本、Docker、Skills 分类，解释运行逻辑。
</callout>

| 模块点 | 说明 |
|-|-|
| unit tests | core clipboard/reasoning trigger 等单测。 |
| e2e mock | chat、sidebar、artifact、thread-history 等 mocked backend。 |
| e2e real backend | auth-disabled、multi-run-order、real-backend-render。 |
| record tests | record write/read file 流程。 |

```mermaid
flowchart TD
  FrontendCode --> Unit[vitest unit]
  FrontendCode --> E2E[playwright e2e]
  E2E --> MockBackend[tests e2e mock api]
  E2E --> RealBackend[e2e real backend]
  RealBackend --> Gateway[real gateway]
  Unit --> CI[frontend-unit-tests]
  E2E --> CI2[e2e-tests]
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
  Vitest["vitest.config.ts"] --> UnitSpec["tests/unit"]
  UnitSpec --> CoreSrc["src/core"]

  Mock["playwright.config.ts"] --> MockSpec["tests/e2e"]
  Mock --> FrontendA["next build and start :3000"]
  FrontendA --> MockSpec
  MockSpec -.mock.-> MockAPI["utils/mock-api.ts"]

  Real["playwright.real-backend.config.ts"] --> RealSpec["tests/e2e-real-backend"]
  Real --> ReplayGW["run_replay_gateway.py :8011"]
  Real --> FrontendB["next start :3000"]
  FrontendB -- DEER_FLOW_INTERNAL_GATEWAY_BASE_URL --> ReplayGW
  ReplayGW --> RealSpec
  RealSpec --> Fixtures["tests/fixtures/replay"]

  Record["playwright.record.config.ts"] --> RecordSpec["tests/e2e-record"]
  Record --> RecordGW["record_gateway.py :8012"]
  Record --> FrontendC["next start :3000"]
  FrontendC --> RecordGW
  RecordGW -- DEERFLOW_RECORD_OUT --> Capture["recorded captures"]

  Mock -. DEER_FLOW_AUTH_DISABLED .-> FrontendA
  Real -. DEER_FLOW_AUTH_DISABLED .-> FrontendB
```